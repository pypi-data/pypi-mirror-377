"""
Multi-market specific exception classes.

This module defines exceptions for multi-market trading scenarios including
market-specific errors, session handling, broker failover, and regulatory
compliance violations.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum

from .base_exceptions import TradingBotException, ExchangeException
from .recovery_exceptions import RecoverableException, NonRecoverableException


class MarketType(Enum):
    """Supported market types."""
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCK = "stock"
    COMMODITY = "commodity"


class MarketSpecificException(TradingBotException):
    """Base exception for market-specific errors."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        market_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.market_type = market_type
        self.market_name = market_name
        self.context['market_type'] = market_type.value
        if market_name:
            self.context['market_name'] = market_name


class MarketClosedException(MarketSpecificException):
    """Exception raised when attempting to trade in a closed market."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        next_open_time: Optional[datetime] = None,
        market_session: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, market_type, **kwargs)
        self.next_open_time = next_open_time
        self.market_session = market_session
        if next_open_time:
            self.context['next_open_time'] = next_open_time.isoformat()
        if market_session:
            self.context['market_session'] = market_session


class MarketSessionException(MarketSpecificException):
    """Exception for market session-related errors."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        session_name: Optional[str] = None,
        session_status: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, market_type, **kwargs)
        self.session_name = session_name
        self.session_status = session_status
        if session_name:
            self.context['session_name'] = session_name
        if session_status:
            self.context['session_status'] = session_status


class BrokerException(MarketSpecificException):
    """Base exception for broker-related errors."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        broker_name: str,
        broker_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, market_type, **kwargs)
        self.broker_name = broker_name
        self.broker_id = broker_id
        self.context['broker_name'] = broker_name
        if broker_id:
            self.context['broker_id'] = broker_id


class BrokerConnectionException(BrokerException, RecoverableException):
    """Exception for broker connection failures."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        broker_name: str,
        connection_type: Optional[str] = None,
        last_successful_connection: Optional[datetime] = None,
        **kwargs
    ):
        super().__init__(message, market_type, broker_name, **kwargs)
        self.connection_type = connection_type
        self.last_successful_connection = last_successful_connection
        if connection_type:
            self.context['connection_type'] = connection_type
        if last_successful_connection:
            self.context['last_successful_connection'] = last_successful_connection.isoformat()


class BrokerAuthenticationException(BrokerException, NonRecoverableException):
    """Exception for broker authentication failures."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        broker_name: str,
        auth_method: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, market_type, broker_name, **kwargs)
        self.auth_method = auth_method
        if auth_method:
            self.context['auth_method'] = auth_method


class BrokerUnavailableException(BrokerException, RecoverableException):
    """Exception when broker is temporarily unavailable."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        broker_name: str,
        maintenance_window: Optional[Dict[str, datetime]] = None,
        **kwargs
    ):
        super().__init__(message, market_type, broker_name, **kwargs)
        self.maintenance_window = maintenance_window
        if maintenance_window:
            self.context['maintenance_window'] = {
                k: v.isoformat() for k, v in maintenance_window.items()
            }


class ForexBrokerException(BrokerException):
    """Forex-specific broker exception."""
    
    def __init__(
        self,
        message: str,
        broker_name: str,
        account_type: Optional[str] = None,
        server: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, MarketType.FOREX, broker_name, **kwargs)
        self.account_type = account_type
        self.server = server
        if account_type:
            self.context['account_type'] = account_type
        if server:
            self.context['server'] = server


class CryptoBrokerException(BrokerException):
    """Crypto-specific broker exception."""
    
    def __init__(
        self,
        message: str,
        broker_name: str,
        api_version: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, MarketType.CRYPTO, broker_name, **kwargs)
        self.api_version = api_version
        if api_version:
            self.context['api_version'] = api_version


