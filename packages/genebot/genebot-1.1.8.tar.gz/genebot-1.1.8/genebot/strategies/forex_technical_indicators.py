"""
Forex-specific technical indicators and signal processing.

This module provides technical indicators specifically designed for forex trading,
including pip calculations, currency strength analysis, and forex-specific patterns.
"""

from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import logging
import math

from .technical_indicators import TechnicalIndicators
from ..models.data_models import UnifiedMarketData
from ..markets.types import UnifiedSymbol, MarketType


class ForexTechnicalIndicators(TechnicalIndicators):
    """
    Extended technical indicators specifically for forex trading.
    
    Includes forex-specific calculations like pip values, currency strength,
    and forex market patterns.
    """
    
    # Pip values for different currency pairs
    PIP_VALUES = {
        'JPY': 0.01,      # JPY pairs: 1 pip = 0.01
        'default': 0.0001  # Most pairs: 1 pip = 0.0001
    }
    
    # Major currency rankings (for strength calculation)
    MAJOR_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']
    
    def __init__(self):
        """Initialize forex technical indicators."""
        super().__init__()
        self.logger = logging.getLogger("forex_technical_indicators")
    
    def calculate_pip_value(self, symbol: UnifiedSymbol, price: float = None) -> float:
        """
        Calculate pip value for a currency pair.
        
        Args:
            symbol: Currency pair symbol
            price: Current price (optional, for more accurate calculation)
            
        Returns:
            float: Pip value
        """
        try:
            if symbol.quote_asset == 'JPY':
                return self.PIP_VALUES['JPY']
            else:
                return self.PIP_VALUES['default']
                
        except Exception as e:
            self.logger.error(f"Error calculating pip value for {symbol}: {str(e)}")
            return self.PIP_VALUES['default']
    
    def price_to_pips(self, symbol: UnifiedSymbol, price_diff: float) -> float:
        """
        Convert price difference to pips.
        
        Args:
            symbol: Currency pair symbol
            price_diff: Price difference
            
        Returns:
            float: Difference in pips
        """
        pip_value = self.calculate_pip_value(symbol)
        return abs(price_diff) / pip_value
    
    def pips_to_price(self, symbol: UnifiedSymbol, pips: float) -> float:
        """
        Convert pips to price difference.
        
        Args:
            symbol: Currency pair symbol
            pips: Number of pips
            
        Returns:
            float: Price difference
        """
        pip_value = self.calculate_pip_value(symbol)
        return pips * pip_value
    
    def calculate_spread_in_pips(self, symbol: UnifiedSymbol, bid: float, ask: float) -> float:
        """
        Calculate spread in pips.
        
        Args:
            symbol: Currency pair symbol
            bid: Bid price
            ask: Ask price
            
        Returns:
            float: Spread in pips
        """
        spread = ask - bid
        return self.price_to_pips(symbol, spread)
    
    def forex_atr_pips(self, symbol: UnifiedSymbol, high_prices: List[float], 
                      low_prices: List[float], close_prices: List[float], 
                      period: int = 14) -> Optional[float]:
        """
        Calculate ATR in pips for forex pairs.
        
        Args:
            symbol: Currency pair symbol
            high_prices: List of high prices
            low_prices: List of low prices
            close_prices: List of close prices
            period: ATR period
            
        Returns:
            Optional[float]: ATR in pips
        """
        atr_price = self.atr(high_prices, low_prices, close_prices, period)
        if atr_price is None:
            return None
        
        return self.price_to_pips(symbol, atr_price)
    
    def pivot_points(self, high: float, low: float, close: float) -> Dict[str, float]:
        """
        Calculate pivot points for forex trading.
        
        Args:
            high: Previous day's high
            low: Previous day's low
            close: Previous day's close
            
        Returns:
            Dict[str, float]: Pivot points (PP, R1, R2, R3, S1, S2, S3)
        """
        try:
            # Standard pivot point calculation
            pp = (high + low + close) / 3
            
            # Resistance levels
            r1 = (2 * pp) - low
            r2 = pp + (high - low)
            r3 = high + 2 * (pp - low)
            
            # Support levels
            s1 = (2 * pp) - high
            s2 = pp - (high - low)
            s3 = low - 2 * (high - pp)
            
            return {
                'PP': pp,
                'R1': r1, 'R2': r2, 'R3': r3,
                'S1': s1, 'S2': s2, 'S3': s3
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating pivot points: {str(e)}")
            return {}
    
    def fibonacci_retracement(self, high: float, low: float, 
                            trend_direction: str = 'up') -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels.
        
        Args:
            high: Swing high
            low: Swing low
            trend_direction: 'up' or 'down'
            
        Returns:
            Dict[str, float]: Fibonacci levels
        """
        try:
            fib_ratios = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
            levels = {}
            
            if trend_direction.lower() == 'up':
                # Uptrend: retracement from high to low
                for ratio in fib_ratios:
                    level = high - (ratio * (high - low))
                    levels[f'{ratio:.3f}'] = level
            else:
                # Downtrend: retracement from low to high
                for ratio in fib_ratios:
                    level = low + (ratio * (high - low))
                    levels[f'{ratio:.3f}'] = level
            
            return levels
            
        except Exception as e:
            self.logger.error(f"Error calculating Fibonacci retracement: {str(e)}")
            return {}
    
    def currency_strength(self, market_data: Dict[UnifiedSymbol, List[UnifiedMarketData]], 
                         period: int = 20) -> Dict[str, float]:
        """
        Calculate relative currency strength.
        
        Args:
            market_data: Dictionary of symbol -> market data
            period: Period for strength calculation
            
        Returns:
            Dict[str, float]: Currency strength scores
        """
        try:
            currency_changes = {}
            currency_counts = {}
            
            # Initialize currency tracking
            for currency in self.MAJOR_CURRENCIES:
                currency_changes[currency] = 0.0
                currency_counts[currency] = 0
            
            # Calculate price changes for each pair
            for symbol, data_points in market_data.items():
                if len(data_points) < period + 1:
                    continue
                
                # Calculate percentage change over period
                old_price = float(data_points[-period-1].close)
                new_price = float(data_points[-1].close)
                pct_change = (new_price - old_price) / old_price
                
                # Add to base currency (positive change = stronger)
                base = symbol.base_asset
                quote = symbol.quote_asset
                
                if base in currency_changes:
                    currency_changes[base] += pct_change
                    currency_counts[base] += 1
                
                # Subtract from quote currency (pair up = quote weaker)
                if quote in currency_changes:
                    currency_changes[quote] -= pct_change
                    currency_counts[quote] += 1
            
            # Calculate average strength
            strength_scores = {}
            for currency in self.MAJOR_CURRENCIES:
                if currency_counts[currency] > 0:
                    avg_strength = currency_changes[currency] / currency_counts[currency]
                    strength_scores[currency] = avg_strength
                else:
                    strength_scores[currency] = 0.0
            
            return strength_scores
            
        except Exception as e:
            self.logger.error(f"Error calculating currency strength: {str(e)}")
            return {}
    
    def correlation_coefficient(self, prices1: List[float], prices2: List[float], 
                              period: int = 20) -> Optional[float]:
        """
        Calculate correlation coefficient between two price series.
        
        Args:
            prices1: First price series
            prices2: Second price series
            period: Period for correlation calculation
            
        Returns:
            Optional[float]: Correlation coefficient (-1 to 1)
        """
        try:
            if len(prices1) < period or len(prices2) < period:
                return None
            
            # Use last 'period' prices
            p1 = prices1[-period:]
            p2 = prices2[-period:]
            
            if len(p1) != len(p2):
                return None
            
            # Calculate means
            mean1 = sum(p1) / len(p1)
            mean2 = sum(p2) / len(p2)
            
            # Calculate correlation coefficient
            numerator = sum((p1[i] - mean1) * (p2[i] - mean2) for i in range(len(p1)))
            
            sum_sq1 = sum((p1[i] - mean1) ** 2 for i in range(len(p1)))
            sum_sq2 = sum((p2[i] - mean2) ** 2 for i in range(len(p2)))
            
            denominator = math.sqrt(sum_sq1 * sum_sq2)
            
            if denominator == 0:
                return 0.0
            
            correlation = numerator / denominator
            return max(-1.0, min(1.0, correlation))  # Clamp to [-1, 1]
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {str(e)}")
            return None
    
    def forex_momentum(self, prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate forex-specific momentum indicator.
        
        Args:
            prices: List of prices
            period: Momentum period
            
        Returns:
            Optional[float]: Momentum value
        """
        try:
            if len(prices) < period + 1:
                return None
            
            current_price = prices[-1]
            past_price = prices[-period-1]
            
            momentum = (current_price - past_price) / past_price * 100
            return momentum
            
        except Exception as e:
            self.logger.error(f"Error calculating forex momentum: {str(e)}")
            return None
    
    def williams_percent_r(self, high_prices: List[float], low_prices: List[float], 
                          close_prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate Williams %R oscillator.
        
        Args:
            high_prices: List of high prices
            low_prices: List of low prices
            close_prices: List of close prices
            period: Period for calculation
            
        Returns:
            Optional[float]: Williams %R value (-100 to 0)
        """
        try:
            if len(high_prices) < period or len(low_prices) < period or len(close_prices) < period:
                return None
            
            # Get recent data
            recent_highs = high_prices[-period:]
            recent_lows = low_prices[-period:]
            current_close = close_prices[-1]
            
            highest_high = max(recent_highs)
            lowest_low = min(recent_lows)
            
            if highest_high == lowest_low:
                return -50.0  # Neutral value
            
            williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
            return williams_r
            
        except Exception as e:
            self.logger.error(f"Error calculating Williams %R: {str(e)}")
            return None
    
    def commodity_channel_index(self, high_prices: List[float], low_prices: List[float], 
                               close_prices: List[float], period: int = 20) -> Optional[float]:
        """
        Calculate Commodity Channel Index (CCI).
        
        Args:
            high_prices: List of high prices
            low_prices: List of low prices
            close_prices: List of close prices
            period: Period for calculation
            
        Returns:
            Optional[float]: CCI value
        """
        try:
            if len(high_prices) < period or len(low_prices) < period or len(close_prices) < period:
                return None
            
            # Calculate typical prices
            typical_prices = []
            for i in range(len(close_prices)):
                tp = (high_prices[i] + low_prices[i] + close_prices[i]) / 3
                typical_prices.append(tp)
            
            # Get recent typical prices
            recent_tp = typical_prices[-period:]
            
            # Calculate SMA of typical prices
            sma_tp = sum(recent_tp) / period
            
            # Calculate mean deviation
            mean_deviation = sum(abs(tp - sma_tp) for tp in recent_tp) / period
            
            if mean_deviation == 0:
                return 0.0
            
            # Calculate CCI
            current_tp = typical_prices[-1]
            cci = (current_tp - sma_tp) / (0.015 * mean_deviation)
            
            return cci
            
        except Exception as e:
            self.logger.error(f"Error calculating CCI: {str(e)}")
            return None
    
    def forex_volatility_bands(self, prices: List[float], period: int = 20, 
                              multiplier: float = 2.0) -> Optional[Tuple[float, float, float]]:
        """
        Calculate volatility bands similar to Bollinger Bands but optimized for forex.
        
        Args:
            prices: List of prices
            period: Period for calculation
            multiplier: Standard deviation multiplier
            
        Returns:
            Optional[Tuple[float, float, float]]: (Upper, Middle, Lower) bands
        """
        try:
            if len(prices) < period:
                return None
            
            # Calculate EMA instead of SMA for more responsive bands
            ema_values = self.ema(prices, period)
            if not ema_values:
                return None
            
            middle = ema_values[-1]
            
            # Calculate standard deviation of recent prices
            recent_prices = prices[-period:]
            mean_price = sum(recent_prices) / period
            variance = sum((price - mean_price) ** 2 for price in recent_prices) / period
            std_dev = variance ** 0.5
            
            upper = middle + (multiplier * std_dev)
            lower = middle - (multiplier * std_dev)
            
            return upper, middle, lower
            
        except Exception as e:
            self.logger.error(f"Error calculating forex volatility bands: {str(e)}")
            return None
    
    def detect_forex_patterns(self, data_points: List[UnifiedMarketData]) -> List[str]:
        """
        Detect common forex chart patterns.
        
        Args:
            data_points: List of market data points
            
        Returns:
            List[str]: List of detected patterns
        """
        patterns = []
        
        try:
            if len(data_points) < 10:
                return patterns
            
            highs = [float(d.high) for d in data_points]
            lows = [float(d.low) for d in data_points]
            closes = [float(d.close) for d in data_points]
            
            # Simple pattern detection
            patterns.extend(self._detect_double_top_bottom(highs, lows))
            patterns.extend(self._detect_head_shoulders(highs, lows))
            patterns.extend(self._detect_triangles(highs, lows))
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting forex patterns: {str(e)}")
            return []
    
    def _detect_double_top_bottom(self, highs: List[float], lows: List[float]) -> List[str]:
        """Detect double top/bottom patterns."""
        patterns = []
        
        try:
            # Simple double top detection
            if len(highs) >= 5:
                recent_highs = highs[-5:]
                max_high = max(recent_highs)
                high_count = sum(1 for h in recent_highs if abs(h - max_high) / max_high < 0.001)
                
                if high_count >= 2:
                    patterns.append("double_top")
            
            # Simple double bottom detection
            if len(lows) >= 5:
                recent_lows = lows[-5:]
                min_low = min(recent_lows)
                low_count = sum(1 for l in recent_lows if abs(l - min_low) / min_low < 0.001)
                
                if low_count >= 2:
                    patterns.append("double_bottom")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting double top/bottom: {str(e)}")
            return []
    
    def _detect_head_shoulders(self, highs: List[float], lows: List[float]) -> List[str]:
        """Detect head and shoulders patterns."""
        patterns = []
        
        try:
            # Simplified head and shoulders detection
            if len(highs) >= 7:
                recent_highs = highs[-7:]
                
                # Look for three peaks with middle one being highest
                if (recent_highs[1] < recent_highs[3] > recent_highs[5] and
                    abs(recent_highs[1] - recent_highs[5]) / recent_highs[3] < 0.02):
                    patterns.append("head_shoulders")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting head and shoulders: {str(e)}")
            return []
    
    def _detect_triangles(self, highs: List[float], lows: List[float]) -> List[str]:
        """Detect triangle patterns."""
        patterns = []
        
        try:
            if len(highs) >= 6 and len(lows) >= 6:
                recent_highs = highs[-6:]
                recent_lows = lows[-6:]
                
                # Check for ascending triangle (flat resistance, rising support)
                high_trend = self._calculate_trend(recent_highs)
                low_trend = self._calculate_trend(recent_lows)
                
                if abs(high_trend) < 0.001 and low_trend > 0.001:
                    patterns.append("ascending_triangle")
                elif abs(low_trend) < 0.001 and high_trend < -0.001:
                    patterns.append("descending_triangle")
                elif high_trend < -0.001 and low_trend > 0.001:
                    patterns.append("symmetrical_triangle")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting triangles: {str(e)}")
            return []
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate simple trend slope."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        denominator = n * x2_sum - x_sum * x_sum
        if denominator == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / denominator
        return slope