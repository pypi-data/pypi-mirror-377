"""
Multi-Indicator Strategy combining multiple technical indicators for high-probability signals.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

from .base_strategy import BaseStrategy, StrategyConfig
from .technical_indicators import TechnicalIndicators
from ..models.data_models import MarketData, TradingSignal, SignalAction


class MultiIndicatorStrategy(BaseStrategy):
    """
    Advanced Multi-Indicator Strategy for high-probability trading signals.
    
    This strategy combines multiple technical indicators with confluence analysis:
    - Moving Average convergence/divergence
    - RSI momentum confirmation
    - Bollinger Bands volatility analysis
    - MACD trend confirmation
    - Volume analysis
    - Support/Resistance levels
    
    Signals are only generated when multiple indicators align (confluence).
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the Multi-Indicator Strategy.
        
        Args:
            config: Strategy configuration containing parameters:
                - ma_fast: Fast moving average period (default: 8)
                - ma_slow: Slow moving average period (default: 21)
                - rsi_period: RSI period (default: 14)
                - rsi_oversold: RSI oversold threshold (default: 30)
                - rsi_overbought: RSI overbought threshold (default: 70)
                - bb_period: Bollinger Bands period (default: 20)
                - bb_std: Bollinger Bands standard deviation (default: 2.0)
                - macd_fast: MACD fast period (default: 12)
                - macd_slow: MACD slow period (default: 26)
                - macd_signal: MACD signal period (default: 9)
                - volume_threshold: Volume confirmation threshold (default: 1.2)
                - min_confluence: Minimum number of confirming indicators (default: 4)
                - min_confidence: Minimum confidence threshold (default: 0.85)
        """
        super().__init__(config)
        
        # Extract parameters with defaults
        self.ma_fast = self.parameters.get('ma_fast', 8)
        self.ma_slow = self.parameters.get('ma_slow', 21)
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.rsi_oversold = self.parameters.get('rsi_oversold', 30)
        self.rsi_overbought = self.parameters.get('rsi_overbought', 70)
        self.bb_period = self.parameters.get('bb_period', 20)
        self.bb_std = self.parameters.get('bb_std', 2.0)
        self.macd_fast = self.parameters.get('macd_fast', 12)
        self.macd_slow = self.parameters.get('macd_slow', 26)
        self.macd_signal = self.parameters.get('macd_signal', 9)
        self.volume_threshold = self.parameters.get('volume_threshold', 1.2)
        self.min_confluence = self.parameters.get('min_confluence', 4)
        self.min_confidence = self.parameters.get('min_confidence', 0.85)
        
        # Technical indicators
        self.indicators = TechnicalIndicators()
        
        # Strategy state
        self._price_history = []
        self._volume_history = []
        self._support_resistance_levels = []
        self._last_signal = None
        self._last_signal_time = None
        
        self.logger = logging.getLogger(f"strategy.multi_indicator.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the strategy."""
        try:
            self.logger.info(f"Initializing Multi-Indicator Strategy: {self.name}")
            self.logger.info(f"Parameters: MA({self.ma_fast},{self.ma_slow}), "
                           f"RSI({self.rsi_period}), BB({self.bb_period},{self.bb_std}), "
                           f"MACD({self.macd_fast},{self.macd_slow},{self.macd_signal})")
            
            # Clear state
            self._price_history.clear()
            self._volume_history.clear()
            self._support_resistance_levels.clear()
            self._last_signal = None
            self._last_signal_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze market data using multiple indicators for confluence.
        
        Args:
            market_data: List of market data points
            
        Returns:
            Optional[TradingSignal]: High-confidence signal if confluence is met
        """
        if len(market_data) < self.get_required_data_length():
            return None
        
        try:
            # Extract price and volume data
            prices = [float(data.close) for data in market_data]
            volumes = [float(data.volume) for data in market_data]
            highs = [float(data.high) for data in market_data]
            lows = [float(data.low) for data in market_data]
            
            current_data = market_data[-1]
            current_price = float(current_data.close)
            
            # Update internal state
            self._price_history = prices[-100:]  # Keep last 100 prices
            self._volume_history = volumes[-50:]  # Keep last 50 volumes
            
            # Calculate all indicators
            indicators = self._calculate_all_indicators(prices, volumes, highs, lows)
            
            if not indicators:
                return None
            
            # Update support/resistance levels
            self._update_support_resistance(prices[-50:], highs[-50:], lows[-50:])
            
            # Analyze confluence for buy/sell signals
            buy_confluence = self._analyze_buy_confluence(indicators, current_price)
            sell_confluence = self._analyze_sell_confluence(indicators, current_price)
            
            # Generate signal if confluence threshold is met
            signal = None
            if buy_confluence['count'] >= self.min_confluence:
                confidence = self._calculate_confidence(buy_confluence, indicators, True)
                if confidence >= self.min_confidence:
                    signal = self._create_signal(current_data, SignalAction.BUY, confidence, 
                                               buy_confluence, indicators)
            
            elif sell_confluence['count'] >= self.min_confluence:
                confidence = self._calculate_confidence(sell_confluence, indicators, False)
                if confidence >= self.min_confidence:
                    signal = self._create_signal(current_data, SignalAction.SELL, confidence, 
                                               sell_confluence, indicators)
            
            if signal:
                self.logger.info(f"High-confidence signal: {signal.action.value} "
                               f"(confidence: {signal.confidence:.3f}, "
                               f"confluence: {buy_confluence['count'] if signal.action == SignalAction.BUY else sell_confluence['count']})")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in analysis: {str(e)}")
            return None
    
    def get_required_data_length(self) -> int:
        """Get minimum data points required."""
        return max(self.ma_slow, self.bb_period, self.macd_slow + self.macd_signal) + 10
    
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        try:
            # Validate MA parameters
            if self.ma_fast >= self.ma_slow or self.ma_fast <= 0 or self.ma_slow <= 0:
                self.logger.error("Invalid moving average parameters")
                return False
            
            # Validate RSI parameters
            if not (0 < self.rsi_oversold < self.rsi_overbought < 100):
                self.logger.error("Invalid RSI parameters")
                return False
            
            # Validate MACD parameters
            if self.macd_fast >= self.macd_slow or any(p <= 0 for p in [self.macd_fast, self.macd_slow, self.macd_signal]):
                self.logger.error("Invalid MACD parameters")
                return False
            
            # Validate confluence and confidence
            if not (1 <= self.min_confluence <= 8):
                self.logger.error("min_confluence must be between 1 and 8")
                return False
            
            if not (0.0 <= self.min_confidence <= 1.0):
                self.logger.error("min_confidence must be between 0.0 and 1.0")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _calculate_all_indicators(self, prices: List[float], volumes: List[float], 
                                 highs: List[float], lows: List[float]) -> Optional[Dict[str, Any]]:
        """Calculate all technical indicators."""
        try:
            indicators = {}
            
            # Moving Averages
            ma_fast = self.indicators.sma(prices, self.ma_fast)
            ma_slow = self.indicators.sma(prices, self.ma_slow)
            ema_fast = self.indicators.ema(prices, self.ma_fast)
            
            if ma_fast and ma_slow and ema_fast:
                indicators['ma_fast'] = ma_fast[-1]
                indicators['ma_slow'] = ma_slow[-1]
                indicators['ema_fast'] = ema_fast[-1]
                indicators['ma_fast_prev'] = ma_fast[-2] if len(ma_fast) > 1 else ma_fast[-1]
                indicators['ma_slow_prev'] = ma_slow[-2] if len(ma_slow) > 1 else ma_slow[-1]
            
            # RSI
            rsi = self.indicators.rsi(prices, self.rsi_period)
            if rsi is not None:
                indicators['rsi'] = rsi
            
            # Bollinger Bands
            bb_result = self.indicators.bollinger_bands(prices, self.bb_period, self.bb_std)
            if bb_result:
                upper, middle, lower = bb_result
                indicators['bb_upper'] = upper
                indicators['bb_middle'] = middle
                indicators['bb_lower'] = lower
                indicators['bb_position'] = (prices[-1] - lower) / (upper - lower)
            
            # MACD
            macd_result = self.indicators.macd(prices, self.macd_fast, self.macd_slow, self.macd_signal)
            if macd_result:
                macd_line, signal_line, histogram = macd_result
                indicators['macd_line'] = macd_line
                indicators['macd_signal'] = signal_line
                indicators['macd_histogram'] = histogram
            
            # Stochastic
            stoch_result = self.indicators.stochastic(highs, lows, prices, 14, 3)
            if stoch_result:
                k_percent, d_percent = stoch_result
                indicators['stoch_k'] = k_percent
                indicators['stoch_d'] = d_percent
            
            # Volume analysis
            if len(volumes) >= 20:
                avg_volume = sum(volumes[-20:]) / 20
                indicators['volume_ratio'] = volumes[-1] / avg_volume if avg_volume > 0 else 1.0
            
            # Price momentum
            if len(prices) >= 10:
                indicators['momentum_5'] = (prices[-1] - prices[-6]) / prices[-6] * 100
                indicators['momentum_10'] = (prices[-1] - prices[-11]) / prices[-11] * 100
            
            return indicators if len(indicators) >= 5 else None
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}")
            return None
    
    def _analyze_buy_confluence(self, indicators: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Analyze confluence for buy signals."""
        confluence = {'count': 0, 'signals': [], 'strength': 0.0}
        
        try:
            # 1. Moving Average Bullish Crossover
            if ('ma_fast' in indicators and 'ma_slow' in indicators and 
                'ma_fast_prev' in indicators and 'ma_slow_prev' in indicators):
                
                if (indicators['ma_fast_prev'] <= indicators['ma_slow_prev'] and 
                    indicators['ma_fast'] > indicators['ma_slow']):
                    confluence['count'] += 1
                    confluence['signals'].append('MA_Bullish_Crossover')
                    confluence['strength'] += 0.15
            
            # 2. Price above both MAs
            if ('ma_fast' in indicators and 'ma_slow' in indicators):
                if current_price > indicators['ma_fast'] > indicators['ma_slow']:
                    confluence['count'] += 1
                    confluence['signals'].append('Price_Above_MAs')
                    confluence['strength'] += 0.10
            
            # 3. RSI Oversold Recovery
            if 'rsi' in indicators:
                if self.rsi_oversold <= indicators['rsi'] <= self.rsi_oversold + 10:
                    confluence['count'] += 1
                    confluence['signals'].append('RSI_Oversold_Recovery')
                    confluence['strength'] += 0.12
            
            # 4. Bollinger Bands Bounce
            if 'bb_position' in indicators:
                if indicators['bb_position'] <= 0.2:  # Near lower band
                    confluence['count'] += 1
                    confluence['signals'].append('BB_Lower_Bounce')
                    confluence['strength'] += 0.10
            
            # 5. MACD Bullish Signal
            if ('macd_line' in indicators and 'macd_signal' in indicators and 
                'macd_histogram' in indicators):
                
                if (indicators['macd_line'] > indicators['macd_signal'] and 
                    indicators['macd_histogram'] > 0):
                    confluence['count'] += 1
                    confluence['signals'].append('MACD_Bullish')
                    confluence['strength'] += 0.13
            
            # 6. Stochastic Oversold
            if 'stoch_k' in indicators and 'stoch_d' in indicators:
                if indicators['stoch_k'] <= 20 and indicators['stoch_d'] <= 20:
                    confluence['count'] += 1
                    confluence['signals'].append('Stoch_Oversold')
                    confluence['strength'] += 0.08
            
            # 7. Volume Confirmation
            if 'volume_ratio' in indicators:
                if indicators['volume_ratio'] >= self.volume_threshold:
                    confluence['count'] += 1
                    confluence['signals'].append('Volume_Confirmation')
                    confluence['strength'] += 0.10
            
            # 8. Support Level Bounce
            if self._is_near_support(current_price):
                confluence['count'] += 1
                confluence['signals'].append('Support_Bounce')
                confluence['strength'] += 0.12
            
            # 9. Positive Momentum
            if 'momentum_5' in indicators and 'momentum_10' in indicators:
                if indicators['momentum_5'] > 0 and indicators['momentum_10'] > -2:
                    confluence['count'] += 1
                    confluence['signals'].append('Positive_Momentum')
                    confluence['strength'] += 0.08
            
        except Exception as e:
            self.logger.error(f"Error in buy confluence analysis: {str(e)}")
        
        return confluence
    
    def _analyze_sell_confluence(self, indicators: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Analyze confluence for sell signals."""
        confluence = {'count': 0, 'signals': [], 'strength': 0.0}
        
        try:
            # 1. Moving Average Bearish Crossover
            if ('ma_fast' in indicators and 'ma_slow' in indicators and 
                'ma_fast_prev' in indicators and 'ma_slow_prev' in indicators):
                
                if (indicators['ma_fast_prev'] >= indicators['ma_slow_prev'] and 
                    indicators['ma_fast'] < indicators['ma_slow']):
                    confluence['count'] += 1
                    confluence['signals'].append('MA_Bearish_Crossover')
                    confluence['strength'] += 0.15
            
            # 2. Price below both MAs
            if ('ma_fast' in indicators and 'ma_slow' in indicators):
                if current_price < indicators['ma_fast'] < indicators['ma_slow']:
                    confluence['count'] += 1
                    confluence['signals'].append('Price_Below_MAs')
                    confluence['strength'] += 0.10
            
            # 3. RSI Overbought Reversal
            if 'rsi' in indicators:
                if self.rsi_overbought - 10 <= indicators['rsi'] <= self.rsi_overbought:
                    confluence['count'] += 1
                    confluence['signals'].append('RSI_Overbought_Reversal')
                    confluence['strength'] += 0.12
            
            # 4. Bollinger Bands Rejection
            if 'bb_position' in indicators:
                if indicators['bb_position'] >= 0.8:  # Near upper band
                    confluence['count'] += 1
                    confluence['signals'].append('BB_Upper_Rejection')
                    confluence['strength'] += 0.10
            
            # 5. MACD Bearish Signal
            if ('macd_line' in indicators and 'macd_signal' in indicators and 
                'macd_histogram' in indicators):
                
                if (indicators['macd_line'] < indicators['macd_signal'] and 
                    indicators['macd_histogram'] < 0):
                    confluence['count'] += 1
                    confluence['signals'].append('MACD_Bearish')
                    confluence['strength'] += 0.13
            
            # 6. Stochastic Overbought
            if 'stoch_k' in indicators and 'stoch_d' in indicators:
                if indicators['stoch_k'] >= 80 and indicators['stoch_d'] >= 80:
                    confluence['count'] += 1
                    confluence['signals'].append('Stoch_Overbought')
                    confluence['strength'] += 0.08
            
            # 7. Volume Confirmation
            if 'volume_ratio' in indicators:
                if indicators['volume_ratio'] >= self.volume_threshold:
                    confluence['count'] += 1
                    confluence['signals'].append('Volume_Confirmation')
                    confluence['strength'] += 0.10
            
            # 8. Resistance Level Rejection
            if self._is_near_resistance(current_price):
                confluence['count'] += 1
                confluence['signals'].append('Resistance_Rejection')
                confluence['strength'] += 0.12
            
            # 9. Negative Momentum
            if 'momentum_5' in indicators and 'momentum_10' in indicators:
                if indicators['momentum_5'] < 0 and indicators['momentum_10'] < 2:
                    confluence['count'] += 1
                    confluence['signals'].append('Negative_Momentum')
                    confluence['strength'] += 0.08
            
        except Exception as e:
            self.logger.error(f"Error in sell confluence analysis: {str(e)}")
        
        return confluence
    
    def _update_support_resistance(self, prices: List[float], highs: List[float], lows: List[float]):
        """Update support and resistance levels."""
        try:
            if len(prices) < 20:
                return
            
            # Find local maxima and minima
            levels = []
            
            # Recent highs (resistance)
            for i in range(2, len(highs) - 2):
                if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                    highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                    levels.append(('resistance', highs[i]))
            
            # Recent lows (support)
            for i in range(2, len(lows) - 2):
                if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                    lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                    levels.append(('support', lows[i]))
            
            # Keep only significant levels (within 5% of current price)
            current_price = prices[-1]
            significant_levels = []
            
            for level_type, price in levels:
                if abs(price - current_price) / current_price <= 0.05:
                    significant_levels.append((level_type, price))
            
            self._support_resistance_levels = significant_levels[-10:]  # Keep last 10
            
        except Exception as e:
            self.logger.error(f"Error updating support/resistance: {str(e)}")
    
    def _is_near_support(self, price: float) -> bool:
        """Check if price is near a support level."""
        for level_type, level_price in self._support_resistance_levels:
            if level_type == 'support' and abs(price - level_price) / price <= 0.01:
                return True
        return False
    
    def _is_near_resistance(self, price: float) -> bool:
        """Check if price is near a resistance level."""
        for level_type, level_price in self._support_resistance_levels:
            if level_type == 'resistance' and abs(price - level_price) / price <= 0.01:
                return True
        return False
    
    def _calculate_confidence(self, confluence: Dict[str, Any], indicators: Dict[str, Any], 
                            is_buy: bool) -> float:
        """Calculate confidence based on confluence strength and indicator quality."""
        try:
            base_confidence = 0.6
            
            # Confluence strength bonus
            confluence_bonus = min(confluence['strength'], 0.3)
            
            # Number of confirming indicators bonus
            count_bonus = min(confluence['count'] * 0.02, 0.15)
            
            # Indicator quality bonus
            quality_bonus = 0.0
            
            # RSI quality
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if is_buy and rsi <= 35:
                    quality_bonus += 0.05
                elif not is_buy and rsi >= 65:
                    quality_bonus += 0.05
            
            # MACD quality
            if 'macd_histogram' in indicators:
                hist = abs(indicators['macd_histogram'])
                if hist > 0.1:  # Strong MACD signal
                    quality_bonus += 0.03
            
            # Volume quality
            if 'volume_ratio' in indicators:
                vol_ratio = indicators['volume_ratio']
                if vol_ratio >= 1.5:  # High volume confirmation
                    quality_bonus += 0.04
            
            confidence = base_confidence + confluence_bonus + count_bonus + quality_bonus
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {str(e)}")
            return 0.6
    
    def _create_signal(self, market_data: MarketData, action: SignalAction, 
                      confidence: float, confluence: Dict[str, Any], 
                      indicators: Dict[str, Any]) -> Optional[TradingSignal]:
        """Create trading signal with detailed metadata."""
        try:
            # Check cooldown
            if (self._last_signal == action and self._last_signal_time and 
                (market_data.timestamp - self._last_signal_time).total_seconds() < 1800):  # 30 min
                return None
            
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
                    'confluence_count': confluence['count'],
                    'confluence_signals': confluence['signals'],
                    'confluence_strength': confluence['strength'],
                    'indicators': {
                        'rsi': indicators.get('rsi'),
                        'ma_fast': indicators.get('ma_fast'),
                        'ma_slow': indicators.get('ma_slow'),
                        'bb_position': indicators.get('bb_position'),
                        'macd_histogram': indicators.get('macd_histogram'),
                        'volume_ratio': indicators.get('volume_ratio')
                    },
                    'support_resistance_levels': len(self._support_resistance_levels),
                    'strategy_type': 'multi_indicator_confluence'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error creating signal: {str(e)}")
            return None