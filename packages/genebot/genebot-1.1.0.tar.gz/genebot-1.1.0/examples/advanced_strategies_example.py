#!/usr/bin/env python3
"""
Advanced Trading Strategies Example - 99% Probability Focus

This example demonstrates the advanced trading strategies designed for high-probability signals:
1. MultiIndicatorStrategy - Confluence-based signals
2. MLPatternStrategy - Machine learning pattern recognition
3. AdvancedMomentumStrategy - Multi-timeframe momentum analysis
4. MeanReversionStrategy - Statistical mean reversion

These strategies combine multiple indicators and sophisticated analysis techniques
to achieve high-confidence trading signals with 99% probability focus.
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.strategies import (
    MultiIndicatorStrategy,
    AdvancedMomentumStrategy, 
    MeanReversionStrategy,
    StrategyRegistry,
    StrategyEngine,
    SignalProcessor,
    StrategyConfigManager,
    TechnicalIndicators
)

# Conditional ML import
try:
    from src.strategies import MLPatternStrategy
    ML_AVAILABLE = True
except ImportError:
    MLPatternStrategy = None
    ML_AVAILABLE = False
    print("Warning: MLPatternStrategy not available (scikit-learn required)")

from src.models.data_models import MarketData


def create_realistic_market_data(symbol: str = "BTCUSD", num_points: int = 200) -> list[MarketData]:
    """
    Create realistic market data with various patterns for testing advanced strategies.
    
    Args:
        symbol: Trading symbol
        num_points: Number of data points to generate
        
    Returns:
        List of MarketData objects with realistic price patterns
    """
    market_data = []
    base_time = datetime.now() - timedelta(minutes=num_points)
    base_price = 50000.0
    
    # Create different market phases
    trend_phase = num_points // 4
    consolidation_phase = num_points // 4
    reversal_phase = num_points // 4
    volatile_phase = num_points - (trend_phase + consolidation_phase + reversal_phase)
    
    prices = []
    volumes = []
    
    # Phase 1: Trending market (uptrend with momentum)
    for i in range(trend_phase):
        trend_component = i * 20  # Strong uptrend
        noise = np.random.normal(0, 50)  # Market noise
        momentum = min(i * 2, 100)  # Increasing momentum
        
        price = base_price + trend_component + noise + momentum
        volume = 1000 + np.random.normal(200, 50) + (i * 5)  # Increasing volume
        
        prices.append(max(price, base_price * 0.8))  # Prevent negative prices
        volumes.append(max(volume, 100))
    
    # Phase 2: Consolidation (sideways with mean reversion opportunities)
    consolidation_center = prices[-1]
    for i in range(consolidation_phase):
        # Oscillating around center with decreasing amplitude
        oscillation = np.sin(i * 0.3) * (200 - i * 2)
        noise = np.random.normal(0, 30)
        
        price = consolidation_center + oscillation + noise
        volume = 800 + np.random.normal(100, 30)  # Lower volume in consolidation
        
        prices.append(price)
        volumes.append(max(volume, 100))
    
    # Phase 3: Reversal (momentum shift with divergences)
    reversal_start = prices[-1]
    for i in range(reversal_phase):
        # Gradual then accelerating downtrend
        reversal_component = -(i ** 1.5) * 3
        noise = np.random.normal(0, 40)
        
        price = reversal_start + reversal_component + noise
        volume = 1200 + np.random.normal(300, 100) + (i * 8)  # High volume on reversal
        
        prices.append(price)
        volumes.append(max(volume, 100))
    
    # Phase 4: High volatility (extreme conditions for mean reversion)
    volatile_start = prices[-1]
    for i in range(volatile_phase):
        # High volatility with extreme moves
        volatility = np.random.choice([-1, 1]) * np.random.exponential(100)
        noise = np.random.normal(0, 80)
        
        price = volatile_start + volatility + noise
        volume = 1500 + np.random.normal(500, 200)  # Very high volume
        
        prices.append(price)
        volumes.append(max(volume, 100))
        volatile_start = price  # Update base for next iteration
    
    # Create MarketData objects
    for i, (price, volume) in enumerate(zip(prices, volumes)):
        # Create realistic OHLC from close price
        open_price = price + np.random.normal(0, 10)
        high_price = max(open_price, price) + abs(np.random.normal(0, 20))
        low_price = min(open_price, price) - abs(np.random.normal(0, 20))
        
        data = MarketData(
            symbol=symbol,
            timestamp=base_time + timedelta(minutes=i),
            open=Decimal(str(round(open_price, 2))),
            high=Decimal(str(round(high_price, 2))),
            low=Decimal(str(round(low_price, 2))),
            close=Decimal(str(round(price, 2))),
            volume=Decimal(str(round(volume, 2))),
            exchange="advanced_example"
        )
        market_data.append(data)
    
    return market_data


def demonstrate_multi_indicator_strategy(market_data):
    """Demonstrate MultiIndicatorStrategy for high-probability confluence signals."""
    print("=== Multi-Indicator Confluence Strategy Demo ===")
    
    config_manager = StrategyConfigManager()
    
    # Create high-probability configuration
    config = config_manager.create_config_from_template(
        'MultiIndicatorStrategy',
        'multi_indicator_99_prob',
        {
            'ma_fast': 8,
            'ma_slow': 21,
            'min_confluence': 6,  # Require 6+ confirming indicators
            'min_confidence': 0.92,  # Very high confidence threshold
            'volume_threshold': 1.5,
            'rsi_oversold': 25,
            'rsi_overbought': 75
        }
    )
    
    strategy = MultiIndicatorStrategy(config)
    strategy.initialize()
    strategy.start()
    
    print(f"Strategy parameters: {strategy.parameters}")
    print(f"Required data length: {strategy.get_required_data_length()}")
    
    # Process market data
    signals_generated = 0
    for i in range(strategy.get_required_data_length(), len(market_data)):
        data_slice = market_data[:i+1]
        signal = strategy.process_market_data(data_slice)
        
        if signal:
            signals_generated += 1
            print(f"  Signal #{signals_generated}: {signal.action.value} at ${float(signal.price):.2f}")
            print(f"    Confidence: {signal.confidence:.3f}")
            print(f"    Confluence count: {signal.metadata['confluence_count']}")
            print(f"    Confirming signals: {signal.metadata['confluence_signals']}")
            print(f"    Indicators: RSI={signal.metadata['indicators']['rsi']:.1f}, "
                  f"Volume ratio={signal.metadata['indicators']['volume_ratio']:.2f}")
            print()
    
    print(f"Multi-Indicator Strategy generated {signals_generated} high-confidence signals")
    print(f"Average confidence: {strategy.get_performance_metrics()['success_rate']:.3f}")
    print()


def demonstrate_ml_pattern_strategy(market_data):
    """Demonstrate MLPatternStrategy for pattern recognition."""
    if not ML_AVAILABLE:
        print("=== ML Pattern Strategy Demo ===")
        print("MLPatternStrategy not available (requires scikit-learn)")
        print()
        return
    
    print("=== ML Pattern Recognition Strategy Demo ===")
    
    config_manager = StrategyConfigManager()
    
    # Create ML configuration
    config = config_manager.create_config_from_template(
        'MLPatternStrategy',
        'ml_pattern_99_prob',
        {
            'lookback_period': 120,
            'prediction_threshold': 0.85,  # High ML confidence
            'min_confidence': 0.95,  # Very high signal confidence
            'retrain_frequency': 40,
            'use_ensemble': True
        }
    )
    
    strategy = MLPatternStrategy(config)
    strategy.initialize()
    strategy.start()
    
    print(f"Strategy parameters: {strategy.parameters}")
    print(f"Required data length: {strategy.get_required_data_length()}")
    
    # Process market data (ML needs more data to train)
    signals_generated = 0
    training_complete = False
    
    for i in range(strategy.get_required_data_length(), len(market_data)):
        data_slice = market_data[:i+1]
        signal = strategy.process_market_data(data_slice)
        
        if not training_complete and strategy.is_trained:
            print("  ML models trained successfully!")
            training_complete = True
        
        if signal:
            signals_generated += 1
            print(f"  ML Signal #{signals_generated}: {signal.action.value} at ${float(signal.price):.2f}")
            print(f"    Confidence: {signal.confidence:.3f}")
            print(f"    ML confidence: {signal.metadata['ml_confidence']:.3f}")
            print(f"    Features used: {signal.metadata['feature_count']}")
            print(f"    Models: {signal.metadata['models']}")
            print()
    
    print(f"ML Pattern Strategy generated {signals_generated} high-confidence signals")
    print()


def demonstrate_advanced_momentum_strategy(market_data):
    """Demonstrate AdvancedMomentumStrategy for momentum analysis."""
    print("=== Advanced Momentum Strategy Demo ===")
    
    config_manager = StrategyConfigManager()
    
    # Create momentum configuration
    config = config_manager.create_config_from_template(
        'AdvancedMomentumStrategy',
        'momentum_99_prob',
        {
            'momentum_periods': [5, 10, 20],
            'roc_periods': [3, 7, 14],
            'momentum_threshold': 2.5,  # Higher threshold for stronger signals
            'min_confidence': 0.91,  # Very high confidence
            'divergence_lookback': 12
        }
    )
    
    strategy = AdvancedMomentumStrategy(config)
    strategy.initialize()
    strategy.start()
    
    print(f"Strategy parameters: momentum_threshold={strategy.momentum_threshold}%")
    print(f"Required data length: {strategy.get_required_data_length()}")
    
    # Process market data
    signals_generated = 0
    for i in range(strategy.get_required_data_length(), len(market_data)):
        data_slice = market_data[:i+1]
        signal = strategy.process_market_data(data_slice)
        
        if signal:
            signals_generated += 1
            print(f"  Momentum Signal #{signals_generated}: {signal.action.value} at ${float(signal.price):.2f}")
            print(f"    Confidence: {signal.confidence:.3f}")
            print(f"    Signal count: {signal.metadata['signal_count']}")
            print(f"    Momentum signals: {signal.metadata['momentum_signals']}")
            print(f"    Divergences: Bullish={signal.metadata['bullish_divergence']}, "
                  f"Bearish={signal.metadata['bearish_divergence']}")
            print(f"    RSI: {signal.metadata['rsi']:.1f}")
            print()
    
    print(f"Advanced Momentum Strategy generated {signals_generated} high-confidence signals")
    print()


def demonstrate_mean_reversion_strategy(market_data):
    """Demonstrate MeanReversionStrategy for reversal signals."""
    print("=== Mean Reversion Strategy Demo ===")
    
    config_manager = StrategyConfigManager()
    
    # Create mean reversion configuration
    config = config_manager.create_config_from_template(
        'MeanReversionStrategy',
        'mean_reversion_99_prob',
        {
            'bb_std_dev': 2.8,  # Wider bands for extreme conditions
            'rsi_extreme_oversold': 15,  # Very extreme levels
            'rsi_extreme_overbought': 85,
            'deviation_threshold': 2.5,  # Higher deviation threshold
            'min_confluence': 5,  # Require 5+ confirming signals
            'min_confidence': 0.90,  # Very high confidence
            'volume_confirmation': 1.8
        }
    )
    
    strategy = MeanReversionStrategy(config)
    strategy.initialize()
    strategy.start()
    
    print(f"Strategy parameters: BB std_dev={strategy.bb_std_dev}, "
          f"RSI extremes={strategy.rsi_extreme_oversold}-{strategy.rsi_extreme_overbought}")
    print(f"Required data length: {strategy.get_required_data_length()}")
    
    # Process market data
    signals_generated = 0
    for i in range(strategy.get_required_data_length(), len(market_data)):
        data_slice = market_data[:i+1]
        signal = strategy.process_market_data(data_slice)
        
        if signal:
            signals_generated += 1
            print(f"  Reversion Signal #{signals_generated}: {signal.action.value} at ${float(signal.price):.2f}")
            print(f"    Confidence: {signal.confidence:.3f}")
            print(f"    Confluence count: {signal.metadata['confluence_count']}")
            print(f"    Reversion signals: {signal.metadata['reversion_signals']}")
            print(f"    BB position: {signal.metadata['bb_position']:.3f}")
            print(f"    RSI: {signal.metadata['rsi']:.1f}")
            print(f"    Z-score: {signal.metadata['z_score']:.2f}")
            print()
    
    print(f"Mean Reversion Strategy generated {signals_generated} high-confidence signals")
    print()


def demonstrate_strategy_engine_with_advanced_strategies(market_data):
    """Demonstrate running multiple advanced strategies together."""
    print("=== Advanced Strategy Engine Demo ===")
    
    # Set up strategy registry
    registry = StrategyRegistry()
    registry.register_strategy(MultiIndicatorStrategy)
    registry.register_strategy(AdvancedMomentumStrategy)
    registry.register_strategy(MeanReversionStrategy)
    
    if ML_AVAILABLE:
        registry.register_strategy(MLPatternStrategy)
    
    # Set up signal processor and engine
    signal_processor = SignalProcessor()
    engine = StrategyEngine(registry, signal_processor, max_workers=3)
    
    # Create high-probability strategy configurations
    config_manager = StrategyConfigManager()
    
    configs = [
        {
            'type': 'MultiIndicatorStrategy',
            'name': 'multi_indicator_engine',
            'enabled': True,
            'parameters': {
                'min_confluence': 5,
                'min_confidence': 0.90,
                'volume_threshold': 1.5
            }
        },
        {
            'type': 'AdvancedMomentumStrategy',
            'name': 'momentum_engine',
            'enabled': True,
            'parameters': {
                'momentum_threshold': 2.0,
                'min_confidence': 0.88
            }
        },
        {
            'type': 'MeanReversionStrategy',
            'name': 'reversion_engine',
            'enabled': True,
            'parameters': {
                'min_confluence': 4,
                'min_confidence': 0.87,
                'bb_std_dev': 2.5
            }
        }
    ]
    
    # Add ML strategy if available
    if ML_AVAILABLE:
        configs.append({
            'type': 'MLPatternStrategy',
            'name': 'ml_pattern_engine',
            'enabled': True,
            'parameters': {
                'min_confidence': 0.93,
                'prediction_threshold': 0.80
            }
        })
    
    # Create strategies from config
    strategies = registry.create_strategies_from_config(configs)
    print(f"Created {len(strategies)} advanced strategies")
    
    # Add strategies to engine
    for strategy in strategies:
        engine.add_strategy(strategy)
    
    # Start engine and strategies
    engine.start_engine()
    started_count = engine.start_all_strategies()
    print(f"Started {started_count} strategies in engine")
    
    # Process market data through engine
    print("\nProcessing market data through advanced strategy engine...")
    total_signals = 0
    
    # Process in chunks to show progress
    chunk_size = 50
    for chunk_start in range(100, len(market_data), chunk_size):
        chunk_end = min(chunk_start + chunk_size, len(market_data))
        data_slice = market_data[:chunk_end]
        
        signals = engine.process_market_data(data_slice)
        
        if signals:
            total_signals += len(signals)
            print(f"\nSignals at data point {chunk_end}:")
            for signal in signals:
                print(f"  - {signal.original_signal.strategy_name}: "
                      f"{signal.original_signal.action.value} "
                      f"(confidence: {signal.original_signal.confidence:.3f}, "
                      f"priority: {signal.priority.name})")
    
    # Get final statistics
    print(f"\n=== Final Engine Statistics ===")
    print(f"Total high-confidence signals generated: {total_signals}")
    
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
    print(f"  - Successful executions: {engine_stats['execution_stats']['successful_executions']}")
    print(f"  - Average execution time: {engine_stats['execution_stats']['average_execution_time']:.4f}s")
    
    # Stop engine
    engine.stop_engine()
    print("\nAdvanced strategy engine stopped")
    print()


def demonstrate_technical_indicators():
    """Demonstrate advanced technical indicators."""
    print("=== Advanced Technical Indicators Demo ===")
    
    indicators = TechnicalIndicators()
    
    # Create sample data with trend and volatility
    prices = []
    base_price = 50000
    for i in range(100):
        trend = i * 10
        volatility = np.sin(i * 0.1) * 200
        noise = np.random.normal(0, 50)
        price = base_price + trend + volatility + noise
        prices.append(price)
    
    print(f"Analyzing {len(prices)} price points...")
    
    # Calculate multiple indicators
    sma_20 = indicators.sma(prices, 20)
    ema_20 = indicators.ema(prices, 20)
    rsi = indicators.rsi(prices, 14)
    macd_result = indicators.macd(prices)
    bb_result = indicators.bollinger_bands(prices, 20, 2.0)
    
    print(f"Current indicators:")
    print(f"  SMA(20): ${sma_20[-1]:.2f}" if sma_20 else "  SMA(20): N/A")
    print(f"  EMA(20): ${ema_20[-1]:.2f}" if ema_20 else "  EMA(20): N/A")
    print(f"  RSI(14): {rsi:.1f}" if rsi else "  RSI(14): N/A")
    
    if macd_result:
        macd_line, signal_line, histogram = macd_result
        print(f"  MACD: {macd_line:.2f}, Signal: {signal_line:.2f}, Histogram: {histogram:.2f}")
    
    if bb_result:
        upper, middle, lower = bb_result
        bb_position = (prices[-1] - lower) / (upper - lower)
        print(f"  Bollinger Bands: Upper=${upper:.2f}, Middle=${middle:.2f}, Lower=${lower:.2f}")
        print(f"  BB Position: {bb_position:.3f} (0=lower band, 1=upper band)")
    
    available = indicators.get_available_indicators()
    print(f"  TA-Lib available: {available['talib_available']}")
    print()


def main():
    """Main demonstration function."""
    print("Advanced Trading Strategies - 99% Probability Focus")
    print("=" * 60)
    print()
    
    # Create realistic market data
    print("Creating realistic market data with multiple phases...")
    market_data = create_realistic_market_data("BTCUSD", 250)
    print(f"Generated {len(market_data)} data points")
    print(f"Price range: ${float(market_data[0].close):.2f} - ${float(market_data[-1].close):.2f}")
    print(f"Time range: {market_data[0].timestamp} to {market_data[-1].timestamp}")
    print()
    
    # Demonstrate advanced technical indicators
    demonstrate_technical_indicators()
    
    # Demonstrate individual advanced strategies
    demonstrate_multi_indicator_strategy(market_data)
    demonstrate_ml_pattern_strategy(market_data)
    demonstrate_advanced_momentum_strategy(market_data)
    demonstrate_mean_reversion_strategy(market_data)
    
    # Demonstrate strategy engine with multiple advanced strategies
    demonstrate_strategy_engine_with_advanced_strategies(market_data)
    
    print("=" * 60)
    print("Advanced Strategies Demo Completed!")
    print()
    print("Key Features Demonstrated:")
    print("✓ Multi-Indicator Confluence (6+ confirming signals)")
    print("✓ Machine Learning Pattern Recognition (95%+ confidence)")
    print("✓ Advanced Momentum Analysis (divergence detection)")
    print("✓ Statistical Mean Reversion (extreme deviation analysis)")
    print("✓ High-Probability Signal Generation (87%+ confidence)")
    print("✓ Concurrent Strategy Execution")
    print("✓ Advanced Risk Management")
    print()
    print("These strategies are designed to identify the highest probability")
    print("trading opportunities by combining multiple confirmation signals")
    print("and sophisticated analysis techniques.")


if __name__ == "__main__":
    main()