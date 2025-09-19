"""Integration tests for unified data management system."""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock

from src.data.unified_manager import UnifiedDataManager
from src.data.normalizer import MarketDataNormalizer
from src.data.cross_market_store import CrossMarketDataStore
from src.models.data_models import UnifiedMarketData, MarketData, SessionInfo
from src.markets.types import MarketType, UnifiedSymbol
from src.database.connection import DatabaseManager


class TestUnifiedDataManager:
    """Test cases for UnifiedDataManager."""
    
    @pytest.fixture
    def mock_database_manager(self):
        """Create mock database manager."""
        return Mock(spec=DatabaseManager)
    
    @pytest.fixture
    def unified_manager(self, mock_database_manager):
        """Create UnifiedDataManager instance."""
        return UnifiedDataManager(mock_database_manager)
    
    @pytest.fixture
    def sample_crypto_symbol(self):
        """Create sample crypto symbol."""
        return UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USDT",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSDT"
        )
    
    @pytest.fixture
    def sample_forex_symbol(self):
        """Create sample forex symbol."""
        return UnifiedSymbol(
            base_asset="EUR",
            quote_asset="USD",
            market_type=MarketType.FOREX,
            native_symbol="EURUSD"
        )
    
    @pytest.fixture
    def sample_unified_data(self, sample_crypto_symbol):
        """Create sample unified market data."""
        return UnifiedMarketData(
            symbol=sample_crypto_symbol,
            timestamp=datetime.now(timezone.utc),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49500.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            source="binance",
            market_type=MarketType.CRYPTO,
        )
    
    @pytest.fixture
    def sample_legacy_data(self):
        """Create sample legacy market data."""
        return MarketData(
            symbol="BTCUSDT",
            timestamp=datetime.now(timezone.utc),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49500.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            exchange="binance",
        )
    
    @pytest.fixture
    def sample_session_info(self):
        """Create sample session info."""
        return SessionInfo(
            session_name="london",
            is_active=True,
            next_open=datetime.now(timezone.utc) + timedelta(hours=8),
            next_close=datetime.now(timezone.utc) + timedelta(hours=16),
            market_type=MarketType.FOREX,
        )
    
    @pytest.mark.asyncio
    async def test_store_unified_market_data(self, unified_manager, sample_unified_data):
        """Test storing unified market data."""
        # Mock the cross-market store
        unified_manager.cross_market_store.store_unified_data = AsyncMock(return_value=True)
        
        # Store the data
        result = await unified_manager.store_market_data(sample_unified_data)
        
        # Verify result
        assert result is True
        unified_manager.cross_market_store.store_unified_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_legacy_market_data(self, unified_manager, sample_legacy_data):
        """Test storing legacy market data with conversion."""
        # Mock the cross-market store
        unified_manager.cross_market_store.store_unified_data = AsyncMock(return_value=True)
        
        # Store the legacy data
        result = await unified_manager.store_market_data(
            sample_legacy_data, 
            market_type=MarketType.CRYPTO
        )
        
        # Verify result
        assert result is True
        unified_manager.cross_market_store.store_unified_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_legacy_data_without_market_type_fails(self, unified_manager, sample_legacy_data):
        """Test that storing legacy data without market type fails."""
        result = await unified_manager.store_market_data(sample_legacy_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_market_data(self, unified_manager, sample_crypto_symbol, sample_unified_data):
        """Test retrieving market data."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc)
        
        # Mock the cross-market store
        unified_manager.cross_market_store.get_unified_data = AsyncMock(
            return_value=[sample_unified_data]
        )
        
        # Get the data
        result = await unified_manager.get_market_data(
            sample_crypto_symbol, start_time, end_time
        )
        
        # Verify result
        assert len(result) == 1
        assert result[0] == sample_unified_data
        unified_manager.cross_market_store.get_unified_data.assert_called_once_with(
            sample_crypto_symbol, start_time, end_time, None
        )
    
    @pytest.mark.asyncio
    async def test_get_market_data_with_string_symbol(self, unified_manager, sample_unified_data):
        """Test retrieving market data using string symbol."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc)
        
        # Mock the cross-market store
        unified_manager.cross_market_store.get_unified_data = AsyncMock(
            return_value=[sample_unified_data]
        )
        
        # Get the data using string symbol
        result = await unified_manager.get_market_data(
            "BTCUSDT", start_time, end_time, market_type=MarketType.CRYPTO
        )
        
        # Verify result
        assert len(result) == 1
        unified_manager.cross_market_store.get_unified_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_latest_market_data(self, unified_manager, sample_crypto_symbol, sample_unified_data):
        """Test retrieving latest market data."""
        # Mock the cross-market store
        unified_manager.cross_market_store.get_latest_data = AsyncMock(
            return_value=sample_unified_data
        )
        
        # Get latest data
        result = await unified_manager.get_latest_market_data(sample_crypto_symbol)
        
        # Verify result
        assert result == sample_unified_data
        unified_manager.cross_market_store.get_latest_data.assert_called_once_with(
            sample_crypto_symbol, None
        )
    
    @pytest.mark.asyncio
    async def test_get_cross_market_data(self, unified_manager, sample_crypto_symbol, 
                                       sample_forex_symbol, sample_unified_data):
        """Test retrieving cross-market data."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc)
        
        # Mock the cross-market store
        unified_manager.cross_market_store.get_unified_data = AsyncMock(
            return_value=[sample_unified_data]
        )
        
        # Get cross-market data
        symbols = [sample_crypto_symbol, sample_forex_symbol]
        result = await unified_manager.get_cross_market_data(symbols, start_time, end_time)
        
        # Verify result
        assert len(result) == 2
        assert "BTC/USDT" in result
        assert "EUR/USD" in result
        assert unified_manager.cross_market_store.get_unified_data.call_count == 2
    
    @pytest.mark.asyncio
    async def test_store_session_info(self, unified_manager, sample_session_info):
        """Test storing session information."""
        # Mock the cross-market store
        unified_manager.cross_market_store.store_session_info = AsyncMock(return_value=True)
        
        # Store session info
        result = await unified_manager.store_session_info(
            MarketType.FOREX, sample_session_info
        )
        
        # Verify result
        assert result is True
        unified_manager.cross_market_store.store_session_info.assert_called_once_with(
            MarketType.FOREX, sample_session_info
        )
    
    @pytest.mark.asyncio
    async def test_get_session_info(self, unified_manager, sample_session_info):
        """Test retrieving session information."""
        # Mock the cross-market store
        unified_manager.cross_market_store.get_session_info = AsyncMock(
            return_value=sample_session_info
        )
        
        # Get session info
        result = await unified_manager.get_session_info(MarketType.FOREX)
        
        # Verify result
        assert result == sample_session_info
        unified_manager.cross_market_store.get_session_info.assert_called_once_with(
            MarketType.FOREX
        )
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, unified_manager):
        """Test cleaning up old data."""
        # Mock the cross-market store
        unified_manager.cross_market_store.cleanup_old_data = AsyncMock(return_value=True)
        
        # Cleanup old data
        result = await unified_manager.cleanup_old_data(retention_days=30)
        
        # Verify result
        assert result is True
        unified_manager.cross_market_store.cleanup_old_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_data_statistics(self, unified_manager):
        """Test retrieving data statistics."""
        expected_stats = {
            'total_records': 1000,
            'crypto_records': 600,
            'forex_records': 400,
            'unique_symbols': 50,
        }
        
        # Mock the cross-market store
        unified_manager.cross_market_store.get_data_statistics = AsyncMock(
            return_value=expected_stats
        )
        
        # Get statistics
        result = await unified_manager.get_data_statistics()
        
        # Verify result
        assert result == expected_stats
        unified_manager.cross_market_store.get_data_statistics.assert_called_once()
    
    def test_clear_cache(self, unified_manager):
        """Test clearing internal caches."""
        # Add some items to cache
        unified_manager._symbol_cache["test"] = Mock()
        unified_manager._session_cache[MarketType.CRYPTO] = Mock()
        
        # Clear cache
        unified_manager.clear_cache()
        
        # Verify cache is empty
        assert len(unified_manager._symbol_cache) == 0
        assert len(unified_manager._session_cache) == 0


class TestMarketDataNormalizer:
    """Test cases for MarketDataNormalizer."""
    
    @pytest.fixture
    def normalizer(self):
        """Create MarketDataNormalizer instance."""
        return MarketDataNormalizer()
    
    @pytest.fixture
    def sample_crypto_data(self):
        """Create sample crypto data."""
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USDT",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSDT"
        )
        
        return UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            open=Decimal("50000.12345678"),
            high=Decimal("51000.87654321"),
            low=Decimal("49500.11111111"),
            close=Decimal("50500.99999999"),
            volume=Decimal("100.12345678"),
            source="  BINANCE  ",  # Test normalization
            market_type=MarketType.CRYPTO,
        )
    
    def test_normalize_market_data(self, normalizer, sample_crypto_data):
        """Test normalizing market data."""
        result = normalizer.normalize_market_data(sample_crypto_data)
        
        # Verify normalization
        assert result.source == "binance"  # Normalized to lowercase
        assert result.timestamp.tzinfo == timezone.utc
        assert isinstance(result.open, Decimal)
        assert isinstance(result.high, Decimal)
        assert isinstance(result.low, Decimal)
        assert isinstance(result.close, Decimal)
        assert isinstance(result.volume, Decimal)
    
    def test_normalize_raw_crypto_data(self, normalizer):
        """Test normalizing raw crypto data."""
        raw_data = {
            'symbol': 'BTCUSDT',
            'timestamp': 1640995200,  # Unix timestamp
            'open': 50000.0,
            'high': 51000.0,
            'low': 49500.0,
            'close': 50500.0,
            'volume': 100.5,
        }
        
        result = normalizer.normalize_raw_data(raw_data, MarketType.CRYPTO, "binance")
        
        # Verify result
        assert result.symbol.base_asset == "BTC"
        assert result.symbol.quote_asset == "USDT"
        assert result.market_type == MarketType.CRYPTO
        assert result.source == "binance"
        assert isinstance(result.timestamp, datetime)
    
    def test_normalize_raw_forex_data(self, normalizer):
        """Test normalizing raw forex data."""
        raw_data = {
            'symbol': 'EURUSD',
            'timestamp': '2024-01-01T12:00:00Z',
            'open': 1.1000,
            'high': 1.1050,
            'low': 1.0950,
            'close': 1.1025,
            'volume': 1000000,
        }
        
        result = normalizer.normalize_raw_data(raw_data, MarketType.FOREX, "oanda")
        
        # Verify result
        assert result.symbol.base_asset == "EUR"
        assert result.symbol.quote_asset == "USD"
        assert result.market_type == MarketType.FOREX
        assert result.source == "oanda"
        assert isinstance(result.timestamp, datetime)
    
    def test_normalize_asset_name(self, normalizer):
        """Test asset name normalization."""
        # Test common mappings
        assert normalizer._normalize_asset_name("BITCOIN") == "BTC"
        assert normalizer._normalize_asset_name("ETHEREUM") == "ETH"
        assert normalizer._normalize_asset_name("TETHER") == "USDT"
        
        # Test unknown asset (should remain unchanged)
        assert normalizer._normalize_asset_name("UNKNOWN") == "UNKNOWN"
    
    def test_round_decimal(self, normalizer):
        """Test decimal rounding."""
        value = Decimal("123.123456789")
        
        # Test different precisions
        assert normalizer._round_decimal(value, 2) == Decimal("123.12")
        assert normalizer._round_decimal(value, 4) == Decimal("123.1235")
        assert normalizer._round_decimal(value, 8) == Decimal("123.12345679")


class TestCrossMarketDataStore:
    """Test cases for CrossMarketDataStore."""
    
    @pytest.fixture
    def mock_database_manager(self):
        """Create mock database manager."""
        mock_db = Mock(spec=DatabaseManager)
        mock_session = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_session)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_db.get_session.return_value = mock_context_manager
        return mock_db
    
    @pytest.fixture
    def data_store(self, mock_database_manager):
        """Create CrossMarketDataStore instance."""
        return CrossMarketDataStore(mock_database_manager)
    
    @pytest.fixture
    def sample_unified_data(self):
        """Create sample unified market data."""
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USDT",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSDT"
        )
        
        return UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49500.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            source="binance",
            market_type=MarketType.CRYPTO,
        )
    
    @pytest.mark.asyncio
    async def test_store_unified_data(self, data_store, sample_unified_data, mock_database_manager):
        """Test storing unified data."""
        # Mock session operations
        mock_session = mock_database_manager.get_session.return_value.__enter__.return_value
        
        # Store data
        result = await data_store.store_unified_data(sample_unified_data)
        
        # Verify result
        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_unified_data(self, data_store, mock_database_manager):
        """Test retrieving unified data."""
        # Mock database query results
        mock_session = mock_database_manager.get_session.return_value.__enter__.return_value
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USDT",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSDT"
        )
        
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc)
        
        # Get data
        result = await data_store.get_unified_data(symbol, start_time, end_time)
        
        # Verify result
        assert isinstance(result, list)
        mock_session.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_session_info(self, data_store, mock_database_manager):
        """Test storing session information."""
        # Mock session operations
        mock_session = mock_database_manager.get_session.return_value.__enter__.return_value
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # No existing session
        
        session_info = SessionInfo(
            session_name="london",
            is_active=True,
            market_type=MarketType.FOREX,
        )
        
        # Store session info
        result = await data_store.store_session_info(MarketType.FOREX, session_info)
        
        # Verify result
        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, data_store, mock_database_manager):
        """Test cleaning up old data."""
        # Mock session operations
        mock_session = mock_database_manager.get_session.return_value.__enter__.return_value
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 100  # Mock deleted count
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Cleanup data
        result = await data_store.cleanup_old_data(cutoff_date)
        
        # Verify result
        assert result is True
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_data_statistics(self, data_store, mock_database_manager):
        """Test retrieving data statistics."""
        # Mock session operations
        mock_session = mock_database_manager.get_session.return_value.__enter__.return_value
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.count.return_value = 1000
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.first.return_value = (
            datetime.now(timezone.utc) - timedelta(days=30),
            datetime.now(timezone.utc)
        )
        
        # Get statistics
        result = await data_store.get_data_statistics()
        
        # Verify result
        assert isinstance(result, dict)
        assert 'total_records' in result
        assert 'crypto_records' in result
        assert 'forex_records' in result


@pytest.mark.integration
class TestUnifiedDataIntegration:
    """Integration tests for the complete unified data management system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self):
        """Test complete data flow from storage to retrieval."""
        # This would require a real database connection
        # For now, we'll test the component integration with mocks
        
        # Mock database manager
        mock_db = Mock(spec=DatabaseManager)
        mock_session = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_session)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_db.get_session.return_value = mock_context_manager
        
        # Create unified manager
        manager = UnifiedDataManager(mock_db)
        
        # Create test data
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USDT",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSDT"
        )
        
        test_data = UnifiedMarketData(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49500.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            source="binance",
            market_type=MarketType.CRYPTO,
        )
        
        # Test storage
        store_result = await manager.store_market_data(test_data)
        assert store_result is True
        
        # Verify session operations were called
        mock_session.add.assert_called()
        mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_multi_market_data_handling(self):
        """Test handling data from multiple markets."""
        # Mock database manager
        mock_db = Mock(spec=DatabaseManager)
        mock_session = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_session)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_db.get_session.return_value = mock_context_manager
        
        # Create unified manager
        manager = UnifiedDataManager(mock_db)
        
        # Create crypto data
        crypto_symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USDT",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSDT"
        )
        
        crypto_data = UnifiedMarketData(
            symbol=crypto_symbol,
            timestamp=datetime.now(timezone.utc),
            open=Decimal("50000.00"),
            high=Decimal("51000.00"),
            low=Decimal("49500.00"),
            close=Decimal("50500.00"),
            volume=Decimal("100.5"),
            source="binance",
            market_type=MarketType.CRYPTO,
        )
        
        # Create forex data
        forex_symbol = UnifiedSymbol(
            base_asset="EUR",
            quote_asset="USD",
            market_type=MarketType.FOREX,
            native_symbol="EURUSD"
        )
        
        forex_data = UnifiedMarketData(
            symbol=forex_symbol,
            timestamp=datetime.now(timezone.utc),
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0950"),
            close=Decimal("1.1025"),
            volume=Decimal("1000000"),
            source="oanda",
            market_type=MarketType.FOREX,
        )
        
        # Store both types of data
        crypto_result = await manager.store_market_data(crypto_data)
        forex_result = await manager.store_market_data(forex_data)
        
        # Verify both succeeded
        assert crypto_result is True
        assert forex_result is True
        
        # Verify session operations were called for both
        assert mock_session.add.call_count == 2
        assert mock_session.commit.call_count == 2