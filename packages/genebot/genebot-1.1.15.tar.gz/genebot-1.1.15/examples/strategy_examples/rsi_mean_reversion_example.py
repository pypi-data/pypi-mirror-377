#!/usr/bin/env python3
"""
RSI Mean Reversion Strategy Example

This example demonstrates how to implement and use an RSI-based mean reversion strategy.
The strategy generates buy signals when RSI is oversold (below 30) and sell signals
when RSI is overbought (above 70).
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.strategies.rsi_strategy import RSIStrategy
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

class RSIMeanReversionExample:
    """Example implementation of RSI mean reversion strategy"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.strategy_engine = StrategyEngine()
        self.data_collector = None
        self.exchange_adapter = None
        self.positions = {}  # Track simulated positions
        
    async def setup(self):
        """Initialize the example components"""
        logger.info("Setting up RSI Mean Reversion Strategy Example")
        
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
        
        # Configure RSI strategy with different parameters for demonstration
        strategy_configs = {
            'conservative_rsi': {
                'rsi_period': 14,
                'oversold_threshold': 25,    # More conservative (lower threshold)
                'overbought_threshold': 75,  # More conservative (higher threshold)
                'confidence_multiplier': 1.2,
                'symbols': ['BTC/USDT'],
                'timeframe': '1h'
            },
            'aggressive_rsi': {
                'rsi_period': 14,
                'oversold_threshold': 35,    # More aggressive (higher threshold)
                'overbought_threshold': 65,  # More aggressive (lower threshold)
                'confidence_multiplier': 0.8,
                'symbols': ['ETH/USDT'],
                'timeframe': '1h'
            },
            'short_term_rsi': {
                'rsi_period': 7,             # Shorter period for faster signals
                'oversold_threshold': 20,
                'overbought_threshold': 80,
                'confidence_multiplier': 1.0,
                'symbols': ['ADA/USDT'],
                'timeframe': '15m'
            }
        }
        
        # Create and register strategies
        for name, config in strategy_configs.items():
            strategy = RSIStrategy(config)
            self.strategy_engine.register_strategy(name, strategy)
            logger.info(f"Registered strategy: {name}")
        
        logger.info("Setup completed successfully")
    
    async def run_parameter_comparison(self):
        """Compare different RSI parameters on the same data"""
        logger.info("Running RSI parameter comparison")
        
        symbol = 'BTC/USDT'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Last 7 days
        
        # Get historical data
        historical_data = await self.data_collector.get_historical_data(
            symbol=symbol,
            timeframe='1h',
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        logger.info(f"Retrieved {len(historical_data)} historical data points")
        
        # Test different RSI configurations
        results = {}
        
        for strategy_name in ['conservative_rsi', 'aggressive_rsi']:
            strategy = self.strategy_engine.get_strategy(strategy_name)
            signals = []
            
            logger.info(f"\nTesting {strategy_name} strategy:")
            
            for data_point in historical_data:
                signal = await strategy.analyze(data_point)
                if signal.action != 'HOLD':
                    signals.append(signal)
                    logger.info(f"  {signal.action} at {signal.timestamp.strftime('%Y-%m-%d %H:%M')} "
                              f"(RSI: {signal.metadata.get('rsi', 'N/A'):.1f}, "
                              f"confidence: {signal.confidence:.2f})")
            
            results[strategy_name] = signals
            logger.info(f"  Total signals: {len(signals)}")
        
        # Compare results
        self._compare_strategy_results(results)
    
    async def run_multi_timeframe_analysis(self):
        """Analyze RSI signals across multiple timeframes"""
        logger.info("Running multi-timeframe RSI analysis")
        
        symbol = 'ETH/USDT'
        timeframes = ['15m', '1h', '4h']
        
        # Configure strategy for different timeframes
        for timeframe in timeframes:
            config = {
                'rsi_period': 14,
                'oversold_threshold': 30,
                'overbought_threshold': 70,
                'symbols': [symbol],
                'timeframe': timeframe
            }
            
            strategy_name = f'rsi_{timeframe}'
            strategy = RSIStrategy(config)
            self.strategy_engine.register_strategy(strategy_name, strategy)
        
        # Get data for each timeframe
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3)  # Last 3 days
        
        timeframe_results = {}
        
        for timeframe in timeframes:
            logger.info(f"\nAnalyzing {timeframe} timeframe:")
            
            historical_data = await self.data_collector.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            strategy = self.strategy_engine.get_strategy(f'rsi_{timeframe}')
            signals = []
            
            for data_point in historical_data:
                signal = await strategy.analyze(data_point)
                if signal.action != 'HOLD':
                    signals.append(signal)
                    logger.info(f"  {signal.action} at {signal.timestamp.strftime('%Y-%m-%d %H:%M')} "
                              f"(RSI: {signal.metadata.get('rsi', 'N/A'):.1f})")
            
            timeframe_results[timeframe] = signals
            logger.info(f"  Signals for {timeframe}: {len(signals)}")
        
        # Analyze timeframe correlation
        self._analyze_timeframe_correlation(timeframe_results)
    
    async def run_live_rsi_monitoring(self):
        """Monitor RSI levels in real-time"""
        logger.info("Starting live RSI monitoring")
        
        symbols = ['BTC/USDT', 'ETH/USDT']
        
        # Start real-time data collection
        await self.data_collector.start_realtime_collection(symbols)
        
        # Get strategy instance
        strategy = self.strategy_engine.get_strategy('conservative_rsi')
        
        try:
            # Monitor for 3 minutes as an example
            end_time = datetime.now() + timedelta(minutes=3)
            
            while datetime.now() < end_time:
                for symbol in symbols:
                    # Get latest market data
                    latest_data = await self.data_collector.get_latest_data(symbol)
                    
                    if latest_data:
                        # Generate trading signal
                        signal = await strategy.analyze(latest_data)
                        
                        # Always log RSI level for monitoring
                        rsi_value = signal.metadata.get('rsi', 'N/A')
                        logger.info(f"{symbol} - Price: {latest_data.close:.2f}, "
                                  f"RSI: {rsi_value:.1f if rsi_value != 'N/A' else 'N/A'}")
                        
                        if signal.action != 'HOLD':
                            logger.info(f"🚨 SIGNAL: {signal.action} {signal.symbol} "
                                      f"(RSI: {rsi_value:.1f}, confidence: {signal.confidence:.2f})")
                            
                            # Simulate trade execution
                            await self._simulate_mean_reversion_trade(signal, latest_data)
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
        finally:
            # Stop data collection
            await self.data_collector.stop_realtime_collection()
            logger.info("Live RSI monitoring completed")
    
    async def _simulate_mean_reversion_trade(self, signal: TradingSignal, market_data: MarketData):
        """Simulate mean reversion trade execution with position tracking"""
        symbol = signal.symbol
        current_price = market_data.close
        
        if signal.action == 'BUY' and symbol not in self.positions:
            # Enter long position (expecting price to revert upward)
            position_size = 1000 / current_price  # $1000 position
            self.positions[symbol] = {
                'side': 'long',
                'size': position_size,
                'entry_price': current_price,
                'entry_time': signal.timestamp,
                'entry_rsi': signal.metadata.get('rsi', 0)
            }
            
            logger.info(f"📈 ENTERED LONG: {symbol} at ${current_price:.2f} "
                      f"(RSI: {signal.metadata.get('rsi', 0):.1f}) - Size: {position_size:.4f}")
            
        elif signal.action == 'SELL' and symbol not in self.positions:
            # Enter short position (expecting price to revert downward)
            position_size = 1000 / current_price  # $1000 position
            self.positions[symbol] = {
                'side': 'short',
                'size': position_size,
                'entry_price': current_price,
                'entry_time': signal.timestamp,
                'entry_rsi': signal.metadata.get('rsi', 0)
            }
            
            logger.info(f"📉 ENTERED SHORT: {symbol} at ${current_price:.2f} "
                      f"(RSI: {signal.metadata.get('rsi', 0):.1f}) - Size: {position_size:.4f}")
            
        elif symbol in self.positions:
            # Check if we should close the position (mean reversion occurred)
            position = self.positions[symbol]
            
            should_close = False
            if position['side'] == 'long' and signal.action == 'SELL':
                should_close = True
            elif position['side'] == 'short' and signal.action == 'BUY':
                should_close = True
            
            if should_close:
                # Calculate P&L
                if position['side'] == 'long':
                    pnl = (current_price - position['entry_price']) * position['size']
                else:  # short
                    pnl = (position['entry_price'] - current_price) * position['size']
                
                pnl_percent = (pnl / 1000) * 100  # Percentage of initial $1000
                
                logger.info(f"🔄 CLOSED {position['side'].upper()}: {symbol} at ${current_price:.2f} "
                          f"(Entry: ${position['entry_price']:.2f}, "
                          f"RSI: {signal.metadata.get('rsi', 0):.1f}) - "
                          f"P&L: ${pnl:.2f} ({pnl_percent:+.1f}%)")
                
                # Remove position
                del self.positions[symbol]
    
    def _compare_strategy_results(self, results: Dict[str, List[TradingSignal]]):
        """Compare results from different strategy configurations"""
        logger.info("\n" + "="*50)
        logger.info("STRATEGY COMPARISON RESULTS")
        logger.info("="*50)
        
        for strategy_name, signals in results.items():
            logger.info(f"\n{strategy_name.upper()}:")
            
            if not signals:
                logger.info("  No signals generated")
                continue
            
            buy_signals = [s for s in signals if s.action == 'BUY']
            sell_signals = [s for s in signals if s.action == 'SELL']
            
            logger.info(f"  Total signals: {len(signals)}")
            logger.info(f"  Buy signals: {len(buy_signals)}")
            logger.info(f"  Sell signals: {len(sell_signals)}")
            
            if buy_signals:
                avg_buy_rsi = sum(s.metadata.get('rsi', 0) for s in buy_signals) / len(buy_signals)
                avg_buy_confidence = sum(s.confidence for s in buy_signals) / len(buy_signals)
                logger.info(f"  Avg buy RSI: {avg_buy_rsi:.1f}")
                logger.info(f"  Avg buy confidence: {avg_buy_confidence:.2f}")
            
            if sell_signals:
                avg_sell_rsi = sum(s.metadata.get('rsi', 0) for s in sell_signals) / len(sell_signals)
                avg_sell_confidence = sum(s.confidence for s in sell_signals) / len(sell_signals)
                logger.info(f"  Avg sell RSI: {avg_sell_rsi:.1f}")
                logger.info(f"  Avg sell confidence: {avg_sell_confidence:.2f}")
    
    def _analyze_timeframe_correlation(self, timeframe_results: Dict[str, List[TradingSignal]]):
        """Analyze correlation between different timeframe signals"""
        logger.info("\n" + "="*50)
        logger.info("TIMEFRAME CORRELATION ANALYSIS")
        logger.info("="*50)
        
        for timeframe, signals in timeframe_results.items():
            logger.info(f"\n{timeframe.upper()} TIMEFRAME:")
            logger.info(f"  Signal count: {len(signals)}")
            
            if signals:
                # Calculate signal distribution
                buy_count = len([s for s in signals if s.action == 'BUY'])
                sell_count = len([s for s in signals if s.action == 'SELL'])
                
                logger.info(f"  Buy/Sell ratio: {buy_count}/{sell_count}")
                
                # Calculate average time between signals
                if len(signals) > 1:
                    time_diffs = []
                    for i in range(1, len(signals)):
                        diff = (signals[i].timestamp - signals[i-1].timestamp).total_seconds() / 3600
                        time_diffs.append(diff)
                    
                    avg_time_between = sum(time_diffs) / len(time_diffs)
                    logger.info(f"  Avg time between signals: {avg_time_between:.1f} hours")
        
        # Look for signal alignment across timeframes
        logger.info("\nSIGNAL ALIGNMENT:")
        logger.info("Looking for signals that occur within 1 hour across timeframes...")
        
        # This is a simplified alignment check
        all_signals = []
        for timeframe, signals in timeframe_results.items():
            for signal in signals:
                all_signals.append((timeframe, signal))
        
        # Sort by timestamp
        all_signals.sort(key=lambda x: x[1].timestamp)
        
        aligned_signals = 0
        for i in range(len(all_signals) - 1):
            current_tf, current_signal = all_signals[i]
            next_tf, next_signal = all_signals[i + 1]
            
            time_diff = (next_signal.timestamp - current_signal.timestamp).total_seconds() / 3600
            
            if (time_diff <= 1.0 and 
                current_signal.action == next_signal.action and 
                current_tf != next_tf):
                aligned_signals += 1
                logger.info(f"  Aligned: {current_signal.action} signal in {current_tf} and {next_tf} "
                          f"({time_diff:.1f}h apart)")
        
        logger.info(f"Total aligned signals: {aligned_signals}")
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources")
        
        if self.data_collector:
            await self.data_collector.stop_realtime_collection()
        
        if self.exchange_adapter:
            await self.exchange_adapter.disconnect()
        
        # Log final positions
        if self.positions:
            logger.info("Open positions at cleanup:")
            for symbol, position in self.positions.items():
                logger.info(f"  {symbol}: {position['side']} at ${position['entry_price']:.2f}")
        
        logger.info("Cleanup completed")

