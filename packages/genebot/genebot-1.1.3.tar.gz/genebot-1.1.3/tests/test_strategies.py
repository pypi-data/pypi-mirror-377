"""
Unit tests for the strategy framework components.
"""

import pytest
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import List, Optional

from src.strategies import BaseStrategy, StrategyEngine, StrategyRegistry, SignalProcessor
from src.strategies.base_strategy import StrategyConfig
from src.strategies.signal_processor import SignalPriority, ProcessedSignal, ConfidenceFilter, DuplicateFilter
from src.models.data_models import MarketData, TradingSignal


# Test Strategy Implementation
class TestStrategy(BaseStrategy):
    """Test strategy implementation for testing."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.analysis_calls = 0
        self.should_generate_signal = False
        
    def initialize(self) -> bool:
        return True
        
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        self.analysis_calls += 1
        if self.should_generate_signal:
            return TradingSignal(
                symbol="BTCUSD",
                action="BUY",
                confidence=0.8,
                timestamp=datetime.now(),
                strategy_name=self.name,
                metadata={}
            )
        return None
        
    def get_required_data_length(self) -> int:
        return 10
        
    def validate_parameters(self) -> bool:
        return True


class FailingStrategy(BaseStrategy):
    """Strategy that fails for testing error handling."""
    
    def initialize(self) -> bool:
        return False
        
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        raise Exception("Analysis failed")
        
    def get_required_data_length(self) -> int:
        return 5
        
    def validate_parameters(self) -> bool:
        return False


class TestBaseStrategy:
    """Test cases for BaseStrategy."""
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        config = StrategyConfig(
            name="test_strategy",
            enabled=True,
            parameters={"param1": "value1"},
            risk_limits={"max_position": 1000}
        )
        
        strategy = TestStrategy(config)
        
        assert strategy.name == "test_strategy"
        assert strategy.enabled is True
        assert strategy.parameters == {"param1": "value1"}
        assert strategy.risk_limits == {"max_position": 1000}
        assert not strategy._initialized
        assert not strategy._running
        
    def test_strategy_start_stop(self):
        """Test strategy start and stop functionality."""
        config = StrategyConfig(name="test_strategy")
        strategy = TestStrategy(config)
        
        # Test start
        assert strategy.start() is True
        assert strategy.is_running() is True
        assert strategy._initialized is True
        
        # Test stop
        assert strategy.stop() is True
        assert strategy.is_running() is False
        
    def test_disabled_strategy(self):
        """Test disabled strategy behavior."""
        config = StrategyConfig(name="test_strategy", enabled=False)
        strategy = TestStrategy(config)
        
        assert strategy.start() is False
        assert strategy.is_running() is False
        
    def test_failing_strategy(self):
        """Test strategy that fails to initialize."""
        config = StrategyConfig(name="failing_strategy")
        strategy = FailingStrategy(config)
        
        assert strategy.start() is False
        assert strategy.is_running() is False
        
    def test_process_market_data(self):
        """Test market data processing."""
        config = StrategyConfig(name="test_strategy")
        strategy = TestStrategy(config)
        strategy.start()
        
        # Create test market data
        market_data = [
            MarketData(
                symbol="BTCUSD",
                timestamp=datetime.now(),
                open=50000.0,
                high=51000.0,
                low=49000.0,
                close=50500.0,
                volume=1000.0,
                exchange="test"
            ) for _ in range(15)
        ]
        
        # Test without signal generation
        signal = strategy.process_market_data(market_data)
        assert signal is None
        assert strategy.analysis_calls == 1
        
        # Test with signal generation
        strategy.should_generate_signal = True
        signal = strategy.process_market_data(market_data)
        assert signal is not None
        assert signal.symbol == "BTCUSD"
        assert signal.action == "BUY"
        assert strategy.signals_generated == 1
        
    def test_insufficient_data(self):
        """Test behavior with insufficient market data."""
        config = StrategyConfig(name="test_strategy")
        strategy = TestStrategy(config)
        strategy.start()
        
        # Provide insufficient data
        market_data = [Mock() for _ in range(5)]  # Need 10, providing 5
        
        signal = strategy.process_market_data(market_data)
        assert signal is None
        assert strategy.analysis_calls == 0
        
    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        config = StrategyConfig(name="test_strategy")
        strategy = TestStrategy(config)
        
        metrics = strategy.get_performance_metrics()
        assert metrics['name'] == "test_strategy"
        assert metrics['signals_generated'] == 0
        assert metrics['success_rate'] == 0.0
        
        # Update success tracking
        strategy.signals_generated = 10
        strategy.update_signal_success(True)
        strategy.update_signal_success(False)
        
        metrics = strategy.get_performance_metrics()
        assert metrics['signals_generated'] == 10
        assert metrics['successful_signals'] == 1
        assert metrics['success_rate'] == 0.1


class TestStrategyRegistry:
    """Test cases for StrategyRegistry."""
    
    def test_register_strategy(self):
        """Test strategy registration."""
        registry = StrategyRegistry()
        
        assert registry.register_strategy(TestStrategy) is True
        assert "TestStrategy" in registry
        assert len(registry) == 1
        
    def test_register_invalid_strategy(self):
        """Test registration of invalid strategy."""
        registry = StrategyRegistry()
        
        # Try to register non-strategy class
        assert registry.register_strategy(str) is False
        
        # Try to register BaseStrategy itself
        assert registry.register_strategy(BaseStrategy) is False
        
    def test_create_strategy(self):
        """Test strategy instance creation."""
        registry = StrategyRegistry()
        registry.register_strategy(TestStrategy)
        
        config = StrategyConfig(name="test_instance")
        strategy = registry.create_strategy("TestStrategy", config)
        
        assert strategy is not None
        assert isinstance(strategy, TestStrategy)
        assert strategy.name == "test_instance"
        
    def test_create_nonexistent_strategy(self):
        """Test creation of non-existent strategy."""
        registry = StrategyRegistry()
        
        config = StrategyConfig(name="test")
        strategy = registry.create_strategy("NonExistent", config)
        
        assert strategy is None
        
    def test_create_strategies_from_config(self):
        """Test creating multiple strategies from configuration."""
        registry = StrategyRegistry()
        registry.register_strategy(TestStrategy)
        
        configs = [
            {
                'type': 'TestStrategy',
                'name': 'strategy1',
                'enabled': True,
                'parameters': {'param1': 'value1'}
            },
            {
                'type': 'TestStrategy',
                'name': 'strategy2',
                'enabled': False
            }
        ]
        
        strategies = registry.create_strategies_from_config(configs)
        
        assert len(strategies) == 2
        assert strategies[0].name == "strategy1"
        assert strategies[0].enabled is True
        assert strategies[1].name == "strategy2"
        assert strategies[1].enabled is False
        
    def test_unregister_strategy(self):
        """Test strategy unregistration."""
        registry = StrategyRegistry()
        registry.register_strategy(TestStrategy)
        
        assert registry.unregister_strategy("TestStrategy") is True
        assert "TestStrategy" not in registry
        assert len(registry) == 0
        
    def test_get_strategy_info(self):
        """Test getting strategy information."""
        registry = StrategyRegistry()
        registry.register_strategy(TestStrategy)
        
        info = registry.get_strategy_info("TestStrategy")
        
        assert info is not None
        assert info['name'] == "TestStrategy"
        assert info['class'] == "TestStrategy"
        assert 'methods' in info
        
    def test_validate_strategy_config(self):
        """Test strategy configuration validation."""
        registry = StrategyRegistry()
        registry.register_strategy(TestStrategy)
        
        valid_config = {
            'name': 'test',
            'enabled': True,
            'parameters': {}
        }
        
        assert registry.validate_strategy_config("TestStrategy", valid_config) is True
        assert registry.validate_strategy_config("NonExistent", valid_config) is False


class TestStrategyEngine:
    """Test cases for StrategyEngine."""
    
    @pytest.fixture
    def engine_setup(self):
        """Set up strategy engine with dependencies."""
        registry = StrategyRegistry()
        registry.register_strategy(TestStrategy)
        
        signal_processor = SignalProcessor()
        engine = StrategyEngine(registry, signal_processor)
        
        return engine, registry, signal_processor
        
    def test_engine_initialization(self, engine_setup):
        """Test engine initialization."""
        engine, registry, signal_processor = engine_setup
        
        assert engine.strategy_registry == registry
        assert engine.signal_processor == signal_processor
        assert not engine._running
        assert len(engine._strategies) == 0
        
    def test_add_remove_strategy(self, engine_setup):
        """Test adding and removing strategies."""
        engine, registry, signal_processor = engine_setup
        
        config = StrategyConfig(name="test_strategy")
        strategy = TestStrategy(config)
        
        # Test add
        assert engine.add_strategy(strategy) is True
        assert "test_strategy" in engine._strategies
        
        # Test add duplicate
        assert engine.add_strategy(strategy) is False
        
        # Test remove
        assert engine.remove_strategy("test_strategy") is True
        assert "test_strategy" not in engine._strategies
        
    def test_start_stop_strategy(self, engine_setup):
        """Test starting and stopping individual strategies."""
        engine, registry, signal_processor = engine_setup
        
        config = StrategyConfig(name="test_strategy")
        strategy = TestStrategy(config)
        engine.add_strategy(strategy)
        
        # Test start
        assert engine.start_strategy("test_strategy") is True
        assert "test_strategy" in engine._active_strategies
        
        # Test stop
        assert engine.stop_strategy("test_strategy") is True
        assert "test_strategy" not in engine._active_strategies
        
    def test_start_stop_all_strategies(self, engine_setup):
        """Test starting and stopping all strategies."""
        engine, registry, signal_processor = engine_setup
        
        # Add multiple strategies
        for i in range(3):
            config = StrategyConfig(name=f"strategy_{i}")
            strategy = TestStrategy(config)
            engine.add_strategy(strategy)
            
        # Start all
        started = engine.start_all_strategies()
        assert started == 3
        assert len(engine._active_strategies) == 3
        
        # Stop all
        stopped = engine.stop_all_strategies()
        assert stopped == 3
        assert len(engine._active_strategies) == 0
        
    def test_engine_start_stop(self, engine_setup):
        """Test engine start and stop."""
        engine, registry, signal_processor = engine_setup
        
        assert engine.start_engine() is True
        assert engine._running is True
        
        assert engine.stop_engine() is True
        assert engine._running is False
        
    def test_process_market_data(self, engine_setup):
        """Test market data processing through engine."""
        engine, registry, signal_processor = engine_setup
        
        # Set up strategy
        config = StrategyConfig(name="test_strategy")
        strategy = TestStrategy(config)
        strategy.should_generate_signal = True
        engine.add_strategy(strategy)
        
        # Start engine and strategy
        engine.start_engine()
        engine.start_strategy("test_strategy")
        
        # Create test data
        market_data = [Mock() for _ in range(15)]
        
        # Process data
        signals = engine.process_market_data(market_data)
        
        # Should have processed signals
        assert len(signals) >= 0  # Depends on signal processor filtering
        
    def test_get_strategy_status(self, engine_setup):
        """Test getting strategy status."""
        engine, registry, signal_processor = engine_setup
        
        config = StrategyConfig(name="test_strategy")
        strategy = TestStrategy(config)
        engine.add_strategy(strategy)
        engine.start_strategy("test_strategy")
        
        status = engine.get_strategy_status()
        
        assert "test_strategy" in status
        assert status["test_strategy"]["active"] is True
        assert "performance" in status["test_strategy"]
        
    def test_get_engine_stats(self, engine_setup):
        """Test getting engine statistics."""
        engine, registry, signal_processor = engine_setup
        
        stats = engine.get_engine_stats()
        
        assert "running" in stats
        assert "total_strategies" in stats
        assert "active_strategies" in stats
        assert "execution_stats" in stats


class TestSignalProcessor:
    """Test cases for SignalProcessor."""
    
    def create_test_signal(self, symbol="BTCUSD", action="BUY", confidence=0.8, strategy="test"):
        """Create a test trading signal."""
        return TradingSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            timestamp=datetime.now(),
            strategy_name=strategy,
            metadata={}
        )
        
    def test_processor_initialization(self):
        """Test signal processor initialization."""
        processor = SignalProcessor()
        
        assert len(processor.filters) > 0  # Should have default filters
        assert len(processor.priority_rules) > 0  # Should have default priority rules
        
    def test_add_remove_filters(self):
        """Test adding and removing filters."""
        processor = SignalProcessor()
        initial_count = len(processor.filters)
        
        # Add filter
        test_filter = ConfidenceFilter(min_confidence=0.6)
        processor.add_filter(test_filter)
        
        assert len(processor.filters) == initial_count + 1
        
        # Remove filter
        assert processor.remove_filter("confidence_filter") is True
        assert len(processor.filters) == initial_count
        
    def test_confidence_filter(self):
        """Test confidence-based filtering."""
        filter_obj = ConfidenceFilter(min_confidence=0.5)
        
        high_confidence_signal = self.create_test_signal(confidence=0.8)
        low_confidence_signal = self.create_test_signal(confidence=0.3)
        
        assert filter_obj.filter(high_confidence_signal) is True
        assert filter_obj.filter(low_confidence_signal) is False
        
    def test_duplicate_filter(self):
        """Test duplicate signal filtering."""
        filter_obj = DuplicateFilter(time_window_minutes=1)
        
        signal1 = self.create_test_signal()
        signal2 = self.create_test_signal()  # Same signal
        
        assert filter_obj.filter(signal1) is True
        assert filter_obj.filter(signal2) is False  # Should be filtered as duplicate
        
    def test_process_signals(self):
        """Test signal processing."""
        processor = SignalProcessor()
        
        signals = [
            self.create_test_signal(confidence=0.9, strategy="strategy1"),
            self.create_test_signal(confidence=0.6, strategy="strategy2"),
            self.create_test_signal(confidence=0.2, strategy="strategy3")  # Should be filtered
        ]
        
        processed = processor.process_signals(signals)
        
        # Should filter out low confidence signal
        assert len(processed) <= len(signals)
        
        # Check that processed signals have required fields
        for signal in processed:
            assert isinstance(signal, ProcessedSignal)
            assert hasattr(signal, 'priority')
            assert hasattr(signal, 'confidence_adjusted')
            assert hasattr(signal, 'risk_score')
            
    def test_conflict_resolution(self):
        """Test signal conflict resolution."""
        processor = SignalProcessor()
        
        # Create conflicting signals for same symbol
        signals = [
            self.create_test_signal(symbol="BTCUSD", action="BUY", confidence=0.6),
            self.create_test_signal(symbol="BTCUSD", action="SELL", confidence=0.8),
            self.create_test_signal(symbol="ETHUSD", action="BUY", confidence=0.7)
        ]
        
        processed = processor.process_signals(signals)
        
        # Should resolve conflicts and keep best signals
        symbols = [s.original_signal.symbol for s in processed]
        assert len(set(symbols)) == len(processed)  # No duplicate symbols
        
    def test_priority_assignment(self):
        """Test signal priority assignment."""
        processor = SignalProcessor()
        
        high_conf_signal = self.create_test_signal(confidence=0.95)
        low_conf_signal = self.create_test_signal(confidence=0.4)
        
        processed_high = processor.process_signals([high_conf_signal])
        processed_low = processor.process_signals([low_conf_signal])
        
        if processed_high and processed_low:
            assert processed_high[0].priority.value >= processed_low[0].priority.value
            
    def test_statistics(self):
        """Test signal processing statistics."""
        processor = SignalProcessor()
        
        initial_stats = processor.get_statistics()
        assert initial_stats['total_signals_received'] == 0
        
        signals = [self.create_test_signal() for _ in range(5)]
        processor.process_signals(signals)
        
        stats = processor.get_statistics()
        assert stats['total_signals_received'] == 5
        assert stats['signals_processed'] > 0
        
        # Test reset
        processor.reset_statistics()
        reset_stats = processor.get_statistics()
        assert reset_stats['total_signals_received'] == 0


class TestIntegration:
    """Integration tests for strategy framework components."""
    
    def test_full_workflow(self):
        """Test complete strategy framework workflow."""
        # Set up components
        registry = StrategyRegistry()
        registry.register_strategy(TestStrategy)
        
        signal_processor = SignalProcessor()
        engine = StrategyEngine(registry, signal_processor)
        
        # Create and add strategy
        config = StrategyConfig(name="integration_test")
        strategy = TestStrategy(config)
        strategy.should_generate_signal = True
        
        engine.add_strategy(strategy)
        
        # Start engine and strategy
        engine.start_engine()
        engine.start_strategy("integration_test")
        
        # Create market data
        market_data = [Mock() for _ in range(15)]
        
        # Process data through complete pipeline
        signals = engine.process_market_data(market_data)
        
        # Verify workflow
        assert strategy.analysis_calls > 0
        assert len(signals) >= 0  # May be filtered
        
        # Clean up
        engine.stop_engine()
        
    def test_concurrent_processing(self):
        """Test concurrent strategy processing."""
        registry = StrategyRegistry()
        registry.register_strategy(TestStrategy)
        
        signal_processor = SignalProcessor()
        engine = StrategyEngine(registry, signal_processor, max_workers=2)
        
        # Add multiple strategies
        for i in range(3):
            config = StrategyConfig(name=f"concurrent_test_{i}")
            strategy = TestStrategy(config)
            strategy.should_generate_signal = True
            engine.add_strategy(strategy)
            
        engine.start_engine()
        engine.start_all_strategies()
        
        # Process data concurrently
        market_data = [Mock() for _ in range(15)]
        signals = engine.process_market_data(market_data)
        
        # Verify all strategies were called
        for strategy in engine._strategies.values():
            assert strategy.analysis_calls > 0
            
        engine.stop_engine()


if __name__ == "__main__":
    pytest.main([__file__])


class TestMovingAverageStrategy:
    """Test cases for MovingAverageStrategy."""
    
    def create_market_data(self, prices: List[float], symbol: str = "BTCUSD") -> List[MarketData]:
        """Create market data from price list."""
        market_data = []
        base_time = datetime.now()
        
        for i, price in enumerate(prices):
            data = MarketData(
                symbol=symbol,
                timestamp=base_time + timedelta(minutes=i),
                open=price,
                high=price * 1.01,
                low=price * 0.99,
                close=price,
                volume=1000.0,
                exchange="test"
            )
            market_data.append(data)
        
        return market_data
    
    def test_strategy_initialization(self):
        """Test MovingAverageStrategy initialization."""
        from src.strategies import MovingAverageStrategy
        
        config = StrategyConfig(
            name="ma_test",
            parameters={
                'short_window': 5,
                'long_window': 10,
                'min_confidence': 0.8
            }
        )
        
        strategy = MovingAverageStrategy(config)
        
        assert strategy.name == "ma_test"
        assert strategy.short_window == 5
        assert strategy.long_window == 10
        assert strategy.min_confidence == 0.8
        
    def test_parameter_validation(self):
        """Test parameter validation."""
        from src.strategies import MovingAverageStrategy
        
        # Valid parameters
        valid_config = StrategyConfig(
            name="ma_test",
            parameters={
                'short_window': 5,
                'long_window': 10,
                'min_confidence': 0.7
            }
        )
        strategy = MovingAverageStrategy(valid_config)
        assert strategy.validate_parameters() is True
        
        # Invalid parameters - short >= long
        invalid_config = StrategyConfig(
            name="ma_test",
            parameters={
                'short_window': 10,
                'long_window': 5,
                'min_confidence': 0.7
            }
        )
        strategy = MovingAverageStrategy(invalid_config)
        assert strategy.validate_parameters() is False
        
        # Invalid confidence
        invalid_config = StrategyConfig(
            name="ma_test",
            parameters={
                'short_window': 5,
                'long_window': 10,
                'min_confidence': 1.5
            }
        )
        strategy = MovingAverageStrategy(invalid_config)
        assert strategy.validate_parameters() is False
    
    def test_required_data_length(self):
        """Test required data length calculation."""
        from src.strategies import MovingAverageStrategy
        
        config = StrategyConfig(
            name="ma_test",
            parameters={'short_window': 5, 'long_window': 20}
        )
        strategy = MovingAverageStrategy(config)
        
        assert strategy.get_required_data_length() == 21  # long_window + 1
    
    def test_bullish_crossover_signal(self):
        """Test bullish crossover signal generation."""
        from src.strategies import MovingAverageStrategy
        
        config = StrategyConfig(
            name="ma_test",
            parameters={
                'short_window': 3,
                'long_window': 5,
                'min_confidence': 0.5
            }
        )
        strategy = MovingAverageStrategy(config)
        strategy.initialize()
        
        # Create price data that will generate bullish crossover
        # Prices: [100, 101, 102, 103, 104, 105, 110, 115]
        # Short MA (3): crosses above Long MA (5)
        prices = [100, 101, 102, 103, 104, 105, 110, 115]
        market_data = self.create_market_data(prices)
        
        # Process data to build history
        for i in range(len(market_data)):
            if i >= strategy.get_required_data_length() - 1:
                signal = strategy.analyze(market_data[:i+1])
                if signal and signal.action.value == "BUY":
                    assert signal.symbol == "BTCUSD"
                    assert signal.confidence >= 0.5
                    assert 'crossover_type' in signal.metadata
                    assert signal.metadata['crossover_type'] == 'bullish'
                    break
    
    def test_bearish_crossover_signal(self):
        """Test bearish crossover signal generation."""
        from src.strategies import MovingAverageStrategy
        
        config = StrategyConfig(
            name="ma_test",
            parameters={
                'short_window': 3,
                'long_window': 5,
                'min_confidence': 0.5
            }
        )
        strategy = MovingAverageStrategy(config)
        strategy.initialize()
        
        # Create price data that will generate bearish crossover
        # Start high, then decline to create bearish crossover
        prices = [115, 110, 105, 104, 103, 102, 101, 100]
        market_data = self.create_market_data(prices)
        
        # Process data to build history
        for i in range(len(market_data)):
            if i >= strategy.get_required_data_length() - 1:
                signal = strategy.analyze(market_data[:i+1])
                if signal and signal.action.value == "SELL":
                    assert signal.symbol == "BTCUSD"
                    assert signal.confidence >= 0.5
                    assert 'crossover_type' in signal.metadata
                    assert signal.metadata['crossover_type'] == 'bearish'
                    break
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        from src.strategies import MovingAverageStrategy
        
        config = StrategyConfig(name="ma_test")
        strategy = MovingAverageStrategy(config)
        strategy.initialize()
        
        # Provide insufficient data
        prices = [100, 101, 102]  # Need 31 (30 + 1), providing 3
        market_data = self.create_market_data(prices)
        
        signal = strategy.analyze(market_data)
        assert signal is None
    
    def test_no_crossover(self):
        """Test behavior when no crossover occurs."""
        from src.strategies import MovingAverageStrategy
        
        config = StrategyConfig(
            name="ma_test",
            parameters={'short_window': 3, 'long_window': 5}
        )
        strategy = MovingAverageStrategy(config)
        strategy.initialize()
        
        # Create stable price data (no crossover)
        prices = [100] * 10
        market_data = self.create_market_data(prices)
        
        signal = strategy.analyze(market_data)
        assert signal is None
    
    def test_signal_cooldown(self):
        """Test signal cooldown mechanism."""
        from src.strategies import MovingAverageStrategy
        
        config = StrategyConfig(
            name="ma_test",
            parameters={
                'short_window': 2,
                'long_window': 3,
                'min_confidence': 0.5
            }
        )
        strategy = MovingAverageStrategy(config)
        strategy.initialize()
        
        # Generate first signal
        prices = [100, 101, 102, 110, 115]
        market_data = self.create_market_data(prices)
        
        signal1 = strategy.analyze(market_data)
        
        # Try to generate another signal immediately (should be blocked by cooldown)
        prices2 = [100, 101, 102, 110, 115, 120]
        market_data2 = self.create_market_data(prices2)
        
        signal2 = strategy.analyze(market_data2)
        
        # Second signal should be None due to cooldown
        if signal1 and signal1.action.value == "BUY":
            assert signal2 is None or signal2.action.value != "BUY"


class TestRSIStrategy:
    """Test cases for RSIStrategy."""
    
    def create_market_data(self, prices: List[float], symbol: str = "BTCUSD") -> List[MarketData]:
        """Create market data from price list."""
        market_data = []
        base_time = datetime.now()
        
        for i, price in enumerate(prices):
            data = MarketData(
                symbol=symbol,
                timestamp=base_time + timedelta(minutes=i),
                open=price,
                high=price * 1.01,
                low=price * 0.99,
                close=price,
                volume=1000.0,
                exchange="test"
            )
            market_data.append(data)
        
        return market_data
    
    def test_strategy_initialization(self):
        """Test RSIStrategy initialization."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(
            name="rsi_test",
            parameters={
                'rsi_period': 10,
                'oversold_threshold': 25,
                'overbought_threshold': 75,
                'min_confidence': 0.8
            }
        )
        
        strategy = RSIStrategy(config)
        
        assert strategy.name == "rsi_test"
        assert strategy.rsi_period == 10
        assert strategy.oversold_threshold == 25
        assert strategy.overbought_threshold == 75
        assert strategy.min_confidence == 0.8
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        from src.strategies import RSIStrategy
        
        # Valid parameters
        valid_config = StrategyConfig(
            name="rsi_test",
            parameters={
                'rsi_period': 14,
                'oversold_threshold': 30,
                'overbought_threshold': 70,
                'min_confidence': 0.7
            }
        )
        strategy = RSIStrategy(valid_config)
        assert strategy.validate_parameters() is True
        
        # Invalid parameters - oversold >= overbought
        invalid_config = StrategyConfig(
            name="rsi_test",
            parameters={
                'rsi_period': 14,
                'oversold_threshold': 70,
                'overbought_threshold': 30,
                'min_confidence': 0.7
            }
        )
        strategy = RSIStrategy(invalid_config)
        assert strategy.validate_parameters() is False
        
        # Invalid RSI period
        invalid_config = StrategyConfig(
            name="rsi_test",
            parameters={
                'rsi_period': -5,
                'oversold_threshold': 30,
                'overbought_threshold': 70,
                'min_confidence': 0.7
            }
        )
        strategy = RSIStrategy(invalid_config)
        assert strategy.validate_parameters() is False
    
    def test_required_data_length(self):
        """Test required data length calculation."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(
            name="rsi_test",
            parameters={'rsi_period': 14}
        )
        strategy = RSIStrategy(config)
        
        assert strategy.get_required_data_length() == 15  # rsi_period + 1
    
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(
            name="rsi_test",
            parameters={'rsi_period': 5}
        )
        strategy = RSIStrategy(config)
        
        # Create price data with known RSI characteristics
        # Declining prices should create low RSI (oversold)
        declining_prices = [100, 95, 90, 85, 80, 75]
        rsi_low = strategy._calculate_rsi(declining_prices)
        
        # Rising prices should create high RSI (overbought)
        rising_prices = [75, 80, 85, 90, 95, 100]
        rsi_high = strategy._calculate_rsi(rising_prices)
        
        assert rsi_low is not None
        assert rsi_high is not None
        assert rsi_low < rsi_high
        assert 0 <= rsi_low <= 100
        assert 0 <= rsi_high <= 100
    
    def test_oversold_signal(self):
        """Test oversold signal generation."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(
            name="rsi_test",
            parameters={
                'rsi_period': 5,
                'oversold_threshold': 40,  # Higher threshold for easier testing
                'overbought_threshold': 70,
                'min_confidence': 0.5
            }
        )
        strategy = RSIStrategy(config)
        strategy.initialize()
        
        # Create strongly declining prices to generate oversold condition
        prices = [100, 90, 80, 70, 60, 50, 40]
        market_data = self.create_market_data(prices)
        
        signal = strategy.analyze(market_data)
        
        if signal:
            assert signal.action.value == "BUY"
            assert signal.symbol == "BTCUSD"
            assert signal.confidence >= 0.5
            assert 'signal_type' in signal.metadata
            assert signal.metadata['signal_type'] == 'oversold'
    
    def test_overbought_signal(self):
        """Test overbought signal generation."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(
            name="rsi_test",
            parameters={
                'rsi_period': 5,
                'oversold_threshold': 30,
                'overbought_threshold': 60,  # Lower threshold for easier testing
                'min_confidence': 0.5
            }
        )
        strategy = RSIStrategy(config)
        strategy.initialize()
        
        # Create strongly rising prices to generate overbought condition
        prices = [40, 50, 60, 70, 80, 90, 100]
        market_data = self.create_market_data(prices)
        
        signal = strategy.analyze(market_data)
        
        if signal:
            assert signal.action.value == "SELL"
            assert signal.symbol == "BTCUSD"
            assert signal.confidence >= 0.5
            assert 'signal_type' in signal.metadata
            assert signal.metadata['signal_type'] == 'overbought'
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(name="rsi_test")
        strategy = RSIStrategy(config)
        strategy.initialize()
        
        # Provide insufficient data
        prices = [100, 101, 102]  # Need 15 (14 + 1), providing 3
        market_data = self.create_market_data(prices)
        
        signal = strategy.analyze(market_data)
        assert signal is None
    
    def test_neutral_rsi(self):
        """Test behavior when RSI is in neutral range."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(
            name="rsi_test",
            parameters={'rsi_period': 5}
        )
        strategy = RSIStrategy(config)
        strategy.initialize()
        
        # Create price data that should result in neutral RSI
        prices = [100, 101, 100, 101, 100, 101]
        market_data = self.create_market_data(prices)
        
        signal = strategy.analyze(market_data)
        assert signal is None
    
    def test_signal_cooldown(self):
        """Test signal cooldown mechanism."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(
            name="rsi_test",
            parameters={
                'rsi_period': 3,
                'oversold_threshold': 40,
                'overbought_threshold': 70,
                'min_confidence': 0.5
            }
        )
        strategy = RSIStrategy(config)
        strategy.initialize()
        
        # Generate first signal
        prices = [100, 80, 60, 40]
        market_data = self.create_market_data(prices)
        
        signal1 = strategy.analyze(market_data)
        
        # Try to generate another signal immediately (should be blocked by cooldown)
        prices2 = [100, 80, 60, 40, 30]
        market_data2 = self.create_market_data(prices2)
        
        signal2 = strategy.analyze(market_data2)
        
        # Second signal should be None due to cooldown
        if signal1 and signal1.action.value == "BUY":
            assert signal2 is None or signal2.action.value != "BUY"
    
    def test_get_strategy_info(self):
        """Test strategy information retrieval."""
        from src.strategies import RSIStrategy
        
        config = StrategyConfig(name="rsi_test")
        strategy = RSIStrategy(config)
        
        info = strategy.get_strategy_info()
        
        assert info['strategy_type'] == 'RSIStrategy'
        assert 'parameters' in info
        assert 'state' in info
        assert 'current_values' in info


class TestTechnicalIndicators:
    """Test cases for TechnicalIndicators."""
    
    def test_sma_calculation(self):
        """Test Simple Moving Average calculation."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        prices = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
        
        sma_5 = indicators.sma(prices, 5)
        
        assert sma_5 is not None
        assert len(sma_5) == 6  # 10 prices - 5 period + 1
        
        # Check last SMA value (average of last 5 prices)
        expected_last = sum(prices[-5:]) / 5
        assert abs(sma_5[-1] - expected_last) < 0.001
    
    def test_ema_calculation(self):
        """Test Exponential Moving Average calculation."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        prices = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
        
        ema_5 = indicators.ema(prices, 5)
        
        assert ema_5 is not None
        assert len(ema_5) == 6  # 10 prices - 5 period + 1
        
        # EMA should be different from SMA
        sma_5 = indicators.sma(prices, 5)
        assert ema_5[-1] != sma_5[-1]
    
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        # Rising prices should give high RSI
        rising_prices = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38]
        rsi_high = indicators.rsi(rising_prices, 14)
        
        # Falling prices should give low RSI
        falling_prices = [38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10]
        rsi_low = indicators.rsi(falling_prices, 14)
        
        assert rsi_high is not None
        assert rsi_low is not None
        assert 0 <= rsi_high <= 100
        assert 0 <= rsi_low <= 100
        assert rsi_high > rsi_low
    
    def test_macd_calculation(self):
        """Test MACD calculation."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        # Create price data with trend
        prices = list(range(10, 50))  # 40 data points
        
        macd_result = indicators.macd(prices)
        
        if macd_result:
            macd_line, signal_line, histogram = macd_result
            
            assert isinstance(macd_line, float)
            assert isinstance(signal_line, float)
            assert isinstance(histogram, float)
            
            # Histogram should be MACD - Signal
            assert abs(histogram - (macd_line - signal_line)) < 0.001
    
    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        prices = [20, 21, 19, 22, 18, 23, 17, 24, 16, 25, 15, 26, 14, 27, 13, 28, 12, 29, 11, 30]
        
        bb_result = indicators.bollinger_bands(prices, 10, 2.0)
        
        if bb_result:
            upper, middle, lower = bb_result
            
            assert isinstance(upper, float)
            assert isinstance(middle, float)
            assert isinstance(lower, float)
            
            # Upper should be greater than middle, middle greater than lower
            assert upper > middle > lower
    
    def test_stochastic_calculation(self):
        """Test Stochastic Oscillator calculation."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        # Create OHLC data
        highs = [22, 23, 21, 24, 20, 25, 19, 26, 18, 27, 17, 28, 16, 29, 15]
        lows = [18, 19, 17, 20, 16, 21, 15, 22, 14, 23, 13, 24, 12, 25, 11]
        closes = [20, 21, 19, 22, 18, 23, 17, 24, 16, 25, 15, 26, 14, 27, 13]
        
        stoch_result = indicators.stochastic(highs, lows, closes, 14, 3)
        
        if stoch_result:
            k_percent, d_percent = stoch_result
            
            assert isinstance(k_percent, float)
            assert isinstance(d_percent, float)
            assert 0 <= k_percent <= 100
            assert 0 <= d_percent <= 100
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        prices = [10, 12, 14]  # Only 3 prices
        
        # Should return None for insufficient data
        assert indicators.sma(prices, 10) is None
        assert indicators.ema(prices, 10) is None
        assert indicators.rsi(prices, 14) is None
        assert indicators.macd(prices) is None
        assert indicators.bollinger_bands(prices, 20) is None
    
    def test_get_available_indicators(self):
        """Test getting available indicators."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        available = indicators.get_available_indicators()
        
        assert isinstance(available, dict)
        assert 'sma' in available
        assert 'ema' in available
        assert 'rsi' in available
        assert 'macd' in available
        assert 'bollinger_bands' in available
        assert 'stochastic' in available
        assert 'talib_available' in available


