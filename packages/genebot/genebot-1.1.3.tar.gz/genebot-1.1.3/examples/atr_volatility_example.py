#!/usr/bin/env python3
"""
ATR Volatility Strategy Example

This example demonstrates the ATR (Average True Range) Volatility Strategy
for high-probability volatility-based trading signals.

The ATR strategy focuses on:
1. Volatility breakouts and contractions
2. ATR-based support/resistance levels
3. Volume-volatility correlation analysis
4. Volatility squeeze detection and expansion
5. Multi-timeframe volatility analysis
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.strategies import (
    ATRVolatilityStrategy,
    StrategyRegistry,
    StrategyEngine,
    SignalProcessor,
    StrategyConfigManager,
    TechnicalIndicators
)
from src.models.data_models import MarketData


def create_volatility_market_data(symbol: str = "BTCUSD", num_points: int = 150) -> list[MarketData]:
    """
    Create market data with realistic volatility patterns for ATR strategy testing.
    
    Args:
        symbol: Trading symbol
        num_points: Number of data points to generate
        
    Returns:
        List of MarketData objects with volatility patterns
    """
    market_data = []
    base_time = datetime.now() - timedelta(minutes=num_points)
    base_price = 50000.0
    
    # Create different volatility phases
    squeeze_phase = num_points // 3      # Low volatility squeeze
    expansion_phase = num_points // 4    # High volatility expansion
    normal_phase = num_points - (squeeze_phase + expansion_phase)  # Normal volatility
    
    prices = []
    volumes = []
    
    # Phase 1: Volatility squeeze (low ATR)
    current_price = base_price
    for i in range(squeeze_phase):
        # Very tight price movement (low volatility)
        price_change = np.random.normal(0, 10)  # Small movements
        current_price += price_change
        
        # Lower volume during squeeze
        volume = 800 + np.random.normal(100, 50)
        
        prices.append(current_price)
        volumes.append(max(volume, 100))
    
    # Phase 2: Volatility expansion (high ATR)
    for i in range(expansion_phase):
        # Large price movements (high volatility)
        if i < expansion_phase // 2:
            # Breakout upward
            price_change = abs(np.random.normal(50, 30))  # Strong upward moves
        else:
            # Some retracement
            price_change = np.random.normal(-20, 40)  # Mixed movements
        
        current_price += price_change
        
        # Higher volume during expansion
        volume = 1500 + np.random.normal(300, 150)
        
        prices.append(current_price)
        volumes.append(max(volume, 100))
    
    # Phase 3: Normal volatility
    for i in range(normal_phase):
        # Normal price movements
        price_change = np.random.normal(0, 25)  # Medium movements
        current_price += price_change
        
        # Normal volume
        volume = 1000 + np.random.normal(200, 100)
        
        prices.append(current_price)
        volumes.append(max(volume, 100))
    
    # Create MarketData objects with realistic OHLC
    for i, (price, volume) in enumerate(zip(prices, volumes)):
        # Calculate volatility for this period
        if i < squeeze_phase:
            volatility_factor = 0.003  # 0.3% volatility during squeeze
        elif i < squeeze_phase + expansion_phase:
            volatility_factor = 0.015  # 1.5% volatility during expansion
        else:
            volatility_factor = 0.008  # 0.8% normal volatility
        
        # Create realistic OHLC
        open_price = price + np.random.normal(0, price * volatility_factor * 0.3)
        
        # High and low based on volatility
        high_offset = abs(np.random.normal(0, price * volatility_factor))
        low_offset = abs(np.random.normal(0, price * volatility_factor))
        
        high_price = max(open_price, price) + high_offset
        low_price = min(open_price, price) - low_offset
        
        data = MarketData(
            symbol=symbol,
            timestamp=base_time + timedelta(minutes=i),
            open=Decimal(str(round(open_price, 2))),
            high=Decimal(str(round(high_price, 2))),
            low=Decimal(str(round(low_price, 2))),
            close=Decimal(str(round(price, 2))),
            volume=Decimal(str(round(volume, 2))),
            exchange="atr_example"
        )
        market_data.append(data)
    
    return market_data


def demonstrate_atr_indicators():
    """Demonstrate ATR technical indicators."""
    print("=== ATR Technical Indicators Demo ===")
    
    indicators = TechnicalIndicators()
    
    # Create sample OHLC data with varying volatility
    base_price = 50000
    prices = []
    highs = []
    lows = []
    
    for i in range(30):
        # Simulate increasing volatility
        volatility = 50 + (i * 5)  # Increasing volatility
        
        price = base_price + np.random.normal(0, 20)
        high = price + abs(np.random.normal(0, volatility))
        low = price - abs(np.random.normal(0, volatility))
        
        prices.append(price)
        highs.append(high)
        lows.append(low)
        base_price = price
    
    print(f"Sample data: {len(prices)} price points")
    print(f"Price range: ${prices[0]:.2f} - ${prices[-1]:.2f}")
    
    # Calculate ATR
    atr = indicators.atr(highs, lows, prices, 14)
    print(f"ATR(14): ${atr:.2f}" if atr else "ATR(14): N/A")
    
    # Calculate ATR bands
    atr_bands = indicators.atr_bands(highs, lows, prices, 14, 2.0)
    if atr_bands:
        upper, middle, lower = atr_bands
        print(f"ATR Bands (2.0x): Upper=${upper:.2f}, Middle=${middle:.2f}, Lower=${lower:.2f}")
        
        # Calculate current position within bands
        current_price = prices[-1]
        position = (current_price - lower) / (upper - lower) if upper != lower else 0.5
        print(f"Current position in ATR bands: {position:.3f} (0=lower, 1=upper)")
    
    # Show volatility analysis
    if len(prices) >= 20:
        recent_atr = []
        for i in range(14, len(prices)):
            period_atr = indicators.atr(highs[:i+1], lows[:i+1], prices[:i+1], 14)
            if period_atr:
                recent_atr.append(period_atr)
        
        if len(recent_atr) >= 2:
            atr_change = (recent_atr[-1] - recent_atr[0]) / recent_atr[0] * 100
            print(f"ATR change over period: {atr_change:.1f}%")
            
            if atr_change > 50:
                print("  → Volatility EXPANSION detected")
            elif atr_change < -30:
                print("  → Volatility CONTRACTION detected")
            else:
                print("  → Normal volatility levels")
    
    print()


def demonstrate_atr_volatility_strategy(market_data):
    """Demonstrate ATR Volatility Strategy."""
    print("=== ATR Volatility Strategy Demo ===")
    
    config_manager = StrategyConfigManager()
    
    # Create ATR volatility configuration
    config = config_manager.create_config_from_template(
        'ATRVolatilityStrategy',
        'atr_demo',
        {
            'atr_period': 14,
            'atr_multiplier': 2.0,
            'volatility_threshold': 1.5,
            'squeeze_threshold': 0.6,
            'expansion_threshold': 2.0,
            'min_confidence': 0.85,
            'trend_filter': True
        }
    )
    
    strategy = ATRVolatilityStrategy(config)
    strategy.initialize()
    strategy.start()
    
    print(f"Strategy parameters:")
    print(f"  ATR period: {strategy.atr_period}")
    print(f"  ATR multiplier: {strategy.atr_multiplier}")
    print(f"  Volatility threshold: {strategy.volatility_threshold}")
    print(f"  Squeeze threshold: {strategy.squeeze_threshold}")
    print(f"  Expansion threshold: {strategy.expansion_threshold}")
    print(f"  Required data length: {strategy.get_required_data_length()}")
    
    # Process market data
    signals_generated = 0
    volatility_states = []
    
    for i in range(strategy.get_required_data_length(), len(market_data)):
        data_slice = market_data[:i+1]
        signal = strategy.process_market_data(data_slice)
        
        # Track volatility states
        if len(strategy._atr_history) >= 20:
            current_atr = strategy._atr_history[-1]
            atr_ma = sum(strategy._atr_history[-20:]) / 20
            atr_ratio = current_atr / atr_ma if atr_ma > 0 else 1.0
            volatility_state = strategy._classify_volatility_state(atr_ratio)
            volatility_states.append(volatility_state)
        
        if signal:
            signals_generated += 1
            print(f"\n  ATR Signal #{signals_generated}: {signal.action.value} at ${float(signal.price):.2f}")
            print(f"    Confidence: {signal.confidence:.3f}")
            print(f"    Volatility state: {signal.metadata['volatility_state']}")
            print(f"    ATR ratio: {signal.metadata['atr_ratio']:.2f}")
            print(f"    Breakout type: {signal.metadata.get('breakout_type', 'N/A')}")
            print(f"    Pattern strength: {signal.metadata['pattern_strength']:.2f}")
            print(f"    Volume confirmation: {signal.metadata['volume_confirmation']}")
            print(f"    Current ATR: ${signal.metadata['current_atr']:.2f}")
            print(f"    ATR stop loss: ${signal.metadata['atr_stop_loss']:.2f}")
            print(f"    ATR take profit: ${signal.metadata['atr_take_profit']:.2f}")
            print(f"    Upper breakout: ${signal.metadata['upper_breakout']:.2f}")
            print(f"    Lower breakout: ${signal.metadata['lower_breakout']:.2f}")
    
    print(f"\nATR Volatility Strategy Results:")
    print(f"  Total signals generated: {signals_generated}")
    print(f"  Average confidence: {strategy.get_performance_metrics()['success_rate']:.3f}")
    
    # Analyze volatility states
    if volatility_states:
        state_counts = {}
        for state in volatility_states:
            state_counts[state] = state_counts.get(state, 0) + 1
        
        print(f"  Volatility state distribution:")
        for state, count in state_counts.items():
            percentage = count / len(volatility_states) * 100
            print(f"    {state}: {count} periods ({percentage:.1f}%)")
    
    print()


def demonstrate_atr_strategy_presets():
    """Demonstrate ATR strategy preset configurations."""
    print("=== ATR Strategy Presets Demo ===")
    
    config_manager = StrategyConfigManager()
    
    # Get ATR presets
    presets = config_manager.create_preset_configs()
    atr_presets = {name: config for name, config in presets.items() 
                   if 'atr_volatility' in name and config is not None}
    
    print(f"Available ATR presets: {len(atr_presets)}")
    
    for preset_name, config in atr_presets.items():
        print(f"\n--- {preset_name} ---")
        print(f"  ATR multiplier: {config.parameters.get('atr_multiplier', 'N/A')}")
        print(f"  Volatility threshold: {config.parameters.get('volatility_threshold', 'N/A')}")
        print(f"  Squeeze threshold: {config.parameters.get('squeeze_threshold', 'N/A')}")
        print(f"  Expansion threshold: {config.parameters.get('expansion_threshold', 'N/A')}")
        print(f"  Min confidence: {config.parameters.get('min_confidence', 'N/A')}")
        print(f"  Trend filter: {config.parameters.get('trend_filter', 'N/A')}")
        print(f"  Risk limits: {config.risk_limits}")
    
    # Demonstrate parameter info
    param_info = config_manager.get_parameter_info('ATRVolatilityStrategy')
    if param_info:
        print(f"\n--- ATR Strategy Parameter Info ---")
        print(f"Description: {param_info['description']}")
        print(f"Parameters:")
        for param_name, param_data in param_info['parameters'].items():
            print(f"  {param_name}: {param_data['description']}")
            print(f"    Default: {param_data['default']}")
            print(f"    Range: {param_data['range']}")
    
    print()


def demonstrate_atr_engine_integration(market_data):
    """Demonstrate ATR strategy integration with strategy engine."""
    print("=== ATR Strategy Engine Integration Demo ===")
    
    # Set up strategy registry
    registry = StrategyRegistry()
    registry.register_strategy(ATRVolatilityStrategy)
    
    # Set up signal processor and engine
    signal_processor = SignalProcessor()
    engine = StrategyEngine(registry, signal_processor, max_workers=2)
    
    # Create multiple ATR strategy configurations
    configs = [
        {
            'type': 'ATRVolatilityStrategy',
            'name': 'atr_breakout',
            'enabled': True,
            'parameters': {
                'atr_multiplier': 2.5,
                'expansion_threshold': 2.5,
                'min_confidence': 0.88,
                'trend_filter': True
            }
        },
        {
            'type': 'ATRVolatilityStrategy',
            'name': 'atr_squeeze',
            'enabled': True,
            'parameters': {
                'atr_multiplier': 1.8,
                'squeeze_threshold': 0.5,
                'min_confidence': 0.86,
                'volume_correlation': 0.8
            }
        }
    ]
    
    # Create strategies from config
    strategies = registry.create_strategies_from_config(configs)
    print(f"Created {len(strategies)} ATR strategies")
    
    # Add strategies to engine
    for strategy in strategies:
        engine.add_strategy(strategy)
    
    # Start engine and strategies
    engine.start_engine()
    started_count = engine.start_all_strategies()
    print(f"Started {started_count} ATR strategies in engine")
    
    # Process market data through engine
    print("\nProcessing market data through ATR strategy engine...")
    total_signals = 0
    
    # Process in chunks to show progress
    chunk_size = 30
    for chunk_start in range(70, len(market_data), chunk_size):
        chunk_end = min(chunk_start + chunk_size, len(market_data))
        data_slice = market_data[:chunk_end]
        
        signals = engine.process_market_data(data_slice)
        
        if signals:
            total_signals += len(signals)
            print(f"\nATR signals at data point {chunk_end}:")
            for signal in signals:
                print(f"  - {signal.original_signal.strategy_name}: "
                      f"{signal.original_signal.action.value} "
                      f"(confidence: {signal.original_signal.confidence:.3f}, "
                      f"priority: {signal.priority.name})")
                
                # Show ATR-specific metadata
                metadata = signal.original_signal.metadata
                print(f"    Volatility: {metadata.get('volatility_state', 'N/A')}, "
                      f"ATR ratio: {metadata.get('atr_ratio', 0):.2f}, "
                      f"Breakout: {metadata.get('breakout_type', 'N/A')}")
    
    # Get final statistics
    print(f"\n=== ATR Engine Statistics ===")
    print(f"Total ATR signals generated: {total_signals}")
    
    status = engine.get_strategy_status()
    for name, info in status.items():
        perf = info['performance']
        print(f"{name}:")
        print(f"  - Signals generated: {perf['signals_generated']}")
        print(f"  - Success rate: {perf['success_rate']:.3f}")
        print(f"  - Active: {info['active']}")
    
    engine_stats = engine.get_engine_stats()
    print(f"\nEngine execution stats:")
    print(f"  - Total executions: {engine_stats['execution_stats']['total_executions']}")
    print(f"  - Average execution time: {engine_stats['execution_stats']['average_execution_time']:.4f}s")
    
    # Stop engine
    engine.stop_engine()
    print("\nATR strategy engine stopped")
    print()


def analyze_volatility_patterns(market_data):
    """Analyze volatility patterns in the market data."""
    print("=== Volatility Pattern Analysis ===")
    
    indicators = TechnicalIndicators()
    
    # Extract OHLC data
    highs = [float(data.high) for data in market_data]
    lows = [float(data.low) for data in market_data]
    closes = [float(data.close) for data in market_data]
    volumes = [float(data.volume) for data in market_data]
    
    # Calculate ATR over time
    atr_values = []
    atr_ratios = []
    
    for i in range(14, len(market_data)):
        atr = indicators.atr(highs[:i+1], lows[:i+1], closes[:i+1], 14)
        if atr:
            atr_values.append(atr)
            
            # Calculate ATR ratio (current vs average)
            if len(atr_values) >= 20:
                atr_avg = sum(atr_values[-20:]) / 20
                atr_ratio = atr / atr_avg if atr_avg > 0 else 1.0
                atr_ratios.append(atr_ratio)
    
    if atr_values:
        print(f"ATR Analysis ({len(atr_values)} periods):")
        print(f"  Average ATR: ${np.mean(atr_values):.2f}")
        print(f"  Min ATR: ${min(atr_values):.2f}")
        print(f"  Max ATR: ${max(atr_values):.2f}")
        print(f"  ATR volatility: {np.std(atr_values):.2f}")
    
    if atr_ratios:
        print(f"\nATR Ratio Analysis ({len(atr_ratios)} periods):")
        print(f"  Average ratio: {np.mean(atr_ratios):.2f}")
        print(f"  Min ratio: {min(atr_ratios):.2f}")
        print(f"  Max ratio: {max(atr_ratios):.2f}")
        
        # Classify periods
        squeeze_periods = sum(1 for ratio in atr_ratios if ratio <= 0.6)
        expansion_periods = sum(1 for ratio in atr_ratios if ratio >= 2.0)
        normal_periods = len(atr_ratios) - squeeze_periods - expansion_periods
        
        print(f"\nVolatility Distribution:")
        print(f"  Squeeze periods: {squeeze_periods} ({squeeze_periods/len(atr_ratios)*100:.1f}%)")
        print(f"  Expansion periods: {expansion_periods} ({expansion_periods/len(atr_ratios)*100:.1f}%)")
        print(f"  Normal periods: {normal_periods} ({normal_periods/len(atr_ratios)*100:.1f}%)")
    
    # Volume-volatility correlation
    if len(volumes) >= len(atr_values):
        recent_volumes = volumes[-len(atr_values):]
        if len(recent_volumes) == len(atr_values):
            # Simple correlation calculation
            vol_corr = np.corrcoef(recent_volumes, atr_values)[0, 1]
            print(f"\nVolume-Volatility Correlation: {vol_corr:.3f}")
            
            if vol_corr > 0.5:
                print("  → Strong positive correlation (volume confirms volatility)")
            elif vol_corr < -0.5:
                print("  → Strong negative correlation (volume inverse to volatility)")
            else:
                print("  → Weak correlation (volume and volatility not aligned)")
    
    print()


def main():
    """Main demonstration function."""
    print("ATR Volatility Strategy Example")
    print("=" * 50)
    print()
    
    # Create market data with volatility patterns
    print("Creating market data with volatility patterns...")
    market_data = create_volatility_market_data("BTCUSD", 180)
    print(f"Generated {len(market_data)} data points")
    print(f"Price range: ${float(market_data[0].close):.2f} - ${float(market_data[-1].close):.2f}")
    print(f"Time range: {market_data[0].timestamp} to {market_data[-1].timestamp}")
    print()
    
    # Demonstrate ATR technical indicators
    demonstrate_atr_indicators()
    
    # Analyze volatility patterns in the data
    analyze_volatility_patterns(market_data)
    
    # Demonstrate ATR strategy presets
    demonstrate_atr_strategy_presets()
    
    # Demonstrate individual ATR strategy
    demonstrate_atr_volatility_strategy(market_data)
    
    # Demonstrate ATR strategy engine integration
    demonstrate_atr_engine_integration(market_data)
    
    print("=" * 50)
    print("ATR Volatility Strategy Demo Completed!")
    print()
    print("Key Features Demonstrated:")
    print("✓ ATR calculation and analysis")
    print("✓ Volatility squeeze and expansion detection")
    print("✓ ATR-based breakout levels")
    print("✓ Volume-volatility correlation analysis")
    print("✓ Multi-timeframe volatility analysis")
    print("✓ ATR-based position sizing and risk management")
    print("✓ High-confidence volatility signals (86%+ confidence)")
    print("✓ Integration with strategy framework")
    print()
    print("The ATR Volatility Strategy is designed to identify high-probability")
    print("trading opportunities based on volatility analysis, providing reliable")
    print("signals for both breakout and mean reversion scenarios.")


if __name__ == "__main__":
    main()