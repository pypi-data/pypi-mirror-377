"""
Retry handler with exponential backoff.

This module provides retry logic for network operations and other potentially
transient failures, implementing exponential backoff with jitter.
"""

import asyncio
import random
import time
import logging
from typing import Callable, Any, Optional, Type, Union, Tuple
from functools import wraps

from ..exceptions import RetryableException, NetworkException, ExchangeException


logger = logging.getLogger(__name__)


class RetryHandler:
    """Handles retry logic with exponential backoff and jitter."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
    ):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            backoff_multiplier: Multiplier for exponential backoff
            max_delay: Maximum delay between retries
            jitter: Whether to add random jitter to delays
            retryable_exceptions: Tuple of exception types that should trigger retries
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (
            RetryableException,
            NetworkException,
            ConnectionError,
            TimeoutError
        )
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if an exception should trigger a retry."""
        if attempt >= self.max_retries:
            return False
        
        # Check if it's a retryable exception type
        if isinstance(exception, self.retryable_exceptions):
            return True
        
        # Special handling for specific exception types
        if isinstance(exception, ExchangeException):
            # Don't retry authentication errors
            if "authentication" in str(exception).lower():
                return False
            # Don't retry insufficient funds
            if "insufficient" in str(exception).lower():
                return False
            return True
        
        return False
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self.should_retry(e, attempt):
                    func_name = getattr(func, '__name__', 'unknown_function')
                    logger.error(
                        f"Function {func_name} failed permanently after {attempt} attempts: {e}"
                    )
                    raise
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    func_name = getattr(func, '__name__', 'unknown_function')
                    logger.warning(
                        f"Function {func_name} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
        
        # This should never be reached, but just in case
        raise last_exception
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self.should_retry(e, attempt):
                    func_name = getattr(func, '__name__', 'unknown_function')
                    logger.error(
                        f"Async function {func_name} failed permanently after {attempt} attempts: {e}"
                    )
                    raise
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    func_name = getattr(func, '__name__', 'unknown_function')
                    logger.warning(
                        f"Async function {func_name} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    await asyncio.sleep(delay)
        
        # This should never be reached, but just in case
        raise last_exception


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
):
    """
    Decorator for adding retry logic with exponential backoff to functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff
        max_delay: Maximum delay between retries
        jitter: Whether to add random jitter to delays
        retryable_exceptions: Tuple of exception types that should trigger retries
    """
    def decorator(func: Callable) -> Callable:
        retry_handler = RetryHandler(
            max_retries=max_retries,
            initial_delay=initial_delay,
            backoff_multiplier=backoff_multiplier,
            max_delay=max_delay,
            jitter=jitter,
            retryable_exceptions=retryable_exceptions
        )
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await retry_handler.execute_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return retry_handler.execute(func, *args, **kwargs)
            return sync_wrapper
    
    return decorator


class NetworkRetryHandler(RetryHandler):
    """Specialized retry handler for network operations."""
    
    def __init__(self, **kwargs):
        # Default settings optimized for network operations
        defaults = {
            'max_retries': 5,
            'initial_delay': 0.5,
            'backoff_multiplier': 1.5,
            'max_delay': 30.0,
            'jitter': True,
            'retryable_exceptions': (
                NetworkException,
                ConnectionError,
                TimeoutError,
                OSError,  # Network-related OS errors
            )
        }
        defaults.update(kwargs)
        super().__init__(**defaults)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Enhanced retry logic for network operations."""
        if attempt >= self.max_retries:
            return False
        
        # Check HTTP status codes for retryable errors
        if hasattr(exception, 'status_code'):
            status_code = exception.status_code
            # Retry on server errors and rate limits
            if status_code in [429, 500, 502, 503, 504]:
                return True
            # Don't retry on client errors (except rate limits)
            if 400 <= status_code < 500:
                return False
        
        return super().should_retry(exception, attempt)