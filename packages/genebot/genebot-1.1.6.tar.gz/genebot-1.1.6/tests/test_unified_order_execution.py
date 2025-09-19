"""
Tests for unified order execution system.

This module contains comprehensive tests for the UnifiedOrderManager,
including cross-market order execution, routing, and status tracking.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
from decimal import Decimal

from src.trading.unified_order_manager import (
    UnifiedOrderManager, UnifiedOrderRequest, OrderExecutionResult,
    OrderTypeTranslator, OrderValidationError, OrderExecutionError, OrderRoutingError
)
from src.models.data_models import (
    MarketSpecificOrder, OrderSide, OrderType, OrderStatus, TradingSignal, SignalAction
)
from src.markets.types import MarketType, UnifiedSymbol
from src.markets.manager import MarketManager
from src.risk.cross_market_risk_manager import CrossMarketRiskManager


class TestOrderTypeTranslator:
    """Test order type translation between market conventions."""
    
    def test_crypto_order_type_translation(self):
        """Test crypto order type translation."""
        # Test all supported crypto order types
        assert OrderTypeTranslator.translate_order_type(OrderType.MARKET, MarketType.CRYPTO) == "market"
        assert OrderTypeTranslator.translate_order_type(OrderType.LIMIT, MarketType.CRYPTO) == "limit"
        assert OrderTypeTranslator.translate_order_type(OrderType.STOP_LOSS, MarketType.CRYPTO) == "stop_market"
        assert OrderTypeTranslator.translate_order_type(OrderType.STOP_LIMIT, MarketType.CRYPTO) == "stop_limit"
    
    def test_forex_order_type_translation(self):
        """Test forex order type translation."""
        # Test all supported forex order types
        assert OrderTypeTranslator.translate_order_type(OrderType.MARKET, MarketType.FOREX) == "market"
        assert OrderTypeTranslator.translate_order_type(OrderType.LIMIT, MarketType.FOREX) == "limit"
        assert OrderTypeTranslator.translate_order_type(OrderType.STOP_LOSS, MarketType.FOREX) == "stop"
        assert OrderTypeTranslator.translate_order_type(OrderType.STOP_LIMIT, MarketType.FOREX) == "stop_limit"
    
    def test_unsupported_market_type(self):
        """Test translation with unsupported market type."""
        with pytest.raises(OrderValidationError, match="Unsupported market type"):
            OrderTypeTranslator.translate_order_type(OrderType.MARKET, "invalid_market")
    
    def test_get_supported_order_types(self):
        """Test getting supported order types for each market."""
        crypto_types = OrderTypeTranslator.get_supported_order_types(MarketType.CRYPTO)
        forex_types = OrderTypeTranslator.get_supported_order_types(MarketType.FOREX)
        
        assert OrderType.MARKET in crypto_types
        assert OrderType.LIMIT in crypto_types
        assert OrderType.STOP_LOSS in crypto_types
        assert OrderType.STOP_LIMIT in crypto_types
        
        assert OrderType.MARKET in forex_types
        assert OrderType.LIMIT in forex_types
        assert OrderType.STOP_LOSS in forex_types
        assert OrderType.STOP_LIMIT in forex_types


class TestUnifiedOrderRequest:
    """Test unified order request validation and creation."""
    
    def test_valid_crypto_order_request(self):
        """Test creating valid crypto order request."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.MARKET
        )
        
        assert request.symbol == symbol
        assert request.side == OrderSide.BUY
        assert request.amount == Decimal("0.1")
        assert request.order_type == OrderType.MARKET
        assert request.client_order_id is not None
    
    def test_valid_forex_order_request(self):
        """Test creating valid forex order request."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.SELL,
            amount=Decimal("1.0"),
            order_type=OrderType.LIMIT,
            price=Decimal("1.1000"),
            leverage=50
        )
        
        assert request.symbol == symbol
        assert request.side == OrderSide.SELL
        assert request.amount == Decimal("1.0")
        assert request.order_type == OrderType.LIMIT
        assert request.price == Decimal("1.1000")
        assert request.leverage == 50
    
    def test_invalid_amount(self):
        """Test validation with invalid amount."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        with pytest.raises(ValueError, match="Amount must be positive"):
            UnifiedOrderRequest(
                symbol=symbol,
                side=OrderSide.BUY,
                amount=Decimal("-0.1"),
                order_type=OrderType.MARKET
            )
    
    def test_limit_order_without_price(self):
        """Test validation of limit order without price."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        with pytest.raises(ValueError, match="Price required for limit orders"):
            UnifiedOrderRequest(
                symbol=symbol,
                side=OrderSide.BUY,
                amount=Decimal("0.1"),
                order_type=OrderType.LIMIT
            )
    
    def test_stop_order_without_stop_price(self):
        """Test validation of stop order without stop price."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        with pytest.raises(ValueError, match="Stop price required for stop orders"):
            UnifiedOrderRequest(
                symbol=symbol,
                side=OrderSide.BUY,
                amount=Decimal("0.1"),
                order_type=OrderType.STOP_LOSS
            )
    
    def test_leverage_on_crypto_order(self):
        """Test validation of leverage on crypto order."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        with pytest.raises(ValueError, match="Leverage is only applicable to forex orders"):
            UnifiedOrderRequest(
                symbol=symbol,
                side=OrderSide.BUY,
                amount=Decimal("0.1"),
                order_type=OrderType.MARKET,
                leverage=10
            )
    
    def test_to_dict_serialization(self):
        """Test order request serialization to dictionary."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            order_type=OrderType.LIMIT,
            price=Decimal("1.1000"),
            leverage=50
        )
        
        data = request.to_dict()
        
        assert data["symbol"]["base_asset"] == "EUR"
        assert data["symbol"]["quote_asset"] == "USD"
        assert data["symbol"]["market_type"] == "forex"
        assert data["side"] == "BUY"
        assert data["amount"] == "1.0"
        assert data["order_type"] == "LIMIT"
        assert data["price"] == "1.1000"
        assert data["leverage"] == 50


