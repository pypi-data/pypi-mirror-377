"""
Unit tests for cross-market analysis capabilities.

Tests the correlation analyzer, arbitrage detector, and event analyzer
components for accuracy and reliability.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from src.analysis.correlation_analyzer import (
    CrossMarketCorrelationAnalyzer, CorrelationResult, CorrelationTrend, CorrelationRegime
)
from src.analysis.arbitrage_detector import (
    ArbitrageDetector, ArbitrageOpportunity, PriceDiscrepancy, TriangularArbitrageChain
)
from src.analysis.event_analyzer import (
    CrossMarketEventAnalyzer, MarketEvent, CrossMarketImpact, EventType, EventSeverity
)
from src.models.data_models import UnifiedMarketData, Position, OrderSide
from src.markets.types import MarketType, UnifiedSymbol
from src.data.cross_market_store import CrossMarketDataStore


class TestCrossMarketCorrelationAnalyzer:
    """Test cases for CrossMarketCorrelationAnalyzer."""
    
    @pytest.fixture
    def mock_data_store(self):
        """Create mock data store."""
        return Mock(spec=CrossMarketDataStore)
    
    @pytest.fixture
    def analyzer_config(self):
        """Configuration for correlation analyzer."""
        return {
            'min_observations': 10,
            'significance_level': 0.05,
            'rolling_window_days': 30,
            'trend_detection_periods': 5
        }
    
    @pytest.fixture
    def correlation_analyzer(self, mock_data_store, analyzer_config):
        """Create correlation analyzer instance."""
        return CrossMarketCorrelationAnalyzer(mock_data_store, analyzer_config)
    
    @pytest.fixture
    def sample_symbols(self):
        """Create sample unified symbols."""
        btc_symbol = UnifiedSymbol(
            base_asset='BTC',
            quote_asset='USD',
            market_type=MarketType.CRYPTO,
            native_symbol='BTCUSD'
        )
        
        eur_symbol = UnifiedSymbol(
            base_asset='EUR',
            quote_asset='USD',
            market_type=MarketType.FOREX,
            native_symbol='EURUSD'
        )
        
        return btc_symbol, eur_symbol
    
    @pytest.fixture
    def sample_market_data(self, sample_symbols):
        """Create sample market data."""
        btc_symbol, eur_symbol = sample_symbols
        
        # Generate correlated price data
        base_time = datetime.now() - timedelta(days=30)
        btc_data = []
        eur_data = []
        
        for i in range(50):
            timestamp = base_time + timedelta(hours=i)
            
            # Generate correlated prices (correlation ~0.7)
            btc_price = 50000 + 1000 * np.sin(i * 0.1) + np.random.normal(0, 500)
            eur_price = 1.1 + 0.05 * np.sin(i * 0.1) + np.random.normal(0, 0.01)
            
            btc_data.append(UnifiedMarketData(
                symbol=btc_symbol,
                timestamp=timestamp,
                open=Decimal(str(btc_price * 0.999)),
                high=Decimal(str(btc_price * 1.002)),
                low=Decimal(str(btc_price * 0.998)),
                close=Decimal(str(btc_price)),
                volume=Decimal('1000'),
                source='test_exchange',
                market_type=MarketType.CRYPTO
            ))
            
            eur_data.append(UnifiedMarketData(
                symbol=eur_symbol,
                timestamp=timestamp,
                open=Decimal(str(eur_price * 0.9999)),
                high=Decimal(str(eur_price * 1.0002)),
                low=Decimal(str(eur_price * 0.9998)),
                close=Decimal(str(eur_price)),
                volume=Decimal('10000'),
                source='test_broker',
                market_type=MarketType.FOREX
            ))
        
        return btc_data, eur_data
    
    @pytest.mark.asyncio
    async def test_analyze_correlation_basic(self, correlation_analyzer, sample_symbols, sample_market_data):
        """Test basic correlation analysis."""
        btc_symbol, eur_symbol = sample_symbols
        btc_data, eur_data = sample_market_data
        
        # Mock data store responses
        correlation_analyzer.data_store.get_unified_data = AsyncMock()
        correlation_analyzer.data_store.get_unified_data.side_effect = [btc_data, eur_data]
        correlation_analyzer.data_store.store_correlation_data = AsyncMock(return_value=True)
        
        # Analyze correlation
        result = await correlation_analyzer.analyze_correlation(btc_symbol, eur_symbol)
        
        # Verify result
        assert result is not None
        assert isinstance(result, CorrelationResult)
        assert result.symbol1 == btc_symbol
        assert result.symbol2 == eur_symbol
        assert -1.0 <= result.pearson_correlation <= 1.0
        assert -1.0 <= result.spearman_correlation <= 1.0
        assert 0.0 <= result.p_value <= 1.0
        assert result.sample_size > 0
        assert result.correlation_strength in ['NEGLIGIBLE', 'WEAK', 'MODERATE', 'STRONG', 'VERY_STRONG']
    
    @pytest.mark.asyncio
    async def test_analyze_correlation_insufficient_data(self, correlation_analyzer, sample_symbols):
        """Test correlation analysis with insufficient data."""
        btc_symbol, eur_symbol = sample_symbols
        
        # Mock insufficient data
        correlation_analyzer.data_store.get_unified_data = AsyncMock()
        correlation_analyzer.data_store.get_unified_data.side_effect = [[], []]
        
        # Analyze correlation
        result = await correlation_analyzer.analyze_correlation(btc_symbol, eur_symbol)
        
        # Should return None for insufficient data
        assert result is None
    
    @pytest.mark.asyncio
    async def test_analyze_correlation_matrix(self, correlation_analyzer, sample_symbols, sample_market_data):
        """Test correlation matrix calculation."""
        btc_symbol, eur_symbol = sample_symbols
        btc_data, eur_data = sample_market_data
        symbols = [btc_symbol, eur_symbol]
        
        # Mock correlation analysis
        with patch.object(correlation_analyzer, 'analyze_correlation') as mock_analyze:
            mock_result = CorrelationResult(
                symbol1=btc_symbol,
                symbol2=eur_symbol,
                pearson_correlation=0.7,
                spearman_correlation=0.65,
                p_value=0.01,
                confidence_interval=(0.5, 0.85),
                sample_size=50,
                time_period=timedelta(days=30),
                calculated_at=datetime.now(),
                is_significant=True,
                correlation_strength='STRONG'
            )
            mock_analyze.return_value = mock_result
            
            # Calculate matrix
            matrix = await correlation_analyzer.analyze_correlation_matrix(symbols)
            
            # Verify matrix structure
            assert len(matrix) == 2
            assert btc_symbol.to_standard_format() in matrix
            assert eur_symbol.to_standard_format() in matrix
            
            # Self-correlations should be 1.0
            assert matrix[btc_symbol.to_standard_format()][btc_symbol.to_standard_format()] == 1.0
            assert matrix[eur_symbol.to_standard_format()][eur_symbol.to_standard_format()] == 1.0
            
            # Cross-correlations should match
            btc_key = btc_symbol.to_standard_format()
            eur_key = eur_symbol.to_standard_format()
            assert matrix[btc_key][eur_key] == matrix[eur_key][btc_key]
    
    @pytest.mark.asyncio
    async def test_detect_correlation_trends(self, correlation_analyzer, sample_symbols, sample_market_data):
        """Test correlation trend detection."""
        btc_symbol, eur_symbol = sample_symbols
        btc_data, eur_data = sample_market_data
        
        # Mock data store to return data for different time windows
        correlation_analyzer.data_store.get_unified_data = AsyncMock()
        correlation_analyzer.data_store.get_unified_data.side_effect = lambda symbol, start, end: (
            btc_data[:20] if symbol == btc_symbol else eur_data[:20]
        )
        
        # Detect trends
        trend = await correlation_analyzer.detect_correlation_trends(btc_symbol, eur_symbol)
        
        # Verify trend result
        if trend:  # May be None if insufficient data
            assert isinstance(trend, CorrelationTrend)
            assert trend.symbol_pair == (btc_symbol, eur_symbol)
            assert trend.trend_direction in ['INCREASING', 'DECREASING', 'STABLE']
            assert len(trend.rolling_correlations) > 0
            assert len(trend.time_windows) == len(trend.rolling_correlations)
    
    def test_calculate_correlation_adjusted_position_size(self, correlation_analyzer, sample_symbols):
        """Test correlation-adjusted position sizing."""
        btc_symbol, eur_symbol = sample_symbols
        
        # Add mock correlation to cache
        cache_key = tuple(sorted([
            btc_symbol.to_standard_format(),
            eur_symbol.to_standard_format()
        ]))
        
        mock_result = CorrelationResult(
            symbol1=btc_symbol,
            symbol2=eur_symbol,
            pearson_correlation=0.8,  # High correlation
            spearman_correlation=0.75,
            p_value=0.01,
            confidence_interval=(0.6, 0.9),
            sample_size=50,
            time_period=timedelta(days=30),
            calculated_at=datetime.now(),
            is_significant=True,
            correlation_strength='VERY_STRONG'
        )
        
        correlation_analyzer.correlation_cache[cache_key] = mock_result
        
        # Calculate adjusted position size
        base_size = 1000.0
        portfolio_symbols = [eur_symbol]
        
        adjusted_size = correlation_analyzer.calculate_correlation_adjusted_position_size(
            base_size, btc_symbol, portfolio_symbols
        )
        
        # Should be reduced due to high correlation
        assert adjusted_size < base_size
        assert adjusted_size > 0
    
    def test_get_correlation_insights(self, correlation_analyzer, sample_symbols):
        """Test correlation insights generation."""
        btc_symbol, eur_symbol = sample_symbols
        symbols = [btc_symbol, eur_symbol]
        
        # Add mock data to cache
        cache_key = tuple(sorted([
            btc_symbol.to_standard_format(),
            eur_symbol.to_standard_format()
        ]))
        
        mock_result = CorrelationResult(
            symbol1=btc_symbol,
            symbol2=eur_symbol,
            pearson_correlation=0.85,
            spearman_correlation=0.8,
            p_value=0.001,
            confidence_interval=(0.7, 0.95),
            sample_size=100,
            time_period=timedelta(days=30),
            calculated_at=datetime.now(),
            is_significant=True,
            correlation_strength='VERY_STRONG'
        )
        
        correlation_analyzer.correlation_cache[cache_key] = mock_result
        
        # Get insights
        insights = correlation_analyzer.get_correlation_insights(symbols)
        
        # Verify insights structure
        assert 'total_symbols' in insights
        assert 'high_correlations' in insights
        assert 'negative_correlations' in insights
        assert 'diversification_score' in insights
        
        assert insights['total_symbols'] == 2
        assert len(insights['high_correlations']) > 0  # Should detect high correlation
        assert 0.0 <= insights['diversification_score'] <= 1.0


class TestArbitrageDetector:
    """Test cases for ArbitrageDetector."""
    
    @pytest.fixture
    def mock_data_store(self):
        """Create mock data store."""
        return Mock(spec=CrossMarketDataStore)
    
    @pytest.fixture
    def detector_config(self):
        """Configuration for arbitrage detector."""
        return {
            'min_profit_threshold': 0.001,
            'max_execution_time_seconds': 30,
            'min_volume_threshold': 1000,
            'max_spread_age_seconds': 10,
            'max_slippage': 0.002,
            'execution_delay_penalty': 0.0005,
            'market_fees': {
                'exchange1': 0.001,
                'exchange2': 0.0015
            },
            'market_latencies': {
                'exchange1': 0.1,
                'exchange2': 0.15
            }
        }
    
    @pytest.fixture
    def arbitrage_detector(self, mock_data_store, detector_config):
        """Create arbitrage detector instance."""
        return ArbitrageDetector(mock_data_store, detector_config)
    
    @pytest.fixture
    def sample_symbol(self):
        """Create sample symbol."""
        return UnifiedSymbol(
            base_asset='BTC',
            quote_asset='USD',
            market_type=MarketType.CRYPTO,
            native_symbol='BTCUSD'
        )
    
    @pytest.fixture
    def sample_price_data(self, sample_symbol):
        """Create sample price data with discrepancy."""
        timestamp = datetime.now()
        
        # Price data from two different exchanges
        data1 = UnifiedMarketData(
            symbol=sample_symbol,
            timestamp=timestamp,
            open=Decimal('49900'),
            high=Decimal('50100'),
            low=Decimal('49800'),
            close=Decimal('50000'),  # Lower price
            volume=Decimal('10000'),
            source='exchange1',
            market_type=MarketType.CRYPTO
        )
        
        data2 = UnifiedMarketData(
            symbol=sample_symbol,
            timestamp=timestamp,
            open=Decimal('50650'),
            high=Decimal('50750'),
            low=Decimal('50550'),
            close=Decimal('50700'),  # Higher price - 1.4% arbitrage opportunity
            volume=Decimal('8000'),
            source='exchange2',
            market_type=MarketType.CRYPTO
        )
        
        return [data1, data2]
    
    @pytest.mark.asyncio
    async def test_detect_simple_arbitrage(self, arbitrage_detector, sample_symbol, sample_price_data):
        """Test simple arbitrage detection."""
        # Mock data store
        arbitrage_detector.data_store.get_latest_data = AsyncMock()
        arbitrage_detector.data_store.get_latest_data.side_effect = sample_price_data
        
        # Mock _get_latest_prices_all_sources to return both price points
        with patch.object(arbitrage_detector, '_get_latest_prices_all_sources') as mock_get_prices:
            mock_get_prices.return_value = sample_price_data
            
            # Detect arbitrage
            opportunities = await arbitrage_detector.detect_simple_arbitrage([sample_symbol])
            
            # Should detect arbitrage opportunity
            assert len(opportunities) > 0
            
            opportunity = opportunities[0]
            assert isinstance(opportunity, ArbitrageOpportunity)
            assert opportunity.opportunity_type == 'SIMPLE'
            assert opportunity.expected_profit > 0
            assert len(opportunity.execution_path) == 2  # Buy and sell steps
            assert opportunity.execution_path[0]['action'] == 'BUY'
            assert opportunity.execution_path[1]['action'] == 'SELL'
    
    def test_find_price_discrepancies(self, arbitrage_detector, sample_symbol, sample_price_data):
        """Test price discrepancy detection."""
        discrepancies = arbitrage_detector._find_price_discrepancies(sample_symbol, sample_price_data)
        
        # Should find one discrepancy
        assert len(discrepancies) == 1
        
        discrepancy = discrepancies[0]
        assert isinstance(discrepancy, PriceDiscrepancy)
        assert discrepancy.symbol == sample_symbol
        assert discrepancy.spread > 0
        assert discrepancy.spread_percentage > 0
        assert discrepancy.is_actionable  # Should be actionable given the spread
    
    @pytest.mark.asyncio
    async def test_create_simple_arbitrage_opportunity(self, arbitrage_detector, sample_price_data):
        """Test arbitrage opportunity creation."""
        # Create discrepancy from sample data
        discrepancy = PriceDiscrepancy(
            symbol=sample_price_data[0].symbol,
            market1='exchange1',
            market2='exchange2',
            price1=sample_price_data[0].close,
            price2=sample_price_data[1].close,
            spread=sample_price_data[1].close - sample_price_data[0].close,
            spread_percentage=float((sample_price_data[1].close - sample_price_data[0].close) / sample_price_data[0].close * 100),
            volume1=sample_price_data[0].volume,
            volume2=sample_price_data[1].volume,
            detected_at=datetime.now(),
            is_actionable=True
        )
        
        # Create opportunity
        opportunity = await arbitrage_detector._create_simple_arbitrage_opportunity(discrepancy)
        
        # Verify opportunity
        assert opportunity is not None
        assert isinstance(opportunity, ArbitrageOpportunity)
        assert opportunity.opportunity_type == 'SIMPLE'
        assert opportunity.expected_profit > 0
        assert len(opportunity.execution_path) == 2
        assert len(opportunity.markets) == 2
    
    def test_get_opportunity_summary(self, arbitrage_detector):
        """Test opportunity summary generation."""
        # Add mock opportunities
        mock_opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[],
            markets=['exchange1', 'exchange2'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('0.2'),
            execution_path=[],
            risk_factors=[],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=5),
            minimum_capital=Decimal('10000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        arbitrage_detector.active_opportunities = [mock_opportunity]
        
        # Get summary
        summary = arbitrage_detector.get_opportunity_summary()
        
        # Verify summary
        assert 'total_opportunities' in summary
        assert 'simple_arbitrage' in summary
        assert 'total_potential_profit' in summary
        assert 'urgency_breakdown' in summary
        
        assert summary['total_opportunities'] == 1
        assert summary['simple_arbitrage'] == 1
        assert summary['total_potential_profit'] == 100.0
    
    def test_get_execution_plan(self, arbitrage_detector):
        """Test execution plan generation."""
        # Create mock opportunity
        mock_opportunity = ArbitrageOpportunity(
            opportunity_type='SIMPLE',
            symbols=[],
            markets=['exchange1', 'exchange2'],
            expected_profit=Decimal('100'),
            profit_percentage=Decimal('0.2'),
            execution_path=[
                {
                    'action': 'BUY',
                    'symbol': 'BTC/USD',
                    'market': 'exchange1',
                    'amount': 0.1,
                    'expected_price': 50000,
                    'timing': 'IMMEDIATE'
                },
                {
                    'action': 'SELL',
                    'symbol': 'BTC/USD',
                    'market': 'exchange2',
                    'amount': 0.1,
                    'expected_price': 50200,
                    'timing': 'IMMEDIATE',
                    'dependencies': ['step_1']
                }
            ],
            risk_factors=['LOW_SPREAD_MARGIN'],
            confidence=0.8,
            time_sensitivity='HIGH',
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=5),
            minimum_capital=Decimal('5000'),
            estimated_execution_time=timedelta(seconds=10)
        )
        
        # Get execution plan
        plan = arbitrage_detector.get_execution_plan(mock_opportunity)
        
        # Verify plan structure
        assert 'opportunity_id' in plan
        assert 'type' in plan
        assert 'expected_profit' in plan
        assert 'steps' in plan
        assert 'risk_assessment' in plan
        assert 'market_conditions' in plan
        
        assert len(plan['steps']) == 2
        assert plan['type'] == 'SIMPLE'
        assert plan['expected_profit'] == 100.0


class TestCrossMarketEventAnalyzer:
    """Test cases for CrossMarketEventAnalyzer."""
    
    @pytest.fixture
    def mock_data_store(self):
        """Create mock data store."""
        return Mock(spec=CrossMarketDataStore)
    
    @pytest.fixture
    def analyzer_config(self):
        """Configuration for event analyzer."""
        return {
            'price_spike_threshold': 0.05,
            'volume_surge_threshold': 3.0,
            'volatility_threshold': 2.0,
            'correlation_breakdown_threshold': 0.3
        }
    
    @pytest.fixture
    def event_analyzer(self, mock_data_store, analyzer_config):
        """Create event analyzer instance."""
        return CrossMarketEventAnalyzer(mock_data_store, analyzer_config)
    
    @pytest.fixture
    def sample_symbol(self):
        """Create sample symbol."""
        return UnifiedSymbol(
            base_asset='BTC',
            quote_asset='USD',
            market_type=MarketType.CRYPTO,
            native_symbol='BTCUSD'
        )
    
    @pytest.fixture
    def spike_data(self, sample_symbol):
        """Create data with price spike."""
        base_time = datetime.now() - timedelta(hours=1)
        data = []
        
        # Normal prices, then spike
        for i in range(20):
            timestamp = base_time + timedelta(minutes=i * 3)
            
            if i < 15:
                price = 50000 + (i * 10)  # Gradual increase
            else:
                price = 50000 * 1.08 + (i * 10)  # 8% spike
            
            data.append(UnifiedMarketData(
                symbol=sample_symbol,
                timestamp=timestamp,
                open=Decimal(str(price * 0.999)),
                high=Decimal(str(price * 1.001)),
                low=Decimal(str(price * 0.998)),
                close=Decimal(str(price)),
                volume=Decimal('1000'),
                source='test_exchange',
                market_type=MarketType.CRYPTO
            ))
        
        return data
    
    @pytest.fixture
    def volume_surge_data(self, sample_symbol):
        """Create data with volume surge."""
        base_time = datetime.now() - timedelta(hours=1)
        data = []
        
        # Normal volume, then surge
        for i in range(20):
            timestamp = base_time + timedelta(minutes=i * 3)
            price = 50000 + (i * 10)
            
            if i < 15:
                volume = 1000 + (i * 2)  # Normal volume, gradual increase
            else:
                volume = 8000 + (i * 20)  # 8x volume surge
            
            data.append(UnifiedMarketData(
                symbol=sample_symbol,
                timestamp=timestamp,
                open=Decimal(str(price * 0.999)),
                high=Decimal(str(price * 1.001)),
                low=Decimal(str(price * 0.998)),
                close=Decimal(str(price)),
                volume=Decimal(str(max(volume, 100))),  # Ensure positive volume
                source='test_exchange',
                market_type=MarketType.CRYPTO
            ))
        
        return data
    
    @pytest.mark.asyncio
    async def test_detect_price_events(self, event_analyzer, sample_symbol, spike_data):
        """Test price event detection."""
        events = await event_analyzer._detect_price_events(sample_symbol, spike_data)
        
        # Should detect price spike
        assert len(events) > 0
        
        event = events[0]
        assert isinstance(event, MarketEvent)
        assert event.event_type == EventType.PRICE_SPIKE
        assert event.source_symbol == sample_symbol
        assert event.severity in [EventSeverity.MEDIUM, EventSeverity.HIGH]
        assert 'price_change' in event.event_data
    
    @pytest.mark.asyncio
    async def test_detect_volume_events(self, event_analyzer, sample_symbol, volume_surge_data):
        """Test volume event detection."""
        events = await event_analyzer._detect_volume_events(sample_symbol, volume_surge_data)
        
        # Should detect volume surge
        assert len(events) > 0
        
        event = events[0]
        assert isinstance(event, MarketEvent)
        assert event.event_type == EventType.VOLUME_SURGE
        assert event.source_symbol == sample_symbol
        assert 'volume_ratio' in event.event_data
        assert event.event_data['volume_ratio'] > event_analyzer.volume_surge_threshold
    
    @pytest.mark.asyncio
    async def test_detect_events(self, event_analyzer, sample_symbol, spike_data):
        """Test comprehensive event detection."""
        # Mock data store
        event_analyzer.data_store.get_unified_data = AsyncMock(return_value=spike_data)
        
        # Detect events
        events = await event_analyzer.detect_events([sample_symbol])
        
        # Should detect events
        assert len(events) > 0
        
        # Events should be stored in recent_events
        assert len(event_analyzer.recent_events) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_cross_market_impact(self, event_analyzer, sample_symbol):
        """Test cross-market impact analysis."""
        # Create mock event
        event = MarketEvent(
            event_id='test_event',
            event_type=EventType.PRICE_SPIKE,
            severity=EventSeverity.HIGH,
            source_market=MarketType.CRYPTO,
            source_symbol=sample_symbol,
            detected_at=datetime.now(),
            event_data={'price_change': 0.08},
            description='Test price spike',
            confidence=0.9
        )
        
        # Create target symbol
        target_symbol = UnifiedSymbol(
            base_asset='EUR',
            quote_asset='USD',
            market_type=MarketType.FOREX,
            native_symbol='EURUSD'
        )
        
        # Mock data for impact analysis
        pre_event_data = []
        post_event_data = []
        
        base_time = event.detected_at
        for i in range(10):
            # Pre-event data (stable)
            pre_event_data.append(UnifiedMarketData(
                symbol=target_symbol,
                timestamp=base_time - timedelta(minutes=60-i*5),
                open=Decimal('1.1000'),
                high=Decimal('1.1005'),
                low=Decimal('1.0995'),
                close=Decimal('1.1000'),
                volume=Decimal('10000'),
                source='test_broker',
                market_type=MarketType.FOREX
            ))
            
            # Post-event data (showing impact)
            impact_price = 1.1000 * (1 + 0.02)  # 2% impact
            post_event_data.append(UnifiedMarketData(
                symbol=target_symbol,
                timestamp=base_time + timedelta(minutes=i*5),
                open=Decimal(str(impact_price * 0.9999)),
                high=Decimal(str(impact_price * 1.0005)),
                low=Decimal(str(impact_price * 0.9995)),
                close=Decimal(str(impact_price)),
                volume=Decimal('12000'),
                source='test_broker',
                market_type=MarketType.FOREX
            ))
        
        # Mock data store
        event_analyzer.data_store.get_unified_data = AsyncMock()
        event_analyzer.data_store.get_unified_data.side_effect = [pre_event_data, post_event_data]
        
        # Analyze impact
        impacts = await event_analyzer.analyze_cross_market_impact(event, [target_symbol])
        
        # Should detect impact
        assert len(impacts) > 0
        
        impact = impacts[0]
        assert isinstance(impact, CrossMarketImpact)
        assert impact.source_event == event
        assert impact.affected_market == MarketType.FOREX
        assert target_symbol in impact.affected_symbols
        assert impact.impact_magnitude != 0  # Should detect some impact
    
    def test_get_event_summary(self, event_analyzer):
        """Test event summary generation."""
        # Add mock events
        mock_event = MarketEvent(
            event_id='test_event',
            event_type=EventType.PRICE_SPIKE,
            severity=EventSeverity.HIGH,
            source_market=MarketType.CRYPTO,
            source_symbol=Mock(),
            detected_at=datetime.now(),
            event_data={},
            description='Test event',
            confidence=0.9
        )
        
        event_analyzer.recent_events.append(mock_event)
        
        # Get summary
        summary = event_analyzer.get_event_summary()
        
        # Verify summary structure
        assert 'recent_events_24h' in summary
        assert 'event_breakdown' in summary
        assert 'severity_breakdown' in summary
        assert 'market_breakdown' in summary
        assert 'total_tracked_impacts' in summary
        assert 'active_alerts' in summary
        
        assert summary['recent_events_24h'] == 1
        assert 'PRICE_SPIKE' in summary['event_breakdown']
        assert 'HIGH' in summary['severity_breakdown']
        assert 'crypto' in summary['market_breakdown']
    
    @pytest.mark.asyncio
    async def test_generate_event_alerts(self, event_analyzer, sample_symbol):
        """Test event alert generation."""
        # Create significant event
        event = MarketEvent(
            event_id='test_alert_event',
            event_type=EventType.PRICE_SPIKE,
            severity=EventSeverity.HIGH,
            source_market=MarketType.CRYPTO,
            source_symbol=sample_symbol,
            detected_at=datetime.now(),
            event_data={'price_change': 0.1},  # 10% spike
            description='Major price spike',
            confidence=0.95
        )
        
        # Mock predict_event_impact
        mock_impact = CrossMarketImpact(
            source_event=event,
            affected_market=MarketType.FOREX,
            affected_symbols=[sample_symbol],
            impact_magnitude=0.05,  # 5% impact
            impact_direction='POSITIVE',
            propagation_delay=timedelta(minutes=5),
            duration=timedelta(minutes=30),
            confidence=0.8,
            impact_metrics={}
        )
        
        with patch.object(event_analyzer, 'predict_event_impact') as mock_predict:
            mock_predict.return_value = [mock_impact]
            
            # Generate alerts
            alerts = await event_analyzer.generate_event_alerts([event], [sample_symbol])
            
            # Should generate alert for significant event
            assert len(alerts) > 0
            
            alert = alerts[0]
            assert alert.event == event
            assert len(alert.predicted_impacts) > 0
            assert len(alert.recommended_actions) > 0
            assert alert.urgency in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']


if __name__ == '__main__':
    pytest.main([__file__])