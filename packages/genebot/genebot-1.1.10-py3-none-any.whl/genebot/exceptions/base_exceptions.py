"""
Base exception classes for the trading bot.

This module defines the core exception hierarchy that provides structured
error handling across all trading bot components.
"""

from typing import Optional, Dict, Any
import traceback
from datetime import datetime, timezone


class TradingBotException(Exception):
    """Base exception for all trading bot errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now(timezone.utc)
        self.traceback_str = traceback.format_exc() if original_exception else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback_str,
            'original_exception': str(self.original_exception) if self.original_exception else None
        }


class ExchangeException(TradingBotException):
    """Exception for exchange-related errors."""
    
    def __init__(
        self,
        message: str,
        exchange_name: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message, error_code, context, original_exception)
        self.exchange_name = exchange_name
        if exchange_name:
            self.context['exchange'] = exchange_name


class ConnectionException(ExchangeException):
    """Exception for connection-related errors."""
    
    def __init__(
        self,
        message: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.host = host
        self.port = port
        self.timeout = timeout
        if host:
            self.context['host'] = host
        if port:
            self.context['port'] = port
        if timeout:
            self.context['timeout'] = timeout


class NetworkException(ExchangeException):
    """Exception for network-related errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.retry_after = retry_after
        if status_code:
            self.context['status_code'] = status_code
        if retry_after:
            self.context['retry_after'] = retry_after


class AuthenticationException(ExchangeException):
    """Exception for authentication-related errors."""
    pass


class InsufficientFundsException(ExchangeException):
    """Exception for insufficient funds errors."""
    
    def __init__(
        self,
        message: str,
        required_amount: Optional[float] = None,
        available_amount: Optional[float] = None,
        currency: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.required_amount = required_amount
        self.available_amount = available_amount
        self.currency = currency
        if required_amount:
            self.context['required_amount'] = required_amount
        if available_amount:
            self.context['available_amount'] = available_amount
        if currency:
            self.context['currency'] = currency


class InsufficientMarginException(ExchangeException):
    """Exception for insufficient margin errors."""
    
    def __init__(
        self,
        message: str,
        required_margin: Optional[float] = None,
        available_margin: Optional[float] = None,
        currency: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.required_margin = required_margin
        self.available_margin = available_margin
        self.currency = currency
        if required_margin:
            self.context['required_margin'] = required_margin
        if available_margin:
            self.context['available_margin'] = available_margin
        if currency:
            self.context['currency'] = currency


class OrderException(ExchangeException):
    """Exception for order-related errors."""
    
    def __init__(
        self,
        message: str,
        order_id: Optional[str] = None,
        symbol: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.order_id = order_id
        self.symbol = symbol
        if order_id:
            self.context['order_id'] = order_id
        if symbol:
            self.context['symbol'] = symbol


class PositionException(TradingBotException):
    """Exception for position-related errors."""
    
    def __init__(
        self,
        message: str,
        symbol: Optional[str] = None,
        position_size: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.symbol = symbol
        self.position_size = position_size
        if symbol:
            self.context['symbol'] = symbol
        if position_size:
            self.context['position_size'] = position_size


class StrategyException(TradingBotException):
    """Exception for strategy-related errors."""
    
    def __init__(
        self,
        message: str,
        strategy_name: Optional[str] = None,
        symbol: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.strategy_name = strategy_name
        self.symbol = symbol
        if strategy_name:
            self.context['strategy'] = strategy_name
        if symbol:
            self.context['symbol'] = symbol


class RiskException(TradingBotException):
    """Exception for risk management violations."""
    
    def __init__(
        self,
        message: str,
        risk_type: Optional[str] = None,
        threshold_value: Optional[float] = None,
        current_value: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.risk_type = risk_type
        self.threshold_value = threshold_value
        self.current_value = current_value
        if risk_type:
            self.context['risk_type'] = risk_type
        if threshold_value:
            self.context['threshold_value'] = threshold_value
        if current_value:
            self.context['current_value'] = current_value


class DataException(TradingBotException):
    """Exception for data-related errors."""
    
    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.data_type = data_type
        self.symbol = symbol
        self.timeframe = timeframe
        if data_type:
            self.context['data_type'] = data_type
        if symbol:
            self.context['symbol'] = symbol
        if timeframe:
            self.context['timeframe'] = timeframe


class ConfigurationException(TradingBotException):
    """Exception for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.config_value = config_value
        if config_key:
            self.context['config_key'] = config_key
        if config_value is not None:
            self.context['config_value'] = str(config_value)


class ValidationException(TradingBotException):
    """Exception for validation errors."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule
        if field_name:
            self.context['field_name'] = field_name
        if field_value is not None:
            self.context['field_value'] = str(field_value)
        if validation_rule:
            self.context['validation_rule'] = validation_rule


class BacktestException(TradingBotException):
    """Exception for backtesting-related errors."""
    
    def __init__(
        self,
        message: str,
        strategy_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.strategy_name = strategy_name
        self.start_date = start_date
        self.end_date = end_date
        if strategy_name:
            self.context['strategy'] = strategy_name
        if start_date:
            self.context['start_date'] = start_date
        if end_date:
            self.context['end_date'] = end_date