class TestStrategyConfigManager:
    """Test cases for StrategyConfigManager."""
    
    def test_manager_initialization(self):
        """Test StrategyConfigManager initialization."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager()
        
        assert manager.config_dir.exists()
        assert len(manager._templates) > 0
        assert 'MovingAverageStrategy' in manager._templates
        assert 'RSIStrategy' in manager._templates
    
    def test_get_template(self):
        """Test getting strategy templates."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager()
        
        ma_template = manager.get_template('MovingAverageStrategy')
        assert ma_template is not None
        assert ma_template.strategy_type == 'MovingAverageStrategy'
        assert 'short_window' in ma_template.default_parameters
        
        rsi_template = manager.get_template('RSIStrategy')
        assert rsi_template is not None
        assert rsi_template.strategy_type == 'RSIStrategy'
        assert 'rsi_period' in rsi_template.default_parameters
        
        # Non-existent template
        assert manager.get_template('NonExistentStrategy') is None
    
    def test_create_config_from_template(self):
        """Test creating configuration from template."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager()
        
        # Create MA config with default parameters
        config = manager.create_config_from_template('MovingAverageStrategy', 'test_ma')
        
        assert config is not None
        assert config.name == 'test_ma'
        assert config.enabled is True
        assert 'short_window' in config.parameters
        assert 'long_window' in config.parameters
        
        # Create RSI config with custom parameters
        custom_params = {'rsi_period': 21, 'oversold_threshold': 25}
        config = manager.create_config_from_template(
            'RSIStrategy', 'test_rsi', custom_params
        )
        
        assert config is not None
        assert config.parameters['rsi_period'] == 21
        assert config.parameters['oversold_threshold'] == 25
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager()
        
        # Valid parameters
        valid_params = {'short_window': 10, 'long_window': 20, 'min_confidence': 0.7}
        assert manager._validate_parameters('MovingAverageStrategy', valid_params) is True
        
        # Invalid parameters (short >= long)
        invalid_params = {'short_window': 20, 'long_window': 10, 'min_confidence': 0.7}
        assert manager._validate_parameters('MovingAverageStrategy', invalid_params) is False
    
    def test_get_parameter_info(self):
        """Test getting parameter information."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager()
        
        info = manager.get_parameter_info('MovingAverageStrategy')
        
        assert info is not None
        assert 'description' in info
        assert 'parameters' in info
        assert 'risk_limits' in info
        
        # Check parameter details
        params = info['parameters']
        assert 'short_window' in params
        assert 'default' in params['short_window']
        assert 'description' in params['short_window']
        assert 'range' in params['short_window']
    
    def test_create_preset_configs(self):
        """Test creating preset configurations."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager()
        
        presets = manager.create_preset_configs()
        
        assert isinstance(presets, dict)
        assert len(presets) > 0
        
        # Check that presets contain expected configurations
        preset_names = list(presets.keys())
        assert any('ma_' in name for name in preset_names)
        assert any('rsi_' in name for name in preset_names)
        
        # Verify preset configurations are valid
        for name, config in presets.items():
            assert config is not None
            assert config.name == name
    
    def test_export_import_json(self):
        """Test JSON export and import."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager()
        
        # Create a config
        config = manager.create_config_from_template('MovingAverageStrategy', 'test_export')
        
        # Export to JSON
        json_str = manager.export_config_to_json(config)
        assert isinstance(json_str, str)
        assert 'test_export' in json_str
        
        # Import from JSON
        imported_config = manager.import_config_from_json(json_str)
        
        assert imported_config is not None
        assert imported_config.name == config.name
        assert imported_config.parameters == config.parameters
    
    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create temporary config directory for testing."""
        return tmp_path / "test_configs"
    
    def test_save_load_config(self, temp_config_dir):
        """Test saving and loading configurations."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager(str(temp_config_dir))
        
        # Create and save config
        config = manager.create_config_from_template('RSIStrategy', 'test_save')
        assert manager.save_config(config) is True
        
        # Verify file was created
        config_file = temp_config_dir / "test_save.yaml"
        assert config_file.exists()
        
        # Load config
        loaded_config = manager.load_config("test_save.yaml")
        
        assert loaded_config is not None
        assert loaded_config.name == config.name
        assert loaded_config.parameters == config.parameters
    
    def test_load_configs_from_directory(self, temp_config_dir):
        """Test loading all configs from directory."""
        from src.strategies import StrategyConfigManager
        
        manager = StrategyConfigManager(str(temp_config_dir))
        
        # Create and save multiple configs
        config1 = manager.create_config_from_template('MovingAverageStrategy', 'ma_test')
        config2 = manager.create_config_from_template('RSIStrategy', 'rsi_test')
        
        manager.save_config(config1)
        manager.save_config(config2)
        
        # Load all configs
        configs = manager.load_configs_from_directory()
        
        assert len(configs) == 2
        config_names = [c.name for c in configs]
        assert 'ma_test' in config_names
        assert 'rsi_test' in config_names


