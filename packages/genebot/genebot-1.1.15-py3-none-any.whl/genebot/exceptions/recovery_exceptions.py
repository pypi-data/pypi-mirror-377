"""
Recovery-related exception classes.

This module defines exceptions that indicate whether errors are recoverable
and how the system should handle recovery attempts.
"""

from typing import Optional, Dict, Any
from .base_exceptions import TradingBotException


class RecoverableException(TradingBotException):
    """Base class for exceptions that can be recovered from."""
    
    def __init__(
        self,
        message: str,
        recovery_strategy: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.recovery_strategy = recovery_strategy
        self.max_retries = max_retries
        if recovery_strategy:
            self.context['recovery_strategy'] = recovery_strategy
        self.context['max_retries'] = max_retries


class NonRecoverableException(TradingBotException):
    """Base class for exceptions that cannot be recovered from."""
    
    def __init__(
        self,
        message: str,
        shutdown_required: bool = False,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.shutdown_required = shutdown_required
        self.context['shutdown_required'] = shutdown_required


class RetryableException(RecoverableException):
    """Exception that should trigger retry logic."""
    
    def __init__(
        self,
        message: str,
        retry_delay: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_delay: float = 60.0,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_delay = retry_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
        self.context.update({
            'retry_delay': retry_delay,
            'backoff_multiplier': backoff_multiplier,
            'max_delay': max_delay
        })


class CircuitBreakerException(TradingBotException):
    """Exception raised when circuit breaker is open."""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        failure_count: int,
        threshold: int,
        timeout: float,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.failure_count = failure_count
        self.threshold = threshold
        self.timeout = timeout
        self.context.update({
            'service_name': service_name,
            'failure_count': failure_count,
            'threshold': threshold,
            'timeout': timeout
        })