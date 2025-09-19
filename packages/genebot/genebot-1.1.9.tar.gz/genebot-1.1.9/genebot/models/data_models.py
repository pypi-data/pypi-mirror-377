"""Core data models using dataclasses for type safety and validation."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
from enum import Enum

# Import market types for multi-market support
from ..markets.types import MarketType, UnifiedSymbol


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class SignalAction(Enum):
    """Trading signal action enumeration."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class SessionInfo:
    """Market session context information."""
    
    session_name: str
    is_active: bool
    next_open: Optional[datetime] = None
    next_close: Optional[datetime] = None
    market_type: Optional[MarketType] = None
    
    def __post_init__(self):
        """Validate session info after initialization."""
        if not self.session_name:
            raise ValueError("Session name cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_name": self.session_name,
            "is_active": self.is_active,
            "next_open": self.next_open.isoformat() if self.next_open else None,
            "next_close": self.next_close.isoformat() if self.next_close else None,
            "market_type": self.market_type.value if self.market_type else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionInfo':
        """Create SessionInfo from dictionary."""
        return cls(
            session_name=data["session_name"],
            is_active=data["is_active"],
            next_open=datetime.fromisoformat(data["next_open"]) if data.get("next_open") else None,
            next_close=datetime.fromisoformat(data["next_close"]) if data.get("next_close") else None,
            market_type=MarketType(data["market_type"]) if data.get("market_type") else None,
        )


@dataclass
class MarketData:
    """Market data representation with OHLCV information."""
    
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    exchange: str
    
    def __post_init__(self):
        """Validate market data after initialization."""
        if self.high < self.low:
            raise ValueError("High price cannot be less than low price")
        if self.open < 0 or self.high < 0 or self.low < 0 or self.close < 0:
            raise ValueError("Prices cannot be negative")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if not self.exchange:
            raise ValueError("Exchange cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "open": str(self.open),
            "high": str(self.high),
            "low": str(self.low),
            "close": str(self.close),
            "volume": str(self.volume),
            "exchange": self.exchange,
        }


@dataclass
class UnifiedMarketData:
    """Enhanced market data representation with multi-market support."""
    
    symbol: UnifiedSymbol
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    source: str  # Exchange or broker name
    market_type: MarketType
    session_info: Optional[SessionInfo] = None
    
    def __post_init__(self):
        """Validate unified market data after initialization."""
        if self.high < self.low:
            raise ValueError("High price cannot be less than low price")
        if self.open < 0 or self.high < 0 or self.low < 0 or self.close < 0:
            raise ValueError("Prices cannot be negative")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
        if not self.source:
            raise ValueError("Source cannot be empty")
        
        # Validate market type consistency
        if self.symbol.market_type != self.market_type:
            raise ValueError("Symbol market type must match data market type")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "symbol": {
                "base_asset": self.symbol.base_asset,
                "quote_asset": self.symbol.quote_asset,
                "market_type": self.symbol.market_type.value,
                "native_symbol": self.symbol.native_symbol,
            },
            "timestamp": self.timestamp.isoformat(),
            "open": str(self.open),
            "high": str(self.high),
            "low": str(self.low),
            "close": str(self.close),
            "volume": str(self.volume),
            "source": self.source,
            "market_type": self.market_type.value,
            "session_info": self.session_info.to_dict() if self.session_info else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedMarketData':
        """Create UnifiedMarketData from dictionary."""
        symbol_data = data["symbol"]
        symbol = UnifiedSymbol(
            base_asset=symbol_data["base_asset"],
            quote_asset=symbol_data["quote_asset"],
            market_type=MarketType(symbol_data["market_type"]),
            native_symbol=symbol_data["native_symbol"]
        )
        
        session_info = None
        if data.get("session_info"):
            session_info = SessionInfo.from_dict(data["session_info"])
        
        return cls(
            symbol=symbol,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            open=Decimal(data["open"]),
            high=Decimal(data["high"]),
            low=Decimal(data["low"]),
            close=Decimal(data["close"]),
            volume=Decimal(data["volume"]),
            source=data["source"],
            market_type=MarketType(data["market_type"]),
            session_info=session_info,
        )
    
    @classmethod
    def from_legacy_market_data(cls, market_data: MarketData, 
                               market_type: MarketType,
                               session_info: Optional[SessionInfo] = None) -> 'UnifiedMarketData':
        """Convert legacy MarketData to UnifiedMarketData."""
        # Parse symbol based on market type
        if market_type == MarketType.CRYPTO:
            symbol = UnifiedSymbol.from_crypto_symbol(market_data.symbol)
        elif market_type == MarketType.FOREX:
            symbol = UnifiedSymbol.from_forex_symbol(market_data.symbol)
        else:
            raise ValueError(f"Unsupported market type: {market_type}")
        
        return cls(
            symbol=symbol,
            timestamp=market_data.timestamp,
            open=market_data.open,
            high=market_data.high,
            low=market_data.low,
            close=market_data.close,
            volume=market_data.volume,
            source=market_data.exchange,
            market_type=market_type,
            session_info=session_info,
        )
    
    def to_legacy_market_data(self) -> MarketData:
        """Convert to legacy MarketData format for backward compatibility."""
        return MarketData(
            symbol=self.symbol.native_symbol,
            timestamp=self.timestamp,
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
            exchange=self.source,
        )


@dataclass
class TradingSignal:
    """Trading signal generated by strategies."""
    
    symbol: str
    action: SignalAction
    confidence: float
    timestamp: datetime
    strategy_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    price: Optional[Decimal] = None
    
    def __post_init__(self):
        """Validate trading signal after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if not self.strategy_name:
            raise ValueError("Strategy name cannot be empty")
        if self.price is not None and self.price < 0:
            raise ValueError("Price cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "action": self.action.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "strategy_name": self.strategy_name,
            "metadata": self.metadata,
            "price": str(self.price) if self.price else None,
        }


@dataclass
class Order:
    """Order representation for trade execution."""
    
    id: str
    symbol: str
    side: OrderSide
    amount: Decimal
    price: Optional[Decimal]
    order_type: OrderType
    status: OrderStatus
    timestamp: datetime
    exchange: str
    filled_amount: Decimal = field(default_factory=lambda: Decimal("0"))
    average_fill_price: Optional[Decimal] = None
    fees: Decimal = field(default_factory=lambda: Decimal("0"))
    client_order_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate order after initialization."""
        if not self.id:
            raise ValueError("Order ID cannot be empty")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        if self.price is not None and self.price <= 0:
            raise ValueError("Price must be positive")
        if self.filled_amount < 0:
            raise ValueError("Filled amount cannot be negative")
        if self.filled_amount > self.amount:
            raise ValueError("Filled amount cannot exceed order amount")
        if not self.exchange:
            raise ValueError("Exchange cannot be empty")
    
    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_partially_filled(self) -> bool:
        """Check if order is partially filled."""
        return self.status == OrderStatus.PARTIALLY_FILLED
    
    @property
    def remaining_amount(self) -> Decimal:
        """Calculate remaining unfilled amount."""
        return self.amount - self.filled_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side.value,
            "amount": str(self.amount),
            "price": str(self.price) if self.price else None,
            "order_type": self.order_type.value,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "exchange": self.exchange,
            "filled_amount": str(self.filled_amount),
            "average_fill_price": str(self.average_fill_price) if self.average_fill_price else None,
            "fees": str(self.fees),
            "client_order_id": self.client_order_id,
        }