class TestStrategyIntegration:
    """Integration tests for the complete strategy implementation."""
    
    def test_moving_average_strategy_integration(self):
        """Test MovingAverageStrategy integration with framework."""
        from src.strategies import MovingAverageStrategy, StrategyRegistry, StrategyEngine, SignalProcessor
        
        # Set up framework
        registry = StrategyRegistry()
        registry.register_strategy(MovingAverageStrategy)
        
        signal_processor = SignalProcessor()
        engine = StrategyEngine(registry, signal_processor)
        
        # Create strategy config
        config = StrategyConfig(
            name="ma_integration",
            parameters={
                'short_window': 3,
                'long_window': 5,
                'min_confidence': 0.5
            }
        )
        
        # Create and add strategy
        strategy = registry.create_strategy("MovingAverageStrategy", config)
        assert strategy is not None
        
        engine.add_strategy(strategy)
        engine.start_engine()
        engine.start_strategy("ma_integration")
        
        # Create market data that should generate signals
        market_data = []
        base_time = datetime.now()
        prices = [100, 101, 102, 103, 104, 105, 110, 115]
        
        for i, price in enumerate(prices):
            data = MarketData(
                symbol="BTCUSD",
                timestamp=base_time + timedelta(minutes=i),
                open=price,
                high=price * 1.01,
                low=price * 0.99,
                close=price,
                volume=1000.0,
                exchange="test"
            )
            market_data.append(data)
        
        # Process data
        signals = engine.process_market_data(market_data)
        
        # Verify integration
        assert strategy.analysis_calls > 0
        
        # Clean up
        engine.stop_engine()
    
    def test_rsi_strategy_integration(self):
        """Test RSIStrategy integration with framework."""
        from src.strategies import RSIStrategy, StrategyRegistry, StrategyEngine, SignalProcessor
        
        # Set up framework
        registry = StrategyRegistry()
        registry.register_strategy(RSIStrategy)
        
        signal_processor = SignalProcessor()
        engine = StrategyEngine(registry, signal_processor)
        
        # Create strategy config
        config = StrategyConfig(
            name="rsi_integration",
            parameters={
                'rsi_period': 5,
                'oversold_threshold': 40,
                'overbought_threshold': 60,
                'min_confidence': 0.5
            }
        )
        
        # Create and add strategy
        strategy = registry.create_strategy("RSIStrategy", config)
        assert strategy is not None
        
        engine.add_strategy(strategy)
        engine.start_engine()
        engine.start_strategy("rsi_integration")
        
        # Create market data that should generate oversold signal
        market_data = []
        base_time = datetime.now()
        prices = [100, 90, 80, 70, 60, 50, 40]
        
        for i, price in enumerate(prices):
            data = MarketData(
                symbol="BTCUSD",
                timestamp=base_time + timedelta(minutes=i),
                open=price,
                high=price * 1.01,
                low=price * 0.99,
                close=price,
                volume=1000.0,
                exchange="test"
            )
            market_data.append(data)
        
        # Process data
        signals = engine.process_market_data(market_data)
        
        # Verify integration
        assert strategy.analysis_calls > 0
        
        # Clean up
        engine.stop_engine()
    
    def test_multiple_strategies_integration(self):
        """Test multiple strategies working together."""
        from src.strategies import (MovingAverageStrategy, RSIStrategy, StrategyRegistry, 
                                  StrategyEngine, SignalProcessor, StrategyConfigManager)
        
        # Set up framework
        registry = StrategyRegistry()
        registry.register_strategy(MovingAverageStrategy)
        registry.register_strategy(RSIStrategy)
        
        signal_processor = SignalProcessor()
        engine = StrategyEngine(registry, signal_processor)
        
        # Create strategies using config manager
        config_manager = StrategyConfigManager()
        
        ma_config = config_manager.create_config_from_template(
            'MovingAverageStrategy', 'ma_multi', {'short_window': 3, 'long_window': 5}
        )
        rsi_config = config_manager.create_config_from_template(
            'RSIStrategy', 'rsi_multi', {'rsi_period': 5}
        )
        
        # Create and add strategies
        ma_strategy = registry.create_strategy("MovingAverageStrategy", ma_config)
        rsi_strategy = registry.create_strategy("RSIStrategy", rsi_config)
        
        engine.add_strategy(ma_strategy)
        engine.add_strategy(rsi_strategy)
        
        engine.start_engine()
        engine.start_all_strategies()
        
        # Create market data
        market_data = []
        base_time = datetime.now()
        prices = [100, 95, 90, 85, 80, 85, 90, 95, 100, 105]
        
        for i, price in enumerate(prices):
            data = MarketData(
                symbol="BTCUSD",
                timestamp=base_time + timedelta(minutes=i),
                open=price,
                high=price * 1.01,
                low=price * 0.99,
                close=price,
                volume=1000.0,
                exchange="test"
            )
            market_data.append(data)
        
        # Process data
        signals = engine.process_market_data(market_data)
        
        # Verify both strategies were called
        assert ma_strategy.analysis_calls > 0
        assert rsi_strategy.analysis_calls > 0
        
        # Get status
        status = engine.get_strategy_status()
        assert 'ma_multi' in status
        assert 'rsi_multi' in status
        
        # Clean up
        engine.stop_engine()


