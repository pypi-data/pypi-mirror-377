"""
Unit tests for enhanced data models with multi-market support.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from src.models.data_models import (
    UnifiedMarketData, MarketSpecificOrder, SessionInfo,
    MarketData, Order, OrderSide, OrderType, OrderStatus
)
from src.markets.types import MarketType, UnifiedSymbol


class TestSessionInfo:
    """Test cases for SessionInfo data class."""
    
    def test_session_info_creation(self):
        """Test basic SessionInfo creation."""
        session = SessionInfo(
            session_name="London",
            is_active=True,
            market_type=MarketType.FOREX
        )
        
        assert session.session_name == "London"
        assert session.is_active is True
        assert session.market_type == MarketType.FOREX
        assert session.next_open is None
        assert session.next_close is None
    
    def test_session_info_with_times(self):
        """Test SessionInfo with open/close times."""
        now = datetime.now()
        later = datetime.now()
        
        session = SessionInfo(
            session_name="New York",
            is_active=False,
            next_open=now,
            next_close=later,
            market_type=MarketType.FOREX
        )
        
        assert session.next_open == now
        assert session.next_close == later
    
    def test_session_info_validation(self):
        """Test SessionInfo validation."""
        with pytest.raises(ValueError, match="Session name cannot be empty"):
            SessionInfo(session_name="", is_active=True)
    
    def test_session_info_serialization(self):
        """Test SessionInfo to_dict and from_dict."""
        now = datetime.now()
        session = SessionInfo(
            session_name="Tokyo",
            is_active=True,
            next_open=now,
            market_type=MarketType.FOREX
        )
        
        data = session.to_dict()
        assert data["session_name"] == "Tokyo"
        assert data["is_active"] is True
        assert data["next_open"] == now.isoformat()
        assert data["market_type"] == "forex"
        
        # Test round-trip
        restored = SessionInfo.from_dict(data)
        assert restored.session_name == session.session_name
        assert restored.is_active == session.is_active
        assert restored.next_open == session.next_open
        assert restored.market_type == session.market_type


class TestUnifiedMarketData:
    """Test cases for UnifiedMarketData class."""
    
    def test_unified_market_data_creation(self):
        """Test basic UnifiedMarketData creation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        session = SessionInfo("24/7", True, market_type=MarketType.CRYPTO)
        
        data = UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime.now(),
            open=Decimal("50000"),
            high=Decimal("51000"),
            low=Decimal("49000"),
            close=Decimal("50500"),
            volume=Decimal("100"),
            source="binance",
            market_type=MarketType.CRYPTO,
            session_info=session
        )
        
        assert data.symbol.base_asset == "BTC"
        assert data.symbol.quote_asset == "USDT"
        assert data.market_type == MarketType.CRYPTO
        assert data.source == "binance"
        assert data.session_info == session
    
    def test_unified_market_data_validation(self):
        """Test UnifiedMarketData validation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        # Test negative prices
        with pytest.raises(ValueError, match="Prices cannot be negative"):
            UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open=Decimal("-1"),
                high=Decimal("51000"),
                low=Decimal("49000"),
                close=Decimal("50500"),
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO
            )
        
        # Test high < low
        with pytest.raises(ValueError, match="High price cannot be less than low price"):
            UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open=Decimal("50000"),
                high=Decimal("49000"),
                low=Decimal("51000"),
                close=Decimal("50500"),
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO
            )
        
        # Test market type mismatch
        forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        with pytest.raises(ValueError, match="Symbol market type must match data market type"):
            UnifiedMarketData(
                symbol=forex_symbol,
                timestamp=datetime.now(),
                open=Decimal("1.1000"),
                high=Decimal("1.1100"),
                low=Decimal("1.0900"),
                close=Decimal("1.1050"),
                volume=Decimal("1000"),
                source="oanda",
                market_type=MarketType.CRYPTO  # Wrong market type
            )
    
    def test_unified_market_data_serialization(self):
        """Test UnifiedMarketData serialization."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        session = SessionInfo("London", True, market_type=MarketType.FOREX)
        
        data = UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            open=Decimal("1.1000"),
            high=Decimal("1.1100"),
            low=Decimal("1.0900"),
            close=Decimal("1.1050"),
            volume=Decimal("1000"),
            source="oanda",
            market_type=MarketType.FOREX,
            session_info=session
        )
        
        serialized = data.to_dict()
        assert serialized["symbol"]["base_asset"] == "EUR"
        assert serialized["symbol"]["quote_asset"] == "USD"
        assert serialized["market_type"] == "forex"
        assert serialized["source"] == "oanda"
        assert serialized["session_info"]["session_name"] == "London"
        
        # Test round-trip
        restored = UnifiedMarketData.from_dict(serialized)
        assert restored.symbol.base_asset == data.symbol.base_asset
        assert restored.symbol.quote_asset == data.symbol.quote_asset
        assert restored.market_type == data.market_type
        assert restored.source == data.source
        assert restored.open == data.open
    
    def test_legacy_conversion(self):
        """Test conversion from/to legacy MarketData."""
        # Create legacy MarketData
        legacy_data = MarketData(
            symbol="BTCUSDT",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            open=Decimal("50000"),
            high=Decimal("51000"),
            low=Decimal("49000"),
            close=Decimal("50500"),
            volume=Decimal("100"),
            exchange="binance"
        )
        
        # Convert to UnifiedMarketData
        unified_data = UnifiedMarketData.from_legacy_market_data(
            legacy_data, MarketType.CRYPTO
        )
        
        assert unified_data.symbol.base_asset == "BTC"
        assert unified_data.symbol.quote_asset == "USDT"
        assert unified_data.market_type == MarketType.CRYPTO
        assert unified_data.source == "binance"
        assert unified_data.open == legacy_data.open
        
        # Convert back to legacy
        converted_back = unified_data.to_legacy_market_data()
        assert converted_back.symbol == legacy_data.symbol
        assert converted_back.exchange == legacy_data.exchange
        assert converted_back.open == legacy_data.open


