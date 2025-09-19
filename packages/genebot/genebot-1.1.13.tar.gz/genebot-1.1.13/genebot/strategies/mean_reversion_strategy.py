"""
Advanced Mean Reversion Strategy for high-probability reversal signals.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

from .base_strategy import BaseStrategy, StrategyConfig
from .technical_indicators import TechnicalIndicators
from ..models.data_models import MarketData, TradingSignal, SignalAction


class MeanReversionStrategy(BaseStrategy):
    """
    Advanced Mean Reversion Strategy for high-probability reversal trading.
    
    This strategy identifies extreme price deviations and high-probability reversals:
    - Multi-timeframe mean reversion analysis
    - Statistical deviation measurement
    - Volume profile analysis
    - Support/resistance confluence
    - Oversold/overbought extremes
    - Market structure analysis
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the Mean Reversion Strategy.
        
        Args:
            config: Strategy configuration containing parameters:
                - bb_period: Bollinger Bands period (default: 20)
                - bb_std_dev: Bollinger Bands standard deviation (default: 2.5)
                - rsi_period: RSI period (default: 14)
                - rsi_extreme_oversold: Extreme oversold level (default: 20)
                - rsi_extreme_overbought: Extreme overbought level (default: 80)
                - stoch_period: Stochastic period (default: 14)
                - deviation_threshold: Price deviation threshold (default: 2.0)
                - volume_confirmation: Volume confirmation multiplier (default: 1.5)
                - mean_periods: Mean calculation periods (default: [10, 20, 50])
                - min_confluence: Minimum confluence signals (default: 4)
                - min_confidence: Minimum confidence threshold (default: 0.87)
        """
        super().__init__(config)
        
        # Extract parameters
        self.bb_period = self.parameters.get('bb_period', 20)
        self.bb_std_dev = self.parameters.get('bb_std_dev', 2.5)
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.rsi_extreme_oversold = self.parameters.get('rsi_extreme_oversold', 20)
        self.rsi_extreme_overbought = self.parameters.get('rsi_extreme_overbought', 80)
        self.stoch_period = self.parameters.get('stoch_period', 14)
        self.deviation_threshold = self.parameters.get('deviation_threshold', 2.0)
        self.volume_confirmation = self.parameters.get('volume_confirmation', 1.5)
        self.mean_periods = self.parameters.get('mean_periods', [10, 20, 50])
        self.min_confluence = self.parameters.get('min_confluence', 4)
        self.min_confidence = self.parameters.get('min_confidence', 0.87)
        
        # Technical indicators
        self.indicators = TechnicalIndicators()
        
        # Strategy state
        self._price_history = []
        self._volume_history = []
        self._deviation_history = []
        self._support_levels = []
        self._resistance_levels = []
        self._last_signal = None
        self._last_signal_time = None
        
        self.logger = logging.getLogger(f"strategy.mean_reversion.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the strategy."""
        try:
            self.logger.info(f"Initializing Mean Reversion Strategy: {self.name}")
            self.logger.info(f"BB period: {self.bb_period}, std dev: {self.bb_std_dev}")
            self.logger.info(f"RSI extremes: {self.rsi_extreme_oversold}-{self.rsi_extreme_overbought}")
            
            # Clear state
            self._price_history.clear()
            self._volume_history.clear()
            self._deviation_history.clear()
            self._support_levels.clear()
            self._resistance_levels.clear()
            self._last_signal = None
            self._last_signal_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze market data for mean reversion signals.
        
        Args:
            market_data: List of market data points
            
        Returns:
            Optional[TradingSignal]: High-confidence mean reversion signal
        """
        if len(market_data) < self.get_required_data_length():
            return None
        
        try:
            # Extract data
            prices = [float(data.close) for data in market_data]
            volumes = [float(data.volume) for data in market_data]
            highs = [float(data.high) for data in market_data]
            lows = [float(data.low) for data in market_data]
            
            current_data = market_data[-1]
            current_price = float(current_data.close)
            
            # Update history
            self._update_history(prices, volumes, highs, lows)
            
            # Calculate mean reversion indicators
            reversion_analysis = self._calculate_reversion_indicators(prices, volumes, highs, lows)
            
            if not reversion_analysis:
                return None
            
            # Analyze confluence for reversal signals
            confluence_analysis = self._analyze_reversion_confluence(reversion_analysis, current_price)
            
            # Check market structure
            structure_analysis = self._analyze_market_structure(prices, highs, lows)
            
            # Generate signal if conditions are met
            signal = self._generate_reversion_signal(
                current_data, confluence_analysis, structure_analysis, reversion_analysis
            )
            
            if signal:
                self.logger.info(f"Mean reversion signal: {signal.action.value} "
                               f"(confidence: {signal.confidence:.3f})")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in mean reversion analysis: {str(e)}")
            return None
    
    def get_required_data_length(self) -> int:
        """Get minimum data points required."""
        return max(
            self.bb_period,
            self.rsi_period,
            self.stoch_period,
            max(self.mean_periods)
        ) + 30
    
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        try:
            # Validate Bollinger Bands
            if self.bb_period <= 0 or self.bb_std_dev <= 0:
                self.logger.error("BB parameters must be positive")
                return False
            
            # Validate RSI
            if not (0 < self.rsi_extreme_oversold < self.rsi_extreme_overbought < 100):
                self.logger.error("Invalid RSI extreme levels")
                return False
            
            # Validate other parameters
            if self.deviation_threshold <= 0:
                self.logger.error("Deviation threshold must be positive")
                return False
            
            if not all(p > 0 for p in self.mean_periods):
                self.logger.error("All mean periods must be positive")
                return False
            
            if not (0.0 <= self.min_confidence <= 1.0):
                self.logger.error("min_confidence must be between 0.0 and 1.0")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _update_history(self, prices: List[float], volumes: List[float], 
                       highs: List[float], lows: List[float]):
        """Update internal history buffers."""
        self._price_history = prices[-100:]
        self._volume_history = volumes[-100:]
        
        # Update support/resistance levels
        self._update_support_resistance(prices[-50:], highs[-50:], lows[-50:])
    
    def _calculate_reversion_indicators(self, prices: List[float], volumes: List[float],
                                      highs: List[float], lows: List[float]) -> Optional[Dict[str, Any]]:
        """Calculate mean reversion indicators."""
        try:
            indicators = {}
            current_price = prices[-1]
            
            # 1. Bollinger Bands analysis
            bb_result = self.indicators.bollinger_bands(prices, self.bb_period, self.bb_std_dev)
            if bb_result:
                upper, middle, lower = bb_result
                bb_position = (current_price - lower) / (upper - lower) if upper != lower else 0.5
                bb_width = (upper - lower) / middle if middle > 0 else 0.0
                
                indicators['bb_upper'] = upper
                indicators['bb_middle'] = middle
                indicators['bb_lower'] = lower
                indicators['bb_position'] = bb_position
                indicators['bb_width'] = bb_width
                
                # Extreme positions
                indicators['bb_extreme_low'] = bb_position <= 0.05
                indicators['bb_extreme_high'] = bb_position >= 0.95
            
            # 2. Multi-timeframe mean analysis
            mean_deviations = {}
            for period in self.mean_periods:
                if len(prices) >= period:
                    mean_price = sum(prices[-period:]) / period
                    deviation = (current_price - mean_price) / mean_price * 100
                    mean_deviations[f'mean_{period}'] = {
                        'mean': mean_price,
                        'deviation': deviation,
                        'extreme': abs(deviation) > self.deviation_threshold
                    }
            
            indicators['mean_deviations'] = mean_deviations
            
            # 3. RSI extremes
            rsi = self.indicators.rsi(prices, self.rsi_period)
            if rsi is not None:
                indicators['rsi'] = rsi
                indicators['rsi_extreme_oversold'] = rsi <= self.rsi_extreme_oversold
                indicators['rsi_extreme_overbought'] = rsi >= self.rsi_extreme_overbought
            
            # 4. Stochastic extremes
            stoch_result = self.indicators.stochastic(highs, lows, prices, self.stoch_period, 3)
            if stoch_result:
                k_percent, d_percent = stoch_result
                indicators['stoch_k'] = k_percent
                indicators['stoch_d'] = d_percent
                indicators['stoch_extreme_oversold'] = k_percent <= 10 and d_percent <= 10
                indicators['stoch_extreme_overbought'] = k_percent >= 90 and d_percent >= 90
            
            # 5. Statistical deviation
            if len(prices) >= 20:
                recent_prices = prices[-20:]
                price_mean = sum(recent_prices) / len(recent_prices)
                price_std = np.std(recent_prices)
                
                z_score = (current_price - price_mean) / price_std if price_std > 0 else 0
                indicators['z_score'] = z_score
                indicators['z_extreme'] = abs(z_score) > 2.0
            
            # 6. Volume analysis
            if len(volumes) >= 20:
                avg_volume = sum(volumes[-20:]) / 20
                volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1.0
                indicators['volume_ratio'] = volume_ratio
                indicators['volume_spike'] = volume_ratio >= self.volume_confirmation
            
            # 7. Price exhaustion patterns
            exhaustion_analysis = self._analyze_price_exhaustion(prices, highs, lows)
            indicators.update(exhaustion_analysis)
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating reversion indicators: {str(e)}")
            return None
    
    def _analyze_price_exhaustion(self, prices: List[float], highs: List[float], 
                                lows: List[float]) -> Dict[str, Any]:
        """Analyze price exhaustion patterns."""
        exhaustion = {}
        
        try:
            if len(prices) < 10:
                return exhaustion
            
            # 1. Consecutive moves in same direction
            consecutive_up = 0
            consecutive_down = 0
            
            for i in range(len(prices) - 1, max(0, len(prices) - 8), -1):
                if i > 0:
                    if prices[i] > prices[i-1]:
                        consecutive_up += 1
                        if consecutive_down > 0:
                            break
                    elif prices[i] < prices[i-1]:
                        consecutive_down += 1
                        if consecutive_up > 0:
                            break
                    else:
                        break
            
            exhaustion['consecutive_up'] = consecutive_up
            exhaustion['consecutive_down'] = consecutive_down
            exhaustion['exhaustion_up'] = consecutive_up >= 5
            exhaustion['exhaustion_down'] = consecutive_down >= 5
            
            # 2. Diminishing momentum
            if len(prices) >= 6:
                recent_moves = [prices[i] - prices[i-1] for i in range(-5, 0)]
                if len(recent_moves) >= 4:
                    # Check if moves are getting smaller
                    avg_early = abs(sum(recent_moves[:2]) / 2)
                    avg_late = abs(sum(recent_moves[-2:]) / 2)
                    
                    exhaustion['diminishing_momentum'] = avg_late < avg_early * 0.5
            
            # 3. Wick analysis (rejection patterns)
            if len(highs) >= 3 and len(lows) >= 3:
                current_high = highs[-1]
                current_low = lows[-1]
                current_close = prices[-1]
                current_open = prices[-1]  # Approximation
                
                # Upper wick (potential resistance)
                upper_wick = (current_high - max(current_open, current_close)) / current_high
                # Lower wick (potential support)
                lower_wick = (min(current_open, current_close) - current_low) / current_high
                
                exhaustion['upper_wick_rejection'] = upper_wick > 0.02  # 2% wick
                exhaustion['lower_wick_support'] = lower_wick > 0.02  # 2% wick
            
        except Exception as e:
            self.logger.error(f"Error analyzing price exhaustion: {str(e)}")
        
        return exhaustion
    
    def _analyze_reversion_confluence(self, indicators: Dict[str, Any], 
                                    current_price: float) -> Dict[str, Any]:
        """Analyze confluence for mean reversion signals."""
        confluence = {
            'bullish_reversion_count': 0,
            'bearish_reversion_count': 0,
            'bullish_signals': [],
            'bearish_signals': [],
            'strength': 0.0
        }
        
        try:
            # 1. Bollinger Bands extremes
            if indicators.get('bb_extreme_low'):
                confluence['bullish_reversion_count'] += 1
                confluence['bullish_signals'].append('BB_Extreme_Oversold')
                confluence['strength'] += 0.15
            
            if indicators.get('bb_extreme_high'):
                confluence['bearish_reversion_count'] += 1
                confluence['bearish_signals'].append('BB_Extreme_Overbought')
                confluence['strength'] += 0.15
            
            # 2. RSI extremes
            if indicators.get('rsi_extreme_oversold'):
                confluence['bullish_reversion_count'] += 1
                confluence['bullish_signals'].append('RSI_Extreme_Oversold')
                confluence['strength'] += 0.12
            
            if indicators.get('rsi_extreme_overbought'):
                confluence['bearish_reversion_count'] += 1
                confluence['bearish_signals'].append('RSI_Extreme_Overbought')
                confluence['strength'] += 0.12
            
            # 3. Stochastic extremes
            if indicators.get('stoch_extreme_oversold'):
                confluence['bullish_reversion_count'] += 1
                confluence['bullish_signals'].append('Stoch_Extreme_Oversold')
                confluence['strength'] += 0.10
            
            if indicators.get('stoch_extreme_overbought'):
                confluence['bearish_reversion_count'] += 1
                confluence['bearish_signals'].append('Stoch_Extreme_Overbought')
                confluence['strength'] += 0.10
            
            # 4. Mean deviation extremes
            mean_deviations = indicators.get('mean_deviations', {})
            extreme_negative = sum(1 for data in mean_deviations.values() 
                                 if data['deviation'] < -self.deviation_threshold)
            extreme_positive = sum(1 for data in mean_deviations.values() 
                                 if data['deviation'] > self.deviation_threshold)
            
            if extreme_negative >= 2:
                confluence['bullish_reversion_count'] += 1
                confluence['bullish_signals'].append('Mean_Deviation_Oversold')
                confluence['strength'] += 0.13
            
            if extreme_positive >= 2:
                confluence['bearish_reversion_count'] += 1
                confluence['bearish_signals'].append('Mean_Deviation_Overbought')
                confluence['strength'] += 0.13
            
            # 5. Statistical Z-score extreme
            if indicators.get('z_extreme'):
                z_score = indicators.get('z_score', 0)
                if z_score < -2.0:
                    confluence['bullish_reversion_count'] += 1
                    confluence['bullish_signals'].append('Z_Score_Oversold')
                    confluence['strength'] += 0.11
                elif z_score > 2.0:
                    confluence['bearish_reversion_count'] += 1
                    confluence['bearish_signals'].append('Z_Score_Overbought')
                    confluence['strength'] += 0.11
            
            # 6. Volume confirmation
            if indicators.get('volume_spike'):
                # Volume spike adds to both directions (confirmation)
                if confluence['bullish_reversion_count'] > 0:
                    confluence['bullish_signals'].append('Volume_Confirmation')
                    confluence['strength'] += 0.08
                if confluence['bearish_reversion_count'] > 0:
                    confluence['bearish_signals'].append('Volume_Confirmation')
                    confluence['strength'] += 0.08
            
            # 7. Price exhaustion patterns
            if indicators.get('exhaustion_up'):
                confluence['bearish_reversion_count'] += 1
                confluence['bearish_signals'].append('Price_Exhaustion_Up')
                confluence['strength'] += 0.09
            
            if indicators.get('exhaustion_down'):
                confluence['bullish_reversion_count'] += 1
                confluence['bullish_signals'].append('Price_Exhaustion_Down')
                confluence['strength'] += 0.09
            
            # 8. Wick rejections
            if indicators.get('upper_wick_rejection'):
                confluence['bearish_reversion_count'] += 1
                confluence['bearish_signals'].append('Upper_Wick_Rejection')
                confluence['strength'] += 0.07
            
            if indicators.get('lower_wick_support'):
                confluence['bullish_reversion_count'] += 1
                confluence['bullish_signals'].append('Lower_Wick_Support')
                confluence['strength'] += 0.07
            
            # 9. Support/Resistance confluence
            if self._is_near_support(current_price):
                confluence['bullish_reversion_count'] += 1
                confluence['bullish_signals'].append('Support_Level_Confluence')
                confluence['strength'] += 0.10
            
            if self._is_near_resistance(current_price):
                confluence['bearish_reversion_count'] += 1
                confluence['bearish_signals'].append('Resistance_Level_Confluence')
                confluence['strength'] += 0.10
            
        except Exception as e:
            self.logger.error(f"Error analyzing reversion confluence: {str(e)}")
        
        return confluence
    
    def _analyze_market_structure(self, prices: List[float], highs: List[float], 
                                lows: List[float]) -> Dict[str, Any]:
        """Analyze market structure for additional confirmation."""
        structure = {
            'trend_strength': 0.0,
            'structure_support': False,
            'structure_resistance': False
        }
        
        try:
            if len(prices) < 20:
                return structure
            
            # Trend analysis
            short_ma = sum(prices[-10:]) / 10
            long_ma = sum(prices[-20:]) / 20
            
            trend_strength = abs(short_ma - long_ma) / long_ma if long_ma > 0 else 0
            structure['trend_strength'] = trend_strength
            
            # Structure levels (simplified)
            recent_highs = highs[-20:]
            recent_lows = lows[-20:]
            
            # Find significant levels
            max_high = max(recent_highs)
            min_low = min(recent_lows)
            current_price = prices[-1]
            
            # Check if near structure levels
            price_range = max_high - min_low
            if price_range > 0:
                distance_to_high = abs(current_price - max_high) / price_range
                distance_to_low = abs(current_price - min_low) / price_range
                
                structure['structure_resistance'] = distance_to_high <= 0.02  # Within 2%
                structure['structure_support'] = distance_to_low <= 0.02  # Within 2%
            
        except Exception as e:
            self.logger.error(f"Error analyzing market structure: {str(e)}")
        
        return structure
    
    def _update_support_resistance(self, prices: List[float], highs: List[float], lows: List[float]):
        """Update support and resistance levels."""
        try:
            if len(prices) < 20:
                return
            
            # Simple pivot point detection
            support_levels = []
            resistance_levels = []
            
            for i in range(2, len(lows) - 2):
                # Support (local low)
                if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                    lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                    support_levels.append(lows[i])
                
                # Resistance (local high)
                if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                    highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                    resistance_levels.append(highs[i])
            
            # Keep only recent and significant levels
            current_price = prices[-1]
            
            # Filter support levels (within 10% below current price)
            self._support_levels = [level for level in support_levels 
                                  if 0.9 * current_price <= level <= current_price][-5:]
            
            # Filter resistance levels (within 10% above current price)
            self._resistance_levels = [level for level in resistance_levels 
                                     if current_price <= level <= 1.1 * current_price][-5:]
            
        except Exception as e:
            self.logger.error(f"Error updating support/resistance: {str(e)}")
    
    def _is_near_support(self, price: float) -> bool:
        """Check if price is near a support level."""
        for level in self._support_levels:
            if abs(price - level) / price <= 0.01:  # Within 1%
                return True
        return False
    
    def _is_near_resistance(self, price: float) -> bool:
        """Check if price is near a resistance level."""
        for level in self._resistance_levels:
            if abs(price - level) / price <= 0.01:  # Within 1%
                return True
        return False
    
    def _generate_reversion_signal(self, market_data: MarketData, confluence_analysis: Dict[str, Any],
                                 structure_analysis: Dict[str, Any], 
                                 indicators: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generate mean reversion trading signal."""
        try:
            # Check cooldown
            if (self._last_signal_time and 
                (market_data.timestamp - self._last_signal_time).total_seconds() < 2700):  # 45 min
                return None
            
            # Determine signal direction
            bullish_count = confluence_analysis['bullish_reversion_count']
            bearish_count = confluence_analysis['bearish_reversion_count']
            
            # Add structure confirmation
            if structure_analysis['structure_support'] and bullish_count > 0:
                bullish_count += 1
            if structure_analysis['structure_resistance'] and bearish_count > 0:
                bearish_count += 1
            
            # Check minimum confluence
            if bullish_count < self.min_confluence and bearish_count < self.min_confluence:
                return None
            
            # Determine action
            action = None
            signal_count = 0
            
            if bullish_count >= self.min_confluence and bullish_count > bearish_count:
                action = SignalAction.BUY
                signal_count = bullish_count
            elif bearish_count >= self.min_confluence and bearish_count > bullish_count:
                action = SignalAction.SELL
                signal_count = bearish_count
            else:
                return None
            
            # Calculate confidence
            base_confidence = 0.75
            confluence_bonus = min(signal_count * 0.025, 0.15)
            strength_bonus = min(confluence_analysis['strength'], 0.12)
            
            confidence = base_confidence + confluence_bonus + strength_bonus
            confidence = min(confidence, 1.0)
            
            if confidence < self.min_confidence:
                return None
            
            # Update state
            self._last_signal = action
            self._last_signal_time = market_data.timestamp
            
            return TradingSignal(
                symbol=market_data.symbol,
                action=action,
                confidence=confidence,
                timestamp=market_data.timestamp,
                strategy_name=self.name,
                price=market_data.close,
                metadata={
                    'reversion_signals': (confluence_analysis['bullish_signals'] 
                                        if action == SignalAction.BUY 
                                        else confluence_analysis['bearish_signals']),
                    'confluence_count': signal_count,
                    'confluence_strength': confluence_analysis['strength'],
                    'bb_position': indicators.get('bb_position'),
                    'rsi': indicators.get('rsi'),
                    'z_score': indicators.get('z_score'),
                    'volume_ratio': indicators.get('volume_ratio'),
                    'mean_deviations': indicators.get('mean_deviations'),
                    'structure_support': structure_analysis['structure_support'],
                    'structure_resistance': structure_analysis['structure_resistance'],
                    'support_levels_count': len(self._support_levels),
                    'resistance_levels_count': len(self._resistance_levels),
                    'strategy_type': 'mean_reversion'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error generating reversion signal: {str(e)}")
            return None