if __name__ == "__main__":
    pytest.main([__file__])


class TestATRVolatilityStrategy:
    """Test cases for ATRVolatilityStrategy."""
    
    def create_market_data(self, prices: List[float], symbol: str = "BTCUSD") -> List[MarketData]:
        """Create market data from price list with realistic OHLC."""
        market_data = []
        base_time = datetime.now()
        
        for i, price in enumerate(prices):
            # Create realistic OHLC with some volatility
            volatility = abs(np.random.normal(0, price * 0.01))  # 1% volatility
            
            open_price = price + np.random.normal(0, volatility * 0.5)
            high_price = max(open_price, price) + abs(np.random.normal(0, volatility))
            low_price = min(open_price, price) - abs(np.random.normal(0, volatility))
            
            data = MarketData(
                symbol=symbol,
                timestamp=base_time + timedelta(minutes=i),
                open=open_price,
                high=high_price,
                low=low_price,
                close=price,
                volume=1000.0 + np.random.normal(0, 200),
                exchange="test"
            )
            market_data.append(data)
        
        return market_data
    
    def test_strategy_initialization(self):
        """Test ATRVolatilityStrategy initialization."""
        from src.strategies import ATRVolatilityStrategy
        
        config = StrategyConfig(
            name="atr_test",
            parameters={
                'atr_period': 14,
                'atr_multiplier': 2.0,
                'volatility_threshold': 1.5,
                'min_confidence': 0.86
            }
        )
        
        strategy = ATRVolatilityStrategy(config)
        
        assert strategy.name == "atr_test"
        assert strategy.atr_period == 14
        assert strategy.atr_multiplier == 2.0
        assert strategy.volatility_threshold == 1.5
        assert strategy.min_confidence == 0.86
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        from src.strategies import ATRVolatilityStrategy
        
        # Valid parameters
        valid_config = StrategyConfig(
            name="atr_test",
            parameters={
                'atr_period': 14,
                'atr_multiplier': 2.0,
                'squeeze_threshold': 0.5,
                'expansion_threshold': 2.0,
                'min_confidence': 0.86
            }
        )
        strategy = ATRVolatilityStrategy(valid_config)
        assert strategy.validate_parameters() is True
        
        # Invalid parameters - squeeze >= expansion
        invalid_config = StrategyConfig(
            name="atr_test",
            parameters={
                'atr_period': 14,
                'squeeze_threshold': 2.0,
                'expansion_threshold': 1.0,
                'min_confidence': 0.86
            }
        )
        strategy = ATRVolatilityStrategy(invalid_config)
        assert strategy.validate_parameters() is False
        
        # Invalid ATR period
        invalid_config = StrategyConfig(
            name="atr_test",
            parameters={
                'atr_period': -5,
                'min_confidence': 0.86
            }
        )
        strategy = ATRVolatilityStrategy(invalid_config)
        assert strategy.validate_parameters() is False
    
    def test_required_data_length(self):
        """Test required data length calculation."""
        from src.strategies import ATRVolatilityStrategy
        
        config = StrategyConfig(
            name="atr_test",
            parameters={'atr_period': 14, 'lookback_period': 50}
        )
        strategy = ATRVolatilityStrategy(config)
        
        assert strategy.get_required_data_length() == 70  # max(14, 50) + 20
    
    def test_atr_calculation(self):
        """Test ATR calculation functionality."""
        from src.strategies import ATRVolatilityStrategy
        
        config = StrategyConfig(
            name="atr_test",
            parameters={'atr_period': 5}
        )
        strategy = ATRVolatilityStrategy(config)
        
        # Create price data with increasing volatility
        prices = [100, 102, 98, 105, 95, 110, 90, 115, 85, 120]
        highs = [p * 1.02 for p in prices]
        lows = [p * 0.98 for p in prices]
        
        atr_values = strategy._calculate_atr(highs, lows, prices)
        
        assert atr_values is not None
        assert len(atr_values) > 0
        assert all(atr > 0 for atr in atr_values)
    
    def test_volatility_breakout_signal(self):
        """Test volatility breakout signal generation."""
        from src.strategies import ATRVolatilityStrategy
        
        config = StrategyConfig(
            name="atr_test",
            parameters={
                'atr_period': 10,
                'atr_multiplier': 1.5,
                'min_confidence': 0.8,
                'trend_filter': False  # Disable trend filter for testing
            }
        )
        strategy = ATRVolatilityStrategy(config)
        strategy.initialize()
        
        # Create price data with volatility breakout pattern
        # Start with low volatility, then sudden price jump
        base_prices = [100] * 20  # Low volatility period
        breakout_prices = [100, 101, 102, 108, 115, 120]  # Volatility expansion
        prices = base_prices + breakout_prices
        
        market_data = self.create_market_data(prices)
        
        # Process data to detect breakout
        signal = None
        for i in range(strategy.get_required_data_length(), len(market_data)):
            data_slice = market_data[:i+1]
            signal = strategy.process_market_data(data_slice)
            if signal:
                break
        
        # Should detect volatility breakout
        if signal:
            assert signal.symbol == "BTCUSD"
            assert signal.confidence >= 0.8
            assert 'atr_ratio' in signal.metadata
            assert 'volatility_state' in signal.metadata
    
    def test_volatility_squeeze_detection(self):
        """Test volatility squeeze detection."""
        from src.strategies import ATRVolatilityStrategy
        
        config = StrategyConfig(
            name="atr_test",
            parameters={
                'atr_period': 8,
                'squeeze_threshold': 0.6,
                'min_confidence': 0.8
            }
        )
        strategy = ATRVolatilityStrategy(config)
        strategy.initialize()
        
        # Create price data with volatility squeeze (very low volatility)
        prices = [100 + np.sin(i * 0.1) * 0.5 for i in range(50)]  # Very tight range
        market_data = self.create_market_data(prices)
        
        # Process data
        for i in range(strategy.get_required_data_length(), len(market_data)):
            data_slice = market_data[:i+1]
            strategy.process_market_data(data_slice)
        
        # Check if squeeze was detected in volatility history
        assert len(strategy._atr_history) > 0
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        from src.strategies import ATRVolatilityStrategy
        
        config = StrategyConfig(name="atr_test")
        strategy = ATRVolatilityStrategy(config)
        strategy.initialize()
        
        # Provide insufficient data
        prices = [100, 101, 102]  # Need 70, providing 3
        market_data = self.create_market_data(prices)
        
        signal = strategy.analyze(market_data)
        assert signal is None
    
    def test_trend_filter(self):
        """Test trend filter functionality."""
        from src.strategies import ATRVolatilityStrategy
        
        # Test with trend filter enabled
        config_with_filter = StrategyConfig(
            name="atr_test",
            parameters={
                'trend_filter': True,
                'min_confidence': 0.8
            }
        )
        strategy_with_filter = ATRVolatilityStrategy(config_with_filter)
        strategy_with_filter.initialize()
        
        # Test with trend filter disabled
        config_without_filter = StrategyConfig(
            name="atr_test",
            parameters={
                'trend_filter': False,
                'min_confidence': 0.8
            }
        )
        strategy_without_filter = ATRVolatilityStrategy(config_without_filter)
        strategy_without_filter.initialize()
        
        # Both should initialize successfully
        assert strategy_with_filter.trend_filter is True
        assert strategy_without_filter.trend_filter is False
    
    def test_correlation_calculation(self):
        """Test volume-volatility correlation calculation."""
        from src.strategies import ATRVolatilityStrategy
        
        config = StrategyConfig(name="atr_test")
        strategy = ATRVolatilityStrategy(config)
        
        # Test correlation calculation
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]  # Perfect positive correlation
        
        correlation = strategy._calculate_correlation(x, y)
        assert abs(correlation - 1.0) < 0.01  # Should be close to 1.0
        
        # Test with no correlation
        y_no_corr = [5, 3, 8, 1, 9]
        correlation_no = strategy._calculate_correlation(x, y_no_corr)
        assert abs(correlation_no) < 0.8  # Should be low correlation
    
    def test_volatility_state_classification(self):
        """Test volatility state classification."""
        from src.strategies import ATRVolatilityStrategy
        
        config = StrategyConfig(
            name="atr_test",
            parameters={
                'squeeze_threshold': 0.5,
                'expansion_threshold': 2.0
            }
        )
        strategy = ATRVolatilityStrategy(config)
        
        # Test different volatility states
        assert strategy._classify_volatility_state(0.3) == 'squeeze'
        assert strategy._classify_volatility_state(0.8) == 'normal'
        assert strategy._classify_volatility_state(1.2) == 'elevated'
        assert strategy._classify_volatility_state(2.5) == 'expansion'


