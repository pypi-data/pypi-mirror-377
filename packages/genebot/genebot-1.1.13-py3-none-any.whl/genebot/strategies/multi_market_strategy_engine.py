"""
Multi-market strategy engine for managing strategies across different market types.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading

from .strategy_engine import StrategyEngine
from .base_strategy import BaseStrategy
from .market_agnostic_strategy import MarketAgnosticStrategy
from .market_specific_strategy import MarketSpecificStrategy
from .strategy_registry import StrategyRegistry
from .signal_processor import SignalProcessor
from ..models.data_models import MarketData, UnifiedMarketData, TradingSignal
from ..markets.types import MarketType, UnifiedSymbol


class MultiMarketStrategyEngine(StrategyEngine):
    """
    Enhanced strategy engine that manages strategies across multiple market types.
    
    This engine extends the base StrategyEngine to support:
    - Market-specific strategy routing
    - Market-agnostic strategy execution
    - Market type validation and filtering
    - Cross-market strategy coordination
    """
    
    def __init__(self, 
                 strategy_registry: StrategyRegistry,
                 signal_processor: SignalProcessor,
                 max_workers: int = 4):
        """
        Initialize the multi-market strategy engine.
        
        Args:
            strategy_registry: Registry for managing strategies
            signal_processor: Processor for handling trading signals
            max_workers: Maximum number of worker threads for strategy execution
        """
        super().__init__(strategy_registry, signal_processor, max_workers)
        
        # Market-specific strategy tracking
        self._market_strategies: Dict[MarketType, Set[str]] = {
            MarketType.CRYPTO: set(),
            MarketType.FOREX: set()
        }
        self._agnostic_strategies: Set[str] = set()
        
        # Market data routing
        self._market_data_cache: Dict[MarketType, List[UnifiedMarketData]] = {
            MarketType.CRYPTO: [],
            MarketType.FOREX: []
        }
        
        # Enhanced statistics
        self._market_stats = {
            MarketType.CRYPTO: {
                'strategies_count': 0,
                'signals_generated': 0,
                'last_execution': None
            },
            MarketType.FOREX: {
                'strategies_count': 0,
                'signals_generated': 0,
                'last_execution': None
            }
        }
        
        self.logger = logging.getLogger("multi_market_strategy_engine")
        
    def add_strategy(self, strategy: BaseStrategy) -> bool:
        """
        Add a strategy to the engine with market type classification.
        
        Args:
            strategy: Strategy instance to add
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        if not super().add_strategy(strategy):
            return False
            
        # Classify strategy by market support
        self._classify_strategy(strategy)
        
        return True
    
    def remove_strategy(self, strategy_name: str) -> bool:
        """
        Remove a strategy from the engine and update market classifications.
        
        Args:
            strategy_name: Name of the strategy to remove
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        if not super().remove_strategy(strategy_name):
            return False
            
        # Remove from market classifications
        self._remove_strategy_classification(strategy_name)
        
        return True
    
    def process_unified_market_data(self, market_data: List[UnifiedMarketData]) -> List[TradingSignal]:
        """
        Process unified market data through appropriate strategies.
        
        Args:
            market_data: List of unified market data points
            
        Returns:
            List[TradingSignal]: List of generated trading signals
        """
        if not self._running:
            return []
            
        start_time = datetime.now()
        signals = []
        
        try:
            # Group data by market type
            market_data_groups = self._group_data_by_market(market_data)
            
            # Update market data cache
            self._update_market_data_cache(market_data_groups)
            
            # Process each market type
            for market_type, data_list in market_data_groups.items():
                if not data_list:
                    continue
                    
                market_signals = self._process_market_data(market_type, data_list)
                signals.extend(market_signals)
                
                # Update market statistics
                self._market_stats[market_type]['signals_generated'] += len(market_signals)
                self._market_stats[market_type]['last_execution'] = datetime.now()
            
            # Process signals through signal processor
            if signals:
                processed_signals = self.signal_processor.process_signals(signals)
                self.logger.debug(f"Generated {len(signals)} signals, processed {len(processed_signals)}")
                signals = processed_signals
            
            # Update general statistics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(execution_time, len(signals) > 0)
            
        except Exception as e:
            self.logger.error(f"Error in multi-market strategy engine execution: {str(e)}")
            self._execution_stats['failed_executions'] += 1
            
        return signals
    
    def process_market_data(self, market_data: List[MarketData]) -> List[TradingSignal]:
        """
        Process legacy market data (backward compatibility).
        
        Args:
            market_data: List of legacy market data points
            
        Returns:
            List[TradingSignal]: List of generated trading signals
        """
        # Convert legacy data to unified format (assume crypto for backward compatibility)
        unified_data = []
        for data in market_data:
            try:
                unified = UnifiedMarketData.from_legacy_market_data(data, MarketType.CRYPTO)
                unified_data.append(unified)
            except Exception as e:
                self.logger.warning(f"Failed to convert legacy market data: {str(e)}")
                
        return self.process_unified_market_data(unified_data)
    
    def get_market_strategies(self, market_type: MarketType) -> List[str]:
        """
        Get strategies that support a specific market type.
        
        Args:
            market_type: Market type to query
            
        Returns:
            List[str]: List of strategy names supporting the market type
        """
        market_specific = list(self._market_strategies.get(market_type, set()))
        agnostic = list(self._agnostic_strategies)
        return market_specific + agnostic
    
    def get_strategy_market_support(self, strategy_name: str) -> List[MarketType]:
        """
        Get market types supported by a strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            List[MarketType]: List of supported market types
        """
        supported_markets = []
        
        # Check if strategy is market-agnostic
        if strategy_name in self._agnostic_strategies:
            return [MarketType.CRYPTO, MarketType.FOREX]
        
        # Check market-specific support
        for market_type, strategies in self._market_strategies.items():
            if strategy_name in strategies:
                supported_markets.append(market_type)
                
        return supported_markets
    
    def validate_strategy_market_compatibility(self, strategy_name: str, 
                                             market_data: UnifiedMarketData) -> bool:
        """
        Validate if a strategy can process data from a specific market.
        
        Args:
            strategy_name: Name of the strategy
            market_data: Market data to validate against
            
        Returns:
            bool: True if strategy can process the data, False otherwise
        """
        if strategy_name not in self._strategies:
            return False
            
        strategy = self._strategies[strategy_name]
        
        # Market-agnostic strategies can process any market data
        if isinstance(strategy, MarketAgnosticStrategy):
            return True
            
        # Market-specific strategies must match market type
        if isinstance(strategy, MarketSpecificStrategy):
            return strategy.supports_market_type(market_data.market_type)
            
        # Legacy strategies default to crypto support
        return market_data.market_type == MarketType.CRYPTO
    
    def get_multi_market_stats(self) -> Dict:
        """
        Get enhanced statistics including market-specific metrics.
        
        Returns:
            Dict: Enhanced engine statistics with market breakdown
        """
        base_stats = self.get_engine_stats()
        
        # Add market-specific statistics
        base_stats['market_breakdown'] = {}
        for market_type in MarketType:
            base_stats['market_breakdown'][market_type.value] = {
                'strategies_count': len(self._market_strategies.get(market_type, set())),
                'signals_generated': self._market_stats[market_type]['signals_generated'],
                'last_execution': self._market_stats[market_type]['last_execution'],
                'data_cache_size': len(self._market_data_cache.get(market_type, []))
            }
        
        base_stats['agnostic_strategies_count'] = len(self._agnostic_strategies)
        
        return base_stats
    
    def _classify_strategy(self, strategy: BaseStrategy):
        """
        Classify a strategy based on its market support.
        
        Args:
            strategy: Strategy to classify
        """
        strategy_name = strategy.name
        
        if isinstance(strategy, MarketAgnosticStrategy):
            self._agnostic_strategies.add(strategy_name)
            self.logger.debug(f"Classified {strategy_name} as market-agnostic")
            
        elif isinstance(strategy, MarketSpecificStrategy):
            supported_markets = strategy.get_supported_markets()
            for market_type in supported_markets:
                self._market_strategies[market_type].add(strategy_name)
                self._market_stats[market_type]['strategies_count'] += 1
            
            self.logger.debug(f"Classified {strategy_name} as market-specific: {supported_markets}")
            
        else:
            # Legacy strategy - assume crypto support
            self._market_strategies[MarketType.CRYPTO].add(strategy_name)
            self._market_stats[MarketType.CRYPTO]['strategies_count'] += 1
            self.logger.debug(f"Classified {strategy_name} as legacy crypto strategy")
    
    def _remove_strategy_classification(self, strategy_name: str):
        """
        Remove strategy from all market classifications.
        
        Args:
            strategy_name: Name of strategy to remove
        """
        # Remove from agnostic strategies
        self._agnostic_strategies.discard(strategy_name)
        
        # Remove from market-specific strategies
        for market_type, strategies in self._market_strategies.items():
            if strategy_name in strategies:
                strategies.discard(strategy_name)
                self._market_stats[market_type]['strategies_count'] -= 1
    
    def _group_data_by_market(self, market_data: List[UnifiedMarketData]) -> Dict[MarketType, List[UnifiedMarketData]]:
        """
        Group market data by market type.
        
        Args:
            market_data: List of unified market data
            
        Returns:
            Dict[MarketType, List[UnifiedMarketData]]: Data grouped by market type
        """
        groups = {market_type: [] for market_type in MarketType}
        
        for data in market_data:
            groups[data.market_type].append(data)
            
        return groups
    
    def _update_market_data_cache(self, market_data_groups: Dict[MarketType, List[UnifiedMarketData]]):
        """
        Update market data cache with latest data.
        
        Args:
            market_data_groups: Market data grouped by type
        """
        for market_type, data_list in market_data_groups.items():
            if data_list:
                # Keep only recent data (last 1000 points per market)
                self._market_data_cache[market_type].extend(data_list)
                self._market_data_cache[market_type] = self._market_data_cache[market_type][-1000:]
    
    def _process_market_data(self, market_type: MarketType, 
                           market_data: List[UnifiedMarketData]) -> List[TradingSignal]:
        """
        Process market data for a specific market type.
        
        Args:
            market_type: Type of market being processed
            market_data: Market data for the specific market type
            
        Returns:
            List[TradingSignal]: Generated trading signals
        """
        signals = []
        
        # Get strategies that can process this market type
        applicable_strategies = self._get_applicable_strategies(market_type)
        
        if not applicable_strategies:
            return signals
        
        # Process strategies concurrently
        futures = []
        for strategy_name in applicable_strategies:
            if strategy_name not in self._active_strategies:
                continue
                
            strategy = self._strategies[strategy_name]
            
            # Prepare data for strategy
            strategy_data = self._prepare_strategy_data(strategy, market_data)
            
            if strategy_data:
                future = self._executor.submit(strategy.process_market_data, strategy_data)
                futures.append((strategy_name, future))
        
        # Collect results
        for strategy_name, future in futures:
            try:
                signal = future.result(timeout=30)  # 30 second timeout
                if signal:
                    signals.append(signal)
                    
            except Exception as e:
                self.logger.error(f"Error processing {market_type.value} data in strategy {strategy_name}: {str(e)}")
                self._execution_stats['failed_executions'] += 1
        
        return signals
    
    def _get_applicable_strategies(self, market_type: MarketType) -> List[str]:
        """
        Get strategies applicable to a market type.
        
        Args:
            market_type: Market type to get strategies for
            
        Returns:
            List[str]: List of applicable strategy names
        """
        applicable = []
        
        # Add market-specific strategies
        applicable.extend(self._market_strategies.get(market_type, set()))
        
        # Add market-agnostic strategies
        applicable.extend(self._agnostic_strategies)
        
        return applicable
    
    def _prepare_strategy_data(self, strategy: BaseStrategy, 
                             market_data: List[UnifiedMarketData]) -> Optional[List]:
        """
        Prepare market data for strategy processing.
        
        Args:
            strategy: Strategy that will process the data
            market_data: Raw market data
            
        Returns:
            Optional[List]: Prepared data for strategy, or None if incompatible
        """
        if isinstance(strategy, (MarketAgnosticStrategy, MarketSpecificStrategy)):
            # New strategy types can handle UnifiedMarketData directly
            return market_data
        else:
            # Legacy strategies need MarketData format
            legacy_data = []
            for data in market_data:
                try:
                    legacy_data.append(data.to_legacy_market_data())
                except Exception as e:
                    self.logger.warning(f"Failed to convert data for legacy strategy {strategy.name}: {str(e)}")
            return legacy_data if legacy_data else None