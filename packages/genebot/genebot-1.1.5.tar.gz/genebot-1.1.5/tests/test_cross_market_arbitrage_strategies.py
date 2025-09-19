"""
Unit tests for cross-market arbitrage strategies.

This module tests the arbitrage strategy implementations including:
- CrossMarketArbitrageStrategy base class
- CryptoForexArbitrageStrategy
- TriangularArbitrageStrategy
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.strategies.cross_market_arbitrage_strategy import CrossMarketArbitrageStrategy, ArbitrageSignal
from src.strategies.crypto_forex_arbitrage_strategy import CryptoForexArbitrageStrategy
from src.strategies.triangular_arbitrage_strategy import TriangularArbitrageStrategy
from src.strategies.base_strategy import StrategyConfig
from src.models.data_models import UnifiedMarketData, SessionInfo, SignalAction
from src.markets.types import MarketType, UnifiedSymbol
from src.analysis.arbitrage_detector import ArbitrageOpportunity


class TestCrossMarketArbitrageStrategy:
    """Test cases for the base CrossMarketArbitrageStrategy class."""
    
    @pytest.fixture
    def strategy_config(self):
        """Create a test strategy configuration."""
        return StrategyConfig(
            name="test_arbitrage",
            enabled=True,
            parameters={
                'min_profit_threshold': 0.005,
                'max_execution_time_seconds': 30,
                'max_position_size': 10000,
                'risk_tolerance': 'MEDIUM',
                'crypto_exchanges': ['binance', 'coinbase'],
                'forex_brokers': ['oanda', 'mt5']
            }
        )
    
    @pytest.fixture
    def mock_arbitrage_strategy(self, strategy_config):
        """Create a mock arbitrage strategy for testing."""
        class MockArbitrageStrategy(CrossMarketArbitrageStrategy):
            def _detect_arbitrage_opportunities(self, crypto_data, forex_data):
                return []
        
        return MockArbitrageStrategy(strategy_config)
    
    def test_strategy_initialization(self, mock_arbitrage_strategy):
        """Test strategy initialization."""
        assert mock_arbitrage_strategy.name == "test_arbitrage"
        assert mock_arbitrage_strategy.min_profit_threshold == Decimal('0.005')
        assert mock_arbitrage_strategy.max_execution_time == timedelta(seconds=30)
        assert mock_arbitrage_strategy.max_position_size == Decimal('10000')
        assert mock_arbitrage_strategy.risk_tolerance == 'MEDIUM'
        assert mock_arbitrage_strategy.crypto_exchanges == ['binance', 'coinbase']
        assert mock_arbitrage_strategy.forex_brokers == ['oanda', 'mt5']
    
    def test_strategy_initialization_success(self, mock_arbitrage_strategy):
        """Test successful strategy initialization."""
        result = mock_arbitrage_strategy.initialize()
        assert result is True
        assert mock_arbitrage_strategy._initialized is True
    
    def test_parameter_validation_success(self, mock_arbitrage_strategy):
        """Test successful parameter validation."""
        result = mock_arbitrage_strategy.validate_parameters()
        assert result is True
    
    def test_parameter_validation_invalid_profit_threshold(self, strategy_config):
        """Test parameter validation with invalid profit threshold."""
        strategy_config.parameters['min_profit_threshold'] = -0.001
        
        class MockArbitrageStrategy(CrossMarketArbitrageStrategy):
            def _detect_arbitrage_opportunities(self, crypto_data, forex_data):
                return []
        
        strategy = MockArbitrageStrategy(strategy_config)
        result = strategy.validate_parameters()
        assert result is False
    
    def test_parameter_validation_invalid_execution_time(self, strategy_config):
        """Test parameter validation with invalid execution time."""
        strategy_config.parameters['max_execution_time_seconds'] = -10
        
        class MockArbitrageStrategy(CrossMarketArbitrageStrategy):
            def _detect_arbitrage_opportunities(self, crypto_data, forex_data):
                return []
        
        strategy = MockArbitrageStrategy(strategy_config)
        result = strategy.validate_parameters()
        assert result is False
    
    def test_parameter_validation_invalid_risk_tolerance(self, strategy_config):
        """Test parameter validation with invalid risk tolerance."""
        strategy_config.parameters['risk_tolerance'] = 'INVALID'
        
        class MockArbitrageStrategy(CrossMarketArbitrageStrategy):
            def _detect_arbitrage_opportunities(self, crypto_data, forex_data):
                return []
        
        strategy = MockArbitrageStrategy(strategy_config)
        result = strategy.validate_parameters()
        assert result is False
    
    def test_opportunity_scoring(self, mock_arbitrage_strategy):
        """Test opportunity scoring calculation."""
        opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD')],
            markets=['binance', 'coinbase'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('1.5'),
            execution_path=[],
            risk_factors=['LOW_SPREAD_MARGIN'],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            minimum_capital=Decimal('1000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        score = mock_arbitrage_strategy._calculate_opportunity_score(opportunity)
        assert score > 0
        assert isinstance(score, float)
    
    def test_opportunity_validation_success(self, mock_arbitrage_strategy):
        """Test successful opportunity validation."""
        opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD')],
            markets=['binance', 'coinbase'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('1.0'),
            execution_path=[],
            risk_factors=['LOW_SPREAD_MARGIN'],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            minimum_capital=Decimal('1000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        result = mock_arbitrage_strategy._validate_opportunity(opportunity)
        assert result is True
    
    def test_opportunity_validation_expired(self, mock_arbitrage_strategy):
        """Test opportunity validation with expired opportunity."""
        opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD')],
            markets=['binance', 'coinbase'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('1.0'),
            execution_path=[],
            risk_factors=[],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() - timedelta(seconds=10),  # Expired
            minimum_capital=Decimal('1000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        result = mock_arbitrage_strategy._validate_opportunity(opportunity)
        assert result is False
    
    def test_opportunity_validation_too_much_capital(self, mock_arbitrage_strategy):
        """Test opportunity validation with excessive capital requirements."""
        opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD')],
            markets=['binance', 'coinbase'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('1.0'),
            execution_path=[],
            risk_factors=[],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            minimum_capital=Decimal('20000'),  # Exceeds max_position_size
            estimated_execution_time=timedelta(seconds=10)
        )
        
        result = mock_arbitrage_strategy._validate_opportunity(opportunity)
        assert result is False
    
    def test_performance_metrics(self, mock_arbitrage_strategy):
        """Test performance metrics collection."""
        # Simulate some activity
        mock_arbitrage_strategy.successful_arbitrages = 5
        mock_arbitrage_strategy.failed_arbitrages = 2
        mock_arbitrage_strategy.total_arbitrage_profit = Decimal('500')
        
        metrics = mock_arbitrage_strategy.get_performance_metrics()
        
        assert metrics['strategy_type'] == 'cross_market_arbitrage'
        assert metrics['successful_arbitrages'] == 5
        assert metrics['failed_arbitrages'] == 2
        assert metrics['arbitrage_success_rate'] == 5/7
        assert metrics['total_arbitrage_profit'] == 500.0
    
    def test_arbitrage_result_update_success(self, mock_arbitrage_strategy):
        """Test updating arbitrage results for successful execution."""
        opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD')],
            markets=['binance'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('1.0'),
            execution_path=[],
            risk_factors=[],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            minimum_capital=Decimal('1000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        mock_arbitrage_strategy.active_opportunities.append(opportunity)
        
        mock_arbitrage_strategy.update_arbitrage_result(opportunity, True, Decimal('95'))
        
        assert mock_arbitrage_strategy.successful_arbitrages == 1
        assert mock_arbitrage_strategy.total_arbitrage_profit == Decimal('95')
        assert opportunity in mock_arbitrage_strategy.executed_opportunities
        assert opportunity not in mock_arbitrage_strategy.active_opportunities
    
    def test_arbitrage_result_update_failure(self, mock_arbitrage_strategy):
        """Test updating arbitrage results for failed execution."""
        opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD')],
            markets=['binance'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('1.0'),
            execution_path=[],
            risk_factors=[],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            minimum_capital=Decimal('1000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        mock_arbitrage_strategy.active_opportunities.append(opportunity)
        
        mock_arbitrage_strategy.update_arbitrage_result(opportunity, False)
        
        assert mock_arbitrage_strategy.failed_arbitrages == 1
        assert opportunity in mock_arbitrage_strategy.rejected_opportunities
        assert opportunity not in mock_arbitrage_strategy.active_opportunities


class TestCryptoForexArbitrageStrategy:
    """Test cases for the CryptoForexArbitrageStrategy class."""
    
    @pytest.fixture
    def crypto_forex_config(self):
        """Create a test configuration for crypto-forex arbitrage."""
        return StrategyConfig(
            name="crypto_forex_arbitrage",
            enabled=True,
            parameters={
                'min_profit_threshold': 0.005,
                'max_execution_time_seconds': 30,
                'max_position_size': 10000,
                'risk_tolerance': 'MEDIUM',
                'supported_crypto_currencies': ['BTC', 'ETH'],
                'supported_fiat_currencies': ['USD', 'EUR'],
                'max_conversion_spread': 0.002,
                'min_session_overlap_minutes': 30
            }
        )
    
    @pytest.fixture
    def crypto_forex_strategy(self, crypto_forex_config):
        """Create a crypto-forex arbitrage strategy."""
        return CryptoForexArbitrageStrategy(crypto_forex_config)
    
    @pytest.fixture
    def sample_crypto_data(self):
        """Create sample crypto market data."""
        return [
            UnifiedMarketData(
                symbol=UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD'),
                timestamp=datetime.now(),
                open=Decimal('50000'),
                high=Decimal('50100'),
                low=Decimal('49900'),
                close=Decimal('50050'),
                volume=Decimal('5000'),  # Higher volume
                source='binance',
                market_type=MarketType.CRYPTO
            )
        ]
    
    @pytest.fixture
    def sample_forex_data(self):
        """Create sample forex market data."""
        return [
            UnifiedMarketData(
                symbol=UnifiedSymbol('BTC', 'USD', MarketType.FOREX, 'BTCUSD'),
                timestamp=datetime.now(),
                open=Decimal('49500'),
                high=Decimal('49600'),
                low=Decimal('49400'),
                close=Decimal('49700'),  # Much lower than crypto price to create profitable arbitrage
                volume=Decimal('5000'),  # Higher volume
                source='oanda',
                market_type=MarketType.FOREX
            )
        ]
    
    def test_strategy_initialization(self, crypto_forex_strategy):
        """Test crypto-forex strategy initialization."""
        assert crypto_forex_strategy.name == "crypto_forex_arbitrage"
        assert crypto_forex_strategy.supported_crypto_currencies == ['BTC', 'ETH']
        assert crypto_forex_strategy.supported_fiat_currencies == ['USD', 'EUR']
        assert crypto_forex_strategy.max_conversion_spread == Decimal('0.002')
    
    def test_currency_mappings_initialization(self, crypto_forex_strategy):
        """Test currency pair mappings initialization."""
        mappings = crypto_forex_strategy.currency_pair_mappings
        
        assert 'BTC/USD' in mappings
        assert 'ETH/EUR' in mappings
        
        # Check direct mapping for BTC/USD
        btc_usd_mapping = mappings['BTC/USD']
        assert btc_usd_mapping['conversion_type'] == 'DIRECT'
        assert btc_usd_mapping['requires_conversion'] is False
    
    def test_group_data_by_symbol(self, crypto_forex_strategy, sample_crypto_data):
        """Test grouping data by symbol."""
        grouped = crypto_forex_strategy._group_data_by_symbol(sample_crypto_data)
        
        assert 'BTC/USD' in grouped
        assert len(grouped['BTC/USD']) == 1
        assert grouped['BTC/USD'][0].source == 'binance'
    
    def test_direct_arbitrage_opportunity_creation(self, crypto_forex_strategy, 
                                                  sample_crypto_data, sample_forex_data):
        """Test creation of direct arbitrage opportunity."""
        opportunity = crypto_forex_strategy._create_direct_arbitrage_opportunity(
            sample_crypto_data, sample_forex_data
        )
        
        assert opportunity is not None
        assert opportunity.opportunity_type == 'CRYPTO_FOREX'
        assert len(opportunity.symbols) == 2
        assert len(opportunity.markets) == 2
        assert opportunity.expected_profit > 0
        assert len(opportunity.execution_path) == 2
    
    def test_cross_market_fees_estimation(self, crypto_forex_strategy, 
                                         sample_crypto_data, sample_forex_data):
        """Test cross-market fees estimation."""
        crypto_data = sample_crypto_data[0]
        forex_data = sample_forex_data[0]
        
        fees = crypto_forex_strategy._estimate_cross_market_fees(crypto_data, forex_data)
        
        assert fees > 0
        assert isinstance(fees, Decimal)
    
    def test_crypto_forex_risk_assessment(self, crypto_forex_strategy, 
                                         sample_crypto_data, sample_forex_data):
        """Test crypto-forex risk assessment."""
        crypto_data = sample_crypto_data[0]
        forex_data = sample_forex_data[0]
        
        risks = crypto_forex_strategy._assess_crypto_forex_risks(crypto_data, forex_data)
        
        assert isinstance(risks, list)
        assert 'REGULATORY_RISK' in risks  # Always present
    
    def test_confidence_calculation(self, crypto_forex_strategy, 
                                   sample_crypto_data, sample_forex_data):
        """Test confidence calculation for crypto-forex arbitrage."""
        crypto_data = sample_crypto_data[0]
        forex_data = sample_forex_data[0]
        risk_factors = ['REGULATORY_RISK']
        
        confidence = crypto_forex_strategy._calculate_confidence(
            crypto_data, forex_data, risk_factors
        )
        
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)
    
    def test_parameter_validation_success(self, crypto_forex_strategy):
        """Test successful parameter validation."""
        result = crypto_forex_strategy.validate_parameters()
        assert result is True
    
    def test_parameter_validation_no_crypto_currencies(self, crypto_forex_config):
        """Test parameter validation with no crypto currencies."""
        crypto_forex_config.parameters['supported_crypto_currencies'] = []
        strategy = CryptoForexArbitrageStrategy(crypto_forex_config)
        
        result = strategy.validate_parameters()
        assert result is False
    
    def test_parameter_validation_invalid_conversion_spread(self, crypto_forex_config):
        """Test parameter validation with invalid conversion spread."""
        crypto_forex_config.parameters['max_conversion_spread'] = 0.02  # Too high
        strategy = CryptoForexArbitrageStrategy(crypto_forex_config)
        
        result = strategy.validate_parameters()
        assert result is False


class TestTriangularArbitrageStrategy:
    """Test cases for the TriangularArbitrageStrategy class."""
    
    @pytest.fixture
    def triangular_config(self):
        """Create a test configuration for triangular arbitrage."""
        return StrategyConfig(
            name="triangular_arbitrage",
            enabled=True,
            parameters={
                'min_profit_threshold': 0.005,
                'max_execution_time_seconds': 30,
                'max_position_size': 10000,
                'risk_tolerance': 'MEDIUM',
                'base_currencies': ['USD', 'BTC', 'ETH'],
                'min_triangle_volume': 5000,
                'max_step_delay_seconds': 2,
                'triangle_expiry_seconds': 15,
                'preferred_markets': ['binance', 'coinbase']
            }
        )
    
    @pytest.fixture
    def triangular_strategy(self, triangular_config):
        """Create a triangular arbitrage strategy."""
        return TriangularArbitrageStrategy(triangular_config)
    
    @pytest.fixture
    def triangle_market_data(self):
        """Create sample market data for triangular arbitrage."""
        return [
            UnifiedMarketData(
                symbol=UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD'),
                timestamp=datetime.now(),
                open=Decimal('50000'),
                high=Decimal('50100'),
                low=Decimal('49900'),
                close=Decimal('50000'),
                volume=Decimal('10000'),
                source='binance',
                market_type=MarketType.CRYPTO
            ),
            UnifiedMarketData(
                symbol=UnifiedSymbol('ETH', 'USD', MarketType.CRYPTO, 'ETHUSD'),
                timestamp=datetime.now(),
                open=Decimal('3000'),
                high=Decimal('3010'),
                low=Decimal('2990'),
                close=Decimal('3000'),
                volume=Decimal('10000'),
                source='binance',
                market_type=MarketType.CRYPTO
            ),
            UnifiedMarketData(
                symbol=UnifiedSymbol('ETH', 'BTC', MarketType.CRYPTO, 'ETHBTC'),
                timestamp=datetime.now(),
                open=Decimal('0.06'),
                high=Decimal('0.061'),
                low=Decimal('0.059'),
                close=Decimal('0.06'),  # This creates a triangular opportunity
                volume=Decimal('10000'),
                source='binance',
                market_type=MarketType.CRYPTO
            )
        ]
    
    def test_strategy_initialization(self, triangular_strategy):
        """Test triangular strategy initialization."""
        assert triangular_strategy.name == "triangular_arbitrage"
        assert triangular_strategy.base_currencies == ['USD', 'BTC', 'ETH']
        assert triangular_strategy.min_triangle_volume == Decimal('5000')
        assert triangular_strategy.max_step_delay == timedelta(seconds=2)
        assert triangular_strategy.preferred_markets == ['binance', 'coinbase']
    
    def test_group_data_by_market(self, triangular_strategy, triangle_market_data):
        """Test grouping data by market."""
        grouped = triangular_strategy._group_data_by_market(triangle_market_data)
        
        assert 'binance' in grouped
        assert len(grouped['binance']) == 3
    
    def test_find_pair_direct(self, triangular_strategy, triangle_market_data):
        """Test finding currency pair (direct)."""
        available_pairs = {
            'BTC/USD': ('BTC', 'USD'),
            'ETH/USD': ('ETH', 'USD'),
            'ETH/BTC': ('ETH', 'BTC')
        }
        symbol_data = {data.symbol.to_standard_format(): data for data in triangle_market_data}
        
        pair = triangular_strategy._find_pair('BTC', 'USD', available_pairs, symbol_data)
        
        assert pair is not None
        assert pair['symbol'] == 'BTC/USD'
        assert pair['base'] == 'BTC'
        assert pair['quote'] == 'USD'
        assert pair['inverted'] is False
    
    def test_find_pair_inverted(self, triangular_strategy, triangle_market_data):
        """Test finding currency pair (inverted)."""
        available_pairs = {
            'BTC/USD': ('BTC', 'USD'),
            'ETH/USD': ('ETH', 'USD'),
            'ETH/BTC': ('ETH', 'BTC')
        }
        symbol_data = {data.symbol.to_standard_format(): data for data in triangle_market_data}
        
        pair = triangular_strategy._find_pair('USD', 'BTC', available_pairs, symbol_data)
        
        assert pair is not None
        assert pair['symbol'] == 'BTC/USD'
        assert pair['base'] == 'BTC'
        assert pair['quote'] == 'USD'
        assert pair['inverted'] is True
    
    def test_calculate_implied_rate(self, triangular_strategy, triangle_market_data):
        """Test implied rate calculation."""
        # BTC/USD = 50000, ETH/BTC = 0.06
        # Implied ETH/USD = 50000 * 0.06 = 3000
        
        pair1 = {'symbol': 'BTC/USD', 'inverted': False}
        pair2 = {'symbol': 'ETH/BTC', 'inverted': False}
        
        data1 = triangle_market_data[0]  # BTC/USD
        data2 = triangle_market_data[2]  # ETH/BTC
        
        implied_rate = triangular_strategy._calculate_implied_rate(pair1, pair2, data1, data2)
        
        assert implied_rate is not None
        assert implied_rate == Decimal('3000')  # 50000 * 0.06
    
    def test_get_direct_rate(self, triangular_strategy, triangle_market_data):
        """Test direct rate extraction."""
        pair3 = {'symbol': 'ETH/USD', 'inverted': False}
        data3 = triangle_market_data[1]  # ETH/USD
        
        direct_rate = triangular_strategy._get_direct_rate(pair3, data3)
        
        assert direct_rate is not None
        assert direct_rate == Decimal('3000')
    
    def test_determine_execution_sequence(self, triangular_strategy):
        """Test execution sequence determination."""
        implied_rate = Decimal('3010')  # Higher than actual
        actual_rate = Decimal('3000')
        
        pair1 = {'symbol': 'BTC/USD'}
        pair2 = {'symbol': 'ETH/BTC'}
        pair3 = {'symbol': 'ETH/USD'}
        
        sequence = triangular_strategy._determine_execution_sequence(
            'USD', 'BTC', 'ETH', implied_rate, actual_rate, pair1, pair2, pair3
        )
        
        assert len(sequence) == 3
        assert all('BUY' in step or 'SELL' in step for step in sequence)
    
    def test_triangular_fees_estimation(self, triangular_strategy, triangle_market_data):
        """Test triangular fees estimation."""
        from src.analysis.arbitrage_detector import TriangularArbitrageChain
        
        chain = TriangularArbitrageChain(
            base_currency='USD',
            intermediate_currency='BTC',
            quote_currency='ETH',
            symbol1=triangle_market_data[0].symbol,
            symbol2=triangle_market_data[2].symbol,
            symbol3=triangle_market_data[1].symbol,
            market='binance',
            implied_rate=Decimal('3010'),
            actual_rate=Decimal('3000'),
            profit_opportunity=Decimal('10'),
            execution_sequence=['BUY BTC/USD', 'BUY ETH/BTC', 'SELL ETH/USD']
        )
        
        symbol_data = {data.symbol.to_standard_format(): data for data in triangle_market_data}
        
        fees = triangular_strategy._estimate_triangular_fees(chain, symbol_data)
        
        assert fees > 0
        assert isinstance(fees, Decimal)
    
    def test_triangular_slippage_estimation(self, triangular_strategy, triangle_market_data):
        """Test triangular slippage estimation."""
        from src.analysis.arbitrage_detector import TriangularArbitrageChain
        
        chain = TriangularArbitrageChain(
            base_currency='USD',
            intermediate_currency='BTC',
            quote_currency='ETH',
            symbol1=triangle_market_data[0].symbol,
            symbol2=triangle_market_data[2].symbol,
            symbol3=triangle_market_data[1].symbol,
            market='binance',
            implied_rate=Decimal('3010'),
            actual_rate=Decimal('3000'),
            profit_opportunity=Decimal('10'),
            execution_sequence=['BUY BTC/USD', 'BUY ETH/BTC', 'SELL ETH/USD']
        )
        
        symbol_data = {data.symbol.to_standard_format(): data for data in triangle_market_data}
        
        slippage = triangular_strategy._estimate_triangular_slippage(chain, symbol_data)
        
        assert slippage > 0
        assert isinstance(slippage, Decimal)
    
    def test_triangular_risk_assessment(self, triangular_strategy, triangle_market_data):
        """Test triangular risk assessment."""
        from src.analysis.arbitrage_detector import TriangularArbitrageChain
        
        chain = TriangularArbitrageChain(
            base_currency='USD',
            intermediate_currency='BTC',
            quote_currency='ETH',
            symbol1=triangle_market_data[0].symbol,
            symbol2=triangle_market_data[2].symbol,
            symbol3=triangle_market_data[1].symbol,
            market='binance',
            implied_rate=Decimal('3010'),
            actual_rate=Decimal('3000'),
            profit_opportunity=Decimal('10'),
            execution_sequence=['BUY BTC/USD', 'BUY ETH/BTC', 'SELL ETH/USD']
        )
        
        symbol_data = {data.symbol.to_standard_format(): data for data in triangle_market_data}
        
        risks = triangular_strategy._assess_triangular_risks(chain, symbol_data)
        
        assert isinstance(risks, list)
        assert 'MULTI_STEP_EXECUTION' in risks  # Always present
    
    def test_triangular_confidence_calculation(self, triangular_strategy, triangle_market_data):
        """Test triangular confidence calculation."""
        from src.analysis.arbitrage_detector import TriangularArbitrageChain
        
        chain = TriangularArbitrageChain(
            base_currency='USD',
            intermediate_currency='BTC',
            quote_currency='ETH',
            symbol1=triangle_market_data[0].symbol,
            symbol2=triangle_market_data[2].symbol,
            symbol3=triangle_market_data[1].symbol,
            market='binance',  # Preferred market
            implied_rate=Decimal('3010'),
            actual_rate=Decimal('3000'),
            profit_opportunity=Decimal('10'),
            execution_sequence=['BUY BTC/USD', 'BUY ETH/BTC', 'SELL ETH/USD']
        )
        
        symbol_data = {data.symbol.to_standard_format(): data for data in triangle_market_data}
        risk_factors = ['MULTI_STEP_EXECUTION']
        
        confidence = triangular_strategy._calculate_triangular_confidence(
            chain, symbol_data, risk_factors
        )
        
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)
    
    def test_triangle_success_rate_update(self, triangular_strategy):
        """Test triangle success rate update."""
        triangle_key = "USD-BTC-ETH"
        
        # Update with success
        triangular_strategy.update_triangle_success_rate(triangle_key, True)
        assert triangle_key in triangular_strategy.triangle_success_rate
        
        initial_rate = triangular_strategy.triangle_success_rate[triangle_key]
        
        # Update with failure
        triangular_strategy.update_triangle_success_rate(triangle_key, False)
        
        # Rate should decrease
        assert triangular_strategy.triangle_success_rate[triangle_key] < initial_rate
    
    def test_parameter_validation_success(self, triangular_strategy):
        """Test successful parameter validation."""
        result = triangular_strategy.validate_parameters()
        assert result is True
    
    def test_parameter_validation_no_base_currencies(self, triangular_config):
        """Test parameter validation with no base currencies."""
        triangular_config.parameters['base_currencies'] = []
        strategy = TriangularArbitrageStrategy(triangular_config)
        
        result = strategy.validate_parameters()
        assert result is False
    
    def test_parameter_validation_invalid_triangle_volume(self, triangular_config):
        """Test parameter validation with invalid triangle volume."""
        triangular_config.parameters['min_triangle_volume'] = -1000
        strategy = TriangularArbitrageStrategy(triangular_config)
        
        result = strategy.validate_parameters()
        assert result is False


class TestArbitrageSignal:
    """Test cases for the ArbitrageSignal class."""
    
    def test_arbitrage_signal_creation(self):
        """Test arbitrage signal creation."""
        opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD')],
            markets=['binance'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('1.0'),
            execution_path=[],
            risk_factors=[],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            minimum_capital=Decimal('1000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        execution_plan = {'test': 'plan'}
        risk_assessment = {'test': 'assessment'}
        
        signal = ArbitrageSignal(
            symbol='BTC/USD',
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name='test_strategy',
            opportunity=opportunity,
            execution_plan=execution_plan,
            risk_assessment=risk_assessment
        )
        
        assert signal.opportunity == opportunity
        assert signal.execution_plan == execution_plan
        assert signal.risk_assessment == risk_assessment
    
    def test_arbitrage_signal_validation_no_opportunity(self):
        """Test arbitrage signal validation with no opportunity."""
        with pytest.raises(ValueError, match="Arbitrage opportunity cannot be None"):
            ArbitrageSignal(
                symbol='BTC/USD',
                action=SignalAction.BUY,
                confidence=0.8,
                timestamp=datetime.now(),
                strategy_name='test_strategy',
                opportunity=None,
                execution_plan={'test': 'plan'},
                risk_assessment={'test': 'assessment'}
            )
    
    def test_arbitrage_signal_validation_empty_execution_plan(self):
        """Test arbitrage signal validation with empty execution plan."""
        opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTCUSD')],
            markets=['binance'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('1.0'),
            execution_path=[],
            risk_factors=[],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            minimum_capital=Decimal('1000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        with pytest.raises(ValueError, match="Execution plan cannot be empty"):
            ArbitrageSignal(
                symbol='BTC/USD',
                action=SignalAction.BUY,
                confidence=0.8,
                timestamp=datetime.now(),
                strategy_name='test_strategy',
                opportunity=opportunity,
                execution_plan={},
                risk_assessment={'test': 'assessment'}
            )


if __name__ == '__main__':
    pytest.main([__file__])