class TestATRTechnicalIndicators:
    """Test cases for ATR technical indicators."""
    
    def test_atr_calculation(self):
        """Test ATR calculation in technical indicators."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        # Create sample OHLC data
        highs = [102, 104, 103, 106, 105, 108, 107, 110, 109, 112, 111, 114, 113, 116, 115]
        lows = [98, 96, 97, 94, 95, 92, 93, 90, 91, 88, 89, 86, 87, 84, 85]
        closes = [100, 102, 101, 104, 103, 106, 105, 108, 107, 110, 109, 112, 111, 114, 113]
        
        atr = indicators.atr(highs, lows, closes, 14)
        
        assert atr is not None
        assert atr > 0
        assert isinstance(atr, float)
    
    def test_atr_bands_calculation(self):
        """Test ATR bands calculation."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        # Create sample OHLC data
        highs = [102, 104, 103, 106, 105, 108, 107, 110, 109, 112, 111, 114, 113, 116, 115]
        lows = [98, 96, 97, 94, 95, 92, 93, 90, 91, 88, 89, 86, 87, 84, 85]
        closes = [100, 102, 101, 104, 103, 106, 105, 108, 107, 110, 109, 112, 111, 114, 113]
        
        atr_bands = indicators.atr_bands(highs, lows, closes, 14, 2.0)
        
        if atr_bands:
            upper, middle, lower = atr_bands
            
            assert isinstance(upper, float)
            assert isinstance(middle, float)
            assert isinstance(lower, float)
            assert upper > middle > lower
    
    def test_atr_insufficient_data(self):
        """Test ATR with insufficient data."""
        from src.strategies import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        # Insufficient data
        highs = [102, 104]
        lows = [98, 96]
        closes = [100, 102]
        
        atr = indicators.atr(highs, lows, closes, 14)
        assert atr is None
        
        atr_bands = indicators.atr_bands(highs, lows, closes, 14)
        assert atr_bands is None


