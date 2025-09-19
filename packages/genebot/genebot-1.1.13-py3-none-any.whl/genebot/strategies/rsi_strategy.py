"""
RSI Strategy implementation using Relative Strength Index indicators.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import pandas as pd
import numpy as np

from .base_strategy import BaseStrategy, StrategyConfig
from ..models.data_models import MarketData, TradingSignal, SignalAction


class RSIStrategy(BaseStrategy):
    """
    Relative Strength Index (RSI) Strategy.
    
    This strategy generates buy signals when RSI is oversold (below lower threshold)
    and sell signals when RSI is overbought (above upper threshold).
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the RSI Strategy.
        
        Args:
            config: Strategy configuration containing parameters:
                - rsi_period: RSI calculation period (default: 14)
                - oversold_threshold: RSI oversold level (default: 30)
                - overbought_threshold: RSI overbought level (default: 70)
                - min_confidence: Minimum confidence threshold (default: 0.7)
        """
        super().__init__(config)
        
        # Extract parameters with defaults
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.oversold_threshold = self.parameters.get('oversold_threshold', 30)
        self.overbought_threshold = self.parameters.get('overbought_threshold', 70)
        self.min_confidence = self.parameters.get('min_confidence', 0.7)
        
        # Strategy state
        self._price_history = []
        self._rsi_history = []
        self._last_signal = None
        self._last_signal_time = None
        
        self.logger = logging.getLogger(f"strategy.rsi.{self.name}")
    
    def initialize(self) -> bool:
        """
        Initialize the strategy.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info(f"Initializing RSI Strategy: {self.name}")
            self.logger.info(f"Parameters: rsi_period={self.rsi_period}, "
                           f"oversold={self.oversold_threshold}, overbought={self.overbought_threshold}")
            
            # Clear any existing state
            self._price_history.clear()
            self._rsi_history.clear()
            self._last_signal = None
            self._last_signal_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze market data and generate trading signals based on RSI levels.
        
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
            
            # Calculate RSI
            rsi = self._calculate_rsi(prices)
            
            if rsi is None:
                return None
            
            # Store current values
            self._price_history = prices[-self.rsi_period * 2:]  # Keep extra history
            self._rsi_history.append(rsi)
            
            # Keep only necessary history
            if len(self._rsi_history) > 20:
                self._rsi_history = self._rsi_history[-20:]
            
            # Generate signals based on RSI levels
            signal = self._generate_rsi_signal(rsi, current_data)
            
            if signal:
                self.logger.info(f"Generated signal: {signal.action.value} for {signal.symbol} "
                               f"(RSI: {rsi:.2f}, confidence: {signal.confidence:.2f})")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in analysis: {str(e)}")
            return None
    
    def get_required_data_length(self) -> int:
        """
        Get the minimum number of data points required for analysis.
        
        Returns:
            int: Minimum number of data points (rsi_period + 1 for calculation)
        """
        return self.rsi_period + 1
    
    def validate_parameters(self) -> bool:
        """
        Validate strategy parameters.
        
        Returns:
            bool: True if parameters are valid
        """
        try:
            # Check RSI period
            if not isinstance(self.rsi_period, int) or self.rsi_period <= 0:
                self.logger.error("rsi_period must be a positive integer")
                return False
            
            # Check thresholds
            if not isinstance(self.oversold_threshold, (int, float)) or not 0 <= self.oversold_threshold <= 100:
                self.logger.error("oversold_threshold must be between 0 and 100")
                return False
            
            if not isinstance(self.overbought_threshold, (int, float)) or not 0 <= self.overbought_threshold <= 100:
                self.logger.error("overbought_threshold must be between 0 and 100")
                return False
            
            if self.oversold_threshold >= self.overbought_threshold:
                self.logger.error("oversold_threshold must be less than overbought_threshold")
                return False
            
            # Check confidence threshold
            if not isinstance(self.min_confidence, (int, float)) or not 0.0 <= self.min_confidence <= 1.0:
                self.logger.error("min_confidence must be a number between 0.0 and 1.0")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _calculate_rsi(self, prices: List[float]) -> Optional[float]:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: List of closing prices
            
        Returns:
            Optional[float]: RSI value (0-100) or None if insufficient data
        """
        if len(prices) < self.rsi_period + 1:
            return None
        
        try:
            # Calculate price changes
            price_changes = []
            for i in range(1, len(prices)):
                price_changes.append(prices[i] - prices[i-1])
            
            if len(price_changes) < self.rsi_period:
                return None
            
            # Separate gains and losses
            gains = [change if change > 0 else 0 for change in price_changes]
            losses = [-change if change < 0 else 0 for change in price_changes]
            
            # Calculate initial average gain and loss
            avg_gain = sum(gains[-self.rsi_period:]) / self.rsi_period
            avg_loss = sum(losses[-self.rsi_period:]) / self.rsi_period
            
            # Handle division by zero
            if avg_loss == 0:
                return 100.0
            
            # Calculate RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}")
            return None
    
    def _generate_rsi_signal(self, rsi: float, current_data: MarketData) -> Optional[TradingSignal]:
        """
        Generate trading signals based on RSI levels.
        
        Args:
            rsi: Current RSI value
            current_data: Current market data point
            
        Returns:
            Optional[TradingSignal]: Trading signal if conditions are met
        """
        # Check for oversold condition (buy signal)
        if rsi <= self.oversold_threshold:
            # Avoid duplicate signals
            if (self._last_signal != SignalAction.BUY or 
                self._last_signal_time is None or 
                (current_data.timestamp - self._last_signal_time).total_seconds() > 1800):  # 30 min cooldown
                
                confidence = self._calculate_confidence(rsi, True)
                
                if confidence >= self.min_confidence:
                    self._last_signal = SignalAction.BUY
                    self._last_signal_time = current_data.timestamp
                    
                    return TradingSignal(
                        symbol=current_data.symbol,
                        action=SignalAction.BUY,
                        confidence=confidence,
                        timestamp=current_data.timestamp,
                        strategy_name=self.name,
                        price=current_data.close,
                        metadata={
                            'rsi': rsi,
                            'rsi_period': self.rsi_period,
                            'oversold_threshold': self.oversold_threshold,
                            'signal_type': 'oversold'
                        }
                    )
        
        # Check for overbought condition (sell signal)
        elif rsi >= self.overbought_threshold:
            # Avoid duplicate signals
            if (self._last_signal != SignalAction.SELL or 
                self._last_signal_time is None or 
                (current_data.timestamp - self._last_signal_time).total_seconds() > 1800):  # 30 min cooldown
                
                confidence = self._calculate_confidence(rsi, False)
                
                if confidence >= self.min_confidence:
                    self._last_signal = SignalAction.SELL
                    self._last_signal_time = current_data.timestamp
                    
                    return TradingSignal(
                        symbol=current_data.symbol,
                        action=SignalAction.SELL,
                        confidence=confidence,
                        timestamp=current_data.timestamp,
                        strategy_name=self.name,
                        price=current_data.close,
                        metadata={
                            'rsi': rsi,
                            'rsi_period': self.rsi_period,
                            'overbought_threshold': self.overbought_threshold,
                            'signal_type': 'overbought'
                        }
                    )
        
        return None
    
    def _calculate_confidence(self, rsi: float, is_buy_signal: bool) -> float:
        """
        Calculate confidence level for the signal based on RSI extremity.
        
        Args:
            rsi: Current RSI value
            is_buy_signal: Whether this is a buy signal (oversold)
            
        Returns:
            float: Confidence level between 0.0 and 1.0
        """
        try:
            base_confidence = 0.6
            
            if is_buy_signal:
                # More oversold = higher confidence
                extremity = max(0, self.oversold_threshold - rsi) / self.oversold_threshold
                extremity_bonus = extremity * 0.3  # Max 0.3 bonus
            else:
                # More overbought = higher confidence
                extremity = max(0, rsi - self.overbought_threshold) / (100 - self.overbought_threshold)
                extremity_bonus = extremity * 0.3  # Max 0.3 bonus
            
            # RSI trend consideration
            trend_bonus = 0.0
            if len(self._rsi_history) >= 3:
                rsi_trend = self._rsi_history[-1] - self._rsi_history[-3]
                if is_buy_signal and rsi_trend < 0:  # RSI still falling (more oversold)
                    trend_bonus = 0.05
                elif not is_buy_signal and rsi_trend > 0:  # RSI still rising (more overbought)
                    trend_bonus = 0.05
            
            confidence = base_confidence + extremity_bonus + trend_bonus
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
            'strategy_type': 'RSIStrategy',
            'parameters': {
                'rsi_period': self.rsi_period,
                'oversold_threshold': self.oversold_threshold,
                'overbought_threshold': self.overbought_threshold,
                'min_confidence': self.min_confidence
            },
            'state': {
                'last_signal': self._last_signal.value if self._last_signal else None,
                'last_signal_time': self._last_signal_time.isoformat() if self._last_signal_time else None,
                'price_history_length': len(self._price_history),
                'rsi_history_length': len(self._rsi_history)
            },
            'current_values': {}
        }
        
        if self._rsi_history:
            current_rsi = self._rsi_history[-1]
            info['current_values'] = {
                'current_rsi': current_rsi,
                'market_condition': self._get_market_condition(current_rsi)
            }
        
        return info
    
    def _get_market_condition(self, rsi: float) -> str:
        """
        Get market condition based on RSI value.
        
        Args:
            rsi: Current RSI value
            
        Returns:
            str: Market condition description
        """
        if rsi <= self.oversold_threshold:
            return 'oversold'
        elif rsi >= self.overbought_threshold:
            return 'overbought'
        elif rsi < 50:
            return 'bearish'
        else:
            return 'bullish'