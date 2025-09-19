#!/usr/bin/env python3
"""
Example script demonstrating the configuration management system.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    ConfigManager,
    ConfigurationError,
    get_config_manager,
    get_config,
    ExchangeType,
    StrategyType
)


def main():
    """Demonstrate configuration management functionality."""
    print("=== Trading Bot Configuration Management Example ===\n")
    
    # 1. Create a configuration manager
    print("1. Creating configuration manager...")
    config_manager = ConfigManager()
    
    # 2. Save a configuration template
    print("2. Saving configuration template...")
    template_path = project_root / "config_template.yaml"
    config_manager.save_config_template(template_path)
    print(f"   Template saved to: {template_path}")
    
    # 3. Set up environment variables for testing
    print("3. Setting up test environment variables...")
    os.environ.update({
        'APP_NAME': 'TestTradingBot',
        'DEBUG': 'true',
        'DRY_RUN': 'true',
        
        # Exchange configuration
        'EXCHANGE_BINANCE_EXCHANGE_TYPE': 'binance',
        'EXCHANGE_BINANCE_API_KEY': 'test_api_key_123',
        'EXCHANGE_BINANCE_API_SECRET': 'test_api_secret_456',
        'EXCHANGE_BINANCE_SANDBOX': 'true',
        'EXCHANGE_BINANCE_ENABLED': 'true',
        
        # Strategy configuration
        'STRATEGY_MA_STRATEGY_TYPE': 'moving_average',
        'STRATEGY_MA_ENABLED': 'true',
        'STRATEGY_MA_SYMBOLS': 'BTC/USDT,ETH/USDT',
        'STRATEGY_MA_TIMEFRAME': '1h',
        'STRATEGY_MA_MAX_POSITIONS': '2',
        
        # Risk management
        'RISK_MAX_POSITION_SIZE': '0.05',
        'RISK_STOP_LOSS_PERCENTAGE': '0.02',
        
        # Logging
        'LOG_LEVEL': 'DEBUG',
        'LOG_FORMAT': 'json'
    })
    
    # 4. Load configuration
    print("4. Loading configuration from environment variables...")
    try:
        config = config_manager.load_config()
        print("   ✓ Configuration loaded successfully!")
        
        # Display configuration summary
        print(f"\n   App Name: {config.app_name}")
        print(f"   Debug Mode: {config.debug}")
        print(f"   Dry Run: {config.dry_run}")
        print(f"   Base Currency: {config.base_currency}")
        
        print(f"\n   Exchanges configured: {len(config.exchanges)}")
        for name, exchange in config.exchanges.items():
            print(f"     - {name}: {exchange.exchange_type.value} (enabled: {exchange.enabled})")
        
        print(f"\n   Strategies configured: {len(config.strategies)}")
        for name, strategy in config.strategies.items():
            print(f"     - {name}: {strategy.strategy_type.value} (enabled: {strategy.enabled})")
            print(f"       Symbols: {', '.join(strategy.symbols)}")
            print(f"       Timeframe: {strategy.timeframe}")
        
        print(f"\n   Risk Management:")
        print(f"     - Max position size: {config.risk.max_position_size}")
        print(f"     - Stop loss: {config.risk.stop_loss_percentage}")
        print(f"     - Max open positions: {config.risk.max_open_positions}")
        
        print(f"\n   Logging:")
        print(f"     - Level: {config.logging.log_level.value}")
        print(f"     - Format: {config.logging.log_format.value}")
        
    except ConfigurationError as e:
        print(f"   ✗ Configuration error: {e}")
        return 1
    
    # 5. Test configuration access methods
    print("\n5. Testing configuration access methods...")
    
    # Get specific exchange config
    binance_config = config_manager.get_exchange_config('binance')
    if binance_config:
        print(f"   ✓ Binance exchange found: {binance_config.exchange_type.value}")
    
    # Get enabled exchanges
    enabled_exchanges = config_manager.get_enabled_exchanges()
    print(f"   ✓ Enabled exchanges: {list(enabled_exchanges.keys())}")
    
    # Get enabled strategies
    enabled_strategies = config_manager.get_enabled_strategies()
    print(f"   ✓ Enabled strategies: {list(enabled_strategies.keys())}")
    
    # 6. Test global configuration access
    print("\n6. Testing global configuration access...")
    global_config = get_config()
    print(f"   ✓ Global config app name: {global_config.app_name}")
    
    # 7. Test configuration validation
    print("\n7. Testing configuration validation...")
    try:
        config_manager.validate_config()
        print("   ✓ Configuration validation passed!")
    except ConfigurationError as e:
        print(f"   ✗ Configuration validation failed: {e}")
    
    # 8. Test configuration reloading
    print("\n8. Testing configuration reloading...")
    os.environ['APP_NAME'] = 'ReloadedTradingBot'
    reloaded_config = config_manager.reload_config()
    print(f"   ✓ Configuration reloaded. New app name: {reloaded_config.app_name}")
    
    print("\n=== Configuration Management Example Complete ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())