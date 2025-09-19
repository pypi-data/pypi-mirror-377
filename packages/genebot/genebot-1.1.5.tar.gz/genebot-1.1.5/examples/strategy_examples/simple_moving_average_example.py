#!/usr/bin/env python3
"""
Simple Moving Average Strategy Example

This example demonstrates how to implement and use a basic moving average crossover strategy.
The strategy generates buy signals when the short-term moving average crosses above the long-term
moving average, and sell signals when it crosses below.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from src.strategies.moving_average_strategy import MovingAverageStrategy
from src.strategies.strategy_engine import StrategyEngine
from src.data.collector import MarketDataCollector
from src.exchanges.ccxt_adapter import CCXTAdapter
from src.models.data_models import MarketData, TradingSignal
from config.manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMovingAverageExample:
    """Example implementation of a simple moving average strategy"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.strategy_engine = StrategyEngine()
        self.data_collector = None
        self.exchange_adapter = None
        
    async def setup(self):
        """Initialize the example components"""
        logger.info("Setting up Simple Moving Average Strategy Example")
        
        # Load configuration
        self.config_manager.load_config('config/trading_bot_config.yaml')
        
        # Initialize exchange adapter (using sandbox mode)
        exchange_config = {
            'apiKey': 'your_api_key',  # Replace with actual API key
            'secret': 'your_secret',   # Replace with actual secret
            'sandbox': True,           # Use testnet for examples
            'enableRateLimit': True
        }
        
        self.exchange_adapter = CCXTAdapter('binance', exchange_config)
        await self.exchange_adapter.connect()
        
        # Initialize data collector
        self.data_collector = MarketDataCollector(self.exchange_adapter)
        
        # Configure strategy
        strategy_config = {
            'short_period': 10,      # 10-period short moving average
            'long_period': 20,       # 20-period long moving average
            'confidence_threshold': 0.7,  # Minimum confidence for signals
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'timeframe': '1h'
        }
        
        # Create and register strategy
        ma_strategy = MovingAverageStrategy(strategy_config)
        self.strategy_engine.register_strategy('moving_average', ma_strategy)
        
        logger.info("Setup completed successfully")
    
    async def run_backtest_example(self):
        """Run a backtest example with historical data"""
        logger.info("Running backtest example")
        
        # Get historical data for backtesting
        symbol = 'BTC/USDT'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        historical_data = await self.data_collector.get_historical_data(
            symbol=symbol,
            timeframe='1h',
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        logger.info(f"Retrieved {len(historical_data)} historical data points")
        
        # Get strategy instance
        strategy = self.strategy_engine.get_strategy('moving_average')
        
        # Process historical data and generate signals
        signals = []
        for data_point in historical_data:
            signal = await strategy.analyze(data_point)
            if signal.action != 'HOLD':
                signals.append(signal)
                logger.info(f"Signal generated: {signal.action} {signal.symbol} "
                          f"at {signal.timestamp} (confidence: {signal.confidence:.2f})")
        
        logger.info(f"Generated {len(signals)} trading signals")
        
        # Analyze signal performance
        self._analyze_signals(signals, historical_data)
    
    async def run_realtime_example(self):
        """Run a real-time trading example"""
        logger.info("Starting real-time trading example")
        
        symbols = ['BTC/USDT', 'ETH/USDT']
        
        # Start real-time data collection
        await self.data_collector.start_realtime_collection(symbols)
        
        # Get strategy instance
        strategy = self.strategy_engine.get_strategy('moving_average')
        
        try:
            # Run for 5 minutes as an example
            end_time = datetime.now() + timedelta(minutes=5)
            
            while datetime.now() < end_time:
                for symbol in symbols:
                    # Get latest market data
                    latest_data = await self.data_collector.get_latest_data(symbol)
                    
                    if latest_data:
                        # Generate trading signal
                        signal = await strategy.analyze(latest_data)
                        
                        if signal.action != 'HOLD':
                            logger.info(f"Real-time signal: {signal.action} {signal.symbol} "
                                      f"at {signal.timestamp} (confidence: {signal.confidence:.2f})")
                            
                            # In a real implementation, you would execute the trade here
                            await self._simulate_trade_execution(signal, latest_data)
                
                # Wait before next iteration
                await asyncio.sleep(10)  # Check every 10 seconds
                
        finally:
            # Stop data collection
            await self.data_collector.stop_realtime_collection()
            logger.info("Real-time example completed")
    
    async def _simulate_trade_execution(self, signal: TradingSignal, market_data: MarketData):
        """Simulate trade execution (for example purposes only)"""
        logger.info(f"Simulating {signal.action} order for {signal.symbol}")
        logger.info(f"Current price: {market_data.close}")
        logger.info(f"Signal confidence: {signal.confidence:.2f}")
        logger.info(f"Signal metadata: {signal.metadata}")
        
        # In a real implementation, you would:
        # 1. Calculate position size based on risk management
        # 2. Place the actual order through the exchange
        # 3. Monitor order execution
        # 4. Update portfolio tracking
        
        # For this example, we just log the simulated action
        if signal.action == 'BUY':
            logger.info("✅ Simulated BUY order placed")
        elif signal.action == 'SELL':
            logger.info("❌ Simulated SELL order placed")
    
    def _analyze_signals(self, signals: list, historical_data: list):
        """Analyze the performance of generated signals"""
        if not signals:
            logger.info("No signals generated for analysis")
            return
        
        buy_signals = [s for s in signals if s.action == 'BUY']
        sell_signals = [s for s in signals if s.action == 'SELL']
        
        logger.info(f"Signal Analysis:")
        logger.info(f"  Total signals: {len(signals)}")
        logger.info(f"  Buy signals: {len(buy_signals)}")
        logger.info(f"  Sell signals: {len(sell_signals)}")
        
        if buy_signals:
            avg_buy_confidence = sum(s.confidence for s in buy_signals) / len(buy_signals)
            logger.info(f"  Average buy confidence: {avg_buy_confidence:.2f}")
        
        if sell_signals:
            avg_sell_confidence = sum(s.confidence for s in sell_signals) / len(sell_signals)
            logger.info(f"  Average sell confidence: {avg_sell_confidence:.2f}")
        
        # Calculate signal frequency
        time_span = (signals[-1].timestamp - signals[0].timestamp).total_seconds() / 3600  # hours
        signal_frequency = len(signals) / time_span if time_span > 0 else 0
        logger.info(f"  Signal frequency: {signal_frequency:.2f} signals/hour")
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources")
        
        if self.data_collector:
            await self.data_collector.stop_realtime_collection()
        
        if self.exchange_adapter:
            await self.exchange_adapter.disconnect()
        
        logger.info("Cleanup completed")

async def main():
    """Main function to run the example"""
    example = SimpleMovingAverageExample()
    
    try:
        # Setup the example
        await example.setup()
        
        # Run backtest example
        print("\n" + "="*50)
        print("RUNNING BACKTEST EXAMPLE")
        print("="*50)
        await example.run_backtest_example()
        
        # Run real-time example
        print("\n" + "="*50)
        print("RUNNING REAL-TIME EXAMPLE")
        print("="*50)
        await example.run_realtime_example()
        
    except Exception as e:
        logger.error(f"Example failed with error: {e}")
        raise
    finally:
        # Clean up
        await example.cleanup()

if __name__ == "__main__":
    print("Simple Moving Average Strategy Example")
    print("=====================================")
    print("This example demonstrates:")
    print("1. Setting up a moving average crossover strategy")
    print("2. Running backtests with historical data")
    print("3. Simulating real-time trading signals")
    print("4. Analyzing strategy performance")
    print("\nNote: This example uses sandbox/testnet mode for safety")
    print("="*50)
    
    # Run the example
    asyncio.run(main())