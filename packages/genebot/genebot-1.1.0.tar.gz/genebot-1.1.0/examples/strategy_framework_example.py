"""
Example demonstrating the strategy framework usage.
"""

import sys
import os
from datetime import datetime
from typing import List, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.strategies import BaseStrategy, StrategyEngine, StrategyRegistry, SignalProcessor
from src.strategies.base_strategy import StrategyConfig
from src.models.data_models import MarketData, TradingSignal


class SimpleMovingAverageStrategy(BaseStrategy):
    """
    Example strategy implementing simple moving average crossover.
    """
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.short_period = self.parameters.get('short_period', 10)
        self.long_period = self.parameters.get('long_period', 20)
        
    def initialize(self) -> bool:
        """Initialize the strategy."""
        self.logger.info(f"Initializing MA strategy with periods {self.short_period}/{self.long_period}")
        return True
        
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """Analyze market data using moving average crossover."""
        if len(market_data) < self.long_period:
            return None
            
        # Calculate moving averages
        short_ma = sum(data.close for data in market_data[-self.short_period:]) / self.short_period
        long_ma = sum(data.close for data in market_data[-self.long_period:]) / self.long_period
        
        # Previous MAs for crossover detection
        prev_short_ma = sum(data.close for data in market_data[-self.short_period-1:-1]) / self.short_period
        prev_long_ma = sum(data.close for data in market_data[-self.long_period-1:-1]) / self.long_period
        
        # Detect crossover
        current_cross = short_ma > long_ma
        prev_cross = prev_short_ma > prev_long_ma
        
        if current_cross and not prev_cross:
            # Bullish crossover
            return TradingSignal(
                symbol=market_data[-1].symbol,
                action="BUY",
                confidence=0.7,
                timestamp=datetime.now(),
                strategy_name=self.name,
                metadata={
                    'short_ma': short_ma,
                    'long_ma': long_ma,
                    'signal_type': 'bullish_crossover'
                }
            )
        elif not current_cross and prev_cross:
            # Bearish crossover
            return TradingSignal(
                symbol=market_data[-1].symbol,
                action="SELL",
                confidence=0.7,
                timestamp=datetime.now(),
                strategy_name=self.name,
                metadata={
                    'short_ma': short_ma,
                    'long_ma': long_ma,
                    'signal_type': 'bearish_crossover'
                }
            )
            
        return None
        
    def get_required_data_length(self) -> int:
        """Return required data length."""
        return self.long_period + 1
        
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        if self.short_period >= self.long_period:
            self.logger.error("Short period must be less than long period")
            return False
        if self.short_period < 1 or self.long_period < 1:
            self.logger.error("Periods must be positive")
            return False
        return True


def create_sample_market_data(symbol: str, count: int) -> List[MarketData]:
    """Create sample market data for testing."""
    import random
    
    data = []
    base_price = 50000.0
    
    for i in range(count):
        # Simulate price movement
        change = random.uniform(-0.02, 0.02)  # ±2% change
        base_price *= (1 + change)
        
        data.append(MarketData(
            symbol=symbol,
            timestamp=datetime.now(),
            open=base_price * 0.999,
            high=base_price * 1.001,
            low=base_price * 0.998,
            close=base_price,
            volume=random.uniform(100, 1000),
            exchange="example"
        ))
        
    return data


def main():
    """Demonstrate the strategy framework."""
    print("Strategy Framework Example")
    print("=" * 50)
    
    # 1. Create strategy registry and register strategies
    print("\n1. Setting up strategy registry...")
    registry = StrategyRegistry()
    registry.register_strategy(SimpleMovingAverageStrategy, "MovingAverage")
    
    print(f"Registered strategies: {registry.get_registered_strategies()}")
    
    # 2. Create signal processor
    print("\n2. Setting up signal processor...")
    signal_processor = SignalProcessor()
    
    # 3. Create strategy engine
    print("\n3. Setting up strategy engine...")
    engine = StrategyEngine(registry, signal_processor)
    
    # 4. Create strategy instances
    print("\n4. Creating strategy instances...")
    strategy_configs = [
        {
            'type': 'MovingAverage',
            'name': 'MA_10_20',
            'enabled': True,
            'parameters': {
                'short_period': 10,
                'long_period': 20
            }
        },
        {
            'type': 'MovingAverage', 
            'name': 'MA_5_15',
            'enabled': True,
            'parameters': {
                'short_period': 5,
                'long_period': 15
            }
        }
    ]
    
    strategies = registry.create_strategies_from_config(strategy_configs)
    
    # Add strategies to engine
    for strategy in strategies:
        engine.add_strategy(strategy)
        
    print(f"Added {len(strategies)} strategies to engine")
    
    # 5. Start engine and strategies
    print("\n5. Starting engine and strategies...")
    engine.start_engine()
    started_count = engine.start_all_strategies()
    print(f"Started {started_count} strategies")
    
    # 6. Generate sample market data and process
    print("\n6. Processing market data...")
    market_data = create_sample_market_data("BTCUSD", 50)
    
    # Process data multiple times to potentially generate signals
    total_signals = 0
    for i in range(5):
        # Add some new data points
        new_data = create_sample_market_data("BTCUSD", 5)
        market_data.extend(new_data)
        
        # Process through engine
        signals = engine.process_market_data(market_data[-30:])  # Use last 30 points
        
        if signals:
            print(f"\nIteration {i+1}: Generated {len(signals)} signals")
            for signal in signals:
                print(f"  - {signal.original_signal.action} {signal.original_signal.symbol} "
                      f"(confidence: {signal.confidence_adjusted:.2f}, "
                      f"priority: {signal.priority.name})")
            total_signals += len(signals)
        else:
            print(f"Iteration {i+1}: No signals generated")
    
    # 7. Show statistics
    print(f"\n7. Final Statistics:")
    print(f"Total signals generated: {total_signals}")
    
    # Engine stats
    engine_stats = engine.get_engine_stats()
    print(f"Engine stats: {engine_stats}")
    
    # Strategy status
    strategy_status = engine.get_strategy_status()
    for name, status in strategy_status.items():
        perf = status['performance']
        print(f"Strategy {name}: {perf['signals_generated']} signals, "
              f"success rate: {perf['success_rate']:.2%}")
    
    # Signal processor stats
    processor_stats = signal_processor.get_statistics()
    print(f"Signal processor stats: {processor_stats}")
    
    # 8. Clean up
    print("\n8. Shutting down...")
    engine.stop_engine()
    print("Strategy framework example completed!")


if __name__ == "__main__":
    main()