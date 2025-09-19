"""
Base strategy abstract class defining the interface for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.data_models import MarketData, TradingSignal


@dataclass
class StrategyConfig:
    """Configuration parameters for a strategy."""
    name: str
    enabled: bool = True
    parameters: Dict[str, Any] = None
    risk_limits: Dict[str, float] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.risk_limits is None:
            self.risk_limits = {}


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All trading strategies must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the strategy with configuration.
        
        Args:
            config: Strategy configuration parameters
        """
        self.config = config
        self.name = config.name
        self.enabled = config.enabled
        self.parameters = config.parameters
        self.risk_limits = config.risk_limits
        
        # Strategy state
        self._initialized = False
        self._running = False
        self._last_signal_time = None
        
        # Logging
        self.logger = logging.getLogger(f"strategy.{self.name}")
        
        # Performance tracking
        self.signals_generated = 0
        self.successful_signals = 0
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the strategy with any required setup.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze market data and generate trading signals.
        
        Args:
            market_data: List of market data points for analysis
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        pass
    
    @abstractmethod
    def get_required_data_length(self) -> int:
        """
        Get the minimum number of data points required for analysis.
        
        Returns:
            int: Minimum number of data points needed
        """
        pass
    
    def validate_parameters(self) -> bool:
        """
        Validate strategy parameters.
        
        Default implementation validates basic parameters.
        Subclasses should override this method to add specific validation.
        
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        try:
            # Basic validation - check if name is set
            if not self.name:
                self.logger.error("Strategy name cannot be empty")
                return False
            
            # Check if parameters is a dictionary
            if self.parameters is not None and not isinstance(self.parameters, dict):
                self.logger.error("Parameters must be a dictionary")
                return False
            
            # Check if risk_limits is a dictionary
            if self.risk_limits is not None and not isinstance(self.risk_limits, dict):
                self.logger.error("Risk limits must be a dictionary")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def start(self) -> bool:
        """
        Start the strategy execution.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if not self.enabled:
            self.logger.warning(f"Strategy {self.name} is disabled")
            return False
            
        if not self._initialized:
            if not self.initialize():
                self.logger.error(f"Failed to initialize strategy {self.name}")
                return False
            self._initialized = True
            
        if not self.validate_parameters():
            self.logger.error(f"Invalid parameters for strategy {self.name}")
            return False
            
        self._running = True
        self.logger.info(f"Strategy {self.name} started successfully")
        return True
    
    def stop(self) -> bool:
        """
        Stop the strategy execution.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        self._running = False
        self.logger.info(f"Strategy {self.name} stopped")
        return True
    
    def is_running(self) -> bool:
        """
        Check if the strategy is currently running.
        
        Returns:
            bool: True if running, False otherwise
        """
        return self._running and self.enabled
    
    def process_market_data(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Process market data and generate signals if strategy is running.
        
        Args:
            market_data: List of market data points
            
        Returns:
            Optional[TradingSignal]: Trading signal if generated, None otherwise
        """
        if not self.is_running():
            return None
            
        if len(market_data) < self.get_required_data_length():
            self.logger.debug(f"Insufficient data for {self.name}: "
                            f"need {self.get_required_data_length()}, got {len(market_data)}")
            return None
            
        try:
            signal = self.analyze(market_data)
            if signal:
                self.signals_generated += 1
                self._last_signal_time = datetime.now()
                self.logger.info(f"Signal generated by {self.name}: {signal.action} {signal.symbol}")
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in strategy {self.name}: {str(e)}")
            return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get strategy performance metrics.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        success_rate = 0.0
        if self.signals_generated > 0:
            success_rate = self.successful_signals / self.signals_generated
            
        return {
            'name': self.name,
            'enabled': self.enabled,
            'running': self._running,
            'signals_generated': self.signals_generated,
            'successful_signals': self.successful_signals,
            'success_rate': success_rate,
            'last_signal_time': self._last_signal_time
        }
    
    def update_signal_success(self, successful: bool):
        """
        Update signal success tracking.
        
        Args:
            successful: Whether the signal was successful
        """
        if successful:
            self.successful_signals += 1
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"Strategy({self.name}, enabled={self.enabled}, running={self._running})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the strategy."""
        return (f"BaseStrategy(name='{self.name}', enabled={self.enabled}, "
                f"running={self._running}, signals={self.signals_generated})")