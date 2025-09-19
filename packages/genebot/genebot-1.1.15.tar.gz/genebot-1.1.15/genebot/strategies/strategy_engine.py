"""
Strategy engine for managing strategy lifecycle and execution.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading

from .base_strategy import BaseStrategy
from .strategy_registry import StrategyRegistry
from .signal_processor import SignalProcessor
from ..models.data_models import MarketData, TradingSignal


class StrategyEngine:
    """
    Manages the lifecycle and execution of trading strategies.
    
    The StrategyEngine coordinates multiple strategies, manages their execution,
    and processes the signals they generate.
    """
    
    def __init__(self, 
                 strategy_registry: StrategyRegistry,
                 signal_processor: SignalProcessor,
                 max_workers: int = 4):
        """
        Initialize the strategy engine.
        
        Args:
            strategy_registry: Registry for managing strategies
            signal_processor: Processor for handling trading signals
            max_workers: Maximum number of worker threads for strategy execution
        """
        self.strategy_registry = strategy_registry
        self.signal_processor = signal_processor
        self.max_workers = max_workers
        
        # Engine state
        self._running = False
        self._strategies: Dict[str, BaseStrategy] = {}
        self._active_strategies: Set[str] = set()
        
        # Threading
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.RLock()
        
        # Performance tracking
        self._execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'last_execution_time': None
        }
        
        # Logging
        self.logger = logging.getLogger("strategy_engine")
        
    def add_strategy(self, strategy: BaseStrategy) -> bool:
        """
        Add a strategy to the engine.
        
        Args:
            strategy: Strategy instance to add
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        with self._lock:
            if strategy.name in self._strategies:
                self.logger.warning(f"Strategy {strategy.name} already exists")
                return False
                
            self._strategies[strategy.name] = strategy
            self.logger.info(f"Added strategy: {strategy.name}")
            return True
    
    def remove_strategy(self, strategy_name: str) -> bool:
        """
        Remove a strategy from the engine.
        
        Args:
            strategy_name: Name of the strategy to remove
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        with self._lock:
            if strategy_name not in self._strategies:
                self.logger.warning(f"Strategy {strategy_name} not found")
                return False
                
            # Stop strategy if running
            if strategy_name in self._active_strategies:
                self.stop_strategy(strategy_name)
                
            del self._strategies[strategy_name]
            self.logger.info(f"Removed strategy: {strategy_name}")
            return True
    
    def start_strategy(self, strategy_name: str) -> bool:
        """
        Start a specific strategy.
        
        Args:
            strategy_name: Name of the strategy to start
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        with self._lock:
            if strategy_name not in self._strategies:
                self.logger.error(f"Strategy {strategy_name} not found")
                return False
                
            strategy = self._strategies[strategy_name]
            if strategy.start():
                self._active_strategies.add(strategy_name)
                self.logger.info(f"Started strategy: {strategy_name}")
                return True
            else:
                self.logger.error(f"Failed to start strategy: {strategy_name}")
                return False
    
    def stop_strategy(self, strategy_name: str) -> bool:
        """
        Stop a specific strategy.
        
        Args:
            strategy_name: Name of the strategy to stop
            
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        with self._lock:
            if strategy_name not in self._strategies:
                self.logger.error(f"Strategy {strategy_name} not found")
                return False
                
            strategy = self._strategies[strategy_name]
            if strategy.stop():
                self._active_strategies.discard(strategy_name)
                self.logger.info(f"Stopped strategy: {strategy_name}")
                return True
            else:
                self.logger.error(f"Failed to stop strategy: {strategy_name}")
                return False
    
    def start_all_strategies(self) -> int:
        """
        Start all registered strategies.
        
        Returns:
            int: Number of strategies started successfully
        """
        started_count = 0
        with self._lock:
            for strategy_name in self._strategies:
                if self.start_strategy(strategy_name):
                    started_count += 1
                    
        self.logger.info(f"Started {started_count} strategies")
        return started_count
    
    def stop_all_strategies(self) -> int:
        """
        Stop all active strategies.
        
        Returns:
            int: Number of strategies stopped successfully
        """
        stopped_count = 0
        with self._lock:
            # Create a copy to avoid modification during iteration
            active_strategies = list(self._active_strategies)
            for strategy_name in active_strategies:
                if self.stop_strategy(strategy_name):
                    stopped_count += 1
                    
        self.logger.info(f"Stopped {stopped_count} strategies")
        return stopped_count
    
    def start_engine(self) -> bool:
        """
        Start the strategy engine.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self._running:
            self.logger.warning("Strategy engine is already running")
            return False
            
        self._running = True
        self.logger.info("Strategy engine started")
        return True
    
    def stop_engine(self) -> bool:
        """
        Stop the strategy engine and all strategies.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if not self._running:
            self.logger.warning("Strategy engine is not running")
            return False
            
        # Stop all strategies
        self.stop_all_strategies()
        
        # Shutdown executor
        self._executor.shutdown(wait=True)
        
        self._running = False
        self.logger.info("Strategy engine stopped")
        return True
    
    def process_market_data(self, market_data: List[MarketData]) -> List[TradingSignal]:
        """
        Process market data through all active strategies.
        
        Args:
            market_data: List of market data points
            
        Returns:
            List[TradingSignal]: List of generated trading signals
        """
        if not self._running:
            return []
            
        start_time = datetime.now()
        signals = []
        
        try:
            with self._lock:
                active_strategies = list(self._active_strategies)
            
            # Process strategies concurrently
            futures = []
            for strategy_name in active_strategies:
                strategy = self._strategies[strategy_name]
                future = self._executor.submit(strategy.process_market_data, market_data)
                futures.append((strategy_name, future))
            
            # Collect results
            for strategy_name, future in futures:
                try:
                    signal = future.result(timeout=30)  # 30 second timeout
                    if signal:
                        signals.append(signal)
                        
                except Exception as e:
                    self.logger.error(f"Error processing data in strategy {strategy_name}: {str(e)}")
                    self._execution_stats['failed_executions'] += 1
            
            # Process signals
            if signals:
                processed_signals = self.signal_processor.process_signals(signals)
                self.logger.debug(f"Generated {len(signals)} signals, processed {len(processed_signals)}")
                signals = processed_signals
            
            # Update statistics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(execution_time, len(signals) > 0)
            
        except Exception as e:
            self.logger.error(f"Error in strategy engine execution: {str(e)}")
            self._execution_stats['failed_executions'] += 1
            
        return signals
    
    def get_strategy_status(self) -> Dict[str, Dict]:
        """
        Get status of all strategies.
        
        Returns:
            Dict[str, Dict]: Status information for each strategy
        """
        status = {}
        with self._lock:
            for name, strategy in self._strategies.items():
                status[name] = {
                    'active': name in self._active_strategies,
                    'performance': strategy.get_performance_metrics(),
                    'config': {
                        'enabled': strategy.enabled,
                        'parameters': strategy.parameters,
                        'risk_limits': strategy.risk_limits
                    }
                }
        return status
    
    def get_engine_stats(self) -> Dict:
        """
        Get engine performance statistics.
        
        Returns:
            Dict: Engine performance statistics
        """
        with self._lock:
            return {
                'running': self._running,
                'total_strategies': len(self._strategies),
                'active_strategies': len(self._active_strategies),
                'execution_stats': self._execution_stats.copy()
            }
    
    def _update_execution_stats(self, execution_time: float, successful: bool):
        """
        Update execution statistics.
        
        Args:
            execution_time: Time taken for execution in seconds
            successful: Whether the execution was successful
        """
        self._execution_stats['total_executions'] += 1
        self._execution_stats['last_execution_time'] = datetime.now()
        
        if successful:
            self._execution_stats['successful_executions'] += 1
        
        # Update average execution time
        total = self._execution_stats['total_executions']
        current_avg = self._execution_stats['average_execution_time']
        self._execution_stats['average_execution_time'] = (
            (current_avg * (total - 1) + execution_time) / total
        )
    
    def __enter__(self):
        """Context manager entry."""
        self.start_engine()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_engine()