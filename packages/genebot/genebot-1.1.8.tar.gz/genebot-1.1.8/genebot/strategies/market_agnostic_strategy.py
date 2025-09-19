"""
Market-agnostic strategy base class for cross-market trading strategies.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

from .base_strategy import BaseStrategy, StrategyConfig
from ..models.data_models import MarketData, UnifiedMarketData, TradingSignal
from ..markets.types import MarketType, UnifiedSymbol


class MarketAgnosticStrategy(BaseStrategy):
    """
    Abstract base class for market-agnostic trading strategies.
    
    Market-agnostic strategies can operate across different market types
    (crypto, forex, etc.) using unified data formats and interfaces.
    These strategies focus on universal market patterns and behaviors
    that transcend specific market characteristics.
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the market-agnostic strategy.
        
        Args:
            config: Strategy configuration parameters
        """
        super().__init__(config)
        
        # Market-agnostic specific configuration
        self.supported_markets = [MarketType.CRYPTO, MarketType.FOREX]
        self.market_weights = config.parameters.get('market_weights', {})
        self.cross_market_correlation_threshold = config.parameters.get(
            'cross_market_correlation_threshold', 0.7
        )
        
        # Data management
        self._unified_data_history: Dict[str, List[UnifiedMarketData]] = {}
        self._market_data_history: Dict[MarketType, List[UnifiedMarketData]] = {
            MarketType.CRYPTO: [],
            MarketType.FOREX: []
        }
        
        self.logger = logging.getLogger(f"market_agnostic_strategy.{self.name}")
    
    @abstractmethod
    def analyze_unified_data(self, market_data: List[UnifiedMarketData]) -> Optional[TradingSignal]:
        """
        Analyze unified market data and generate trading signals.
        
        This method should implement the core strategy logic that works
        across different market types using unified data formats.
        
        Args:
            market_data: List of unified market data points for analysis
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        pass
    
    @abstractmethod
    def get_cross_market_correlation_threshold(self) -> float:
        """
        Get the correlation threshold for cross-market analysis.
        
        Returns:
            float: Correlation threshold (0.0 to 1.0)
        """
        pass
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze legacy market data (backward compatibility).
        
        This method converts legacy MarketData to UnifiedMarketData
        and delegates to analyze_unified_data.
        
        Args:
            market_data: List of legacy market data points
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        try:
            # Convert legacy data to unified format (assume crypto)
            unified_data = []
            for data in market_data:
                unified = UnifiedMarketData.from_legacy_market_data(data, MarketType.CRYPTO)
                unified_data.append(unified)
            
            return self.analyze_unified_data(unified_data)
            
        except Exception as e:
            self.logger.error(f"Error converting legacy data in {self.name}: {str(e)}")
            return None
    
    def process_market_data(self, market_data: Union[List[MarketData], List[UnifiedMarketData]]) -> Optional[TradingSignal]:
        """
        Process market data (supports both legacy and unified formats).
        
        Args:
            market_data: List of market data points (legacy or unified)
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        if not self.is_running():
            return None
        
        # Determine data format and process accordingly
        if not market_data:
            return None
        
        # Check if we have unified data
        if isinstance(market_data[0], UnifiedMarketData):
            return self._process_unified_data(market_data)
        else:
            # Legacy data processing
            return super().process_market_data(market_data)
    
    def _process_unified_data(self, market_data: List[UnifiedMarketData]) -> Optional[TradingSignal]:
        """
        Process unified market data.
        
        Args:
            market_data: List of unified market data points
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        if len(market_data) < self.get_required_data_length():
            self.logger.debug(f"Insufficient unified data for {self.name}: "
                            f"need {self.get_required_data_length()}, got {len(market_data)}")
            return None
        
        try:
            # Update data history
            self._update_data_history(market_data)
            
            # Analyze data
            signal = self.analyze_unified_data(market_data)
            
            if signal:
                self.signals_generated += 1
                self._last_signal_time = datetime.now()
                self.logger.info(f"Signal generated by {self.name}: {signal.action} {signal.symbol}")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in market-agnostic strategy {self.name}: {str(e)}")
            return None
    
    def get_market_data_history(self, market_type: Optional[MarketType] = None) -> List[UnifiedMarketData]:
        """
        Get historical market data for analysis.
        
        Args:
            market_type: Specific market type to get data for (None for all)
            
        Returns:
            List[UnifiedMarketData]: Historical market data
        """
        if market_type is None:
            # Return all data combined
            all_data = []
            for data_list in self._market_data_history.values():
                all_data.extend(data_list)
            return sorted(all_data, key=lambda x: x.timestamp)
        else:
            return self._market_data_history.get(market_type, [])
    
    def get_symbol_data_history(self, symbol: Union[str, UnifiedSymbol]) -> List[UnifiedMarketData]:
        """
        Get historical data for a specific symbol.
        
        Args:
            symbol: Symbol to get data for (string or UnifiedSymbol)
            
        Returns:
            List[UnifiedMarketData]: Historical data for the symbol
        """
        if isinstance(symbol, UnifiedSymbol):
            symbol_key = symbol.to_standard_format()
        else:
            symbol_key = symbol
            
        return self._unified_data_history.get(symbol_key, [])
    
    def calculate_cross_market_correlation(self, symbol1: str, symbol2: str, 
                                         periods: int = 20) -> Optional[float]:
        """
        Calculate correlation between two symbols across markets.
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
            periods: Number of periods to calculate correlation over
            
        Returns:
            Optional[float]: Correlation coefficient (-1.0 to 1.0), None if insufficient data
        """
        try:
            data1 = self.get_symbol_data_history(symbol1)[-periods:]
            data2 = self.get_symbol_data_history(symbol2)[-periods:]
            
            if len(data1) < periods or len(data2) < periods:
                return None
            
            # Extract closing prices
            prices1 = [float(d.close) for d in data1]
            prices2 = [float(d.close) for d in data2]
            
            # Calculate correlation
            return self._calculate_correlation(prices1, prices2)
            
        except Exception as e:
            self.logger.error(f"Error calculating cross-market correlation: {str(e)}")
            return None
    
    def is_cross_market_correlated(self, symbol1: str, symbol2: str) -> bool:
        """
        Check if two symbols are significantly correlated across markets.
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
            
        Returns:
            bool: True if symbols are correlated above threshold
        """
        correlation = self.calculate_cross_market_correlation(symbol1, symbol2)
        if correlation is None:
            return False
        
        return abs(correlation) >= self.cross_market_correlation_threshold
    
    def get_market_weight(self, market_type: MarketType) -> float:
        """
        Get the weight assigned to a specific market type.
        
        Args:
            market_type: Market type to get weight for
            
        Returns:
            float: Market weight (default 1.0 if not specified)
        """
        return self.market_weights.get(market_type.value, 1.0)
    
    def supports_market_type(self, market_type: MarketType) -> bool:
        """
        Check if this strategy supports a specific market type.
        
        Args:
            market_type: Market type to check
            
        Returns:
            bool: True if market type is supported
        """
        return market_type in self.supported_markets
    
    def get_supported_markets(self) -> List[MarketType]:
        """
        Get list of supported market types.
        
        Returns:
            List[MarketType]: List of supported market types
        """
        return self.supported_markets.copy()
    
    def validate_parameters(self) -> bool:
        """
        Validate market-agnostic strategy parameters.
        
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        try:
            # Validate base parameters
            if not super().validate_parameters():
                return False
            
            # Validate market weights
            if self.market_weights:
                for market, weight in self.market_weights.items():
                    if not isinstance(weight, (int, float)) or weight < 0:
                        self.logger.error(f"Invalid market weight for {market}: {weight}")
                        return False
            
            # Validate correlation threshold
            if not 0.0 <= self.cross_market_correlation_threshold <= 1.0:
                self.logger.error(f"Invalid correlation threshold: {self.cross_market_correlation_threshold}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _update_data_history(self, market_data: List[UnifiedMarketData]):
        """
        Update internal data history with new market data.
        
        Args:
            market_data: New market data to add to history
        """
        for data in market_data:
            # Update symbol-specific history
            symbol_key = data.symbol.to_standard_format()
            if symbol_key not in self._unified_data_history:
                self._unified_data_history[symbol_key] = []
            
            self._unified_data_history[symbol_key].append(data)
            
            # Keep only recent data (last 1000 points per symbol)
            self._unified_data_history[symbol_key] = self._unified_data_history[symbol_key][-1000:]
            
            # Update market-specific history
            market_type = data.market_type
            self._market_data_history[market_type].append(data)
            
            # Keep only recent data (last 500 points per market)
            self._market_data_history[market_type] = self._market_data_history[market_type][-500:]
    
    def _calculate_correlation(self, prices1: List[float], prices2: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient between two price series.
        
        Args:
            prices1: First price series
            prices2: Second price series
            
        Returns:
            float: Correlation coefficient (-1.0 to 1.0)
        """
        if len(prices1) != len(prices2) or len(prices1) < 2:
            return 0.0
        
        # Calculate means
        mean1 = sum(prices1) / len(prices1)
        mean2 = sum(prices2) / len(prices2)
        
        # Calculate correlation components
        numerator = sum((p1 - mean1) * (p2 - mean2) for p1, p2 in zip(prices1, prices2))
        
        sum_sq1 = sum((p1 - mean1) ** 2 for p1 in prices1)
        sum_sq2 = sum((p2 - mean2) ** 2 for p2 in prices2)
        
        denominator = (sum_sq1 * sum_sq2) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get enhanced performance metrics including cross-market data.
        
        Returns:
            Dict[str, Any]: Enhanced performance metrics
        """
        base_metrics = super().get_performance_metrics()
        
        # Add market-agnostic specific metrics
        base_metrics.update({
            'strategy_type': 'market_agnostic',
            'supported_markets': [m.value for m in self.supported_markets],
            'market_weights': self.market_weights,
            'cross_market_correlation_threshold': self.cross_market_correlation_threshold,
            'data_history_size': {
                market.value: len(data_list) 
                for market, data_list in self._market_data_history.items()
            },
            'symbols_tracked': len(self._unified_data_history)
        })
        
        return base_metrics