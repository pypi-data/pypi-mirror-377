"""
Forex news-based trading strategy that trades around economic events.

This strategy monitors economic calendar events and trades based on
expected volatility and market reactions to news releases.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import logging

from .market_specific_strategy import MarketSpecificStrategy, StrategyConfig
from ..models.data_models import UnifiedMarketData, TradingSignal, SignalAction
from ..markets.types import MarketType, UnifiedSymbol
from .technical_indicators import TechnicalIndicators


class NewsImpact(Enum):
    """Economic news impact levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NewsStrategy(Enum):
    """News trading strategies."""
    PRE_NEWS = "pre_news"      # Trade before news release
    POST_NEWS = "post_news"    # Trade after news release
    BREAKOUT = "breakout"      # Trade breakouts from news
    FADE = "fade"              # Fade initial news reaction


class EconomicEvent:
    """Represents an economic calendar event."""
    
    def __init__(self, currency: str, event_name: str, release_time: datetime,
                 impact: NewsImpact, forecast: Optional[float] = None,
                 previous: Optional[float] = None, actual: Optional[float] = None):
        self.currency = currency
        self.event_name = event_name
        self.release_time = release_time
        self.impact = impact
        self.forecast = forecast
        self.previous = previous
        self.actual = actual
        self.is_released = actual is not None
    
    def get_surprise_factor(self) -> Optional[float]:
        """Calculate surprise factor (actual vs forecast)."""
        if self.actual is None or self.forecast is None:
            return None
        
        if self.forecast == 0:
            return 0.0
        
        return (self.actual - self.forecast) / abs(self.forecast)
    
    def affects_currency_pair(self, symbol: UnifiedSymbol) -> bool:
        """Check if this event affects the given currency pair."""
        return self.currency in [symbol.base_asset, symbol.quote_asset]


