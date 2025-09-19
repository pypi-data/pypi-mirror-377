"""
Example demonstrating order execution and portfolio management.

This example shows how to use the OrderManager and PortfolioManager
to execute trades and track portfolio performance.
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trading.order_manager import OrderManager, OrderRequest
from src.trading.portfolio_manager import PortfolioManager
from src.models.data_models import OrderSide, OrderType, TradingSignal, SignalAction, MarketData
from src.risk.risk_manager import RiskManager, RiskConfig


class MockExchange:
    """Simple mock exchange for demonstration."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_connected = True
        self.is_authenticated = True
        self.order_counter = 1
    
    async def create_order(self, symbol, side, amount, order_type=OrderType.MARKET, price=None, params=None):
        from src.models.data_models import Order, OrderStatus
        
        order_id = f"order_{self.order_counter}"
        self.order_counter += 1
        
        return Order(
            id=order_id,
            symbol=symbol,
            side=side,
            amount=amount,
            price=price or Decimal('50000'),
            order_type=order_type,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            exchange=self.name,
            filled_amount=amount,
            average_fill_price=price or Decimal('50000'),
            fees=amount * Decimal('0.001')
        )
    
    def get_minimum_order_size(self, symbol):
        return Decimal('0.001')
    
    async def get_markets(self):
        return {'BTC/USDT': {'symbol': 'BTC/USDT'}}


async def main():
    """Demonstrate order execution and portfolio management."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create mock exchange
    exchange = MockExchange("demo_exchange")
    exchanges = {"demo_exchange": exchange}
    
    # Create risk manager
    risk_config = RiskConfig(max_position_size_pct=0.1)
    risk_manager = RiskManager(risk_config)
    
    # Create managers
    order_manager = OrderManager(exchanges, risk_manager)
    portfolio_manager = PortfolioManager(exchanges, Decimal('10000'))
    
    print("=== Order Execution and Portfolio Management Demo ===\n")
    
    # Initialize portfolio
    portfolio_manager.cash_balances['demo_exchange'] = Decimal('10000')
    print(f"Initial portfolio value: ${portfolio_manager.get_portfolio_value()}")
    
    # Create trading signal
    signal = TradingSignal(
        symbol="BTC/USDT",
        action=SignalAction.BUY,
        confidence=0.8,
        timestamp=datetime.now(),
        strategy_name="demo_strategy"
    )
    
    # Create order from signal
    order_request = await order_manager.create_order_from_signal(
        signal, "demo_exchange", Decimal('0.1')
    )
    
    print(f"Created order request: {order_request.symbol} {order_request.side.value} {order_request.amount}")
    
    # Place order
    order = await order_manager.place_order("demo_exchange", order_request)
    print(f"Order placed: {order.id} - Status: {order.status.value}")
    
    # Process order fill in portfolio
    trade = portfolio_manager.process_order_fill(order)
    print(f"Trade processed: {trade.symbol} - Amount: {trade.amount}")
    
    # Check position
    position = portfolio_manager.get_position("BTC/USDT", "demo_exchange")
    if position:
        print(f"Position created: {position.symbol} - Size: {position.size} - Entry: ${position.entry_price}")
    
    # Update market price
    market_data = [MarketData(
        symbol="BTC/USDT",
        timestamp=datetime.now(),
        open=Decimal('50000'),
        high=Decimal('52000'),
        low=Decimal('49000'),
        close=Decimal('51000'),
        volume=Decimal('100'),
        exchange="demo_exchange"
    )]
    
    portfolio_manager.update_market_prices(market_data)
    print(f"Market price updated to: ${market_data[0].close}")
    
    # Check unrealized P&L
    unrealized_pnl = portfolio_manager.get_unrealized_pnl()
    print(f"Unrealized P&L: ${unrealized_pnl}")
    
    # Create portfolio snapshot
    snapshot = portfolio_manager.create_snapshot()
    print(f"\nPortfolio Snapshot:")
    print(f"  Total Value: ${snapshot.total_value}")
    print(f"  Cash: ${snapshot.cash_balance}")
    print(f"  Positions Value: ${snapshot.positions_value}")
    print(f"  Unrealized P&L: ${snapshot.unrealized_pnl}")
    print(f"  Position Count: {snapshot.position_count}")
    
    # Get order statistics
    stats = order_manager.get_order_statistics()
    print(f"\nOrder Statistics:")
    print(f"  Total Orders: {stats['total_orders']}")
    print(f"  Fill Rate: {stats['fill_rate_pct']:.1f}%")
    
    # Cleanup
    await order_manager.shutdown()
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())