@dataclass
class MarketSpecificOrder:
    """Extended order with market-specific fields and multi-market support."""
    
    # Base order fields
    id: str
    symbol: UnifiedSymbol
    side: OrderSide
    amount: Decimal
    price: Optional[Decimal]
    order_type: OrderType
    status: OrderStatus
    timestamp: datetime
    source: str  # Exchange or broker name
    
    # Market-specific fields
    market_type: MarketType
    broker_order_id: Optional[str] = None
    swap_cost: Optional[Decimal] = None  # Forex specific - overnight financing cost
    commission: Optional[Decimal] = None
    regulatory_info: Optional[Dict[str, Any]] = field(default_factory=dict)
    filled_amount: Decimal = field(default_factory=lambda: Decimal("0"))
    average_fill_price: Optional[Decimal] = None
    fees: Decimal = field(default_factory=lambda: Decimal("0"))
    client_order_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate market-specific order after initialization."""
        if not self.id:
            raise ValueError("Order ID cannot be empty")
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        if self.price is not None and self.price <= 0:
            raise ValueError("Price must be positive")
        if self.filled_amount < 0:
            raise ValueError("Filled amount cannot be negative")
        if self.filled_amount > self.amount:
            raise ValueError("Filled amount cannot exceed order amount")
        if not self.source:
            raise ValueError("Source cannot be empty")
        
        # Validate market type consistency
        if self.symbol.market_type != self.market_type:
            raise ValueError("Symbol market type must match order market type")
        
        # Validate market-specific fields
        if self.swap_cost is not None and self.market_type != MarketType.FOREX:
            raise ValueError("Swap cost is only applicable to forex orders")
    
    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_partially_filled(self) -> bool:
        """Check if order is partially filled."""
        return self.status == OrderStatus.PARTIALLY_FILLED
    
    @property
    def remaining_amount(self) -> Decimal:
        """Calculate remaining unfilled amount."""
        return self.amount - self.filled_amount
    
    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost including fees and swap costs."""
        base_cost = self.fees
        if self.swap_cost:
            base_cost += self.swap_cost
        if self.commission:
            base_cost += self.commission
        return base_cost
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "symbol": {
                "base_asset": self.symbol.base_asset,
                "quote_asset": self.symbol.quote_asset,
                "market_type": self.symbol.market_type.value,
                "native_symbol": self.symbol.native_symbol,
            },
            "side": self.side.value,
            "amount": str(self.amount),
            "price": str(self.price) if self.price else None,
            "order_type": self.order_type.value,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "market_type": self.market_type.value,
            "broker_order_id": self.broker_order_id,
            "swap_cost": str(self.swap_cost) if self.swap_cost else None,
            "commission": str(self.commission) if self.commission else None,
            "regulatory_info": self.regulatory_info,
            "filled_amount": str(self.filled_amount),
            "average_fill_price": str(self.average_fill_price) if self.average_fill_price else None,
            "fees": str(self.fees),
            "client_order_id": self.client_order_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketSpecificOrder':
        """Create MarketSpecificOrder from dictionary."""
        symbol_data = data["symbol"]
        symbol = UnifiedSymbol(
            base_asset=symbol_data["base_asset"],
            quote_asset=symbol_data["quote_asset"],
            market_type=MarketType(symbol_data["market_type"]),
            native_symbol=symbol_data["native_symbol"]
        )
        
        return cls(
            id=data["id"],
            symbol=symbol,
            side=OrderSide(data["side"]),
            amount=Decimal(data["amount"]),
            price=Decimal(data["price"]) if data.get("price") else None,
            order_type=OrderType(data["order_type"]),
            status=OrderStatus(data["status"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data["source"],
            market_type=MarketType(data["market_type"]),
            broker_order_id=data.get("broker_order_id"),
            swap_cost=Decimal(data["swap_cost"]) if data.get("swap_cost") else None,
            commission=Decimal(data["commission"]) if data.get("commission") else None,
            regulatory_info=data.get("regulatory_info", {}),
            filled_amount=Decimal(data.get("filled_amount", "0")),
            average_fill_price=Decimal(data["average_fill_price"]) if data.get("average_fill_price") else None,
            fees=Decimal(data.get("fees", "0")),
            client_order_id=data.get("client_order_id"),
        )
    
    @classmethod
    def from_legacy_order(cls, order: Order, market_type: MarketType) -> 'MarketSpecificOrder':
        """Convert legacy Order to MarketSpecificOrder."""
        # Parse symbol based on market type
        if market_type == MarketType.CRYPTO:
            symbol = UnifiedSymbol.from_crypto_symbol(order.symbol)
        elif market_type == MarketType.FOREX:
            symbol = UnifiedSymbol.from_forex_symbol(order.symbol)
        else:
            raise ValueError(f"Unsupported market type: {market_type}")
        
        return cls(
            id=order.id,
            symbol=symbol,
            side=order.side,
            amount=order.amount,
            price=order.price,
            order_type=order.order_type,
            status=order.status,
            timestamp=order.timestamp,
            source=order.exchange,
            market_type=market_type,
            filled_amount=order.filled_amount,
            average_fill_price=order.average_fill_price,
            fees=order.fees,
            client_order_id=order.client_order_id,
        )
    
    def to_legacy_order(self) -> Order:
        """Convert to legacy Order format for backward compatibility."""
        return Order(
            id=self.id,
            symbol=self.symbol.native_symbol,
            side=self.side,
            amount=self.amount,
            price=self.price,
            order_type=self.order_type,
            status=self.status,
            timestamp=self.timestamp,
            exchange=self.source,
            filled_amount=self.filled_amount,
            average_fill_price=self.average_fill_price,
            fees=self.fees,
            client_order_id=self.client_order_id,
        )


@dataclass
class Position:
    """Position representation for portfolio tracking."""
    
    symbol: str
    size: Decimal
    entry_price: Decimal
    current_price: Decimal
    timestamp: datetime
    exchange: str
    side: OrderSide = field(default=OrderSide.BUY)
    
    def __post_init__(self):
        """Validate position after initialization."""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.entry_price <= 0:
            raise ValueError("Entry price must be positive")
        if self.current_price <= 0:
            raise ValueError("Current price must be positive")
        if not self.exchange:
            raise ValueError("Exchange cannot be empty")
    
    @property
    def unrealized_pnl(self) -> Decimal:
        """Calculate unrealized profit/loss."""
        if self.side == OrderSide.BUY:
            return (self.current_price - self.entry_price) * abs(self.size)
        else:
            return (self.entry_price - self.current_price) * abs(self.size)
    
    @property
    def unrealized_pnl_percentage(self) -> Decimal:
        """Calculate unrealized P&L as percentage."""
        if self.side == OrderSide.BUY:
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.current_price) / self.entry_price) * 100
    
    @property
    def market_value(self) -> Decimal:
        """Calculate current market value of position."""
        return abs(self.size) * self.current_price
    
    def update_price(self, new_price: Decimal) -> None:
        """Update current price and timestamp."""
        if new_price <= 0:
            raise ValueError("Price must be positive")
        self.current_price = new_price
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "size": f"{self.size:.2f}",
            "entry_price": f"{self.entry_price:.2f}",
            "current_price": f"{self.current_price:.2f}",
            "timestamp": self.timestamp.isoformat(),
            "exchange": self.exchange,
            "side": self.side.value,
            "unrealized_pnl": f"{self.unrealized_pnl:.2f}",
            "unrealized_pnl_percentage": f"{self.unrealized_pnl_percentage:.2f}",
            "market_value": f"{self.market_value:.2f}",
        }