class ForexNewsStrategy(MarketSpecificStrategy):
    """
    Forex news-based trading strategy.
    
    This strategy:
    1. Monitors economic calendar for high-impact events
    2. Identifies currency pairs likely to be affected
    3. Uses different strategies based on timing and event type
    4. Manages risk around volatile news periods
    """
    
    # High-impact economic indicators by currency
    HIGH_IMPACT_EVENTS = {
        'USD': [
            'Non-Farm Payrolls', 'FOMC Rate Decision', 'CPI', 'GDP',
            'Unemployment Rate', 'Retail Sales', 'ISM Manufacturing PMI'
        ],
        'EUR': [
            'ECB Rate Decision', 'CPI', 'GDP', 'Unemployment Rate',
            'Manufacturing PMI', 'Services PMI'
        ],
        'GBP': [
            'BOE Rate Decision', 'CPI', 'GDP', 'Unemployment Rate',
            'Manufacturing PMI', 'Retail Sales'
        ],
        'JPY': [
            'BOJ Rate Decision', 'CPI', 'GDP', 'Unemployment Rate',
            'Manufacturing PMI', 'Tankan Survey'
        ],
        'AUD': [
            'RBA Rate Decision', 'CPI', 'GDP', 'Unemployment Rate',
            'Employment Change'
        ],
        'CAD': [
            'BOC Rate Decision', 'CPI', 'GDP', 'Unemployment Rate',
            'Employment Change'
        ],
        'CHF': [
            'SNB Rate Decision', 'CPI', 'GDP', 'Unemployment Rate'
        ],
        'NZD': [
            'RBNZ Rate Decision', 'CPI', 'GDP', 'Unemployment Rate'
        ]
    }
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize forex news strategy.
        
        Args:
            config: Strategy configuration
        """
        # Only support forex markets
        super().__init__(config, [MarketType.FOREX])
        
        self.indicators = TechnicalIndicators()
        
        # Strategy parameters
        params = config.parameters
        self.news_strategy = NewsStrategy(params.get('news_strategy', 'breakout'))
        self.min_impact_level = NewsImpact(params.get('min_impact_level', 'medium'))
        self.pre_news_minutes = params.get('pre_news_minutes', 30)
        self.post_news_minutes = params.get('post_news_minutes', 60)
        self.volatility_threshold = params.get('volatility_threshold', 0.005)  # 0.5%
        self.breakout_multiplier = params.get('breakout_multiplier', 1.5)
        
        # Technical analysis parameters
        self.support_resistance_period = params.get('support_resistance_period', 20)
        self.atr_period = params.get('atr_period', 14)
        self.rsi_period = params.get('rsi_period', 14)
        
        # Risk management
        self.max_news_exposure = params.get('max_news_exposure', 2)  # Max positions during news
        self.news_stop_multiplier = params.get('news_stop_multiplier', 2.0)
        
        # Event tracking
        self._upcoming_events: List[EconomicEvent] = []
        self._recent_events: List[EconomicEvent] = []
        self._news_positions: Dict[str, Dict[str, Any]] = {}
        
        self.logger = logging.getLogger(f"forex_news_strategy.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the forex news strategy."""
        try:
            self.logger.info(f"Initializing forex news strategy: {self.name}")
            
            # Load initial economic calendar (in production, this would come from data feed)
            self._load_sample_events()
            
            self.logger.info(f"Strategy initialized with {len(self._upcoming_events)} upcoming events")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze_market_data(self, market_data: List[UnifiedMarketData], 
                           market_type: MarketType) -> Optional[TradingSignal]:
        """
        Analyze forex market data for news-based trading opportunities.
        
        Args:
            market_data: List of unified market data points
            market_type: Market type (should be FOREX)
            
        Returns:
            Optional[TradingSignal]: Trading signal if conditions are met
        """
        if market_type != MarketType.FOREX:
            return None
        
        if len(market_data) < self.get_required_data_length():
            return None
        
        try:
            current_time = datetime.now()
            
            # Update event status
            self._update_event_status(current_time)
            
            # Group data by symbol
            symbol_data = self._group_data_by_symbol(market_data)
            
            # Find the best news-based opportunity
            best_signal = None
            best_score = 0.0
            
            for symbol, data_points in symbol_data.items():
                if len(data_points) < self.get_required_data_length():
                    continue
                
                # Check for relevant news events
                relevant_events = self._get_relevant_events(symbol, current_time)
                if not relevant_events:
                    continue
                
                # Analyze news opportunity
                signal = self._analyze_news_opportunity(symbol, data_points, relevant_events, current_time)
                if signal and signal.confidence > best_score:
                    best_signal = signal
                    best_score = signal.confidence
            
            return best_signal
            
        except Exception as e:
            self.logger.error(f"Error analyzing market data: {str(e)}")
            return None
    
    def get_market_specific_parameters(self, market_type: MarketType) -> Dict[str, Any]:
        """Get forex news strategy specific parameters."""
        if market_type != MarketType.FOREX:
            return {}
        
        return {
            'news_strategy': self.news_strategy.value,
            'min_impact_level': self.min_impact_level.value,
            'pre_news_minutes': self.pre_news_minutes,
            'post_news_minutes': self.post_news_minutes,
            'volatility_threshold': self.volatility_threshold,
            'breakout_multiplier': self.breakout_multiplier,
            'max_news_exposure': self.max_news_exposure
        }
    
    def validate_market_conditions(self, market_data: List[UnifiedMarketData], 
                                 market_type: MarketType) -> bool:
        """
        Validate if market conditions are suitable for news trading.
        
        Args:
            market_data: Market data to validate
            market_type: Market type
            
        Returns:
            bool: True if conditions are suitable
        """
        if market_type != MarketType.FOREX:
            return False
        
        if not market_data:
            return False
        
        try:
            current_time = datetime.now()
            
            # Check if we have relevant upcoming events
            has_relevant_events = False
            for data in market_data:
                relevant_events = self._get_relevant_events(data.symbol, current_time)
                if relevant_events:
                    has_relevant_events = True
                    break
            
            if not has_relevant_events:
                return False
            
            # Check if we're not over-exposed to news trades
            if len(self._news_positions) >= self.max_news_exposure:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating market conditions: {str(e)}")
            return False
    
    def get_required_data_length(self) -> int:
        """Get minimum data points required for analysis."""
        return max(self.support_resistance_period, self.atr_period, self.rsi_period) + 5
    
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        try:
            if not super().validate_parameters():
                return False
            
            # Validate news-specific parameters
            if self.pre_news_minutes <= 0 or self.post_news_minutes <= 0:
                self.logger.error("News timing parameters must be positive")
                return False
            
            if self.volatility_threshold <= 0:
                self.logger.error("Volatility threshold must be positive")
                return False
            
            if self.max_news_exposure <= 0:
                self.logger.error("Max news exposure must be positive")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _group_data_by_symbol(self, market_data: List[UnifiedMarketData]) -> Dict[UnifiedSymbol, List[UnifiedMarketData]]:
        """Group market data by symbol."""
        symbol_data = {}
        for data in market_data:
            if data.symbol not in symbol_data:
                symbol_data[data.symbol] = []
            symbol_data[data.symbol].append(data)
        
        # Sort each symbol's data by timestamp
        for symbol in symbol_data:
            symbol_data[symbol].sort(key=lambda x: x.timestamp)
        
        return symbol_data
    
    def _load_sample_events(self):
        """Load sample economic events (in production, this would come from economic calendar API)."""
        current_time = datetime.now()
        
        # Sample upcoming events
        sample_events = [
            EconomicEvent('USD', 'Non-Farm Payrolls', current_time + timedelta(hours=2), NewsImpact.HIGH),
            EconomicEvent('EUR', 'ECB Rate Decision', current_time + timedelta(hours=6), NewsImpact.HIGH),
            EconomicEvent('GBP', 'CPI', current_time + timedelta(hours=12), NewsImpact.MEDIUM),
            EconomicEvent('JPY', 'GDP', current_time + timedelta(days=1), NewsImpact.MEDIUM),
            EconomicEvent('AUD', 'Employment Change', current_time + timedelta(days=2), NewsImpact.MEDIUM),
        ]
        
        self._upcoming_events = sample_events
    
    def _update_event_status(self, current_time: datetime):
        """Update event status and move released events to recent list."""
        # Move past events to recent list
        past_events = [event for event in self._upcoming_events if event.release_time <= current_time]
        for event in past_events:
            self._recent_events.append(event)
            self._upcoming_events.remove(event)
        
        # Keep only recent events from last 24 hours
        cutoff_time = current_time - timedelta(hours=24)
        self._recent_events = [event for event in self._recent_events if event.release_time >= cutoff_time]
    
    def _get_relevant_events(self, symbol: UnifiedSymbol, current_time: datetime) -> List[EconomicEvent]:
        """Get events relevant to the given currency pair."""
        relevant_events = []
        
        # Check upcoming events
        for event in self._upcoming_events:
            if event.affects_currency_pair(symbol):
                time_to_event = (event.release_time - current_time).total_seconds() / 60  # minutes
                
                # Include events within our time window
                if -self.post_news_minutes <= time_to_event <= self.pre_news_minutes:
                    # Filter by impact level
                    impact_levels = [NewsImpact.LOW, NewsImpact.MEDIUM, NewsImpact.HIGH]
                    min_index = impact_levels.index(self.min_impact_level)
                    event_index = impact_levels.index(event.impact)
                    
                    if event_index >= min_index:
                        relevant_events.append(event)
        
        # Check recent events for post-news strategies
        for event in self._recent_events:
            if event.affects_currency_pair(symbol):
                time_since_event = (current_time - event.release_time).total_seconds() / 60  # minutes
                
                if 0 <= time_since_event <= self.post_news_minutes:
                    impact_levels = [NewsImpact.LOW, NewsImpact.MEDIUM, NewsImpact.HIGH]
                    min_index = impact_levels.index(self.min_impact_level)
                    event_index = impact_levels.index(event.impact)
                    
                    if event_index >= min_index:
                        relevant_events.append(event)
        
        return relevant_events
    
    def _analyze_news_opportunity(self, symbol: UnifiedSymbol, 
                                data_points: List[UnifiedMarketData],
                                events: List[EconomicEvent],
                                current_time: datetime) -> Optional[TradingSignal]:
        """Analyze news-based trading opportunity."""
        try:
            # Extract price data
            closes = [float(d.close) for d in data_points]
            highs = [float(d.high) for d in data_points]
            lows = [float(d.low) for d in data_points]
            
            # Calculate technical indicators
            atr = self.indicators.atr(highs, lows, closes, self.atr_period)
            rsi = self.indicators.rsi(closes, self.rsi_period)
            
            if None in [atr, rsi]:
                return None
            
            # Calculate support and resistance levels
            support, resistance = self._calculate_support_resistance(data_points)
            
            # Get the most impactful event
            primary_event = max(events, key=lambda e: [NewsImpact.LOW, NewsImpact.MEDIUM, NewsImpact.HIGH].index(e.impact))
            
            # Determine strategy based on timing
            time_to_event = (primary_event.release_time - current_time).total_seconds() / 60
            
            if time_to_event > 0:
                # Pre-news strategy
                signal = self._analyze_pre_news(symbol, data_points, primary_event, support, resistance, atr)
            else:
                # Post-news strategy
                signal = self._analyze_post_news(symbol, data_points, primary_event, support, resistance, atr)
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error analyzing news opportunity for {symbol}: {str(e)}")
            return None
    
    def _calculate_support_resistance(self, data_points: List[UnifiedMarketData]) -> Tuple[float, float]:
        """Calculate support and resistance levels."""
        recent_data = data_points[-self.support_resistance_period:]
        
        # Simple support/resistance calculation
        highs = [float(d.high) for d in recent_data]
        lows = [float(d.low) for d in recent_data]
        
        resistance = max(highs)
        support = min(lows)
        
        return support, resistance
    
    def _analyze_pre_news(self, symbol: UnifiedSymbol, data_points: List[UnifiedMarketData],
                         event: EconomicEvent, support: float, resistance: float,
                         atr: float) -> Optional[TradingSignal]:
        """Analyze pre-news trading opportunity."""
        if self.news_strategy not in [NewsStrategy.PRE_NEWS, NewsStrategy.BREAKOUT]:
            return None
        
        latest_data = data_points[-1]
        current_price = float(latest_data.close)
        
        # Calculate volatility
        volatility = self._calculate_recent_volatility(data_points[-10:])
        
        if self.news_strategy == NewsStrategy.PRE_NEWS:
            # Position for expected news direction
            expected_direction = self._predict_news_direction(event, symbol)
            if expected_direction == 0:
                return None
            
            action = SignalAction.BUY if expected_direction > 0 else SignalAction.SELL
            confidence = 0.6  # Moderate confidence for pre-news
            
        else:  # BREAKOUT strategy
            # Set up for breakout in either direction
            distance_to_resistance = (resistance - current_price) / current_price
            distance_to_support = (current_price - support) / current_price
            
            # Prefer direction with more room to move
            if distance_to_resistance > distance_to_support:
                action = SignalAction.BUY
                confidence = min(0.8, distance_to_resistance * 10)
            else:
                action = SignalAction.SELL
                confidence = min(0.8, distance_to_support * 10)
        
        if confidence > 0.5:
            return TradingSignal(
                symbol=symbol.native_symbol,
                action=action,
                confidence=confidence,
                timestamp=latest_data.timestamp,
                strategy_name=self.name,
                price=Decimal(str(current_price)),
                metadata={
                    'market_type': 'forex',
                    'strategy_type': 'news_pre',
                    'event_name': event.event_name,
                    'event_currency': event.currency,
                    'event_impact': event.impact.value,
                    'time_to_event_minutes': (event.release_time - datetime.now()).total_seconds() / 60,
                    'support': support,
                    'resistance': resistance,
                    'atr': atr,
                    'volatility': volatility,
                    'news_strategy': self.news_strategy.value
                }
            )
        
        return None
    
    def _analyze_post_news(self, symbol: UnifiedSymbol, data_points: List[UnifiedMarketData],
                          event: EconomicEvent, support: float, resistance: float,
                          atr: float) -> Optional[TradingSignal]:
        """Analyze post-news trading opportunity."""
        if self.news_strategy not in [NewsStrategy.POST_NEWS, NewsStrategy.FADE]:
            return None
        
        latest_data = data_points[-1]
        current_price = float(latest_data.close)
        
        # Calculate price movement since news
        pre_news_data = [d for d in data_points if d.timestamp <= event.release_time]
        if not pre_news_data:
            return None
        
        pre_news_price = float(pre_news_data[-1].close)
        news_move = (current_price - pre_news_price) / pre_news_price
        
        # Calculate volatility spike
        volatility = self._calculate_recent_volatility(data_points[-5:])
        
        if self.news_strategy == NewsStrategy.POST_NEWS:
            # Continue in direction of news move if strong
            if abs(news_move) > self.volatility_threshold:
                action = SignalAction.BUY if news_move > 0 else SignalAction.SELL
                confidence = min(0.8, abs(news_move) * 100)
            else:
                return None
                
        else:  # FADE strategy
            # Fade the initial news reaction
            if abs(news_move) > self.volatility_threshold * 2:
                action = SignalAction.SELL if news_move > 0 else SignalAction.BUY
                confidence = min(0.7, abs(news_move) * 50)
            else:
                return None
        
        if confidence > 0.5:
            return TradingSignal(
                symbol=symbol.native_symbol,
                action=action,
                confidence=confidence,
                timestamp=latest_data.timestamp,
                strategy_name=self.name,
                price=Decimal(str(current_price)),
                metadata={
                    'market_type': 'forex',
                    'strategy_type': 'news_post',
                    'event_name': event.event_name,
                    'event_currency': event.currency,
                    'event_impact': event.impact.value,
                    'time_since_event_minutes': (datetime.now() - event.release_time).total_seconds() / 60,
                    'news_move_percent': news_move * 100,
                    'pre_news_price': pre_news_price,
                    'support': support,
                    'resistance': resistance,
                    'atr': atr,
                    'volatility': volatility,
                    'news_strategy': self.news_strategy.value
                }
            )
        
        return None
    
    def _predict_news_direction(self, event: EconomicEvent, symbol: UnifiedSymbol) -> int:
        """
        Predict likely direction of price movement based on event.
        
        Returns:
            int: 1 for bullish, -1 for bearish, 0 for neutral
        """
        # This is a simplified prediction - in practice, this would be more sophisticated
        event_currency = event.currency
        
        # Determine if event currency is base or quote
        if event_currency == symbol.base_asset:
            # Good news for base currency = pair goes up
            multiplier = 1
        elif event_currency == symbol.quote_asset:
            # Good news for quote currency = pair goes down
            multiplier = -1
        else:
            return 0
        
        # Predict based on event type (simplified)
        bullish_events = ['Rate Decision', 'GDP', 'Employment', 'PMI']
        bearish_events = ['Unemployment', 'CPI']  # High CPI can be bearish due to inflation concerns
        
        for bullish in bullish_events:
            if bullish.lower() in event.event_name.lower():
                return multiplier
        
        for bearish in bearish_events:
            if bearish.lower() in event.event_name.lower():
                return -multiplier
        
        return 0  # Neutral if can't determine
    
    def _calculate_recent_volatility(self, data_points: List[UnifiedMarketData]) -> float:
        """Calculate recent volatility."""
        if len(data_points) < 2:
            return 0.0
        
        # Calculate price changes
        changes = []
        for i in range(1, len(data_points)):
            prev_close = float(data_points[i-1].close)
            curr_close = float(data_points[i].close)
            change = abs(curr_close - prev_close) / prev_close
            changes.append(change)
        
        return sum(changes) / len(changes) if changes else 0.0
    
    def add_economic_event(self, event: EconomicEvent):
        """Add an economic event to the calendar."""
        self._upcoming_events.append(event)
        self._upcoming_events.sort(key=lambda e: e.release_time)
        
        self.logger.info(f"Added economic event: {event.event_name} ({event.currency}) at {event.release_time}")
    
    def update_event_actual(self, event_name: str, currency: str, actual_value: float):
        """Update an event with actual released value."""
        for event in self._upcoming_events + self._recent_events:
            if event.event_name == event_name and event.currency == currency:
                event.actual = actual_value
                event.is_released = True
                
                surprise = event.get_surprise_factor()
                if surprise is not None:
                    self.logger.info(f"Event released: {event_name} ({currency}) - "
                                   f"Actual: {actual_value}, Surprise: {surprise:.2%}")
                break