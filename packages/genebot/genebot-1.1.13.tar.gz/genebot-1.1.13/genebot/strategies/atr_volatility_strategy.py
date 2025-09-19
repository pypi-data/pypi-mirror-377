"""
ATR Volatility Strategy using Average True Range for high-probability volatility-based signals.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

from .base_strategy import BaseStrategy, StrategyConfig
from .technical_indicators import TechnicalIndicators
from ..models.data_models import MarketData, TradingSignal, SignalAction


class ATRVolatilityStrategy(BaseStrategy):
    """
    Advanced ATR Volatility Strategy for high-probability volatility-based trading.
    
    This strategy uses Average True Range (ATR) analysis combined with volatility patterns:
    - ATR-based volatility breakouts and contractions
    - Volatility squeeze detection and expansion
    - ATR-adjusted support/resistance levels
    - Volume-volatility correlation analysis
    - Multi-timeframe volatility analysis
    - ATR-based position sizing and stop-loss levels
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the ATR Volatility Strategy.
        
        Args:
            config: Strategy configuration containing parameters:
                - atr_period: ATR calculation period (default: 14)
                - atr_multiplier: ATR multiplier for breakout detection (default: 2.0)
                - volatility_threshold: Volatility change threshold (default: 1.5)
                - squeeze_threshold: Volatility squeeze threshold (default: 0.5)
                - expansion_threshold: Volatility expansion threshold (default: 2.0)
                - volume_correlation: Volume-volatility correlation threshold (default: 0.7)
                - trend_filter: Use trend filter for signals (default: True)
                - min_confidence: Minimum confidence threshold (default: 0.86)
                - lookback_period: Lookback period for volatility analysis (default: 50)
        """
        super().__init__(config)
        
        # Extract parameters with defaults
        self.atr_period = self.parameters.get('atr_period', 14)
        self.atr_multiplier = self.parameters.get('atr_multiplier', 2.0)
        self.volatility_threshold = self.parameters.get('volatility_threshold', 1.5)
        self.squeeze_threshold = self.parameters.get('squeeze_threshold', 0.5)
        self.expansion_threshold = self.parameters.get('expansion_threshold', 2.0)
        self.volume_correlation = self.parameters.get('volume_correlation', 0.7)
        self.trend_filter = self.parameters.get('trend_filter', True)
        self.min_confidence = self.parameters.get('min_confidence', 0.86)
        self.lookback_period = self.parameters.get('lookback_period', 50)
        
        # Technical indicators
        self.indicators = TechnicalIndicators()
        
        # Strategy state
        self._atr_history = []
        self._volatility_history = []
        self._price_history = []
        self._volume_history = []
        self._squeeze_periods = []
        self._breakout_levels = {'upper': None, 'lower': None}
        self._last_signal = None
        self._last_signal_time = None
        
        self.logger = logging.getLogger(f"strategy.atr_volatility.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the strategy."""
        try:
            self.logger.info(f"Initializing ATR Volatility Strategy: {self.name}")
            self.logger.info(f"Parameters: ATR period={self.atr_period}, "
                           f"multiplier={self.atr_multiplier}, "
                           f"volatility threshold={self.volatility_threshold}")
            
            # Clear state
            self._atr_history.clear()
            self._volatility_history.clear()
            self._price_history.clear()
            self._volume_history.clear()
            self._squeeze_periods.clear()
            self._breakout_levels = {'upper': None, 'lower': None}
            self._last_signal = None
            self._last_signal_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze market data for ATR volatility-based signals.
        
        Args:
            market_data: List of market data points
            
        Returns:
            Optional[TradingSignal]: High-confidence volatility signal
        """
        if len(market_data) < self.get_required_data_length():
            return None
        
        try:
            # Extract data
            prices = [float(data.close) for data in market_data]
            highs = [float(data.high) for data in market_data]
            lows = [float(data.low) for data in market_data]
            volumes = [float(data.volume) for data in market_data]
            
            current_data = market_data[-1]
            current_price = float(current_data.close)
            
            # Update history
            self._update_history(prices, volumes)
            
            # Calculate ATR and volatility indicators
            volatility_analysis = self._calculate_volatility_indicators(prices, highs, lows, volumes)
            
            if not volatility_analysis:
                return None
            
            # Detect volatility patterns
            pattern_analysis = self._detect_volatility_patterns(volatility_analysis, current_price)
            
            # Analyze breakout conditions
            breakout_analysis = self._analyze_breakout_conditions(volatility_analysis, current_price)
            
            # Apply trend filter if enabled
            trend_analysis = self._analyze_trend_context(prices) if self.trend_filter else {'trend_aligned': True}
            
            # Generate signal if conditions are met
            signal = self._generate_volatility_signal(
                current_data, volatility_analysis, pattern_analysis, 
                breakout_analysis, trend_analysis
            )
            
            if signal:
                self.logger.info(f"ATR Volatility signal: {signal.action.value} "
                               f"(confidence: {signal.confidence:.3f})")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in ATR volatility analysis: {str(e)}")
            return None
    
    def get_required_data_length(self) -> int:
        """Get minimum data points required."""
        return max(self.atr_period, self.lookback_period) + 20
    
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        try:
            # Validate ATR parameters
            if self.atr_period <= 0:
                self.logger.error("ATR period must be positive")
                return False
            
            if self.atr_multiplier <= 0:
                self.logger.error("ATR multiplier must be positive")
                return False
            
            # Validate thresholds
            if self.volatility_threshold <= 0:
                self.logger.error("Volatility threshold must be positive")
                return False
            
            if not (0.0 < self.squeeze_threshold < self.expansion_threshold):
                self.logger.error("Squeeze threshold must be less than expansion threshold")
                return False
            
            if not (0.0 <= self.min_confidence <= 1.0):
                self.logger.error("min_confidence must be between 0.0 and 1.0")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _update_history(self, prices: List[float], volumes: List[float]):
        """Update internal history buffers."""
        self._price_history = prices[-self.lookback_period:]
        self._volume_history = volumes[-self.lookback_period:]
    
    def _calculate_volatility_indicators(self, prices: List[float], highs: List[float], 
                                       lows: List[float], volumes: List[float]) -> Optional[Dict[str, Any]]:
        """Calculate ATR and volatility indicators."""
        try:
            indicators = {}
            
            # 1. Calculate ATR
            atr_values = self._calculate_atr(highs, lows, prices)
            if not atr_values:
                return None
            
            current_atr = atr_values[-1]
            indicators['current_atr'] = current_atr
            indicators['atr_values'] = atr_values[-20:]  # Keep recent ATR values
            
            # Store ATR history
            self._atr_history.append(current_atr)
            if len(self._atr_history) > self.lookback_period:
                self._atr_history = self._atr_history[-self.lookback_period:]
            
            # 2. ATR-based volatility analysis
            if len(self._atr_history) >= 20:
                atr_ma = sum(self._atr_history[-20:]) / 20
                atr_ratio = current_atr / atr_ma if atr_ma > 0 else 1.0
                
                indicators['atr_ma'] = atr_ma
                indicators['atr_ratio'] = atr_ratio
                indicators['volatility_state'] = self._classify_volatility_state(atr_ratio)
            
            # 3. True Range analysis
            if len(highs) >= 2 and len(lows) >= 2 and len(prices) >= 2:
                true_range = max(
                    highs[-1] - lows[-1],
                    abs(highs[-1] - prices[-2]),
                    abs(lows[-1] - prices[-2])
                )
                indicators['true_range'] = true_range
                indicators['tr_normalized'] = true_range / prices[-1] if prices[-1] > 0 else 0
            
            # 4. Volatility percentile
            if len(self._atr_history) >= 20:
                sorted_atr = sorted(self._atr_history[-20:])
                percentile_rank = (sorted_atr.index(current_atr) + 1) / len(sorted_atr)
                indicators['volatility_percentile'] = percentile_rank
            
            # 5. Volume-volatility correlation
            if len(volumes) >= 20 and len(self._atr_history) >= 20:
                recent_volumes = volumes[-20:]
                recent_atr = self._atr_history[-20:]
                correlation = self._calculate_correlation(recent_volumes, recent_atr)
                indicators['volume_volatility_correlation'] = correlation
            
            # 6. Volatility momentum
            if len(self._atr_history) >= 5:
                atr_momentum = (self._atr_history[-1] - self._atr_history[-5]) / self._atr_history[-5]
                indicators['volatility_momentum'] = atr_momentum
            
            # 7. ATR-based breakout levels
            current_price = prices[-1]
            upper_breakout = current_price + (current_atr * self.atr_multiplier)
            lower_breakout = current_price - (current_atr * self.atr_multiplier)
            
            indicators['upper_breakout'] = upper_breakout
            indicators['lower_breakout'] = lower_breakout
            
            # Update breakout levels
            self._breakout_levels['upper'] = upper_breakout
            self._breakout_levels['lower'] = lower_breakout
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility indicators: {str(e)}")
            return None
    
    def _calculate_atr(self, highs: List[float], lows: List[float], closes: List[float]) -> Optional[List[float]]:
        """Calculate Average True Range."""
        try:
            if len(highs) < self.atr_period + 1:
                return None
            
            # Calculate True Range for each period
            true_ranges = []
            for i in range(1, len(highs)):
                tr = max(
                    highs[i] - lows[i],
                    abs(highs[i] - closes[i-1]),
                    abs(lows[i] - closes[i-1])
                )
                true_ranges.append(tr)
            
            # Calculate ATR using simple moving average
            atr_values = []
            for i in range(self.atr_period - 1, len(true_ranges)):
                atr = sum(true_ranges[i - self.atr_period + 1:i + 1]) / self.atr_period
                atr_values.append(atr)
            
            return atr_values
            
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {str(e)}")
            return None
    
    def _classify_volatility_state(self, atr_ratio: float) -> str:
        """Classify current volatility state."""
        if atr_ratio <= self.squeeze_threshold:
            return 'squeeze'
        elif atr_ratio >= self.expansion_threshold:
            return 'expansion'
        elif atr_ratio > 1.0:
            return 'elevated'
        else:
            return 'normal'
    
    def _detect_volatility_patterns(self, indicators: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Detect volatility patterns and signals."""
        patterns = {
            'squeeze_breakout': False,
            'volatility_expansion': False,
            'volatility_contraction': False,
            'volume_confirmation': False,
            'pattern_strength': 0.0
        }
        
        try:
            volatility_state = indicators.get('volatility_state', 'normal')
            atr_ratio = indicators.get('atr_ratio', 1.0)
            vol_momentum = indicators.get('volatility_momentum', 0.0)
            vol_correlation = indicators.get('volume_volatility_correlation', 0.0)
            
            # 1. Volatility squeeze breakout
            if len(self._atr_history) >= 10:
                recent_states = [self._classify_volatility_state(
                    atr / (sum(self._atr_history[-20:-10]) / 10) if sum(self._atr_history[-20:-10]) > 0 else 1.0
                ) for atr in self._atr_history[-10:]]
                
                squeeze_count = recent_states.count('squeeze')
                if squeeze_count >= 5 and volatility_state in ['elevated', 'expansion']:
                    patterns['squeeze_breakout'] = True
                    patterns['pattern_strength'] += 0.25
            
            # 2. Volatility expansion
            if volatility_state == 'expansion' and vol_momentum > 0.2:
                patterns['volatility_expansion'] = True
                patterns['pattern_strength'] += 0.20
            
            # 3. Volatility contraction
            if volatility_state == 'squeeze' and vol_momentum < -0.1:
                patterns['volatility_contraction'] = True
                patterns['pattern_strength'] += 0.15
            
            # 4. Volume confirmation
            if abs(vol_correlation) >= self.volume_correlation:
                patterns['volume_confirmation'] = True
                patterns['pattern_strength'] += 0.15
            
            # 5. Volatility percentile extremes
            vol_percentile = indicators.get('volatility_percentile', 0.5)
            if vol_percentile <= 0.2 or vol_percentile >= 0.8:
                patterns['pattern_strength'] += 0.10
            
        except Exception as e:
            self.logger.error(f"Error detecting volatility patterns: {str(e)}")
        
        return patterns
    
    def _analyze_breakout_conditions(self, indicators: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Analyze breakout conditions based on ATR levels."""
        breakout = {
            'bullish_breakout': False,
            'bearish_breakout': False,
            'breakout_strength': 0.0,
            'breakout_type': None
        }
        
        try:
            upper_level = indicators.get('upper_breakout')
            lower_level = indicators.get('lower_breakout')
            current_atr = indicators.get('current_atr', 0)
            
            if not upper_level or not lower_level:
                return breakout
            
            # Check for price breakouts
            price_above_upper = current_price > upper_level
            price_below_lower = current_price < lower_level
            
            # Calculate breakout strength
            if price_above_upper:
                breakout_distance = current_price - upper_level
                breakout_strength = breakout_distance / current_atr if current_atr > 0 else 0
                
                if breakout_strength >= 0.5:  # Significant breakout
                    breakout['bullish_breakout'] = True
                    breakout['breakout_strength'] = min(breakout_strength, 2.0)
                    breakout['breakout_type'] = 'upside_breakout'
            
            elif price_below_lower:
                breakout_distance = lower_level - current_price
                breakout_strength = breakout_distance / current_atr if current_atr > 0 else 0
                
                if breakout_strength >= 0.5:  # Significant breakout
                    breakout['bearish_breakout'] = True
                    breakout['breakout_strength'] = min(breakout_strength, 2.0)
                    breakout['breakout_type'] = 'downside_breakout'
            
            # Check for false breakout conditions
            if len(self._price_history) >= 5:
                recent_prices = self._price_history[-5:]
                price_volatility = np.std(recent_prices) / np.mean(recent_prices)
                
                # Reduce breakout strength for high recent volatility (potential false breakout)
                if price_volatility > 0.02:  # 2% volatility
                    breakout['breakout_strength'] *= 0.7
            
        except Exception as e:
            self.logger.error(f"Error analyzing breakout conditions: {str(e)}")
        
        return breakout
    
    def _analyze_trend_context(self, prices: List[float]) -> Dict[str, Any]:
        """Analyze trend context for signal filtering."""
        trend = {
            'trend_direction': 'neutral',
            'trend_strength': 0.0,
            'trend_aligned': True
        }
        
        try:
            if len(prices) < 20:
                return trend
            
            # Simple trend analysis using moving averages
            short_ma = sum(prices[-10:]) / 10
            long_ma = sum(prices[-20:]) / 20
            current_price = prices[-1]
            
            # Determine trend direction
            if short_ma > long_ma and current_price > short_ma:
                trend['trend_direction'] = 'bullish'
                trend['trend_strength'] = (short_ma - long_ma) / long_ma
            elif short_ma < long_ma and current_price < short_ma:
                trend['trend_direction'] = 'bearish'
                trend['trend_strength'] = (long_ma - short_ma) / long_ma
            else:
                trend['trend_direction'] = 'neutral'
                trend['trend_strength'] = 0.0
            
            # Trend strength classification
            if trend['trend_strength'] > 0.02:  # 2% difference
                trend['trend_aligned'] = True
            else:
                trend['trend_aligned'] = False
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend context: {str(e)}")
        
        return trend
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two series."""
        try:
            if len(x) != len(y) or len(x) < 2:
                return 0.0
            
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            sum_y2 = sum(yi * yi for yi in y)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {str(e)}")
            return 0.0
    
    def _generate_volatility_signal(self, market_data: MarketData, volatility_analysis: Dict[str, Any],
                                  pattern_analysis: Dict[str, Any], breakout_analysis: Dict[str, Any],
                                  trend_analysis: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generate volatility-based trading signal."""
        try:
            # Check cooldown
            if (self._last_signal_time and 
                (market_data.timestamp - self._last_signal_time).total_seconds() < 2700):  # 45 min
                return None
            
            # Determine signal conditions
            bullish_conditions = 0
            bearish_conditions = 0
            signal_strength = 0.0
            
            # 1. Breakout conditions
            if breakout_analysis['bullish_breakout']:
                bullish_conditions += 2
                signal_strength += breakout_analysis['breakout_strength'] * 0.3
            
            if breakout_analysis['bearish_breakout']:
                bearish_conditions += 2
                signal_strength += breakout_analysis['breakout_strength'] * 0.3
            
            # 2. Volatility patterns
            if pattern_analysis['squeeze_breakout']:
                # Squeeze breakout can be bullish or bearish - use trend context
                if trend_analysis['trend_direction'] == 'bullish':
                    bullish_conditions += 1
                elif trend_analysis['trend_direction'] == 'bearish':
                    bearish_conditions += 1
                signal_strength += 0.2
            
            if pattern_analysis['volatility_expansion']:
                # Volatility expansion - use price momentum
                current_price = float(market_data.close)
                if len(self._price_history) >= 5:
                    price_momentum = (current_price - self._price_history[-5]) / self._price_history[-5]
                    if price_momentum > 0.01:  # 1% positive momentum
                        bullish_conditions += 1
                    elif price_momentum < -0.01:  # 1% negative momentum
                        bearish_conditions += 1
                signal_strength += 0.15
            
            # 3. Volume confirmation
            if pattern_analysis['volume_confirmation']:
                bullish_conditions += 1 if bullish_conditions > bearish_conditions else 0
                bearish_conditions += 1 if bearish_conditions > bullish_conditions else 0
                signal_strength += 0.1
            
            # 4. Trend alignment (if enabled)
            if self.trend_filter and not trend_analysis['trend_aligned']:
                # Reduce signal strength for counter-trend signals
                signal_strength *= 0.6
            
            # 5. Pattern strength bonus
            signal_strength += pattern_analysis['pattern_strength']
            
            # Determine signal direction
            min_conditions = 2  # Minimum conditions for signal
            action = None
            
            if bullish_conditions >= min_conditions and bullish_conditions > bearish_conditions:
                action = SignalAction.BUY
            elif bearish_conditions >= min_conditions and bearish_conditions > bullish_conditions:
                action = SignalAction.SELL
            else:
                return None
            
            # Calculate confidence
            base_confidence = 0.7
            condition_bonus = min((bullish_conditions if action == SignalAction.BUY else bearish_conditions) * 0.05, 0.15)
            strength_bonus = min(signal_strength, 0.2)
            
            # ATR quality bonus
            atr_ratio = volatility_analysis.get('atr_ratio', 1.0)
            volatility_state = volatility_analysis.get('volatility_state', 'normal')
            
            quality_bonus = 0.0
            if volatility_state in ['squeeze', 'expansion']:
                quality_bonus += 0.05
            if breakout_analysis['breakout_strength'] > 1.0:
                quality_bonus += 0.03
            
            confidence = base_confidence + condition_bonus + strength_bonus + quality_bonus
            confidence = min(confidence, 1.0)
            
            if confidence < self.min_confidence:
                return None
            
            # Update state
            self._last_signal = action
            self._last_signal_time = market_data.timestamp
            
            # Calculate ATR-based stop loss and take profit
            current_atr = volatility_analysis.get('current_atr', 0)
            stop_loss_distance = current_atr * 1.5  # 1.5x ATR stop loss
            take_profit_distance = current_atr * 3.0  # 3x ATR take profit (2:1 R/R)
            
            return TradingSignal(
                symbol=market_data.symbol,
                action=action,
                confidence=confidence,
                timestamp=market_data.timestamp,
                strategy_name=self.name,
                price=market_data.close,
                metadata={
                    'volatility_conditions': bullish_conditions if action == SignalAction.BUY else bearish_conditions,
                    'signal_strength': signal_strength,
                    'volatility_state': volatility_analysis.get('volatility_state'),
                    'atr_ratio': volatility_analysis.get('atr_ratio'),
                    'breakout_type': breakout_analysis.get('breakout_type'),
                    'breakout_strength': breakout_analysis.get('breakout_strength'),
                    'pattern_strength': pattern_analysis['pattern_strength'],
                    'volume_confirmation': pattern_analysis['volume_confirmation'],
                    'trend_direction': trend_analysis['trend_direction'],
                    'current_atr': current_atr,
                    'atr_stop_loss': stop_loss_distance,
                    'atr_take_profit': take_profit_distance,
                    'upper_breakout': volatility_analysis.get('upper_breakout'),
                    'lower_breakout': volatility_analysis.get('lower_breakout'),
                    'volatility_percentile': volatility_analysis.get('volatility_percentile'),
                    'strategy_type': 'atr_volatility'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error generating volatility signal: {str(e)}")
            return None