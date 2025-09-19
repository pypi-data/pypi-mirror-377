"""Unit tests for database models."""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models.database_models import (
    Base,
    MarketDataModel,
    TradingSignalModel,
    OrderModel,
    PositionModel,
    TradeModel,
    StrategyPerformanceModel,
    RiskEventModel,
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


class TestMarketDataModel:
    """Test cases for MarketDataModel."""

    def test_create_market_data(self, db_session):
        """Test creating market data record."""
        market_data = MarketDataModel(
            symbol="BTC/USD",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49000.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            exchange="binance"
        )
        
        db_session.add(market_data)
        db_session.commit()
        
        # Verify the record was created
        retrieved = db_session.query(MarketDataModel).first()
        assert retrieved.symbol == "BTC/USD"
        assert retrieved.open == Decimal("50000.00")
        assert retrieved.high == Decimal("51000.00")
        assert retrieved.low == Decimal("49000.00")
        assert retrieved.close == Decimal("50500.00")
        assert retrieved.volume == Decimal("100.5")
        assert retrieved.exchange == "binance"
        assert retrieved.created_at is not None

    def test_market_data_unique_constraint(self, db_session):
        """Test unique constraint on symbol, timestamp, exchange."""
        market_data1 = MarketDataModel(
            symbol="BTC/USD",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49000.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            exchange="binance"
        )
        
        market_data2 = MarketDataModel(
            symbol="BTC/USD",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),  # Same timestamp
            open=Decimal("50100.00"),
            high=Decimal("51100.00"),
            low=Decimal("49100.00"),
            close=Decimal("50600.00"),
            volume=Decimal("200.5"),
            exchange="binance"  # Same exchange
        )
        
        db_session.add(market_data1)
        db_session.commit()
        
        db_session.add(market_data2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_market_data_repr(self, db_session):
        """Test string representation."""
        market_data = MarketDataModel(
            symbol="BTC/USD",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49000.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            exchange="binance"
        )
        
        expected = "<MarketData(symbol=BTC/USD, timestamp=2023-01-01 12:00:00, close=50500.00)>"
        assert repr(market_data) == expected


class TestTradingSignalModel:
    """Test cases for TradingSignalModel."""

    def test_create_trading_signal(self, db_session):
        """Test creating trading signal record."""
        signal = TradingSignalModel(
            symbol="BTC/USD",
            action="BUY",
            confidence=Decimal("0.8500"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            strategy_name="MovingAverage",
            price=Decimal("50000.00"),
            signal_metadata={"ma_short": 50, "ma_long": 200}
        )
        
        db_session.add(signal)
        db_session.commit()
        
        # Verify the record was created
        retrieved = db_session.query(TradingSignalModel).first()
        assert retrieved.symbol == "BTC/USD"
        assert retrieved.action == "BUY"
        assert retrieved.confidence == Decimal("0.8500")
        assert retrieved.strategy_name == "MovingAverage"
        assert retrieved.price == Decimal("50000.00")
        assert retrieved.signal_metadata == {"ma_short": 50, "ma_long": 200}
        assert retrieved.created_at is not None

    def test_trading_signal_repr(self, db_session):
        """Test string representation."""
        signal = TradingSignalModel(
            symbol="BTC/USD",
            action="BUY",
            confidence=Decimal("0.8500"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            strategy_name="MovingAverage"
        )
        
        expected = "<TradingSignal(symbol=BTC/USD, action=BUY, strategy=MovingAverage)>"
        assert repr(signal) == expected


class TestOrderModel:
    """Test cases for OrderModel."""

    def test_create_order(self, db_session):
        """Test creating order record."""
        order = OrderModel(
            id="order_123",
            symbol="BTC/USD",
            side="BUY",
            amount=Decimal("1.5"),
            price=Decimal("50000.00"),
            order_type="LIMIT",
            status="OPEN",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance",
            filled_amount=Decimal("0.5"),
            average_fill_price=Decimal("49900.00"),
            fees=Decimal("25.00"),
            client_order_id="client_123"
        )
        
        db_session.add(order)
        db_session.commit()
        
        # Verify the record was created
        retrieved = db_session.query(OrderModel).first()
        assert retrieved.id == "order_123"
        assert retrieved.symbol == "BTC/USD"
        assert retrieved.side == "BUY"
        assert retrieved.amount == Decimal("1.5")
        assert retrieved.price == Decimal("50000.00")
        assert retrieved.order_type == "LIMIT"
        assert retrieved.status == "OPEN"
        assert retrieved.exchange == "binance"
        assert retrieved.filled_amount == Decimal("0.5")
        assert retrieved.average_fill_price == Decimal("49900.00")
        assert retrieved.fees == Decimal("25.00")
        assert retrieved.client_order_id == "client_123"
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None

    def test_order_repr(self, db_session):
        """Test string representation."""
        order = OrderModel(
            id="order_123",
            symbol="BTC/USD",
            side="BUY",
            amount=Decimal("1.5"),
            order_type="LIMIT",
            status="OPEN",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance"
        )
        
        expected = "<Order(id=order_123, symbol=BTC/USD, side=BUY, status=OPEN)>"
        assert repr(order) == expected


class TestPositionModel:
    """Test cases for PositionModel."""

    def test_create_position(self, db_session):
        """Test creating position record."""
        position = PositionModel(
            symbol="BTC/USD",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            side="BUY",
            exchange="binance",
            opened_at=datetime(2023, 1, 1, 12, 0, 0),
            is_active="true"
        )
        
        db_session.add(position)
        db_session.commit()
        
        # Verify the record was created
        retrieved = db_session.query(PositionModel).first()
        assert retrieved.symbol == "BTC/USD"
        assert retrieved.size == Decimal("1.5")
        assert retrieved.entry_price == Decimal("50000.00")
        assert retrieved.current_price == Decimal("51000.00")
        assert retrieved.side == "BUY"
        assert retrieved.exchange == "binance"
        assert retrieved.is_active == "true"
        assert retrieved.opened_at == datetime(2023, 1, 1, 12, 0, 0)
        assert retrieved.updated_at is not None
        assert retrieved.closed_at is None

    def test_position_repr(self, db_session):
        """Test string representation."""
        position = PositionModel(
            symbol="BTC/USD",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            side="BUY",
            exchange="binance",
            opened_at=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        expected = "<Position(symbol=BTC/USD, size=1.5, entry_price=50000.00)>"
        assert repr(position) == expected


class TestTradeModel:
    """Test cases for TradeModel."""

    def test_create_trade_with_order(self, db_session):
        """Test creating trade record with associated order."""
        # First create an order
        order = OrderModel(
            id="order_123",
            symbol="BTC/USD",
            side="BUY",
            amount=Decimal("1.5"),
            price=Decimal("50000.00"),
            order_type="LIMIT",
            status="FILLED",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance"
        )
        db_session.add(order)
        db_session.commit()
        
        # Then create a trade
        trade = TradeModel(
            order_id="order_123",
            symbol="BTC/USD",
            side="BUY",
            amount=Decimal("1.5"),
            price=Decimal("49950.00"),
            fees=Decimal("25.00"),
            timestamp=datetime(2023, 1, 1, 12, 5, 0),
            exchange="binance",
            trade_id="trade_456"
        )
        
        db_session.add(trade)
        db_session.commit()
        
        # Verify the record was created and relationship works
        retrieved = db_session.query(TradeModel).first()
        assert retrieved.order_id == "order_123"
        assert retrieved.symbol == "BTC/USD"
        assert retrieved.side == "BUY"
        assert retrieved.amount == Decimal("1.5")
        assert retrieved.price == Decimal("49950.00")
        assert retrieved.fees == Decimal("25.00")
        assert retrieved.exchange == "binance"
        assert retrieved.trade_id == "trade_456"
        assert retrieved.order is not None
        assert retrieved.order.id == "order_123"

    def test_trade_repr(self, db_session):
        """Test string representation."""
        trade = TradeModel(
            order_id="order_123",
            symbol="BTC/USD",
            side="BUY",
            amount=Decimal("1.5"),
            price=Decimal("49950.00"),
            fees=Decimal("25.00"),
            timestamp=datetime(2023, 1, 1, 12, 5, 0),
            exchange="binance"
        )
        
        expected = "<Trade(symbol=BTC/USD, side=BUY, amount=1.5, price=49950.00)>"
        assert repr(trade) == expected


class TestStrategyPerformanceModel:
    """Test cases for StrategyPerformanceModel."""

    def test_create_strategy_performance(self, db_session):
        """Test creating strategy performance record."""
        performance = StrategyPerformanceModel(
            strategy_name="MovingAverage",
            symbol="BTC/USD",
            period_start=datetime(2023, 1, 1, 0, 0, 0),
            period_end=datetime(2023, 1, 31, 23, 59, 59),
            total_trades=100,
            winning_trades=65,
            losing_trades=35,
            total_pnl=Decimal("5000.00"),
            max_drawdown=Decimal("1200.00"),
            sharpe_ratio=Decimal("1.5000"),
            win_rate=Decimal("0.6500"),
            avg_win=Decimal("150.00"),
            avg_loss=Decimal("80.00")
        )
        
        db_session.add(performance)
        db_session.commit()
        
        # Verify the record was created
        retrieved = db_session.query(StrategyPerformanceModel).first()
        assert retrieved.strategy_name == "MovingAverage"
        assert retrieved.symbol == "BTC/USD"
        assert retrieved.total_trades == 100
        assert retrieved.winning_trades == 65
        assert retrieved.losing_trades == 35
        assert retrieved.total_pnl == Decimal("5000.00")
        assert retrieved.max_drawdown == Decimal("1200.00")
        assert retrieved.sharpe_ratio == Decimal("1.5000")
        assert retrieved.win_rate == Decimal("0.6500")
        assert retrieved.avg_win == Decimal("150.00")
        assert retrieved.avg_loss == Decimal("80.00")
        assert retrieved.created_at is not None

    def test_strategy_performance_repr(self, db_session):
        """Test string representation."""
        performance = StrategyPerformanceModel(
            strategy_name="MovingAverage",
            symbol="BTC/USD",
            period_start=datetime(2023, 1, 1, 0, 0, 0),
            period_end=datetime(2023, 1, 31, 23, 59, 59),
            total_trades=100,
            winning_trades=65,
            losing_trades=35,
            total_pnl=Decimal("5000.00"),
            max_drawdown=Decimal("1200.00"),
            win_rate=Decimal("0.6500"),
            avg_win=Decimal("150.00"),
            avg_loss=Decimal("80.00")
        )
        
        expected = "<StrategyPerformance(strategy=MovingAverage, symbol=BTC/USD, pnl=5000.00)>"
        assert repr(performance) == expected


class TestRiskEventModel:
    """Test cases for RiskEventModel."""

    def test_create_risk_event(self, db_session):
        """Test creating risk event record."""
        risk_event = RiskEventModel(
            event_type="STOP_LOSS",
            symbol="BTC/USD",
            description="Stop loss triggered due to price drop",
            severity="HIGH",
            triggered_value=Decimal("48000.00"),
            threshold_value=Decimal("48500.00"),
            action_taken="CLOSE_POSITION",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            risk_metadata={"position_size": "1.5", "loss_amount": "1500.00"}
        )
        
        db_session.add(risk_event)
        db_session.commit()
        
        # Verify the record was created
        retrieved = db_session.query(RiskEventModel).first()
        assert retrieved.event_type == "STOP_LOSS"
        assert retrieved.symbol == "BTC/USD"
        assert retrieved.description == "Stop loss triggered due to price drop"
        assert retrieved.severity == "HIGH"
        assert retrieved.triggered_value == Decimal("48000.00")
        assert retrieved.threshold_value == Decimal("48500.00")
        assert retrieved.action_taken == "CLOSE_POSITION"
        assert retrieved.risk_metadata == {"position_size": "1.5", "loss_amount": "1500.00"}
        assert retrieved.created_at is not None

    def test_risk_event_repr(self, db_session):
        """Test string representation."""
        risk_event = RiskEventModel(
            event_type="STOP_LOSS",
            symbol="BTC/USD",
            description="Stop loss triggered due to price drop",
            severity="HIGH",
            timestamp=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        expected = "<RiskEvent(type=STOP_LOSS, symbol=BTC/USD, severity=HIGH)>"
        assert repr(risk_event) == expected


class TestDatabaseRelationships:
    """Test database relationships between models."""

    def test_order_trade_relationship(self, db_session):
        """Test relationship between orders and trades."""
        # Create an order
        order = OrderModel(
            id="order_123",
            symbol="BTC/USD",
            side="BUY",
            amount=Decimal("2.0"),
            price=Decimal("50000.00"),
            order_type="LIMIT",
            status="FILLED",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            exchange="binance"
        )
        db_session.add(order)
        
        # Create multiple trades for the same order
        trade1 = TradeModel(
            order_id="order_123",
            symbol="BTC/USD",
            side="BUY",
            amount=Decimal("1.0"),
            price=Decimal("49950.00"),
            fees=Decimal("12.50"),
            timestamp=datetime(2023, 1, 1, 12, 1, 0),
            exchange="binance",
            trade_id="trade_1"
        )
        
        trade2 = TradeModel(
            order_id="order_123",
            symbol="BTC/USD",
            side="BUY",
            amount=Decimal("1.0"),
            price=Decimal("50050.00"),
            fees=Decimal("12.50"),
            timestamp=datetime(2023, 1, 1, 12, 2, 0),
            exchange="binance",
            trade_id="trade_2"
        )
        
        db_session.add_all([trade1, trade2])
        db_session.commit()
        
        # Test the relationship
        retrieved_order = db_session.query(OrderModel).first()
        assert len(retrieved_order.trades) == 2
        assert retrieved_order.trades[0].trade_id in ["trade_1", "trade_2"]
        assert retrieved_order.trades[1].trade_id in ["trade_1", "trade_2"]
        
        # Test reverse relationship
        retrieved_trade = db_session.query(TradeModel).first()
        assert retrieved_trade.order.id == "order_123"