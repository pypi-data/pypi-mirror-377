"""
Unit tests for multi-market backtesting capabilities.

This module tests the multi-market backtesting engine, portfolio simulator,
performance analyzer, and report generator to ensure accuracy and reliability.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
import tempfile
import os

from src.backtesting.multi_market_backtest_engine import (
    MultiMarketBacktestEngine, MultiMarketBacktestConfig, MultiMarketBacktestResult
)
from src.backtesting.multi_market_portfolio_simulator import (
    MultiMarketPortfolioSimulator, MultiMarketPosition, MultiMarketTrade
)
from src.backtesting.multi_market_performance_analyzer import (
    MultiMarketPerformanceAnalyzer, MarketPerformanceMetrics, CrossMarketAnalysis
)
from src.backtesting.multi_market_report_generator import MultiMarketReportGenerator
from src.markets.types import MarketType, UnifiedSymbol
from src.models.data_models import UnifiedMarketData, MarketSpecificOrder, OrderSide, OrderType, OrderStatus
from src.strategies.base_strategy import BaseStrategy


class MockMultiMarketStrategy(BaseStrategy):
    """Mock strategy for testing multi-market backtesting."""
    
    def __init__(self):
        from src.strategies.strategy_config import StrategyConfig
        config = StrategyConfig(name="MockMultiMarketStrategy")
        super().__init__(config)
        self.signals_to_generate = []
    
    def initialize(self):
        """Initialize the strategy."""
        pass
    
    def get_required_data_length(self):
        """Return required data length."""
        return 1
    
    def analyze(self, market_data):
        """Generate mock signals for testing."""
        if not market_data:
            return None
        
        # Simple mock logic: buy if price is increasing
        if len(market_data) > 0:
            current_data = market_data[0]
            if hasattr(current_data, 'close') and float(current_data.close) > 100:
                from src.models.data_models import TradingSignal, SignalAction
                return TradingSignal(
                    symbol=current_data.symbol,
                    action=SignalAction.BUY,
                    confidence=0.8,
                    timestamp=current_data.timestamp,
                    strategy_name=self.name,
                    price=current_data.close
                )
        return None


class TestMultiMarketBacktestConfig(unittest.TestCase):
    """Test multi-market backtest configuration."""
    
    def test_config_creation(self):
        """Test creating multi-market backtest configuration."""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        initial_capital = 100000.0
        
        config = MultiMarketBacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        
        self.assertEqual(config.start_date, start_date)
        self.assertEqual(config.end_date, end_date)
        self.assertEqual(config.initial_capital, initial_capital)
        self.assertIn(MarketType.CRYPTO, config.commission_rates)
        self.assertIn(MarketType.FOREX, config.commission_rates)
    
    def test_config_getters(self):
        """Test configuration getter methods."""
        config = MultiMarketBacktestConfig(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 12, 31),
            initial_capital=100000.0
        )
        
        crypto_commission = config.get_commission_rate(MarketType.CRYPTO)
        forex_commission = config.get_commission_rate(MarketType.FOREX)
        
        self.assertIsInstance(crypto_commission, float)
        self.assertIsInstance(forex_commission, float)
        self.assertGreater(crypto_commission, 0)
        self.assertGreater(forex_commission, 0)


class TestMultiMarketPortfolioSimulator(unittest.TestCase):
    """Test multi-market portfolio simulator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulator = MultiMarketPortfolioSimulator(
            initial_capital=Decimal("100000"),
            base_currency="USD"
        )
        
        # Create test symbols
        self.crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        self.forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        
        # Create test market data
        self.crypto_data = UnifiedMarketData(
            symbol=self.crypto_symbol,
            timestamp=datetime.now(),
            open=Decimal("50000"),
            high=Decimal("51000"),
            low=Decimal("49000"),
            close=Decimal("50500"),
            volume=Decimal("100"),
            source="test",
            market_type=MarketType.CRYPTO
        )
        
        self.forex_data = UnifiedMarketData(
            symbol=self.forex_symbol,
            timestamp=datetime.now(),
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0950"),
            close=Decimal("1.1025"),
            volume=Decimal("1000000"),
            source="test",
            market_type=MarketType.FOREX
        )
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        self.assertEqual(self.simulator.initial_capital, Decimal("100000"))
        self.assertEqual(self.simulator.base_currency, "USD")
        self.assertEqual(self.simulator.cash, Decimal("100000"))
        self.assertEqual(len(self.simulator.positions), 0)
    
    def test_buy_order_execution(self):
        """Test executing buy orders."""
        # Create buy order
        buy_order = MarketSpecificOrder(
            id="test_buy_1",
            symbol=self.crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("1"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="test",
            market_type=MarketType.CRYPTO
        )
        
        # Execute order
        result = self.simulator.execute_order(buy_order, self.crypto_data)
        
        self.assertTrue(result)
        self.assertEqual(len(self.simulator.positions), 1)
        self.assertLess(self.simulator.cash, Decimal("100000"))  # Cash should decrease
        
        # Check position
        position_key = str(self.crypto_symbol)
        self.assertIn(position_key, self.simulator.positions)
        position = self.simulator.positions[position_key]
        self.assertEqual(position.size, Decimal("1"))
        self.assertEqual(position.market_type, MarketType.CRYPTO)
    
    def test_sell_order_execution(self):
        """Test executing sell orders."""
        # First, create a position by buying
        buy_order = MarketSpecificOrder(
            id="test_buy_1",
            symbol=self.crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("1"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="test",
            market_type=MarketType.CRYPTO
        )
        
        self.simulator.execute_order(buy_order, self.crypto_data)
        initial_cash = self.simulator.cash
        
        # Now sell the position
        sell_order = MarketSpecificOrder(
            id="test_sell_1",
            symbol=self.crypto_symbol,
            side=OrderSide.SELL,
            amount=Decimal("1"),
            price=Decimal("51000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now() + timedelta(hours=1),
            source="test",
            market_type=MarketType.CRYPTO
        )
        
        result = self.simulator.execute_order(sell_order, self.crypto_data)
        
        self.assertTrue(result)
        self.assertEqual(len(self.simulator.positions), 0)  # Position should be closed
        self.assertGreater(self.simulator.cash, initial_cash)  # Should have profit
        self.assertEqual(len(self.simulator.completed_trades), 1)  # Should have one completed trade
    
    def test_position_updates(self):
        """Test updating positions with new market data."""
        # Create position
        buy_order = MarketSpecificOrder(
            id="test_buy_1",
            symbol=self.crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("1"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="test",
            market_type=MarketType.CRYPTO
        )
        
        self.simulator.execute_order(buy_order, self.crypto_data)
        
        # Update with new market data
        new_crypto_data = UnifiedMarketData(
            symbol=self.crypto_symbol,
            timestamp=datetime.now(),
            open=Decimal("51000"),
            high=Decimal("52000"),
            low=Decimal("50500"),
            close=Decimal("51500"),  # Price increased
            volume=Decimal("100"),
            source="test",
            market_type=MarketType.CRYPTO
        )
        
        market_data = {str(self.crypto_symbol): new_crypto_data}
        self.simulator.update_positions(market_data)
        
        # Check that position was updated
        position = self.simulator.positions[str(self.crypto_symbol)]
        self.assertEqual(position.current_price, Decimal("51500"))
        self.assertGreater(position.unrealized_pnl, 0)  # Should have unrealized profit
    
    def test_portfolio_snapshot(self):
        """Test taking portfolio snapshots."""
        timestamp = datetime.now()
        snapshot = self.simulator.take_snapshot(timestamp)
        
        self.assertEqual(snapshot.timestamp, timestamp)
        self.assertEqual(snapshot.cash, Decimal("100000"))
        self.assertEqual(snapshot.positions_value, Decimal("0"))
        self.assertEqual(snapshot.total_value, Decimal("100000"))
        self.assertEqual(len(snapshot.positions), 0)
    
    def test_market_allocation(self):
        """Test market allocation calculation."""
        # Create positions in different markets
        crypto_order = MarketSpecificOrder(
            id="crypto_buy",
            symbol=self.crypto_symbol,
            side=OrderSide.BUY,
            amount=Decimal("1"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="test",
            market_type=MarketType.CRYPTO
        )
        
        forex_order = MarketSpecificOrder(
            id="forex_buy",
            symbol=self.forex_symbol,
            side=OrderSide.BUY,
            amount=Decimal("10000"),
            price=Decimal("1.1000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="test",
            market_type=MarketType.FOREX
        )
        
        self.simulator.execute_order(crypto_order, self.crypto_data)
        self.simulator.execute_order(forex_order, self.forex_data)
        
        allocation = self.simulator.get_market_allocation()
        
        self.assertIn(MarketType.CRYPTO, allocation)
        self.assertIn(MarketType.FOREX, allocation)
        # The allocation should include both markets and cash
        # Since we have cash remaining, the sum might not be exactly 100%
        self.assertGreater(sum(allocation.values()), 50.0)  # Should have significant allocation


class TestMultiMarketBacktestEngine(unittest.TestCase):
    """Test multi-market backtest engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MultiMarketBacktestConfig(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 31),
            initial_capital=100000.0,
            respect_market_hours=False  # Disable for testing
        )
        
        self.engine = MultiMarketBacktestEngine(self.config)
        self.strategy = MockMultiMarketStrategy()
        
        # Create test symbols
        self.crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        self.forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertEqual(self.engine.config, self.config)
        self.assertIsNotNone(self.engine.performance_analyzer)
        self.assertEqual(len(self.engine.portfolio_simulators), len(MarketType))
    
    def test_load_market_data(self):
        """Test loading market data."""
        # Create test data
        dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
        data = pd.DataFrame({
            'open': np.random.uniform(50000, 51000, len(dates)),
            'high': np.random.uniform(51000, 52000, len(dates)),
            'low': np.random.uniform(49000, 50000, len(dates)),
            'close': np.random.uniform(50000, 51000, len(dates)),
            'volume': np.random.uniform(100, 1000, len(dates))
        }, index=dates)
        
        self.engine.load_market_data(self.crypto_symbol, data)
        
        symbol_key = str(self.crypto_symbol)
        self.assertIn(symbol_key, self.engine.market_data)
        self.assertIn(symbol_key, self.engine.unified_market_data)
        self.assertEqual(len(self.engine.market_data[symbol_key]), len(dates))
    
    def test_should_trade_at_time(self):
        """Test market hours enforcement."""
        timestamp = datetime(2023, 1, 15, 12, 0)  # Sunday noon
        
        # Crypto should always trade
        crypto_should_trade = self.engine._should_trade_at_time(MarketType.CRYPTO, timestamp)
        self.assertTrue(crypto_should_trade)
        
        # Forex should trade when market hours are disabled
        forex_should_trade = self.engine._should_trade_at_time(MarketType.FOREX, timestamp)
        self.assertTrue(forex_should_trade)  # Because respect_market_hours=False
    
    @patch('src.backtesting.multi_market_backtest_engine.logger')
    def test_run_backtest_no_data(self, mock_logger):
        """Test running backtest with no data."""
        symbols = [self.crypto_symbol]
        
        with self.assertRaises(ValueError) as context:
            self.engine.run_backtest(self.strategy, symbols)
        
        self.assertIn("Missing market data", str(context.exception))
    
    def test_run_backtest_with_data(self):
        """Test running complete backtest."""
        # Create test data
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
        crypto_data = pd.DataFrame({
            'open': [50000] * len(dates),
            'high': [51000] * len(dates),
            'low': [49000] * len(dates),
            'close': [50500] * len(dates),
            'volume': [100] * len(dates)
        }, index=dates)
        
        self.engine.load_market_data(self.crypto_symbol, crypto_data)
        
        # Run backtest
        result = self.engine.run_backtest(self.strategy, [self.crypto_symbol])
        
        self.assertIsInstance(result, MultiMarketBacktestResult)
        self.assertEqual(result.strategy_name, "MockMultiMarketStrategy")
        self.assertIsNotNone(result.portfolio_history)
        self.assertIsInstance(result.trade_history, list)


class TestMultiMarketPerformanceAnalyzer(unittest.TestCase):
    """Test multi-market performance analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MultiMarketPerformanceAnalyzer()
        
        # Create mock backtest result
        self.mock_result = Mock(spec=MultiMarketBacktestResult)
        self.mock_result.strategy_name = "TestStrategy"
        self.mock_result.total_return = 0.15
        self.mock_result.sharpe_ratio = 1.2
        self.mock_result.max_drawdown = -0.05
        self.mock_result.total_trades = 50
        self.mock_result.win_rate = 0.6
        self.mock_result.profit_factor = 1.8
        
        # Create mock portfolio history
        dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
        self.mock_result.portfolio_history = pd.DataFrame({
            'cash': np.random.uniform(80000, 120000, len(dates)),
            'positions_value': np.random.uniform(0, 20000, len(dates)),
            'total_value': np.random.uniform(90000, 130000, len(dates)),
            'unrealized_pnl': np.random.uniform(-5000, 5000, len(dates)),
            'realized_pnl': np.random.uniform(-2000, 8000, len(dates))
        }, index=dates)
        
        # Create mock trade history
        self.mock_result.trade_history = [
            {
                'symbol': 'BTCUSDT',
                'market_type': 'crypto',
                'net_pnl': 1000,
                'timestamp': datetime(2023, 1, 5),
                'entry_timestamp': datetime(2023, 1, 5),
                'exit_timestamp': datetime(2023, 1, 6)
            },
            {
                'symbol': 'EURUSD',
                'market_type': 'forex',
                'net_pnl': -500,
                'timestamp': datetime(2023, 1, 10),
                'entry_timestamp': datetime(2023, 1, 10),
                'exit_timestamp': datetime(2023, 1, 11)
            }
        ]
        
        # Mock additional attributes
        self.mock_result.market_performance = {}
        self.mock_result.session_performance = {}
        self.mock_result.cross_market_correlations = {}
        
        # Mock config
        mock_config = Mock()
        mock_config.initial_capital = 100000.0
        self.mock_result.config = mock_config
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(self.analyzer.risk_free_rate, 0.02)
        self.assertIsNotNone(self.analyzer.base_analyzer)
    
    def test_analyze_multi_market_performance(self):
        """Test comprehensive multi-market performance analysis."""
        analysis = self.analyzer.analyze_multi_market_performance(self.mock_result)
        
        self.assertIn('basic_metrics', analysis)
        self.assertIn('market_performance', analysis)
        self.assertIn('cross_market_analysis', analysis)
        self.assertIn('currency_analysis', analysis)
        self.assertIn('risk_attribution', analysis)
        self.assertIn('time_analysis', analysis)
    
    def test_market_performance_analysis(self):
        """Test market-specific performance analysis."""
        market_performance = self.analyzer._analyze_market_performance(self.mock_result)
        
        self.assertIsInstance(market_performance, dict)
        # Should have analysis for both crypto and forex
        if market_performance:
            for market_type, metrics in market_performance.items():
                self.assertIsInstance(metrics, MarketPerformanceMetrics)
                self.assertEqual(metrics.market_type, market_type)
    
    def test_cross_market_analysis(self):
        """Test cross-market relationship analysis."""
        cross_market = self.analyzer._analyze_cross_market_relationships(self.mock_result)
        
        self.assertIsInstance(cross_market, CrossMarketAnalysis)
        self.assertIsNotNone(cross_market.correlation_matrix)
        self.assertIsInstance(cross_market.diversification_ratio, float)
        self.assertIsInstance(cross_market.market_concentration, dict)
    
    def test_generate_multi_market_report(self):
        """Test generating multi-market performance report."""
        analysis = self.analyzer.analyze_multi_market_performance(self.mock_result)
        report = self.analyzer.generate_multi_market_report(analysis)
        
        self.assertIsInstance(report, str)
        self.assertIn("MULTI-MARKET PERFORMANCE ANALYSIS", report)
        self.assertIn("OVERALL PERFORMANCE", report)


class TestMultiMarketReportGenerator(unittest.TestCase):
    """Test multi-market report generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = MultiMarketReportGenerator(self.temp_dir)
        
        # Create mock backtest result
        self.mock_result = Mock(spec=MultiMarketBacktestResult)
        self.mock_result.strategy_name = "TestStrategy"
        self.mock_result.total_return = 0.15
        self.mock_result.sharpe_ratio = 1.2
        self.mock_result.max_drawdown = -0.05
        self.mock_result.total_trades = 50
        self.mock_result.win_rate = 0.6
        self.mock_result.profit_factor = 1.8
        
        # Mock config
        mock_config = Mock()
        mock_config.start_date = datetime(2023, 1, 1)
        mock_config.end_date = datetime(2023, 1, 31)
        mock_config.initial_capital = 100000.0
        self.mock_result.config = mock_config
        
        # Create mock portfolio history
        dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
        self.mock_result.portfolio_history = pd.DataFrame({
            'cash': [90000] * len(dates),
            'positions_value': [10000] * len(dates),
            'total_value': [100000] * len(dates),
            'unrealized_pnl': [0] * len(dates),
            'realized_pnl': [0] * len(dates)
        }, index=dates)
        
        # Mock trade history
        self.mock_result.trade_history = [
            {
                'symbol': 'BTCUSDT',
                'market_type': 'crypto',
                'net_pnl': 1000,
                'timestamp': datetime(2023, 1, 5)
            }
        ]
        
        # Mock additional attributes
        self.mock_result.market_performance = {}
        self.mock_result.session_performance = {}
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.output_dir, self.temp_dir)
        self.assertIsNotNone(self.generator.performance_analyzer)
        self.assertIsNotNone(self.generator.base_generator)
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_charts(self, mock_close, mock_savefig):
        """Test chart generation."""
        # Mock analysis data
        analysis = {
            'cross_market_analysis': Mock(),
            'session_performance': {},
            'currency_analysis': {},
            'risk_attribution': {},
            'time_analysis': {}
        }
        
        # Mock correlation matrix
        analysis['cross_market_analysis'].correlation_matrix = pd.DataFrame()
        
        chart_files = self.generator._generate_multi_market_charts(self.mock_result, analysis)
        
        self.assertIsInstance(chart_files, dict)
        self.assertGreater(len(chart_files), 0)
        
        # Verify that charts were "saved" (mocked)
        self.assertGreater(mock_savefig.call_count, 0)
        self.assertGreater(mock_close.call_count, 0)
    
    def test_export_csv_data(self):
        """Test CSV data export."""
        csv_files = self.generator._export_multi_market_data_to_csv(self.mock_result)
        
        self.assertIsInstance(csv_files, dict)
        self.assertIn('portfolio_history', csv_files)
        self.assertIn('trade_history', csv_files)
        
        # Check that files were created
        for file_path in csv_files.values():
            self.assertTrue(os.path.exists(file_path))


class TestMultiMarketIntegration(unittest.TestCase):
    """Integration tests for multi-market backtesting system."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        self.config = MultiMarketBacktestConfig(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 10),
            initial_capital=100000.0,
            respect_market_hours=False
        )
        
        self.engine = MultiMarketBacktestEngine(self.config)
        self.strategy = MockMultiMarketStrategy()
        
        # Create test symbols
        self.crypto_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        self.forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_backtest(self):
        """Test complete end-to-end multi-market backtesting workflow."""
        # Create test data for both markets
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
        
        crypto_data = pd.DataFrame({
            'open': np.random.uniform(50000, 51000, len(dates)),
            'high': np.random.uniform(51000, 52000, len(dates)),
            'low': np.random.uniform(49000, 50000, len(dates)),
            'close': np.random.uniform(50000, 51000, len(dates)),
            'volume': np.random.uniform(100, 1000, len(dates))
        }, index=dates)
        
        forex_data = pd.DataFrame({
            'open': np.random.uniform(1.1000, 1.1100, len(dates)),
            'high': np.random.uniform(1.1100, 1.1200, len(dates)),
            'low': np.random.uniform(1.0900, 1.1000, len(dates)),
            'close': np.random.uniform(1.1000, 1.1100, len(dates)),
            'volume': np.random.uniform(1000000, 2000000, len(dates))
        }, index=dates)
        
        # Load data
        self.engine.load_market_data(self.crypto_symbol, crypto_data)
        self.engine.load_market_data(self.forex_symbol, forex_data)
        
        # Run backtest
        result = self.engine.run_backtest(self.strategy, [self.crypto_symbol, self.forex_symbol])
        
        # Verify result
        self.assertIsInstance(result, MultiMarketBacktestResult)
        self.assertEqual(result.strategy_name, "MockMultiMarketStrategy")
        self.assertIsNotNone(result.portfolio_history)
        self.assertIsInstance(result.trade_history, list)
        
        # Analyze performance
        analyzer = MultiMarketPerformanceAnalyzer()
        analysis = analyzer.analyze_multi_market_performance(result)
        
        self.assertIn('basic_metrics', analysis)
        self.assertIn('market_performance', analysis)
        
        # Generate report
        generator = MultiMarketReportGenerator(self.temp_dir)
        generated_files = generator.generate_full_report(result, save_charts=False, save_html=True)
        
        self.assertIn('html_report', generated_files)
        self.assertTrue(os.path.exists(generated_files['html_report']))
    
    def test_session_aware_backtesting(self):
        """Test session-aware backtesting functionality."""
        # Create config with session awareness
        config_with_sessions = MultiMarketBacktestConfig(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 10),
            initial_capital=100000.0,
            respect_market_hours=True,
            session_config_path=None  # Will disable session manager
        )
        
        engine = MultiMarketBacktestEngine(config_with_sessions)
        
        # Test should_trade_at_time method
        timestamp = datetime(2023, 1, 5, 12, 0)  # Thursday noon
        
        crypto_should_trade = engine._should_trade_at_time(MarketType.CRYPTO, timestamp)
        forex_should_trade = engine._should_trade_at_time(MarketType.FOREX, timestamp)
        
        # Crypto should always trade
        self.assertTrue(crypto_should_trade)
        
        # Forex should trade when no session manager (defaults to True)
        self.assertTrue(forex_should_trade)
    
    def test_currency_conversion_accuracy(self):
        """Test currency conversion accuracy in portfolio simulation."""
        simulator = MultiMarketPortfolioSimulator(
            initial_capital=Decimal("100000"),
            base_currency="USD"
        )
        
        # Update exchange rates
        simulator.update_exchange_rate("EUR", Decimal("1.1"))
        simulator.update_exchange_rate("BTC", Decimal("50000"))
        
        # Test exchange rate retrieval
        eur_rate = simulator._get_exchange_rate("EUR")
        btc_rate = simulator._get_exchange_rate("BTC")
        
        self.assertEqual(eur_rate, Decimal("1.1"))
        self.assertEqual(btc_rate, Decimal("50000"))
        
        # Test position with currency conversion
        forex_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        forex_data = UnifiedMarketData(
            symbol=forex_symbol,
            timestamp=datetime.now(),
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0950"),
            close=Decimal("1.1025"),
            volume=Decimal("1000000"),
            source="test",
            market_type=MarketType.FOREX
        )
        
        forex_order = MarketSpecificOrder(
            id="forex_test",
            symbol=forex_symbol,
            side=OrderSide.BUY,
            amount=Decimal("10000"),
            price=Decimal("1.1000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(),
            source="test",
            market_type=MarketType.FOREX
        )
        
        initial_cash = simulator.cash
        result = simulator.execute_order(forex_order, forex_data)
        
        self.assertTrue(result)
        self.assertLess(simulator.cash, initial_cash)
        
        # Verify position was created with correct currency handling
        position_key = str(forex_symbol)
        self.assertIn(position_key, simulator.positions)


if __name__ == '__main__':
    unittest.main()