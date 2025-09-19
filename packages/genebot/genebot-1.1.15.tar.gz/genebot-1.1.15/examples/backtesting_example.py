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
import logging
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up logger
logger = logging.getLogger(__name__)

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


def load_historical_market_data(symbol, start_date, end_date):
    """
    Load historical market data from a real data source.
    
    Args:
        symbol: Trading symbol
        start_date: Start date for data
        end_date: End date for data
        
    Returns:
        DataFrame with OHLCV data
    """
    import pandas as pd
    from datetime import datetime, timedelta
    import os
    
    # Try multiple data sources in order of preference
    
    # Option 1: Try Yahoo Finance first (most reliable for stocks)
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        if not data.empty:
            data = data.reset_index()
            data.columns = [col.lower() for col in data.columns]
            return data
    except ImportError:
        logger.warning("yfinance not available, trying alternative data sources")
    except Exception as e:
        logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
    
    # Option 2: Try CCXT for crypto symbols
    try:
        import ccxt
        # Detect if it's a crypto symbol
        if '/' in symbol or symbol.upper() in ['BTC', 'ETH', 'ADA', 'DOT', 'USDT']:
            exchange = ccxt.binance()
            # Convert dates to timestamps
            start_ts = int(datetime.strptime(str(start_date), '%Y-%m-%d').timestamp() * 1000)
            ohlcv = exchange.fetch_ohlcv(symbol, '1d', since=start_ts)
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
    except ImportError:
        logger.warning("ccxt not available for crypto data")
    except Exception as e:
        logger.warning(f"CCXT failed for {symbol}: {e}")
    
    # Option 3: Try CSV file from historical_data directory
    try:
        csv_path = f'historical_data/{symbol}.csv'
        if os.path.exists(csv_path):
            data = pd.read_csv(csv_path)
            data['date'] = pd.to_datetime(data['date'])
            # Filter by date range
            mask = (data['date'] >= pd.to_datetime(start_date)) & (data['date'] <= pd.to_datetime(end_date))
            return data.loc[mask]
    except Exception as e:
        logger.warning(f"CSV file loading failed for {symbol}: {e}")
    
    # Option 4: Generate synthetic data as fallback
    logger.warning(f"No real data source available for {symbol}, generating synthetic data")
    try:
        # Try to import standalone utility
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
        from synthetic_data_generator import generate_synthetic_market_data
        return generate_synthetic_market_data(symbol, start_date, end_date)
    except ImportError:
        # Fallback to inline implementation
        return _generate_synthetic_data_inline(symbol, start_date, end_date)


def _generate_synthetic_data_inline(symbol, start_date, end_date):
    """Inline synthetic market data generation for testing purposes"""
    import pandas as pd
    import numpy as np
    
    # Create date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate realistic price data with random walk
    np.random.seed(42)  # For reproducible results
    initial_price = 100.0
    returns = np.random.normal(0.001, 0.02, len(dates))  # 0.1% daily return, 2% volatility
    
    prices = [initial_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Generate OHLCV data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # Generate realistic OHLC from close price
        volatility = abs(np.random.normal(0, 0.01))
        high = close * (1 + volatility)
        low = close * (1 - volatility)
        open_price = prices[i-1] if i > 0 else close
        volume = np.random.randint(1000000, 10000000)
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    return pd.DataFrame(data)


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
        # Load historical data from real source
        data = load_historical_market_data(
            symbol, 
            config.start_date, 
            config.end_date
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
    market_data = load_historical_market_data(symbol, config.start_date, config.end_date)
    
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