"""
Multi-Market Backtesting Example

This example demonstrates how to use the multi-market backtesting capabilities
to test trading strategies across both cryptocurrency and forex markets.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal

from src.backtesting.multi_market_backtest_engine import (
    MultiMarketBacktestEngine, MultiMarketBacktestConfig
)
from src.backtesting.multi_market_portfolio_simulator import MultiMarketPortfolioSimulator
from src.backtesting.multi_market_performance_analyzer import MultiMarketPerformanceAnalyzer
from src.backtesting.multi_market_report_generator import MultiMarketReportGenerator
from src.markets.types import MarketType, UnifiedSymbol
from src.models.data_models import TradingSignal, SignalAction
from src.strategies.base_strategy import BaseStrategy
from src.strategies.strategy_config import StrategyConfig


class SimpleMultiMarketStrategy(BaseStrategy):
    """
    Simple multi-market strategy for demonstration.
    
    This strategy implements a basic momentum approach that works
    across both crypto and forex markets.
    """
    
    def __init__(self):
        config = StrategyConfig(name="SimpleMultiMarketStrategy")
        super().__init__(config)
        self.price_history = {}
        self.lookback_period = 5
    
    def initialize(self):
        """Initialize the strategy."""
        print(f"Initializing {self.name}")
    
    def get_required_data_length(self):
        """Return required data length."""
        return self.lookback_period
    
    def analyze(self, market_data):
        """
        Analyze market data and generate trading signals.
        
        Simple momentum strategy:
        - Buy if price is above 5-period moving average
        - Sell if price is below 5-period moving average
        """
        if not market_data:
            return None
        
        current_data = market_data[0]
        symbol = current_data.symbol
        current_price = float(current_data.close)
        
        # Store price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(current_price)
        
        # Keep only recent prices
        if len(self.price_history[symbol]) > self.lookback_period:
            self.price_history[symbol] = self.price_history[symbol][-self.lookback_period:]
        
        # Need enough history to calculate moving average
        if len(self.price_history[symbol]) < self.lookback_period:
            return None
        
        # Calculate moving average
        moving_average = np.mean(self.price_history[symbol])
        
        # Generate signals based on momentum
        if current_price > moving_average * 1.02:  # 2% above MA
            return TradingSignal(
                symbol=symbol,
                action=SignalAction.BUY,
                confidence=0.7,
                timestamp=current_data.timestamp,
                strategy_name=self.name,
                price=Decimal(str(current_price)),
                metadata={
                    'moving_average': moving_average,
                    'price_ratio': current_price / moving_average,
                    'market_type': current_data.market_type.value if hasattr(current_data, 'market_type') else 'unknown'
                }
            )
        elif current_price < moving_average * 0.98:  # 2% below MA
            return TradingSignal(
                symbol=symbol,
                action=SignalAction.SELL,
                confidence=0.7,
                timestamp=current_data.timestamp,
                strategy_name=self.name,
                price=Decimal(str(current_price)),
                metadata={
                    'moving_average': moving_average,
                    'price_ratio': current_price / moving_average,
                    'market_type': current_data.market_type.value if hasattr(current_data, 'market_type') else 'unknown'
                }
            )
        
        return None


def generate_sample_data(symbol: UnifiedSymbol, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Generate sample market data for backtesting.
    
    Args:
        symbol: Symbol to generate data for
        start_date: Start date for data
        end_date: End date for data
        
    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='H')  # Hourly data
    
    # Different base prices for different markets
    if symbol.market_type == MarketType.CRYPTO:
        if 'BTC' in symbol.base_asset:
            base_price = 50000
            volatility = 0.02
        else:  # ETH
            base_price = 3000
            volatility = 0.025
    else:  # FOREX
        if symbol.base_asset == 'EUR':
            base_price = 1.1000
            volatility = 0.005
        else:  # GBP
            base_price = 1.3000
            volatility = 0.006
    
    # Generate price series with trend and noise
    np.random.seed(42)  # For reproducible results
    
    # Create a trending price series
    trend = np.linspace(0, 0.1, len(dates))  # 10% upward trend over period
    noise = np.random.normal(0, volatility, len(dates))
    
    # Generate price movements
    price_changes = trend + noise
    prices = base_price * np.exp(np.cumsum(price_changes))
    
    # Generate OHLCV data
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # Add some intraday volatility
        high = price * (1 + abs(np.random.normal(0, volatility/2)))
        low = price * (1 - abs(np.random.normal(0, volatility/2)))
        open_price = prices[i-1] if i > 0 else price
        close_price = price
        
        # Ensure OHLC relationships are valid
        high = max(high, open_price, close_price)
        low = min(low, open_price, close_price)
        
        # Volume varies by market type
        if symbol.market_type == MarketType.CRYPTO:
            volume = np.random.uniform(100, 1000)
        else:
            volume = np.random.uniform(1000000, 10000000)
        
        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(data, index=dates)


def run_multi_market_backtest_example():
    """Run a comprehensive multi-market backtesting example."""
    
    print("=== Multi-Market Backtesting Example ===\n")
    
    # 1. Set up backtesting configuration
    print("1. Setting up backtesting configuration...")
    
    config = MultiMarketBacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 3, 31),  # 3 months of data
        initial_capital=100000.0,
        commission_rates={
            MarketType.CRYPTO: 0.001,  # 0.1% for crypto
            MarketType.FOREX: 0.0002   # 0.02% for forex
        },
        slippage_rates={
            MarketType.CRYPTO: 0.0005,  # 0.05% for crypto
            MarketType.FOREX: 0.0001    # 0.01% for forex
        },
        max_positions_per_market={
            MarketType.CRYPTO: 3,
            MarketType.FOREX: 5
        },
        respect_market_hours=False  # Disable for this example
    )
    
    print(f"   - Initial Capital: ${config.initial_capital:,.2f}")
    print(f"   - Period: {config.start_date.date()} to {config.end_date.date()}")
    print(f"   - Markets: {len(config.commission_rates)} market types")
    
    # 2. Create symbols for different markets
    print("\n2. Creating trading symbols...")
    
    symbols = [
        UnifiedSymbol.from_crypto_symbol("BTCUSDT"),
        UnifiedSymbol.from_crypto_symbol("ETHUSDT"),
        UnifiedSymbol.from_forex_symbol("EURUSD"),
        UnifiedSymbol.from_forex_symbol("GBPUSD")
    ]
    
    for symbol in symbols:
        print(f"   - {symbol} ({symbol.market_type.value})")
    
    # 3. Generate sample market data
    print("\n3. Generating sample market data...")
    
    engine = MultiMarketBacktestEngine(config)
    
    for symbol in symbols:
        print(f"   - Generating data for {symbol}...")
        data = generate_sample_data(symbol, config.start_date, config.end_date)
        engine.load_market_data(symbol, data)
        print(f"     Generated {len(data)} data points")
    
    # 4. Create and initialize strategy
    print("\n4. Initializing trading strategy...")
    
    strategy = SimpleMultiMarketStrategy()
    strategy.initialize()
    
    # 5. Run backtest
    print("\n5. Running multi-market backtest...")
    print("   This may take a moment...")
    
    result = engine.run_backtest(strategy, symbols)
    
    print(f"   - Backtest completed!")
    print(f"   - Total trades executed: {result.total_trades}")
    print(f"   - Markets traded: {len(set(trade['market_type'] for trade in result.trade_history))}")
    
    # 6. Analyze performance
    print("\n6. Analyzing performance...")
    
    analyzer = MultiMarketPerformanceAnalyzer()
    analysis = analyzer.analyze_multi_market_performance(result)
    
    # Display basic results
    basic_metrics = analysis.get('basic_metrics', {})
    print(f"   - Total Return: {basic_metrics.get('total_return', 0):.2%}")
    print(f"   - Sharpe Ratio: {basic_metrics.get('sharpe_ratio', 0):.2f}")
    print(f"   - Max Drawdown: {basic_metrics.get('max_drawdown', 0):.2%}")
    print(f"   - Win Rate: {basic_metrics.get('win_rate', 0):.2%}")
    
    # Display market-specific performance
    if 'market_performance' in analysis:
        print("\n   Market-Specific Performance:")
        for market_type, metrics in analysis['market_performance'].items():
            if hasattr(metrics, 'total_trades'):
                print(f"   - {market_type.value.upper()}:")
                print(f"     * Trades: {metrics.total_trades}")
                print(f"     * Win Rate: {metrics.win_rate:.2%}")
                print(f"     * Total Return: {metrics.total_return:.2%}")
    
    # 7. Generate comprehensive report
    print("\n7. Generating comprehensive report...")
    
    report_generator = MultiMarketReportGenerator("backtest_reports")
    generated_files = report_generator.generate_full_report(
        result, 
        save_charts=True, 
        save_html=True
    )
    
    print("   Generated files:")
    for file_type, file_path in generated_files.items():
        print(f"   - {file_type}: {file_path}")
    
    # 8. Display summary report
    print("\n8. Performance Summary:")
    print("=" * 50)
    
    summary_report = analyzer.generate_multi_market_report(analysis)
    print(summary_report)
    
    # 9. Portfolio allocation analysis
    print("\n9. Portfolio Analysis:")
    print("=" * 30)
    
    if not result.portfolio_history.empty:
        final_value = result.portfolio_history['total_value'].iloc[-1]
        initial_value = result.portfolio_history['total_value'].iloc[0]
        
        print(f"Initial Portfolio Value: ${initial_value:,.2f}")
        print(f"Final Portfolio Value: ${final_value:,.2f}")
        print(f"Absolute Return: ${final_value - initial_value:,.2f}")
        print(f"Percentage Return: {(final_value / initial_value - 1) * 100:.2f}%")
        
        # Show final allocation
        final_cash = result.portfolio_history['cash'].iloc[-1]
        final_positions = result.portfolio_history['positions_value'].iloc[-1]
        
        print(f"\nFinal Allocation:")
        print(f"Cash: ${final_cash:,.2f} ({final_cash/final_value*100:.1f}%)")
        print(f"Positions: ${final_positions:,.2f} ({final_positions/final_value*100:.1f}%)")
    
    print("\n=== Multi-Market Backtesting Example Complete ===")
    
    return result, analysis


def demonstrate_portfolio_simulator():
    """Demonstrate the multi-market portfolio simulator capabilities."""
    
    print("\n=== Multi-Market Portfolio Simulator Demo ===\n")
    
    # Create portfolio simulator
    simulator = MultiMarketPortfolioSimulator(
        initial_capital=Decimal("50000"),
        base_currency="USD"
    )
    
    print(f"Initial Capital: ${simulator.initial_capital}")
    print(f"Base Currency: {simulator.base_currency}")
    
    # Create test symbols and market data
    crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
    forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
    
    from src.models.data_models import UnifiedMarketData
    
    crypto_data = UnifiedMarketData(
        symbol=crypto_symbol,
        timestamp=datetime.now(),
        open=Decimal("50000"),
        high=Decimal("51000"),
        low=Decimal("49000"),
        close=Decimal("50500"),
        volume=Decimal("100"),
        source="demo",
        market_type=MarketType.CRYPTO
    )
    
    forex_data = UnifiedMarketData(
        symbol=forex_symbol,
        timestamp=datetime.now(),
        open=Decimal("1.1000"),
        high=Decimal("1.1050"),
        low=Decimal("1.0950"),
        close=Decimal("1.1025"),
        volume=Decimal("1000000"),
        source="demo",
        market_type=MarketType.FOREX
    )
    
    # Create and execute orders
    from src.models.data_models import MarketSpecificOrder, OrderSide, OrderType, OrderStatus
    
    crypto_order = MarketSpecificOrder(
        id="demo_crypto_buy",
        symbol=crypto_symbol,
        side=OrderSide.BUY,
        amount=Decimal("0.5"),
        price=Decimal("50000"),
        order_type=OrderType.MARKET,
        status=OrderStatus.FILLED,
        timestamp=datetime.now(),
        source="demo",
        market_type=MarketType.CRYPTO
    )
    
    forex_order = MarketSpecificOrder(
        id="demo_forex_buy",
        symbol=forex_symbol,
        side=OrderSide.BUY,
        amount=Decimal("10000"),
        price=Decimal("1.1000"),
        order_type=OrderType.MARKET,
        status=OrderStatus.FILLED,
        timestamp=datetime.now(),
        source="demo",
        market_type=MarketType.FOREX
    )
    
    print("\nExecuting orders...")
    
    # Execute crypto order
    crypto_success = simulator.execute_order(crypto_order, crypto_data)
    print(f"Crypto order executed: {crypto_success}")
    
    # Execute forex order
    forex_success = simulator.execute_order(forex_order, forex_data)
    print(f"Forex order executed: {forex_success}")
    
    # Show portfolio status
    print(f"\nPortfolio Status:")
    print(f"Cash: ${simulator.cash}")
    print(f"Total Value: ${simulator.get_portfolio_value()}")
    print(f"Positions: {len(simulator.positions)}")
    
    # Show market allocation
    allocation = simulator.get_market_allocation()
    print(f"\nMarket Allocation:")
    for market_type, percentage in allocation.items():
        print(f"  {market_type.value}: {percentage:.1f}%")
    
    # Show currency allocation
    currency_allocation = simulator.get_currency_allocation()
    print(f"\nCurrency Allocation:")
    for currency, percentage in currency_allocation.items():
        print(f"  {currency}: {percentage:.1f}%")
    
    print("\n=== Portfolio Simulator Demo Complete ===")


if __name__ == "__main__":
    # Run the main multi-market backtesting example
    result, analysis = run_multi_market_backtest_example()
    
    # Demonstrate portfolio simulator
    demonstrate_portfolio_simulator()
    
    print(f"\nExample completed successfully!")
    print(f"Check the 'backtest_reports' directory for detailed reports and charts.")