async def main():
    """Main function to run the example"""
    example = RSIMeanReversionExample()
    
    try:
        # Setup the example
        await example.setup()
        
        # Run parameter comparison
        print("\n" + "="*60)
        print("RUNNING RSI PARAMETER COMPARISON")
        print("="*60)
        await example.run_parameter_comparison()
        
        # Run multi-timeframe analysis
        print("\n" + "="*60)
        print("RUNNING MULTI-TIMEFRAME ANALYSIS")
        print("="*60)
        await example.run_multi_timeframe_analysis()
        
        # Run live monitoring
        print("\n" + "="*60)
        print("RUNNING LIVE RSI MONITORING")
        print("="*60)
        await example.run_live_rsi_monitoring()
        
    except Exception as e:
        logger.error(f"Example failed with error: {e}")
        raise
    finally:
        # Clean up
        await example.cleanup()

if __name__ == "__main__":
    print("RSI Mean Reversion Strategy Example")
    print("===================================")
    print("This example demonstrates:")
    print("1. RSI-based mean reversion strategy implementation")
    print("2. Comparing different RSI parameter configurations")
    print("3. Multi-timeframe RSI analysis")
    print("4. Real-time RSI monitoring and trade simulation")
    print("5. Position tracking for mean reversion trades")
    print("\nNote: This example uses sandbox/testnet mode for safety")
    print("="*60)
    
    # Run the example
    asyncio.run(main())