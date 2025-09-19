"""
Strategy registry for dynamic strategy loading and registration.
"""

import importlib
import inspect
import logging
from typing import Dict, List, Type, Optional, Any
from pathlib import Path
import pkgutil

from .base_strategy import BaseStrategy, StrategyConfig


class StrategyRegistry:
    """
    Registry for managing and dynamically loading trading strategies.
    
    The StrategyRegistry provides functionality to:
    - Register strategy classes
    - Create strategy instances from configuration
    - Discover and load strategies from modules
    - Validate strategy implementations
    """
    
    def __init__(self):
        """Initialize the strategy registry."""
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._instances: Dict[str, BaseStrategy] = {}
        self.logger = logging.getLogger("strategy_registry")
        
    def register_strategy(self, strategy_class: Type[BaseStrategy], name: Optional[str] = None) -> bool:
        """
        Register a strategy class.
        
        Args:
            strategy_class: Strategy class to register
            name: Optional name for the strategy (defaults to class name)
            
        Returns:
            bool: True if registered successfully, False otherwise
        """
        if not self._validate_strategy_class(strategy_class):
            return False
            
        strategy_name = name or strategy_class.__name__
        
        if strategy_name in self._strategies:
            self.logger.warning(f"Strategy {strategy_name} already registered, overwriting")
            
        self._strategies[strategy_name] = strategy_class
        self.logger.info(f"Registered strategy: {strategy_name}")
        return True
    
    def unregister_strategy(self, name: str) -> bool:
        """
        Unregister a strategy class.
        
        Args:
            name: Name of the strategy to unregister
            
        Returns:
            bool: True if unregistered successfully, False otherwise
        """
        if name not in self._strategies:
            self.logger.warning(f"Strategy {name} not found in registry")
            return False
            
        # Remove any instances
        if name in self._instances:
            del self._instances[name]
            
        del self._strategies[name]
        self.logger.info(f"Unregistered strategy: {name}")
        return True
    
    def create_strategy(self, name: str, config: StrategyConfig) -> Optional[BaseStrategy]:
        """
        Create a strategy instance from configuration.
        
        Args:
            name: Name of the strategy class to instantiate
            config: Configuration for the strategy
            
        Returns:
            Optional[BaseStrategy]: Strategy instance if created successfully, None otherwise
        """
        if name not in self._strategies:
            self.logger.error(f"Strategy {name} not found in registry")
            return None
            
        try:
            strategy_class = self._strategies[name]
            instance = strategy_class(config)
            
            # Store instance for management
            instance_key = f"{name}_{config.name}"
            self._instances[instance_key] = instance
            
            self.logger.info(f"Created strategy instance: {instance_key}")
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to create strategy {name}: {str(e)}")
            return None
    
    def create_strategies_from_config(self, configs: List[Dict[str, Any]]) -> List[BaseStrategy]:
        """
        Create multiple strategy instances from configuration list.
        
        Args:
            configs: List of strategy configuration dictionaries
            
        Returns:
            List[BaseStrategy]: List of created strategy instances
        """
        strategies = []
        
        for config_dict in configs:
            try:
                # Extract strategy type and create config
                strategy_type = config_dict.get('type')
                if not strategy_type:
                    self.logger.error("Strategy configuration missing 'type' field")
                    continue
                    
                config = StrategyConfig(
                    name=config_dict.get('name', strategy_type),
                    enabled=config_dict.get('enabled', True),
                    parameters=config_dict.get('parameters', {}),
                    risk_limits=config_dict.get('risk_limits', {})
                )
                
                strategy = self.create_strategy(strategy_type, config)
                if strategy:
                    strategies.append(strategy)
                    
            except Exception as e:
                self.logger.error(f"Failed to create strategy from config: {str(e)}")
                
        self.logger.info(f"Created {len(strategies)} strategies from configuration")
        return strategies
    
    def discover_strategies(self, package_path: str) -> int:
        """
        Discover and register strategies from a package.
        
        Args:
            package_path: Python package path to search for strategies
            
        Returns:
            int: Number of strategies discovered and registered
        """
        discovered_count = 0
        
        try:
            # Import the package
            package = importlib.import_module(package_path)
            package_dir = Path(package.__file__).parent
            
            # Walk through all modules in the package
            for importer, modname, ispkg in pkgutil.iter_modules([str(package_dir)]):
                if ispkg:
                    continue
                    
                try:
                    # Import the module
                    full_module_name = f"{package_path}.{modname}"
                    module = importlib.import_module(full_module_name)
                    
                    # Find strategy classes in the module
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BaseStrategy) and 
                            obj != BaseStrategy and 
                            obj.__module__ == full_module_name):
                            
                            if self.register_strategy(obj, name):
                                discovered_count += 1
                                
                except Exception as e:
                    self.logger.error(f"Failed to import module {modname}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Failed to discover strategies in {package_path}: {str(e)}")
            
        self.logger.info(f"Discovered {discovered_count} strategies in {package_path}")
        return discovered_count
    
    def get_registered_strategies(self) -> List[str]:
        """
        Get list of registered strategy names.
        
        Returns:
            List[str]: List of registered strategy names
        """
        return list(self._strategies.keys())
    
    def get_strategy_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered strategy.
        
        Args:
            name: Name of the strategy
            
        Returns:
            Optional[Dict[str, Any]]: Strategy information if found, None otherwise
        """
        if name not in self._strategies:
            return None
            
        strategy_class = self._strategies[name]
        
        return {
            'name': name,
            'class': strategy_class.__name__,
            'module': strategy_class.__module__,
            'docstring': strategy_class.__doc__,
            'methods': [method for method in dir(strategy_class) 
                       if not method.startswith('_')],
            'registered_instances': [key for key in self._instances.keys() 
                                   if key.startswith(f"{name}_")]
        }
    
    def get_all_strategy_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered strategies.
        
        Returns:
            Dict[str, Dict[str, Any]]: Information for all registered strategies
        """
        return {name: self.get_strategy_info(name) 
                for name in self._strategies.keys()}
    
    def validate_strategy_config(self, strategy_type: str, config: Dict[str, Any]) -> bool:
        """
        Validate a strategy configuration.
        
        Args:
            strategy_type: Type of strategy to validate against
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if strategy_type not in self._strategies:
            self.logger.error(f"Strategy type {strategy_type} not registered")
            return False
            
        try:
            # Create a temporary config object to validate
            strategy_config = StrategyConfig(
                name=config.get('name', strategy_type),
                enabled=config.get('enabled', True),
                parameters=config.get('parameters', {}),
                risk_limits=config.get('risk_limits', {})
            )
            
            # Create temporary instance to validate parameters
            strategy_class = self._strategies[strategy_type]
            temp_instance = strategy_class(strategy_config)
            
            return temp_instance.validate_parameters()
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed for {strategy_type}: {str(e)}")
            return False
    
    def _validate_strategy_class(self, strategy_class: Type[BaseStrategy]) -> bool:
        """
        Validate that a class is a proper strategy implementation.
        
        Args:
            strategy_class: Strategy class to validate
            
        Returns:
            bool: True if valid strategy class, False otherwise
        """
        if not inspect.isclass(strategy_class):
            self.logger.error("Provided object is not a class")
            return False
            
        if not issubclass(strategy_class, BaseStrategy):
            self.logger.error(f"Class {strategy_class.__name__} does not inherit from BaseStrategy")
            return False
            
        if strategy_class == BaseStrategy:
            self.logger.error("Cannot register the BaseStrategy class itself")
            return False
            
        # Check that all abstract methods are implemented
        abstract_methods = getattr(strategy_class, '__abstractmethods__', set())
        if abstract_methods:
            self.logger.error(f"Class {strategy_class.__name__} has unimplemented abstract methods: {abstract_methods}")
            return False
            
        return True
    
    def clear_registry(self):
        """Clear all registered strategies and instances."""
        self._strategies.clear()
        self._instances.clear()
        self.logger.info("Cleared strategy registry")
    
    def __len__(self) -> int:
        """Return number of registered strategies."""
        return len(self._strategies)
    
    def __contains__(self, name: str) -> bool:
        """Check if strategy is registered."""
        return name in self._strategies
    
    def __iter__(self):
        """Iterate over registered strategy names."""
        return iter(self._strategies.keys())