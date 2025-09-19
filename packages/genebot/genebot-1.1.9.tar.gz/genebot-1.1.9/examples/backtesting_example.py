"""
Example demonstrating the backtesting engine functionality.

This example shows how to:
1. Set up a backtesting environment
2. Load historical market data
3. Create and run a backtest with a simple strategy
4. Generate performance reports and visualizations
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.backtesting.backtest_engine import BacktestEngine, BacktestConfig
from src.backtesting.report_generator import ReportGenerator
from src.models.data_models import MarketData, TradingSignal
from src.strategies.base_strategy import BaseStrategy


class SimpleMovingAverageStrategy(BaseStrategy):
    """
    Simple moving average crossover strategy for backtesting demonstration.
    
    Generates buy signals when short MA crosses above long MA,
    and sell signals when short MA crosses below long MA.
    """
    
    def __init__(self, short_window=10, long_window=30):
        from src.strategies.base_strategy import StrategyConfig
        config = StrategyConfig(
            name="SimpleMA",
            parameters={
                'short_window': short_window,
                'long_window': long_window
            }
        )
        super().__init__(config)
        self.short_window = short_window
        self.long_window = long_window
        self.price_history = {}
        
    def initialize(self):
        """Initialize the strategy."""
        return True
        
    def get_required_data_length(self):
        """Get required data length."""
        return max(self.short_window, self.long_window)
        
    def validate_parameters(self):
        """Validate strategy parameters."""
        return self.short_window > 0 and self.long_window > self.short_window
        
    def analyze(self, market_data):
        """Analyze market data and generate signals."""
        # For backtesting compatibility, we'll implement generate_signals
        # and call it from analyze
        if hasattr(self, '_current_market_data'):
            signals = self.generate_signals(self._current_market_data)
            return signals[0] if signals else None
        return None
        
    def generate_signals(self, market_data):
        """Generate trading signals based on moving average crossover."""
        signals = []
        
        for symbol, data in market_data.items():
            # Store price history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
                
            self.price_history[symbol].append(data.close)
            
            # Keep only necessary history
            max_window = max(self.short_window, self.long_window)
            if len(self.price_history[symbol]) > max_window + 10:
                self.price_history[symbol] = self.price_history[symbol][-max_window-5:]
                
            prices = self.price_history[symbol]
            
            # Need enough data for both moving averages
            if len(prices) < self.long_window:
                continue
                
            # Calculate moving averages
            short_ma = np.mean(prices[-self.short_window:])
            long_ma = np.mean(prices[-self.long_window:])
            
            # Previous moving averages for crossover detection
            if len(prices) >= self.long_window + 1:
                prev_short_ma = np.mean(prices[-self.short_window-1:-1])
                prev_long_ma = np.mean(prices[-self.long_window-1:-1])
                
                # Detect crossovers
                if prev_short_ma <= prev_long_ma and short_ma > long_ma:
                    # Golden cross - buy signal
                    signals.append(TradingSignal(
                        symbol=symbol,
                        action='BUY',
                        confidence=0.8,
                        timestamp=data.timestamp,
                        strategy_name=self.name,
                        metadata={
                            'short_ma': short_ma,
                            'long_ma': long_ma,
                            'signal_type': 'golden_cross'
                        }
                    ))
                    
                elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
                    # Death cross - sell signal
                    signals.append(TradingSignal(
                        symbol=symbol,
                        action='SELL',
                        confidence=0.8,
                        timestamp=data.timestamp,
                        strategy_name=self.name,
                        metadata={
                            'short_ma': short_ma,
                            'long_ma': long_ma,
                            'signal_type': 'death_cross'
                        }
                    ))
                    
        return signals


def generate_sample_market_data(symbol, start_date, end_date, initial_price=100.0):
    """
    Generate realistic sample market data for backtesting.
    
    Args:
        symbol: Trading symbol
        start_date: Start date for data
        end_date: End date for data
        initial_price: Starting price
        
    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    data = []
    current_price = initial_price
    
    for date in dates:
        # Generate price movement with trend and volatility
        # Add slight upward trend with random walk
        trend = 0.0002  # 0.02% daily trend
        volatility = 0.02  # 2% daily volatility
        
        price_change = np.random.normal(trend, volatility)
        current_price *= (1 + price_change)
        
        # Generate OHLC from close price
        daily_range = abs(np.random.normal(0, 0.01))  # Daily range
        high = current_price * (1 + daily_range)
        low = current_price * (1 - daily_range)
        open_price = current_price * (1 + np.random.normal(0, 0.005))
        
        # Ensure OHLC relationships are valid
        high = max(high, open_price, current_price)
        low = min(low, open_price, current_price)
        
        # Generate volume
        volume = np.random.uniform(10000, 100000)
        
        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': current_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data, index=dates)
    return df


