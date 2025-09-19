"""
Strategy configuration and parameter management.
"""

import logging
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import json

from .base_strategy import BaseStrategy, StrategyConfig


@dataclass
class StrategyTemplate:
    """Template for creating strategy configurations."""
    
    name: str
    strategy_type: str
    description: str
    default_parameters: Dict[str, Any] = field(default_factory=dict)
    parameter_descriptions: Dict[str, str] = field(default_factory=dict)
    parameter_ranges: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    risk_limits: Dict[str, float] = field(default_factory=dict)


class StrategyConfigManager:
    """
    Manager for strategy configurations and parameter validation.
    
    This class provides functionality to:
    - Load and save strategy configurations
    - Validate strategy parameters
    - Create strategy configurations from templates
    - Manage strategy parameter presets
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the strategy configuration manager.
        
        Args:
            config_dir: Directory to store configuration files (default: config/strategies)
        """
        self.config_dir = Path(config_dir or "config/strategies")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("strategy_config_manager")
        
        # Built-in strategy templates
        self._templates = self._create_builtin_templates()
        
        # Loaded configurations
        self._configurations: Dict[str, StrategyConfig] = {}
    
    def _create_builtin_templates(self) -> Dict[str, StrategyTemplate]:
        """Create built-in strategy templates."""
        templates = {}
        
        # Moving Average Strategy Template
        templates['MovingAverageStrategy'] = StrategyTemplate(
            name='MovingAverageStrategy',
            strategy_type='MovingAverageStrategy',
            description='Simple Moving Average Crossover Strategy',
            default_parameters={
                'short_window': 10,
                'long_window': 30,
                'min_confidence': 0.7
            },
            parameter_descriptions={
                'short_window': 'Short-term moving average period',
                'long_window': 'Long-term moving average period',
                'min_confidence': 'Minimum confidence threshold for signals'
            },
            parameter_ranges={
                'short_window': {'min': 2, 'max': 50, 'type': 'int'},
                'long_window': {'min': 10, 'max': 200, 'type': 'int'},
                'min_confidence': {'min': 0.0, 'max': 1.0, 'type': 'float'}
            },
            risk_limits={
                'max_position_size': 0.1,  # 10% of portfolio
                'max_daily_trades': 5
            }
        )
        
        # RSI Strategy Template
        templates['RSIStrategy'] = StrategyTemplate(
            name='RSIStrategy',
            strategy_type='RSIStrategy',
            description='Relative Strength Index Strategy',
            default_parameters={
                'rsi_period': 14,
                'oversold_threshold': 30,
                'overbought_threshold': 70,
                'min_confidence': 0.7
            },
            parameter_descriptions={
                'rsi_period': 'RSI calculation period',
                'oversold_threshold': 'RSI oversold level (buy signal)',
                'overbought_threshold': 'RSI overbought level (sell signal)',
                'min_confidence': 'Minimum confidence threshold for signals'
            },
            parameter_ranges={
                'rsi_period': {'min': 2, 'max': 50, 'type': 'int'},
                'oversold_threshold': {'min': 10, 'max': 40, 'type': 'float'},
                'overbought_threshold': {'min': 60, 'max': 90, 'type': 'float'},
                'min_confidence': {'min': 0.0, 'max': 1.0, 'type': 'float'}
            },
            risk_limits={
                'max_position_size': 0.15,  # 15% of portfolio
                'max_daily_trades': 8
            }
        )
        
        # Multi-Indicator Strategy Template
        templates['MultiIndicatorStrategy'] = StrategyTemplate(
            name='MultiIndicatorStrategy',
            strategy_type='MultiIndicatorStrategy',
            description='Advanced Multi-Indicator Confluence Strategy for High-Probability Signals',
            default_parameters={
                'ma_fast': 8,
                'ma_slow': 21,
                'rsi_period': 14,
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'bb_period': 20,
                'bb_std': 2.0,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'volume_threshold': 1.2,
                'min_confluence': 4,
                'min_confidence': 0.85
            },
            parameter_descriptions={
                'ma_fast': 'Fast moving average period',
                'ma_slow': 'Slow moving average period',
                'rsi_period': 'RSI calculation period',
                'rsi_oversold': 'RSI oversold threshold',
                'rsi_overbought': 'RSI overbought threshold',
                'bb_period': 'Bollinger Bands period',
                'bb_std': 'Bollinger Bands standard deviation',
                'macd_fast': 'MACD fast EMA period',
                'macd_slow': 'MACD slow EMA period',
                'macd_signal': 'MACD signal line period',
                'volume_threshold': 'Volume confirmation multiplier',
                'min_confluence': 'Minimum number of confirming indicators',
                'min_confidence': 'Minimum confidence threshold'
            },
            parameter_ranges={
                'ma_fast': {'min': 3, 'max': 20, 'type': 'int'},
                'ma_slow': {'min': 10, 'max': 50, 'type': 'int'},
                'rsi_period': {'min': 5, 'max': 30, 'type': 'int'},
                'rsi_oversold': {'min': 20, 'max': 40, 'type': 'float'},
                'rsi_overbought': {'min': 60, 'max': 80, 'type': 'float'},
                'bb_period': {'min': 10, 'max': 30, 'type': 'int'},
                'bb_std': {'min': 1.5, 'max': 3.0, 'type': 'float'},
                'volume_threshold': {'min': 1.0, 'max': 3.0, 'type': 'float'},
                'min_confluence': {'min': 2, 'max': 8, 'type': 'int'},
                'min_confidence': {'min': 0.7, 'max': 1.0, 'type': 'float'}
            },
            risk_limits={
                'max_position_size': 0.08,  # 8% of portfolio (more conservative)
                'max_daily_trades': 3
            }
        )
        
        # ML Pattern Strategy Template
        templates['MLPatternStrategy'] = StrategyTemplate(
            name='MLPatternStrategy',
            strategy_type='MLPatternStrategy',
            description='Machine Learning Pattern Recognition Strategy',
            default_parameters={
                'lookback_period': 100,
                'feature_window': 20,
                'prediction_threshold': 0.75,
                'retrain_frequency': 50,
                'min_confidence': 0.90,
                'use_ensemble': True
            },
            parameter_descriptions={
                'lookback_period': 'Historical data lookback period',
                'feature_window': 'Feature calculation window',
                'prediction_threshold': 'ML prediction confidence threshold',
                'retrain_frequency': 'Model retraining frequency (signals)',
                'min_confidence': 'Minimum signal confidence',
                'use_ensemble': 'Use ensemble of ML models'
            },
            parameter_ranges={
                'lookback_period': {'min': 50, 'max': 500, 'type': 'int'},
                'feature_window': {'min': 10, 'max': 50, 'type': 'int'},
                'prediction_threshold': {'min': 0.6, 'max': 0.95, 'type': 'float'},
                'retrain_frequency': {'min': 20, 'max': 200, 'type': 'int'},
                'min_confidence': {'min': 0.8, 'max': 1.0, 'type': 'float'}
            },
            risk_limits={
                'max_position_size': 0.06,  # 6% of portfolio (very conservative)
                'max_daily_trades': 2
            }
        )
        
        # Advanced Momentum Strategy Template
        templates['AdvancedMomentumStrategy'] = StrategyTemplate(
            name='AdvancedMomentumStrategy',
            strategy_type='AdvancedMomentumStrategy',
            description='Advanced Multi-Timeframe Momentum Strategy',
            default_parameters={
                'momentum_periods': [5, 10, 20],
                'roc_periods': [3, 7, 14],
                'rsi_period': 14,
                'stoch_k_period': 14,
                'stoch_d_period': 3,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'volume_ma_period': 20,
                'momentum_threshold': 2.0,
                'divergence_lookback': 10,
                'min_confidence': 0.88
            },
            parameter_descriptions={
                'momentum_periods': 'List of momentum calculation periods',
                'roc_periods': 'List of rate of change periods',
                'rsi_period': 'RSI calculation period',
                'stoch_k_period': 'Stochastic %K period',
                'stoch_d_period': 'Stochastic %D period',
                'macd_fast': 'MACD fast period',
                'macd_slow': 'MACD slow period',
                'macd_signal': 'MACD signal period',
                'volume_ma_period': 'Volume moving average period',
                'momentum_threshold': 'Minimum momentum threshold (%)',
                'divergence_lookback': 'Divergence detection lookback',
                'min_confidence': 'Minimum confidence threshold'
            },
            parameter_ranges={
                'momentum_threshold': {'min': 1.0, 'max': 5.0, 'type': 'float'},
                'divergence_lookback': {'min': 5, 'max': 20, 'type': 'int'},
                'min_confidence': {'min': 0.8, 'max': 1.0, 'type': 'float'}
            },
            risk_limits={
                'max_position_size': 0.12,  # 12% of portfolio
                'max_daily_trades': 4
            }
        )
        
        # Mean Reversion Strategy Template
        templates['MeanReversionStrategy'] = StrategyTemplate(
            name='MeanReversionStrategy',
            strategy_type='MeanReversionStrategy',
            description='Advanced Mean Reversion Strategy for High-Probability Reversals',
            default_parameters={
                'bb_period': 20,
                'bb_std_dev': 2.5,
                'rsi_period': 14,
                'rsi_extreme_oversold': 20,
                'rsi_extreme_overbought': 80,
                'stoch_period': 14,
                'deviation_threshold': 2.0,
                'volume_confirmation': 1.5,
                'mean_periods': [10, 20, 50],
                'min_confluence': 4,
                'min_confidence': 0.87
            },
            parameter_descriptions={
                'bb_period': 'Bollinger Bands period',
                'bb_std_dev': 'Bollinger Bands standard deviation',
                'rsi_period': 'RSI calculation period',
                'rsi_extreme_oversold': 'Extreme oversold RSI level',
                'rsi_extreme_overbought': 'Extreme overbought RSI level',
                'stoch_period': 'Stochastic oscillator period',
                'deviation_threshold': 'Price deviation threshold (%)',
                'volume_confirmation': 'Volume confirmation multiplier',
                'mean_periods': 'Mean calculation periods',
                'min_confluence': 'Minimum confluence signals',
                'min_confidence': 'Minimum confidence threshold'
            },
            parameter_ranges={
                'bb_period': {'min': 15, 'max': 30, 'type': 'int'},
                'bb_std_dev': {'min': 2.0, 'max': 3.0, 'type': 'float'},
                'rsi_extreme_oversold': {'min': 10, 'max': 25, 'type': 'float'},
                'rsi_extreme_overbought': {'min': 75, 'max': 90, 'type': 'float'},
                'deviation_threshold': {'min': 1.5, 'max': 3.0, 'type': 'float'},
                'volume_confirmation': {'min': 1.2, 'max': 2.5, 'type': 'float'},
                'min_confluence': {'min': 3, 'max': 7, 'type': 'int'},
                'min_confidence': {'min': 0.8, 'max': 1.0, 'type': 'float'}
            },
            risk_limits={
                'max_position_size': 0.10,  # 10% of portfolio
                'max_daily_trades': 3
            }
        )
        
        # ATR Volatility Strategy Template
        templates['ATRVolatilityStrategy'] = StrategyTemplate(
            name='ATRVolatilityStrategy',
            strategy_type='ATRVolatilityStrategy',
            description='Advanced ATR Volatility Strategy for High-Probability Volatility-Based Signals',
            default_parameters={
                'atr_period': 14,
                'atr_multiplier': 2.0,
                'volatility_threshold': 1.5,
                'squeeze_threshold': 0.5,
                'expansion_threshold': 2.0,
                'volume_correlation': 0.7,
                'trend_filter': True,
                'min_confidence': 0.86,
                'lookback_period': 50
            },
            parameter_descriptions={
                'atr_period': 'ATR calculation period',
                'atr_multiplier': 'ATR multiplier for breakout detection',
                'volatility_threshold': 'Volatility change threshold',
                'squeeze_threshold': 'Volatility squeeze threshold',
                'expansion_threshold': 'Volatility expansion threshold',
                'volume_correlation': 'Volume-volatility correlation threshold',
                'trend_filter': 'Use trend filter for signals',
                'min_confidence': 'Minimum confidence threshold',
                'lookback_period': 'Lookback period for volatility analysis'
            },
            parameter_ranges={
                'atr_period': {'min': 7, 'max': 30, 'type': 'int'},
                'atr_multiplier': {'min': 1.0, 'max': 4.0, 'type': 'float'},
                'volatility_threshold': {'min': 1.0, 'max': 3.0, 'type': 'float'},
                'squeeze_threshold': {'min': 0.2, 'max': 0.8, 'type': 'float'},
                'expansion_threshold': {'min': 1.5, 'max': 3.0, 'type': 'float'},
                'volume_correlation': {'min': 0.5, 'max': 0.9, 'type': 'float'},
                'lookback_period': {'min': 30, 'max': 100, 'type': 'int'},
                'min_confidence': {'min': 0.8, 'max': 1.0, 'type': 'float'}
            },
            risk_limits={
                'max_position_size': 0.12,  # 12% of portfolio
                'max_daily_trades': 4
            }
        )
        
        return templates
    
    def get_template(self, strategy_type: str) -> Optional[StrategyTemplate]:
        """
        Get strategy template by type.
        
        Args:
            strategy_type: Type of strategy
            
        Returns:
            Optional[StrategyTemplate]: Strategy template or None if not found
        """
        return self._templates.get(strategy_type)
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available strategy templates.
        
        Returns:
            List[str]: List of available strategy types
        """
        return list(self._templates.keys())
    
    def create_config_from_template(self, strategy_type: str, name: str, 
                                  custom_parameters: Optional[Dict[str, Any]] = None,
                                  enabled: bool = True) -> Optional[StrategyConfig]:
        """
        Create strategy configuration from template.
        
        Args:
            strategy_type: Type of strategy
            name: Name for the strategy instance
            custom_parameters: Custom parameters to override defaults
            enabled: Whether the strategy is enabled
            
        Returns:
            Optional[StrategyConfig]: Created configuration or None if template not found
        """
        template = self.get_template(strategy_type)
        if not template:
            self.logger.error(f"Template not found for strategy type: {strategy_type}")
            return None
        
        # Start with default parameters
        parameters = template.default_parameters.copy()
        
        # Override with custom parameters
        if custom_parameters:
            parameters.update(custom_parameters)
        
        # Validate parameters
        if not self._validate_parameters(strategy_type, parameters):
            self.logger.error(f"Invalid parameters for strategy {name}")
            return None
        
        config = StrategyConfig(
            name=name,
            enabled=enabled,
            parameters=parameters,
            risk_limits=template.risk_limits.copy()
        )
        
        self._configurations[name] = config
        self.logger.info(f"Created configuration for strategy: {name}")
        return config
    
    def save_config(self, config: StrategyConfig, filename: Optional[str] = None) -> bool:
        """
        Save strategy configuration to file.
        
        Args:
            config: Strategy configuration to save
            filename: Optional filename (defaults to config name)
            
        Returns:
            bool: True if saved successfully
        """
        try:
            filename = filename or f"{config.name}.yaml"
            filepath = self.config_dir / filename
            
            config_dict = {
                'name': config.name,
                'enabled': config.enabled,
                'parameters': config.parameters,
                'risk_limits': config.risk_limits
            }
            
            with open(filepath, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved configuration to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def load_config(self, filename: str) -> Optional[StrategyConfig]:
        """
        Load strategy configuration from file.
        
        Args:
            filename: Configuration filename
            
        Returns:
            Optional[StrategyConfig]: Loaded configuration or None if failed
        """
        try:
            filepath = self.config_dir / filename
            
            if not filepath.exists():
                self.logger.error(f"Configuration file not found: {filepath}")
                return None
            
            with open(filepath, 'r') as f:
                config_dict = yaml.safe_load(f)
            
            config = StrategyConfig(
                name=config_dict['name'],
                enabled=config_dict.get('enabled', True),
                parameters=config_dict.get('parameters', {}),
                risk_limits=config_dict.get('risk_limits', {})
            )
            
            self._configurations[config.name] = config
            self.logger.info(f"Loaded configuration from: {filepath}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return None
    
    def load_configs_from_directory(self) -> List[StrategyConfig]:
        """
        Load all strategy configurations from the config directory.
        
        Returns:
            List[StrategyConfig]: List of loaded configurations
        """
        configs = []
        
        for filepath in self.config_dir.glob("*.yaml"):
            config = self.load_config(filepath.name)
            if config:
                configs.append(config)
        
        self.logger.info(f"Loaded {len(configs)} configurations from directory")
        return configs
    
    def validate_config(self, config: StrategyConfig, strategy_type: str) -> bool:
        """
        Validate strategy configuration against template.
        
        Args:
            config: Configuration to validate
            strategy_type: Type of strategy
            
        Returns:
            bool: True if configuration is valid
        """
        return self._validate_parameters(strategy_type, config.parameters)
    
    def _validate_parameters(self, strategy_type: str, parameters: Dict[str, Any]) -> bool:
        """
        Validate strategy parameters against template ranges.
        
        Args:
            strategy_type: Type of strategy
            parameters: Parameters to validate
            
        Returns:
            bool: True if parameters are valid
        """
        template = self.get_template(strategy_type)
        if not template:
            self.logger.error(f"No template found for strategy type: {strategy_type}")
            return False
        
        try:
            for param_name, param_value in parameters.items():
                if param_name in template.parameter_ranges:
                    param_range = template.parameter_ranges[param_name]
                    
                    # Check type
                    expected_type = param_range.get('type', 'float')
                    if expected_type == 'int' and not isinstance(param_value, int):
                        self.logger.error(f"Parameter {param_name} must be an integer")
                        return False
                    elif expected_type == 'float' and not isinstance(param_value, (int, float)):
                        self.logger.error(f"Parameter {param_name} must be a number")
                        return False
                    
                    # Check range
                    if 'min' in param_range and param_value < param_range['min']:
                        self.logger.error(f"Parameter {param_name} below minimum: {param_range['min']}")
                        return False
                    if 'max' in param_range and param_value > param_range['max']:
                        self.logger.error(f"Parameter {param_name} above maximum: {param_range['max']}")
                        return False
            
            # Check for required parameters
            for param_name in template.default_parameters:
                if param_name not in parameters:
                    self.logger.warning(f"Missing parameter {param_name}, using default")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def get_parameter_info(self, strategy_type: str) -> Optional[Dict[str, Any]]:
        """
        Get parameter information for a strategy type.
        
        Args:
            strategy_type: Type of strategy
            
        Returns:
            Optional[Dict[str, Any]]: Parameter information or None if not found
        """
        template = self.get_template(strategy_type)
        if not template:
            return None
        
        return {
            'description': template.description,
            'parameters': {
                param_name: {
                    'default': template.default_parameters.get(param_name),
                    'description': template.parameter_descriptions.get(param_name, ''),
                    'range': template.parameter_ranges.get(param_name, {})
                }
                for param_name in template.default_parameters
            },
            'risk_limits': template.risk_limits
        }
    
    def create_preset_configs(self) -> Dict[str, StrategyConfig]:
        """
        Create preset configurations for common strategy setups.
        
        Returns:
            Dict[str, StrategyConfig]: Dictionary of preset configurations
        """
        presets = {}
        
        # Basic Strategies
        # Conservative Moving Average
        presets['ma_conservative'] = self.create_config_from_template(
            'MovingAverageStrategy',
            'ma_conservative',
            {
                'short_window': 20,
                'long_window': 50,
                'min_confidence': 0.8
            }
        )
        
        # Aggressive Moving Average
        presets['ma_aggressive'] = self.create_config_from_template(
            'MovingAverageStrategy',
            'ma_aggressive',
            {
                'short_window': 5,
                'long_window': 15,
                'min_confidence': 0.6
            }
        )
        
        # Conservative RSI
        presets['rsi_conservative'] = self.create_config_from_template(
            'RSIStrategy',
            'rsi_conservative',
            {
                'rsi_period': 21,
                'oversold_threshold': 25,
                'overbought_threshold': 75,
                'min_confidence': 0.8
            }
        )
        
        # Aggressive RSI
        presets['rsi_aggressive'] = self.create_config_from_template(
            'RSIStrategy',
            'rsi_aggressive',
            {
                'rsi_period': 7,
                'oversold_threshold': 35,
                'overbought_threshold': 65,
                'min_confidence': 0.6
            }
        )
        
        # Advanced Strategies
        # High-Probability Multi-Indicator
        presets['multi_indicator_high_prob'] = self.create_config_from_template(
            'MultiIndicatorStrategy',
            'multi_indicator_high_prob',
            {
                'ma_fast': 8,
                'ma_slow': 21,
                'min_confluence': 5,
                'min_confidence': 0.90,
                'volume_threshold': 1.5
            }
        )
        
        # Balanced Multi-Indicator
        presets['multi_indicator_balanced'] = self.create_config_from_template(
            'MultiIndicatorStrategy',
            'multi_indicator_balanced',
            {
                'ma_fast': 10,
                'ma_slow': 25,
                'min_confluence': 4,
                'min_confidence': 0.85,
                'volume_threshold': 1.2
            }
        )
        
        # ML Pattern Recognition (Conservative)
        presets['ml_pattern_conservative'] = self.create_config_from_template(
            'MLPatternStrategy',
            'ml_pattern_conservative',
            {
                'lookback_period': 150,
                'prediction_threshold': 0.80,
                'min_confidence': 0.92,
                'retrain_frequency': 30
            }
        )
        
        # ML Pattern Recognition (Adaptive)
        presets['ml_pattern_adaptive'] = self.create_config_from_template(
            'MLPatternStrategy',
            'ml_pattern_adaptive',
            {
                'lookback_period': 100,
                'prediction_threshold': 0.75,
                'min_confidence': 0.88,
                'retrain_frequency': 50
            }
        )
        
        # Advanced Momentum (Trend Following)
        presets['momentum_trend_following'] = self.create_config_from_template(
            'AdvancedMomentumStrategy',
            'momentum_trend_following',
            {
                'momentum_periods': [5, 10, 20],
                'momentum_threshold': 2.5,
                'min_confidence': 0.90,
                'divergence_lookback': 15
            }
        )
        
        # Advanced Momentum (Scalping)
        presets['momentum_scalping'] = self.create_config_from_template(
            'AdvancedMomentumStrategy',
            'momentum_scalping',
            {
                'momentum_periods': [3, 5, 10],
                'momentum_threshold': 1.5,
                'min_confidence': 0.85,
                'divergence_lookback': 8
            }
        )
        
        # Mean Reversion (Extreme)
        presets['mean_reversion_extreme'] = self.create_config_from_template(
            'MeanReversionStrategy',
            'mean_reversion_extreme',
            {
                'bb_std_dev': 2.8,
                'rsi_extreme_oversold': 15,
                'rsi_extreme_overbought': 85,
                'deviation_threshold': 2.5,
                'min_confluence': 5,
                'min_confidence': 0.90
            }
        )
        
        # Mean Reversion (Moderate)
        presets['mean_reversion_moderate'] = self.create_config_from_template(
            'MeanReversionStrategy',
            'mean_reversion_moderate',
            {
                'bb_std_dev': 2.2,
                'rsi_extreme_oversold': 25,
                'rsi_extreme_overbought': 75,
                'deviation_threshold': 1.8,
                'min_confluence': 4,
                'min_confidence': 0.85
            }
        )
        
        # ATR Volatility (Breakout)
        presets['atr_volatility_breakout'] = self.create_config_from_template(
            'ATRVolatilityStrategy',
            'atr_volatility_breakout',
            {
                'atr_multiplier': 2.5,
                'volatility_threshold': 2.0,
                'expansion_threshold': 2.5,
                'min_confidence': 0.90,
                'trend_filter': True
            }
        )
        
        # ATR Volatility (Squeeze)
        presets['atr_volatility_squeeze'] = self.create_config_from_template(
            'ATRVolatilityStrategy',
            'atr_volatility_squeeze',
            {
                'atr_multiplier': 1.8,
                'squeeze_threshold': 0.4,
                'expansion_threshold': 1.8,
                'min_confidence': 0.88,
                'volume_correlation': 0.8
            }
        )
        
        # ATR Volatility (Conservative)
        presets['atr_volatility_conservative'] = self.create_config_from_template(
            'ATRVolatilityStrategy',
            'atr_volatility_conservative',
            {
                'atr_multiplier': 3.0,
                'volatility_threshold': 2.5,
                'min_confidence': 0.92,
                'trend_filter': True,
                'lookback_period': 60
            }
        )
        
        # High-Probability Portfolio (Multiple Strategies)
        presets['high_prob_portfolio'] = {
            'multi_indicator': presets.get('multi_indicator_high_prob'),
            'ml_pattern': presets.get('ml_pattern_conservative'),
            'mean_reversion': presets.get('mean_reversion_extreme'),
            'atr_volatility': presets.get('atr_volatility_conservative')
        }
        
        # Filter out None values
        presets = {k: v for k, v in presets.items() if v is not None and k != 'high_prob_portfolio'}
        
        # Add portfolio as a special case
        if all(presets.get(f'{strategy}_high_prob') or presets.get(f'{strategy}_conservative') or presets.get(f'{strategy}_extreme') 
               for strategy in ['multi_indicator', 'ml_pattern', 'mean_reversion']):
            presets['high_prob_portfolio'] = 'portfolio_config'  # Special marker
        
        self.logger.info(f"Created {len(presets)} preset configurations")
        return presets
    
    def export_config_to_json(self, config: StrategyConfig) -> str:
        """
        Export configuration to JSON string.
        
        Args:
            config: Configuration to export
            
        Returns:
            str: JSON representation of the configuration
        """
        config_dict = {
            'name': config.name,
            'enabled': config.enabled,
            'parameters': config.parameters,
            'risk_limits': config.risk_limits
        }
        return json.dumps(config_dict, indent=2)
    
    def import_config_from_json(self, json_str: str) -> Optional[StrategyConfig]:
        """
        Import configuration from JSON string.
        
        Args:
            json_str: JSON string containing configuration
            
        Returns:
            Optional[StrategyConfig]: Imported configuration or None if failed
        """
        try:
            config_dict = json.loads(json_str)
            
            config = StrategyConfig(
                name=config_dict['name'],
                enabled=config_dict.get('enabled', True),
                parameters=config_dict.get('parameters', {}),
                risk_limits=config_dict.get('risk_limits', {})
            )
            
            self._configurations[config.name] = config
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration from JSON: {str(e)}")
            return None