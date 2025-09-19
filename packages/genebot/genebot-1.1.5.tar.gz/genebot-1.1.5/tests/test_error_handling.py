"""
Tests for error handling and recovery mechanisms.

This module tests the custom exception hierarchy, retry logic,
circuit breaker pattern, and graceful degradation functionality.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.exceptions import (
    TradingBotException,
    ExchangeException,
    StrategyException,
    RiskException,
    DataException,
    NetworkException,
    RetryableException,
    CircuitBreakerException,
    NonRecoverableException
)
from src.utils.retry_handler import RetryHandler, retry_with_backoff, NetworkRetryHandler
from src.utils.circuit_breaker import CircuitBreaker, CircuitState, circuit_breaker
from src.utils.graceful_degradation import (
    GracefulDegradationManager,
    ComponentStatus,
    ServiceLevel
)


class TestExceptionHierarchy:
    """Test custom exception hierarchy."""
    
    def test_trading_bot_exception_basic(self):
        """Test basic TradingBotException functionality."""
        exception = TradingBotException("Test error", error_code="TEST_001")
        
        assert str(exception) == "Test error"
        assert exception.error_code == "TEST_001"
        assert exception.context == {}
        assert isinstance(exception.timestamp, datetime)
    
    def test_trading_bot_exception_with_context(self):
        """Test TradingBotException with context."""
        context = {"symbol": "BTC/USD", "amount": 1.5}
        exception = TradingBotException("Test error", context=context)
        
        assert exception.context == context
        
        exception_dict = exception.to_dict()
        assert exception_dict["context"] == context
        assert exception_dict["error_type"] == "TradingBotException"
    
    def test_exchange_exception(self):
        """Test ExchangeException functionality."""
        exception = ExchangeException(
            "Connection failed",
            exchange_name="binance",
            error_code="CONN_001"
        )
        
        assert exception.exchange_name == "binance"
        assert exception.context["exchange"] == "binance"
    
    def test_network_exception(self):
        """Test NetworkException functionality."""
        exception = NetworkException(
            "HTTP 429 Too Many Requests",
            status_code=429,
            retry_after=60
        )
        
        assert exception.status_code == 429
        assert exception.retry_after == 60
        assert exception.context["status_code"] == 429
        assert exception.context["retry_after"] == 60
    
    def test_strategy_exception(self):
        """Test StrategyException functionality."""
        exception = StrategyException(
            "Strategy failed",
            strategy_name="MovingAverage",
            symbol="ETH/USD"
        )
        
        assert exception.strategy_name == "MovingAverage"
        assert exception.symbol == "ETH/USD"
        assert exception.context["strategy"] == "MovingAverage"
        assert exception.context["symbol"] == "ETH/USD"
    
    def test_risk_exception(self):
        """Test RiskException functionality."""
        exception = RiskException(
            "Position size too large",
            risk_type="position_size",
            threshold_value=1000.0,
            current_value=1500.0
        )
        
        assert exception.risk_type == "position_size"
        assert exception.threshold_value == 1000.0
        assert exception.current_value == 1500.0


class TestRetryHandler:
    """Test retry handler functionality."""
    
    def test_retry_handler_success(self):
        """Test successful execution without retries."""
        handler = RetryHandler(max_retries=3)
        mock_func = Mock(return_value="success")
        
        result = handler.execute(mock_func, "arg1", kwarg1="value1")
        
        assert result == "success"
        mock_func.assert_called_once_with("arg1", kwarg1="value1")
    
    def test_retry_handler_with_retries(self):
        """Test retry logic with eventual success."""
        handler = RetryHandler(max_retries=3, initial_delay=0.01)
        mock_func = Mock(side_effect=[
            RetryableException("Temporary error"),
            RetryableException("Another error"),
            "success"
        ])
        
        result = handler.execute(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_handler_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        handler = RetryHandler(max_retries=2, initial_delay=0.01)
        mock_func = Mock(side_effect=RetryableException("Persistent error"))
        
        with pytest.raises(RetryableException):
            handler.execute(mock_func)
        
        assert mock_func.call_count == 3  # Initial + 2 retries
    
    def test_retry_handler_non_retryable_exception(self):
        """Test that non-retryable exceptions are not retried."""
        handler = RetryHandler(max_retries=3)
        mock_func = Mock(side_effect=ValueError("Non-retryable error"))
        
        with pytest.raises(ValueError):
            handler.execute(mock_func)
        
        mock_func.assert_called_once()
    
    def test_delay_calculation(self):
        """Test exponential backoff delay calculation."""
        handler = RetryHandler(
            initial_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=10.0,
            jitter=False
        )
        
        assert handler.calculate_delay(0) == 1.0
        assert handler.calculate_delay(1) == 2.0
        assert handler.calculate_delay(2) == 4.0
        assert handler.calculate_delay(3) == 8.0
        assert handler.calculate_delay(4) == 10.0  # Capped at max_delay
    
    @pytest.mark.asyncio
    async def test_async_retry_handler(self):
        """Test async retry handler."""
        handler = RetryHandler(max_retries=2, initial_delay=0.01)
        mock_func = AsyncMock(side_effect=[
            RetryableException("Temporary error"),
            "success"
        ])
        
        result = await handler.execute_async(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 2
    
    def test_retry_decorator(self):
        """Test retry decorator functionality."""
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def test_function():
            if not hasattr(test_function, 'call_count'):
                test_function.call_count = 0
            test_function.call_count += 1
            
            if test_function.call_count < 2:
                raise RetryableException("Temporary error")
            return "success"
        
        result = test_function()
        assert result == "success"
        assert test_function.call_count == 2
    
    def test_network_retry_handler(self):
        """Test specialized network retry handler."""
        handler = NetworkRetryHandler()
        
        # Test HTTP 429 (rate limit) - should retry
        exception = NetworkException("Rate limited", status_code=429)
        assert handler.should_retry(exception, 0) is True
        
        # Test HTTP 401 (unauthorized) - should not retry
        exception = NetworkException("Unauthorized", status_code=401)
        assert handler.should_retry(exception, 0) is False
        
        # Test HTTP 500 (server error) - should retry
        exception = NetworkException("Server error", status_code=500)
        assert handler.should_retry(exception, 0) is True


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state."""
        cb = CircuitBreaker("test", failure_threshold=3)
        mock_func = AsyncMock(return_value="success")
        
        result = await cb.call(mock_func)
        
        assert result == "success"
        assert cb.is_closed
        assert cb.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures."""
        cb = CircuitBreaker("test", failure_threshold=2, timeout=0.1)
        mock_func = AsyncMock(side_effect=ExchangeException("Test error"))
        
        # First failure
        with pytest.raises(ExchangeException):
            await cb.call(mock_func)
        assert cb.is_closed
        assert cb.failure_count == 1
        
        # Second failure - should open circuit
        with pytest.raises(ExchangeException):
            await cb.call(mock_func)
        assert cb.is_open
        assert cb.failure_count == 2
        
        # Third call should fail fast
        with pytest.raises(CircuitBreakerException):
            await cb.call(mock_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        cb = CircuitBreaker("test", failure_threshold=1, timeout=0.01, success_threshold=2)
        
        # Cause failure to open circuit
        mock_func = AsyncMock(side_effect=ExchangeException("Test error"))
        with pytest.raises(ExchangeException):
            await cb.call(mock_func)
        assert cb.is_open
        
        # Wait for timeout
        await asyncio.sleep(0.02)
        
        # Next call should transition to half-open
        mock_func.side_effect = None
        mock_func.return_value = "success"
        result = await cb.call(mock_func)
        assert result == "success"
        assert cb.is_half_open
        
        # Another success should close the circuit
        result = await cb.call(mock_func)
        assert result == "success"
        assert cb.is_closed
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_decorator(self):
        """Test circuit breaker decorator."""
        @circuit_breaker("test_service", failure_threshold=2)
        async def test_function(should_fail=False):
            if should_fail:
                raise ExchangeException("Test error")
            return "success"
        
        # Successful calls
        result = await test_function()
        assert result == "success"
        
        # Cause failures to open circuit
        with pytest.raises(ExchangeException):
            await test_function(should_fail=True)
        with pytest.raises(ExchangeException):
            await test_function(should_fail=True)
        
        # Circuit should be open now
        with pytest.raises(CircuitBreakerException):
            await test_function()
    
    def test_circuit_breaker_stats(self):
        """Test circuit breaker statistics."""
        cb = CircuitBreaker("test", failure_threshold=3)
        stats = cb.get_stats()
        
        assert stats["name"] == "test"
        assert stats["state"] == "closed"
        assert stats["failure_count"] == 0
        assert stats["failure_threshold"] == 3


class TestGracefulDegradation:
    """Test graceful degradation functionality."""
    
    @pytest.fixture
    def degradation_manager(self):
        """Create a fresh degradation manager for each test."""
        return GracefulDegradationManager()
    
    def test_component_registration(self, degradation_manager):
        """Test component registration."""
        degradation_manager.register_component(
            "exchange_api",
            dependencies={"network"},
            critical=True
        )
        
        assert "exchange_api" in degradation_manager.components
        component = degradation_manager.components["exchange_api"]
        assert component.name == "exchange_api"
        assert component.status == ComponentStatus.HEALTHY
        assert "network" in component.dependencies
    
    @pytest.mark.asyncio
    async def test_component_status_update(self, degradation_manager):
        """Test component status updates."""
        degradation_manager.register_component("test_component")
        
        await degradation_manager.update_component_status(
            "test_component",
            ComponentStatus.DEGRADED,
            "Test error"
        )
        
        component = degradation_manager.components["test_component"]
        assert component.status == ComponentStatus.DEGRADED
        assert component.error_count == 1
        assert component.last_error == "Test error"
    
    @pytest.mark.asyncio
    async def test_service_level_degradation(self, degradation_manager):
        """Test service level changes based on component failures."""
        # Register components
        degradation_manager.register_component("critical_component", critical=True)
        degradation_manager.register_component("normal_component")
        
        # Initially should be full service
        assert degradation_manager.service_level == ServiceLevel.FULL
        
        # Fail critical component - should go to emergency
        await degradation_manager.update_component_status(
            "critical_component",
            ComponentStatus.FAILED
        )
        assert degradation_manager.service_level == ServiceLevel.EMERGENCY
    
    @pytest.mark.asyncio
    async def test_fallback_handler_execution(self, degradation_manager):
        """Test fallback handler execution."""
        fallback_called = False
        
        def fallback_handler(error):
            nonlocal fallback_called
            fallback_called = True
        
        degradation_manager.register_component(
            "test_component",
            fallback_handler=fallback_handler
        )
        
        # Record error should trigger fallback
        await degradation_manager.record_component_error(
            "test_component",
            Exception("Test error")
        )
        
        assert fallback_called
        component = degradation_manager.components["test_component"]
        assert component.status == ComponentStatus.DEGRADED
    
    def test_component_availability_check(self, degradation_manager):
        """Test component availability checking."""
        degradation_manager.register_component("test_component")
        
        # Initially available
        assert degradation_manager.is_component_available("test_component")
        
        # Update to failed - should not be available
        asyncio.run(degradation_manager.update_component_status(
            "test_component",
            ComponentStatus.FAILED
        ))
        assert not degradation_manager.is_component_available("test_component")
    
    def test_operation_execution_check(self, degradation_manager):
        """Test operation execution capability checking."""
        degradation_manager.register_component("component1")
        degradation_manager.register_component("component2")
        
        # Both components healthy - operation should be possible
        assert degradation_manager.can_execute_operation(["component1", "component2"])
        
        # Fail one component
        asyncio.run(degradation_manager.update_component_status(
            "component1",
            ComponentStatus.FAILED
        ))
        assert not degradation_manager.can_execute_operation(["component1", "component2"])
    
    def test_system_health_report(self, degradation_manager):
        """Test system health reporting."""
        degradation_manager.register_component("component1")
        degradation_manager.register_component("component2")
        
        health = degradation_manager.get_system_health()
        
        assert health["total_components"] == 2
        assert health["healthy_components"] == 2
        assert health["health_percentage"] == 100.0
        assert health["service_level"] == "full"
        assert "components" in health


class TestErrorRecoveryIntegration:
    """Test integration of error handling components."""
    
    @pytest.mark.asyncio
    async def test_retry_with_circuit_breaker(self):
        """Test retry handler working with circuit breaker."""
        cb = CircuitBreaker("test_service", failure_threshold=5)  # Higher threshold
        retry_handler = RetryHandler(max_retries=2, initial_delay=0.01)  # Fewer retries
        
        call_count = 0
        
        async def failing_function():
            nonlocal call_count
            call_count += 1
            raise ExchangeException("Service unavailable")
        
        # First attempt - should exhaust retries before circuit opens
        with pytest.raises(ExchangeException):
            await retry_handler.execute_async(
                lambda: cb.call(failing_function)
            )
        
        # Circuit should still be closed since we haven't hit the threshold
        assert not cb.is_open
        
        # Make more calls to open the circuit
        for i in range(2):  # Only 2 more calls needed (3 + 2 = 5)
            with pytest.raises(ExchangeException):
                await cb.call(failing_function)
        
        # Now circuit should be open
        assert cb.is_open
        
        # Subsequent calls should fail fast due to circuit breaker
        with pytest.raises(CircuitBreakerException):
            await cb.call(failing_function)
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_with_fallback(self):
        """Test graceful degradation with fallback mechanisms."""
        degradation_manager = GracefulDegradationManager()
        fallback_used = False
        
        def exchange_fallback(error):
            nonlocal fallback_used
            fallback_used = True
            # Simulate switching to backup exchange
            return "backup_exchange_data"
        
        degradation_manager.register_component(
            "primary_exchange",
            fallback_handler=exchange_fallback
        )
        
        # Simulate exchange failure
        await degradation_manager.record_component_error(
            "primary_exchange",
            ExchangeException("Primary exchange down")
        )
        
        # Fallback should have been triggered
        assert fallback_used
        
        # Component should be degraded but still available
        assert degradation_manager.is_component_available("primary_exchange")
        component = degradation_manager.components["primary_exchange"]
        assert component.status == ComponentStatus.DEGRADED