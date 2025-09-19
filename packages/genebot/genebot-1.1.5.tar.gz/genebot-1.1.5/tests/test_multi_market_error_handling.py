"""
Unit tests for multi-market error handling system.

Tests cover market-specific exceptions, market closure handling, broker failover,
regulatory compliance, and error recovery scenarios.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from src.exceptions.multi_market_exceptions import (
    MarketType,
    MarketSpecificException,
    MarketClosedException,
    BrokerConnectionException,
    BrokerUnavailableException,
    RegulatoryViolationException,
    FailoverException,
    ReconnectionException,
    CrossMarketException,
    CorrelationException,
    ArbitrageException
)

from src.exceptions.market_closure_handler import (
    MarketClosureHandler,
    OrderQueueManager,
    QueuedOrder,
    OrderStatus
)

from src.exceptions.broker_failover import (
    BrokerFailoverManager,
    BrokerHealthMonitor,
    BrokerConfig,
    BrokerStatus,
    FailoverStrategy
)

from src.exceptions.regulatory_handler import (
    RegulatoryComplianceManager,
    RegulatoryMonitor,
    RegulatoryActionHandler,
    RegulatoryRule,
    ViolationEvent,
    CorrectiveAction,
    ActionType,
    ViolationType,
    Severity
)


class TestMultiMarketExceptions:
    """Test multi-market specific exceptions."""
    
    def test_market_specific_exception(self):
        """Test MarketSpecificException creation and attributes."""
        exception = MarketSpecificException(
            "Test error",
            MarketType.FOREX,
            market_name="OANDA"
        )
        
        assert exception.market_type == MarketType.FOREX
        assert exception.market_name == "OANDA"
        assert exception.context['market_type'] == "forex"
        assert exception.context['market_name'] == "OANDA"
    
    def test_market_closed_exception(self):
        """Test MarketClosedException with next open time."""
        next_open = datetime.now(timezone.utc) + timedelta(hours=8)
        
        exception = MarketClosedException(
            "Market is closed",
            MarketType.FOREX,
            next_open_time=next_open,
            market_session="london"
        )
        
        assert exception.market_type == MarketType.FOREX
        assert exception.next_open_time == next_open
        assert exception.market_session == "london"
        assert "next_open_time" in exception.context
    
    def test_broker_connection_exception(self):
        """Test BrokerConnectionException with recovery info."""
        last_connection = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        exception = BrokerConnectionException(
            "Connection failed",
            MarketType.FOREX,
            "MT5",
            connection_type="websocket",
            last_successful_connection=last_connection
        )
        
        assert exception.broker_name == "MT5"
        assert exception.connection_type == "websocket"
        assert exception.last_successful_connection == last_connection
    
    def test_regulatory_violation_exception(self):
        """Test RegulatoryViolationException with violation details."""
        exception = RegulatoryViolationException(
            "Position limit exceeded",
            MarketType.FOREX,
            "position_limit",
            "MiFID II",
            jurisdiction="EU",
            penalty="warning"
        )
        
        assert exception.violation_type == "position_limit"
        assert exception.regulation == "MiFID II"
        assert exception.jurisdiction == "EU"
        assert exception.penalty == "warning"
        assert exception.shutdown_required is False  # From NonRecoverableException
    
    def test_cross_market_exception(self):
        """Test CrossMarketException with multiple markets."""
        markets = [MarketType.CRYPTO, MarketType.FOREX]
        
        exception = CrossMarketException(
            "Cross-market correlation failed",
            markets,
            operation_type="correlation_analysis"
        )
        
        assert exception.involved_markets == markets
        assert exception.operation_type == "correlation_analysis"
        assert exception.context['involved_markets'] == ["crypto", "forex"]
    
    def test_correlation_exception(self):
        """Test CorrelationException with correlation values."""
        markets = [MarketType.CRYPTO, MarketType.FOREX]
        
        exception = CorrelationException(
            "Correlation threshold exceeded",
            markets,
            correlation_threshold=0.8,
            current_correlation=0.95
        )
        
        assert exception.correlation_threshold == 0.8
        assert exception.current_correlation == 0.95
        assert exception.context['correlation_threshold'] == 0.8
    
    def test_arbitrage_exception(self):
        """Test ArbitrageException with arbitrage details."""
        markets = [MarketType.CRYPTO, MarketType.FOREX]
        
        exception = ArbitrageException(
            "Arbitrage opportunity expired",
            markets,
            arbitrage_type="triangular",
            expected_profit=0.05
        )
        
        assert exception.arbitrage_type == "triangular"
        assert exception.expected_profit == 0.05
        assert exception.context['arbitrage_type'] == "triangular"


class TestMarketClosureHandler:
    """Test market closure handling and order queuing."""
    
    @pytest.fixture
    def closure_handler(self):
        """Create a MarketClosureHandler instance."""
        return MarketClosureHandler(max_queue_size=10)
    
    @pytest.fixture
    def sample_order(self):
        """Create a sample queued order."""
        return QueuedOrder(
            id="test_order_1",
            market_type=MarketType.FOREX,
            broker_name="OANDA",
            symbol="EUR/USD",
            side="buy",
            amount=1000.0,
            price=1.1000,
            order_type="limit",
            created_at=datetime.now(timezone.utc),
            priority=1
        )
    
    def test_crypto_market_always_open(self, closure_handler):
        """Test that crypto markets are always considered open."""
        assert closure_handler.is_market_open(MarketType.CRYPTO) is True
        assert closure_handler.get_next_open_time(MarketType.CRYPTO) is None
    
    def test_forex_market_session_registration(self, closure_handler):
        """Test forex market session registration."""
        session_info = {
            "london": {
                "start": "08:00",
                "end": "17:00",
                "timezone": "UTC"
            }
        }
        
        closure_handler.register_market_session(MarketType.FOREX, session_info)
        
        assert MarketType.FOREX in closure_handler.market_sessions
        assert closure_handler.market_sessions[MarketType.FOREX] == session_info
    
    def test_order_queuing_when_market_closed(self, closure_handler, sample_order):
        """Test order queuing when market is closed."""
        # Mock market as closed
        with patch.object(closure_handler, 'is_market_open', return_value=False):
            closure_handler.queue_order(sample_order)
            
            queued_orders = closure_handler.get_queued_orders(MarketType.FOREX)
            assert len(queued_orders) == 1
            assert queued_orders[0].id == "test_order_1"
    
    def test_order_priority_queuing(self, closure_handler):
        """Test that orders are queued by priority."""
        with patch.object(closure_handler, 'is_market_open', return_value=False):
            # Create orders with different priorities
            low_priority_order = QueuedOrder(
                id="low_priority",
                market_type=MarketType.FOREX,
                broker_name="OANDA",
                symbol="EUR/USD",
                side="buy",
                amount=1000.0,
                order_type="market",
                created_at=datetime.now(timezone.utc),
                priority=1
            )
            
            high_priority_order = QueuedOrder(
                id="high_priority",
                market_type=MarketType.FOREX,
                broker_name="OANDA",
                symbol="EUR/USD",
                side="sell",
                amount=1000.0,
                order_type="market",
                created_at=datetime.now(timezone.utc),
                priority=5
            )
            
            closure_handler.queue_order(low_priority_order)
            closure_handler.queue_order(high_priority_order)
            
            queued_orders = closure_handler.get_queued_orders(MarketType.FOREX)
            assert len(queued_orders) == 2
            assert queued_orders[0].id == "high_priority"  # Higher priority first
            assert queued_orders[1].id == "low_priority"
    
    def test_queue_size_limit(self, closure_handler):
        """Test that queue size limit is enforced."""
        with patch.object(closure_handler, 'is_market_open', return_value=False):
            # Fill queue to capacity
            for i in range(10):
                order = QueuedOrder(
                    id=f"order_{i}",
                    market_type=MarketType.FOREX,
                    broker_name="OANDA",
                    symbol="EUR/USD",
                    side="buy",
                    amount=1000.0,
                    order_type="market",
                    created_at=datetime.now(timezone.utc)
                )
                closure_handler.queue_order(order)
            
            # Try to add one more order
            overflow_order = QueuedOrder(
                id="overflow",
                market_type=MarketType.FOREX,
                broker_name="OANDA",
                symbol="EUR/USD",
                side="buy",
                amount=1000.0,
                order_type="market",
                created_at=datetime.now(timezone.utc)
            )
            
            with pytest.raises(Exception):  # Should raise OrderQueueException
                closure_handler.queue_order(overflow_order)
    
    def test_cancel_queued_order(self, closure_handler, sample_order):
        """Test cancelling a queued order."""
        with patch.object(closure_handler, 'is_market_open', return_value=False):
            closure_handler.queue_order(sample_order)
            
            # Cancel the order
            success = closure_handler.cancel_queued_order("test_order_1", MarketType.FOREX)
            assert success is True
            
            # Check that queue is empty
            queued_orders = closure_handler.get_queued_orders(MarketType.FOREX)
            assert len(queued_orders) == 0
    
    @pytest.mark.asyncio
    async def test_order_processing_when_market_opens(self, closure_handler):
        """Test order processing when market opens."""
        callback_called = False
        
        async def mock_callback(order):
            nonlocal callback_called
            callback_called = True
            assert order.id == "test_order_1"
        
        order = QueuedOrder(
            id="test_order_1",
            market_type=MarketType.FOREX,
            broker_name="OANDA",
            symbol="EUR/USD",
            side="buy",
            amount=1000.0,
            order_type="market",
            created_at=datetime.now(timezone.utc),
            callback=mock_callback
        )
        
        # Queue order when market is closed
        with patch.object(closure_handler, 'is_market_open', return_value=False):
            closure_handler.queue_order(order)
        
        # Process orders when market opens
        with patch.object(closure_handler, 'is_market_open', return_value=True):
            await closure_handler._process_queued_orders(MarketType.FOREX)
        
        assert callback_called is True
        assert len(closure_handler.get_queued_orders(MarketType.FOREX)) == 0


class TestBrokerFailover:
    """Test broker failover and reconnection mechanisms."""
    
    @pytest.fixture
    def health_monitor(self):
        """Create a BrokerHealthMonitor instance."""
        return BrokerHealthMonitor()
    
    @pytest.fixture
    def failover_manager(self):
        """Create a BrokerFailoverManager instance."""
        return BrokerFailoverManager(FailoverStrategy.PRIORITY_BASED)
    
    @pytest.fixture
    def broker_config(self):
        """Create a sample broker configuration."""
        return BrokerConfig(
            name="OANDA",
            market_type=MarketType.FOREX,
            priority=1,
            max_retries=3,
            retry_delay=1.0,
            backoff_multiplier=2.0
        )
    
    def test_broker_registration(self, health_monitor, broker_config):
        """Test broker registration in health monitor."""
        health_monitor.register_broker(broker_config)
        
        assert "OANDA" in health_monitor.broker_status
        assert health_monitor.broker_status["OANDA"] == BrokerStatus.DISCONNECTED
        assert "OANDA" in health_monitor.connection_attempts
        assert "OANDA" in health_monitor.circuit_breaker_state
    
    def test_broker_status_update(self, health_monitor, broker_config):
        """Test broker status updates."""
        health_monitor.register_broker(broker_config)
        
        health_monitor.update_broker_status("OANDA", BrokerStatus.CONNECTED)
        assert health_monitor.broker_status["OANDA"] == BrokerStatus.CONNECTED
        
        health_monitor.update_broker_status("OANDA", BrokerStatus.FAILED, "Connection timeout")
        assert health_monitor.broker_status["OANDA"] == BrokerStatus.FAILED
    
    def test_connection_attempt_recording(self, health_monitor, broker_config):
        """Test recording connection attempts."""
        health_monitor.register_broker(broker_config)
        
        health_monitor.record_connection_attempt("OANDA", True, duration=0.5)
        attempts = health_monitor.connection_attempts["OANDA"]
        
        assert len(attempts) == 1
        assert attempts[0].success is True
        assert attempts[0].duration == 0.5
    
    def test_circuit_breaker_activation(self, health_monitor, broker_config):
        """Test circuit breaker activation after failures."""
        health_monitor.register_broker(broker_config)
        
        # Record 5 consecutive failures
        for i in range(5):
            health_monitor.record_connection_attempt("OANDA", False, f"Error {i}")
        
        assert health_monitor.is_circuit_breaker_open("OANDA") is True
        assert health_monitor.is_broker_healthy("OANDA") is False
    
    def test_failure_rate_calculation(self, health_monitor, broker_config):
        """Test failure rate calculation."""
        health_monitor.register_broker(broker_config)
        
        # Record mixed success/failure attempts
        health_monitor.record_connection_attempt("OANDA", True)
        health_monitor.record_connection_attempt("OANDA", False, "Error 1")
        health_monitor.record_connection_attempt("OANDA", False, "Error 2")
        health_monitor.record_connection_attempt("OANDA", True)
        
        failure_rate = health_monitor.get_failure_rate("OANDA")
        assert failure_rate == 0.5  # 2 failures out of 4 attempts
    
    def test_failover_manager_broker_registration(self, failover_manager, broker_config):
        """Test broker registration in failover manager."""
        failover_manager.register_broker(broker_config)
        
        assert "OANDA" in failover_manager.broker_configs
        assert failover_manager.primary_brokers[MarketType.FOREX] == "OANDA"
        assert failover_manager.active_brokers[MarketType.FOREX] == "OANDA"
    
    def test_backup_broker_registration(self, failover_manager):
        """Test backup broker registration and priority ordering."""
        primary_config = BrokerConfig(
            name="OANDA",
            market_type=MarketType.FOREX,
            priority=1
        )
        
        backup_config = BrokerConfig(
            name="MT5",
            market_type=MarketType.FOREX,
            priority=2
        )
        
        failover_manager.register_broker(primary_config)
        failover_manager.register_broker(backup_config)
        
        assert failover_manager.primary_brokers[MarketType.FOREX] == "OANDA"
        assert "MT5" in failover_manager.backup_brokers[MarketType.FOREX]
    
    @pytest.mark.asyncio
    async def test_broker_failure_handling(self, failover_manager):
        """Test broker failure handling and failover."""
        # Register primary and backup brokers
        primary_config = BrokerConfig(name="OANDA", market_type=MarketType.FOREX, priority=1)
        backup_config = BrokerConfig(name="MT5", market_type=MarketType.FOREX, priority=2)
        
        failover_manager.register_broker(primary_config)
        failover_manager.register_broker(backup_config)
        
        # Mock healthy backup broker
        with patch.object(failover_manager.health_monitor, 'is_broker_healthy') as mock_healthy:
            mock_healthy.side_effect = lambda name: name == "MT5"
            
            with patch.object(failover_manager, '_connect_to_broker') as mock_connect:
                mock_connect.return_value = None
                
                # Handle failure of primary broker
                new_broker = await failover_manager.handle_broker_failure(
                    "OANDA",
                    Exception("Connection failed"),
                    MarketType.FOREX
                )
                
                assert new_broker == "MT5"
                assert failover_manager.active_brokers[MarketType.FOREX] == "MT5"
    
    @pytest.mark.asyncio
    async def test_reconnection_with_backoff(self, failover_manager):
        """Test reconnection attempts with exponential backoff."""
        broker_config = BrokerConfig(
            name="OANDA",
            market_type=MarketType.FOREX,
            max_retries=3,
            retry_delay=0.1,  # Short delay for testing
            backoff_multiplier=2.0
        )
        
        failover_manager.register_broker(broker_config)
        
        connection_attempts = []
        
        async def mock_connect(broker_name):
            connection_attempts.append(datetime.now())
            if len(connection_attempts) < 3:
                raise Exception("Connection failed")
            # Succeed on third attempt
        
        with patch.object(failover_manager, '_connect_to_broker', side_effect=mock_connect):
            await failover_manager._reconnect_broker("OANDA")
        
        assert len(connection_attempts) == 3
        
        # Check that delays increased (approximately)
        if len(connection_attempts) >= 3:
            delay1 = (connection_attempts[1] - connection_attempts[0]).total_seconds()
            delay2 = (connection_attempts[2] - connection_attempts[1]).total_seconds()
            assert delay2 > delay1  # Exponential backoff


class TestRegulatoryHandler:
    """Test regulatory violation detection and handling."""
    
    @pytest.fixture
    def compliance_manager(self):
        """Create a RegulatoryComplianceManager instance."""
        return RegulatoryComplianceManager()
    
    @pytest.fixture
    def regulatory_monitor(self):
        """Create a RegulatoryMonitor instance."""
        return RegulatoryMonitor()
    
    @pytest.fixture
    def sample_rule(self):
        """Create a sample regulatory rule."""
        return RegulatoryRule(
            id="position_limit_rule",
            name="Position Limit Rule",
            description="Limit position size per symbol",
            market_type=MarketType.FOREX,
            jurisdiction="US",
            violation_type=ViolationType.POSITION_LIMIT_EXCEEDED,
            severity=Severity.HIGH,
            threshold_value=10000.0
        )
    
    def test_regulatory_rule_registration(self, regulatory_monitor, sample_rule):
        """Test regulatory rule registration."""
        regulatory_monitor.register_rule(sample_rule)
        
        assert "position_limit_rule" in regulatory_monitor.rules
        assert regulatory_monitor.rules["position_limit_rule"] == sample_rule
    
    def test_position_limit_checking(self, regulatory_monitor):
        """Test position limit violation detection."""
        regulatory_monitor.set_position_limits(
            MarketType.FOREX,
            {"EUR/USD": 10000.0}
        )
        
        # Test within limit
        violation = regulatory_monitor.check_position_limits(
            MarketType.FOREX,
            "EUR/USD",
            current_position=5000.0,
            proposed_change=3000.0
        )
        assert violation is None
        
        # Test exceeding limit
        violation = regulatory_monitor.check_position_limits(
            MarketType.FOREX,
            "EUR/USD",
            current_position=8000.0,
            proposed_change=5000.0
        )
        assert violation is not None
        assert violation.violation_type == ViolationType.POSITION_LIMIT_EXCEEDED
        assert violation.current_value == 13000.0
        assert violation.threshold_value == 10000.0
    
    def test_leverage_limit_checking(self, regulatory_monitor):
        """Test leverage limit violation detection."""
        violation = regulatory_monitor.check_leverage_limits(
            MarketType.FOREX,
            "account_123",
            current_leverage=60.0,
            max_leverage=50.0
        )
        
        assert violation is not None
        assert violation.violation_type == ViolationType.LEVERAGE_LIMIT_EXCEEDED
        assert violation.current_value == 60.0
        assert violation.threshold_value == 50.0
        assert "account_123" in violation.affected_accounts
    
    def test_wash_trading_detection(self, regulatory_monitor):
        """Test wash trading pattern detection."""
        # Record alternating buy/sell trades with similar prices
        trades = [
            {"symbol": "BTC/USD", "side": "buy", "price": 50000.0, "timestamp": datetime.now(timezone.utc)},
            {"symbol": "BTC/USD", "side": "sell", "price": 50010.0, "timestamp": datetime.now(timezone.utc)},
            {"symbol": "BTC/USD", "side": "buy", "price": 50005.0, "timestamp": datetime.now(timezone.utc)},
            {"symbol": "BTC/USD", "side": "sell", "price": 50015.0, "timestamp": datetime.now(timezone.utc)},
        ]
        
        for trade in trades:
            regulatory_monitor.record_trade(trade)
        
        violation = regulatory_monitor.check_wash_trading("BTC/USD")
        assert violation is not None
        assert violation.violation_type == ViolationType.WASH_TRADING
        assert "BTC/USD" in violation.affected_symbols
    
    def test_trading_hours_violation(self, regulatory_monitor):
        """Test trading hours violation detection."""
        # Test weekend trading for forex (should be violation)
        weekend_time = datetime(2024, 1, 6, 12, 0, 0, tzinfo=timezone.utc)  # Saturday
        
        violation = regulatory_monitor.check_trading_hours(MarketType.FOREX, weekend_time)
        assert violation is not None
        assert violation.violation_type == ViolationType.TRADING_HOURS_VIOLATION
        
        # Test crypto trading (should be allowed)
        violation = regulatory_monitor.check_trading_hours(MarketType.CRYPTO, weekend_time)
        assert violation is None
    
    def test_violation_resolution(self, regulatory_monitor):
        """Test violation resolution."""
        # Create a violation
        violation = regulatory_monitor._create_violation(
            rule_id="test_rule",
            violation_type=ViolationType.POSITION_LIMIT_EXCEEDED,
            severity=Severity.HIGH,
            market_type=MarketType.FOREX,
            description="Test violation"
        )
        
        violation_id = violation.id
        
        # Resolve the violation
        success = regulatory_monitor.resolve_violation(
            violation_id,
            "Position reduced to comply with limits"
        )
        
        assert success is True
        assert regulatory_monitor.violations[violation_id].resolved is True
        assert regulatory_monitor.violations[violation_id].resolution_notes == "Position reduced to comply with limits"
    
    @pytest.mark.asyncio
    async def test_corrective_action_creation(self, compliance_manager):
        """Test corrective action creation and execution."""
        # Create a violation
        violation = ViolationEvent(
            id="test_violation",
            rule_id="test_rule",
            violation_type=ViolationType.POSITION_LIMIT_EXCEEDED,
            severity=Severity.HIGH,
            market_type=MarketType.FOREX,
            jurisdiction="US",
            description="Position limit exceeded",
            detected_at=datetime.now(timezone.utc),
            affected_symbols=["EUR/USD"]
        )
        
        # Mock action handler
        action_executed = False
        
        async def mock_action_handler(action):
            nonlocal action_executed
            action_executed = True
            assert action.action_type == ActionType.POSITION_REDUCTION
        
        compliance_manager.action_handler.register_action_handler(
            ActionType.POSITION_REDUCTION,
            mock_action_handler
        )
        
        # Create corrective action
        action = await compliance_manager.action_handler.create_corrective_action(
            violation,
            ActionType.POSITION_REDUCTION,
            "Reduce EUR/USD position",
            {"symbol": "EUR/USD", "reduction_percentage": 0.5}
        )
        
        assert action_executed is True
        assert action.success is True
        assert action.executed_at is not None
    
    def test_violation_filtering(self, regulatory_monitor):
        """Test violation filtering by criteria."""
        # Create violations with different attributes
        violation1 = regulatory_monitor._create_violation(
            rule_id="rule1",
            violation_type=ViolationType.POSITION_LIMIT_EXCEEDED,
            severity=Severity.HIGH,
            market_type=MarketType.FOREX,
            description="Forex violation"
        )
        
        violation2 = regulatory_monitor._create_violation(
            rule_id="rule2",
            violation_type=ViolationType.LEVERAGE_LIMIT_EXCEEDED,
            severity=Severity.MEDIUM,
            market_type=MarketType.CRYPTO,
            description="Crypto violation"
        )
        
        # Test filtering by market type
        forex_violations = regulatory_monitor.get_violations(market_type=MarketType.FOREX)
        assert len(forex_violations) == 1
        assert forex_violations[0].market_type == MarketType.FOREX
        
        # Test filtering by severity
        high_violations = regulatory_monitor.get_violations(severity=Severity.HIGH)
        assert len(high_violations) == 1
        assert high_violations[0].severity == Severity.HIGH
        
        # Test filtering by resolved status
        unresolved_violations = regulatory_monitor.get_violations(resolved=False)
        assert len(unresolved_violations) == 2


@pytest.mark.asyncio
async def test_integrated_error_handling_scenario():
    """Test integrated error handling scenario across multiple components."""
    # Create components
    closure_handler = MarketClosureHandler()
    failover_manager = BrokerFailoverManager()
    compliance_manager = RegulatoryComplianceManager()
    
    # Register brokers
    primary_broker = BrokerConfig(
        name="OANDA",
        market_type=MarketType.FOREX,
        priority=1
    )
    backup_broker = BrokerConfig(
        name="MT5",
        market_type=MarketType.FOREX,
        priority=2
    )
    
    failover_manager.register_broker(primary_broker)
    failover_manager.register_broker(backup_broker)
    
    # Set up regulatory rules
    compliance_manager.monitor.set_position_limits(
        MarketType.FOREX,
        {"EUR/USD": 10000.0}
    )
    
    # Simulate market closure
    with patch.object(closure_handler, 'is_market_open', return_value=False):
        order = QueuedOrder(
            id="test_order",
            market_type=MarketType.FOREX,
            broker_name="OANDA",
            symbol="EUR/USD",
            side="buy",
            amount=15000.0,  # Exceeds position limit
            order_type="market",
            created_at=datetime.now(timezone.utc)
        )
        
        # Order should be queued due to market closure
        closure_handler.queue_order(order)
        queued_orders = closure_handler.get_queued_orders(MarketType.FOREX)
        assert len(queued_orders) == 1
    
    # Simulate broker failure and failover
    with patch.object(failover_manager.health_monitor, 'is_broker_healthy') as mock_healthy:
        mock_healthy.side_effect = lambda name: name == "MT5"
        
        with patch.object(failover_manager, '_connect_to_broker'):
            new_broker = await failover_manager.handle_broker_failure(
                "OANDA",
                Exception("Connection failed"),
                MarketType.FOREX
            )
            
            assert new_broker == "MT5"
    
    # Check regulatory violation
    violation = compliance_manager.monitor.check_position_limits(
        MarketType.FOREX,
        "EUR/USD",
        current_position=0.0,
        proposed_change=15000.0
    )
    
    assert violation is not None
    assert violation.violation_type == ViolationType.POSITION_LIMIT_EXCEEDED


if __name__ == "__main__":
    pytest.main([__file__])