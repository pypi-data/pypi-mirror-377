"""
Forex carry trade strategy that exploits interest rate differentials.

This strategy identifies currency pairs with significant interest rate differentials
and trades in the direction that earns positive carry (swap) while managing risk
through technical analysis and correlation monitoring.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .market_specific_strategy import MarketSpecificStrategy, StrategyConfig
from ..models.data_models import UnifiedMarketData, TradingSignal, SignalAction
from ..markets.types import MarketType, UnifiedSymbol
from .technical_indicators import TechnicalIndicators


class ForexCarryTradeStrategy(MarketSpecificStrategy):
    """
    Forex carry trade strategy based on interest rate differentials.
    
    This strategy:
    1. Identifies currency pairs with favorable interest rate differentials
    2. Goes long high-yield currencies vs low-yield currencies
    3. Uses technical analysis to time entries and exits
    4. Monitors risk through correlation and volatility analysis
    """
    
    # Interest rates (approximate, should be updated from real data)
    # These are example rates - in production, these should come from economic data feeds
    INTEREST_RATES = {
        'USD': 5.25,   # US Federal Reserve rate
        'EUR': 4.50,   # ECB rate
        'GBP': 5.25,   # Bank of England rate
        'JPY': -0.10,  # Bank of Japan rate
        'CHF': 1.75,   # Swiss National Bank rate
        'AUD': 4.35,   # Reserve Bank of Australia rate
        'NZD': 5.50,   # Reserve Bank of New Zealand rate
        'CAD': 5.00,   # Bank of Canada rate
        'NOK': 4.50,   # Norges Bank rate
        'SEK': 4.00,   # Sveriges Riksbank rate
    }
    
    # Currency risk scores (higher = more volatile/risky)
    CURRENCY_RISK_SCORES = {
        'USD': 1.0,  # Base currency
        'EUR': 1.1,
        'GBP': 1.3,
        'JPY': 1.2,
        'CHF': 0.9,
        'AUD': 1.5,
        'NZD': 1.7,
        'CAD': 1.2,
        'NOK': 1.6,
        'SEK': 1.4,
    }
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize forex carry trade strategy.
        
        Args:
            config: Strategy configuration
        """
        # Only support forex markets
        super().__init__(config, [MarketType.FOREX])
        
        self.indicators = TechnicalIndicators()
        
        # Strategy parameters
        params = config.parameters
        self.min_rate_differential = params.get('min_rate_differential', 1.0)  # Minimum 1% differential
        self.max_risk_score = params.get('max_risk_score', 2.0)  # Maximum risk tolerance
        self.trend_period = params.get('trend_period', 50)
        self.volatility_period = params.get('volatility_period', 20)
        self.max_volatility = params.get('max_volatility', 0.02)  # 2% daily volatility
        self.rsi_period = params.get('rsi_period', 14)
        self.rsi_neutral_min = params.get('rsi_neutral_min', 40)
        self.rsi_neutral_max = params.get('rsi_neutral_max', 60)
        
        # Carry trade specific settings
        self.min_holding_days = params.get('min_holding_days', 7)  # Minimum holding period
        self.correlation_threshold = params.get('correlation_threshold', 0.7)  # Max correlation with other positions
        self.swap_importance = params.get('swap_importance', 0.3)  # Weight of swap in decision
        
        # Position tracking
        self._carry_positions: Dict[str, Dict[str, Any]] = {}
        self._rate_history: Dict[str, List[Tuple[datetime, float]]] = {}
        
        self.logger = logging.getLogger(f"forex_carry_trade_strategy.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the forex carry trade strategy."""
        try:
            self.logger.info(f"Initializing forex carry trade strategy: {self.name}")
            
            # Initialize rate history tracking
            for currency in self.INTEREST_RATES:
                self._rate_history[currency] = []
            
            # Log current rate differentials
            self._log_rate_differentials()
            
            self.logger.info("Carry trade strategy initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze_market_data(self, market_data: List[UnifiedMarketData], 
                           market_type: MarketType) -> Optional[TradingSignal]:
        """
        Analyze forex market data for carry trade opportunities.
        
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
            
            # Analyze each symbol for carry trade potential
            best_signal = None
            best_score = 0.0
            
            for symbol, data_points in symbol_data.items():
                if len(data_points) < self.get_required_data_length():
                    continue
                
                # Check if this pair has good carry potential
                carry_score = self._calculate_carry_score(symbol)
                if carry_score < 0.5:  # Minimum carry attractiveness
                    continue
                
                # Analyze technical conditions
                signal = self._analyze_carry_opportunity(symbol, data_points, carry_score)
                if signal and signal.confidence > best_score:
                    best_signal = signal
                    best_score = signal.confidence
            
            return best_signal
            
        except Exception as e:
            self.logger.error(f"Error analyzing market data: {str(e)}")
            return None
    
    def get_market_specific_parameters(self, market_type: MarketType) -> Dict[str, Any]:
        """Get forex carry trade specific parameters."""
        if market_type != MarketType.FOREX:
            return {}
        
        return {
            'min_rate_differential': self.min_rate_differential,
            'max_risk_score': self.max_risk_score,
            'trend_period': self.trend_period,
            'volatility_period': self.volatility_period,
            'max_volatility': self.max_volatility,
            'min_holding_days': self.min_holding_days,
            'correlation_threshold': self.correlation_threshold,
            'swap_importance': self.swap_importance
        }
    
    def validate_market_conditions(self, market_data: List[UnifiedMarketData], 
                                 market_type: MarketType) -> bool:
        """
        Validate if market conditions are suitable for carry trading.
        
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
            # Check for recent data
            latest_data = market_data[-1]
            time_diff = datetime.now() - latest_data.timestamp.replace(tzinfo=None)
            if time_diff.total_seconds() > 3600:  # 1 hour old
                return False
            
            # Check overall market volatility
            if len(market_data) >= self.volatility_period:
                avg_volatility = self._calculate_average_volatility(market_data)
                if avg_volatility > self.max_volatility * 2:  # Too volatile for carry trades
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating market conditions: {str(e)}")
            return False
    
    def get_required_data_length(self) -> int:
        """Get minimum data points required for analysis."""
        return max(self.trend_period, self.volatility_period, self.rsi_period) + 10
    
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        try:
            if not super().validate_parameters():
                return False
            
            # Validate carry trade specific parameters
            if self.min_rate_differential <= 0:
                self.logger.error("Minimum rate differential must be positive")
                return False
            
            if self.max_risk_score <= 0:
                self.logger.error("Maximum risk score must be positive")
                return False
            
            if not (0 < self.rsi_neutral_min < self.rsi_neutral_max < 100):
                self.logger.error("Invalid RSI neutral zone")
                return False
            
            if self.min_holding_days <= 0:
                self.logger.error("Minimum holding days must be positive")
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
    
    def _calculate_carry_score(self, symbol: UnifiedSymbol) -> float:
        """
        Calculate carry trade attractiveness score for a currency pair.
        
        Args:
            symbol: Currency pair symbol
            
        Returns:
            float: Carry score (0-1, higher is better)
        """
        try:
            base_currency = symbol.base_asset
            quote_currency = symbol.quote_asset
            
            # Get interest rates
            base_rate = self.INTEREST_RATES.get(base_currency, 0.0)
            quote_rate = self.INTEREST_RATES.get(quote_currency, 0.0)
            
            # Calculate rate differential
            rate_differential = base_rate - quote_rate
            
            # Check minimum differential requirement
            if abs(rate_differential) < self.min_rate_differential:
                return 0.0
            
            # Get risk scores
            base_risk = self.CURRENCY_RISK_SCORES.get(base_currency, 2.0)
            quote_risk = self.CURRENCY_RISK_SCORES.get(quote_currency, 2.0)
            avg_risk = (base_risk + quote_risk) / 2
            
            # Check risk tolerance
            if avg_risk > self.max_risk_score:
                return 0.0
            
            # Calculate carry score
            # Higher rate differential = better
            # Lower risk = better
            differential_score = min(abs(rate_differential) / 5.0, 1.0)  # Normalize to 0-1
            risk_score = max(0.0, (self.max_risk_score - avg_risk) / self.max_risk_score)
            
            carry_score = (differential_score * 0.7) + (risk_score * 0.3)
            
            return carry_score
            
        except Exception as e:
            self.logger.error(f"Error calculating carry score for {symbol}: {str(e)}")
            return 0.0
    
    def _analyze_carry_opportunity(self, symbol: UnifiedSymbol, 
                                 data_points: List[UnifiedMarketData],
                                 carry_score: float) -> Optional[TradingSignal]:
        """Analyze specific carry trade opportunity."""
        try:
            # Extract price data
            closes = [float(d.close) for d in data_points]
            highs = [float(d.high) for d in data_points]
            lows = [float(d.low) for d in data_points]
            
            # Calculate technical indicators
            sma_trend = self.indicators.sma(closes, self.trend_period)
            rsi = self.indicators.rsi(closes, self.rsi_period)
            atr = self.indicators.atr(highs, lows, closes, 14)
            
            if None in [sma_trend, rsi, atr]:
                return None
            
            # Calculate volatility
            volatility = self._calculate_volatility(data_points[-self.volatility_period:])
            if volatility > self.max_volatility:
                return None  # Too volatile for carry trade
            
            # Determine carry direction
            base_rate = self.INTEREST_RATES.get(symbol.base_asset, 0.0)
            quote_rate = self.INTEREST_RATES.get(symbol.quote_asset, 0.0)
            rate_differential = base_rate - quote_rate
            
            # Positive differential = go long (buy base, sell quote)
            # Negative differential = go short (sell base, buy quote)
            preferred_direction = 1 if rate_differential > 0 else -1
            
            # Check technical conditions
            latest_data = data_points[-1]
            current_price = float(latest_data.close)
            trend_direction = 1 if current_price > sma_trend[-1] else -1
            
            # RSI should be in neutral zone for carry trades (avoid extremes)
            if not (self.rsi_neutral_min <= rsi <= self.rsi_neutral_max):
                return None
            
            # Check if technical trend aligns with carry direction
            alignment_score = 1.0 if trend_direction == preferred_direction else 0.3
            
            # Calculate final confidence
            technical_score = self._calculate_technical_score(
                current_price, sma_trend[-1], rsi, volatility
            )
            
            final_confidence = (
                carry_score * self.swap_importance +
                technical_score * (1 - self.swap_importance)
            ) * alignment_score
            
            if final_confidence > 0.6:  # Minimum confidence threshold
                action = SignalAction.BUY if preferred_direction > 0 else SignalAction.SELL
                
                # Calculate expected daily swap
                expected_swap = self._calculate_expected_swap(symbol, preferred_direction)
                
                return TradingSignal(
                    symbol=symbol.native_symbol,
                    action=action,
                    confidence=min(final_confidence, 1.0),
                    timestamp=latest_data.timestamp,
                    strategy_name=self.name,
                    price=Decimal(str(current_price)),
                    metadata={
                        'market_type': 'forex',
                        'strategy_type': 'carry_trade',
                        'rate_differential': rate_differential,
                        'expected_daily_swap': expected_swap,
                        'carry_score': carry_score,
                        'technical_score': technical_score,
                        'alignment_score': alignment_score,
                        'volatility': volatility,
                        'rsi': rsi,
                        'trend_direction': trend_direction,
                        'preferred_direction': preferred_direction,
                        'min_holding_days': self.min_holding_days
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing carry opportunity for {symbol}: {str(e)}")
            return None
    
    def _calculate_volatility(self, data_points: List[UnifiedMarketData]) -> float:
        """Calculate recent volatility."""
        if len(data_points) < 2:
            return 0.0
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(data_points)):
            prev_close = float(data_points[i-1].close)
            curr_close = float(data_points[i].close)
            daily_return = (curr_close - prev_close) / prev_close
            returns.append(daily_return)
        
        if not returns:
            return 0.0
        
        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = variance ** 0.5
        
        return volatility
    
    def _calculate_average_volatility(self, market_data: List[UnifiedMarketData]) -> float:
        """Calculate average volatility across all symbols."""
        symbol_data = self._group_data_by_symbol(market_data)
        volatilities = []
        
        for symbol, data_points in symbol_data.items():
            if len(data_points) >= self.volatility_period:
                vol = self._calculate_volatility(data_points[-self.volatility_period:])
                volatilities.append(vol)
        
        return sum(volatilities) / len(volatilities) if volatilities else 0.0
    
    def _calculate_technical_score(self, current_price: float, trend_price: float, 
                                 rsi: float, volatility: float) -> float:
        """Calculate technical analysis score."""
        # Trend score (closer to trend line = better)
        trend_diff = abs(current_price - trend_price) / trend_price
        trend_score = max(0.0, 1.0 - trend_diff * 10)  # Penalize large deviations
        
        # RSI score (neutral zone is preferred)
        rsi_center = (self.rsi_neutral_min + self.rsi_neutral_max) / 2
        rsi_diff = abs(rsi - rsi_center) / (self.rsi_neutral_max - rsi_center)
        rsi_score = max(0.0, 1.0 - rsi_diff)
        
        # Volatility score (lower volatility is better for carry trades)
        vol_score = max(0.0, 1.0 - (volatility / self.max_volatility))
        
        # Combine scores
        technical_score = (trend_score * 0.4) + (rsi_score * 0.3) + (vol_score * 0.3)
        
        return technical_score
    
    def _calculate_expected_swap(self, symbol: UnifiedSymbol, direction: int) -> float:
        """
        Calculate expected daily swap for a position.
        
        Args:
            symbol: Currency pair
            direction: 1 for long, -1 for short
            
        Returns:
            float: Expected daily swap in pips
        """
        try:
            base_rate = self.INTEREST_RATES.get(symbol.base_asset, 0.0)
            quote_rate = self.INTEREST_RATES.get(symbol.quote_asset, 0.0)
            
            # Calculate annual swap rate
            annual_swap_rate = (base_rate - quote_rate) / 100  # Convert percentage to decimal
            
            # Apply direction
            if direction < 0:  # Short position
                annual_swap_rate = -annual_swap_rate
            
            # Convert to daily rate (approximate)
            daily_swap_rate = annual_swap_rate / 365
            
            # Convert to pips (approximate, varies by pair)
            # This is a simplified calculation - in practice, swap rates are provided by brokers
            if symbol.quote_asset == 'JPY':
                pips_multiplier = 100  # JPY pairs
            else:
                pips_multiplier = 10000  # Most other pairs
            
            expected_daily_swap = daily_swap_rate * pips_multiplier
            
            return expected_daily_swap
            
        except Exception as e:
            self.logger.error(f"Error calculating expected swap: {str(e)}")
            return 0.0
    
    def _log_rate_differentials(self):
        """Log current interest rate differentials for major pairs."""
        major_pairs = [
            ('EUR', 'USD'), ('GBP', 'USD'), ('USD', 'JPY'), ('USD', 'CHF'),
            ('AUD', 'USD'), ('USD', 'CAD'), ('NZD', 'USD')
        ]
        
        self.logger.info("Current interest rate differentials:")
        for base, quote in major_pairs:
            base_rate = self.INTEREST_RATES.get(base, 0.0)
            quote_rate = self.INTEREST_RATES.get(quote, 0.0)
            differential = base_rate - quote_rate
            
            pair_name = f"{base}/{quote}"
            direction = "LONG" if differential > 0 else "SHORT"
            
            self.logger.info(f"{pair_name}: {differential:+.2f}% ({direction} for positive carry)")
    
    def update_interest_rates(self, rates: Dict[str, float]):
        """
        Update interest rates with fresh data.
        
        Args:
            rates: Dictionary of currency -> interest rate
        """
        for currency, rate in rates.items():
            if currency in self.INTEREST_RATES:
                old_rate = self.INTEREST_RATES[currency]
                self.INTEREST_RATES[currency] = rate
                
                # Track rate changes
                if currency not in self._rate_history:
                    self._rate_history[currency] = []
                
                self._rate_history[currency].append((datetime.now(), rate))
                
                # Keep only recent history
                cutoff_date = datetime.now() - timedelta(days=90)
                self._rate_history[currency] = [
                    (date, rate) for date, rate in self._rate_history[currency]
                    if date > cutoff_date
                ]
                
                if abs(rate - old_rate) > 0.25:  # Significant change
                    self.logger.info(f"Interest rate change for {currency}: {old_rate:.2f}% -> {rate:.2f}%")
        
        # Re-log differentials after update
        self._log_rate_differentials()