class TestMarketSpecificOrder:
    """Test cases for MarketSpecificOrder class."""
    
    def test_market_specific_order_creation(self):
        """Test basic MarketSpecificOrder creation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.OPEN,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO
        )
        
        assert order.id == "order_123"
        assert order.symbol.base_asset == "BTC"
        assert order.market_type == MarketType.CRYPTO
        assert order.side == OrderSide.BUY
        assert order.amount == Decimal("1.0")
    
    def test_forex_specific_fields(self):
        """Test forex-specific fields like swap cost."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        order = MarketSpecificOrder(
            id="forex_order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("100000"),  # 1 lot
            price=Decimal("1.1000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="oanda",
            market_type=MarketType.FOREX,
            swap_cost=Decimal("2.50"),
            commission=Decimal("5.00")
        )
        
        assert order.swap_cost == Decimal("2.50")
        assert order.commission == Decimal("5.00")
        assert order.total_cost == Decimal("7.50")  # fees + swap + commission
    
    def test_market_specific_order_validation(self):
        """Test MarketSpecificOrder validation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        # Test market type mismatch
        with pytest.raises(ValueError, match="Symbol market type must match order market type"):
            MarketSpecificOrder(
                id="order_123",
                symbol=symbol,
                side=OrderSide.BUY,
                amount=Decimal("1.0"),
                price=Decimal("50000"),
                order_type=OrderType.LIMIT,
                status=OrderStatus.OPEN,
                timestamp=datetime.now(),
                source="binance",
                market_type=MarketType.FOREX  # Wrong market type
            )
        
        # Test swap cost on non-forex order
        with pytest.raises(ValueError, match="Swap cost is only applicable to forex orders"):
            MarketSpecificOrder(
                id="order_123",
                symbol=symbol,
                side=OrderSide.BUY,
                amount=Decimal("1.0"),
                price=Decimal("50000"),
                order_type=OrderType.LIMIT,
                status=OrderStatus.OPEN,
                timestamp=datetime.now(),
                source="binance",
                market_type=MarketType.CRYPTO,
                swap_cost=Decimal("2.50")  # Invalid for crypto
            )
    
    def test_order_properties(self):
        """Test order status and calculation properties."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("2.0"),
            price=Decimal("50000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.PARTIALLY_FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            fees=Decimal("10.0")
        )
        
        assert order.is_partially_filled is True
        assert order.is_filled is False
        assert order.remaining_amount == Decimal("1.0")
        assert order.total_cost == Decimal("10.0")
    
    def test_market_specific_order_serialization(self):
        """Test MarketSpecificOrder serialization."""
        symbol = UnifiedSymbol.from_forex_symbol("GBPUSD")
        
        order = MarketSpecificOrder(
            id="forex_order_456",
            symbol=symbol,
            side=OrderSide.SELL,
            amount=Decimal("50000"),
            price=Decimal("1.2500"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime(2023, 1, 1, 15, 30, 0),
            source="mt5",
            market_type=MarketType.FOREX,
            broker_order_id="MT5_12345",
            swap_cost=Decimal("1.25"),
            commission=Decimal("3.00"),
            regulatory_info={"jurisdiction": "UK", "mifid_compliant": True}
        )
        
        serialized = order.to_dict()
        assert serialized["id"] == "forex_order_456"
        assert serialized["symbol"]["base_asset"] == "GBP"
        assert serialized["market_type"] == "forex"
        assert serialized["broker_order_id"] == "MT5_12345"
        assert serialized["swap_cost"] == "1.25"
        assert serialized["regulatory_info"]["jurisdiction"] == "UK"
        
        # Test round-trip
        restored = MarketSpecificOrder.from_dict(serialized)
        assert restored.id == order.id
        assert restored.symbol.base_asset == order.symbol.base_asset
        assert restored.market_type == order.market_type
        assert restored.broker_order_id == order.broker_order_id
        assert restored.swap_cost == order.swap_cost
    
    def test_legacy_order_conversion(self):
        """Test conversion from/to legacy Order."""
        # Create legacy Order
        legacy_order = Order(
            id="legacy_123",
            symbol="ETHUSDT",
            side=OrderSide.BUY,
            amount=Decimal("10.0"),
            price=Decimal("2000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.OPEN,
            timestamp=datetime(2023, 1, 1, 10, 0, 0),
            exchange="coinbase",
            filled_amount=Decimal("5.0"),
            fees=Decimal("15.0")
        )
        
        # Convert to MarketSpecificOrder
        market_order = MarketSpecificOrder.from_legacy_order(
            legacy_order, MarketType.CRYPTO
        )
        
        assert market_order.id == legacy_order.id
        assert market_order.symbol.base_asset == "ETH"
        assert market_order.symbol.quote_asset == "USDT"
        assert market_order.market_type == MarketType.CRYPTO
        assert market_order.source == legacy_order.exchange
        assert market_order.filled_amount == legacy_order.filled_amount
        
        # Convert back to legacy
        converted_back = market_order.to_legacy_order()
        assert converted_back.id == legacy_order.id
        assert converted_back.symbol == legacy_order.symbol
        assert converted_back.exchange == legacy_order.exchange
        assert converted_back.amount == legacy_order.amount


class TestDataModelIntegration:
    """Integration tests for enhanced data models."""
    
    def test_crypto_workflow(self):
        """Test complete crypto trading workflow with enhanced models."""
        # Create crypto symbol
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        # Create session info for 24/7 crypto trading
        session = SessionInfo("24/7", True, market_type=MarketType.CRYPTO)
        
        # Create market data
        market_data = UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime.now(),
            open=Decimal("50000"),
            high=Decimal("51000"),
            low=Decimal("49000"),
            close=Decimal("50500"),
            volume=Decimal("100"),
            source="binance",
            market_type=MarketType.CRYPTO,
            session_info=session
        )
        
        # Create order
        order = MarketSpecificOrder(
            id="crypto_order_1",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.OPEN,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO
        )
        
        # Verify consistency
        assert market_data.symbol == order.symbol
        assert market_data.market_type == order.market_type
        assert market_data.source == order.source
    
    def test_forex_workflow(self):
        """Test complete forex trading workflow with enhanced models."""
        # Create forex symbol
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        # Create session info for London session
        session = SessionInfo(
            "London", 
            True, 
            market_type=MarketType.FOREX,
            next_close=datetime(2023, 1, 1, 17, 0, 0)
        )
        
        # Create market data
        market_data = UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime.now(),
            open=Decimal("1.1000"),
            high=Decimal("1.1100"),
            low=Decimal("1.0900"),
            close=Decimal("1.1050"),
            volume=Decimal("1000000"),
            source="oanda",
            market_type=MarketType.FOREX,
            session_info=session
        )
        
        # Create forex order with specific fields
        order = MarketSpecificOrder(
            id="forex_order_1",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("100000"),  # 1 lot
            price=Decimal("1.1000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="oanda",
            market_type=MarketType.FOREX,
            broker_order_id="OANDA_789",
            swap_cost=Decimal("2.50"),
            commission=Decimal("5.00"),
            regulatory_info={"mifid_compliant": True}
        )
        
        # Verify consistency and forex-specific features
        assert market_data.symbol == order.symbol
        assert market_data.market_type == order.market_type
        assert order.swap_cost is not None
        assert order.total_cost == Decimal("7.50")
        assert "mifid_compliant" in order.regulatory_info