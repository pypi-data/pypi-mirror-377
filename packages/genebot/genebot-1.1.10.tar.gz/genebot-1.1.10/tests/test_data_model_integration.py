"""
Integration tests demonstrating enhanced data models with UnifiedSymbol normalization.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from src.models.data_models import UnifiedMarketData, MarketSpecificOrder, SessionInfo
from src.models.data_models import OrderSide, OrderType, OrderStatus
from src.markets.types import MarketType, UnifiedSymbol


class TestUnifiedSymbolNormalization:
    """Test UnifiedSymbol normalization methods with enhanced data models."""
    
    def test_crypto_symbol_normalization_in_market_data(self):
        """Test crypto symbol normalization in UnifiedMarketData."""
        # Test various crypto symbol formats
        test_cases = [
            ("BTCUSDT", "BTC", "USDT"),
            ("ETHUSDC", "ETH", "USDC"),
            ("ADABTC", "ADA", "BTC"),
            ("DOGEEUR", "DOGE", "EUR"),
        ]
        
        for native_symbol, expected_base, expected_quote in test_cases:
            symbol = UnifiedSymbol.from_crypto_symbol(native_symbol)
            
            market_data = UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open=Decimal("1000"),
                high=Decimal("1100"),
                low=Decimal("900"),
                close=Decimal("1050"),
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO
            )
            
            assert market_data.symbol.base_asset == expected_base
            assert market_data.symbol.quote_asset == expected_quote
            assert market_data.symbol.to_standard_format() == f"{expected_base}/{expected_quote}"
            assert market_data.symbol.to_crypto_format() == native_symbol
    
    def test_forex_symbol_normalization_in_orders(self):
        """Test forex symbol normalization in MarketSpecificOrder."""
        # Test various forex symbol formats
        test_cases = [
            ("EURUSD", "EUR", "USD"),
            ("GBPJPY", "GBP", "JPY"),
            ("AUDUSD", "AUD", "USD"),
            ("USDCAD", "USD", "CAD"),
        ]
        
        for native_symbol, expected_base, expected_quote in test_cases:
            symbol = UnifiedSymbol.from_forex_symbol(native_symbol)
            
            order = MarketSpecificOrder(
                id=f"order_{native_symbol}",
                symbol=symbol,
                side=OrderSide.BUY,
                amount=Decimal("100000"),  # 1 lot
                price=Decimal("1.2000"),
                order_type=OrderType.LIMIT,
                status=OrderStatus.OPEN,
                timestamp=datetime.now(),
                source="oanda",
                market_type=MarketType.FOREX,
                swap_cost=Decimal("2.50")
            )
            
            assert order.symbol.base_asset == expected_base
            assert order.symbol.quote_asset == expected_quote
            assert order.symbol.to_standard_format() == f"{expected_base}/{expected_quote}"
            assert order.symbol.to_forex_format() == native_symbol
    
    def test_cross_market_symbol_consistency(self):
        """Test symbol consistency across different data models."""
        # Create crypto symbol
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        # Create market data
        market_data = UnifiedMarketData(
            symbol=crypto_symbol,
            timestamp=datetime.now(),
            open=Decimal("50000"),
            high=Decimal("51000"),
            low=Decimal("49000"),
            close=Decimal("50500"),
            volume=Decimal("100"),
            source="binance",
            market_type=MarketType.CRYPTO
        )
        
        # Create order with same symbol
        order = MarketSpecificOrder(
            id="crypto_order_1",
            symbol=crypto_symbol,
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
        assert market_data.symbol.to_standard_format() == order.symbol.to_standard_format()
        assert market_data.market_type == order.market_type
        assert market_data.source == order.source
    
    def test_symbol_format_conversions(self):
        """Test various symbol format conversions."""
        # Test crypto symbol conversions
        crypto_symbol = UnifiedSymbol.from_standard_format("BTC/USDT", MarketType.CRYPTO)
        assert crypto_symbol.to_crypto_format() == "BTCUSDT"
        assert crypto_symbol.to_standard_format() == "BTC/USDT"
        
        # Test forex symbol conversions
        forex_symbol = UnifiedSymbol.from_standard_format("EUR/USD", MarketType.FOREX)
        assert forex_symbol.to_forex_format() == "EURUSD"
        assert forex_symbol.to_standard_format() == "EUR/USD"
        
        # Test with native symbols
        crypto_with_native = UnifiedSymbol.from_crypto_symbol("BTCUSDT", "BTC-USDT")
        assert crypto_with_native.native_symbol == "BTC-USDT"
        assert crypto_with_native.to_crypto_format() == "BTCUSDT"
    
    def test_session_info_integration(self):
        """Test SessionInfo integration with market data."""
        # Create forex session
        london_session = SessionInfo(
            session_name="London",
            is_active=True,
            next_close=datetime(2023, 1, 1, 17, 0, 0),
            market_type=MarketType.FOREX
        )
        
        # Create forex market data with session info
        forex_symbol = UnifiedSymbol.from_forex_symbol("GBPUSD")
        market_data = UnifiedMarketData(
            symbol=forex_symbol,
            timestamp=datetime.now(),
            open=Decimal("1.2500"),
            high=Decimal("1.2600"),
            low=Decimal("1.2400"),
            close=Decimal("1.2550"),
            volume=Decimal("1000000"),
            source="oanda",
            market_type=MarketType.FOREX,
            session_info=london_session
        )
        
        assert market_data.session_info.session_name == "London"
        assert market_data.session_info.is_active is True
        assert market_data.session_info.market_type == MarketType.FOREX
        
        # Create crypto session (24/7)
        crypto_session = SessionInfo(
            session_name="24/7",
            is_active=True,
            market_type=MarketType.CRYPTO
        )
        
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("ETHUSDT")
        crypto_data = UnifiedMarketData(
            symbol=crypto_symbol,
            timestamp=datetime.now(),
            open=Decimal("2000"),
            high=Decimal("2100"),
            low=Decimal("1900"),
            close=Decimal("2050"),
            volume=Decimal("500"),
            source="coinbase",
            market_type=MarketType.CRYPTO,
            session_info=crypto_session
        )
        
        assert crypto_data.session_info.session_name == "24/7"
        assert crypto_data.session_info.next_open is None
        assert crypto_data.session_info.next_close is None
    
    def test_market_specific_order_features(self):
        """Test market-specific features in orders."""
        # Test forex order with swap costs
        forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        forex_order = MarketSpecificOrder(
            id="forex_order_1",
            symbol=forex_symbol,
            side=OrderSide.BUY,
            amount=Decimal("100000"),  # 1 lot
            price=Decimal("1.1000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="mt5",
            market_type=MarketType.FOREX,
            broker_order_id="MT5_12345",
            swap_cost=Decimal("3.50"),
            commission=Decimal("7.00"),
            regulatory_info={
                "jurisdiction": "EU",
                "mifid_compliant": True,
                "leverage": 30
            }
        )
        
        assert forex_order.swap_cost == Decimal("3.50")
        assert forex_order.commission == Decimal("7.00")
        assert forex_order.total_cost == Decimal("10.50")  # fees + swap + commission
        assert forex_order.regulatory_info["mifid_compliant"] is True
        
        # Test crypto order (no swap costs)
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        crypto_order = MarketSpecificOrder(
            id="crypto_order_1",
            symbol=crypto_symbol,
            side=OrderSide.SELL,
            amount=Decimal("0.5"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            fees=Decimal("12.50")
        )
        
        assert crypto_order.swap_cost is None
        assert crypto_order.total_cost == Decimal("12.50")  # only fees
        assert crypto_order.regulatory_info == {}
    
    def test_serialization_round_trip(self):
        """Test complete serialization round-trip for all enhanced models."""
        # Create complex forex scenario
        forex_symbol = UnifiedSymbol.from_forex_symbol("GBPJPY")
        session = SessionInfo(
            session_name="Tokyo",
            is_active=True,
            next_close=datetime(2023, 1, 1, 9, 0, 0),
            market_type=MarketType.FOREX
        )
        
        market_data = UnifiedMarketData(
            symbol=forex_symbol,
            timestamp=datetime(2023, 1, 1, 8, 30, 0),
            open=Decimal("150.50"),
            high=Decimal("151.00"),
            low=Decimal("150.00"),
            close=Decimal("150.75"),
            volume=Decimal("2000000"),
            source="oanda",
            market_type=MarketType.FOREX,
            session_info=session
        )
        
        order = MarketSpecificOrder(
            id="complex_order_1",
            symbol=forex_symbol,
            side=OrderSide.BUY,
            amount=Decimal("50000"),  # 0.5 lot
            price=Decimal("150.50"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.PARTIALLY_FILLED,
            timestamp=datetime(2023, 1, 1, 8, 30, 0),
            source="oanda",
            market_type=MarketType.FOREX,
            broker_order_id="OANDA_789",
            swap_cost=Decimal("1.75"),
            commission=Decimal("4.25"),
            filled_amount=Decimal("25000"),
            average_fill_price=Decimal("150.52"),
            regulatory_info={"jurisdiction": "JP", "leverage": 25}
        )
        
        # Serialize
        market_data_dict = market_data.to_dict()
        order_dict = order.to_dict()
        
        # Deserialize
        restored_market_data = UnifiedMarketData.from_dict(market_data_dict)
        restored_order = MarketSpecificOrder.from_dict(order_dict)
        
        # Verify market data
        assert restored_market_data.symbol.base_asset == market_data.symbol.base_asset
        assert restored_market_data.symbol.quote_asset == market_data.symbol.quote_asset
        assert restored_market_data.market_type == market_data.market_type
        assert restored_market_data.open == market_data.open
        assert restored_market_data.session_info.session_name == market_data.session_info.session_name
        
        # Verify order
        assert restored_order.id == order.id
        assert restored_order.symbol.base_asset == order.symbol.base_asset
        assert restored_order.swap_cost == order.swap_cost
        assert restored_order.regulatory_info == order.regulatory_info
        assert restored_order.filled_amount == order.filled_amount