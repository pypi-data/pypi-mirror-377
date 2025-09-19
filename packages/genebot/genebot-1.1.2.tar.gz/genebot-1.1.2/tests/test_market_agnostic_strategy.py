"""
Unit tests for market-agnostic strategy base class.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from src.strategies.market_agnostic_strategy import MarketAgnosticStrategy
from src.strategies.base_strategy import StrategyConfig
from src.models.data_models import MarketData, UnifiedMarketData, TradingSignal, SignalAction, SessionInfo
from src.markets.types import MarketType, UnifiedSymbol


class TestMarketAgnosticStrategy(MarketAgnosticStrategy):
    """Concrete implementation for testing."""
    
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
        return self.cross_market_correlation_threshold
    
    def get_required_data_length(self) -> int:
        return 5
    
    def validate_parameters(self) -> bool:
        return super().validate_parameters()


@pytest.fixture
def strategy_config():
    """Create a strategy configuration for testing."""
    return StrategyConfig(
        name="test_agnostic_strategy",
        enabled=True,
        parameters={
            'market_weights': {'crypto': 0.6, 'forex': 0.4},
            'cross_market_correlation_threshold': 0.8
        }
    )


@pytest.fixture
def strategy(strategy_config):
    """Create a test strategy instance."""
    return TestMarketAgnosticStrategy(strategy_config)


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


class TestMarketAgnosticStrategyClass:
    """Test cases for MarketAgnosticStrategy."""
    
    def test_initialization(self, strategy):
        """Test strategy initialization."""
        assert strategy.name == "test_agnostic_strategy"
        assert strategy.enabled is True
        assert MarketType.CRYPTO in strategy.supported_markets
        assert MarketType.FOREX in strategy.supported_markets
        assert strategy.cross_market_correlation_threshold == 0.8
        assert strategy.market_weights == {'crypto': 0.6, 'forex': 0.4}
    
    def test_supports_market_type(self, strategy):
        """Test market type support checking."""
        assert strategy.supports_market_type(MarketType.CRYPTO)
        assert strategy.supports_market_type(MarketType.FOREX)
    
    def test_get_supported_markets(self, strategy):
        """Test getting supported markets."""
        supported = strategy.get_supported_markets()
        assert MarketType.CRYPTO in supported
        assert MarketType.FOREX in supported
        assert len(supported) == 2
    
    def test_get_market_weight(self, strategy):
        """Test getting market weights."""
        assert strategy.get_market_weight(MarketType.CRYPTO) == 0.6
        assert strategy.get_market_weight(MarketType.FOREX) == 0.4
        
        # Test default weight for unspecified market
        strategy.market_weights = {}
        assert strategy.get_market_weight(MarketType.CRYPTO) == 1.0
    
    def test_process_unified_data(self, strategy, sample_crypto_data):
        """Test processing unified market data."""
        strategy.mock_signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_agnostic_strategy"
        )
        
        strategy.start()
        signal = strategy._process_unified_data(sample_crypto_data)
        
        assert signal is not None
        assert signal.symbol == "BTC/USDT"
        assert signal.action == SignalAction.BUY
        assert len(strategy.analyze_calls) == 1
        assert strategy.signals_generated == 1
    
    def test_process_legacy_data(self, strategy, sample_legacy_data):
        """Test processing legacy market data."""
        strategy.mock_signal = TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.SELL,
            confidence=0.7,
            timestamp=datetime.now(),
            strategy_name="test_agnostic_strategy"
        )
        
        strategy.start()
        signal = strategy.process_market_data(sample_legacy_data)
        
        assert signal is not None
        assert signal.symbol == "BTCUSDT"
        assert signal.action == SignalAction.SELL
        assert len(strategy.analyze_calls) == 1
    
    def test_analyze_legacy_data_conversion(self, strategy, sample_legacy_data):
        """Test legacy data conversion in analyze method."""
        strategy.mock_signal = TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.HOLD,
            confidence=0.6,
            timestamp=datetime.now(),
            strategy_name="test_agnostic_strategy"
        )
        
        signal = strategy.analyze(sample_legacy_data)
        
        assert signal is not None
        assert len(strategy.analyze_calls) == 1
        
        # Verify data was converted to unified format
        unified_data = strategy.analyze_calls[0]
        assert all(isinstance(data, UnifiedMarketData) for data in unified_data)
        assert all(data.market_type == MarketType.CRYPTO for data in unified_data)
    
    def test_data_history_management(self, strategy, sample_crypto_data, sample_forex_data):
        """Test data history management."""
        strategy.start()
        
        # Process crypto data
        strategy._process_unified_data(sample_crypto_data)
        
        # Process forex data
        strategy._process_unified_data(sample_forex_data)
        
        # Check market-specific history
        crypto_history = strategy.get_market_data_history(MarketType.CRYPTO)
        forex_history = strategy.get_market_data_history(MarketType.FOREX)
        
        assert len(crypto_history) == len(sample_crypto_data)
        assert len(forex_history) == len(sample_forex_data)
        
        # Check combined history
        all_history = strategy.get_market_data_history()
        assert len(all_history) == len(sample_crypto_data) + len(sample_forex_data)
    
    def test_symbol_data_history(self, strategy, sample_crypto_data):
        """Test symbol-specific data history."""
        strategy.start()
        strategy._process_unified_data(sample_crypto_data)
        
        # Test with UnifiedSymbol
        symbol = sample_crypto_data[0].symbol
        history = strategy.get_symbol_data_history(symbol)
        assert len(history) == len(sample_crypto_data)
        
        # Test with string
        history_str = strategy.get_symbol_data_history("BTC/USDT")
        assert len(history_str) == len(sample_crypto_data)
    
    def test_cross_market_correlation_calculation(self, strategy):
        """Test cross-market correlation calculation."""
        # Create correlated data
        btc_data = []
        eth_data = []
        
        for i in range(20):
            price = 50000 + i * 100  # Increasing prices
            
            btc_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
            btc_data.append(UnifiedMarketData(
                symbol=btc_symbol,
                timestamp=datetime.now() - timedelta(minutes=20-i),
                open=Decimal(str(price)),
                high=Decimal(str(price + 50)),
                low=Decimal(str(price - 50)),
                close=Decimal(str(price)),
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO
            ))
            
            eth_symbol = UnifiedSymbol.from_crypto_symbol("ETHUSDT")
            eth_data.append(UnifiedMarketData(
                symbol=eth_symbol,
                timestamp=datetime.now() - timedelta(minutes=20-i),
                open=Decimal(str(price * 0.08)),  # Correlated with BTC
                high=Decimal(str(price * 0.08 + 5)),
                low=Decimal(str(price * 0.08 - 5)),
                close=Decimal(str(price * 0.08)),
                volume=Decimal("1000"),
                source="binance",
                market_type=MarketType.CRYPTO
            ))
        
        # Update strategy history
        strategy._update_data_history(btc_data + eth_data)
        
        # Calculate correlation
        correlation = strategy.calculate_cross_market_correlation("BTC/USDT", "ETH/USDT", 20)
        
        assert correlation is not None
        assert correlation > 0.9  # Should be highly correlated
    
    def test_is_cross_market_correlated(self, strategy):
        """Test cross-market correlation checking."""
        # Mock correlation calculation
        def mock_correlation(symbol1, symbol2):
            if symbol1 == "BTC/USDT" and symbol2 == "ETH/USDT":
                return 0.9  # High correlation
            return 0.3  # Low correlation
        
        strategy.calculate_cross_market_correlation = mock_correlation
        
        # Test high correlation
        assert strategy.is_cross_market_correlated("BTC/USDT", "ETH/USDT")
        
        # Test low correlation
        assert not strategy.is_cross_market_correlated("BTC/USDT", "EUR/USD")
    
    def test_parameter_validation(self, strategy_config):
        """Test parameter validation."""
        # Test valid parameters
        strategy = TestMarketAgnosticStrategy(strategy_config)
        assert strategy.validate_parameters()
        
        # Test invalid market weights
        invalid_config = StrategyConfig(
            name="invalid_strategy",
            parameters={'market_weights': {'crypto': -0.5}}
        )
        invalid_strategy = TestMarketAgnosticStrategy(invalid_config)
        assert not invalid_strategy.validate_parameters()
        
        # Test invalid correlation threshold
        invalid_config2 = StrategyConfig(
            name="invalid_strategy2",
            parameters={'cross_market_correlation_threshold': 1.5}
        )
        invalid_strategy2 = TestMarketAgnosticStrategy(invalid_config2)
        assert not invalid_strategy2.validate_parameters()
    
    def test_performance_metrics(self, strategy, sample_crypto_data):
        """Test performance metrics."""
        strategy.start()
        strategy._process_unified_data(sample_crypto_data)
        
        metrics = strategy.get_performance_metrics()
        
        assert metrics['strategy_type'] == 'market_agnostic'
        assert 'supported_markets' in metrics
        assert 'market_weights' in metrics
        assert 'cross_market_correlation_threshold' in metrics
        assert 'data_history_size' in metrics
        assert 'symbols_tracked' in metrics
        
        # Verify market support
        assert 'crypto' in metrics['supported_markets']
        assert 'forex' in metrics['supported_markets']
    
    def test_insufficient_data_handling(self, strategy, sample_crypto_data):
        """Test handling of insufficient data."""
        strategy.start()
        
        # Process insufficient data (less than required length)
        insufficient_data = sample_crypto_data[:3]  # Only 3 data points, need 5
        signal = strategy._process_unified_data(insufficient_data)
        
        assert signal is None
        assert len(strategy.analyze_calls) == 0
    
    def test_error_handling_in_analysis(self, strategy, sample_crypto_data):
        """Test error handling during analysis."""
        def raise_error(data):
            raise Exception("Analysis error")
        
        strategy.analyze_unified_data = raise_error
        strategy.start()
        
        signal = strategy._process_unified_data(sample_crypto_data)
        
        assert signal is None
    
    def test_correlation_calculation_edge_cases(self, strategy):
        """Test correlation calculation edge cases."""
        # Test with insufficient data
        correlation = strategy.calculate_cross_market_correlation("BTC/USDT", "ETH/USDT", 20)
        assert correlation is None
        
        # Test with identical prices (zero variance)
        identical_data = []
        for i in range(20):
            symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
            identical_data.append(UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now() - timedelta(minutes=20-i),
                open=Decimal("50000"),
                high=Decimal("50000"),
                low=Decimal("50000"),
                close=Decimal("50000"),  # Same price
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO
            ))
        
        strategy._update_data_history(identical_data)
        correlation = strategy.calculate_cross_market_correlation("BTC/USDT", "BTC/USDT", 20)
        assert correlation == 0.0  # Should handle zero variance
    
    def test_data_history_size_limits(self, strategy):
        """Test data history size limits."""
        # Create large amount of data
        large_data = []
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        
        for i in range(1500):  # More than the 1000 limit
            large_data.append(UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now() - timedelta(minutes=1500-i),
                open=Decimal("50000"),
                high=Decimal("51000"),
                low=Decimal("49000"),
                close=Decimal("50500"),
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO
            ))
        
        strategy._update_data_history(large_data)
        
        # Check that history is limited
        symbol_history = strategy.get_symbol_data_history("BTC/USDT")
        assert len(symbol_history) <= 1000
        
        market_history = strategy.get_market_data_history(MarketType.CRYPTO)
        assert len(market_history) <= 500


if __name__ == "__main__":
    pytest.main([__file__])