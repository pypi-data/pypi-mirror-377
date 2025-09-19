"""
Market-specific strategy base class for single-market trading strategies.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime
import logging

from .base_strategy import BaseStrategy, StrategyConfig
from ..models.data_models import MarketData, UnifiedMarketData, TradingSignal, SessionInfo
from ..markets.types import MarketType, UnifiedSymbol


class MarketSpecificStrategy(BaseStrategy):
    """
    Abstract base class for market-specific trading strategies.
    
    Market-specific strategies are designed to operate on a single market type
    (e.g., crypto or forex) and can leverage market-specific characteristics,
    trading sessions, and specialized features.
    """
    
    def __init__(self, config: StrategyConfig, supported_markets: List[MarketType]):
        """
        Initialize the market-specific strategy.
        
        Args:
            config: Strategy configuration parameters
            supported_markets: List of market types this strategy supports
        """
        super().__init__(config)
        
        if not supported_markets:
            raise ValueError("Market-specific strategy must support at least one market type")
        
        self.supported_markets = supported_markets
        self.primary_market = supported_markets[0]  # Primary market for this strategy
        
        # Market-specific configuration
        self.market_filters = config.parameters.get('market_filters', {})
        self.session_aware = config.parameters.get('session_aware', True)
        self.market_specific_params = config.parameters.get('market_specific_params', {})
        
        # Session management
        self._active_sessions: Dict[MarketType, bool] = {
            market: True for market in self.supported_markets
        }
        self._session_history: Dict[MarketType, List[SessionInfo]] = {
            market: [] for market in self.supported_markets
        }
        
        # Market-specific data management
        self._market_data_cache: Dict[MarketType, List[UnifiedMarketData]] = {
            market: [] for market in self.supported_markets
        }
        
        self.logger = logging.getLogger(f"market_specific_strategy.{self.name}")
    
    @abstractmethod
    def analyze_market_data(self, market_data: List[UnifiedMarketData], 
                           market_type: MarketType) -> Optional[TradingSignal]:
        """
        Analyze market data for a specific market type.
        
        This method should implement the core strategy logic that is
        optimized for the specific market type characteristics.
        
        Args:
            market_data: List of unified market data points for analysis
            market_type: The market type being analyzed
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        pass
    
    @abstractmethod
    def get_market_specific_parameters(self, market_type: MarketType) -> Dict[str, Any]:
        """
        Get parameters specific to a market type.
        
        Args:
            market_type: Market type to get parameters for
            
        Returns:
            Dict[str, Any]: Market-specific parameters
        """
        pass
    
    @abstractmethod
    def validate_market_conditions(self, market_data: List[UnifiedMarketData], 
                                 market_type: MarketType) -> bool:
        """
        Validate if market conditions are suitable for strategy execution.
        
        Args:
            market_data: Market data to validate
            market_type: Market type being validated
            
        Returns:
            bool: True if conditions are suitable, False otherwise
        """
        pass
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze legacy market data (backward compatibility).
        
        This method converts legacy MarketData to UnifiedMarketData
        and delegates to analyze_market_data.
        
        Args:
            market_data: List of legacy market data points
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        try:
            # Convert legacy data to unified format (use primary market)
            unified_data = []
            for data in market_data:
                unified = UnifiedMarketData.from_legacy_market_data(data, self.primary_market)
                unified_data.append(unified)
            
            return self.analyze_market_data(unified_data, self.primary_market)
            
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
            # Filter data by supported markets
            filtered_data = self._filter_market_data(market_data)
            if not filtered_data:
                return None
            
            # Group data by market type
            market_groups = self._group_data_by_market(filtered_data)
            
            # Process each market type
            signals = []
            for market_type, data_list in market_groups.items():
                if not data_list:
                    continue
                
                # Check if market session is active (if session-aware)
                if self.session_aware and not self._is_market_session_active(market_type, data_list):
                    self.logger.debug(f"Skipping {market_type.value} - market session inactive")
                    continue
                
                # Validate market conditions
                if not self.validate_market_conditions(data_list, market_type):
                    self.logger.debug(f"Market conditions not suitable for {market_type.value}")
                    continue
                
                # Update data cache
                self._update_market_cache(market_type, data_list)
                
                # Analyze market data
                signal = self.analyze_market_data(data_list, market_type)
                if signal:
                    signals.append(signal)
            
            # Return the first valid signal (strategies should focus on one market at a time)
            if signals:
                signal = signals[0]
                self.signals_generated += 1
                self._last_signal_time = datetime.now()
                self.logger.info(f"Signal generated by {self.name}: {signal.action} {signal.symbol}")
                return signal
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in market-specific strategy {self.name}: {str(e)}")
            return None
    
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
    
    def get_primary_market(self) -> MarketType:
        """
        Get the primary market type for this strategy.
        
        Returns:
            MarketType: Primary market type
        """
        return self.primary_market
    
    def set_market_session_status(self, market_type: MarketType, is_active: bool):
        """
        Set the session status for a specific market.
        
        Args:
            market_type: Market type to update
            is_active: Whether the market session is active
        """
        if market_type in self.supported_markets:
            self._active_sessions[market_type] = is_active
            self.logger.debug(f"Market session {market_type.value} set to {'active' if is_active else 'inactive'}")
    
    def is_market_session_active(self, market_type: MarketType) -> bool:
        """
        Check if a market session is currently active.
        
        Args:
            market_type: Market type to check
            
        Returns:
            bool: True if session is active, False otherwise
        """
        return self._active_sessions.get(market_type, True)
    
    def update_session_info(self, market_type: MarketType, session_info: SessionInfo):
        """
        Update session information for a market.
        
        Args:
            market_type: Market type to update
            session_info: New session information
        """
        if market_type in self.supported_markets:
            self._session_history[market_type].append(session_info)
            # Keep only recent session history (last 100 entries)
            self._session_history[market_type] = self._session_history[market_type][-100:]
            
            # Update active session status
            self.set_market_session_status(market_type, session_info.is_active)
    
    def get_market_data_cache(self, market_type: MarketType) -> List[UnifiedMarketData]:
        """
        Get cached market data for a specific market type.
        
        Args:
            market_type: Market type to get data for
            
        Returns:
            List[UnifiedMarketData]: Cached market data
        """
        return self._market_data_cache.get(market_type, [])
    
    def apply_market_filter(self, symbol: UnifiedSymbol) -> bool:
        """
        Apply market-specific filters to determine if symbol should be processed.
        
        Args:
            symbol: Symbol to filter
            
        Returns:
            bool: True if symbol passes filters, False otherwise
        """
        market_type = symbol.market_type
        
        # Check if market type is supported
        if not self.supports_market_type(market_type):
            return False
        
        # Apply market-specific filters
        market_filters = self.market_filters.get(market_type.value, {})
        
        # Symbol whitelist/blacklist
        if 'allowed_symbols' in market_filters:
            allowed = market_filters['allowed_symbols']
            if symbol.to_standard_format() not in allowed:
                return False
        
        if 'blocked_symbols' in market_filters:
            blocked = market_filters['blocked_symbols']
            if symbol.to_standard_format() in blocked:
                return False
        
        # Asset filters
        if 'allowed_base_assets' in market_filters:
            allowed_base = market_filters['allowed_base_assets']
            if symbol.base_asset not in allowed_base:
                return False
        
        if 'allowed_quote_assets' in market_filters:
            allowed_quote = market_filters['allowed_quote_assets']
            if symbol.quote_asset not in allowed_quote:
                return False
        
        return True
    
    def validate_parameters(self) -> bool:
        """
        Validate market-specific strategy parameters.
        
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        try:
            # Validate basic strategy configuration
            if not self.name:
                self.logger.error("Strategy name cannot be empty")
                return False
            
            # Validate supported markets
            if not self.supported_markets:
                self.logger.error("No supported markets specified")
                return False
            
            # Validate market filters
            if self.market_filters:
                for market_type_str, filters in self.market_filters.items():
                    try:
                        MarketType(market_type_str)  # Validate market type
                    except ValueError:
                        self.logger.error(f"Invalid market type in filters: {market_type_str}")
                        return False
            
            # Validate market-specific parameters for each supported market
            for market_type in self.supported_markets:
                params = self.get_market_specific_parameters(market_type)
                if not isinstance(params, dict):
                    self.logger.error(f"Invalid parameters for market {market_type.value}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _filter_market_data(self, market_data: List[UnifiedMarketData]) -> List[UnifiedMarketData]:
        """
        Filter market data based on supported markets and filters.
        
        Args:
            market_data: Raw market data
            
        Returns:
            List[UnifiedMarketData]: Filtered market data
        """
        filtered_data = []
        
        for data in market_data:
            # Check if market type is supported
            if not self.supports_market_type(data.market_type):
                continue
            
            # Apply symbol filters
            if not self.apply_market_filter(data.symbol):
                continue
            
            filtered_data.append(data)
        
        return filtered_data
    
    def _group_data_by_market(self, market_data: List[UnifiedMarketData]) -> Dict[MarketType, List[UnifiedMarketData]]:
        """
        Group market data by market type.
        
        Args:
            market_data: Market data to group
            
        Returns:
            Dict[MarketType, List[UnifiedMarketData]]: Data grouped by market type
        """
        groups = {market_type: [] for market_type in self.supported_markets}
        
        for data in market_data:
            if data.market_type in groups:
                groups[data.market_type].append(data)
        
        return groups
    
    def _is_market_session_active(self, market_type: MarketType, 
                                market_data: List[UnifiedMarketData]) -> bool:
        """
        Check if market session is active based on data and session info.
        
        Args:
            market_type: Market type to check
            market_data: Market data to analyze
            
        Returns:
            bool: True if session is active
        """
        if not self.session_aware:
            return True
        
        # Check cached session status
        if not self.is_market_session_active(market_type):
            return False
        
        # Check session info from data
        for data in market_data:
            if data.session_info and not data.session_info.is_active:
                return False
        
        return True
    
    def _update_market_cache(self, market_type: MarketType, market_data: List[UnifiedMarketData]):
        """
        Update market data cache.
        
        Args:
            market_type: Market type to update
            market_data: New market data
        """
        if market_type not in self._market_data_cache:
            self._market_data_cache[market_type] = []
        
        self._market_data_cache[market_type].extend(market_data)
        
        # Keep only recent data (last 1000 points per market)
        self._market_data_cache[market_type] = self._market_data_cache[market_type][-1000:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get enhanced performance metrics including market-specific data.
        
        Returns:
            Dict[str, Any]: Enhanced performance metrics
        """
        base_metrics = super().get_performance_metrics()
        
        # Add market-specific metrics
        base_metrics.update({
            'strategy_type': 'market_specific',
            'supported_markets': [m.value for m in self.supported_markets],
            'primary_market': self.primary_market.value,
            'session_aware': self.session_aware,
            'active_sessions': {
                market.value: is_active 
                for market, is_active in self._active_sessions.items()
            },
            'market_data_cache_size': {
                market.value: len(data_list) 
                for market, data_list in self._market_data_cache.items()
            },
            'market_filters': self.market_filters
        })
        
        return base_metrics