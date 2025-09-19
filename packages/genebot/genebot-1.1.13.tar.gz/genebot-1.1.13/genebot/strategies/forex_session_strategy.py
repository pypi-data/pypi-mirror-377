"""
Forex session-based trading strategy that utilizes market session overlaps.

This strategy takes advantage of increased volatility and liquidity during
forex market session overlaps, particularly London-New York and Tokyo-London overlaps.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime, time, timezone
from decimal import Decimal
import logging

from .market_specific_strategy import MarketSpecificStrategy, StrategyConfig
from ..models.data_models import UnifiedMarketData, TradingSignal, SignalAction, SessionInfo
from ..markets.types import MarketType, UnifiedSymbol
from .technical_indicators import TechnicalIndicators


class ForexSessionStrategy(MarketSpecificStrategy):
    """
    Forex session-based trading strategy.
    
    This strategy focuses on trading during high-volatility periods when
    major forex sessions overlap, using momentum and volatility indicators
    to identify trading opportunities.
    """
    
    # Major forex session times (UTC)
    SESSION_TIMES = {
        'sydney': {'open': time(22, 0), 'close': time(7, 0)},
        'tokyo': {'open': time(0, 0), 'close': time(9, 0)},
        'london': {'open': time(8, 0), 'close': time(17, 0)},
        'new_york': {'open': time(13, 0), 'close': time(22, 0)}
    }
    
    # High-impact session overlaps
    HIGH_IMPACT_OVERLAPS = [
        ('london', 'new_york'),  # 13:00-17:00 UTC - Highest volume
        ('tokyo', 'london'),     # 08:00-09:00 UTC - Asian-European overlap
    ]
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize forex session strategy.
        
        Args:
            config: Strategy configuration
        """
        # Only support forex markets
        super().__init__(config, [MarketType.FOREX])
        
        self.indicators = TechnicalIndicators()
        
        # Strategy parameters
        params = config.parameters
        self.min_volatility_threshold = params.get('min_volatility_threshold', 0.0015)  # 15 pips
        self.momentum_period = params.get('momentum_period', 20)
        self.atr_period = params.get('atr_period', 14)
        self.atr_multiplier = params.get('atr_multiplier', 2.0)
        self.rsi_period = params.get('rsi_period', 14)
        self.rsi_oversold = params.get('rsi_oversold', 30)
        self.rsi_overbought = params.get('rsi_overbought', 70)
        
        # Session overlap settings
        self.overlap_only = params.get('overlap_only', True)
        self.preferred_sessions = set(params.get('preferred_sessions', ['london', 'new_york']))
        self.min_overlap_minutes = params.get('min_overlap_minutes', 60)
        
        # Currency pair preferences
        self.major_pairs = set(params.get('major_pairs', [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF',
            'AUD/USD', 'USD/CAD', 'NZD/USD'
        ]))
        
        # Session tracking
        self._current_overlaps: Set[tuple] = set()
        self._session_volatility: Dict[str, float] = {}
        
        self.logger = logging.getLogger(f"forex_session_strategy.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the forex session strategy."""
        try:
            self.logger.info(f"Initializing forex session strategy: {self.name}")
            
            # Validate configuration
            if not self.preferred_sessions:
                self.logger.error("No preferred sessions configured")
                return False
            
            # Check if preferred sessions are valid
            valid_sessions = set(self.SESSION_TIMES.keys())
            invalid_sessions = self.preferred_sessions - valid_sessions
            if invalid_sessions:
                self.logger.error(f"Invalid sessions configured: {invalid_sessions}")
                return False
            
            self.logger.info(f"Strategy initialized with preferred sessions: {self.preferred_sessions}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze_market_data(self, market_data: List[UnifiedMarketData], 
                           market_type: MarketType) -> Optional[TradingSignal]:
        """
        Analyze forex market data during session overlaps.
        
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
            # Group data by symbol
            symbol_data = self._group_data_by_symbol(market_data)
            
            # Analyze each symbol
            for symbol, data_points in symbol_data.items():
                if len(data_points) < self.get_required_data_length():
                    continue
                
                # Check if we should trade this pair
                if not self._should_trade_pair(symbol):
                    continue
                
                # Check session conditions
                latest_data = data_points[-1]
                if not self._is_favorable_session(latest_data):
                    continue
                
                # Analyze trading opportunity
                signal = self._analyze_symbol_data(symbol, data_points)
                if signal:
                    return signal
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing market data: {str(e)}")
            return None
    
    def get_market_specific_parameters(self, market_type: MarketType) -> Dict[str, Any]:
        """Get forex-specific parameters."""
        if market_type != MarketType.FOREX:
            return {}
        
        return {
            'min_volatility_threshold': self.min_volatility_threshold,
            'momentum_period': self.momentum_period,
            'atr_period': self.atr_period,
            'atr_multiplier': self.atr_multiplier,
            'rsi_period': self.rsi_period,
            'overlap_only': self.overlap_only,
            'preferred_sessions': list(self.preferred_sessions),
            'major_pairs': list(self.major_pairs)
        }
    
    def validate_market_conditions(self, market_data: List[UnifiedMarketData], 
                                 market_type: MarketType) -> bool:
        """
        Validate if market conditions are suitable for forex session trading.
        
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
            # Check if we have recent data
            latest_data = market_data[-1]
            time_diff = datetime.now(timezone.utc) - latest_data.timestamp
            if time_diff.total_seconds() > 300:  # 5 minutes old
                return False
            
            # Check session conditions
            if self.overlap_only and not self._is_favorable_session(latest_data):
                return False
            
            # Check volatility
            if len(market_data) >= 2:
                recent_volatility = self._calculate_volatility(market_data[-20:])
                if recent_volatility < self.min_volatility_threshold:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating market conditions: {str(e)}")
            return False
    
    def get_required_data_length(self) -> int:
        """Get minimum data points required for analysis."""
        return max(self.momentum_period, self.atr_period, self.rsi_period) + 5
    
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        try:
            if not super().validate_parameters():
                return False
            
            # Validate forex-specific parameters
            if self.min_volatility_threshold <= 0:
                self.logger.error("Minimum volatility threshold must be positive")
                return False
            
            if self.momentum_period <= 0 or self.atr_period <= 0 or self.rsi_period <= 0:
                self.logger.error("All periods must be positive")
                return False
            
            if not (0 < self.rsi_oversold < self.rsi_overbought < 100):
                self.logger.error("Invalid RSI thresholds")
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
    
    def _should_trade_pair(self, symbol: UnifiedSymbol) -> bool:
        """Check if we should trade this currency pair."""
        if not symbol.is_forex_pair():
            return False
        
        # Check if it's a major pair
        standard_format = symbol.to_standard_format()
        return standard_format in self.major_pairs
    
    def _is_favorable_session(self, data: UnifiedMarketData) -> bool:
        """Check if current time is during favorable trading sessions."""
        current_time = data.timestamp.time()
        current_overlaps = self._get_current_overlaps(current_time)
        
        # Update current overlaps
        self._current_overlaps = current_overlaps
        
        if self.overlap_only:
            # Only trade during overlaps
            if not current_overlaps:
                return False
            
            # Check if any overlap involves preferred sessions
            for overlap in current_overlaps:
                if any(session in self.preferred_sessions for session in overlap):
                    return True
            return False
        else:
            # Trade during any preferred session
            active_sessions = self._get_active_sessions(current_time)
            return bool(active_sessions.intersection(self.preferred_sessions))
    
    def _get_current_overlaps(self, current_time: time) -> Set[tuple]:
        """Get currently active session overlaps."""
        active_sessions = self._get_active_sessions(current_time)
        overlaps = set()
        
        # Find all pairs of active sessions
        active_list = list(active_sessions)
        for i in range(len(active_list)):
            for j in range(i + 1, len(active_list)):
                overlap = tuple(sorted([active_list[i], active_list[j]]))
                overlaps.add(overlap)
        
        return overlaps
    
    def _get_active_sessions(self, current_time: time) -> Set[str]:
        """Get currently active trading sessions."""
        active_sessions = set()
        
        for session_name, times in self.SESSION_TIMES.items():
            if self._is_time_in_session(current_time, times['open'], times['close']):
                active_sessions.add(session_name)
        
        return active_sessions
    
    def _is_time_in_session(self, current_time: time, open_time: time, close_time: time) -> bool:
        """Check if current time is within session hours."""
        if open_time <= close_time:
            # Same day session
            return open_time <= current_time <= close_time
        else:
            # Session crosses midnight
            return current_time >= open_time or current_time <= close_time
    
    def _analyze_symbol_data(self, symbol: UnifiedSymbol, 
                           data_points: List[UnifiedMarketData]) -> Optional[TradingSignal]:
        """Analyze data for a specific symbol."""
        try:
            # Extract price data
            closes = [float(d.close) for d in data_points]
            highs = [float(d.high) for d in data_points]
            lows = [float(d.low) for d in data_points]
            
            # Calculate technical indicators
            rsi = self.indicators.rsi(closes, self.rsi_period)
            atr = self.indicators.atr(highs, lows, closes, self.atr_period)
            sma_short = self.indicators.sma(closes, 10)
            sma_long = self.indicators.sma(closes, 20)
            
            if None in [rsi, atr, sma_short, sma_long]:
                return None
            
            # Calculate volatility
            volatility = self._calculate_volatility(data_points[-10:])
            
            # Check volatility threshold
            if volatility < self.min_volatility_threshold:
                return None
            
            # Generate trading signals
            latest_data = data_points[-1]
            current_price = float(latest_data.close)
            
            # Momentum signal
            momentum_signal = self._get_momentum_signal(sma_short[-1], sma_long[-1])
            
            # RSI signal
            rsi_signal = self._get_rsi_signal(rsi)
            
            # Volatility signal
            volatility_signal = self._get_volatility_signal(volatility, atr)
            
            # Combine signals
            signal_strength = self._combine_signals(momentum_signal, rsi_signal, volatility_signal)
            
            if abs(signal_strength) > 0.6:  # Minimum confidence threshold
                action = SignalAction.BUY if signal_strength > 0 else SignalAction.SELL
                confidence = min(abs(signal_strength), 1.0)
                
                # Add session context to metadata
                overlap_info = list(self._current_overlaps) if self._current_overlaps else []
                
                return TradingSignal(
                    symbol=symbol.native_symbol,
                    action=action,
                    confidence=confidence,
                    timestamp=latest_data.timestamp,
                    strategy_name=self.name,
                    price=Decimal(str(current_price)),
                    metadata={
                        'market_type': 'forex',
                        'session_overlaps': overlap_info,
                        'volatility': volatility,
                        'atr': atr,
                        'rsi': rsi,
                        'momentum_signal': momentum_signal,
                        'rsi_signal': rsi_signal,
                        'volatility_signal': volatility_signal,
                        'combined_strength': signal_strength
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing symbol {symbol}: {str(e)}")
            return None
    
    def _calculate_volatility(self, data_points: List[UnifiedMarketData]) -> float:
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
        
        # Return average absolute change
        return sum(changes) / len(changes) if changes else 0.0
    
    def _get_momentum_signal(self, sma_short: float, sma_long: float) -> float:
        """Get momentum signal from moving averages."""
        if sma_long == 0:
            return 0.0
        
        # Calculate momentum strength
        momentum = (sma_short - sma_long) / sma_long
        
        # Normalize to [-1, 1] range
        return max(-1.0, min(1.0, momentum * 100))
    
    def _get_rsi_signal(self, rsi: float) -> float:
        """Get RSI-based signal."""
        if rsi <= self.rsi_oversold:
            # Oversold - buy signal
            return (self.rsi_oversold - rsi) / self.rsi_oversold
        elif rsi >= self.rsi_overbought:
            # Overbought - sell signal
            return -(rsi - self.rsi_overbought) / (100 - self.rsi_overbought)
        else:
            # Neutral zone
            return 0.0
    
    def _get_volatility_signal(self, volatility: float, atr: float) -> float:
        """Get volatility-based signal strength multiplier."""
        # Higher volatility during overlaps suggests stronger signals
        if volatility > self.min_volatility_threshold * 2:
            return 1.2  # Boost signal strength
        elif volatility > self.min_volatility_threshold:
            return 1.0  # Normal strength
        else:
            return 0.5  # Reduce signal strength
    
    def _combine_signals(self, momentum: float, rsi: float, volatility_multiplier: float) -> float:
        """Combine different signals into final signal strength."""
        # Weight the signals
        momentum_weight = 0.6
        rsi_weight = 0.4
        
        # Combine signals
        combined = (momentum * momentum_weight) + (rsi * rsi_weight)
        
        # Apply volatility multiplier
        combined *= volatility_multiplier
        
        # Ensure result is in [-1, 1] range
        return max(-1.0, min(1.0, combined))