class RegulatoryViolationException(MarketSpecificException, NonRecoverableException):
    """Exception for regulatory compliance violations."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        violation_type: str,
        regulation: str,
        jurisdiction: Optional[str] = None,
        penalty: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, market_type, **kwargs)
        self.violation_type = violation_type
        self.regulation = regulation
        self.jurisdiction = jurisdiction
        self.penalty = penalty
        self.context.update({
            'violation_type': violation_type,
            'regulation': regulation
        })
        if jurisdiction:
            self.context['jurisdiction'] = jurisdiction
        if penalty:
            self.context['penalty'] = penalty


class OrderQueueException(MarketSpecificException):
    """Exception for order queuing errors."""
    
    def __init__(
        self,
        message: str,
        market_type: MarketType,
        queue_size: Optional[int] = None,
        max_queue_size: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, market_type, **kwargs)
        self.queue_size = queue_size
        self.max_queue_size = max_queue_size
        if queue_size is not None:
            self.context['queue_size'] = queue_size
        if max_queue_size is not None:
            self.context['max_queue_size'] = max_queue_size


class CrossMarketException(TradingBotException):
    """Exception for cross-market operations."""
    
    def __init__(
        self,
        message: str,
        involved_markets: List[MarketType],
        operation_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.involved_markets = involved_markets
        self.operation_type = operation_type
        self.context['involved_markets'] = [m.value for m in involved_markets]
        if operation_type:
            self.context['operation_type'] = operation_type


class CorrelationException(CrossMarketException):
    """Exception for cross-market correlation errors."""
    
    def __init__(
        self,
        message: str,
        involved_markets: List[MarketType],
        correlation_threshold: Optional[float] = None,
        current_correlation: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, involved_markets, "correlation_analysis", **kwargs)
        self.correlation_threshold = correlation_threshold
        self.current_correlation = current_correlation
        if correlation_threshold is not None:
            self.context['correlation_threshold'] = correlation_threshold
        if current_correlation is not None:
            self.context['current_correlation'] = current_correlation


class ArbitrageException(CrossMarketException):
    """Exception for arbitrage operation errors."""
    
    def __init__(
        self,
        message: str,
        involved_markets: List[MarketType],
        arbitrage_type: Optional[str] = None,
        expected_profit: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, involved_markets, "arbitrage", **kwargs)
        self.arbitrage_type = arbitrage_type
        self.expected_profit = expected_profit
        if arbitrage_type:
            self.context['arbitrage_type'] = arbitrage_type
        if expected_profit is not None:
            self.context['expected_profit'] = expected_profit


class FailoverException(RecoverableException):
    """Exception during broker/exchange failover operations."""
    
    def __init__(
        self,
        message: str,
        primary_broker: str,
        backup_brokers: List[str],
        failover_reason: str,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.primary_broker = primary_broker
        self.backup_brokers = backup_brokers
        self.failover_reason = failover_reason
        self.context.update({
            'primary_broker': primary_broker,
            'backup_brokers': backup_brokers,
            'failover_reason': failover_reason
        })


class ReconnectionException(RecoverableException):
    """Exception during reconnection attempts."""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        attempt_count: int,
        max_attempts: int,
        last_error: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.attempt_count = attempt_count
        self.max_attempts = max_attempts
        self.last_error = last_error
        self.context.update({
            'service_name': service_name,
            'attempt_count': attempt_count,
            'max_attempts': max_attempts
        })
        if last_error:
            self.context['last_error'] = last_error


class DataSynchronizationException(CrossMarketException):
    """Exception for cross-market data synchronization errors."""
    
    def __init__(
        self,
        message: str,
        involved_markets: List[MarketType],
        sync_type: str,
        timestamp_drift: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, involved_markets, "data_sync", **kwargs)
        self.sync_type = sync_type
        self.timestamp_drift = timestamp_drift
        self.context['sync_type'] = sync_type
        if timestamp_drift is not None:
            self.context['timestamp_drift'] = timestamp_drift


class PositionSyncException(CrossMarketException):
    """Exception for cross-market position synchronization errors."""
    
    def __init__(
        self,
        message: str,
        involved_markets: List[MarketType],
        symbol: str,
        expected_position: float,
        actual_position: float,
        **kwargs
    ):
        super().__init__(message, involved_markets, "position_sync", **kwargs)
        self.symbol = symbol
        self.expected_position = expected_position
        self.actual_position = actual_position
        self.context.update({
            'symbol': symbol,
            'expected_position': expected_position,
            'actual_position': actual_position
        })