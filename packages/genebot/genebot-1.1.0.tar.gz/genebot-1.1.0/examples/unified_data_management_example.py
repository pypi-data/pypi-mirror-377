"""Example demonstrating the unified data management system."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.unified_manager import UnifiedDataManager
from src.models.data_models import UnifiedMarketData, MarketData, SessionInfo
from src.markets.types import MarketType, UnifiedSymbol
from src.database.connection import DatabaseManager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Demonstrate unified data management capabilities."""
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create unified data manager
    unified_manager = UnifiedDataManager(db_manager)
    
    logger.info("=== Unified Data Management System Demo ===")
    
    # 1. Create sample crypto data
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
    
    logger.info("1. Storing crypto market data...")
    success = await unified_manager.store_market_data(crypto_data)
    logger.info(f"   Crypto data stored: {success}")
    
    # 2. Create sample forex data
    forex_symbol = UnifiedSymbol(
        base_asset="EUR",
        quote_asset="USD",
        market_type=MarketType.FOREX,
        native_symbol="EURUSD"
    )
    
    forex_session = SessionInfo(
        session_name="london",
        is_active=True,
        next_open=datetime.now(timezone.utc) + timedelta(hours=8),
        next_close=datetime.now(timezone.utc) + timedelta(hours=16),
        market_type=MarketType.FOREX,
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
        session_info=forex_session,
    )
    
    logger.info("2. Storing forex market data with session info...")
    success = await unified_manager.store_market_data(forex_data)
    logger.info(f"   Forex data stored: {success}")
    
    # 3. Store session information
    logger.info("3. Storing session information...")
    success = await unified_manager.store_session_info(MarketType.FOREX, forex_session)
    logger.info(f"   Session info stored: {success}")
    
    # 4. Demonstrate legacy data conversion
    legacy_data = MarketData(
        symbol="ETHUSDT",
        timestamp=datetime.now(timezone.utc),
        open=Decimal("3000.00"),
        high=Decimal("3100.00"),
        low=Decimal("2950.00"),
        close=Decimal("3050.00"),
        volume=Decimal("50.25"),
        exchange="coinbase",
    )
    
    logger.info("4. Converting and storing legacy market data...")
    success = await unified_manager.store_market_data(
        legacy_data, 
        market_type=MarketType.CRYPTO
    )
    logger.info(f"   Legacy data converted and stored: {success}")
    
    # 5. Retrieve latest data
    logger.info("5. Retrieving latest market data...")
    latest_crypto = await unified_manager.get_latest_market_data(crypto_symbol)
    if latest_crypto:
        logger.info(f"   Latest BTC/USDT: {latest_crypto.close} at {latest_crypto.timestamp}")
    
    latest_forex = await unified_manager.get_latest_market_data(forex_symbol)
    if latest_forex:
        logger.info(f"   Latest EUR/USD: {latest_forex.close} at {latest_forex.timestamp}")
    
    # 6. Retrieve historical data
    logger.info("6. Retrieving historical data...")
    start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    end_time = datetime.now(timezone.utc)
    
    crypto_history = await unified_manager.get_market_data(
        crypto_symbol, start_time, end_time
    )
    logger.info(f"   Retrieved {len(crypto_history)} crypto data points")
    
    # 7. Cross-market data retrieval
    logger.info("7. Retrieving cross-market data...")
    symbols = [crypto_symbol, forex_symbol]
    cross_market_data = await unified_manager.get_cross_market_data(
        symbols, start_time, end_time
    )
    logger.info(f"   Cross-market data for {len(cross_market_data)} symbols:")
    for symbol_key, data_list in cross_market_data.items():
        logger.info(f"     {symbol_key}: {len(data_list)} data points")
    
    # 8. Retrieve session information
    logger.info("8. Retrieving session information...")
    session_info = await unified_manager.get_session_info(MarketType.FOREX)
    if session_info:
        logger.info(f"   Forex session: {session_info.session_name}, active: {session_info.is_active}")
    
    # 9. Get data statistics
    logger.info("9. Retrieving data statistics...")
    stats = await unified_manager.get_data_statistics()
    logger.info("   Data statistics:")
    for key, value in stats.items():
        logger.info(f"     {key}: {value}")
    
    # 10. Demonstrate data normalization
    logger.info("10. Demonstrating raw data normalization...")
    
    # Raw crypto data from exchange
    raw_crypto_data = {
        'symbol': 'ADAUSDT',
        'timestamp': 1640995200,  # Unix timestamp
        'open': 1.5000,
        'high': 1.5500,
        'low': 1.4500,
        'close': 1.5250,
        'volume': 1000000,
    }
    
    normalized_crypto = unified_manager.normalizer.normalize_raw_data(
        raw_crypto_data, MarketType.CRYPTO, "binance"
    )
    logger.info(f"   Normalized crypto: {normalized_crypto.symbol.to_standard_format()}")
    
    # Raw forex data from broker
    raw_forex_data = {
        'symbol': 'GBPUSD',
        'timestamp': '2024-01-01T12:00:00Z',
        'open': 1.2500,
        'high': 1.2550,
        'low': 1.2450,
        'close': 1.2525,
        'volume': 500000,
    }
    
    normalized_forex = unified_manager.normalizer.normalize_raw_data(
        raw_forex_data, MarketType.FOREX, "oanda"
    )
    logger.info(f"   Normalized forex: {normalized_forex.symbol.to_standard_format()}")
    
    # Store the normalized data
    await unified_manager.store_market_data(normalized_crypto)
    await unified_manager.store_market_data(normalized_forex)
    logger.info("   Normalized data stored successfully")
    
    # 11. Demonstrate cache functionality
    logger.info("11. Demonstrating cache functionality...")
    
    # This will use cached symbol
    cached_data = await unified_manager.get_latest_market_data(
        "BTCUSDT", market_type=MarketType.CRYPTO
    )
    if cached_data:
        logger.info(f"   Cached lookup successful: {cached_data.symbol.to_standard_format()}")
    
    # Clear cache
    unified_manager.clear_cache()
    logger.info("   Cache cleared")
    
    logger.info("=== Demo completed successfully! ===")


if __name__ == "__main__":
    asyncio.run(main())