"""
Moving Average Strategy implementation using simple moving average crossover.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import pandas as pd
import numpy as np

from .base_strategy import BaseStrategy, StrategyConfig
from ..models.data_models import MarketData, TradingSignal, SignalAction


class MovingAverageStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.
    
    This strategy generates buy signals when the short-term moving average
    crosses above the long-term moving average, and sell signals when the
    short-term moving average crosses below the long-term moving average.
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the Moving Average Strategy.
        
        Args:
            config: Strategy configuration containing parameters:
                - short_window: Short-term moving average period (default: 10)
                - long_window: Long-term moving average period (default: 30)
                - min_confidence: Minimum confidence threshold (default: 0.7)
        """
        super().__init__(config)
        
        # Extract parameters with defaults
        self.short_window = self.parameters.get('short_window', 10)
        self.long_window = self.parameters.get('long_window', 30)
        self.min_confidence = self.parameters.get('min_confidence', 0.7)
        
        # Strategy state
        self._price_history = []
        self._short_ma_history = []
        self._long_ma_history = []
        self._last_signal = None
        self._last_crossover_time = None
        
        self.logger = logging.getLogger(f"strategy.moving_average.{self.name}")
    
    def initialize(self) -> bool:
        """
        Initialize the strategy.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info(f"Initializing Moving Average Strategy: {self.name}")
            self.logger.info(f"Parameters: short_window={self.short_window}, "
                           f"long_window={self.long_window}, min_confidence={self.min_confidence}")
            
            # Clear any existing state
            self._price_history.clear()
            self._short_ma_history.clear()
            self._long_ma_history.clear()
            self._last_signal = None
            self._last_crossover_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze market data and generate trading signals based on moving average crossover.
        
        Args:
            market_data: List of market data points (should be sorted by timestamp)
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        if len(market_data) < self.get_required_data_length():
            return None
        
        try:
            # Extract closing prices
            prices = [float(data.close) for data in market_data]
            current_data = market_data[-1]
            
            # Calculate moving averages
            short_ma = self._calculate_moving_average(prices, self.short_window)
            long_ma = self._calculate_moving_average(prices, self.long_window)
            
            if short_ma is None or long_ma is None:
                return None
            
            # Store current values for trend analysis
            self._price_history = prices[-self.long_window:]
            self._short_ma_history.append(short_ma)
            self._long_ma_history.append(long_ma)
            
            # Keep only necessary history
            if len(self._short_ma_history) > 10:
                self._short_ma_history = self._short_ma_history[-10:]
            if len(self._long_ma_history) > 10:
                self._long_ma_history = self._long_ma_history[-10:]
            
            # Check for crossover signals
            signal = self._detect_crossover(short_ma, long_ma, current_data)
            
            if signal:
                self.logger.info(f"Generated signal: {signal.action.value} for {signal.symbol} "
                               f"(confidence: {signal.confidence:.2f})")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in analysis: {str(e)}")
            return None
    
    def get_required_data_length(self) -> int:
        """
        Get the minimum number of data points required for analysis.
        
        Returns:
            int: Minimum number of data points (long_window + 1 for crossover detection)
        """
        return self.long_window + 1
    
    def validate_parameters(self) -> bool:
        """
        Validate strategy parameters.
        
        Returns:
            bool: True if parameters are valid
        """
        try:
            # Check window parameters
            if not isinstance(self.short_window, int) or self.short_window <= 0:
                self.logger.error("short_window must be a positive integer")
                return False
            
            if not isinstance(self.long_window, int) or self.long_window <= 0:
                self.logger.error("long_window must be a positive integer")
                return False
            
            if self.short_window >= self.long_window:
                self.logger.error("short_window must be less than long_window")
                return False
            
            # Check confidence threshold
            if not isinstance(self.min_confidence, (int, float)) or not 0.0 <= self.min_confidence <= 1.0:
                self.logger.error("min_confidence must be a number between 0.0 and 1.0")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _calculate_moving_average(self, prices: List[float], window: int) -> Optional[float]:
        """
        Calculate simple moving average for the given window.
        
        Args:
            prices: List of prices
            window: Moving average window size
            
        Returns:
            Optional[float]: Moving average value or None if insufficient data
        """
        if len(prices) < window:
            return None
        
        return sum(prices[-window:]) / window
    
    def _detect_crossover(self, current_short_ma: float, current_long_ma: float, 
                         current_data: MarketData) -> Optional[TradingSignal]:
        """
        Detect moving average crossover and generate signals.
        
        Args:
            current_short_ma: Current short-term moving average
            current_long_ma: Current long-term moving average
            current_data: Current market data point
            
        Returns:
            Optional[TradingSignal]: Trading signal if crossover detected
        """
        # Need at least 2 data points to detect crossover
        if len(self._short_ma_history) < 2 or len(self._long_ma_history) < 2:
            return None
        
        prev_short_ma = self._short_ma_history[-2]
        prev_long_ma = self._long_ma_history[-2]
        
        # Detect bullish crossover (short MA crosses above long MA)
        if (prev_short_ma <= prev_long_ma and current_short_ma > current_long_ma):
            # Avoid duplicate signals
            if (self._last_signal != SignalAction.BUY or 
                self._last_crossover_time is None or 
                (current_data.timestamp - self._last_crossover_time).total_seconds() > 3600):  # 1 hour cooldown
                
                confidence = self._calculate_confidence(current_short_ma, current_long_ma, True)
                
                if confidence >= self.min_confidence:
                    self._last_signal = SignalAction.BUY
                    self._last_crossover_time = current_data.timestamp
                    
                    return TradingSignal(
                        symbol=current_data.symbol,
                        action=SignalAction.BUY,
                        confidence=confidence,
                        timestamp=current_data.timestamp,
                        strategy_name=self.name,
                        price=current_data.close,
                        metadata={
                            'short_ma': current_short_ma,
                            'long_ma': current_long_ma,
                            'short_window': self.short_window,
                            'long_window': self.long_window,
                            'crossover_type': 'bullish'
                        }
                    )
        
        # Detect bearish crossover (short MA crosses below long MA)
        elif (prev_short_ma >= prev_long_ma and current_short_ma < current_long_ma):
            # Avoid duplicate signals
            if (self._last_signal != SignalAction.SELL or 
                self._last_crossover_time is None or 
                (current_data.timestamp - self._last_crossover_time).total_seconds() > 3600):  # 1 hour cooldown
                
                confidence = self._calculate_confidence(current_short_ma, current_long_ma, False)
                
                if confidence >= self.min_confidence:
                    self._last_signal = SignalAction.SELL
                    self._last_crossover_time = current_data.timestamp
                    
                    return TradingSignal(
                        symbol=current_data.symbol,
                        action=SignalAction.SELL,
                        confidence=confidence,
                        timestamp=current_data.timestamp,
                        strategy_name=self.name,
                        price=current_data.close,
                        metadata={
                            'short_ma': current_short_ma,
                            'long_ma': current_long_ma,
                            'short_window': self.short_window,
                            'long_window': self.long_window,
                            'crossover_type': 'bearish'
                        }
                    )
        
        return None
    
    def _calculate_confidence(self, short_ma: float, long_ma: float, is_bullish: bool) -> float:
        """
        Calculate confidence level for the signal based on various factors.
        
        Args:
            short_ma: Short-term moving average
            long_ma: Long-term moving average
            is_bullish: Whether this is a bullish signal
            
        Returns:
            float: Confidence level between 0.0 and 1.0
        """
        try:
            # Base confidence
            base_confidence = 0.6
            
            # Factor 1: Magnitude of separation between MAs
            separation = abs(short_ma - long_ma) / long_ma
            separation_bonus = min(separation * 10, 0.2)  # Max 0.2 bonus
            
            # Factor 2: Trend strength (based on recent MA slope)
            trend_bonus = 0.0
            if len(self._short_ma_history) >= 3:
                recent_short_slope = (self._short_ma_history[-1] - self._short_ma_history[-3]) / self._short_ma_history[-3]
                if (is_bullish and recent_short_slope > 0) or (not is_bullish and recent_short_slope < 0):
                    trend_bonus = min(abs(recent_short_slope) * 5, 0.15)  # Max 0.15 bonus
            
            # Factor 3: Volume consideration (if available in price history)
            volume_bonus = 0.05  # Default small bonus
            
            confidence = base_confidence + separation_bonus + trend_bonus + volume_bonus
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Error calculating confidence: {str(e)}")
            return 0.6  # Return base confidence on error
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the strategy state.
        
        Returns:
            Dict[str, Any]: Strategy information
        """
        info = {
            'strategy_type': 'MovingAverageStrategy',
            'parameters': {
                'short_window': self.short_window,
                'long_window': self.long_window,
                'min_confidence': self.min_confidence
            },
            'state': {
                'last_signal': self._last_signal.value if self._last_signal else None,
                'last_crossover_time': self._last_crossover_time.isoformat() if self._last_crossover_time else None,
                'price_history_length': len(self._price_history),
                'ma_history_length': len(self._short_ma_history)
            },
            'current_values': {}
        }
        
        if self._short_ma_history and self._long_ma_history:
            info['current_values'] = {
                'current_short_ma': self._short_ma_history[-1],
                'current_long_ma': self._long_ma_history[-1],
                'ma_difference': self._short_ma_history[-1] - self._long_ma_history[-1]
            }
        
        return info