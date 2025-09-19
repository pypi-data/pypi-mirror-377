"""
Advanced Momentum Strategy combining multiple momentum indicators for high-probability signals.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

from .base_strategy import BaseStrategy, StrategyConfig
from .technical_indicators import TechnicalIndicators
from ..models.data_models import MarketData, TradingSignal, SignalAction


class AdvancedMomentumStrategy(BaseStrategy):
    """
    Advanced Momentum Strategy for high-probability momentum trading.
    
    This strategy combines multiple momentum indicators with advanced filtering:
    - Multi-timeframe momentum analysis
    - Momentum divergence detection
    - Acceleration and velocity analysis
    - Volume-weighted momentum
    - Momentum breakout confirmation
    - Dynamic stop-loss and take-profit levels
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the Advanced Momentum Strategy.
        
        Args:
            config: Strategy configuration containing parameters:
                - momentum_periods: List of momentum periods (default: [5, 10, 20])
                - roc_periods: Rate of change periods (default: [3, 7, 14])
                - rsi_period: RSI period (default: 14)
                - stoch_k_period: Stochastic %K period (default: 14)
                - stoch_d_period: Stochastic %D period (default: 3)
                - macd_fast: MACD fast period (default: 12)
                - macd_slow: MACD slow period (default: 26)
                - macd_signal: MACD signal period (default: 9)
                - volume_ma_period: Volume moving average period (default: 20)
                - momentum_threshold: Minimum momentum threshold (default: 2.0)
                - divergence_lookback: Divergence detection lookback (default: 10)
                - min_confidence: Minimum confidence threshold (default: 0.88)
        """
        super().__init__(config)
        
        # Extract parameters
        self.momentum_periods = self.parameters.get('momentum_periods', [5, 10, 20])
        self.roc_periods = self.parameters.get('roc_periods', [3, 7, 14])
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.stoch_k_period = self.parameters.get('stoch_k_period', 14)
        self.stoch_d_period = self.parameters.get('stoch_d_period', 3)
        self.macd_fast = self.parameters.get('macd_fast', 12)
        self.macd_slow = self.parameters.get('macd_slow', 26)
        self.macd_signal = self.parameters.get('macd_signal', 9)
        self.volume_ma_period = self.parameters.get('volume_ma_period', 20)
        self.momentum_threshold = self.parameters.get('momentum_threshold', 2.0)
        self.divergence_lookback = self.parameters.get('divergence_lookback', 10)
        self.min_confidence = self.parameters.get('min_confidence', 0.88)
        
        # Technical indicators
        self.indicators = TechnicalIndicators()
        
        # Strategy state
        self._price_history = []
        self._volume_history = []
        self._momentum_history = []
        self._rsi_history = []
        self._macd_history = []
        self._last_signal = None
        self._last_signal_time = None
        
        self.logger = logging.getLogger(f"strategy.advanced_momentum.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the strategy."""
        try:
            self.logger.info(f"Initializing Advanced Momentum Strategy: {self.name}")
            self.logger.info(f"Momentum periods: {self.momentum_periods}")
            self.logger.info(f"ROC periods: {self.roc_periods}")
            
            # Clear state
            self._price_history.clear()
            self._volume_history.clear()
            self._momentum_history.clear()
            self._rsi_history.clear()
            self._macd_history.clear()
            self._last_signal = None
            self._last_signal_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze market data for advanced momentum signals.
        
        Args:
            market_data: List of market data points
            
        Returns:
            Optional[TradingSignal]: High-confidence momentum signal
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
            self._update_history(prices, volumes)
            
            # Calculate momentum indicators
            momentum_analysis = self._calculate_momentum_indicators(prices, volumes, highs, lows)
            
            if not momentum_analysis:
                return None
            
            # Detect momentum signals
            signal_analysis = self._analyze_momentum_signals(momentum_analysis, current_price)
            
            # Check for divergences
            divergence_analysis = self._detect_divergences(prices, momentum_analysis)
            
            # Generate signal if conditions are met
            signal = self._generate_momentum_signal(
                current_data, signal_analysis, divergence_analysis, momentum_analysis
            )
            
            if signal:
                self.logger.info(f"Momentum signal: {signal.action.value} "
                               f"(confidence: {signal.confidence:.3f})")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in momentum analysis: {str(e)}")
            return None
    
    def get_required_data_length(self) -> int:
        """Get minimum data points required."""
        return max(
            max(self.momentum_periods),
            max(self.roc_periods),
            self.rsi_period,
            self.stoch_k_period,
            self.macd_slow + self.macd_signal,
            self.volume_ma_period,
            self.divergence_lookback
        ) + 20
    
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        try:
            # Validate momentum periods
            if not all(p > 0 for p in self.momentum_periods):
                self.logger.error("All momentum periods must be positive")
                return False
            
            # Validate ROC periods
            if not all(p > 0 for p in self.roc_periods):
                self.logger.error("All ROC periods must be positive")
                return False
            
            # Validate other parameters
            if self.rsi_period <= 0:
                self.logger.error("RSI period must be positive")
                return False
            
            if self.momentum_threshold <= 0:
                self.logger.error("Momentum threshold must be positive")
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
        self._price_history = prices[-100:]  # Keep last 100 prices
        self._volume_history = volumes[-100:]  # Keep last 100 volumes
    
    def _calculate_momentum_indicators(self, prices: List[float], volumes: List[float], 
                                     highs: List[float], lows: List[float]) -> Optional[Dict[str, Any]]:
        """Calculate all momentum indicators."""
        try:
            indicators = {}
            
            # 1. Multi-period momentum
            momentum_values = {}
            for period in self.momentum_periods:
                if len(prices) > period:
                    momentum = ((prices[-1] - prices[-period-1]) / prices[-period-1]) * 100
                    momentum_values[f'momentum_{period}'] = momentum
            
            indicators['momentum'] = momentum_values
            
            # 2. Rate of Change (ROC)
            roc_values = {}
            for period in self.roc_periods:
                if len(prices) > period:
                    roc = ((prices[-1] - prices[-period-1]) / prices[-period-1]) * 100
                    roc_values[f'roc_{period}'] = roc
            
            indicators['roc'] = roc_values
            
            # 3. RSI
            rsi = self.indicators.rsi(prices, self.rsi_period)
            if rsi is not None:
                indicators['rsi'] = rsi
                self._rsi_history.append(rsi)
                if len(self._rsi_history) > 50:
                    self._rsi_history = self._rsi_history[-50:]
            
            # 4. Stochastic Oscillator
            stoch_result = self.indicators.stochastic(
                highs, lows, prices, self.stoch_k_period, self.stoch_d_period
            )
            if stoch_result:
                k_percent, d_percent = stoch_result
                indicators['stoch_k'] = k_percent
                indicators['stoch_d'] = d_percent
            
            # 5. MACD
            macd_result = self.indicators.macd(prices, self.macd_fast, self.macd_slow, self.macd_signal)
            if macd_result:
                macd_line, signal_line, histogram = macd_result
                indicators['macd_line'] = macd_line
                indicators['macd_signal'] = signal_line
                indicators['macd_histogram'] = histogram
                
                self._macd_history.append({
                    'line': macd_line,
                    'signal': signal_line,
                    'histogram': histogram
                })
                if len(self._macd_history) > 50:
                    self._macd_history = self._macd_history[-50:]
            
            # 6. Volume-weighted momentum
            if len(volumes) >= self.volume_ma_period:
                volume_ma = sum(volumes[-self.volume_ma_period:]) / self.volume_ma_period
                volume_ratio = volumes[-1] / volume_ma if volume_ma > 0 else 1.0
                
                # Adjust momentum by volume
                if 'momentum_10' in momentum_values:
                    volume_weighted_momentum = momentum_values['momentum_10'] * min(volume_ratio, 3.0)
                    indicators['volume_weighted_momentum'] = volume_weighted_momentum
            
            # 7. Momentum acceleration (second derivative)
            if len(self._momentum_history) >= 3:
                recent_momentum = [m.get('momentum_10', 0) for m in self._momentum_history[-3:]]
                if len(recent_momentum) == 3:
                    acceleration = recent_momentum[-1] - 2*recent_momentum[-2] + recent_momentum[-3]
                    indicators['momentum_acceleration'] = acceleration
            
            # 8. Momentum velocity (first derivative)
            if len(self._momentum_history) >= 2:
                prev_momentum = self._momentum_history[-2].get('momentum_10', 0)
                curr_momentum = momentum_values.get('momentum_10', 0)
                velocity = curr_momentum - prev_momentum
                indicators['momentum_velocity'] = velocity
            
            # Store current momentum for history
            self._momentum_history.append(momentum_values)
            if len(self._momentum_history) > 50:
                self._momentum_history = self._momentum_history[-50:]
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating momentum indicators: {str(e)}")
            return None
    
    def _analyze_momentum_signals(self, indicators: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Analyze momentum indicators for trading signals."""
        signals = {
            'bullish_count': 0,
            'bearish_count': 0,
            'bullish_signals': [],
            'bearish_signals': [],
            'strength': 0.0
        }
        
        try:
            # 1. Multi-period momentum alignment
            momentum_values = indicators.get('momentum', {})
            positive_momentum = sum(1 for v in momentum_values.values() if v > self.momentum_threshold)
            negative_momentum = sum(1 for v in momentum_values.values() if v < -self.momentum_threshold)
            
            if positive_momentum >= 2:
                signals['bullish_count'] += 1
                signals['bullish_signals'].append('Multi_Period_Momentum_Bullish')
                signals['strength'] += 0.15
            
            if negative_momentum >= 2:
                signals['bearish_count'] += 1
                signals['bearish_signals'].append('Multi_Period_Momentum_Bearish')
                signals['strength'] += 0.15
            
            # 2. ROC confirmation
            roc_values = indicators.get('roc', {})
            positive_roc = sum(1 for v in roc_values.values() if v > 1.0)
            negative_roc = sum(1 for v in roc_values.values() if v < -1.0)
            
            if positive_roc >= 2:
                signals['bullish_count'] += 1
                signals['bullish_signals'].append('ROC_Bullish')
                signals['strength'] += 0.10
            
            if negative_roc >= 2:
                signals['bearish_count'] += 1
                signals['bearish_signals'].append('ROC_Bearish')
                signals['strength'] += 0.10
            
            # 3. RSI momentum
            rsi = indicators.get('rsi')
            if rsi is not None:
                if 40 <= rsi <= 60 and len(self._rsi_history) >= 2:
                    rsi_momentum = rsi - self._rsi_history[-2]
                    if rsi_momentum > 5:
                        signals['bullish_count'] += 1
                        signals['bullish_signals'].append('RSI_Momentum_Bullish')
                        signals['strength'] += 0.08
                    elif rsi_momentum < -5:
                        signals['bearish_count'] += 1
                        signals['bearish_signals'].append('RSI_Momentum_Bearish')
                        signals['strength'] += 0.08
            
            # 4. Stochastic momentum
            stoch_k = indicators.get('stoch_k')
            stoch_d = indicators.get('stoch_d')
            if stoch_k is not None and stoch_d is not None:
                if stoch_k > stoch_d and stoch_k > 20:
                    signals['bullish_count'] += 1
                    signals['bullish_signals'].append('Stoch_Bullish')
                    signals['strength'] += 0.06
                elif stoch_k < stoch_d and stoch_k < 80:
                    signals['bearish_count'] += 1
                    signals['bearish_signals'].append('Stoch_Bearish')
                    signals['strength'] += 0.06
            
            # 5. MACD momentum
            macd_histogram = indicators.get('macd_histogram')
            if macd_histogram is not None:
                if macd_histogram > 0 and len(self._macd_history) >= 2:
                    prev_hist = self._macd_history[-2]['histogram']
                    if macd_histogram > prev_hist:
                        signals['bullish_count'] += 1
                        signals['bullish_signals'].append('MACD_Momentum_Bullish')
                        signals['strength'] += 0.12
                elif macd_histogram < 0 and len(self._macd_history) >= 2:
                    prev_hist = self._macd_history[-2]['histogram']
                    if macd_histogram < prev_hist:
                        signals['bearish_count'] += 1
                        signals['bearish_signals'].append('MACD_Momentum_Bearish')
                        signals['strength'] += 0.12
            
            # 6. Volume-weighted momentum
            vw_momentum = indicators.get('volume_weighted_momentum')
            if vw_momentum is not None:
                if vw_momentum > self.momentum_threshold * 1.5:
                    signals['bullish_count'] += 1
                    signals['bullish_signals'].append('Volume_Weighted_Momentum_Bullish')
                    signals['strength'] += 0.14
                elif vw_momentum < -self.momentum_threshold * 1.5:
                    signals['bearish_count'] += 1
                    signals['bearish_signals'].append('Volume_Weighted_Momentum_Bearish')
                    signals['strength'] += 0.14
            
            # 7. Momentum acceleration
            acceleration = indicators.get('momentum_acceleration')
            if acceleration is not None:
                if acceleration > 1.0:
                    signals['bullish_count'] += 1
                    signals['bullish_signals'].append('Momentum_Acceleration_Bullish')
                    signals['strength'] += 0.10
                elif acceleration < -1.0:
                    signals['bearish_count'] += 1
                    signals['bearish_signals'].append('Momentum_Acceleration_Bearish')
                    signals['strength'] += 0.10
            
            # 8. Momentum velocity
            velocity = indicators.get('momentum_velocity')
            if velocity is not None:
                if velocity > 2.0:
                    signals['bullish_count'] += 1
                    signals['bullish_signals'].append('Momentum_Velocity_Bullish')
                    signals['strength'] += 0.08
                elif velocity < -2.0:
                    signals['bearish_count'] += 1
                    signals['bearish_signals'].append('Momentum_Velocity_Bearish')
                    signals['strength'] += 0.08
            
        except Exception as e:
            self.logger.error(f"Error analyzing momentum signals: {str(e)}")
        
        return signals
    
    def _detect_divergences(self, prices: List[float], indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Detect momentum divergences."""
        divergences = {
            'bullish_divergence': False,
            'bearish_divergence': False,
            'divergence_strength': 0.0
        }
        
        try:
            if len(prices) < self.divergence_lookback or len(self._rsi_history) < self.divergence_lookback:
                return divergences
            
            # Price and RSI for divergence analysis
            recent_prices = prices[-self.divergence_lookback:]
            recent_rsi = self._rsi_history[-self.divergence_lookback:]
            
            # Find price highs and lows
            price_highs = []
            price_lows = []
            rsi_highs = []
            rsi_lows = []
            
            for i in range(2, len(recent_prices) - 2):
                # Price highs
                if (recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i-2] and
                    recent_prices[i] > recent_prices[i+1] and recent_prices[i] > recent_prices[i+2]):
                    price_highs.append((i, recent_prices[i]))
                    rsi_highs.append((i, recent_rsi[i]))
                
                # Price lows
                if (recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i-2] and
                    recent_prices[i] < recent_prices[i+1] and recent_prices[i] < recent_prices[i+2]):
                    price_lows.append((i, recent_prices[i]))
                    rsi_lows.append((i, recent_rsi[i]))
            
            # Check for bullish divergence (price makes lower low, RSI makes higher low)
            if len(price_lows) >= 2 and len(rsi_lows) >= 2:
                last_price_low = price_lows[-1][1]
                prev_price_low = price_lows[-2][1]
                last_rsi_low = rsi_lows[-1][1]
                prev_rsi_low = rsi_lows[-2][1]
                
                if last_price_low < prev_price_low and last_rsi_low > prev_rsi_low:
                    divergences['bullish_divergence'] = True
                    divergences['divergence_strength'] += 0.15
            
            # Check for bearish divergence (price makes higher high, RSI makes lower high)
            if len(price_highs) >= 2 and len(rsi_highs) >= 2:
                last_price_high = price_highs[-1][1]
                prev_price_high = price_highs[-2][1]
                last_rsi_high = rsi_highs[-1][1]
                prev_rsi_high = rsi_highs[-2][1]
                
                if last_price_high > prev_price_high and last_rsi_high < prev_rsi_high:
                    divergences['bearish_divergence'] = True
                    divergences['divergence_strength'] += 0.15
            
        except Exception as e:
            self.logger.error(f"Error detecting divergences: {str(e)}")
        
        return divergences
    
    def _generate_momentum_signal(self, market_data: MarketData, signal_analysis: Dict[str, Any],
                                 divergence_analysis: Dict[str, Any], 
                                 indicators: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generate momentum trading signal."""
        try:
            # Check cooldown
            if (self._last_signal_time and 
                (market_data.timestamp - self._last_signal_time).total_seconds() < 1800):  # 30 min
                return None
            
            # Determine signal direction
            bullish_score = signal_analysis['bullish_count']
            bearish_score = signal_analysis['bearish_count']
            
            # Add divergence bonus
            if divergence_analysis['bullish_divergence']:
                bullish_score += 2
            if divergence_analysis['bearish_divergence']:
                bearish_score += 2
            
            # Minimum threshold for signal generation
            min_signals = 4
            
            action = None
            base_confidence = 0.7
            
            if bullish_score >= min_signals and bullish_score > bearish_score:
                action = SignalAction.BUY
                confidence_bonus = min(bullish_score * 0.03, 0.2)
            elif bearish_score >= min_signals and bearish_score > bullish_score:
                action = SignalAction.SELL
                confidence_bonus = min(bearish_score * 0.03, 0.2)
            else:
                return None
            
            # Calculate final confidence
            strength_bonus = min(signal_analysis['strength'], 0.15)
            divergence_bonus = divergence_analysis['divergence_strength']
            
            confidence = base_confidence + confidence_bonus + strength_bonus + divergence_bonus
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
                    'momentum_signals': signal_analysis['bullish_signals'] if action == SignalAction.BUY else signal_analysis['bearish_signals'],
                    'signal_count': bullish_score if action == SignalAction.BUY else bearish_score,
                    'signal_strength': signal_analysis['strength'],
                    'bullish_divergence': divergence_analysis['bullish_divergence'],
                    'bearish_divergence': divergence_analysis['bearish_divergence'],
                    'momentum_values': indicators.get('momentum', {}),
                    'roc_values': indicators.get('roc', {}),
                    'rsi': indicators.get('rsi'),
                    'volume_weighted_momentum': indicators.get('volume_weighted_momentum'),
                    'momentum_acceleration': indicators.get('momentum_acceleration'),
                    'momentum_velocity': indicators.get('momentum_velocity'),
                    'strategy_type': 'advanced_momentum'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error generating momentum signal: {str(e)}")
            return None