"""
Circuit breaker pattern implementation.

This module provides circuit breaker functionality to prevent cascading failures
and provide graceful degradation when external services are unavailable.
"""

import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict
from functools import wraps

from ..exceptions import CircuitBreakerException, ExchangeException


logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


class CircuitBreaker:
    """
    Circuit breaker implementation for preventing cascading failures.
    
    The circuit breaker monitors failures and opens when failure threshold
    is exceeded, preventing further calls to the failing service.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception,
        success_threshold: int = 3
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Name of the circuit breaker for logging
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
            expected_exception: Exception type that counts as failure
            success_threshold: Number of successes needed to close circuit from half-open
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self.state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing)."""
        return self.state == CircuitState.HALF_OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.timeout
    
    async def _change_state(self, new_state: CircuitState):
        """Change circuit breaker state with logging."""
        old_state = self.state
        self.state = new_state
        
        if old_state != new_state:
            logger.info(
                f"Circuit breaker '{self.name}' state changed: {old_state.value} -> {new_state.value}"
            )
    
    async def _record_success(self):
        """Record a successful operation."""
        async with self._lock:
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    await self._change_state(CircuitState.CLOSED)
                    self.success_count = 0
                    logger.info(f"Circuit breaker '{self.name}' closed after successful recovery")
    
    async def _record_failure(self, exception: Exception):
        """Record a failed operation."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            self.success_count = 0
            
            if self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    await self._change_state(CircuitState.OPEN)
                    logger.warning(
                        f"Circuit breaker '{self.name}' opened after {self.failure_count} failures. "
                        f"Last error: {exception}"
                    )
            elif self.state == CircuitState.HALF_OPEN:
                await self._change_state(CircuitState.OPEN)
                logger.warning(f"Circuit breaker '{self.name}' reopened due to failure during test")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerException: When circuit is open
        """
        # Check if circuit should transition from open to half-open
        if self.state == CircuitState.OPEN and self._should_attempt_reset():
            async with self._lock:
                if self.state == CircuitState.OPEN and self._should_attempt_reset():
                    await self._change_state(CircuitState.HALF_OPEN)
                    logger.info(f"Circuit breaker '{self.name}' attempting recovery (half-open)")
        
        # Fail fast if circuit is open
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerException(
                f"Circuit breaker '{self.name}' is open",
                service_name=self.name,
                failure_count=self.failure_count,
                threshold=self.failure_threshold,
                timeout=self.timeout
            )
        
        # Execute function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self._record_success()
            return result
            
        except self.expected_exception as e:
            await self._record_failure(e)
            raise
        except Exception as e:
            # Unexpected exceptions don't count as failures
            logger.warning(f"Unexpected exception in circuit breaker '{self.name}': {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'failure_threshold': self.failure_threshold,
            'success_threshold': self.success_threshold,
            'timeout': self.timeout,
            'last_failure_time': self.last_failure_time
        }


class CircuitBreakerManager:
    """Manages multiple circuit breakers."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def get_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception,
        success_threshold: int = 3
    ) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                timeout=timeout,
                expected_exception=expected_exception,
                success_threshold=success_threshold
            )
        return self.circuit_breakers[name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {name: cb.get_stats() for name, cb in self.circuit_breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers to closed state."""
        for cb in self.circuit_breakers.values():
            cb.state = CircuitState.CLOSED
            cb.failure_count = 0
            cb.success_count = 0
            cb.last_failure_time = None


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 60.0,
    expected_exception: type = ExchangeException,
    success_threshold: int = 3
):
    """
    Decorator for adding circuit breaker protection to functions.
    
    Args:
        name: Name of the circuit breaker
        failure_threshold: Number of failures before opening circuit
        timeout: Time in seconds before attempting to close circuit
        expected_exception: Exception type that counts as failure
        success_threshold: Number of successes needed to close circuit
    """
    def decorator(func: Callable) -> Callable:
        cb = circuit_breaker_manager.get_circuit_breaker(
            name=name,
            failure_threshold=failure_threshold,
            timeout=timeout,
            expected_exception=expected_exception,
            success_threshold=success_threshold
        )
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await cb.call(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(cb.call(func, *args, **kwargs))
            return sync_wrapper
    
    return decorator