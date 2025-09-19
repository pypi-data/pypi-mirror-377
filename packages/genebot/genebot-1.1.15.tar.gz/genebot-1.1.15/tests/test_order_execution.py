"""
Integration tests for order execution workflow.

Tests the complete order execution and portfolio management workflow
including order placement, tracking, and portfolio updates.
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List

from src.trading.order_manager import OrderManager, OrderRequest, OrderValidationError, OrderExecutionError
from src.trading.portfolio_manager import PortfolioManager, Trade
from src.models.data_models import (
    Order, OrderSide, OrderType, OrderStatus, Position, MarketData, TradingSignal, SignalAction
)
from src.exchanges.base import ExchangeAdapter
from src.risk.risk_manager import RiskManager, RiskConfig


class MockExchange(ExchangeAdapter):
    """Mock exchange for testing."""
    
    def __init__(self, name: str, config: Dict):
        super().__init__(name, config)
        self._connected = True
        self._authenticated = True
        self.orders = {}
        self.order_counter = 1
        self.balances = {
            'USDT': {'free': Decimal('10000'), 'used': Decimal('0'), 'total': Decimal('10000')}
        }
        self.positions = []
        
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> None:
        pass
    
    async def authenticate(self) -> bool:
        return True
    
    async def health_check(self) -> Dict:
        return {'status': 'ok'}
    
    async def get_markets(self) -> Dict:
        return {
            'BTC/USDT': {'symbol': 'BTC/USDT', 'base': 'BTC', 'quote': 'USDT'},
            'ETH/USDT': {'symbol': 'ETH/USDT', 'base': 'ETH', 'quote': 'USDT'}
        }
    
    async def get_ticker(self, symbol: str) -> Dict:
        return {'symbol': symbol, 'last': 50000}
    
    async def get_orderbook(self, symbol: str, limit=None) -> Dict:
        return {'bids': [[49900, 1]], 'asks': [[50100, 1]]}
    
    async def get_ohlcv(self, symbol: str, timeframe='1h', since=None, limit=None) -> List[MarketData]:
        return [MarketData(
            symbol=symbol,
            timestamp=datetime.now(),
            open=Decimal('50000'),
            high=Decimal('51000'),
            low=Decimal('49000'),
            close=Decimal('50000'),
            volume=Decimal('100'),
            exchange=self.name
        )]
    
    async def get_balance(self) -> Dict:
        return self.balances
    
    async def create_order(self, symbol: str, side: OrderSide, amount: Decimal,
                          order_type: OrderType = OrderType.MARKET,
                          price: Decimal = None, params: Dict = None) -> Order:
        order_id = f"order_{self.order_counter}"
        self.order_counter += 1
        
        order = Order(
            id=order_id,
            symbol=symbol,
            side=side,
            amount=amount,
            price=price or Decimal('50000'),
            order_type=order_type,
            status=OrderStatus.FILLED,  # Simulate immediate fill
            timestamp=datetime.now(),
            exchange=self.name,
            filled_amount=amount,
            average_fill_price=price or Decimal('50000'),
            fees=amount * Decimal('0.001'),  # 0.1% fee
            client_order_id=params.get('clientOrderId') if params else None
        )
        
        self.orders[order_id] = order
        return order
    
    async def cancel_order(self, order_id: str, symbol: str) -> Order:
        if order_id in self.orders:
            order = self.orders[order_id]
            order.status = OrderStatus.CANCELLED
            return order
        raise Exception("Order not found")
    
    async def get_order(self, order_id: str, symbol: str) -> Order:
        if order_id in self.orders:
            return self.orders[order_id]
        raise Exception("Order not found")
    
    async def get_open_orders(self, symbol=None) -> List[Order]:
        orders = [o for o in self.orders.values() if o.status in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]]
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return orders
    
    async def get_order_history(self, symbol=None, since=None, limit=None) -> List[Order]:
        return list(self.orders.values())
    
    async def get_positions(self, symbol=None) -> List[Position]:
        return self.positions
    
    async def get_trades(self, symbol=None, since=None, limit=None) -> List[Dict]:
        return []
    
    def validate_credentials(self) -> bool:
        return True
    
    def get_trading_fees(self, symbol=None) -> Dict:
        return {'maker': Decimal('0.001'), 'taker': Decimal('0.001')}
    
    def get_minimum_order_size(self, symbol: str) -> Decimal:
        return Decimal('0.001')


@pytest.fixture
def mock_exchange():
    """Create mock exchange."""
    return MockExchange("test_exchange", {})


@pytest.fixture
def exchanges(mock_exchange):
    """Create exchanges dictionary."""
    return {"test_exchange": mock_exchange}


@pytest.fixture
def risk_manager():
    """Create risk manager."""
    config = RiskConfig(
        max_portfolio_risk_pct=0.02,
        max_daily_loss_pct=0.05,
        max_position_size_pct=0.20
    )
    return RiskManager(config)


@pytest.fixture
def order_manager(exchanges, risk_manager):
    """Create order manager."""
    return OrderManager(exchanges, risk_manager)


@pytest.fixture
def portfolio_manager(exchanges):
    """Create portfolio manager."""
    return PortfolioManager(exchanges, Decimal('10000'))


@pytest.mark.asyncio
class TestOrderExecution:
    """Test order execution workflow."""
    
    async def test_place_market_order_success(self, order_manager):
        """Test successful market order placement."""
        order_request = OrderRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('0.1'),
            order_type=OrderType.MARKET
        )
        
        order = await order_manager.place_order("test_exchange", order_request)
        
        assert order.id is not None
        assert order.symbol == "BTC/USDT"
        assert order.side == OrderSide.BUY
        assert order.amount == Decimal('0.1')
        assert order.status == OrderStatus.FILLED
        assert order.exchange == "test_exchange"
        
        # Check order is tracked
        active_orders = await order_manager.get_active_orders()
        assert len(active_orders) == 0  # Should be moved to history since filled
        
        history = await order_manager.get_order_history()
        assert len(history) == 1
        assert history[0].id == order.id
    
    async def test_place_limit_order_success(self, order_manager):
        """Test successful limit order placement."""
        order_request = OrderRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('0.1'),
            order_type=OrderType.LIMIT,
            price=Decimal('49000')
        )
        
        order = await order_manager.place_order("test_exchange", order_request)
        
        assert order.price == Decimal('49000')
        assert order.order_type == OrderType.LIMIT
    
    async def test_order_validation_failure(self, order_manager):
        """Test order validation failure."""
        # Test invalid exchange
        order_request = OrderRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('0.1')
        )
        
        with pytest.raises(OrderValidationError, match="Exchange 'invalid' not available"):
            await order_manager.place_order("invalid", order_request)
    
    async def test_risk_validation_failure(self, order_manager):
        """Test risk validation failure."""
        order_request = OrderRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('100'),  # Very large amount
            price=Decimal('50000')
        )
        
        portfolio_value = Decimal('10000')
        positions = []
        
        with pytest.raises(OrderValidationError, match="Risk validation failed"):
            await order_manager.place_order(
                "test_exchange", order_request, portfolio_value, positions
            )
    
    async def test_cancel_order_success(self, order_manager, mock_exchange):
        """Test successful order cancellation."""
        # Create an open order
        order = Order(
            id="test_order",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('0.1'),
            price=Decimal('49000'),
            order_type=OrderType.LIMIT,
            status=OrderStatus.OPEN,
            timestamp=datetime.now(),
            exchange="test_exchange"
        )
        
        mock_exchange.orders["test_order"] = order
        order_manager.active_orders["test_order"] = order
        
        cancelled_order = await order_manager.cancel_order("test_order")
        
        assert cancelled_order.status == OrderStatus.CANCELLED
        assert "test_order" not in order_manager.active_orders
    
    async def test_order_from_signal(self, order_manager):
        """Test creating order from trading signal."""
        signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal('50000')
        )
        
        order_request = await order_manager.create_order_from_signal(
            signal, "test_exchange", Decimal('0.1')
        )
        
        assert order_request.symbol == "BTC/USDT"
        assert order_request.side == OrderSide.BUY
        assert order_request.amount == Decimal('0.1')
        assert order_request.price == Decimal('50000')
        assert order_request.metadata['signal_strategy'] == "test_strategy"
    
    async def test_order_statistics(self, order_manager):
        """Test order statistics calculation."""
        # Place some orders
        for i in range(3):
            order_request = OrderRequest(
                symbol="BTC/USDT",
                side=OrderSide.BUY,
                amount=Decimal('0.1')
            )
            await order_manager.place_order("test_exchange", order_request)
        
        stats = order_manager.get_order_statistics()
        
        assert stats['total_orders'] == 3
        assert stats['filled_orders'] == 3
        assert stats['fill_rate_pct'] == 100.0
        assert 'test_exchange' in stats['exchange_stats']


@pytest.mark.asyncio
class TestPortfolioManagement:
    """Test portfolio management functionality."""
    
    async def test_initialize_balances(self, portfolio_manager):
        """Test balance initialization."""
        await portfolio_manager.initialize_balances()
        
        assert 'test_exchange' in portfolio_manager.cash_balances
        assert portfolio_manager.cash_balances['test_exchange'] == Decimal('10000')
    
    def test_process_buy_order_fill(self, portfolio_manager):
        """Test processing buy order fill."""
        order = Order(
            id="test_order",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('0.1'),
            price=Decimal('50000'),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            exchange="test_exchange",
            filled_amount=Decimal('0.1'),
            average_fill_price=Decimal('50000'),
            fees=Decimal('5')
        )
        
        portfolio_manager.cash_balances['test_exchange'] = Decimal('10000')
        trade = portfolio_manager.process_order_fill(order)
        
        assert trade is not None
        assert trade.symbol == "BTC/USDT"
        assert trade.side == OrderSide.BUY
        assert trade.amount == Decimal('0.1')
        
        # Check position created
        position = portfolio_manager.get_position("BTC/USDT", "test_exchange")
        assert position is not None
        assert position.size == Decimal('0.1')
        assert position.entry_price == Decimal('50000')
        
        # Check cash balance updated
        expected_cash = Decimal('10000') - (Decimal('0.1') * Decimal('50000') + Decimal('5'))
        assert portfolio_manager.cash_balances['test_exchange'] == expected_cash
    
    def test_process_sell_order_fill_close_position(self, portfolio_manager):
        """Test processing sell order that closes position."""
        # Create initial position
        position = Position(
            symbol="BTC/USDT",
            size=Decimal('0.1'),
            entry_price=Decimal('50000'),
            current_price=Decimal('55000'),
            timestamp=datetime.now(),
            exchange="test_exchange",
            side=OrderSide.BUY
        )
        portfolio_manager.positions["BTC/USDT_test_exchange"] = position
        portfolio_manager.cash_balances['test_exchange'] = Decimal('5000')
        
        # Create sell order
        sell_order = Order(
            id="sell_order",
            symbol="BTC/USDT",
            side=OrderSide.SELL,
            amount=Decimal('0.1'),
            price=Decimal('55000'),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            exchange="test_exchange",
            filled_amount=Decimal('0.1'),
            average_fill_price=Decimal('55000'),
            fees=Decimal('5.5')
        )
        
        trade = portfolio_manager.process_order_fill(sell_order)
        
        assert trade is not None
        assert trade.realized_pnl is not None
        assert trade.realized_pnl > 0  # Profit from 50000 to 55000
        
        # Position should be closed
        assert portfolio_manager.get_position("BTC/USDT", "test_exchange") is None
        
        # Check realized P&L updated
        assert portfolio_manager.realized_pnl > 0
    
    def test_update_market_prices(self, portfolio_manager):
        """Test market price updates."""
        # Create position
        position = Position(
            symbol="BTC/USDT",
            size=Decimal('0.1'),
            entry_price=Decimal('50000'),
            current_price=Decimal('50000'),
            timestamp=datetime.now(),
            exchange="test_exchange",
            side=OrderSide.BUY
        )
        portfolio_manager.positions["BTC/USDT_test_exchange"] = position
        
        # Update market price
        market_data = [MarketData(
            symbol="BTC/USDT",
            timestamp=datetime.now(),
            open=Decimal('50000'),
            high=Decimal('52000'),
            low=Decimal('49000'),
            close=Decimal('51000'),
            volume=Decimal('100'),
            exchange="test_exchange"
        )]
        
        portfolio_manager.update_market_prices(market_data)
        
        # Check position price updated
        updated_position = portfolio_manager.get_position("BTC/USDT", "test_exchange")
        assert updated_position.current_price == Decimal('51000')
        assert updated_position.unrealized_pnl > 0  # Profit from price increase
    
    def test_portfolio_value_calculation(self, portfolio_manager):
        """Test portfolio value calculation."""
        # Set cash balance
        portfolio_manager.cash_balances['test_exchange'] = Decimal('5000')
        
        # Add position
        position = Position(
            symbol="BTC/USDT",
            size=Decimal('0.1'),
            entry_price=Decimal('50000'),
            current_price=Decimal('55000'),
            timestamp=datetime.now(),
            exchange="test_exchange",
            side=OrderSide.BUY
        )
        portfolio_manager.positions["BTC/USDT_test_exchange"] = position
        
        total_value = portfolio_manager.get_portfolio_value()
        expected_value = Decimal('5000') + (Decimal('0.1') * Decimal('55000'))
        
        assert total_value == expected_value
    
    def test_portfolio_metrics_calculation(self, portfolio_manager):
        """Test portfolio metrics calculation."""
        # Add some trades
        trades = [
            Trade(
                id="trade1",
                symbol="BTC/USDT",
                side=OrderSide.BUY,
                amount=Decimal('0.1'),
                price=Decimal('50000'),
                fees=Decimal('5'),
                timestamp=datetime.now(),
                exchange="test_exchange",
                order_id="order1",
                realized_pnl=Decimal('500')  # Winning trade
            ),
            Trade(
                id="trade2",
                symbol="ETH/USDT",
                side=OrderSide.SELL,
                amount=Decimal('1.0'),
                price=Decimal('3000'),
                fees=Decimal('3'),
                timestamp=datetime.now(),
                exchange="test_exchange",
                order_id="order2",
                realized_pnl=Decimal('-200')  # Losing trade
            )
        ]
        
        portfolio_manager.trades = trades
        portfolio_manager.realized_pnl = Decimal('300')
        
        metrics = portfolio_manager.calculate_metrics()
        
        assert metrics.total_trades == 2
        assert metrics.winning_trades == 1
        assert metrics.losing_trades == 1
        assert metrics.win_rate_pct == 50.0
        assert metrics.average_win == Decimal('500')
        assert metrics.average_loss == Decimal('-200')
    
    def test_portfolio_summary(self, portfolio_manager):
        """Test portfolio summary generation."""
        portfolio_manager.cash_balances['test_exchange'] = Decimal('8000')
        portfolio_manager.realized_pnl = Decimal('500')
        
        summary = portfolio_manager.get_portfolio_summary()
        
        assert 'portfolio_value' in summary
        assert 'initial_capital' in summary
        assert 'cash_balances' in summary
        assert 'realized_pnl' in summary
        assert summary['initial_capital'] == '10000'
        assert summary['realized_pnl'] == '500'


@pytest.mark.asyncio
class TestIntegratedWorkflow:
    """Test integrated order execution and portfolio management workflow."""
    
    async def test_complete_trading_workflow(self, order_manager, portfolio_manager):
        """Test complete trading workflow from signal to portfolio update."""
        # Initialize portfolio
        await portfolio_manager.initialize_balances()
        
        # Create trading signal
        signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal('50000')
        )
        
        # Create order from signal
        order_request = await order_manager.create_order_from_signal(
            signal, "test_exchange", Decimal('0.1')
        )
        
        # Place order
        order = await order_manager.place_order("test_exchange", order_request)
        
        # Process order fill in portfolio
        trade = portfolio_manager.process_order_fill(order)
        
        # Verify workflow
        assert order.status == OrderStatus.FILLED
        assert trade is not None
        assert trade.symbol == "BTC/USDT"
        
        # Check position created
        position = portfolio_manager.get_position("BTC/USDT", "test_exchange")
        assert position is not None
        assert position.size == Decimal('0.1')
        
        # Update market price
        market_data = [MarketData(
            symbol="BTC/USDT",
            timestamp=datetime.now(),
            open=Decimal('50000'),
            high=Decimal('52000'),
            low=Decimal('49000'),
            close=Decimal('51000'),
            volume=Decimal('100'),
            exchange="test_exchange"
        )]
        
        portfolio_manager.update_market_prices(market_data)
        
        # Check unrealized P&L
        unrealized_pnl = portfolio_manager.get_unrealized_pnl()
        assert unrealized_pnl > 0  # Should have profit from price increase
        
        # Create snapshot
        snapshot = portfolio_manager.create_snapshot()
        assert snapshot.position_count == 1
        assert snapshot.unrealized_pnl > 0
    
    async def test_order_callback_integration(self, order_manager):
        """Test order callback functionality."""
        callback_called = False
        callback_update = None
        
        def order_callback(update):
            nonlocal callback_called, callback_update
            callback_called = True
            callback_update = update
        
        # Place order
        order_request = OrderRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('0.1')
        )
        
        order = await order_manager.place_order("test_exchange", order_request)
        
        # Add callback (order should already be filled)
        order_manager.add_order_callback(order.id, order_callback)
        
        # Since order is immediately filled in mock, callback should be triggered
        # during monitoring cycle
        await asyncio.sleep(0.1)  # Allow monitoring to run
        
        # Verify order is in history
        history = await order_manager.get_order_history()
        assert len(history) == 1
        assert history[0].status == OrderStatus.FILLED
    
    async def test_risk_integration_with_portfolio(self, order_manager, portfolio_manager, risk_manager):
        """Test risk management integration with portfolio."""
        # Initialize portfolio with limited capital
        portfolio_manager.cash_balances['test_exchange'] = Decimal('1000')
        
        # Try to place large order that exceeds risk limits
        order_request = OrderRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('1.0'),  # Large amount
            price=Decimal('50000')
        )
        
        portfolio_value = Decimal('1000')
        positions = []
        
        # Should fail risk validation
        with pytest.raises(OrderValidationError, match="Risk validation failed"):
            await order_manager.place_order(
                "test_exchange", order_request, portfolio_value, positions
            )
    
    async def test_multiple_exchange_workflow(self):
        """Test workflow with multiple exchanges."""
        # Create multiple mock exchanges
        exchange1 = MockExchange("exchange1", {})
        exchange2 = MockExchange("exchange2", {})
        exchanges = {"exchange1": exchange1, "exchange2": exchange2}
        
        order_manager = OrderManager(exchanges)
        portfolio_manager = PortfolioManager(exchanges, Decimal('20000'))
        
        # Initialize balances
        await portfolio_manager.initialize_balances()
        
        # Place orders on different exchanges
        order1_request = OrderRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal('0.1')
        )
        
        order2_request = OrderRequest(
            symbol="ETH/USDT",
            side=OrderSide.BUY,
            amount=Decimal('1.0')
        )
        
        order1 = await order_manager.place_order("exchange1", order1_request)
        order2 = await order_manager.place_order("exchange2", order2_request)
        
        # Process fills
        trade1 = portfolio_manager.process_order_fill(order1)
        trade2 = portfolio_manager.process_order_fill(order2)
        
        # Verify positions on different exchanges
        position1 = portfolio_manager.get_position("BTC/USDT", "exchange1")
        position2 = portfolio_manager.get_position("ETH/USDT", "exchange2")
        
        assert position1 is not None
        assert position2 is not None
        assert position1.exchange == "exchange1"
        assert position2.exchange == "exchange2"
        
        # Check portfolio summary includes both exchanges
        summary = portfolio_manager.get_portfolio_summary()
        assert len(summary['exchanges']) == 2
        assert summary['position_count'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])