"""
Technical analysis indicators using ta-lib integration.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
import numpy as np

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("ta-lib not available, using fallback implementations")


class TechnicalIndicators:
    """
    Technical analysis indicators with ta-lib integration and fallback implementations.
    
    This class provides a unified interface for technical indicators, using ta-lib
    when available and falling back to custom implementations when not.
    """
    
    def __init__(self):
        """Initialize the technical indicators class."""
        self.logger = logging.getLogger("technical_indicators")
        if not TALIB_AVAILABLE:
            self.logger.warning("ta-lib not available, using fallback implementations")
    
    def sma(self, prices: List[float], period: int) -> Optional[List[float]]:
        """
        Calculate Simple Moving Average.
        
        Args:
            prices: List of prices
            period: Moving average period
            
        Returns:
            Optional[List[float]]: SMA values or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        try:
            if TALIB_AVAILABLE:
                price_array = np.array(prices, dtype=float)
                sma_values = talib.SMA(price_array, timeperiod=period)
                return sma_values[~np.isnan(sma_values)].tolist()
            else:
                return self._sma_fallback(prices, period)
                
        except Exception as e:
            self.logger.error(f"Error calculating SMA: {str(e)}")
            return None
    
    def ema(self, prices: List[float], period: int) -> Optional[List[float]]:
        """
        Calculate Exponential Moving Average.
        
        Args:
            prices: List of prices
            period: EMA period
            
        Returns:
            Optional[List[float]]: EMA values or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        try:
            if TALIB_AVAILABLE:
                price_array = np.array(prices, dtype=float)
                ema_values = talib.EMA(price_array, timeperiod=period)
                return ema_values[~np.isnan(ema_values)].tolist()
            else:
                return self._ema_fallback(prices, period)
                
        except Exception as e:
            self.logger.error(f"Error calculating EMA: {str(e)}")
            return None
    
    def rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: List of prices
            period: RSI period (default: 14)
            
        Returns:
            Optional[float]: Current RSI value or None if insufficient data
        """
        if len(prices) < period + 1:
            return None
        
        try:
            if TALIB_AVAILABLE:
                price_array = np.array(prices, dtype=float)
                rsi_values = talib.RSI(price_array, timeperiod=period)
                return float(rsi_values[-1]) if not np.isnan(rsi_values[-1]) else None
            else:
                return self._rsi_fallback(prices, period)
                
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}")
            return None
    
    def macd(self, prices: List[float], fast_period: int = 12, 
             slow_period: int = 26, signal_period: int = 9) -> Optional[Tuple[float, float, float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: List of prices
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line EMA period (default: 9)
            
        Returns:
            Optional[Tuple[float, float, float]]: (MACD, Signal, Histogram) or None
        """
        if len(prices) < slow_period + signal_period:
            return None
        
        try:
            if TALIB_AVAILABLE:
                price_array = np.array(prices, dtype=float)
                macd_line, signal_line, histogram = talib.MACD(
                    price_array, fastperiod=fast_period, 
                    slowperiod=slow_period, signalperiod=signal_period
                )
                
                if not (np.isnan(macd_line[-1]) or np.isnan(signal_line[-1]) or np.isnan(histogram[-1])):
                    return float(macd_line[-1]), float(signal_line[-1]), float(histogram[-1])
                return None
            else:
                return self._macd_fallback(prices, fast_period, slow_period, signal_period)
                
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {str(e)}")
            return None
    
    def bollinger_bands(self, prices: List[float], period: int = 20, 
                       std_dev: float = 2.0) -> Optional[Tuple[float, float, float]]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: List of prices
            period: Moving average period (default: 20)
            std_dev: Standard deviation multiplier (default: 2.0)
            
        Returns:
            Optional[Tuple[float, float, float]]: (Upper, Middle, Lower) bands or None
        """
        if len(prices) < period:
            return None
        
        try:
            if TALIB_AVAILABLE:
                price_array = np.array(prices, dtype=float)
                upper, middle, lower = talib.BBANDS(
                    price_array, timeperiod=period, nbdevup=std_dev, 
                    nbdevdn=std_dev, matype=0
                )
                
                if not (np.isnan(upper[-1]) or np.isnan(middle[-1]) or np.isnan(lower[-1])):
                    return float(upper[-1]), float(middle[-1]), float(lower[-1])
                return None
            else:
                return self._bollinger_bands_fallback(prices, period, std_dev)
                
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return None
    
    def stochastic(self, high_prices: List[float], low_prices: List[float], 
                  close_prices: List[float], k_period: int = 14, 
                  d_period: int = 3) -> Optional[Tuple[float, float]]:
        """
        Calculate Stochastic Oscillator.
        
        Args:
            high_prices: List of high prices
            low_prices: List of low prices
            close_prices: List of close prices
            k_period: %K period (default: 14)
            d_period: %D period (default: 3)
            
        Returns:
            Optional[Tuple[float, float]]: (%K, %D) values or None
        """
        if len(high_prices) < k_period or len(low_prices) < k_period or len(close_prices) < k_period:
            return None
        
        try:
            if TALIB_AVAILABLE:
                high_array = np.array(high_prices, dtype=float)
                low_array = np.array(low_prices, dtype=float)
                close_array = np.array(close_prices, dtype=float)
                
                slowk, slowd = talib.STOCH(
                    high_array, low_array, close_array,
                    fastk_period=k_period, slowk_period=d_period, slowd_period=d_period
                )
                
                if not (np.isnan(slowk[-1]) or np.isnan(slowd[-1])):
                    return float(slowk[-1]), float(slowd[-1])
                return None
            else:
                return self._stochastic_fallback(high_prices, low_prices, close_prices, k_period, d_period)
                
        except Exception as e:
            self.logger.error(f"Error calculating Stochastic: {str(e)}")
            return None
    
    # Fallback implementations when ta-lib is not available
    
    def _sma_fallback(self, prices: List[float], period: int) -> List[float]:
        """Fallback SMA implementation."""
        sma_values = []
        for i in range(period - 1, len(prices)):
            sma = sum(prices[i - period + 1:i + 1]) / period
            sma_values.append(sma)
        return sma_values
    
    def _ema_fallback(self, prices: List[float], period: int) -> List[float]:
        """Fallback EMA implementation."""
        multiplier = 2.0 / (period + 1)
        ema_values = []
        
        # Start with SMA for first value
        ema = sum(prices[:period]) / period
        ema_values.append(ema)
        
        # Calculate EMA for remaining values
        for i in range(period, len(prices)):
            ema = (prices[i] * multiplier) + (ema * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def _rsi_fallback(self, prices: List[float], period: int) -> Optional[float]:
        """Fallback RSI implementation."""
        if len(prices) < period + 1:
            return None
        
        # Calculate price changes
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [change if change > 0 else 0 for change in changes]
        losses = [-change if change < 0 else 0 for change in changes]
        
        # Calculate average gain and loss
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _macd_fallback(self, prices: List[float], fast_period: int, 
                      slow_period: int, signal_period: int) -> Optional[Tuple[float, float, float]]:
        """Fallback MACD implementation."""
        if len(prices) < slow_period + signal_period:
            return None
        
        # Calculate EMAs
        fast_ema = self._ema_fallback(prices, fast_period)
        slow_ema = self._ema_fallback(prices, slow_period)
        
        if not fast_ema or not slow_ema:
            return None
        
        # Align EMAs (slow EMA starts later)
        start_idx = slow_period - fast_period
        fast_ema_aligned = fast_ema[start_idx:]
        
        # Calculate MACD line
        macd_line = [fast_ema_aligned[i] - slow_ema[i] for i in range(len(slow_ema))]
        
        # Calculate signal line (EMA of MACD)
        if len(macd_line) < signal_period:
            return None
        
        signal_line = self._ema_fallback(macd_line, signal_period)
        
        if not signal_line:
            return None
        
        # Calculate histogram
        histogram = macd_line[-1] - signal_line[-1]
        
        return macd_line[-1], signal_line[-1], histogram
    
    def _bollinger_bands_fallback(self, prices: List[float], period: int, 
                                 std_dev: float) -> Optional[Tuple[float, float, float]]:
        """Fallback Bollinger Bands implementation."""
        if len(prices) < period:
            return None
        
        # Calculate middle band (SMA)
        recent_prices = prices[-period:]
        middle = sum(recent_prices) / period
        
        # Calculate standard deviation
        variance = sum((price - middle) ** 2 for price in recent_prices) / period
        std = variance ** 0.5
        
        # Calculate bands
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return upper, middle, lower
    
    def _stochastic_fallback(self, high_prices: List[float], low_prices: List[float], 
                           close_prices: List[float], k_period: int, 
                           d_period: int) -> Optional[Tuple[float, float]]:
        """Fallback Stochastic implementation."""
        if len(close_prices) < k_period:
            return None
        
        # Calculate %K
        recent_highs = high_prices[-k_period:]
        recent_lows = low_prices[-k_period:]
        current_close = close_prices[-1]
        
        highest_high = max(recent_highs)
        lowest_low = min(recent_lows)
        
        if highest_high == lowest_low:
            k_percent = 50.0  # Neutral value when no range
        else:
            k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # For %D, we would need multiple %K values, so return simplified version
        d_percent = k_percent  # Simplified - in practice would be SMA of %K values
        
        return k_percent, d_percent
    
    def atr(self, high_prices: List[float], low_prices: List[float], 
            close_prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate Average True Range (ATR).
        
        Args:
            high_prices: List of high prices
            low_prices: List of low prices
            close_prices: List of close prices
            period: ATR period (default: 14)
            
        Returns:
            Optional[float]: Current ATR value or None if insufficient data
        """
        if len(high_prices) < period + 1 or len(low_prices) < period + 1 or len(close_prices) < period + 1:
            return None
        
        try:
            if TALIB_AVAILABLE:
                high_array = np.array(high_prices, dtype=float)
                low_array = np.array(low_prices, dtype=float)
                close_array = np.array(close_prices, dtype=float)
                
                atr_values = talib.ATR(high_array, low_array, close_array, timeperiod=period)
                return float(atr_values[-1]) if not np.isnan(atr_values[-1]) else None
            else:
                return self._atr_fallback(high_prices, low_prices, close_prices, period)
                
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {str(e)}")
            return None
    
    def atr_bands(self, high_prices: List[float], low_prices: List[float], 
                  close_prices: List[float], period: int = 14, 
                  multiplier: float = 2.0) -> Optional[Tuple[float, float, float]]:
        """
        Calculate ATR-based bands (similar to Bollinger Bands but using ATR).
        
        Args:
            high_prices: List of high prices
            low_prices: List of low prices
            close_prices: List of close prices
            period: ATR period (default: 14)
            multiplier: ATR multiplier (default: 2.0)
            
        Returns:
            Optional[Tuple[float, float, float]]: (Upper, Middle, Lower) bands or None
        """
        if len(close_prices) < period:
            return None
        
        try:
            # Calculate ATR
            atr_value = self.atr(high_prices, low_prices, close_prices, period)
            if atr_value is None:
                return None
            
            # Calculate middle line (SMA of close prices)
            middle = sum(close_prices[-period:]) / period
            
            # Calculate bands
            upper = middle + (atr_value * multiplier)
            lower = middle - (atr_value * multiplier)
            
            return upper, middle, lower
            
        except Exception as e:
            self.logger.error(f"Error calculating ATR bands: {str(e)}")
            return None

    def _atr_fallback(self, high_prices: List[float], low_prices: List[float], 
                      close_prices: List[float], period: int) -> Optional[float]:
        """Fallback ATR implementation."""
        try:
            if len(high_prices) < period + 1:
                return None
            
            # Calculate True Range for each period
            true_ranges = []
            for i in range(1, len(high_prices)):
                tr = max(
                    high_prices[i] - low_prices[i],
                    abs(high_prices[i] - close_prices[i-1]),
                    abs(low_prices[i] - close_prices[i-1])
                )
                true_ranges.append(tr)
            
            # Calculate ATR as simple moving average of True Range
            if len(true_ranges) < period:
                return None
            
            atr = sum(true_ranges[-period:]) / period
            return atr
            
        except Exception as e:
            self.logger.error(f"Error in ATR fallback: {str(e)}")
            return None

    def get_available_indicators(self) -> Dict[str, bool]:
        """
        Get list of available indicators and their implementation status.
        
        Returns:
            Dict[str, bool]: Indicator names and whether ta-lib is used
        """
        return {
            'sma': TALIB_AVAILABLE,
            'ema': TALIB_AVAILABLE,
            'rsi': TALIB_AVAILABLE,
            'macd': TALIB_AVAILABLE,
            'bollinger_bands': TALIB_AVAILABLE,
            'stochastic': TALIB_AVAILABLE,
            'atr': TALIB_AVAILABLE,
            'atr_bands': TALIB_AVAILABLE,
            'talib_available': TALIB_AVAILABLE
        }