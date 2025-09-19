"""GeneBot Trading Strategies Package."""

from .strategy_engine import StrategyEngine
from .strategy_registry import StrategyRegistry
from .signal_processor import SignalProcessor
from .strategy_config import StrategyConfigManager
from .base_strategy import BaseStrategy
from .moving_average_strategy import MovingAverageStrategy
from .rsi_strategy import RSIStrategy
from .multi_indicator_strategy import MultiIndicatorStrategy
from .advanced_momentum_strategy import AdvancedMomentumStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .atr_volatility_strategy import ATRVolatilityStrategy

# Optional ML strategy
try:
    from .ml_pattern_strategy import MLPatternStrategy
except ImportError:
    MLPatternStrategy = None

__all__ = [
    'StrategyEngine',
    'StrategyRegistry', 
    'SignalProcessor',
    'StrategyConfigManager',
    'BaseStrategy',
    'MovingAverageStrategy',
    'RSIStrategy',
    'MultiIndicatorStrategy',
    'AdvancedMomentumStrategy',
    'MeanReversionStrategy',
    'ATRVolatilityStrategy',
    'MLPatternStrategy'
]