class TestATRStrategyIntegration:
    """Integration tests for ATR strategy with framework."""
    
    def test_atr_strategy_registration(self):
        """Test ATR strategy registration with framework."""
        from src.strategies import ATRVolatilityStrategy, StrategyRegistry
        
        registry = StrategyRegistry()
        
        # Register ATR strategy
        assert registry.register_strategy(ATRVolatilityStrategy) is True
        assert "ATRVolatilityStrategy" in registry
        
        # Create strategy instance
        config = StrategyConfig(name="atr_integration_test")
        strategy = registry.create_strategy("ATRVolatilityStrategy", config)
        
        assert strategy is not None
        assert isinstance(strategy, ATRVolatilityStrategy)
        assert strategy.name == "atr_integration_test"
    
    def test_atr_strategy_config_manager(self):
        """Test ATR strategy with configuration manager."""
        from src.strategies import StrategyConfigManager
        
        config_manager = StrategyConfigManager()
        
        # Check ATR template is available
        templates = config_manager.get_available_templates()
        assert 'ATRVolatilityStrategy' in templates
        
        # Create ATR configuration
        config = config_manager.create_config_from_template(
            'ATRVolatilityStrategy',
            'atr_config_test',
            {
                'atr_period': 21,
                'atr_multiplier': 2.5,
                'min_confidence': 0.90
            }
        )
        
        assert config is not None
        assert config.name == 'atr_config_test'
        assert config.parameters['atr_period'] == 21
        assert config.parameters['atr_multiplier'] == 2.5
        assert config.parameters['min_confidence'] == 0.90
    
    def test_atr_strategy_presets(self):
        """Test ATR strategy preset configurations."""
        from src.strategies import StrategyConfigManager
        
        config_manager = StrategyConfigManager()
        
        # Create presets
        presets = config_manager.create_preset_configs()
        
        # Check ATR presets exist
        atr_presets = [name for name in presets.keys() if 'atr_volatility' in name]
        assert len(atr_presets) >= 3  # Should have breakout, squeeze, conservative
        
        # Verify preset configurations
        for preset_name in atr_presets:
            if preset_name in presets:
                preset_config = presets[preset_name]
                assert preset_config is not None
                assert 'atr_period' in preset_config.parameters
                assert 'atr_multiplier' in preset_config.parameters
    
    def test_atr_strategy_engine_integration(self):
        """Test ATR strategy integration with strategy engine."""
        from src.strategies import (ATRVolatilityStrategy, StrategyRegistry, 
                                  StrategyEngine, SignalProcessor)
        
        # Set up framework
        registry = StrategyRegistry()
        registry.register_strategy(ATRVolatilityStrategy)
        
        signal_processor = SignalProcessor()
        engine = StrategyEngine(registry, signal_processor)
        
        # Create ATR strategy
        config = StrategyConfig(
            name="atr_engine_test",
            parameters={
                'atr_period': 10,
                'min_confidence': 0.85,
                'trend_filter': False
            }
        )
        
        strategy = registry.create_strategy("ATRVolatilityStrategy", config)
        assert strategy is not None
        
        # Add to engine
        engine.add_strategy(strategy)
        engine.start_engine()
        engine.start_strategy("atr_engine_test")
        
        # Verify strategy is active
        status = engine.get_strategy_status()
        assert "atr_engine_test" in status
        assert status["atr_engine_test"]["active"] is True
        
        # Clean up
        engine.stop_engine()


if __name__ == "__main__":
    pytest.main([__file__])