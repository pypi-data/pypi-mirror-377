"""
Unit tests for multi-market strategy engine functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from typing import List, Optional

from src.strategies.multi_market_strategy_engine import MultiMarketStrategyEngine
from src.strategies.market_agnostic_strategy import MarketAgnosticStrategy
from src.strategies.market_specific_strategy import MarketSpecificStrategy
from src.strategies.strategy_registry import StrategyRegistry
from src.strategies.signal_processor import SignalProcessor
from src.strategies.base_strategy import StrategyConfig
from src.models.data_models import MarketData, UnifiedMarketData, TradingSignal, SignalAction, SessionInfo
from src.markets.types import MarketType, UnifiedSymbol


class MockMarketAgnosticStrategy(MarketAgnosticStrategy):
    """Mock market-agnostic strategy for testing."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.analyze_calls = []
        self.mock_signal = None
    
    def initialize(self) -> bool:
        return True
    
    def analyze_unified_data(self, market_data: List[UnifiedMarketData]) -> Optional[TradingSignal]:
        self.analyze_calls.append(market_data)
        return self.mock_signal
    
    def get_cross_market_correlation_threshold(self) -> float:
        return 0.7
    
    def get_required_data_length(self) -> int:
        return 5
    
    def validate_parameters(self) -> bool:
        return True


class MockMarketSpecificStrategy(MarketSpecificStrategy):
    """Mock market-specific strategy for testing."""
    
    def __init__(self, config: StrategyConfig, supported_markets: List[MarketType]):
        super().__init__(config, supported_markets)
        self.analyze_calls = []
        self.mock_signal = None
    
    def initialize(self) -> bool:
        return True
    
    def analyze_market_data(self, market_data: List[UnifiedMarketData], 
                           market_type: MarketType) -> Optional[TradingSignal]:
        self.analyze_calls.append((market_data, market_type))
        return self.mock_signal
    
    def get_market_specific_parameters(self, market_type: MarketType) -> dict:
        return {"param1": "value1"}
    
    def validate_market_conditions(self, market_data: List[UnifiedMarketData], 
                                 market_type: MarketType) -> bool:
        return True
    
    def get_required_data_length(self) -> int:
        return 5
    
    def validate_parameters(self) -> bool:
        return True


@pytest.fixture
def strategy_registry():
    """Create a strategy registry for testing."""
    return StrategyRegistry()


@pytest.fixture
def signal_processor():
    """Create a signal processor for testing."""
    return SignalProcessor()


@pytest.fixture
def multi_market_engine(strategy_registry, signal_processor):
    """Create a multi-market strategy engine for testing."""
    return MultiMarketStrategyEngine(strategy_registry, signal_processor, max_workers=2)


@pytest.fixture
def sample_crypto_data():
    """Create sample crypto market data."""
    symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
    return [
        UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime.now() - timedelta(minutes=i),
            open=Decimal("50000"),
            high=Decimal("51000"),
            low=Decimal("49000"),
            close=Decimal("50500"),
            volume=Decimal("100"),
            source="binance",
            market_type=MarketType.CRYPTO
        ) for i in range(10, 0, -1)
    ]


@pytest.fixture
def sample_forex_data():
    """Create sample forex market data."""
    symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
    session_info = SessionInfo(
        session_name="london",
        is_active=True,
        market_type=MarketType.FOREX
    )
    return [
        UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime.now() - timedelta(minutes=i),
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0950"),
            close=Decimal("1.1025"),
            volume=Decimal("1000"),
            source="oanda",
            market_type=MarketType.FOREX,
            session_info=session_info
        ) for i in range(10, 0, -1)
    ]


@pytest.fixture
def sample_legacy_data():
    """Create sample legacy market data."""
    return [
        MarketData(
            symbol="BTCUSDT",
            timestamp=datetime.now() - timedelta(minutes=i),
            open=Decimal("50000"),
            high=Decimal("51000"),
            low=Decimal("49000"),
            close=Decimal("50500"),
            volume=Decimal("100"),
            exchange="binance"
        ) for i in range(10, 0, -1)
    ]


