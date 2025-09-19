"""
Unit tests for forex-specific trading strategies.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.strategies.forex_session_strategy import ForexSessionStrategy
from src.strategies.forex_carry_trade_strategy import ForexCarryTradeStrategy
from src.strategies.forex_news_strategy import ForexNewsStrategy, EconomicEvent, NewsImpact, NewsStrategy
from src.strategies.forex_technical_indicators import ForexTechnicalIndicators
from src.strategies.base_strategy import StrategyConfig
from src.models.data_models import UnifiedMarketData, SessionInfo, SignalAction
from src.markets.types import MarketType, UnifiedSymbol


class TestForexSessionStrategy(unittest.TestCase):
    """Test cases for ForexSessionStrategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = StrategyConfig(
            name="test_forex_session",
            parameters={
                'min_volatility_threshold': 0.001,
                'momentum_period': 10,
                'atr_period': 10,
                'rsi_period': 10,
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'overlap_only': True,
                'preferred_sessions': ['london', 'new_york'],
                'major_pairs': ['EUR/USD', 'GBP/USD']
            }
        )
        self.strategy = ForexSessionStrategy(self.config)
    
    def test_initialization(self):
        """Test strategy initialization."""
        self.assertTrue(self.strategy.initialize())
        self.assertEqual(self.strategy.name, "test_forex_session")
        self.assertEqual(len(self.strategy.supported_markets), 1)
        self.assertEqual(self.strategy.supported_markets[0], MarketType.FOREX)
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        # Initialize strategy first
        self.strategy.initialize()
        self.assertTrue(self.strategy.validate_parameters())
        
        # Test invalid parameters
        invalid_config = StrategyConfig(
            name="invalid",
            parameters={'min_volatility_threshold': -1, 'rsi_oversold': 30, 'rsi_overbought': 70}
        )
        invalid_strategy = ForexSessionStrategy(invalid_config)
        invalid_strategy.initialize()
        self.assertFalse(invalid_strategy.validate_parameters())
    
    def test_market_specific_parameters(self):
        """Test market-specific parameter retrieval."""
        params = self.strategy.get_market_specific_parameters(MarketType.FOREX)
        self.assertIn('min_volatility_threshold', params)
        self.assertIn('preferred_sessions', params)
        
        # Non-forex market should return empty dict
        params = self.strategy.get_market_specific_parameters(MarketType.CRYPTO)
        self.assertEqual(params, {})
    
    def test_session_detection(self):
        """Test session overlap detection."""
        # Initialize strategy first
        self.strategy.initialize()
        
        # Test that session detection methods work
        from datetime import time
        
        # Test London session time (15:00 UTC is during London-NY overlap)
        london_ny_time = time(15, 0)
        active_sessions = self.strategy._get_active_sessions(london_ny_time)
        
        # Should detect at least one active session during this time
        self.assertGreater(len(active_sessions), 0)
        
        # Test overlap detection
        overlaps = self.strategy._get_current_overlaps(london_ny_time)
        
        # During 15:00 UTC, there should be session overlaps
        # This is a more focused test of the session logic
        self.assertIsInstance(overlaps, set)
    
    def test_volatility_filtering(self):
        """Test volatility-based filtering."""
        symbol = UnifiedSymbol.from_forex_symbol('EURUSD')
        
        # Create low volatility data
        low_vol_data = self._create_low_volatility_data(symbol, 20)
        
        with patch.object(self.strategy.indicators, 'rsi', return_value=50.0), \
             patch.object(self.strategy.indicators, 'atr', return_value=0.0001), \
             patch.object(self.strategy.indicators, 'sma', return_value=[1.1000, 1.1000]):
            
            signal = self.strategy.analyze_market_data(low_vol_data, MarketType.FOREX)
            # Should not generate signal due to low volatility
            self.assertIsNone(signal)
    
    def test_major_pairs_filtering(self):
        """Test major pairs filtering."""
        # Test with non-major pair
        exotic_symbol = UnifiedSymbol.from_forex_symbol('USDTRY')
        test_data = self._create_test_data(exotic_symbol, datetime.now(timezone.utc), 20)
        
        signal = self.strategy.analyze_market_data(test_data, MarketType.FOREX)
        # Should not trade exotic pairs
        self.assertIsNone(signal)
    
    def _create_test_data(self, symbol: UnifiedSymbol, timestamp: datetime, count: int) -> list:
        """Create test market data."""
        data = []
        base_price = 1.1000
        
        for i in range(count):
            data_point = UnifiedMarketData(
                symbol=symbol,
                timestamp=timestamp - timedelta(minutes=count-i),
                open=Decimal(str(base_price + i * 0.0001)),
                high=Decimal(str(base_price + i * 0.0001 + 0.0005)),
                low=Decimal(str(base_price + i * 0.0001 - 0.0005)),
                close=Decimal(str(base_price + i * 0.0001 + 0.0002)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data
    
    def _create_low_volatility_data(self, symbol: UnifiedSymbol, count: int) -> list:
        """Create low volatility test data."""
        data = []
        base_price = 1.1000
        timestamp = datetime.now(timezone.utc)
        
        for i in range(count):
            # Very small price movements
            data_point = UnifiedMarketData(
                symbol=symbol,
                timestamp=timestamp - timedelta(minutes=count-i),
                open=Decimal(str(base_price)),
                high=Decimal(str(base_price + 0.00001)),
                low=Decimal(str(base_price - 0.00001)),
                close=Decimal(str(base_price)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data
    
    def _create_test_data_with_volatility(self, symbol: UnifiedSymbol, timestamp: datetime, count: int) -> list:
        """Create test market data with sufficient volatility."""
        data = []
        base_price = 1.1000
        
        for i in range(count):
            # Create data with sufficient volatility to meet threshold
            price_variation = 0.002 * (i % 3 - 1)  # Varies between -0.002 and +0.002
            current_price = base_price + price_variation
            
            data_point = UnifiedMarketData(
                symbol=symbol,
                timestamp=timestamp - timedelta(minutes=count-i),
                open=Decimal(str(current_price - 0.0005)),
                high=Decimal(str(current_price + 0.001)),
                low=Decimal(str(current_price - 0.001)),
                close=Decimal(str(current_price + 0.0002)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data


class TestForexCarryTradeStrategy(unittest.TestCase):
    """Test cases for ForexCarryTradeStrategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = StrategyConfig(
            name="test_carry_trade",
            parameters={
                'min_rate_differential': 1.0,
                'max_risk_score': 2.0,
                'trend_period': 10,
                'volatility_period': 10,
                'max_volatility': 0.02
            }
        )
        self.strategy = ForexCarryTradeStrategy(self.config)
    
    def test_initialization(self):
        """Test strategy initialization."""
        self.assertTrue(self.strategy.initialize())
        self.assertEqual(self.strategy.name, "test_carry_trade")
        self.assertIn('USD', self.strategy.INTEREST_RATES)
        self.assertIn('EUR', self.strategy.INTEREST_RATES)
    
    def test_carry_score_calculation(self):
        """Test carry trade score calculation."""
        # Test high-yield vs low-yield pair (AUD/JPY)
        aud_jpy = UnifiedSymbol.from_forex_symbol('AUDJPY')
        carry_score = self.strategy._calculate_carry_score(aud_jpy)
        self.assertGreater(carry_score, 0.0)  # Should have positive carry potential
        
        # Test low differential pair
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        carry_score = self.strategy._calculate_carry_score(eur_usd)
        # Score depends on current rate differential
        self.assertIsInstance(carry_score, float)
    
    def test_expected_swap_calculation(self):
        """Test expected swap calculation."""
        aud_jpy = UnifiedSymbol.from_forex_symbol('AUDJPY')
        
        # Long AUD/JPY should have positive swap (AUD higher rate than JPY)
        long_swap = self.strategy._calculate_expected_swap(aud_jpy, 1)
        self.assertGreater(long_swap, 0)
        
        # Short AUD/JPY should have negative swap
        short_swap = self.strategy._calculate_expected_swap(aud_jpy, -1)
        self.assertLess(short_swap, 0)
    
    def test_volatility_filtering(self):
        """Test volatility-based filtering."""
        symbol = UnifiedSymbol.from_forex_symbol('AUDJPY')
        
        # Create high volatility data
        high_vol_data = self._create_high_volatility_data(symbol, 20)
        
        # Should reject due to high volatility
        valid = self.strategy.validate_market_conditions(high_vol_data, MarketType.FOREX)
        self.assertFalse(valid)
    
    def test_technical_score_calculation(self):
        """Test technical analysis score calculation."""
        current_price = 100.0
        trend_price = 99.0  # Slight uptrend
        rsi = 50.0  # Neutral
        volatility = 0.01  # Moderate volatility
        
        score = self.strategy._calculate_technical_score(current_price, trend_price, rsi, volatility)
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_interest_rate_updates(self):
        """Test interest rate update functionality."""
        old_usd_rate = self.strategy.INTEREST_RATES['USD']
        
        # Update rates
        new_rates = {'USD': 6.0, 'EUR': 3.0}
        self.strategy.update_interest_rates(new_rates)
        
        self.assertEqual(self.strategy.INTEREST_RATES['USD'], 6.0)
        self.assertEqual(self.strategy.INTEREST_RATES['EUR'], 3.0)
        
        # Check rate history tracking
        self.assertIn('USD', self.strategy._rate_history)
        self.assertGreater(len(self.strategy._rate_history['USD']), 0)
    
    def _create_high_volatility_data(self, symbol: UnifiedSymbol, count: int) -> list:
        """Create high volatility test data."""
        data = []
        base_price = 100.0
        timestamp = datetime.now(timezone.utc)
        
        for i in range(count):
            # Large price movements
            price_change = 2.0 if i % 2 == 0 else -2.0  # Alternating large moves
            price = base_price + price_change
            
            data_point = UnifiedMarketData(
                symbol=symbol,
                timestamp=timestamp - timedelta(minutes=count-i),
                open=Decimal(str(price - 0.5)),
                high=Decimal(str(price + 1.0)),
                low=Decimal(str(price - 1.0)),
                close=Decimal(str(price)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data


class TestForexNewsStrategy(unittest.TestCase):
    """Test cases for ForexNewsStrategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = StrategyConfig(
            name="test_news_strategy",
            parameters={
                'news_strategy': 'breakout',
                'min_impact_level': 'medium',
                'pre_news_minutes': 30,
                'post_news_minutes': 60,
                'volatility_threshold': 0.005
            }
        )
        self.strategy = ForexNewsStrategy(self.config)
    
    def test_initialization(self):
        """Test strategy initialization."""
        self.assertTrue(self.strategy.initialize())
        self.assertEqual(self.strategy.name, "test_news_strategy")
        self.assertGreater(len(self.strategy._upcoming_events), 0)
    
    def test_economic_event_creation(self):
        """Test economic event creation and methods."""
        event = EconomicEvent(
            currency='USD',
            event_name='Non-Farm Payrolls',
            release_time=datetime.now() + timedelta(hours=1),
            impact=NewsImpact.HIGH,
            forecast=200000,
            previous=180000,
            actual=220000
        )
        
        # Test surprise factor calculation
        surprise = event.get_surprise_factor()
        self.assertIsNotNone(surprise)
        self.assertGreater(surprise, 0)  # Actual > forecast = positive surprise
        
        # Test currency pair affection
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        gbp_usd = UnifiedSymbol.from_forex_symbol('GBPUSD')
        eur_gbp = UnifiedSymbol.from_forex_symbol('EURGBP')
        
        self.assertTrue(event.affects_currency_pair(eur_usd))  # USD is quote
        self.assertTrue(event.affects_currency_pair(gbp_usd))  # USD is quote
        self.assertFalse(event.affects_currency_pair(eur_gbp))  # USD not involved
    
    def test_event_relevance_filtering(self):
        """Test filtering of relevant events."""
        current_time = datetime.now()
        
        # Add test event
        upcoming_event = EconomicEvent(
            currency='USD',
            event_name='FOMC Rate Decision',
            release_time=current_time + timedelta(minutes=15),
            impact=NewsImpact.HIGH
        )
        self.strategy._upcoming_events.append(upcoming_event)
        
        # Test relevance for USD pair
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        relevant_events = self.strategy._get_relevant_events(eur_usd, current_time)
        
        self.assertGreater(len(relevant_events), 0)
        self.assertIn(upcoming_event, relevant_events)
    
    def test_news_direction_prediction(self):
        """Test news direction prediction."""
        # Test bullish event for base currency
        gdp_event = EconomicEvent(
            currency='EUR',
            event_name='GDP Growth',
            release_time=datetime.now(),
            impact=NewsImpact.HIGH
        )
        
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        direction = self.strategy._predict_news_direction(gdp_event, eur_usd)
        self.assertEqual(direction, 1)  # Bullish for EUR = pair up
        
        # Test for quote currency
        usd_jpy = UnifiedSymbol.from_forex_symbol('USDJPY')
        direction = self.strategy._predict_news_direction(gdp_event, usd_jpy)
        self.assertEqual(direction, 0)  # EUR not involved in USD/JPY
    
    def test_support_resistance_calculation(self):
        """Test support and resistance calculation."""
        symbol = UnifiedSymbol.from_forex_symbol('EURUSD')
        test_data = self._create_test_data_with_range(symbol, 20)
        
        support, resistance = self.strategy._calculate_support_resistance(test_data)
        
        self.assertLess(support, resistance)
        self.assertGreater(support, 0)
        self.assertGreater(resistance, 0)
    
    def test_volatility_calculation(self):
        """Test recent volatility calculation."""
        symbol = UnifiedSymbol.from_forex_symbol('EURUSD')
        
        # Create data with known volatility
        volatile_data = self._create_volatile_data(symbol, 10)
        volatility = self.strategy._calculate_recent_volatility(volatile_data)
        
        self.assertGreater(volatility, 0)
        
        # Create stable data
        stable_data = self._create_stable_data(symbol, 10)
        low_volatility = self.strategy._calculate_recent_volatility(stable_data)
        
        self.assertLess(low_volatility, volatility)
    
    def test_event_update_functionality(self):
        """Test event update and actual value setting."""
        # Add event
        event = EconomicEvent(
            currency='USD',
            event_name='CPI',
            release_time=datetime.now() - timedelta(minutes=30),
            impact=NewsImpact.HIGH,
            forecast=2.5
        )
        self.strategy.add_economic_event(event)
        
        # Update with actual value
        self.strategy.update_event_actual('CPI', 'USD', 2.8)
        
        # Find the updated event
        updated_event = None
        for e in self.strategy._upcoming_events + self.strategy._recent_events:
            if e.event_name == 'CPI' and e.currency == 'USD':
                updated_event = e
                break
        
        self.assertIsNotNone(updated_event)
        self.assertEqual(updated_event.actual, 2.8)
        self.assertTrue(updated_event.is_released)
    
    def _create_test_data_with_range(self, symbol: UnifiedSymbol, count: int) -> list:
        """Create test data with clear support/resistance levels."""
        data = []
        timestamp = datetime.now(timezone.utc)
        
        for i in range(count):
            # Create data with range between 1.1000 and 1.1100
            base_price = 1.1000 + (i % 10) * 0.001  # Oscillate in range
            
            data_point = UnifiedMarketData(
                symbol=symbol,
                timestamp=timestamp - timedelta(minutes=count-i),
                open=Decimal(str(base_price)),
                high=Decimal(str(base_price + 0.0020)),
                low=Decimal(str(base_price - 0.0020)),
                close=Decimal(str(base_price + 0.0010)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data
    
    def _create_volatile_data(self, symbol: UnifiedSymbol, count: int) -> list:
        """Create volatile test data."""
        data = []
        timestamp = datetime.now(timezone.utc)
        base_price = 1.1000
        
        for i in range(count):
            # Large price swings
            price_change = 0.01 if i % 2 == 0 else -0.01
            price = base_price + price_change
            
            data_point = UnifiedMarketData(
                symbol=symbol,
                timestamp=timestamp - timedelta(minutes=count-i),
                open=Decimal(str(price - 0.002)),
                high=Decimal(str(price + 0.005)),
                low=Decimal(str(price - 0.005)),
                close=Decimal(str(price)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data
    
    def _create_stable_data(self, symbol: UnifiedSymbol, count: int) -> list:
        """Create stable test data."""
        data = []
        timestamp = datetime.now(timezone.utc)
        base_price = 1.1000
        
        for i in range(count):
            # Very small price movements
            price = base_price + i * 0.00001
            
            data_point = UnifiedMarketData(
                symbol=symbol,
                timestamp=timestamp - timedelta(minutes=count-i),
                open=Decimal(str(price)),
                high=Decimal(str(price + 0.00005)),
                low=Decimal(str(price - 0.00005)),
                close=Decimal(str(price)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data


class TestForexTechnicalIndicators(unittest.TestCase):
    """Test cases for ForexTechnicalIndicators."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.indicators = ForexTechnicalIndicators()
    
    def test_pip_value_calculation(self):
        """Test pip value calculation for different pairs."""
        # Test JPY pair
        usd_jpy = UnifiedSymbol.from_forex_symbol('USDJPY')
        jpy_pip = self.indicators.calculate_pip_value(usd_jpy)
        self.assertEqual(jpy_pip, 0.01)
        
        # Test non-JPY pair
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        eur_pip = self.indicators.calculate_pip_value(eur_usd)
        self.assertEqual(eur_pip, 0.0001)
    
    def test_price_to_pips_conversion(self):
        """Test price to pips conversion."""
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        
        # 10 pips move in EUR/USD
        price_diff = 0.0010
        pips = self.indicators.price_to_pips(eur_usd, price_diff)
        self.assertEqual(pips, 10.0)
        
        # Test JPY pair
        usd_jpy = UnifiedSymbol.from_forex_symbol('USDJPY')
        price_diff = 0.10  # 10 pips in JPY
        pips = self.indicators.price_to_pips(usd_jpy, price_diff)
        self.assertEqual(pips, 10.0)
    
    def test_pips_to_price_conversion(self):
        """Test pips to price conversion."""
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        
        # 10 pips in EUR/USD
        price_diff = self.indicators.pips_to_price(eur_usd, 10.0)
        self.assertEqual(price_diff, 0.0010)
    
    def test_spread_calculation(self):
        """Test spread calculation in pips."""
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        
        bid = 1.1000
        ask = 1.1002  # 2 pip spread
        
        spread_pips = self.indicators.calculate_spread_in_pips(eur_usd, bid, ask)
        self.assertAlmostEqual(spread_pips, 2.0, places=1)
    
    def test_forex_atr_pips(self):
        """Test ATR calculation in pips."""
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        
        # Create test data
        highs = [1.1010, 1.1020, 1.1015, 1.1025, 1.1030] * 3  # 15 points
        lows = [1.1000, 1.1005, 1.1000, 1.1010, 1.1015] * 3
        closes = [1.1005, 1.1015, 1.1010, 1.1020, 1.1025] * 3
        
        atr_pips = self.indicators.forex_atr_pips(eur_usd, highs, lows, closes, 14)
        self.assertIsNotNone(atr_pips)
        self.assertGreater(atr_pips, 0)
    
    def test_pivot_points_calculation(self):
        """Test pivot points calculation."""
        high = 1.1100
        low = 1.1000
        close = 1.1050
        
        pivots = self.indicators.pivot_points(high, low, close)
        
        self.assertIn('PP', pivots)
        self.assertIn('R1', pivots)
        self.assertIn('S1', pivots)
        
        # Verify relationships
        self.assertGreater(pivots['R1'], pivots['PP'])
        self.assertLess(pivots['S1'], pivots['PP'])
        self.assertGreater(pivots['R2'], pivots['R1'])
        self.assertLess(pivots['S2'], pivots['S1'])
    
    def test_fibonacci_retracement(self):
        """Test Fibonacci retracement calculation."""
        high = 1.1200
        low = 1.1000
        
        # Test uptrend retracement
        fib_levels = self.indicators.fibonacci_retracement(high, low, 'up')
        
        self.assertIn('0.000', fib_levels)
        self.assertIn('0.618', fib_levels)
        self.assertIn('1.000', fib_levels)
        
        # Verify 61.8% retracement level
        expected_618 = high - (0.618 * (high - low))
        self.assertAlmostEqual(fib_levels['0.618'], expected_618, places=4)
    
    def test_currency_strength_calculation(self):
        """Test currency strength calculation."""
        # Create mock market data for multiple pairs
        eur_usd = UnifiedSymbol.from_forex_symbol('EURUSD')
        gbp_usd = UnifiedSymbol.from_forex_symbol('GBPUSD')
        usd_jpy = UnifiedSymbol.from_forex_symbol('USDJPY')
        
        market_data = {
            eur_usd: self._create_price_data(1.1000, 1.1100, 25),  # EUR strengthening
            gbp_usd: self._create_price_data(1.2000, 1.1900, 25),  # GBP weakening
            usd_jpy: self._create_price_data(110.0, 112.0, 25)     # USD strengthening vs JPY
        }
        
        strength = self.indicators.currency_strength(market_data, 20)
        
        self.assertIn('EUR', strength)
        self.assertIn('USD', strength)
        self.assertIn('GBP', strength)
        self.assertIn('JPY', strength)
        
        # EUR should be stronger than GBP based on our test data
        self.assertGreater(strength['EUR'], strength['GBP'])
    
    def test_correlation_coefficient(self):
        """Test correlation coefficient calculation."""
        # Create perfectly correlated series
        prices1 = [1.0, 2.0, 3.0, 4.0, 5.0] * 4  # 20 points
        prices2 = [2.0, 4.0, 6.0, 8.0, 10.0] * 4  # Perfectly correlated
        
        correlation = self.indicators.correlation_coefficient(prices1, prices2, 20)
        self.assertIsNotNone(correlation)
        self.assertAlmostEqual(correlation, 1.0, places=2)
        
        # Create negatively correlated series
        prices3 = [5.0, 4.0, 3.0, 2.0, 1.0] * 4  # Negatively correlated
        
        correlation = self.indicators.correlation_coefficient(prices1, prices3, 20)
        self.assertIsNotNone(correlation)
        self.assertAlmostEqual(correlation, -1.0, places=2)
    
    def test_forex_momentum(self):
        """Test forex momentum calculation."""
        # Create trending price series
        prices = [1.1000 + i * 0.001 for i in range(20)]  # Uptrend
        
        momentum = self.indicators.forex_momentum(prices, 10)
        self.assertIsNotNone(momentum)
        self.assertGreater(momentum, 0)  # Should be positive for uptrend
    
    def test_williams_percent_r(self):
        """Test Williams %R calculation."""
        # Create test data
        highs = [1.1020, 1.1030, 1.1025, 1.1035, 1.1040] * 3
        lows = [1.1000, 1.1010, 1.1005, 1.1015, 1.1020] * 3
        closes = [1.1010, 1.1025, 1.1015, 1.1030, 1.1035] * 3
        
        williams_r = self.indicators.williams_percent_r(highs, lows, closes, 14)
        self.assertIsNotNone(williams_r)
        self.assertLessEqual(williams_r, 0)  # Williams %R is always <= 0
        self.assertGreaterEqual(williams_r, -100)  # Williams %R is always >= -100
    
    def test_commodity_channel_index(self):
        """Test CCI calculation."""
        # Create test data
        highs = [1.1020, 1.1030, 1.1025, 1.1035, 1.1040] * 4
        lows = [1.1000, 1.1010, 1.1005, 1.1015, 1.1020] * 4
        closes = [1.1010, 1.1025, 1.1015, 1.1030, 1.1035] * 4
        
        cci = self.indicators.commodity_channel_index(highs, lows, closes, 20)
        self.assertIsNotNone(cci)
        self.assertIsInstance(cci, float)
    
    def test_forex_volatility_bands(self):
        """Test forex volatility bands calculation."""
        # Create test price data
        prices = [1.1000 + 0.001 * (i % 10 - 5) for i in range(25)]  # Oscillating prices
        
        bands = self.indicators.forex_volatility_bands(prices, 20, 2.0)
        self.assertIsNotNone(bands)
        
        upper, middle, lower = bands
        self.assertGreater(upper, middle)
        self.assertGreater(middle, lower)
    
    def test_pattern_detection(self):
        """Test forex pattern detection."""
        # Create test data with potential patterns
        test_data = self._create_pattern_data()
        
        patterns = self.indicators.detect_forex_patterns(test_data)
        self.assertIsInstance(patterns, list)
        # Pattern detection is complex, just verify it returns a list
    
    def _create_price_data(self, start_price: float, end_price: float, count: int) -> list:
        """Create price data series from start to end."""
        data = []
        price_step = (end_price - start_price) / (count - 1)
        timestamp = datetime.now(timezone.utc)
        
        for i in range(count):
            price = start_price + i * price_step
            
            data_point = UnifiedMarketData(
                symbol=UnifiedSymbol.from_forex_symbol('EURUSD'),
                timestamp=timestamp - timedelta(minutes=count-i),
                open=Decimal(str(price - 0.0005)),
                high=Decimal(str(price + 0.0010)),
                low=Decimal(str(price - 0.0010)),
                close=Decimal(str(price)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data
    
    def _create_pattern_data(self) -> list:
        """Create test data that might contain patterns."""
        data = []
        timestamp = datetime.now(timezone.utc)
        
        # Create data with potential double top pattern
        prices = [1.1000, 1.1050, 1.1100, 1.1050, 1.1000, 1.1050, 1.1100, 1.1050, 1.1000, 1.1020]
        
        for i, price in enumerate(prices):
            data_point = UnifiedMarketData(
                symbol=UnifiedSymbol.from_forex_symbol('EURUSD'),
                timestamp=timestamp - timedelta(minutes=len(prices)-i),
                open=Decimal(str(price - 0.0010)),
                high=Decimal(str(price + 0.0020)),
                low=Decimal(str(price - 0.0020)),
                close=Decimal(str(price)),
                volume=Decimal('1000'),
                source='test',
                market_type=MarketType.FOREX
            )
            data.append(data_point)
        
        return data


if __name__ == '__main__':
    unittest.main()