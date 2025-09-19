#!/usr/bin/env python3
"""
Integration test demonstrating configuration system working with logging.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_config_manager
from config.logging import setup_logging, get_logger


def main():
    """Test configuration integration with logging system."""
    print("=== Configuration + Logging Integration Test ===\n")
    
    # Set up test environment
    os.environ.update({
        'LOG_LEVEL': 'INFO',
        'LOG_FORMAT': 'standard',
        'EXCHANGE_BINANCE_EXCHANGE_TYPE': 'binance',
        'EXCHANGE_BINANCE_API_KEY': '${BINANCE_API_KEY}',
        'EXCHANGE_BINANCE_API_SECRET': '${BINANCE_API_SECRET}',
        'STRATEGY_MA_STRATEGY_TYPE': 'moving_average',
        'STRATEGY_MA_SYMBOLS': 'BTC/USDT',
        'STRATEGY_MA_TIMEFRAME': '1h'
    })
    
    # Load configuration
    config_manager = get_config_manager()
    config = config_manager.load_config()
    
    # Set up logging using configuration
    logging_config = config.logging
    setup_logging(
        log_level=logging_config.log_level.value,
        log_format=logging_config.log_format.value,
        log_file=logging_config.log_file
    )
    
    # Test logging
    logger = get_logger('config_test')
    logger.info("Configuration loaded successfully")
    logger.info(f"App: {config.app_name}")
    logger.info(f"Exchanges: {list(config.exchanges.keys())}")
    logger.info(f"Strategies: {list(config.strategies.keys())}")
    
    print("✓ Configuration and logging integration test completed!")
    print("Check the console output above for log messages.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())