@pytest.fixture
def mock_market_manager():
    """Create mock market manager."""
    manager = Mock(spec=MarketManager)
    manager.get_supported_markets.return_value = [MarketType.CRYPTO, MarketType.FOREX]
    manager.is_market_supported.return_value = True
    manager.get_supported_symbols.return_value = [
        UnifiedSymbol.from_crypto_symbol("BTCUSDT"),
        UnifiedSymbol.from_forex_symbol("EURUSD")
    ]
    manager.place_order = AsyncMock(return_value={
        'id': 'test_order_123',
        'status': 'OPEN',
        'exchange': 'test_exchange',
        'filled': 0,
        'fee': 0.001
    })
    manager.cancel_order = AsyncMock(return_value=True)
    manager.get_order_status = AsyncMock(return_value={
        'status': 'FILLED',
        'filled': 0.1,
        'average': 50000,
        'fee': 0.001
    })
    manager.get_current_price = AsyncMock(return_value=50000.0)
    
    return manager


@pytest.fixture
def mock_risk_manager():
    """Create mock risk manager."""
    manager = Mock(spec=CrossMarketRiskManager)
    manager.validate_unified_order = AsyncMock(return_value=(True, "Risk validation passed"))
    return manager


@pytest.fixture
def unified_order_manager(mock_market_manager, mock_risk_manager):
    """Create unified order manager with mocked dependencies."""
    return UnifiedOrderManager(
        market_manager=mock_market_manager,
        risk_manager=mock_risk_manager,
        config={'routing': {}}
    )


