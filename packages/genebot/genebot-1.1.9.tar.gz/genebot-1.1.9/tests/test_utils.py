"""
Test utilities for trading bot tests.

This module provides common utilities, mocks, and fixtures for testing
the trading bot components.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock
import random

from src.models.data_models import (
    MarketData, TradingSignal, SignalAction, Order, Position,
    OrderSide, OrderType, OrderStatus
)


def create_test_config() -> Dict[str, Any]:
    """Create a test configuration dictionary."""
    return {
        'app_name': 'TestTradingBot',
        'version': '1.0.0',
        'debug': True,
        'dry_run': True,
        'base_currency': 'USDT',
        'exchanges': {
            'binance': {
                'exchange_type': 'binance',
                'api_key': 'test_api_key',
                'api_secret': 'test_api_secret',
                'sandbox': True,
                'rate_limit': 1200,
                'timeout': 30,
                'enabled': True
            }
        },
        'strategies': {
            'moving_average': {
                'strategy_type': 'moving_average',
                'enabled': True,
                'symbols': ['BTC/USDT', 'ETH/USDT'],
                'timeframe': '1h',
                'parameters': {
                    'fast_period': 10,
                    'slow_period': 20
                },
                'max_positions': 2
            },
            'rsi': {
                'strategy_type': 'rsi',
                'enabled': True,
                'symbols': ['BTC/USDT'],
                'timeframe': '1h',
                'parameters': {
                    'period': 14,
                    'oversold': 30,
                    'overbought': 70
                },
                'max_positions': 1
            }
        },
        'risk': {
            'max_position_size': 0.1,
            'max_daily_loss': 0.05,
            'max_drawdown': 0.15,
            'stop_loss_percentage': 0.02,
            'max_open_positions': 5,
            'position_sizing_method': 'fixed_fraction',
            'risk_per_trade': 0.01,
            'close_positions_on_shutdown': False
        },
        'database': {
            'database_type': 'sqlite',
            'database_url': 'sqlite:///:memory:',
            'pool_size': 5,
            'echo': False
        },
        'logging': {
            'log_level': 'DEBUG',
            'log_format': 'standard',
            'log_file': 'logs/test_trading_bot.log',
            'max_file_size': 10485760,
            'backup_count': 5
        }
    }


def create_mock_market_data(
    symbol: str = "BTC/USDT",
    timestamp: Optional[datetime] = None,
    open_price: float = 50000.0,
    high_price: Optional[float] = None,
    low_price: Optional[float] = None,
    close_price: Optional[float] = None,
    volume: float = 1000.0
) -> MarketData:
    """Create mock market data for testing."""
    if timestamp is None:
        timestamp = datetime.now()
    
    if high_price is None:
        high_price = open_price * (1 + random.uniform(0, 0.02))
    
    if low_price is None:
        low_price = open_price * (1 - random.uniform(0, 0.02))
    
    if close_price is None:
        close_price = open_price + random.uniform(-500, 500)
    
    return MarketData(
        symbol=symbol,
        timestamp=timestamp,
        open=Decimal(str(open_price)),
        high=Decimal(str(high_price)),
        low=Decimal(str(low_price)),
        close=Decimal(str(close_price)),
        volume=Decimal(str(volume)),
        exchange="binance"
    )


def create_mock_trading_signal(
    symbol: str = "BTC/USDT",
    action: SignalAction = SignalAction.BUY,
    confidence: float = 0.85,
    price: Optional[Decimal] = None,
    timestamp: Optional[datetime] = None,
    strategy_name: str = "test_strategy"
) -> TradingSignal:
    """Create mock trading signal for testing."""
    if timestamp is None:
        timestamp = datetime.now()
    
    if price is None:
        price = Decimal("50000.0")
    
    return TradingSignal(
        symbol=symbol,
        action=action,
        confidence=confidence,
        price=price,
        timestamp=timestamp,
        strategy_name=strategy_name,
        metadata={"test": True}
    )


def create_mock_order(
    symbol: str = "BTC/USDT",
    side: OrderSide = OrderSide.BUY,
    amount: Decimal = Decimal("0.1"),
    price: Decimal = Decimal("50000.0"),
    order_type: OrderType = OrderType.LIMIT,
    status: OrderStatus = OrderStatus.OPEN,
    order_id: str = "test_order_123"
) -> Order:
    """Create mock order for testing."""
    return Order(
        id=order_id,
        symbol=symbol,
        side=side,
        amount=amount,
        price=price,
        order_type=order_type,
        status=status,
        timestamp=datetime.now(),
        exchange="binance",
        filled_amount=Decimal("0"),
        remaining_amount=amount,
        average_price=None,
        fees=Decimal("0"),
        metadata={}
    )


def create_mock_position(
    symbol: str = "BTC/USDT",
    side: str = "long",
    size: Decimal = Decimal("0.1"),
    entry_price: Decimal = Decimal("50000.0"),
    current_price: Optional[Decimal] = None
) -> Position:
    """Create mock position for testing."""
    if current_price is None:
        current_price = entry_price
    
    unrealized_pnl = (current_price - entry_price) * size if side == "long" else (entry_price - current_price) * size
    
    return Position(
        symbol=symbol,
        side=side,
        size=size,
        entry_price=entry_price,
        current_price=current_price,
        unrealized_pnl=unrealized_pnl,
        timestamp=datetime.now(),
        exchange="binance"
    )


class MockExchange:
    """Mock exchange adapter for testing."""
    
    def __init__(self, name: str = "binance"):
        self.name = name
        self.connected = False
        self.authenticated = False
        self.orders = {}
        self.positions = {}
        self.balance = {
            'USDT': {'free': Decimal('10000'), 'used': Decimal('0'), 'total': Decimal('10000')},
            'BTC': {'free': Decimal('0'), 'used': Decimal('0'), 'total': Decimal('0')}
        }
    
    async def connect(self) -> bool:
        """Mock connect method."""
        self.connected = True
        return True
    
    async def disconnect(self) -> None:
        """Mock disconnect method."""
        self.connected = False
    
    async def authenticate(self) -> bool:
        """Mock authenticate method."""
        self.authenticated = True
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check method."""
        return {
            'status': 'ok',
            'connected': self.connected,
            'authenticated': self.authenticated,
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_markets(self) -> Dict[str, Dict[str, Any]]:
        """Mock get markets method."""
        return {
            'BTC/USDT': {
                'id': 'BTCUSDT',
                'symbol': 'BTC/USDT',
                'base': 'BTC',
                'quote': 'USDT',
                'active': True,
                'precision': {'amount': 8, 'price': 2},
                'limits': {
                    'amount': {'min': 0.00001, 'max': 1000},
                    'price': {'min': 0.01, 'max': 1000000}
                }
            }
        }
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Mock get ticker method."""
        return {
            'symbol': symbol,
            'bid': 49950.0,
            'ask': 50050.0,
            'last': 50000.0,
            'volume': 1000.0,
            'timestamp': datetime.now().timestamp()
        }
    
    async def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
                        since: Optional[datetime] = None, 
                        limit: Optional[int] = None) -> List[MarketData]:
        """Mock get OHLCV method."""
        if limit is None:
            limit = 100
        
        data = []
        base_time = since or (datetime.now() - timedelta(hours=limit))
        
        for i in range(limit):
            timestamp = base_time + timedelta(hours=i)
            data.append(create_mock_market_data(symbol=symbol, timestamp=timestamp))
        
        return data
    
    async def get_balance(self) -> Dict[str, Dict[str, Decimal]]:
        """Mock get balance method."""
        return self.balance
    
    async def create_order(self, symbol: str, side: OrderSide, amount: Decimal,
                          order_type: OrderType = OrderType.MARKET,
                          price: Optional[Decimal] = None,
                          params: Optional[Dict[str, Any]] = None) -> Order:
        """Mock create order method."""
        order_id = f"order_{len(self.orders) + 1}"
        
        order = create_mock_order(
            symbol=symbol,
            side=side,
            amount=amount,
            price=price or Decimal("50000.0"),
            order_type=order_type,
            order_id=order_id
        )
        
        self.orders[order_id] = order
        return order
    
    async def cancel_order(self, order_id: str, symbol: str) -> Order:
        """Mock cancel order method."""
        if order_id in self.orders:
            order = self.orders[order_id]
            order.status = OrderStatus.CANCELLED
            return order
        else:
            raise Exception(f"Order {order_id} not found")
    
    async def get_order(self, order_id: str, symbol: str) -> Order:
        """Mock get order method."""
        if order_id in self.orders:
            return self.orders[order_id]
        else:
            raise Exception(f"Order {order_id} not found")
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Mock get open orders method."""
        orders = []
        for order in self.orders.values():
            if order.status == OrderStatus.OPEN:
                if symbol is None or order.symbol == symbol:
                    orders.append(order)
        return orders
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Mock get positions method."""
        positions = []
        for position in self.positions.values():
            if symbol is None or position.symbol == symbol:
                positions.append(position)
        return positions
    
    def validate_credentials(self) -> bool:
        """Mock validate credentials method."""
        return True
    
    def get_trading_fees(self, symbol: Optional[str] = None) -> Dict[str, Decimal]:
        """Mock get trading fees method."""
        return {
            'maker': Decimal('0.001'),
            'taker': Decimal('0.001')
        }
    
    def get_minimum_order_size(self, symbol: str) -> Decimal:
        """Mock get minimum order size method."""
        return Decimal('0.00001')


class MockDatabase:
    """Mock database manager for testing."""
    
    def __init__(self):
        self.connected = False
        self.data = {}
        self.tables_created = False
    
    def create_tables(self) -> None:
        """Mock create tables method."""
        self.tables_created = True
    
    async def initialize(self) -> bool:
        """Mock initialize method."""
        self.connected = True
        return True
    
    def close(self) -> None:
        """Mock close method (synchronous)."""
        self.connected = False
    
    async def close_async(self) -> None:
        """Mock close method (asynchronous)."""
        self.connected = False
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check method."""
        return {
            'status': 'ok',
            'connected': self.connected,
            'timestamp': datetime.now().isoformat()
        }
    
    async def execute_query(self, query: str, params: Optional[Dict] = None):
        """Mock execute query method."""
        return []
    
    async def insert_market_data(self, market_data: MarketData):
        """Mock insert market data method."""
        key = f"{market_data.symbol}_{market_data.timestamp}"
        self.data[key] = market_data
    
    async def get_market_data(self, symbol: str, start_time: datetime, end_time: datetime) -> List[MarketData]:
        """Mock get market data method."""
        return [create_mock_market_data(symbol=symbol) for _ in range(10)]


class MockStrategy:
    """Mock strategy for testing."""
    
    def __init__(self, name: str = "test_strategy"):
        self.name = name
        self.enabled = True
        self.running = False
        self.parameters = {}
        self.risk_limits = {}
    
    def start(self) -> bool:
        """Mock start method."""
        self.running = True
        return True
    
    def stop(self) -> bool:
        """Mock stop method."""
        self.running = False
        return True
    
    def process_market_data(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """Mock process market data method."""
        if market_data and random.random() > 0.7:  # 30% chance of signal
            return create_mock_trading_signal(
                symbol=market_data[-1].symbol,
                strategy_name=self.name
            )
        return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Mock get performance metrics method."""
        return {
            'total_signals': 10,
            'successful_signals': 7,
            'win_rate': 0.7,
            'average_confidence': 0.85
        }


def create_market_data_series(
    symbol: str = "BTC/USDT",
    count: int = 100,
    start_price: float = 50000.0,
    volatility: float = 0.02
) -> List[MarketData]:
    """Create a series of market data for testing."""
    data = []
    current_price = start_price
    base_time = datetime.now() - timedelta(hours=count)
    
    for i in range(count):
        timestamp = base_time + timedelta(hours=i)
        
        # Simulate price movement
        change = random.uniform(-volatility, volatility)
        open_price = current_price
        close_price = current_price * (1 + change)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, volatility/2))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, volatility/2))
        
        data.append(create_mock_market_data(
            symbol=symbol,
            timestamp=timestamp,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            volume=random.uniform(500, 2000)
        ))
        
        current_price = close_price
    
    return data


def assert_signal_valid(signal: TradingSignal):
    """Assert that a trading signal is valid."""
    assert signal.symbol is not None
    assert signal.action in [SignalAction.BUY, SignalAction.SELL, SignalAction.HOLD]
    assert 0.0 <= signal.confidence <= 1.0
    assert signal.price > 0
    assert signal.timestamp is not None
    assert signal.strategy_name is not None


def assert_order_valid(order: Order):
    """Assert that an order is valid."""
    assert order.id is not None
    assert order.symbol is not None
    assert order.side in [OrderSide.BUY, OrderSide.SELL]
    assert order.amount > 0
    assert order.price > 0
    assert order.order_type in [OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT]
    assert order.status in [OrderStatus.OPEN, OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]
    assert order.timestamp is not None


def assert_position_valid(position: Position):
    """Assert that a position is valid."""
    assert position.symbol is not None
    assert position.side in ["long", "short"]
    assert position.size != 0
    assert position.entry_price > 0
    assert position.current_price > 0
    assert position.timestamp is not None