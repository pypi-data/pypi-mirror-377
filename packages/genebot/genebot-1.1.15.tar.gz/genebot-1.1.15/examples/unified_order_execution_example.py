"""
Unified Order Execution System Example

This example demonstrates how to use the UnifiedOrderManager to execute
orders across multiple markets (crypto and forex) with unified interfaces,
order type translation, and cross-market risk management.
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trading.unified_order_manager import (
    UnifiedOrderManager, UnifiedOrderRequest, OrderTypeTranslator
)
from src.models.data_models import OrderSide, OrderType, OrderStatus, TradingSignal, SignalAction
from src.markets.types import MarketType, UnifiedSymbol
from src.markets.manager import MarketManager
from src.risk.cross_market_risk_manager import CrossMarketRiskManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedOrderExecutionDemo:
    """Demonstration of unified order execution across multiple markets."""
    
    def __init__(self):
        """Initialize the demo with real components using environment variables."""
        self.market_manager = None
        self.risk_manager = None
        self.unified_order_manager = None
    
    async def setup(self):
        """Set up the unified order execution system."""
        logger.info("Setting up unified order execution system...")
        
        # Configure real components using environment variables
        # Ensure all required environment variables are set
        
        # Market manager configuration
        market_config = {
            'markets': {
                'crypto': {
                    'enabled': True,
                    'exchanges': [
                        {
                            'name': 'binance',
                            'api_key': os.getenv('BINANCE_API_KEY'),
                            'api_secret': os.getenv('BINANCE_API_SECRET'),
                            'sandbox': True
                        },
                        {
                            'name': 'coinbase',
                            'api_key': os.getenv('COINBASE_API_KEY'),
                            'api_secret': os.getenv('COINBASE_API_SECRET'),
                            'sandbox': True
                        }
                    ]
                },
                'forex': {
                    'enabled': True,
                    'brokers': [
                        {
                            'name': 'oanda',
                            'api_key': os.getenv('OANDA_API_KEY'),
                            'account_id': os.getenv('OANDA_ACCOUNT_ID'),
                            'sandbox': True
                        },
                        {
                            'name': 'mt5',
                            'login': os.getenv('MT5_LOGIN'),
                            'password': os.getenv('MT5_PASSWORD'),
                            'server': os.getenv('MT5_SERVER'),
                            'sandbox': True
                        }
                    ]
                }
            },
            'health_check_interval': 60,
            'failover_enabled': True
        }
        
        # Initialize market manager
        self.market_manager = MarketManager(market_config)
        # Note: In demo mode, we won't actually initialize connections
        
        # Initialize risk manager
        risk_config = {
            'unified_limits': {
                'max_portfolio_risk': 0.02,
                'max_correlation_exposure': 0.5,
                'daily_loss_limit': 0.05
            },
            'market_specific': {
                'crypto': {
                    'max_position_size': 0.1,
                    'leverage_limit': 3
                },
                'forex': {
                    'max_position_size': 0.05,
                    'leverage_limit': 50
                }
            }
        }
        
        self.risk_manager = CrossMarketRiskManager(risk_config)
        
        # Initialize unified order manager
        unified_config = {
            'routing': {
                'prefer_primary': True,
                'failover_enabled': True
            }
        }
        
        self.unified_order_manager = UnifiedOrderManager(
            market_manager=self.market_manager,
            risk_manager=self.risk_manager,
            config=unified_config
        )
        
        logger.info("Unified order execution system setup complete")
    
    def demonstrate_order_type_translation(self):
        """Demonstrate order type translation between market conventions."""
        logger.info("\n=== Order Type Translation Demo ===")
        
        # Show supported order types for each market
        crypto_types = OrderTypeTranslator.get_supported_order_types(MarketType.CRYPTO)
        forex_types = OrderTypeTranslator.get_supported_order_types(MarketType.FOREX)
        
        logger.info("Supported order types:")
        logger.info(f"  Crypto: {[t.value for t in crypto_types]}")
        logger.info(f"  Forex:  {[t.value for t in forex_types]}")
        
        # Demonstrate translation
        logger.info("\nOrder type translations:")
        for order_type in [OrderType.MARKET, OrderType.LIMIT, OrderType.STOP_LOSS, OrderType.STOP_LIMIT]:
            try:
                crypto_native = OrderTypeTranslator.translate_order_type(order_type, MarketType.CRYPTO)
                forex_native = OrderTypeTranslator.translate_order_type(order_type, MarketType.FOREX)
                logger.info(f"  {order_type.value:12} -> Crypto: {crypto_native:12} | Forex: {forex_native}")
            except Exception as e:
                logger.warning(f"  {order_type.value:12} -> Error: {e}")
    
    def demonstrate_unified_symbol_handling(self):
        """Demonstrate unified symbol handling across markets."""
        logger.info("\n=== Unified Symbol Handling Demo ===")
        
        # Create symbols for different markets
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        logger.info("Symbol representations:")
        logger.info(f"  Crypto Symbol: {crypto_symbol}")
        logger.info(f"    - Standard format: {crypto_symbol.to_standard_format()}")
        logger.info(f"    - Native format:   {crypto_symbol.native_symbol}")
        logger.info(f"    - Market type:     {crypto_symbol.market_type.value}")
        
        logger.info(f"  Forex Symbol: {forex_symbol}")
        logger.info(f"    - Standard format: {forex_symbol.to_standard_format()}")
        logger.info(f"    - Native format:   {forex_symbol.native_symbol}")
        logger.info(f"    - Market type:     {forex_symbol.market_type.value}")
    
    def demonstrate_order_request_creation(self):
        """Demonstrate creating unified order requests."""
        logger.info("\n=== Unified Order Request Creation Demo ===")
        
        # Crypto market order
        crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        crypto_request = UnifiedOrderRequest(
            symbol=crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            order_type=OrderType.MARKET,
            metadata={'strategy': 'momentum', 'confidence': 0.8}
        )
        
        logger.info("Crypto Market Order Request:")
        logger.info(f"  Symbol: {crypto_request.symbol}")
        logger.info(f"  Side: {crypto_request.side.value}")
        logger.info(f"  Amount: {crypto_request.amount}")
        logger.info(f"  Type: {crypto_request.order_type.value}")
        logger.info(f"  Client ID: {crypto_request.client_order_id}")
        
        # Forex limit order with leverage
        forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        forex_request = UnifiedOrderRequest(
            symbol=forex_symbol,
            side=OrderSide.SELL,
            amount=Decimal("1.0"),
            order_type=OrderType.LIMIT,
            price=Decimal("1.1000"),
            leverage=50,
            time_in_force="GTC",
            metadata={'strategy': 'mean_reversion', 'session': 'london'}
        )
        
        logger.info("\nForex Limit Order Request:")
        logger.info(f"  Symbol: {forex_request.symbol}")
        logger.info(f"  Side: {forex_request.side.value}")
        logger.info(f"  Amount: {forex_request.amount}")
        logger.info(f"  Type: {forex_request.order_type.value}")
        logger.info(f"  Price: {forex_request.price}")
        logger.info(f"  Leverage: {forex_request.leverage}")
        logger.info(f"  Time in Force: {forex_request.time_in_force}")
    
    async def demonstrate_signal_to_order_conversion(self):
        """Demonstrate converting trading signals to unified orders."""
        logger.info("\n=== Signal to Order Conversion Demo ===")
        
        # Crypto trading signal
        crypto_signal = TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.BUY,
            confidence=0.85,
            timestamp=datetime.now(timezone.utc),
            strategy_name="crypto_momentum",
            price=Decimal("50000"),
            metadata={'rsi': 30, 'volume_spike': True}
        )
        
        crypto_order_request = await self.unified_order_manager.create_order_from_signal(
            signal=crypto_signal,
            amount=Decimal("0.1"),
            order_type=OrderType.LIMIT,
            price=Decimal("49500")  # Slightly below signal price
        )
        
        logger.info("Crypto Signal to Order Conversion:")
        logger.info(f"  Original Signal: {crypto_signal.symbol} {crypto_signal.action.value}")
        logger.info(f"  Signal Price: {crypto_signal.price}")
        logger.info(f"  Signal Confidence: {crypto_signal.confidence}")
        logger.info(f"  Order Symbol: {crypto_order_request.symbol}")
        logger.info(f"  Order Side: {crypto_order_request.side.value}")
        logger.info(f"  Order Price: {crypto_order_request.price}")
        logger.info(f"  Order Metadata: {crypto_order_request.metadata}")
        
        # Forex trading signal
        forex_signal = TradingSignal(
            symbol="EURUSD",
            action=SignalAction.SELL,
            confidence=0.92,
            timestamp=datetime.now(timezone.utc),
            strategy_name="forex_breakout",
            price=Decimal("1.1050"),
            metadata={'breakout_level': 1.1060, 'volume': 'high'}
        )
        
        forex_order_request = await self.unified_order_manager.create_order_from_signal(
            signal=forex_signal,
            amount=Decimal("2.0"),
            order_type=OrderType.LIMIT,  # Changed from STOP_LIMIT to LIMIT
            price=Decimal("1.1040")
        )
        
        logger.info("\nForex Signal to Order Conversion:")
        logger.info(f"  Original Signal: {forex_signal.symbol} {forex_signal.action.value}")
        logger.info(f"  Signal Price: {forex_signal.price}")
        logger.info(f"  Signal Confidence: {forex_signal.confidence}")
        logger.info(f"  Order Symbol: {forex_order_request.symbol}")
        logger.info(f"  Order Side: {forex_order_request.side.value}")
        logger.info(f"  Order Price: {forex_order_request.price}")
        logger.info(f"  Order Type: {forex_order_request.order_type.value}")
    
    def demonstrate_order_validation(self):
        """Demonstrate order validation for different markets."""
        logger.info("\n=== Order Validation Demo ===")
        
        # Valid crypto order
        try:
            crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
            valid_crypto_request = UnifiedOrderRequest(
                symbol=crypto_symbol,
                side=OrderSide.BUY,
                amount=Decimal("0.1"),
                order_type=OrderType.MARKET
            )
            logger.info("✓ Valid crypto market order created successfully")
        except Exception as e:
            logger.error(f"✗ Valid crypto order failed: {e}")
        
        # Invalid crypto order (leverage not allowed)
        try:
            crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
            invalid_crypto_request = UnifiedOrderRequest(
                symbol=crypto_symbol,
                side=OrderSide.BUY,
                amount=Decimal("0.1"),
                order_type=OrderType.MARKET,
                leverage=10  # Not allowed for crypto
            )
            logger.error("✗ Invalid crypto order should have failed")
        except ValueError as e:
            logger.info(f"✓ Invalid crypto order correctly rejected: {e}")
        
        # Valid forex order with leverage
        try:
            forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
            valid_forex_request = UnifiedOrderRequest(
                symbol=forex_symbol,
                side=OrderSide.BUY,
                amount=Decimal("1.0"),
                order_type=OrderType.LIMIT,
                price=Decimal("1.1000"),
                leverage=50
            )
            logger.info("✓ Valid forex limit order with leverage created successfully")
        except Exception as e:
            logger.error(f"✗ Valid forex order failed: {e}")
        
        # Invalid order (negative amount)
        try:
            crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
            invalid_amount_request = UnifiedOrderRequest(
                symbol=crypto_symbol,
                side=OrderSide.BUY,
                amount=Decimal("-0.1"),  # Invalid negative amount
                order_type=OrderType.MARKET
            )
            logger.error("✗ Invalid amount order should have failed")
        except ValueError as e:
            logger.info(f"✓ Invalid amount order correctly rejected: {e}")
        
        # Invalid limit order (no price)
        try:
            crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
            invalid_limit_request = UnifiedOrderRequest(
                symbol=crypto_symbol,
                side=OrderSide.BUY,
                amount=Decimal("0.1"),
                order_type=OrderType.LIMIT  # No price specified
            )
            logger.error("✗ Invalid limit order should have failed")
        except ValueError as e:
            logger.info(f"✓ Invalid limit order correctly rejected: {e}")
    
    def demonstrate_execution_statistics(self):
        """Demonstrate execution statistics tracking."""
        logger.info("\n=== Execution Statistics Demo ===")
        
        # Simulate some execution statistics
        self.unified_order_manager._update_execution_stats(MarketType.CRYPTO, 'successful_orders')
        self.unified_order_manager._update_execution_stats(MarketType.CRYPTO, 'successful_orders')
        self.unified_order_manager._update_execution_stats(MarketType.CRYPTO, 'failed_orders')
        
        self.unified_order_manager._update_execution_stats(MarketType.FOREX, 'successful_orders')
        self.unified_order_manager._update_execution_stats(MarketType.FOREX, 'successful_orders')
        self.unified_order_manager._update_execution_stats(MarketType.FOREX, 'successful_orders')
        self.unified_order_manager._update_execution_stats(MarketType.FOREX, 'cancelled_orders')
        
        stats = self.unified_order_manager.get_execution_statistics()
        
        logger.info("Execution Statistics:")
        logger.info(f"  Overall Success Rate: {stats['success_rate_pct']:.1f}%")
        logger.info(f"  Total Orders: {stats['overall']['total_orders']}")
        logger.info(f"  Successful Orders: {stats['overall']['successful_orders']}")
        logger.info(f"  Failed Orders: {stats['overall']['failed_orders']}")
        logger.info(f"  Cancelled Orders: {stats['overall']['cancelled_orders']}")
        
        logger.info("\n  By Market:")
        for market, market_stats in stats['by_market'].items():
            logger.info(f"    {market.upper()}:")
            logger.info(f"      Total: {market_stats['total_orders']}")
            logger.info(f"      Successful: {market_stats['successful_orders']}")
            logger.info(f"      Failed: {market_stats['failed_orders']}")
            logger.info(f"      Cancelled: {market_stats['cancelled_orders']}")
        
        logger.info(f"\n  Active Orders: {stats['active_orders']}")
        logger.info(f"  Historical Orders: {stats['historical_orders']}")
        logger.info(f"  Monitoring Active: {stats['monitoring_active']}")
        logger.info(f"  Supported Markets: {stats['supported_markets']}")
    
    def demonstrate_order_serialization(self):
        """Demonstrate order request serialization."""
        logger.info("\n=== Order Serialization Demo ===")
        
        # Create a complex order request
        forex_symbol = UnifiedSymbol.from_forex_symbol("GBPJPY")
        complex_request = UnifiedOrderRequest(
            symbol=forex_symbol,
            side=OrderSide.BUY,
            amount=Decimal("0.5"),
            order_type=OrderType.STOP_LIMIT,
            price=Decimal("150.50"),
            stop_price=Decimal("150.00"),
            leverage=30,
            time_in_force="IOC",
            reduce_only=True,
            post_only=False,
            metadata={
                'strategy': 'breakout_scalping',
                'session': 'london_tokyo_overlap',
                'risk_level': 'medium',
                'expected_duration': '15min'
            }
        )
        
        # Serialize to dictionary
        serialized = complex_request.to_dict()
        
        logger.info("Complex Order Request Serialization:")
        logger.info(f"  Symbol: {serialized['symbol']}")
        logger.info(f"  Side: {serialized['side']}")
        logger.info(f"  Amount: {serialized['amount']}")
        logger.info(f"  Order Type: {serialized['order_type']}")
        logger.info(f"  Price: {serialized['price']}")
        logger.info(f"  Stop Price: {serialized['stop_price']}")
        logger.info(f"  Leverage: {serialized['leverage']}")
        logger.info(f"  Time in Force: {serialized['time_in_force']}")
        logger.info(f"  Reduce Only: {serialized['reduce_only']}")
        logger.info(f"  Post Only: {serialized['post_only']}")
        logger.info(f"  Client Order ID: {serialized['client_order_id']}")
        logger.info(f"  Metadata: {serialized['metadata']}")
    
    async def run_demo(self):
        """Run the complete unified order execution demo."""
        logger.info("Starting Unified Order Execution System Demo")
        logger.info("=" * 60)
        
        try:
            # Setup
            await self.setup()
            
            # Run demonstrations
            self.demonstrate_order_type_translation()
            self.demonstrate_unified_symbol_handling()
            self.demonstrate_order_request_creation()
            await self.demonstrate_signal_to_order_conversion()
            self.demonstrate_order_validation()
            self.demonstrate_execution_statistics()
            self.demonstrate_order_serialization()
            
            logger.info("\n" + "=" * 60)
            logger.info("Unified Order Execution System Demo completed successfully!")
            
        except Exception as e:
            logger.error(f"Demo failed with error: {e}")
            raise
        finally:
            # Cleanup
            if self.unified_order_manager:
                await self.unified_order_manager.shutdown()


async def main():
    """Main function to run the demo."""
    demo = UnifiedOrderExecutionDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())