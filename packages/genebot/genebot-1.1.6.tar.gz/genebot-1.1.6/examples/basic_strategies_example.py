#!/usr/bin/env python3
"""
Example demonstrating the basic trading strategies implementation.

This example shows how to:
1. Create and configure MovingAverageStrategy and RSIStrategy
2. Use the StrategyConfigManager for parameter management
3. Register strategies with the StrategyRegistry
4. Run strategies through the StrategyEngine
5. Process market data and generate trading signals
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.strategies import (
    MovingAverageStrategy, 
    RSIStrategy, 
    StrategyRegistry, 
    StrategyEngine, 
    SignalProcessor,
    StrategyConfigManager,
    TechnicalIndicators
)
from src.models.data_models import MarketData


def create_sample_market_data(symbol: str = "BTCUSD", num_points: int = 50) -> list[MarketData]:
    """
    Create sample market data for testing strategies.
    
    Args:
        symbol: Trading symbol
        num_points: Number of data points to generate
        
    Returns:
        List of MarketData objects
    """
    market_data = []
    base_time = datetime.now() - timedelta(minutes=num_points)
    base_price = 50000.0
    
    for i in range(num_points):
        # Create some price movement
        price_change = (i % 10 - 5) * 100  # Oscillating pattern
        if i > 25:  # Add trend in second half
            price_change += (i - 25) * 50
            
        price = base_price + price_change
        
        data = MarketData(
            symbol=symbol,
            timestamp=base_time + timedelta(minutes=i),
            open=Decimal(str(price * 0.999)),
            high=Decimal(str(price * 1.002)),
            low=Decimal(str(price * 0.998)),
            close=Decimal(str(price)),
            volume=Decimal("1000.0"),
            exchange="example"
        )
        market_data.append(data)
    
    return market_data


def demonstrate_technical_indicators():
    """Demonstrate technical indicators functionality."""
    print("=== Technical Indicators Demo ===")
    
    indicators = TechnicalIndicators()
    
    # Create sample price data
    prices = [50000 + i * 100 + (i % 5) * 50 for i in range(30)]
    
    print(f"Sample prices (last 10): {prices[-10:]}")
    
    # Calculate various indicators
    sma_10 = indicators.sma(prices, 10)
    ema_10 = indicators.ema(prices, 10)
    rsi = indicators.rsi(prices, 14)
    
    print(f"SMA(10): {sma_10[-1] if sma_10 else 'N/A'}")
    print(f"EMA(10): {ema_10[-1] if ema_10 else 'N/A'}")
    print(f"RSI(14): {rsi if rsi else 'N/A'}")
    
    # MACD
    macd_result = indicators.macd(prices)
    if macd_result:
        macd_line, signal_line, histogram = macd_result
        print(f"MACD: {macd_line:.2f}, Signal: {signal_line:.2f}, Histogram: {histogram:.2f}")
    
    # Bollinger Bands
    bb_result = indicators.bollinger_bands(prices, 20, 2.0)
    if bb_result:
        upper, middle, lower = bb_result
        print(f"Bollinger Bands - Upper: {upper:.2f}, Middle: {middle:.2f}, Lower: {lower:.2f}")
    
    print(f"Available indicators: {indicators.get_available_indicators()}")
    print()


def demonstrate_strategy_config_manager():
    """Demonstrate strategy configuration management."""
    print("=== Strategy Configuration Manager Demo ===")
    
    config_manager = StrategyConfigManager()
    
    # Show available templates
    templates = config_manager.get_available_templates()
    print(f"Available strategy templates: {templates}")
    
    # Get parameter info for MovingAverageStrategy
    ma_info = config_manager.get_parameter_info('MovingAverageStrategy')
    print(f"MovingAverageStrategy parameters: {ma_info['parameters'].keys()}")
    
    # Create configurations from templates
    ma_config = config_manager.create_config_from_template(
        'MovingAverageStrategy', 
        'ma_example',
        {'short_window': 5, 'long_window': 15, 'min_confidence': 0.8}
    )
    
    rsi_config = config_manager.create_config_from_template(
        'RSIStrategy',
        'rsi_example', 
        {'rsi_period': 10, 'oversold_threshold': 25, 'overbought_threshold': 75}
    )
    
    print(f"Created MA config: {ma_config.name} with parameters {ma_config.parameters}")
    print(f"Created RSI config: {rsi_config.name} with parameters {rsi_config.parameters}")
    
    # Create preset configurations
    presets = config_manager.create_preset_configs()
    print(f"Available presets: {list(presets.keys())}")
    
    print()
    return ma_config, rsi_config


def demonstrate_individual_strategies(market_data):
    """Demonstrate individual strategy functionality."""
    print("=== Individual Strategy Demo ===")
    
    config_manager = StrategyConfigManager()
    
    # Test MovingAverageStrategy
    print("--- MovingAverageStrategy ---")
    ma_config = config_manager.create_config_from_template(
        'MovingAverageStrategy',
        'ma_demo',
        {'short_window': 5, 'long_window': 10, 'min_confidence': 0.6}
    )
    
    ma_strategy = MovingAverageStrategy(ma_config)
    ma_strategy.initialize()
    ma_strategy.start()
    
    print(f"MA Strategy required data length: {ma_strategy.get_required_data_length()}")
    print(f"MA Strategy parameters valid: {ma_strategy.validate_parameters()}")
    
    # Process market data
    ma_signal = ma_strategy.process_market_data(market_data)
    if ma_signal:
        print(f"MA Signal: {ma_signal.action.value} {ma_signal.symbol} "
              f"(confidence: {ma_signal.confidence:.2f})")
        print(f"MA Signal metadata: {ma_signal.metadata}")
    else:
        print("No MA signal generated")
    
    ma_info = ma_strategy.get_strategy_info()
    print(f"MA Strategy info: {ma_info['current_values']}")
    
    # Test RSIStrategy
    print("\n--- RSIStrategy ---")
    rsi_config = config_manager.create_config_from_template(
        'RSIStrategy',
        'rsi_demo',
        {'rsi_period': 8, 'oversold_threshold': 35, 'overbought_threshold': 65}
    )
    
    rsi_strategy = RSIStrategy(rsi_config)
    rsi_strategy.initialize()
    rsi_strategy.start()
    
    print(f"RSI Strategy required data length: {rsi_strategy.get_required_data_length()}")
    print(f"RSI Strategy parameters valid: {rsi_strategy.validate_parameters()}")
    
    # Process market data
    rsi_signal = rsi_strategy.process_market_data(market_data)
    if rsi_signal:
        print(f"RSI Signal: {rsi_signal.action.value} {rsi_signal.symbol} "
              f"(confidence: {rsi_signal.confidence:.2f})")
        print(f"RSI Signal metadata: {rsi_signal.metadata}")
    else:
        print("No RSI signal generated")
    
    rsi_info = rsi_strategy.get_strategy_info()
    print(f"RSI Strategy info: {rsi_info['current_values']}")
    
    print()


def demonstrate_strategy_engine(market_data):
    """Demonstrate strategy engine with multiple strategies."""
    print("=== Strategy Engine Demo ===")
    
    # Set up strategy registry
    registry = StrategyRegistry()
    registry.register_strategy(MovingAverageStrategy)
    registry.register_strategy(RSIStrategy)
    
    print(f"Registered strategies: {registry.get_registered_strategies()}")
    
    # Set up signal processor and engine
    signal_processor = SignalProcessor()
    engine = StrategyEngine(registry, signal_processor, max_workers=2)
    
    # Create strategy configurations
    config_manager = StrategyConfigManager()
    
    configs = [
        {
            'type': 'MovingAverageStrategy',
            'name': 'ma_engine_test',
            'enabled': True,
            'parameters': {
                'short_window': 3,
                'long_window': 8,
                'min_confidence': 0.7
            }
        },
        {
            'type': 'RSIStrategy', 
            'name': 'rsi_engine_test',
            'enabled': True,
            'parameters': {
                'rsi_period': 6,
                'oversold_threshold': 30,
                'overbought_threshold': 70,
                'min_confidence': 0.6
            }
        }
    ]
    
    # Create strategies from config
    strategies = registry.create_strategies_from_config(configs)
    print(f"Created {len(strategies)} strategies from config")
    
    # Add strategies to engine
    for strategy in strategies:
        engine.add_strategy(strategy)
    
    # Start engine and strategies
    engine.start_engine()
    started_count = engine.start_all_strategies()
    print(f"Started {started_count} strategies")
    
    # Process market data through engine
    print("Processing market data through engine...")
    signals = engine.process_market_data(market_data)
    
    print(f"Generated {len(signals)} signals from engine")
    for signal in signals:
        print(f"  - {signal.original_signal.strategy_name}: "
              f"{signal.original_signal.action.value} {signal.original_signal.symbol} "
              f"(confidence: {signal.original_signal.confidence:.2f}, "
              f"priority: {signal.priority.name})")
    
    # Get strategy status
    status = engine.get_strategy_status()
    print("\nStrategy Status:")
    for name, info in status.items():
        print(f"  {name}: active={info['active']}, "
              f"signals={info['performance']['signals_generated']}")
    
    # Get engine stats
    stats = engine.get_engine_stats()
    print(f"\nEngine Stats: {stats}")
    
    # Stop engine
    engine.stop_engine()
    print("Engine stopped")
    print()


def main():
    """Main demonstration function."""
    print("Basic Trading Strategies Example")
    print("=" * 50)
    
    # Create sample market data
    print("Creating sample market data...")
    market_data = create_sample_market_data("BTCUSD", 60)
    print(f"Created {len(market_data)} data points")
    print(f"Price range: {float(market_data[0].close):.2f} - {float(market_data[-1].close):.2f}")
    print()
    
    # Demonstrate technical indicators
    demonstrate_technical_indicators()
    
    # Demonstrate strategy configuration manager
    demonstrate_strategy_config_manager()
    
    # Demonstrate individual strategies
    demonstrate_individual_strategies(market_data)
    
    # Demonstrate strategy engine
    demonstrate_strategy_engine(market_data)
    
    print("Demo completed successfully!")


if __name__ == "__main__":
    main()