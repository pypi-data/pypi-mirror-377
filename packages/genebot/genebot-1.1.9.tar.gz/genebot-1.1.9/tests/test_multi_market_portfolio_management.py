"""
Unit tests for multi-market portfolio management functionality.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.trading.multi_market_portfolio_manager import (
    MultiMarketPortfolioManager,
    MultiMarketTrade,
    MultiMarketPosition,
    MultiMarketPortfolioSnapshot,
    CurrencyConverter
)
from src.models.data_models import MarketSpecificOrder, OrderSide, OrderType, OrderStatus, UnifiedMarketData
from src.markets.types import MarketType, UnifiedSymbol
from src.risk.cross_market_risk_manager import CrossMarketRiskManager


class TestCurrencyConverter:
    """Test currency converter functionality."""
    
    def test_currency_converter_initialization(self):
        """Test currency converter initialization."""
        converter = CurrencyConverter()
        
        assert converter.rates['USD'] == Decimal("1.0")
        assert converter.rates['EUR'] > Decimal("1.0")
        assert converter.rates['USDT'] == Decimal("1.0")
    
    def test_get_rate_same_currency(self):
        """Test getting rate for same currency."""
        converter = CurrencyConverter()
        rate = converter.get_rate('USD', 'USD')
        
        assert rate == Decimal("1.0")
    
    def test_get_rate_different_currencies(self):
        """Test getting rate between different currencies."""
        converter = CurrencyConverter()
        rate = converter.get_rate('EUR', 'USD')
        
        assert rate > Decimal("1.0")  # EUR should be worth more than USD
    
    def test_convert_amount(self):
        """Test converting amount between currencies."""
        converter = CurrencyConverter()
        amount = Decimal("100")
        
        converted = converter.convert(amount, 'USD', 'USD')
        assert converted == amount
        
        converted_eur = converter.convert(amount, 'EUR', 'USD')
        assert converted_eur > amount  # EUR should convert to more USD
    
    def test_update_rates(self):
        """Test updating currency rates."""
        converter = CurrencyConverter()
        old_rate = converter.rates['EUR']
        
        new_rates = {'EUR': Decimal("1.2")}
        converter.update_rates(new_rates)
        
        assert converter.rates['EUR'] == Decimal("1.2")
        assert converter.rates['EUR'] != old_rate


class TestMultiMarketPosition:
    """Test multi-market position functionality."""
    
    def test_multi_market_position_creation(self):
        """Test creating a multi-market position."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        position = MultiMarketPosition(
            unified_symbol=symbol,
            size=Decimal("1.0"),
            entry_price=Decimal("50000"),
            current_price=Decimal("52000"),
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY
        )
        
        assert position.unified_symbol == symbol
        assert position.size == Decimal("1.0")
        assert position.market_type == MarketType.CRYPTO
        assert position.side == OrderSide.BUY
    
    def test_position_unrealized_pnl_long(self):
        """Test unrealized P&L calculation for long position."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        position = MultiMarketPosition(
            unified_symbol=symbol,
            size=Decimal("1.0"),
            entry_price=Decimal("50000"),
            current_price=Decimal("52000"),
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY
        )
        
        expected_pnl = Decimal("2000")  # (52000 - 50000) * 1.0
        assert position.unrealized_pnl == expected_pnl
    
    def test_position_unrealized_pnl_short(self):
        """Test unrealized P&L calculation for short position."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        position = MultiMarketPosition(
            unified_symbol=symbol,
            size=Decimal("10000"),
            entry_price=Decimal("1.1000"),
            current_price=Decimal("1.0900"),
            timestamp=datetime.now(),
            source="oanda",
            market_type=MarketType.FOREX,
            side=OrderSide.SELL
        )
        
        expected_pnl = Decimal("100")  # (1.1000 - 1.0900) * 10000 = 0.01 * 10000
        assert position.unrealized_pnl == expected_pnl
    
    def test_position_market_value(self):
        """Test market value calculation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        position = MultiMarketPosition(
            unified_symbol=symbol,
            size=Decimal("1.5"),
            entry_price=Decimal("50000"),
            current_price=Decimal("52000"),
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY
        )
        
        expected_value = Decimal("78000")  # 1.5 * 52000
        assert position.market_value == expected_value
    
    def test_position_update_price(self):
        """Test updating position price."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        position = MultiMarketPosition(
            unified_symbol=symbol,
            size=Decimal("1.0"),
            entry_price=Decimal("50000"),
            current_price=Decimal("50000"),
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY
        )
        
        new_price = Decimal("55000")
        conversion_rate = Decimal("1.0")
        position.update_price(new_price, conversion_rate)
        
        assert position.current_price == new_price
        assert position.conversion_rate == conversion_rate
    
    def test_position_to_dict(self):
        """Test position serialization to dictionary."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        position = MultiMarketPosition(
            unified_symbol=symbol,
            size=Decimal("1.0"),
            entry_price=Decimal("50000"),
            current_price=Decimal("52000"),
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY
        )
        
        position_dict = position.to_dict()
        
        assert position_dict['unified_symbol']['base_asset'] == 'BTC'
        assert position_dict['unified_symbol']['quote_asset'] == 'USDT'
        assert position_dict['market_type'] == 'crypto'
        assert position_dict['side'] == 'BUY'
        assert 'unrealized_pnl' in position_dict
        assert 'market_value' in position_dict


class TestMultiMarketTrade:
    """Test multi-market trade functionality."""
    
    def test_multi_market_trade_creation(self):
        """Test creating a multi-market trade."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        trade = MultiMarketTrade(
            id="trade_123",
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            fees=Decimal("50"),
            timestamp=datetime.now(),
            exchange="binance",
            order_id="order_123",
            market_type=MarketType.CRYPTO,
            unified_symbol=symbol
        )
        
        assert trade.market_type == MarketType.CRYPTO
        assert trade.unified_symbol == symbol
        assert trade.amount == Decimal("1.0")
    
    def test_trade_to_dict(self):
        """Test trade serialization to dictionary."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        trade = MultiMarketTrade(
            id="trade_123",
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            fees=Decimal("50"),
            timestamp=datetime.now(),
            exchange="binance",
            order_id="order_123",
            market_type=MarketType.CRYPTO,
            unified_symbol=symbol,
            base_currency_pnl=Decimal("2000"),
            conversion_rate=Decimal("1.0")
        )
        
        trade_dict = trade.to_dict()
        
        assert trade_dict['market_type'] == 'crypto'
        assert trade_dict['unified_symbol']['base_asset'] == 'BTC'
        assert trade_dict['base_currency_pnl'] == '2000'
        assert trade_dict['conversion_rate'] == '1.0'


class TestMultiMarketPortfolioManager:
    """Test multi-market portfolio manager functionality."""
    
    @pytest.fixture
    def mock_exchanges(self):
        """Create mock exchanges for testing."""
        crypto_exchange = Mock()
        crypto_exchange.is_connected = True
        crypto_exchange.is_authenticated = True
        
        forex_exchange = Mock()
        forex_exchange.is_connected = True
        forex_exchange.is_authenticated = True
        
        return {
            'binance': crypto_exchange,
            'oanda': forex_exchange
        }
    
    @pytest.fixture
    def portfolio_manager(self, mock_exchanges):
        """Create portfolio manager for testing."""
        return MultiMarketPortfolioManager(
            exchanges=mock_exchanges,
            initial_capital=Decimal("10000"),
            base_currency="USD"
        )
    
    def test_portfolio_manager_initialization(self, portfolio_manager):
        """Test portfolio manager initialization."""
        assert portfolio_manager.base_currency == "USD"
        assert portfolio_manager.initial_capital == Decimal("10000")
        assert len(portfolio_manager.multi_market_positions) == 0
        assert len(portfolio_manager.multi_market_trades) == 0
        assert MarketType.CRYPTO in portfolio_manager.market_balances
        assert MarketType.FOREX in portfolio_manager.market_balances
    
    def test_process_crypto_order_fill(self, portfolio_manager):
        """Test processing a crypto order fill."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        trade = portfolio_manager.process_multi_market_order_fill(order)
        
        assert trade is not None
        assert trade.market_type == MarketType.CRYPTO
        assert trade.unified_symbol == symbol
        assert len(portfolio_manager.multi_market_positions) == 1
        assert len(portfolio_manager.multi_market_trades) == 1
    
    def test_process_forex_order_fill(self, portfolio_manager):
        """Test processing a forex order fill."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        order = MarketSpecificOrder(
            id="order_456",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("10000"),
            price=Decimal("1.1000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="oanda",
            market_type=MarketType.FOREX,
            filled_amount=Decimal("10000"),
            average_fill_price=Decimal("1.1000"),
            fees=Decimal("5"),
            swap_cost=Decimal("2")
        )
        
        trade = portfolio_manager.process_multi_market_order_fill(order)
        
        assert trade is not None
        assert trade.market_type == MarketType.FOREX
        assert trade.swap_cost == Decimal("2")
        assert len(portfolio_manager.multi_market_positions) == 1
    
    def test_update_multi_market_prices(self, portfolio_manager):
        """Test updating multi-market prices."""
        # First create a position
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        portfolio_manager.process_multi_market_order_fill(order)
        
        # Update prices
        market_data = [
            UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open=Decimal("50000"),
                high=Decimal("52000"),
                low=Decimal("49000"),
                close=Decimal("51000"),
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO
            )
        ]
        
        portfolio_manager.update_multi_market_prices(market_data)
        
        # Check that position price was updated
        position_key = f"{symbol.to_standard_format()}_binance_crypto"
        position = portfolio_manager.multi_market_positions[position_key]
        assert position.current_price == Decimal("51000")
    
    def test_get_multi_market_portfolio_value(self, portfolio_manager):
        """Test calculating multi-market portfolio value."""
        # Add some positions
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        # Crypto order
        crypto_order = MarketSpecificOrder(
            id="order_123",
            symbol=crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        # Forex order
        forex_order = MarketSpecificOrder(
            id="order_456",
            symbol=forex_symbol,
            side=OrderSide.BUY,
            amount=Decimal("10000"),
            price=Decimal("1.1000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="oanda",
            market_type=MarketType.FOREX,
            filled_amount=Decimal("10000"),
            average_fill_price=Decimal("1.1000"),
            fees=Decimal("5")
        )
        
        portfolio_manager.process_multi_market_order_fill(crypto_order)
        portfolio_manager.process_multi_market_order_fill(forex_order)
        
        total_value = portfolio_manager.get_multi_market_portfolio_value()
        assert total_value > Decimal("0")
    
    def test_get_market_allocation(self, portfolio_manager):
        """Test getting market allocation breakdown."""
        # Add crypto position
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        portfolio_manager.process_multi_market_order_fill(order)
        
        allocation = portfolio_manager.get_market_allocation()
        
        assert MarketType.CRYPTO in allocation
        assert MarketType.FOREX in allocation
        assert allocation[MarketType.CRYPTO]['position_count'] == 1
        assert allocation[MarketType.FOREX]['position_count'] == 0
    
    def test_get_currency_exposure(self, portfolio_manager):
        """Test getting currency exposure breakdown."""
        # Add position
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        portfolio_manager.process_multi_market_order_fill(order)
        
        exposure = portfolio_manager.get_currency_exposure()
        
        assert 'BTC' in exposure or 'USD' in exposure or 'USDT' in exposure
        assert len(exposure) > 0
    
    def test_create_multi_market_snapshot(self, portfolio_manager):
        """Test creating multi-market portfolio snapshot."""
        # Add positions
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        portfolio_manager.process_multi_market_order_fill(order)
        
        snapshot = portfolio_manager.create_multi_market_snapshot()
        
        assert isinstance(snapshot, MultiMarketPortfolioSnapshot)
        assert snapshot.position_count == 1
        assert snapshot.crypto_value > Decimal("0")
        assert snapshot.forex_value >= Decimal("0")  # May have initial balance
        assert len(portfolio_manager.multi_market_snapshots) == 1
    
    def test_rebalance_portfolio(self, portfolio_manager):
        """Test portfolio rebalancing functionality."""
        # Add crypto position to create imbalance
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        portfolio_manager.process_multi_market_order_fill(order)
        
        # Set target allocations
        target_allocations = {
            MarketType.CRYPTO: 50.0,
            MarketType.FOREX: 50.0
        }
        
        rebalancing_result = portfolio_manager.rebalance_portfolio(target_allocations)
        
        assert 'recommendations' in rebalancing_result
        assert 'suggested_trades' in rebalancing_result
        assert 'rebalancing_needed' in rebalancing_result
        assert isinstance(rebalancing_result['recommendations'], list)
    
    def test_get_multi_market_performance_summary(self, portfolio_manager):
        """Test getting multi-market performance summary."""
        # Add some positions and trades
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        portfolio_manager.process_multi_market_order_fill(order)
        
        summary = portfolio_manager.get_multi_market_performance_summary()
        
        assert 'base_currency' in summary
        assert 'total_value' in summary
        assert 'market_allocation' in summary
        assert 'market_performance' in summary
        assert 'currency_exposure' in summary
        assert summary['base_currency'] == 'USD'
        assert summary['total_positions'] == 1
        assert summary['active_markets'] >= 1
    
    def test_position_closing_pnl_calculation(self, portfolio_manager):
        """Test P&L calculation when closing positions."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        # Open position
        buy_order = MarketSpecificOrder(
            id="order_buy",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("50000"),
            fees=Decimal("50")
        )
        
        portfolio_manager.process_multi_market_order_fill(buy_order)
        
        # Close position at higher price
        sell_order = MarketSpecificOrder(
            id="order_sell",
            symbol=symbol,
            side=OrderSide.SELL,
            amount=Decimal("1.0"),
            price=Decimal("52000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("52000"),
            fees=Decimal("50")
        )
        
        trade = portfolio_manager.process_multi_market_order_fill(sell_order)
        
        assert trade is not None
        assert trade.realized_pnl is not None
        assert trade.realized_pnl > Decimal("0")  # Should be profitable
        assert len(portfolio_manager.multi_market_positions) == 0  # Position should be closed
    
    def test_error_handling_invalid_order(self, portfolio_manager):
        """Test error handling for invalid orders."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        # Order with PENDING status (not filled)
        order = MarketSpecificOrder(
            id="order_123",
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.PENDING,  # Not filled
            timestamp=datetime.now(),
            source="binance",
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("0"),
            fees=Decimal("0")
        )
        
        trade = portfolio_manager.process_multi_market_order_fill(order)
        
        assert trade is None  # Should return None for non-filled orders
        assert len(portfolio_manager.multi_market_positions) == 0
        assert len(portfolio_manager.multi_market_trades) == 0


if __name__ == "__main__":
    pytest.main([__file__])