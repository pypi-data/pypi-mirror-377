"""Unit tests for data models."""

import pytest
from datetime import datetime
from decimal import Decimal

from src.models.data_models import (
    MarketData,
    TradingSignal,
    Order,
    Position,
    OrderSide,
    OrderType,
    OrderStatus,
    SignalAction,
)


class TestMarketData:
    """Test cases for MarketData dataclass."""

    def test_valid_market_data_creation(self):
        """Test creating valid market data."""
        data = MarketData(
            symbol="BTC/USD",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49000.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            exchange="binance"
        )
        
        assert data.symbol == "BTC/USD"
        assert data.open == Decimal("50000.00")
        assert data.high == Decimal("51000.00")
        assert data.low == Decimal("49000.00")
        assert data.close == Decimal("50500.00")
        assert data.volume == Decimal("100.5")
        assert data.exchange == "binance"

    def test_market_data_validation_high_less_than_low(self):
        """Test validation when high is less than low."""
        with pytest.raises(ValueError, match="High price cannot be less than low price"):
            MarketData(
                symbol="BTC/USD",
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                open=Decimal("50000.00"),
                high=Decimal("49000.00"),  # High less than low
                low=Decimal("51000.00"),
                close=Decimal("50500.00"),
                volume=Decimal("100.5"),
                exchange="binance"
            )

    def test_market_data_validation_negative_prices(self):
        """Test validation for negative prices."""
        with pytest.raises(ValueError, match="Prices cannot be negative"):
            MarketData(
                symbol="BTC/USD",
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                open=Decimal("-50000.00"),  # Negative price
                high=Decimal("51000.00"),
                low=Decimal("49000.00"),
                close=Decimal("50500.00"),
                volume=Decimal("100.5"),
                exchange="binance"
            )

    def test_market_data_validation_negative_volume(self):
        """Test validation for negative volume."""
        with pytest.raises(ValueError, match="Volume cannot be negative"):
            MarketData(
                symbol="BTC/USD",
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                open=Decimal("50000.00"),
                high=Decimal("51000.00"),
                low=Decimal("49000.00"),
                close=Decimal("50500.00"),
                volume=Decimal("-100.5"),  # Negative volume
                exchange="binance"
            )

    def test_market_data_validation_empty_symbol(self):
        """Test validation for empty symbol."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            MarketData(
                symbol="",  # Empty symbol
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                open=Decimal("50000.00"),
                high=Decimal("51000.00"),
                low=Decimal("49000.00"),
                close=Decimal("50500.00"),
                volume=Decimal("100.5"),
                exchange="binance"
            )

    def test_market_data_validation_empty_exchange(self):
        """Test validation for empty exchange."""
        with pytest.raises(ValueError, match="Exchange cannot be empty"):
            MarketData(
                symbol="BTC/USD",
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                open=Decimal("50000.00"),
                high=Decimal("51000.00"),
                low=Decimal("49000.00"),
                close=Decimal("50500.00"),
                volume=Decimal("100.5"),
                exchange=""  # Empty exchange
            )

    def test_market_data_to_dict(self):
        """Test serialization to dictionary."""
        data = MarketData(
            symbol="BTC/USD",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49000.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            exchange="binance"
        )
        
        result = data.to_dict()
        expected = {
            "symbol": "BTC/USD",
            "timestamp": "2023-01-01T12:00:00",
            "open": "50000.00",
            "high": "51000.00",
            "low": "49000.00",
            "close": "50500.00",
            "volume": "100.5",
            "exchange": "binance",
        }
        
        assert result == expected


class TestTradingSignal:
    """Test cases for TradingSignal dataclass."""

    def test_valid_trading_signal_creation(self):
        """Test creating valid trading signal."""
        signal = TradingSignal(
            symbol="BTC/USD",
            action=SignalAction.BUY,
            confidence=0.85,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            strategy_name="MovingAverage",
            metadata={"ma_short": 50, "ma_long": 200},
            price=Decimal("50000.00")
        )
        
        assert signal.symbol == "BTC/USD"
        assert signal.action == SignalAction.BUY
        assert signal.confidence == 0.85
        assert signal.strategy_name == "MovingAverage"
        assert signal.metadata == {"ma_short": 50, "ma_long": 200}
        assert signal.price == Decimal("50000.00")

    def test_trading_signal_validation_confidence_range(self):
        """Test validation for confidence range."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            TradingSignal(
                symbol="BTC/USD",
                action=SignalAction.BUY,
                confidence=1.5,  # Invalid confidence
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                strategy_name="MovingAverage"
            )

    def test_trading_signal_validation_empty_symbol(self):
        """Test validation for empty symbol."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            TradingSignal(
                symbol="",  # Empty symbol
                action=SignalAction.BUY,
                confidence=0.85,
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                strategy_name="MovingAverage"
            )

    def test_trading_signal_validation_empty_strategy_name(self):
        """Test validation for empty strategy name."""
        with pytest.raises(ValueError, match="Strategy name cannot be empty"):
            TradingSignal(
                symbol="BTC/USD",
                action=SignalAction.BUY,
                confidence=0.85,
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                strategy_name=""  # Empty strategy name
            )

    def test_trading_signal_validation_negative_price(self):
        """Test validation for negative price."""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            TradingSignal(
                symbol="BTC/USD",
                action=SignalAction.BUY,
                confidence=0.85,
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                strategy_name="MovingAverage",
                price=Decimal("-50000.00")  # Negative price
            )

    def test_trading_signal_to_dict(self):
        """Test serialization to dictionary."""
        signal = TradingSignal(
            symbol="BTC/USD",
            action=SignalAction.BUY,
            confidence=0.85,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            strategy_name="MovingAverage",
            metadata={"ma_short": 50},
            price=Decimal("50000.00")
        )
        
        result = signal.to_dict()
        expected = {
            "symbol": "BTC/USD",
            "action": "BUY",
            "confidence": 0.85,
            "timestamp": "2023-01-01T12:00:00",
            "strategy_name": "MovingAverage",
            "metadata": {"ma_short": 50},
            "price": "50000.00",
        }
        
        assert result == expected


class TestOrder:
    """Test cases for Order dataclass."""

    def test_valid_order_creation(self):
        """Test creating valid order."""
        order = Order(
            id="order_123",
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=Decimal("1.5"),
            price=Decimal("50000.00"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.OPEN,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance",
            filled_amount=Decimal("0.5"),
            average_fill_price=Decimal("49900.00"),
            fees=Decimal("25.00"),
            client_order_id="client_123"
        )
        
        assert order.id == "order_123"
        assert order.symbol == "BTC/USD"
        assert order.side == OrderSide.BUY
        assert order.amount == Decimal("1.5")
        assert order.price == Decimal("50000.00")
        assert order.order_type == OrderType.LIMIT
        assert order.status == OrderStatus.OPEN
        assert order.exchange == "binance"
        assert order.filled_amount == Decimal("0.5")
        assert order.average_fill_price == Decimal("49900.00")
        assert order.fees == Decimal("25.00")
        assert order.client_order_id == "client_123"

    def test_order_validation_empty_id(self):
        """Test validation for empty order ID."""
        with pytest.raises(ValueError, match="Order ID cannot be empty"):
            Order(
                id="",  # Empty ID
                symbol="BTC/USD",
                side=OrderSide.BUY,
                amount=Decimal("1.5"),
                price=Decimal("50000.00"),
                order_type=OrderType.LIMIT,
                status=OrderStatus.OPEN,
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                exchange="binance"
            )

    def test_order_validation_negative_amount(self):
        """Test validation for negative amount."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            Order(
                id="order_123",
                symbol="BTC/USD",
                side=OrderSide.BUY,
                amount=Decimal("-1.5"),  # Negative amount
                price=Decimal("50000.00"),
                order_type=OrderType.LIMIT,
                status=OrderStatus.OPEN,
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                exchange="binance"
            )

    def test_order_validation_negative_price(self):
        """Test validation for negative price."""
        with pytest.raises(ValueError, match="Price must be positive"):
            Order(
                id="order_123",
                symbol="BTC/USD",
                side=OrderSide.BUY,
                amount=Decimal("1.5"),
                price=Decimal("-50000.00"),  # Negative price
                order_type=OrderType.LIMIT,
                status=OrderStatus.OPEN,
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                exchange="binance"
            )

    def test_order_validation_filled_amount_exceeds_amount(self):
        """Test validation when filled amount exceeds order amount."""
        with pytest.raises(ValueError, match="Filled amount cannot exceed order amount"):
            Order(
                id="order_123",
                symbol="BTC/USD",
                side=OrderSide.BUY,
                amount=Decimal("1.5"),
                price=Decimal("50000.00"),
                order_type=OrderType.LIMIT,
                status=OrderStatus.OPEN,
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                exchange="binance",
                filled_amount=Decimal("2.0")  # Exceeds order amount
            )

    def test_order_properties(self):
        """Test order properties."""
        order = Order(
            id="order_123",
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=Decimal("1.5"),
            price=Decimal("50000.00"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.FILLED,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance",
            filled_amount=Decimal("1.5")
        )
        
        assert order.is_filled is True
        assert order.is_partially_filled is False
        assert order.remaining_amount == Decimal("0.0")

    def test_order_to_dict(self):
        """Test serialization to dictionary."""
        order = Order(
            id="order_123",
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=Decimal("1.5"),
            price=Decimal("50000.00"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.OPEN,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance"
        )
        
        result = order.to_dict()
        expected = {
            "id": "order_123",
            "symbol": "BTC/USD",
            "side": "BUY",
            "amount": "1.5",
            "price": "50000.00",
            "order_type": "LIMIT",
            "status": "OPEN",
            "timestamp": "2023-01-01T12:00:00",
            "exchange": "binance",
            "filled_amount": "0",
            "average_fill_price": None,
            "fees": "0",
            "client_order_id": None,
        }
        
        assert result == expected


class TestPosition:
    """Test cases for Position dataclass."""

    def test_valid_position_creation(self):
        """Test creating valid position."""
        position = Position(
            symbol="BTC/USD",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance",
            side=OrderSide.BUY
        )
        
        assert position.symbol == "BTC/USD"
        assert position.size == Decimal("1.5")
        assert position.entry_price == Decimal("50000.00")
        assert position.current_price == Decimal("51000.00")
        assert position.exchange == "binance"
        assert position.side == OrderSide.BUY

    def test_position_validation_empty_symbol(self):
        """Test validation for empty symbol."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            Position(
                symbol="",  # Empty symbol
                size=Decimal("1.5"),
                entry_price=Decimal("50000.00"),
                current_price=Decimal("51000.00"),
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                exchange="binance"
            )

    def test_position_validation_negative_entry_price(self):
        """Test validation for negative entry price."""
        with pytest.raises(ValueError, match="Entry price must be positive"):
            Position(
                symbol="BTC/USD",
                size=Decimal("1.5"),
                entry_price=Decimal("-50000.00"),  # Negative entry price
                current_price=Decimal("51000.00"),
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                exchange="binance"
            )

    def test_position_validation_negative_current_price(self):
        """Test validation for negative current price."""
        with pytest.raises(ValueError, match="Current price must be positive"):
            Position(
                symbol="BTC/USD",
                size=Decimal("1.5"),
                entry_price=Decimal("50000.00"),
                current_price=Decimal("-51000.00"),  # Negative current price
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                exchange="binance"
            )

    def test_position_pnl_calculations_long(self):
        """Test P&L calculations for long position."""
        position = Position(
            symbol="BTC/USD",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance",
            side=OrderSide.BUY
        )
        
        # Profit: (51000 - 50000) * 1.5 = 1500
        assert position.unrealized_pnl == Decimal("1500.00")
        assert position.unrealized_pnl_percentage == Decimal("2.00")
        assert position.market_value == Decimal("76500.00")  # 1.5 * 51000

    def test_position_pnl_calculations_short(self):
        """Test P&L calculations for short position."""
        position = Position(
            symbol="BTC/USD",
            size=Decimal("-1.5"),  # Negative size for short
            entry_price=Decimal("50000.00"),
            current_price=Decimal("49000.00"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance",
            side=OrderSide.SELL
        )
        
        # Profit: (50000 - 49000) * 1.5 = 1500
        assert position.unrealized_pnl == Decimal("1500.00")
        assert position.unrealized_pnl_percentage == Decimal("2.00")
        assert position.market_value == Decimal("73500.00")  # 1.5 * 49000

    def test_position_update_price(self):
        """Test updating position price."""
        position = Position(
            symbol="BTC/USD",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance"
        )
        
        original_timestamp = position.timestamp
        position.update_price(Decimal("52000.00"))
        
        assert position.current_price == Decimal("52000.00")
        assert position.timestamp > original_timestamp

    def test_position_update_price_validation(self):
        """Test validation when updating price."""
        position = Position(
            symbol="BTC/USD",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance"
        )
        
        with pytest.raises(ValueError, match="Price must be positive"):
            position.update_price(Decimal("-52000.00"))

    def test_position_to_dict(self):
        """Test serialization to dictionary."""
        position = Position(
            symbol="BTC/USD",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance",
            side=OrderSide.BUY
        )
        
        result = position.to_dict()
        expected = {
            "symbol": "BTC/USD",
            "size": "1.50",
            "entry_price": "50000.00",
            "current_price": "51000.00",
            "timestamp": "2023-01-01T12:00:00",
            "exchange": "binance",
            "side": "BUY",
            "unrealized_pnl": "1500.00",
            "unrealized_pnl_percentage": "2.00",
            "market_value": "76500.00",
        }
        
        assert result == expected