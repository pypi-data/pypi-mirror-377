"""
Multi-Market Portfolio Management Example

This example demonstrates the enhanced portfolio management capabilities
for trading across cryptocurrency and forex markets with unified P&L
calculation, currency conversion, and cross-market exposure tracking.
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trading.multi_market_portfolio_manager import (
    MultiMarketPortfolioManager,
    CurrencyConverter
)
from src.models.data_models import MarketSpecificOrder, OrderSide, OrderType, OrderStatus, UnifiedMarketData
from src.markets.types import MarketType, UnifiedSymbol
from src.risk.cross_market_risk_manager import CrossMarketRiskManager
from tests.mocks.mock_exchange import MockExchange


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiMarketPortfolioExample:
    """Example demonstrating multi-market portfolio management."""
    
    def __init__(self):
        """Initialize the example."""
        # Create mock exchanges
        self.exchanges = {
            'binance': MockExchange('binance'),
            'oanda': MockExchange('oanda'),
            'mt5': MockExchange('mt5')
        }
        
        # Initialize portfolio manager
        self.portfolio_manager = MultiMarketPortfolioManager(
            exchanges=self.exchanges,
            initial_capital=Decimal("100000"),  # $100,000 initial capital
            base_currency="USD"
        )
        
        # Initialize risk manager
        self.risk_manager = CrossMarketRiskManager()
        
        logger.info("Multi-market portfolio management example initialized")
    
    async def demonstrate_currency_conversion(self):
        """Demonstrate currency conversion functionality."""
        logger.info("\n=== Currency Conversion Demo ===")
        
        converter = CurrencyConverter()
        
        # Test various currency conversions
        conversions = [
            (Decimal("1000"), "USD", "EUR"),
            (Decimal("1000"), "EUR", "USD"),
            (Decimal("1000"), "GBP", "USD"),
            (Decimal("1000"), "JPY", "USD"),
            (Decimal("1000"), "USDT", "USD")
        ]
        
        for amount, from_curr, to_curr in conversions:
            converted = converter.convert(amount, from_curr, to_curr)
            rate = converter.get_rate(from_curr, to_curr)
            
            logger.info(f"{amount} {from_curr} = {converted:.2f} {to_curr} (rate: {rate:.4f})")
        
        # Update rates
        new_rates = {
            'EUR': Decimal("1.15"),
            'GBP': Decimal("1.30")
        }
        converter.update_rates(new_rates)
        logger.info(f"Updated rates: {new_rates}")
    
    async def demonstrate_multi_market_trading(self):
        """Demonstrate trading across multiple markets."""
        logger.info("\n=== Multi-Market Trading Demo ===")
        
        # Create crypto positions
        await self._create_crypto_positions()
        
        # Create forex positions
        await self._create_forex_positions()
        
        # Show portfolio status
        await self._show_portfolio_status()
    
    async def _create_crypto_positions(self):
        """Create cryptocurrency positions."""
        logger.info("Creating cryptocurrency positions...")
        
        crypto_orders = [
            {
                'symbol': 'BTCUSDT',
                'side': OrderSide.BUY,
                'amount': Decimal("2.0"),
                'price': Decimal("45000"),
                'source': 'binance'
            },
            {
                'symbol': 'ETHUSDT',
                'side': OrderSide.BUY,
                'amount': Decimal("10.0"),
                'price': Decimal("3000"),
                'source': 'binance'
            },
            {
                'symbol': 'ADAUSDT',
                'side': OrderSide.BUY,
                'amount': Decimal("10000"),
                'price': Decimal("0.50"),
                'source': 'binance'
            }
        ]
        
        for order_data in crypto_orders:
            symbol = UnifiedSymbol.from_crypto_symbol(order_data['symbol'])
            
            order = MarketSpecificOrder(
                id=f"crypto_{datetime.now().timestamp()}",
                symbol=symbol,
                side=order_data['side'],
                amount=order_data['amount'],
                price=order_data['price'],
                order_type=OrderType.MARKET,
                status=OrderStatus.FILLED,
                timestamp=datetime.now(),
                source=order_data['source'],
                market_type=MarketType.CRYPTO,
                filled_amount=order_data['amount'],
                average_fill_price=order_data['price'],
                fees=order_data['amount'] * order_data['price'] * Decimal("0.001")  # 0.1% fee
            )
            
            trade = self.portfolio_manager.process_multi_market_order_fill(order)
            if trade:
                logger.info(f"Created crypto position: {symbol.to_standard_format()} "
                          f"({order_data['amount']} @ ${order_data['price']})")
    
    async def _create_forex_positions(self):
        """Create forex positions."""
        logger.info("Creating forex positions...")
        
        forex_orders = [
            {
                'symbol': 'EURUSD',
                'side': OrderSide.BUY,
                'amount': Decimal("100000"),  # 1 standard lot
                'price': Decimal("1.1000"),
                'source': 'oanda'
            },
            {
                'symbol': 'GBPUSD',
                'side': OrderSide.SELL,
                'amount': Decimal("50000"),   # 0.5 standard lot
                'price': Decimal("1.2500"),
                'source': 'oanda'
            },
            {
                'symbol': 'USDJPY',
                'side': OrderSide.BUY,
                'amount': Decimal("100000"),  # 1 standard lot
                'price': Decimal("150.00"),
                'source': 'mt5'
            }
        ]
        
        for order_data in forex_orders:
            symbol = UnifiedSymbol.from_forex_symbol(order_data['symbol'])
            
            order = MarketSpecificOrder(
                id=f"forex_{datetime.now().timestamp()}",
                symbol=symbol,
                side=order_data['side'],
                amount=order_data['amount'],
                price=order_data['price'],
                order_type=OrderType.MARKET,
                status=OrderStatus.FILLED,
                timestamp=datetime.now(),
                source=order_data['source'],
                market_type=MarketType.FOREX,
                filled_amount=order_data['amount'],
                average_fill_price=order_data['price'],
                fees=Decimal("5.0"),  # Fixed $5 commission
                swap_cost=Decimal("2.0")  # Daily swap cost
            )
            
            trade = self.portfolio_manager.process_multi_market_order_fill(order)
            if trade:
                logger.info(f"Created forex position: {symbol.to_standard_format()} "
                          f"({order_data['amount']} @ {order_data['price']})")
    
    async def _show_portfolio_status(self):
        """Show current portfolio status."""
        logger.info("\n=== Portfolio Status ===")
        
        # Get portfolio value
        total_value = self.portfolio_manager.get_multi_market_portfolio_value()
        logger.info(f"Total Portfolio Value: ${total_value:,.2f}")
        
        # Get market allocation
        allocation = self.portfolio_manager.get_market_allocation()
        logger.info("\nMarket Allocation:")
        for market_type, info in allocation.items():
            logger.info(f"  {market_type.value.upper()}:")
            logger.info(f"    Value: ${Decimal(info['value']):,.2f}")
            logger.info(f"    Allocation: {info['allocation_pct']:.1f}%")
            logger.info(f"    Positions: {info['position_count']}")
            logger.info(f"    Unrealized P&L: ${Decimal(info['unrealized_pnl']):,.2f}")
        
        # Get currency exposure
        exposure = self.portfolio_manager.get_currency_exposure()
        logger.info("\nCurrency Exposure:")
        for currency, info in exposure.items():
            logger.info(f"  {currency}: ${Decimal(info['amount']):,.2f} ({info['exposure_pct']:.1f}%)")
    
    async def demonstrate_price_updates(self):
        """Demonstrate price updates and P&L tracking."""
        logger.info("\n=== Price Updates Demo ===")
        
        # Simulate price movements
        price_updates = [
            # Crypto price updates
            {
                'symbol': UnifiedSymbol.from_crypto_symbol('BTCUSDT'),
                'new_price': Decimal("47000"),  # +4.4% gain
                'source': 'binance',
                'market_type': MarketType.CRYPTO
            },
            {
                'symbol': UnifiedSymbol.from_crypto_symbol('ETHUSDT'),
                'new_price': Decimal("2800"),   # -6.7% loss
                'source': 'binance',
                'market_type': MarketType.CRYPTO
            },
            # Forex price updates
            {
                'symbol': UnifiedSymbol.from_forex_symbol('EURUSD'),
                'new_price': Decimal("1.1050"),  # +0.45% gain
                'source': 'oanda',
                'market_type': MarketType.FOREX
            },
            {
                'symbol': UnifiedSymbol.from_forex_symbol('GBPUSD'),
                'new_price': Decimal("1.2400"),  # +0.8% gain (short position = loss)
                'source': 'oanda',
                'market_type': MarketType.FOREX
            }
        ]
        
        # Create market data updates
        market_data_updates = []
        for update in price_updates:
            market_data = UnifiedMarketData(
                symbol=update['symbol'],
                timestamp=datetime.now(),
                open=update['new_price'] * Decimal("0.99"),
                high=update['new_price'] * Decimal("1.01"),
                low=update['new_price'] * Decimal("0.98"),
                close=update['new_price'],
                volume=Decimal("1000"),
                source=update['source'],
                market_type=update['market_type']
            )
            market_data_updates.append(market_data)
        
        # Update prices
        self.portfolio_manager.update_multi_market_prices(market_data_updates)
        
        logger.info("Updated market prices:")
        for update in price_updates:
            logger.info(f"  {update['symbol'].to_standard_format()}: ${update['new_price']}")
        
        # Show updated portfolio status
        await self._show_portfolio_status()
    
    async def demonstrate_portfolio_rebalancing(self):
        """Demonstrate portfolio rebalancing across markets."""
        logger.info("\n=== Portfolio Rebalancing Demo ===")
        
        # Define target allocations
        target_allocations = {
            MarketType.CRYPTO: 60.0,  # 60% crypto
            MarketType.FOREX: 40.0    # 40% forex
        }
        
        logger.info(f"Target Allocations: Crypto {target_allocations[MarketType.CRYPTO]}%, "
                   f"Forex {target_allocations[MarketType.FOREX]}%")
        
        # Get rebalancing recommendations
        rebalancing_result = self.portfolio_manager.rebalance_portfolio(target_allocations)
        
        logger.info("\nRebalancing Analysis:")
        logger.info(f"Rebalancing Needed: {rebalancing_result['rebalancing_needed']}")
        
        if rebalancing_result['recommendations']:
            logger.info("\nRecommendations:")
            for rec in rebalancing_result['recommendations']:
                logger.info(f"  {rec['market_type'].upper()}:")
                logger.info(f"    Current: {rec['current_allocation_pct']:.1f}%")
                logger.info(f"    Target: {rec['target_allocation_pct']:.1f}%")
                logger.info(f"    Action: {rec['action']} ${Decimal(rec['difference_value']):,.2f}")
                logger.info(f"    Priority: {rec['priority']}")
        
        if rebalancing_result['suggested_trades']:
            logger.info("\nSuggested Trades:")
            for trade in rebalancing_result['suggested_trades']:
                logger.info(f"  {trade['action']} {trade['symbol']}: ${Decimal(trade['amount_usd']):,.2f}")
                logger.info(f"    Reason: {trade['reason']}")
    
    async def demonstrate_performance_analytics(self):
        """Demonstrate performance analytics and reporting."""
        logger.info("\n=== Performance Analytics Demo ===")
        
        # Create portfolio snapshot
        snapshot = self.portfolio_manager.create_multi_market_snapshot()
        
        logger.info("Portfolio Snapshot:")
        logger.info(f"  Timestamp: {snapshot.timestamp}")
        logger.info(f"  Total Value: ${snapshot.total_value:,.2f}")
        logger.info(f"  Crypto Value: ${snapshot.crypto_value:,.2f}")
        logger.info(f"  Forex Value: ${snapshot.forex_value:,.2f}")
        logger.info(f"  Total P&L: ${snapshot.total_pnl:,.2f}")
        logger.info(f"  Position Count: {snapshot.position_count}")
        
        # Get comprehensive performance summary
        summary = self.portfolio_manager.get_multi_market_performance_summary()
        
        logger.info("\nPerformance Summary:")
        logger.info(f"  Base Currency: {summary['base_currency']}")
        logger.info(f"  Total Return: {summary['total_return_pct']:.2f}%")
        logger.info(f"  Total Realized P&L: ${Decimal(summary['total_realized_pnl']):,.2f}")
        logger.info(f"  Total Unrealized P&L: ${Decimal(summary['total_unrealized_pnl']):,.2f}")
        logger.info(f"  Active Markets: {summary['active_markets']}")
        logger.info(f"  Total Trades: {summary['total_trades']}")
        
        logger.info("\nMarket Performance:")
        for market, perf in summary['market_performance'].items():
            logger.info(f"  {market.upper()}:")
            logger.info(f"    Allocation: {perf['allocation_pct']:.1f}%")
            logger.info(f"    Value: ${Decimal(perf['value']):,.2f}")
            logger.info(f"    Realized P&L: ${Decimal(perf['realized_pnl']):,.2f}")
            logger.info(f"    Unrealized P&L: ${Decimal(perf['unrealized_pnl']):,.2f}")
    
    async def demonstrate_position_closing(self):
        """Demonstrate closing positions and P&L realization."""
        logger.info("\n=== Position Closing Demo ===")
        
        # Close a crypto position (BTC)
        btc_symbol = UnifiedSymbol.from_crypto_symbol('BTCUSDT')
        
        close_order = MarketSpecificOrder(
            id=f"close_{datetime.now().timestamp()}",
            symbol=btc_symbol,
            side=OrderSide.SELL,  # Close long position
            amount=Decimal("1.0"),  # Close half of the 2.0 BTC position
            price=Decimal("48000"),  # Sell at higher price for profit
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source='binance',
            market_type=MarketType.CRYPTO,
            filled_amount=Decimal("1.0"),
            average_fill_price=Decimal("48000"),
            fees=Decimal("48")  # 0.1% fee
        )
        
        trade = self.portfolio_manager.process_multi_market_order_fill(close_order)
        
        if trade and trade.realized_pnl:
            logger.info(f"Closed BTC position:")
            logger.info(f"  Amount: {trade.amount} BTC")
            logger.info(f"  Exit Price: ${trade.price}")
            logger.info(f"  Realized P&L: ${trade.realized_pnl:,.2f}")
            logger.info(f"  Base Currency P&L: ${trade.base_currency_pnl:,.2f}")
        
        # Show updated portfolio status
        await self._show_portfolio_status()
    
    async def run_complete_example(self):
        """Run the complete multi-market portfolio management example."""
        logger.info("Starting Multi-Market Portfolio Management Example")
        logger.info("=" * 60)
        
        try:
            # Demonstrate currency conversion
            await self.demonstrate_currency_conversion()
            
            # Demonstrate multi-market trading
            await self.demonstrate_multi_market_trading()
            
            # Demonstrate price updates
            await self.demonstrate_price_updates()
            
            # Demonstrate portfolio rebalancing
            await self.demonstrate_portfolio_rebalancing()
            
            # Demonstrate performance analytics
            await self.demonstrate_performance_analytics()
            
            # Demonstrate position closing
            await self.demonstrate_position_closing()
            
            logger.info("\n" + "=" * 60)
            logger.info("Multi-Market Portfolio Management Example completed successfully!")
            
        except Exception as e:
            logger.error(f"Error in example: {str(e)}")
            raise


async def main():
    """Main function to run the example."""
    example = MultiMarketPortfolioExample()
    await example.run_complete_example()


if __name__ == "__main__":
    asyncio.run(main())