class TestUnifiedOrderManager:
    """Test unified order manager functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, unified_order_manager):
        """Test unified order manager initialization."""
        assert unified_order_manager.market_manager is not None
        assert unified_order_manager.risk_manager is not None
        assert len(unified_order_manager.active_orders) == 0
        assert len(unified_order_manager.order_history) == 0
        assert not unified_order_manager._monitoring_active
    
    @pytest.mark.asyncio
    async def test_place_crypto_market_order(self, unified_order_manager):
        """Test placing crypto market order."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.MARKET
        )
        
        result = await unified_order_manager.place_order(
            request,
            portfolio_value=Decimal("10000"),
            current_positions=[]
        )
        
        assert isinstance(result, OrderExecutionResult)
        assert result.order.symbol == symbol
        assert result.order.side == OrderSide.BUY
        assert result.order.amount == Decimal("0.1")
        assert result.order.market_type == MarketType.CRYPTO
        assert result.routing_info['market_type'] == 'crypto'
        assert result.routing_info['execution_success'] is True
    
    @pytest.mark.asyncio
    async def test_place_forex_limit_order(self, unified_order_manager):
        """Test placing forex limit order."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.SELL,
            amount=Decimal("1.0"),
            order_type=OrderType.LIMIT,
            price=Decimal("1.1000"),
            leverage=50
        )
        
        result = await unified_order_manager.place_order(
            request,
            portfolio_value=Decimal("10000"),
            current_positions=[]
        )
        
        assert isinstance(result, OrderExecutionResult)
        assert result.order.symbol == symbol
        assert result.order.side == OrderSide.SELL
        assert result.order.order_type == OrderType.LIMIT
        assert result.order.price == Decimal("1.1000")
        assert result.order.market_type == MarketType.FOREX
        assert result.routing_info['market_type'] == 'forex'
    
    @pytest.mark.asyncio
    async def test_unsupported_market_type(self, unified_order_manager):
        """Test order placement with unsupported market type."""
        unified_order_manager.market_manager.is_market_supported.return_value = False
        
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.MARKET
        )
        
        with pytest.raises(OrderRoutingError, match="Market crypto is not supported"):
            await unified_order_manager.place_order(request)
    
    @pytest.mark.asyncio
    async def test_unsupported_order_type(self, unified_order_manager):
        """Test order placement with unsupported order type for market."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        # Mock unsupported order type
        with patch.object(OrderTypeTranslator, 'get_supported_order_types', return_value=[]):
            request = UnifiedOrderRequest(
                symbol=symbol,
                side=OrderSide.BUY,
                amount=Decimal("0.1"),
                order_type=OrderType.MARKET
            )
            
            with pytest.raises(OrderValidationError, match="Order type MARKET not supported"):
                await unified_order_manager.place_order(request)
    
    @pytest.mark.asyncio
    async def test_unsupported_symbol(self, unified_order_manager):
        """Test order placement with unsupported symbol."""
        unified_order_manager.market_manager.get_supported_symbols.return_value = []
        
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.MARKET
        )
        
        with pytest.raises(OrderValidationError, match="Symbol .* not supported"):
            await unified_order_manager.place_order(request)
    
    @pytest.mark.asyncio
    async def test_risk_validation_failure(self, unified_order_manager):
        """Test order placement with risk validation failure."""
        unified_order_manager.risk_manager.validate_unified_order.return_value = (
            False, "Position size too large"
        )
        
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.MARKET
        )
        
        with pytest.raises(OrderValidationError, match="Risk validation failed"):
            await unified_order_manager.place_order(
                request,
                portfolio_value=Decimal("10000"),
                current_positions=[]
            )
    
    @pytest.mark.asyncio
    async def test_cancel_order(self, unified_order_manager):
        """Test order cancellation."""
        # First place an order
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.LIMIT,
            price=Decimal("50000")
        )
        
        result = await unified_order_manager.place_order(request)
        order_id = result.order.id
        
        # Cancel the order
        cancelled_order = await unified_order_manager.cancel_order(order_id)
        
        assert cancelled_order.status == OrderStatus.CANCELLED
        assert order_id not in unified_order_manager.active_orders
        assert cancelled_order in unified_order_manager.order_history
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_order(self, unified_order_manager):
        """Test cancelling non-existent order."""
        with pytest.raises(OrderExecutionError, match="Order .* not found in active orders"):
            await unified_order_manager.cancel_order("nonexistent_order")
    
    @pytest.mark.asyncio
    async def test_get_order_status(self, unified_order_manager):
        """Test getting order status."""
        # Place an order first
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.LIMIT,
            price=Decimal("50000")
        )
        
        result = await unified_order_manager.place_order(request)
        order_id = result.order.id
        
        # Get order status
        order = await unified_order_manager.get_order_status(order_id)
        
        assert order.id == order_id
        assert order.status == OrderStatus.FILLED  # Based on mock return value
        assert order.filled_amount == Decimal("0.1")
    
    @pytest.mark.asyncio
    async def test_get_active_orders(self, unified_order_manager):
        """Test getting active orders with filtering."""
        # Place multiple orders
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        # Mock to return OPEN status to keep orders active
        unified_order_manager.market_manager.place_order.return_value = {
            'id': 'test_order_123',
            'status': 'OPEN',
            'exchange': 'test_exchange',
            'filled': 0,
            'fee': 0.001
        }
        
        crypto_request = UnifiedOrderRequest(
            symbol=crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.LIMIT,
            price=Decimal("50000")
        )
        
        forex_request = UnifiedOrderRequest(
            symbol=forex_symbol,
            side=OrderSide.SELL,
            amount=Decimal("1.0"),
            order_type=OrderType.LIMIT,
            price=Decimal("1.1000")
        )
        
        await unified_order_manager.place_order(crypto_request)
        await unified_order_manager.place_order(forex_request)
        
        # Test filtering
        all_orders = await unified_order_manager.get_active_orders()
        crypto_orders = await unified_order_manager.get_active_orders(market_type=MarketType.CRYPTO)
        forex_orders = await unified_order_manager.get_active_orders(market_type=MarketType.FOREX)
        symbol_orders = await unified_order_manager.get_active_orders(symbol=crypto_symbol)
        
        assert len(all_orders) == 2
        assert len(crypto_orders) == 1
        assert len(forex_orders) == 1
        assert len(symbol_orders) == 1
        assert crypto_orders[0].market_type == MarketType.CRYPTO
        assert forex_orders[0].market_type == MarketType.FOREX
    
    @pytest.mark.asyncio
    async def test_cancel_all_orders(self, unified_order_manager):
        """Test cancelling all orders."""
        # Place multiple orders
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        # Mock to return OPEN status to keep orders active
        unified_order_manager.market_manager.place_order.return_value = {
            'id': 'test_order_123',
            'status': 'OPEN',
            'exchange': 'test_exchange',
            'filled': 0,
            'fee': 0.001
        }
        
        crypto_request = UnifiedOrderRequest(
            symbol=crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.LIMIT,
            price=Decimal("50000")
        )
        
        forex_request = UnifiedOrderRequest(
            symbol=forex_symbol,
            side=OrderSide.SELL,
            amount=Decimal("1.0"),
            order_type=OrderType.LIMIT,
            price=Decimal("1.1000")
        )
        
        await unified_order_manager.place_order(crypto_request)
        await unified_order_manager.place_order(forex_request)
        
        # Cancel all orders
        cancelled_orders = await unified_order_manager.cancel_all_orders()
        
        assert len(cancelled_orders) == 2
        assert len(unified_order_manager.active_orders) == 0
        assert len(unified_order_manager.order_history) == 2
    
    @pytest.mark.asyncio
    async def test_create_order_from_signal(self, unified_order_manager):
        """Test creating order from trading signal."""
        signal = TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(timezone.utc),
            strategy_name="test_strategy",
            price=Decimal("50000")
        )
        
        order_request = await unified_order_manager.create_order_from_signal(
            signal=signal,
            amount=Decimal("0.1"),
            order_type=OrderType.LIMIT,
            price=Decimal("49000")
        )
        
        assert order_request.symbol.base_asset == "BTC"
        assert order_request.symbol.quote_asset == "USDT"
        assert order_request.symbol.market_type == MarketType.CRYPTO
        assert order_request.side == OrderSide.BUY
        assert order_request.amount == Decimal("0.1")
        assert order_request.order_type == OrderType.LIMIT
        assert order_request.price == Decimal("49000")
        assert order_request.metadata['signal_strategy'] == "test_strategy"
        assert order_request.metadata['signal_confidence'] == 0.8
    
    @pytest.mark.asyncio
    async def test_create_order_from_forex_signal(self, unified_order_manager):
        """Test creating order from forex trading signal."""
        signal = TradingSignal(
            symbol="EURUSD",
            action=SignalAction.SELL,
            confidence=0.9,
            timestamp=datetime.now(timezone.utc),
            strategy_name="forex_strategy",
            price=Decimal("1.1000")
        )
        
        order_request = await unified_order_manager.create_order_from_signal(
            signal=signal,
            amount=Decimal("1.0"),
            order_type=OrderType.MARKET
        )
        
        assert order_request.symbol.base_asset == "EUR"
        assert order_request.symbol.quote_asset == "USD"
        assert order_request.symbol.market_type == MarketType.FOREX
        assert order_request.side == OrderSide.SELL
        assert order_request.amount == Decimal("1.0")
        assert order_request.order_type == OrderType.MARKET
        assert order_request.price == Decimal("1.1000")  # From signal
    
    def test_execution_statistics(self, unified_order_manager):
        """Test execution statistics tracking."""
        # Update some stats manually for testing
        unified_order_manager._update_execution_stats(MarketType.CRYPTO, 'successful_orders')
        unified_order_manager._update_execution_stats(MarketType.CRYPTO, 'successful_orders')
        unified_order_manager._update_execution_stats(MarketType.FOREX, 'successful_orders')
        unified_order_manager._update_execution_stats(MarketType.FOREX, 'failed_orders')
        
        stats = unified_order_manager.get_execution_statistics()
        
        assert stats['overall']['total_orders'] == 4
        assert stats['overall']['successful_orders'] == 3
        assert stats['overall']['failed_orders'] == 1
        assert stats['success_rate_pct'] == 75.0
        assert stats['by_market']['crypto']['successful_orders'] == 2
        assert stats['by_market']['forex']['successful_orders'] == 1
        assert stats['by_market']['forex']['failed_orders'] == 1
    
    @pytest.mark.asyncio
    async def test_order_callbacks(self, unified_order_manager):
        """Test order status update callbacks."""
        callback_called = False
        callback_order = None
        
        def test_callback(order):
            nonlocal callback_called, callback_order
            callback_called = True
            callback_order = order
        
        # Place an order
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.LIMIT,
            price=Decimal("50000")
        )
        
        # Mock to return OPEN status to keep order active
        unified_order_manager.market_manager.place_order.return_value = {
            'id': 'test_order_123',
            'status': 'OPEN',
            'exchange': 'test_exchange',
            'filled': 0,
            'fee': 0.001
        }
        
        result = await unified_order_manager.place_order(request)
        order_id = result.order.id
        
        # Add callback
        unified_order_manager.add_order_callback(order_id, test_callback)
        
        # Trigger status check (which should call callback)
        await unified_order_manager._check_order_status(order_id)
        
        assert callback_called
        assert callback_order is not None
        assert callback_order.id == order_id
    
    @pytest.mark.asyncio
    async def test_forex_order_validation(self, unified_order_manager):
        """Test forex-specific order validation."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        # Test excessive leverage
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("1.0"),
            order_type=OrderType.MARKET,
            leverage=1000  # Excessive leverage
        )
        
        with pytest.raises(OrderValidationError, match="Forex leverage cannot exceed 500:1"):
            await unified_order_manager.place_order(request)
        
        # Test minimum position size
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.001"),  # Below minimum
            order_type=OrderType.MARKET
        )
        
        with pytest.raises(OrderValidationError, match="Forex minimum position size is 0.01 lots"):
            await unified_order_manager.place_order(request)
    
    @pytest.mark.asyncio
    async def test_crypto_order_validation(self, unified_order_manager):
        """Test crypto-specific order validation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        # Test minimum order size
        request = UnifiedOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.0001"),  # Below minimum
            order_type=OrderType.MARKET
        )
        
        with pytest.raises(OrderValidationError, match="Crypto minimum order size is 0.001"):
            await unified_order_manager.place_order(request)
    
    @pytest.mark.asyncio
    async def test_shutdown(self, unified_order_manager):
        """Test unified order manager shutdown."""
        # Start monitoring
        await unified_order_manager._start_monitoring()
        assert unified_order_manager._monitoring_active
        
        # Shutdown
        await unified_order_manager.shutdown()
        
        assert not unified_order_manager._monitoring_active
        assert unified_order_manager._monitor_task is None or unified_order_manager._monitor_task.done()


if __name__ == "__main__":
    pytest.main([__file__])