class TestMultiMarketStrategyEngine:
    """Test cases for MultiMarketStrategyEngine."""
    
    def test_initialization(self, multi_market_engine):
        """Test engine initialization."""
        assert multi_market_engine is not None
        assert len(multi_market_engine._market_strategies) == 2
        assert MarketType.CRYPTO in multi_market_engine._market_strategies
        assert MarketType.FOREX in multi_market_engine._market_strategies
        assert len(multi_market_engine._agnostic_strategies) == 0
    
    def test_add_market_agnostic_strategy(self, multi_market_engine):
        """Test adding market-agnostic strategy."""
        config = StrategyConfig(name="test_agnostic", enabled=True)
        strategy = MockMarketAgnosticStrategy(config)
        
        result = multi_market_engine.add_strategy(strategy)
        
        assert result is True
        assert "test_agnostic" in multi_market_engine._agnostic_strategies
        assert "test_agnostic" not in multi_market_engine._market_strategies[MarketType.CRYPTO]
        assert "test_agnostic" not in multi_market_engine._market_strategies[MarketType.FOREX]
    
    def test_add_market_specific_strategy(self, multi_market_engine):
        """Test adding market-specific strategy."""
        config = StrategyConfig(name="test_crypto", enabled=True)
        strategy = MockMarketSpecificStrategy(config, [MarketType.CRYPTO])
        
        result = multi_market_engine.add_strategy(strategy)
        
        assert result is True
        assert "test_crypto" in multi_market_engine._market_strategies[MarketType.CRYPTO]
        assert "test_crypto" not in multi_market_engine._market_strategies[MarketType.FOREX]
        assert "test_crypto" not in multi_market_engine._agnostic_strategies
    
    def test_add_multi_market_specific_strategy(self, multi_market_engine):
        """Test adding strategy that supports multiple markets."""
        config = StrategyConfig(name="test_multi", enabled=True)
        strategy = MockMarketSpecificStrategy(config, [MarketType.CRYPTO, MarketType.FOREX])
        
        result = multi_market_engine.add_strategy(strategy)
        
        assert result is True
        assert "test_multi" in multi_market_engine._market_strategies[MarketType.CRYPTO]
        assert "test_multi" in multi_market_engine._market_strategies[MarketType.FOREX]
        assert "test_multi" not in multi_market_engine._agnostic_strategies
    
    def test_remove_strategy(self, multi_market_engine):
        """Test removing strategy."""
        config = StrategyConfig(name="test_remove", enabled=True)
        strategy = MockMarketAgnosticStrategy(config)
        
        multi_market_engine.add_strategy(strategy)
        assert "test_remove" in multi_market_engine._agnostic_strategies
        
        result = multi_market_engine.remove_strategy("test_remove")
        
        assert result is True
        assert "test_remove" not in multi_market_engine._agnostic_strategies
    
    def test_get_market_strategies(self, multi_market_engine):
        """Test getting strategies for specific market."""
        # Add strategies
        agnostic_config = StrategyConfig(name="agnostic", enabled=True)
        agnostic_strategy = MockMarketAgnosticStrategy(agnostic_config)
        
        crypto_config = StrategyConfig(name="crypto_only", enabled=True)
        crypto_strategy = MockMarketSpecificStrategy(crypto_config, [MarketType.CRYPTO])
        
        forex_config = StrategyConfig(name="forex_only", enabled=True)
        forex_strategy = MockMarketSpecificStrategy(forex_config, [MarketType.FOREX])
        
        multi_market_engine.add_strategy(agnostic_strategy)
        multi_market_engine.add_strategy(crypto_strategy)
        multi_market_engine.add_strategy(forex_strategy)
        
        # Test crypto strategies
        crypto_strategies = multi_market_engine.get_market_strategies(MarketType.CRYPTO)
        assert "crypto_only" in crypto_strategies
        assert "agnostic" in crypto_strategies
        assert "forex_only" not in crypto_strategies
        
        # Test forex strategies
        forex_strategies = multi_market_engine.get_market_strategies(MarketType.FOREX)
        assert "forex_only" in forex_strategies
        assert "agnostic" in forex_strategies
        assert "crypto_only" not in forex_strategies
    
    def test_get_strategy_market_support(self, multi_market_engine):
        """Test getting market support for strategy."""
        # Add strategies
        agnostic_config = StrategyConfig(name="agnostic", enabled=True)
        agnostic_strategy = MockMarketAgnosticStrategy(agnostic_config)
        
        crypto_config = StrategyConfig(name="crypto_only", enabled=True)
        crypto_strategy = MockMarketSpecificStrategy(crypto_config, [MarketType.CRYPTO])
        
        multi_market_engine.add_strategy(agnostic_strategy)
        multi_market_engine.add_strategy(crypto_strategy)
        
        # Test agnostic strategy
        agnostic_support = multi_market_engine.get_strategy_market_support("agnostic")
        assert MarketType.CRYPTO in agnostic_support
        assert MarketType.FOREX in agnostic_support
        
        # Test crypto-specific strategy
        crypto_support = multi_market_engine.get_strategy_market_support("crypto_only")
        assert MarketType.CRYPTO in crypto_support
        assert MarketType.FOREX not in crypto_support
    
    def test_validate_strategy_market_compatibility(self, multi_market_engine, sample_crypto_data, sample_forex_data):
        """Test strategy market compatibility validation."""
        # Add strategies
        agnostic_config = StrategyConfig(name="agnostic", enabled=True)
        agnostic_strategy = MockMarketAgnosticStrategy(agnostic_config)
        
        crypto_config = StrategyConfig(name="crypto_only", enabled=True)
        crypto_strategy = MockMarketSpecificStrategy(crypto_config, [MarketType.CRYPTO])
        
        multi_market_engine.add_strategy(agnostic_strategy)
        multi_market_engine.add_strategy(crypto_strategy)
        
        # Test agnostic strategy compatibility
        assert multi_market_engine.validate_strategy_market_compatibility("agnostic", sample_crypto_data[0])
        assert multi_market_engine.validate_strategy_market_compatibility("agnostic", sample_forex_data[0])
        
        # Test crypto-specific strategy compatibility
        assert multi_market_engine.validate_strategy_market_compatibility("crypto_only", sample_crypto_data[0])
        assert not multi_market_engine.validate_strategy_market_compatibility("crypto_only", sample_forex_data[0])
    
    def test_process_unified_market_data(self, multi_market_engine, sample_crypto_data, sample_forex_data):
        """Test processing unified market data."""
        # Add and start strategies
        agnostic_config = StrategyConfig(name="agnostic", enabled=True)
        agnostic_strategy = MockMarketAgnosticStrategy(agnostic_config)
        agnostic_strategy.mock_signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="agnostic"
        )
        
        crypto_config = StrategyConfig(name="crypto_only", enabled=True)
        crypto_strategy = MockMarketSpecificStrategy(crypto_config, [MarketType.CRYPTO])
        crypto_strategy.mock_signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.SELL,
            confidence=0.7,
            timestamp=datetime.now(),
            strategy_name="crypto_only"
        )
        
        multi_market_engine.add_strategy(agnostic_strategy)
        multi_market_engine.add_strategy(crypto_strategy)
        multi_market_engine.start_engine()
        multi_market_engine.start_all_strategies()
        
        # Process mixed market data
        mixed_data = sample_crypto_data + sample_forex_data
        signals = multi_market_engine.process_unified_market_data(mixed_data)
        
        # Verify signals were generated
        assert len(signals) > 0
        
        # Verify strategies were called appropriately
        assert len(agnostic_strategy.analyze_calls) > 0
        assert len(crypto_strategy.analyze_calls) > 0
        
        # Verify crypto strategy only received crypto data
        for call_data, market_type in crypto_strategy.analyze_calls:
            for data in call_data:
                assert data.market_type == MarketType.CRYPTO
    
    def test_process_legacy_market_data(self, multi_market_engine, sample_legacy_data):
        """Test processing legacy market data (backward compatibility)."""
        # Add and start strategy
        agnostic_config = StrategyConfig(name="agnostic", enabled=True)
        agnostic_strategy = MockMarketAgnosticStrategy(agnostic_config)
        agnostic_strategy.mock_signal = TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="agnostic"
        )
        
        multi_market_engine.add_strategy(agnostic_strategy)
        multi_market_engine.start_engine()
        multi_market_engine.start_all_strategies()
        
        # Process legacy data
        signals = multi_market_engine.process_market_data(sample_legacy_data)
        
        # Verify signals were generated
        assert len(signals) > 0
        
        # Verify strategy was called
        assert len(agnostic_strategy.analyze_calls) > 0
    
    def test_get_multi_market_stats(self, multi_market_engine):
        """Test getting multi-market statistics."""
        # Add strategies
        agnostic_config = StrategyConfig(name="agnostic", enabled=True)
        agnostic_strategy = MockMarketAgnosticStrategy(agnostic_config)
        
        crypto_config = StrategyConfig(name="crypto_only", enabled=True)
        crypto_strategy = MockMarketSpecificStrategy(crypto_config, [MarketType.CRYPTO])
        
        multi_market_engine.add_strategy(agnostic_strategy)
        multi_market_engine.add_strategy(crypto_strategy)
        
        stats = multi_market_engine.get_multi_market_stats()
        
        # Verify basic stats
        assert 'running' in stats
        assert 'total_strategies' in stats
        assert 'active_strategies' in stats
        
        # Verify market breakdown
        assert 'market_breakdown' in stats
        assert 'crypto' in stats['market_breakdown']
        assert 'forex' in stats['market_breakdown']
        
        # Verify agnostic strategies count
        assert 'agnostic_strategies_count' in stats
        assert stats['agnostic_strategies_count'] == 1
    
    def test_data_grouping_by_market(self, multi_market_engine, sample_crypto_data, sample_forex_data):
        """Test internal data grouping by market type."""
        mixed_data = sample_crypto_data + sample_forex_data
        groups = multi_market_engine._group_data_by_market(mixed_data)
        
        assert MarketType.CRYPTO in groups
        assert MarketType.FOREX in groups
        assert len(groups[MarketType.CRYPTO]) == len(sample_crypto_data)
        assert len(groups[MarketType.FOREX]) == len(sample_forex_data)
    
    def test_market_data_cache_update(self, multi_market_engine, sample_crypto_data, sample_forex_data):
        """Test market data cache updates."""
        mixed_data = sample_crypto_data + sample_forex_data
        groups = multi_market_engine._group_data_by_market(mixed_data)
        
        multi_market_engine._update_market_data_cache(groups)
        
        # Verify cache was updated
        assert len(multi_market_engine._market_data_cache[MarketType.CRYPTO]) == len(sample_crypto_data)
        assert len(multi_market_engine._market_data_cache[MarketType.FOREX]) == len(sample_forex_data)
    
    def test_strategy_classification_on_add(self, multi_market_engine):
        """Test that strategies are properly classified when added."""
        # Test agnostic strategy classification
        agnostic_config = StrategyConfig(name="agnostic", enabled=True)
        agnostic_strategy = MockMarketAgnosticStrategy(agnostic_config)
        
        multi_market_engine.add_strategy(agnostic_strategy)
        assert "agnostic" in multi_market_engine._agnostic_strategies
        
        # Test market-specific strategy classification
        crypto_config = StrategyConfig(name="crypto_only", enabled=True)
        crypto_strategy = MockMarketSpecificStrategy(crypto_config, [MarketType.CRYPTO])
        
        multi_market_engine.add_strategy(crypto_strategy)
        assert "crypto_only" in multi_market_engine._market_strategies[MarketType.CRYPTO]
        assert "crypto_only" not in multi_market_engine._market_strategies[MarketType.FOREX]
    
    def test_strategy_classification_removal(self, multi_market_engine):
        """Test that strategy classifications are removed properly."""
        # Add strategies
        agnostic_config = StrategyConfig(name="agnostic", enabled=True)
        agnostic_strategy = MockMarketAgnosticStrategy(agnostic_config)
        
        crypto_config = StrategyConfig(name="crypto_only", enabled=True)
        crypto_strategy = MockMarketSpecificStrategy(crypto_config, [MarketType.CRYPTO])
        
        multi_market_engine.add_strategy(agnostic_strategy)
        multi_market_engine.add_strategy(crypto_strategy)
        
        # Remove strategies
        multi_market_engine.remove_strategy("agnostic")
        multi_market_engine.remove_strategy("crypto_only")
        
        # Verify classifications were removed
        assert "agnostic" not in multi_market_engine._agnostic_strategies
        assert "crypto_only" not in multi_market_engine._market_strategies[MarketType.CRYPTO]
    
    def test_error_handling_in_strategy_processing(self, multi_market_engine, sample_crypto_data):
        """Test error handling during strategy processing."""
        # Create strategy that raises exception
        config = StrategyConfig(name="error_strategy", enabled=True)
        strategy = MockMarketAgnosticStrategy(config)
        
        def raise_error(data):
            raise Exception("Test error")
        
        strategy.analyze_unified_data = raise_error
        
        multi_market_engine.add_strategy(strategy)
        multi_market_engine.start_engine()
        multi_market_engine.start_all_strategies()
        
        # Process data - should not raise exception
        signals = multi_market_engine.process_unified_market_data(sample_crypto_data)
        
        # Should return empty list due to error (strategy handles error gracefully)
        assert signals == []
        
        # The error is handled at the strategy level, not the engine level
        # This is correct behavior - strategies should handle their own errors gracefully


if __name__ == "__main__":
    pytest.main([__file__])