def run_backtest_example():
    """Run a complete backtesting example."""
    print("=== Backtesting Engine Example ===\n")
    
    # 1. Set up backtesting configuration
    print("1. Setting up backtest configuration...")
    config = BacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31),
        initial_capital=100000.0,  # $100,000 starting capital
        commission_rate=0.001,     # 0.1% commission
        slippage_rate=0.0005,      # 0.05% slippage
        max_positions=5            # Max 5 concurrent positions
    )
    
    print(f"  Start Date: {config.start_date.strftime('%Y-%m-%d')}")
    print(f"  End Date: {config.end_date.strftime('%Y-%m-%d')}")
    print(f"  Initial Capital: ${config.initial_capital:,.2f}")
    print(f"  Commission Rate: {config.commission_rate:.3f}%")
    print(f"  Slippage Rate: {config.slippage_rate:.4f}%\n")
    
    # 2. Generate sample market data
    print("2. Generating sample market data...")
    symbols = ['BTCUSD', 'ETHUSD', 'ADAUSD']
    market_data = {}
    
    for symbol in symbols:
        # Generate data with different starting prices
        initial_prices = {'BTCUSD': 30000, 'ETHUSD': 2000, 'ADAUSD': 0.5}
        data = generate_sample_market_data(
            symbol, 
            config.start_date, 
            config.end_date,
            initial_prices[symbol]
        )
        market_data[symbol] = data
        print(f"  Generated {len(data)} data points for {symbol}")
    
    print()
    
    # 3. Initialize backtest engine and load data
    print("3. Initializing backtest engine...")
    engine = BacktestEngine(config)
    
    for symbol, data in market_data.items():
        engine.load_market_data(symbol, data)
    
    print(f"  Loaded market data for {len(symbols)} symbols\n")
    
    # 4. Create and run strategy
    print("4. Running backtest with Simple Moving Average strategy...")
    strategy = SimpleMovingAverageStrategy(short_window=10, long_window=30)
    
    # Run the backtest
    result = engine.run_backtest(strategy, symbols)
    
    print(f"  Backtest completed for {result.strategy_name}")
    print(f"  Total trades executed: {result.total_trades}")
    print(f"  Total return: {result.total_return:.2%}")
    print(f"  Sharpe ratio: {result.sharpe_ratio:.2f}")
    print(f"  Max drawdown: {result.max_drawdown:.2%}\n")
    
    # 5. Display detailed performance metrics
    print("5. Performance Analysis:")
    print("=" * 50)
    
    metrics = result.performance_metrics
    
    print(f"RETURN METRICS:")
    print(f"  Total Return: {metrics.get('total_return', 0):.2%}")
    print(f"  Annualized Return: {metrics.get('annualized_return', 0):.2%}")
    print(f"  Initial Value: ${metrics.get('initial_value', 0):,.2f}")
    print(f"  Final Value: ${metrics.get('final_value', 0):,.2f}")
    print()
    
    print(f"RISK METRICS:")
    print(f"  Volatility: {metrics.get('volatility', 0):.2%}")
    print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"  Sortino Ratio: {metrics.get('sortino_ratio', 0):.2f}")
    print(f"  Max Drawdown: {metrics.get('max_drawdown', 0):.2%}")
    print(f"  Current Drawdown: {metrics.get('current_drawdown', 0):.2%}")
    print()
    
    if result.trade_history:
        print(f"TRADE STATISTICS:")
        print(f"  Total Trades: {metrics.get('total_trades', 0)}")
        print(f"  Winning Trades: {metrics.get('winning_trades', 0)}")
        print(f"  Losing Trades: {metrics.get('losing_trades', 0)}")
        print(f"  Win Rate: {metrics.get('win_rate', 0):.2%}")
        print(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        print(f"  Average Win: ${metrics.get('avg_win', 0):.2f}")
        print(f"  Average Loss: ${metrics.get('avg_loss', 0):.2f}")
        print(f"  Largest Win: ${metrics.get('largest_win', 0):.2f}")
        print(f"  Largest Loss: ${metrics.get('largest_loss', 0):.2f}")
        print()
    
    # 6. Generate comprehensive report
    print("6. Generating comprehensive report...")
    
    # Create reports directory
    reports_dir = "backtest_reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    report_generator = ReportGenerator(output_dir=reports_dir)
    
    try:
        # Generate full report with charts and HTML
        generated_files = report_generator.generate_full_report(
            result,
            save_charts=True,
            save_html=True
        )
        
        print("  Report generation completed!")
        print("  Generated files:")
        for file_type, filepath in generated_files.items():
            print(f"    {file_type}: {filepath}")
            
    except ImportError as e:
        print(f"  Warning: Could not generate charts due to missing dependencies: {e}")
        print("  Install matplotlib and seaborn for full report generation")
        
        # Generate report without charts
        generated_files = report_generator.generate_full_report(
            result,
            save_charts=False,
            save_html=True
        )
        
        print("  Generated files (without charts):")
        for file_type, filepath in generated_files.items():
            print(f"    {file_type}: {filepath}")
    
    print()
    
    # 7. Show sample trades
    if result.trade_history:
        print("7. Sample Trade History:")
        print("=" * 80)
        print(f"{'Symbol':<10} {'Side':<5} {'Entry':<10} {'Exit':<10} {'Size':<8} {'P&L':<10} {'Date'}")
        print("-" * 80)
        
        for i, trade in enumerate(result.trade_history[:10]):  # Show first 10 trades
            print(f"{trade['symbol']:<10} {trade['side']:<5} "
                  f"{trade['entry_price']:<10.2f} {trade['exit_price']:<10.2f} "
                  f"{trade['size']:<8.2f} {trade['net_pnl']:<10.2f} "
                  f"{trade['exit_timestamp'].strftime('%Y-%m-%d')}")
        
        if len(result.trade_history) > 10:
            print(f"... and {len(result.trade_history) - 10} more trades")
    
    print("\n=== Backtesting Example Completed ===")
    return result


def compare_strategies_example():
    """Example of comparing multiple strategies."""
    print("\n=== Strategy Comparison Example ===\n")
    
    # Configuration
    config = BacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 6, 30),
        initial_capital=50000.0,
        commission_rate=0.001,
        slippage_rate=0.0005
    )
    
    # Generate market data
    symbol = 'BTCUSD'
    market_data = generate_sample_market_data(symbol, config.start_date, config.end_date, 35000)
    
    # Test different MA strategies
    strategies = [
        SimpleMovingAverageStrategy(short_window=5, long_window=20),
        SimpleMovingAverageStrategy(short_window=10, long_window=30),
        SimpleMovingAverageStrategy(short_window=20, long_window=50)
    ]
    
    results = []
    
    for strategy in strategies:
        engine = BacktestEngine(config)
        engine.load_market_data(symbol, market_data)
        
        result = engine.run_backtest(strategy, [symbol])
        results.append(result)
        
        print(f"Strategy: MA({strategy.short_window},{strategy.long_window})")
        print(f"  Total Return: {result.total_return:.2%}")
        print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"  Max Drawdown: {result.max_drawdown:.2%}")
        print(f"  Total Trades: {result.total_trades}")
        print()
    
    # Find best strategy
    best_strategy = max(results, key=lambda x: x.sharpe_ratio)
    print(f"Best Strategy (by Sharpe Ratio): {best_strategy.strategy_name}")
    print(f"  Sharpe Ratio: {best_strategy.sharpe_ratio:.2f}")
    print(f"  Total Return: {best_strategy.total_return:.2%}")


if __name__ == "__main__":
    # Run the main backtesting example
    result = run_backtest_example()
    
    # Run strategy comparison
    compare_strategies_example()
    
    print("\nExample completed successfully!")
    print("Check the 'backtest_reports' directory for generated reports and charts.")