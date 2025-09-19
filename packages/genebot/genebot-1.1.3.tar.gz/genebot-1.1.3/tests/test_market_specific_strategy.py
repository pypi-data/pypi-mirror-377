"""
Unit tests for market-specific strategy base class.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any

from src.strategies.market_specific_strategy import MarketSpecificStrategy
from src.strategies.base_strategy import StrategyConfig
from src.models.data_models import MarketData, UnifiedMarketData, TradingSignal, SignalAction, SessionInfo
from src.markets.types import MarketType, UnifiedSymbol


class TestMarketSpecificStrategy(MarketSpecificStrategy):
    """Concrete implementation for testing."""
    
    def __init__(self, config: StrategyConfig, supported_markets: List[MarketType]):
        super().__init__(config, supported_markets)
        self.analyze_calls = []
        self.mock_signal = None
        self.mock_conditions_valid = True
    
    def initialize(self) -> bool:
        return True
    
    def analyze_market_data(self, market_data: List[UnifiedMarketData], 
                           market_type: MarketType) -> Optional[TradingSignal]:
        self.analyze_calls.append((market_data, market_type))
        return self.mock_signal
    
    def get_market_specific_parameters(self, market_type: MarketType) -> Dict[str, Any]:
        return {
            "param1": f"value_for_{market_type.value}",
            "param2": 42
        }
    
    def validate_market_conditions(self, market_data: List[UnifiedMarketData], 
                                 market_type: MarketType) -> bool:
        return self.mock_conditions_valid
    
    def get_required_data_length(self) -> int:
        return 5
    
    def validate_parameters(self) -> bool:
        return super().validate_parameters()


@pytest.fixture
def crypto_strategy_config():
    """Create a crypto-specific strategy configuration."""
    return StrategyConfig(
        name="test_crypto_strategy",
        enabled=True,
        parameters={
            'session_aware': True,
            'market_filters': {
                'crypto': {
                    'allowed_symbols': ['BTC/USDT', 'ETH/USDT'],
                    'allowed_base_assets': ['BTC', 'ETH'],
                    'allowed_quote_assets': ['USDT', 'USD']
                }
            },
            'market_specific_params': {
                'crypto': {'volatility_threshold': 0.05}
            }
        }
    )


@pytest.fixture
def forex_strategy_config():
    """Create a forex-specific strategy configuration."""
    return StrategyConfig(
        name="test_forex_strategy",
        enabled=True,
        parameters={
            'session_aware': True,
            'market_filters': {
                'forex': {
                    'allowed_symbols': ['EUR/USD', 'GBP/USD'],
                    'blocked_symbols': ['USD/JPY']
                }
            }
        }
    )


@pytest.fixture
def multi_market_strategy_config():
    """Create a multi-market strategy configuration."""
    return StrategyConfig(
        name="test_multi_strategy",
        enabled=True,
        parameters={
            'session_aware': False,
            'market_filters': {
                'crypto': {'allowed_base_assets': ['BTC']},
                'forex': {'allowed_quote_assets': ['USD']}
            }
        }
    )


@pytest.fixture
def crypto_strategy(crypto_strategy_config):
    """Create a crypto-specific strategy."""
    return TestMarketSpecificStrategy(crypto_strategy_config, [MarketType.CRYPTO])


@pytest.fixture
def forex_strategy(forex_strategy_config):
    """Create a forex-specific strategy."""
    return TestMarketSpecificStrategy(forex_strategy_config, [MarketType.FOREX])


@pytest.fixture
def multi_market_strategy(multi_market_strategy_config):
    """Create a multi-market strategy."""
    return TestMarketSpecificStrategy(multi_market_strategy_config, [MarketType.CRYPTO, MarketType.FOREX])


@pytest.fixture
def sample_crypto_data():
    """Create sample crypto market data."""
    btc_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
    eth_symbol = UnifiedSymbol.from_crypto_symbol("ETHUSDT")
    
    data = []
    for i, symbol in enumerate([btc_symbol, eth_symbol]):
        for j in range(5):
            data.append(UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now() - timedelta(minutes=j),
                open=Decimal("50000"),
                high=Decimal("51000"),
                low=Decimal("49000"),
                close=Decimal("50500"),
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO
            ))
    return data


@pytest.fixture
def sample_forex_data():
    """Create sample forex market data."""
    eur_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
    gbp_symbol = UnifiedSymbol.from_forex_symbol("GBPUSD")
    
    session_info = SessionInfo(
        session_name="london",
        is_active=True,
        market_type=MarketType.FOREX
    )
    
    data = []
    for symbol in [eur_symbol, gbp_symbol]:
        for j in range(5):
            data.append(UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now() - timedelta(minutes=j),
                open=Decimal("1.1000"),
                high=Decimal("1.1050"),
                low=Decimal("1.0950"),
                close=Decimal("1.1025"),
                volume=Decimal("1000"),
                source="oanda",
                market_type=MarketType.FOREX,
                session_info=session_info
            ))
    return data


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


class TestMarketSpecificStrategyClass:
    """Test cases for MarketSpecificStrategy."""
    
    def test_initialization(self, crypto_strategy):
        """Test strategy initialization."""
        assert crypto_strategy.name == "test_crypto_strategy"
        assert crypto_strategy.enabled is True
        assert MarketType.CRYPTO in crypto_strategy.supported_markets
        assert crypto_strategy.primary_market == MarketType.CRYPTO
        assert crypto_strategy.session_aware is True
    
    def test_initialization_validation(self, crypto_strategy_config):
        """Test initialization validation."""
        # Test empty supported markets
        with pytest.raises(ValueError, match="must support at least one market type"):
            TestMarketSpecificStrategy(crypto_strategy_config, [])
    
    def test_supports_market_type(self, crypto_strategy, multi_market_strategy):
        """Test market type support checking."""
        # Crypto-only strategy
        assert crypto_strategy.supports_market_type(MarketType.CRYPTO)
        assert not crypto_strategy.supports_market_type(MarketType.FOREX)
        
        # Multi-market strategy
        assert multi_market_strategy.supports_market_type(MarketType.CRYPTO)
        assert multi_market_strategy.supports_market_type(MarketType.FOREX)
    
    def test_get_supported_markets(self, crypto_strategy, multi_market_strategy):
        """Test getting supported markets."""
        # Crypto-only strategy
        crypto_supported = crypto_strategy.get_supported_markets()
        assert MarketType.CRYPTO in crypto_supported
        assert MarketType.FOREX not in crypto_supported
        assert len(crypto_supported) == 1
        
        # Multi-market strategy
        multi_supported = multi_market_strategy.get_supported_markets()
        assert MarketType.CRYPTO in multi_supported
        assert MarketType.FOREX in multi_supported
        assert len(multi_supported) == 2
    
    def test_get_primary_market(self, crypto_strategy, multi_market_strategy):
        """Test getting primary market."""
        assert crypto_strategy.get_primary_market() == MarketType.CRYPTO
        assert multi_market_strategy.get_primary_market() == MarketType.CRYPTO  # First in list
    
    def test_process_unified_data(self, crypto_strategy, sample_crypto_data):
        """Test processing unified market data."""
        crypto_strategy.mock_signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_crypto_strategy"
        )
        
        crypto_strategy.start()
        signal = crypto_strategy._process_unified_data(sample_crypto_data)
        
        assert signal is not None
        assert signal.symbol == "BTC/USDT"
        assert signal.action == SignalAction.BUY
        assert len(crypto_strategy.analyze_calls) == 1
        assert crypto_strategy.signals_generated == 1
    
    def test_process_legacy_data(self, crypto_strategy, sample_legacy_data):
        """Test processing legacy market data."""
        crypto_strategy.mock_signal = TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.SELL,
            confidence=0.7,
            timestamp=datetime.now(),
            strategy_name="test_crypto_strategy"
        )
        
        crypto_strategy.start()
        signal = crypto_strategy.process_market_data(sample_legacy_data)
        
        assert signal is not None
        assert signal.symbol == "BTCUSDT"
        assert signal.action == SignalAction.SELL
        assert len(crypto_strategy.analyze_calls) == 1
    
    def test_market_data_filtering(self, crypto_strategy, sample_crypto_data, sample_forex_data):
        """Test market data filtering."""
        # Mix crypto and forex data
        mixed_data = sample_crypto_data + sample_forex_data
        
        crypto_strategy.start()
        filtered_data = crypto_strategy._filter_market_data(mixed_data)
        
        # Should only contain crypto data
        assert all(data.market_type == MarketType.CRYPTO for data in filtered_data)
        assert len(filtered_data) == len(sample_crypto_data)
    
    def test_symbol_filtering(self, crypto_strategy):
        """Test symbol filtering."""
        # Test allowed symbols
        btc_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        eth_symbol = UnifiedSymbol.from_crypto_symbol("ETHUSDT")
        ada_symbol = UnifiedSymbol.from_crypto_symbol("ADAUSDT")
        
        assert crypto_strategy.apply_market_filter(btc_symbol)  # In allowed list
        assert crypto_strategy.apply_market_filter(eth_symbol)  # In allowed list
        assert not crypto_strategy.apply_market_filter(ada_symbol)  # Not in allowed list
    
    def test_asset_filtering(self, crypto_strategy):
        """Test asset-based filtering."""
        # Test allowed base assets
        btc_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")  # BTC base allowed
        ada_symbol = UnifiedSymbol.from_crypto_symbol("ADAUSDT")  # ADA base not allowed
        
        assert crypto_strategy.apply_market_filter(btc_symbol)
        assert not crypto_strategy.apply_market_filter(ada_symbol)
    
    def test_session_management(self, crypto_strategy):
        """Test session management."""
        # Test setting session status
        crypto_strategy.set_market_session_status(MarketType.CRYPTO, False)
        assert not crypto_strategy.is_market_session_active(MarketType.CRYPTO)
        
        crypto_strategy.set_market_session_status(MarketType.CRYPTO, True)
        assert crypto_strategy.is_market_session_active(MarketType.CRYPTO)
    
    def test_session_info_update(self, crypto_strategy):
        """Test session info updates."""
        session_info = SessionInfo(
            session_name="test_session",
            is_active=False,
            market_type=MarketType.CRYPTO
        )
        
        crypto_strategy.update_session_info(MarketType.CRYPTO, session_info)
        
        # Should update active session status
        assert not crypto_strategy.is_market_session_active(MarketType.CRYPTO)
    
    def test_session_aware_processing(self, crypto_strategy, sample_crypto_data):
        """Test session-aware processing."""
        crypto_strategy.start()
        
        # Set session as inactive
        crypto_strategy.set_market_session_status(MarketType.CRYPTO, False)
        
        signal = crypto_strategy._process_unified_data(sample_crypto_data)
        
        # Should not process when session is inactive
        assert signal is None
        assert len(crypto_strategy.analyze_calls) == 0
    
    def test_session_unaware_processing(self, multi_market_strategy, sample_crypto_data):
        """Test session-unaware processing."""
        multi_market_strategy.mock_signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_multi_strategy"
        )
        
        multi_market_strategy.start()
        
        # Set session as inactive (should be ignored)
        multi_market_strategy.set_market_session_status(MarketType.CRYPTO, False)
        
        signal = multi_market_strategy._process_unified_data(sample_crypto_data)
        
        # Should still process when session-unaware
        assert signal is not None
        assert len(multi_market_strategy.analyze_calls) == 1
    
    def test_market_conditions_validation(self, crypto_strategy, sample_crypto_data):
        """Test market conditions validation."""
        crypto_strategy.start()
        crypto_strategy.mock_conditions_valid = False
        
        signal = crypto_strategy._process_unified_data(sample_crypto_data)
        
        # Should not process when conditions are invalid
        assert signal is None
        assert len(crypto_strategy.analyze_calls) == 0
    
    def test_data_grouping_by_market(self, multi_market_strategy, sample_crypto_data, sample_forex_data):
        """Test data grouping by market type."""
        mixed_data = sample_crypto_data + sample_forex_data
        groups = multi_market_strategy._group_data_by_market(mixed_data)
        
        assert MarketType.CRYPTO in groups
        assert MarketType.FOREX in groups
        assert len(groups[MarketType.CRYPTO]) == len(sample_crypto_data)
        assert len(groups[MarketType.FOREX]) == len(sample_forex_data)
    
    def test_market_data_cache(self, crypto_strategy, sample_crypto_data):
        """Test market data caching."""
        crypto_strategy._update_market_cache(MarketType.CRYPTO, sample_crypto_data)
        
        cached_data = crypto_strategy.get_market_data_cache(MarketType.CRYPTO)
        assert len(cached_data) == len(sample_crypto_data)
        
        # Test cache size limit
        large_data = sample_crypto_data * 200  # Create large dataset
        crypto_strategy._update_market_cache(MarketType.CRYPTO, large_data)
        
        cached_data = crypto_strategy.get_market_data_cache(MarketType.CRYPTO)
        assert len(cached_data) <= 1000  # Should be limited
    
    def test_multi_market_processing(self, multi_market_strategy, sample_crypto_data, sample_forex_data):
        """Test processing data from multiple markets."""
        multi_market_strategy.mock_signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_multi_strategy"
        )
        
        multi_market_strategy.start()
        mixed_data = sample_crypto_data + sample_forex_data
        
        signal = multi_market_strategy._process_unified_data(mixed_data)
        
        assert signal is not None
        assert len(multi_market_strategy.analyze_calls) >= 1
        
        # Verify both market types were processed
        processed_markets = set()
        for _, market_type in multi_market_strategy.analyze_calls:
            processed_markets.add(market_type)
        
        # Should process at least one market (first valid signal wins)
        assert len(processed_markets) >= 1
    
    def test_parameter_validation(self, crypto_strategy_config):
        """Test parameter validation."""
        # Test valid parameters
        strategy = TestMarketSpecificStrategy(crypto_strategy_config, [MarketType.CRYPTO])
        assert strategy.validate_parameters()
        
        # Test invalid market type in filters
        invalid_config = StrategyConfig(
            name="invalid_strategy",
            parameters={'market_filters': {'invalid_market': {}}}
        )
        invalid_strategy = TestMarketSpecificStrategy(invalid_config, [MarketType.CRYPTO])
        assert not invalid_strategy.validate_parameters()
    
    def test_performance_metrics(self, crypto_strategy, sample_crypto_data):
        """Test performance metrics."""
        crypto_strategy.start()
        crypto_strategy._process_unified_data(sample_crypto_data)
        
        metrics = crypto_strategy.get_performance_metrics()
        
        assert metrics['strategy_type'] == 'market_specific'
        assert 'supported_markets' in metrics
        assert 'primary_market' in metrics
        assert 'session_aware' in metrics
        assert 'active_sessions' in metrics
        assert 'market_data_cache_size' in metrics
        assert 'market_filters' in metrics
        
        # Verify market support
        assert 'crypto' in metrics['supported_markets']
        assert metrics['primary_market'] == 'crypto'
    
    def test_insufficient_data_handling(self, crypto_strategy, sample_crypto_data):
        """Test handling of insufficient data."""
        crypto_strategy.start()
        
        # Process insufficient data (less than required length)
        insufficient_data = sample_crypto_data[:3]  # Only 3 data points, need 5
        signal = crypto_strategy._process_unified_data(insufficient_data)
        
        assert signal is None
        assert len(crypto_strategy.analyze_calls) == 0
    
    def test_error_handling_in_analysis(self, crypto_strategy, sample_crypto_data):
        """Test error handling during analysis."""
        def raise_error(data, market_type):
            raise Exception("Analysis error")
        
        crypto_strategy.analyze_market_data = raise_error
        crypto_strategy.start()
        
        signal = crypto_strategy._process_unified_data(sample_crypto_data)
        
        assert signal is None
    
    def test_blocked_symbols_filter(self):
        """Test blocked symbols filtering."""
        config = StrategyConfig(
            name="test_blocked",
            parameters={
                'market_filters': {
                    'forex': {'blocked_symbols': ['USD/JPY']}
                }
            }
        )
        strategy = TestMarketSpecificStrategy(config, [MarketType.FOREX])
        
        eur_symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        jpy_symbol = UnifiedSymbol.from_forex_symbol("USDJPY")
        
        assert strategy.apply_market_filter(eur_symbol)  # Not blocked
        assert not strategy.apply_market_filter(jpy_symbol)  # Blocked
    
    def test_session_info_from_data(self, crypto_strategy):
        """Test session info extraction from data."""
        # Create data with inactive session info
        inactive_session = SessionInfo(
            session_name="test_session",
            is_active=False,
            market_type=MarketType.CRYPTO
        )
        
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        data_with_inactive_session = [
            UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open=Decimal("50000"),
                high=Decimal("51000"),
                low=Decimal("49000"),
                close=Decimal("50500"),
                volume=Decimal("100"),
                source="binance",
                market_type=MarketType.CRYPTO,
                session_info=inactive_session
            )
        ]
        
        crypto_strategy.start()
        
        # Should not process when session info indicates inactive
        is_active = crypto_strategy._is_market_session_active(MarketType.CRYPTO, data_with_inactive_session)
        assert not is_active


if __name__ == "__main__":
    pytest.main([__file__])