"""
Unit tests for backtesting components.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import tempfile
import os

from src.backtesting.backtest_engine import BacktestEngine, BacktestConfig, BacktestResult
from src.backtesting.portfolio_simulator import PortfolioSimulator, SimulatedPosition, SimulatedTrade
from src.backtesting.performance_analyzer import PerformanceAnalyzer
from src.backtesting.report_generator import ReportGenerator
from src.models.data_models import MarketData, TradingSignal, Order, Position
from src.strategies.base_strategy import BaseStrategy


class MockStrategy(BaseStrategy):
    """Mock strategy for testing."""
    
    def __init__(self, signals=None):
        from src.strategies.base_strategy import StrategyConfig
        config = StrategyConfig(name="MockStrategy", parameters={})
        super().__init__(config)
        self.signals = signals or []
        self.signal_index = 0
        
    def initialize(self):
        """Initialize the strategy."""
        pass
        
    def analyze(self, market_data):
        """Analyze market data."""
        return {}
        
    def get_required_data_length(self):
        """Get required data length."""
        return 1
        
    def validate_parameters(self):
        """Validate strategy parameters."""
        return True
        
    def generate_signals(self, market_data):
        """Generate predefined signals."""
        if self.signal_index < len(self.signals):
            signal = self.signals[self.signal_index]
            self.signal_index += 1
            return [signal]
        return []


@pytest.fixture
def sample_market_data():
    """Create sample market data for testing."""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)  # For reproducible tests
    
    # Generate realistic OHLCV data
    base_price = 100.0
    prices = []
    
    for i in range(len(dates)):
        # Random walk with slight upward trend
        change = np.random.normal(0.001, 0.02)  # 0.1% mean, 2% std
        base_price *= (1 + change)
        
        # Generate OHLC from close price
        high = base_price * (1 + abs(np.random.normal(0, 0.01)))
        low = base_price * (1 - abs(np.random.normal(0, 0.01)))
        open_price = base_price * (1 + np.random.normal(0, 0.005))
        volume = np.random.uniform(1000, 10000)
        
        prices.append({
            'open': open_price,
            'high': max(high, open_price, base_price),
            'low': min(low, open_price, base_price),
            'close': base_price,
            'volume': volume
        })
    
    df = pd.DataFrame(prices, index=dates)
    return df


@pytest.fixture
def backtest_config():
    """Create sample backtest configuration."""
    return BacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 3, 31),
        initial_capital=10000.0,
        commission_rate=0.001,
        slippage_rate=0.0005,
        max_positions=5
    )


class TestPortfolioSimulator:
    """Test cases for PortfolioSimulator."""
    
    def test_initialization(self):
        """Test portfolio simulator initialization."""
        simulator = PortfolioSimulator(
            initial_capital=10000.0,
            commission_rate=0.001,
            slippage_rate=0.0005,
            max_positions=10
        )
        
        assert simulator.initial_capital == 10000.0
        assert simulator.commission_rate == 0.001
        assert simulator.slippage_rate == 0.0005
        assert simulator.max_positions == 10
        assert simulator.cash == 10000.0
        assert len(simulator.positions) == 0
        
    def test_buy_order_execution(self):
        """Test buy order execution."""
        simulator = PortfolioSimulator(initial_capital=10000.0)
        
        market_data = MarketData(
            symbol='BTCUSD',
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0,
            exchange='test'
        )
        
        order = Order(
            id='test_buy_1',
            symbol='BTCUSD',
            side='buy',
            amount=10.0,  # Buy 10 units
            price=102.0,
            order_type='market',
            status='pending',
            timestamp=datetime.now(),
            exchange='test'
        )
        
        # Execute buy order
        result = simulator.execute_order(order, market_data)
        
        assert result is True
        assert 'BTCUSD' in simulator.positions
        assert simulator.positions['BTCUSD'].size == 10.0
        
        # Check cash reduction (price + slippage + commission)
        execution_price = 102.0 * (1 + 0.0005)  # With slippage
        position_value = 10.0 * execution_price
        commission = position_value * 0.001
        expected_cash = 10000.0 - position_value - commission
        
        assert abs(simulator.cash - expected_cash) < 0.01
        
    def test_sell_order_execution(self):
        """Test sell order execution."""
        simulator = PortfolioSimulator(initial_capital=10000.0)
        
        # First, create a position by buying
        market_data = MarketData(
            symbol='BTCUSD',
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=100.0,
            volume=1000.0,
            exchange='test'
        )
        
        buy_order = Order(
            id='test_buy_1',
            symbol='BTCUSD',
            side='buy',
            amount=10.0,
            price=100.0,
            order_type='market',
            status='pending',
            timestamp=datetime.now(),
            exchange='test'
        )
        
        simulator.execute_order(buy_order, market_data)
        initial_cash = simulator.cash
        
        # Now sell at a higher price
        market_data.close = 110.0
        sell_order = Order(
            id='test_sell_1',
            symbol='BTCUSD',
            side='sell',
            amount=5.0,  # Sell half
            price=110.0,
            order_type='market',
            status='pending',
            timestamp=datetime.now(),
            exchange='test'
        )
        
        result = simulator.execute_order(sell_order, market_data)
        
        assert result is True
        assert simulator.positions['BTCUSD'].size == 5.0  # Half remaining
        assert simulator.cash > initial_cash  # Should have made profit
        assert len(simulator.completed_trades) == 1
        
    def test_insufficient_cash(self):
        """Test handling of insufficient cash."""
        simulator = PortfolioSimulator(initial_capital=100.0)  # Small capital
        
        market_data = MarketData(
            symbol='BTCUSD',
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=200.0,  # Expensive
            volume=1000.0,
            exchange='test'
        )
        
        order = Order(
            id='test_buy_1',
            symbol='BTCUSD',
            side='buy',
            amount=10.0,  # Too expensive
            price=200.0,
            order_type='market',
            status='pending',
            timestamp=datetime.now(),
            exchange='test'
        )
        
        result = simulator.execute_order(order, market_data)
        
        assert result is False
        assert len(simulator.positions) == 0
        assert simulator.cash == 100.0  # Unchanged
        
    def test_portfolio_value_calculation(self):
        """Test portfolio value calculation."""
        simulator = PortfolioSimulator(initial_capital=10000.0)
        
        # Create some positions
        simulator.positions['BTCUSD'] = SimulatedPosition(
            symbol='BTCUSD',
            size=10.0,
            entry_price=100.0,
            entry_timestamp=datetime.now(),
            current_price=110.0
        )
        
        simulator.positions['ETHUSD'] = SimulatedPosition(
            symbol='ETHUSD',
            size=50.0,
            entry_price=50.0,
            entry_timestamp=datetime.now(),
            current_price=55.0
        )
        
        simulator.cash = 5000.0
        
        portfolio_value = simulator.get_portfolio_value()
        expected_value = 5000.0 + (10.0 * 110.0) + (50.0 * 55.0)  # Cash + positions
        
        assert portfolio_value == expected_value


class TestPerformanceAnalyzer:
    """Test cases for PerformanceAnalyzer."""
    
    def test_initialization(self):
        """Test performance analyzer initialization."""
        analyzer = PerformanceAnalyzer(risk_free_rate=0.03)
        assert analyzer.risk_free_rate == 0.03
        
    def test_return_metrics_calculation(self, sample_market_data):
        """Test return metrics calculation."""
        analyzer = PerformanceAnalyzer()
        
        # Create portfolio history
        portfolio_values = sample_market_data['close'] * 100  # Scale up
        portfolio_history = pd.DataFrame({
            'total_value': portfolio_values,
            'cash': portfolio_values * 0.1,
            'positions_value': portfolio_values * 0.9,
            'unrealized_pnl': 0,
            'realized_pnl': 0
        }, index=sample_market_data.index)
        
        metrics = analyzer._calculate_return_metrics(portfolio_history)
        
        assert 'total_return' in metrics
        assert 'annualized_return' in metrics
        assert 'avg_daily_return' in metrics
        assert 'initial_value' in metrics
        assert 'final_value' in metrics
        
        # Check that total return is calculated correctly
        initial_value = portfolio_values.iloc[0]
        final_value = portfolio_values.iloc[-1]
        expected_return = (final_value - initial_value) / initial_value
        
        assert abs(metrics['total_return'] - expected_return) < 0.001
        
    def test_risk_metrics_calculation(self, sample_market_data):
        """Test risk metrics calculation."""
        analyzer = PerformanceAnalyzer()
        
        portfolio_values = sample_market_data['close'] * 100
        portfolio_history = pd.DataFrame({
            'total_value': portfolio_values,
            'cash': portfolio_values * 0.1,
            'positions_value': portfolio_values * 0.9,
            'unrealized_pnl': 0,
            'realized_pnl': 0
        }, index=sample_market_data.index)
        
        metrics = analyzer._calculate_risk_metrics(portfolio_history)
        
        assert 'volatility' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'sortino_ratio' in metrics
        assert 'var_95' in metrics
        assert 'cvar_95' in metrics
        
        # Volatility should be positive
        assert metrics['volatility'] >= 0
        
    def test_trade_metrics_calculation(self):
        """Test trade metrics calculation."""
        analyzer = PerformanceAnalyzer()
        
        # Create sample trade history
        trade_history = [
            {'net_pnl': 100.0, 'entry_timestamp': datetime(2023, 1, 1), 'exit_timestamp': datetime(2023, 1, 2)},
            {'net_pnl': -50.0, 'entry_timestamp': datetime(2023, 1, 2), 'exit_timestamp': datetime(2023, 1, 3)},
            {'net_pnl': 75.0, 'entry_timestamp': datetime(2023, 1, 3), 'exit_timestamp': datetime(2023, 1, 4)},
            {'net_pnl': -25.0, 'entry_timestamp': datetime(2023, 1, 4), 'exit_timestamp': datetime(2023, 1, 5)},
        ]
        
        metrics = analyzer._calculate_trade_metrics(trade_history)
        
        assert metrics['total_trades'] == 4
        assert metrics['winning_trades'] == 2
        assert metrics['losing_trades'] == 2
        assert metrics['win_rate'] == 0.5
        assert metrics['avg_win'] == 87.5  # (100 + 75) / 2
        assert metrics['avg_loss'] == -37.5  # (-50 + -25) / 2
        
        # Profit factor = total wins / total losses
        expected_profit_factor = 175.0 / 75.0
        assert abs(metrics['profit_factor'] - expected_profit_factor) < 0.001
        
    def test_drawdown_calculation(self, sample_market_data):
        """Test drawdown calculation."""
        analyzer = PerformanceAnalyzer()
        
        # Create portfolio with a drawdown
        values = [1000, 1100, 1200, 1000, 900, 950, 1100, 1150]
        dates = pd.date_range('2023-01-01', periods=len(values), freq='D')
        
        portfolio_history = pd.DataFrame({
            'total_value': values,
            'cash': [v * 0.1 for v in values],
            'positions_value': [v * 0.9 for v in values],
            'unrealized_pnl': 0,
            'realized_pnl': 0
        }, index=dates)
        
        metrics = analyzer._calculate_drawdown_metrics(portfolio_history)
        
        assert 'max_drawdown' in metrics
        assert 'current_drawdown' in metrics
        assert 'avg_drawdown' in metrics
        
        # Max drawdown should be from peak (1200) to trough (900)
        expected_max_dd = (900 - 1200) / 1200
        assert abs(metrics['max_drawdown'] - expected_max_dd) < 0.001


class TestBacktestEngine:
    """Test cases for BacktestEngine."""
    
    def test_initialization(self, backtest_config):
        """Test backtest engine initialization."""
        engine = BacktestEngine(backtest_config)
        
        assert engine.config == backtest_config
        assert engine.portfolio_simulator is not None
        assert engine.performance_analyzer is not None
        assert len(engine.market_data) == 0
        
    def test_load_market_data(self, backtest_config, sample_market_data):
        """Test loading market data."""
        engine = BacktestEngine(backtest_config)
        
        engine.load_market_data('BTCUSD', sample_market_data)
        
        assert 'BTCUSD' in engine.market_data
        assert len(engine.market_data['BTCUSD']) > 0
        
    def test_run_backtest(self, backtest_config, sample_market_data):
        """Test running a complete backtest."""
        engine = BacktestEngine(backtest_config)
        engine.load_market_data('BTCUSD', sample_market_data)
        
        # Create a simple buy-and-hold strategy
        buy_signal = TradingSignal(
            symbol='BTCUSD',
            action='BUY',
            confidence=1.0,
            timestamp=datetime(2023, 1, 2),
            strategy_name='TestStrategy',
            metadata={}
        )
        
        sell_signal = TradingSignal(
            symbol='BTCUSD',
            action='SELL',
            confidence=1.0,
            timestamp=datetime(2023, 2, 1),
            strategy_name='TestStrategy',
            metadata={}
        )
        
        strategy = MockStrategy([buy_signal, sell_signal])
        
        result = engine.run_backtest(strategy, ['BTCUSD'])
        
        assert isinstance(result, BacktestResult)
        assert result.strategy_name == 'MockStrategy'
        assert result.config == backtest_config
        assert not result.portfolio_history.empty
        assert 'total_return' in result.performance_metrics
        
    def test_missing_market_data(self, backtest_config):
        """Test handling of missing market data."""
        engine = BacktestEngine(backtest_config)
        strategy = MockStrategy()
        
        with pytest.raises(ValueError, match="Missing market data"):
            engine.run_backtest(strategy, ['BTCUSD'])


class TestReportGenerator:
    """Test cases for ReportGenerator."""
    
    def test_initialization(self):
        """Test report generator initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(output_dir=temp_dir)
            assert generator.output_dir == temp_dir
            assert os.path.exists(temp_dir)
            
    def test_generate_full_report(self, backtest_config, sample_market_data):
        """Test generating a full report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(output_dir=temp_dir)
            
            # Create a mock backtest result
            portfolio_history = pd.DataFrame({
                'total_value': sample_market_data['close'] * 100,
                'cash': sample_market_data['close'] * 10,
                'positions_value': sample_market_data['close'] * 90,
                'unrealized_pnl': 0,
                'realized_pnl': 0
            }, index=sample_market_data.index)
            
            trade_history = [
                {
                    'symbol': 'BTCUSD',
                    'side': 'buy',
                    'entry_price': 100.0,
                    'exit_price': 110.0,
                    'size': 10.0,
                    'entry_timestamp': datetime(2023, 1, 1),
                    'exit_timestamp': datetime(2023, 1, 10),
                    'pnl': 100.0,
                    'commission': 1.0,
                    'slippage': 0.5,
                    'net_pnl': 98.5
                }
            ]
            
            result = BacktestResult(
                config=backtest_config,
                strategy_name='TestStrategy',
                total_return=0.15,
                sharpe_ratio=1.2,
                max_drawdown=-0.05,
                total_trades=1,
                win_rate=1.0,
                profit_factor=2.0,
                portfolio_history=portfolio_history,
                trade_history=trade_history,
                performance_metrics={'total_return': 0.15}
            )
            
            # Generate report (skip charts to avoid matplotlib issues in tests)
            files = generator.generate_full_report(
                result, 
                save_charts=False, 
                save_html=True
            )
            
            assert 'html_report' in files
            assert os.path.exists(files['html_report'])
            
            # Check CSV exports
            assert 'portfolio_history' in files
            assert os.path.exists(files['portfolio_history'])


if __name__ == '__main__':
    pytest.main([__file__])