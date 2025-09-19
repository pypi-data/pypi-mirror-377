"""Example usage of exchange connectivity functionality."""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timezone

from src.exchanges.ccxt_adapter import CCXTAdapter
from src.exchanges.credential_manager import CredentialManager
from src.exchanges.exceptions import ExchangeException, ConnectionException, AuthenticationException
from src.models.data_models import OrderSide, OrderType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demonstrate_exchange_connectivity():
    """Demonstrate exchange connectivity features."""
    
    # Example configuration for Binance testnet
    config = {
        'exchange_type': 'binance',
        'api_key': 'your_testnet_api_key_here',
        'api_secret': 'your_testnet_api_secret_here',
        'sandbox': True,  # Use testnet
        'rate_limit': 1200,
        'timeout': 30
    }
    
    # Initialize credential manager
    credential_manager = CredentialManager(master_password='demo_password_123')
    
    # Validate credentials format
    if not credential_manager.validate_credentials(config):
        logger.error("Invalid credentials format")
        return
    
    # Create exchange adapter
    adapter = CCXTAdapter('binance_testnet', config)
    
    try:
        logger.info("=== Exchange Connectivity Demo ===")
        
        # 1. Connect to exchange
        logger.info("1. Connecting to exchange...")
        await adapter.connect()
        logger.info(f"Connected: {adapter.is_connected}")
        
        # 2. Authenticate (if real credentials provided)
        if config['api_key'] != 'your_testnet_api_key_here':
            logger.info("2. Authenticating...")
            await adapter.authenticate()
            logger.info(f"Authenticated: {adapter.is_authenticated}")
        else:
            logger.info("2. Skipping authentication (demo credentials)")
        
        # 3. Health check
        logger.info("3. Performing health check...")
        health = await adapter.health_check()
        logger.info(f"Health status: {health['status']}")
        logger.info(f"Latency: {health.get('latency_ms', 'N/A')} ms")
        
        # 4. Get available markets
        logger.info("4. Fetching available markets...")
        markets = await adapter.get_markets()
        logger.info(f"Available markets: {len(markets)}")
        
        # Show first few markets
        market_symbols = list(markets.keys())[:5]
        logger.info(f"Sample markets: {market_symbols}")
        
        # 5. Get ticker data
        if 'BTC/USDT' in markets:
            logger.info("5. Fetching BTC/USDT ticker...")
            ticker = await adapter.get_ticker('BTC/USDT')
            logger.info(f"BTC/USDT price: ${ticker.get('last', 'N/A')}")
        
        # 6. Get order book
        if 'BTC/USDT' in markets:
            logger.info("6. Fetching BTC/USDT order book...")
            orderbook = await adapter.get_orderbook('BTC/USDT', limit=5)
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else 'N/A'
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else 'N/A'
            logger.info(f"Best bid: ${best_bid}, Best ask: ${best_ask}")
        
        # 7. Get OHLCV data
        if 'BTC/USDT' in markets:
            logger.info("7. Fetching BTC/USDT OHLCV data...")
            ohlcv = await adapter.get_ohlcv('BTC/USDT', '1h', limit=5)
            logger.info(f"Retrieved {len(ohlcv)} candles")
            if ohlcv:
                latest = ohlcv[-1]
                logger.info(f"Latest candle: O:{latest.open} H:{latest.high} L:{latest.low} C:{latest.close}")
        
        # 8. Get account balance (if authenticated)
        if adapter.is_authenticated:
            logger.info("8. Fetching account balance...")
            balance = await adapter.get_balance()
            logger.info("Account balances:")
            for currency, amounts in balance.items():
                if amounts['total'] > 0:
                    logger.info(f"  {currency}: {amounts['total']} (free: {amounts['free']})")
        else:
            logger.info("8. Skipping balance check (not authenticated)")
        
        # 9. Trading fees
        logger.info("9. Getting trading fees...")
        fees = adapter.get_trading_fees('BTC/USDT')
        logger.info(f"Trading fees - Maker: {fees['maker']}, Taker: {fees['taker']}")
        
        # 10. Minimum order size
        if 'BTC/USDT' in markets:
            min_size = adapter.get_minimum_order_size('BTC/USDT')
            logger.info(f"Minimum order size for BTC/USDT: {min_size}")
        
        logger.info("=== Demo completed successfully ===")
        
    except ConnectionException as e:
        logger.error(f"Connection error: {e}")
    except AuthenticationException as e:
        logger.error(f"Authentication error: {e}")
    except ExchangeException as e:
        logger.error(f"Exchange error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Always disconnect
        await adapter.disconnect()
        logger.info("Disconnected from exchange")


async def demonstrate_credential_management():
    """Demonstrate credential management features."""
    
    logger.info("\n=== Credential Management Demo ===")
    
    # Initialize credential manager
    manager = CredentialManager(master_password='demo_password_123')
    
    # Sample credentials
    credentials = {
        'api_key': 'sample_api_key_12345678',
        'api_secret': 'sample_api_secret_87654321',
        'api_passphrase': 'sample_passphrase'
    }
    
    # 1. Validate credentials
    logger.info("1. Validating credentials...")
    is_valid = manager.validate_credentials(credentials)
    logger.info(f"Credentials valid: {is_valid}")
    
    # 2. Mask credentials for logging
    logger.info("2. Masking credentials for safe logging...")
    masked = manager.mask_credentials(credentials)
    logger.info(f"Masked credentials: {masked}")
    
    # 3. Encrypt credentials
    logger.info("3. Encrypting credentials...")
    encrypted = manager.encrypt_credentials(credentials)
    logger.info(f"Encrypted credentials length: {len(encrypted)} characters")
    
    # 4. Decrypt credentials
    logger.info("4. Decrypting credentials...")
    decrypted = manager.decrypt_credentials(encrypted)
    logger.info(f"Decryption successful: {decrypted == credentials}")
    
    # 5. Generate new master key
    logger.info("5. Generating new master key...")
    new_key = CredentialManager.generate_master_key()
    logger.info(f"New master key generated (length: {len(new_key)})")
    
    logger.info("=== Credential management demo completed ===")


async def demonstrate_error_handling():
    """Demonstrate error handling scenarios."""
    
    logger.info("\n=== Error Handling Demo ===")
    
    # Test with invalid configuration
    invalid_config = {
        'exchange_type': 'nonexistent_exchange',
        'api_key': '',
        'api_secret': '',
        'sandbox': True
    }
    
    try:
        logger.info("1. Testing with invalid exchange type...")
        adapter = CCXTAdapter('invalid_exchange', invalid_config)
        # This should fail during initialization or connection
        
    except Exception as e:
        logger.info(f"Expected error caught: {type(e).__name__}: {e}")
    
    # Test credential validation
    logger.info("2. Testing credential validation...")
    manager = CredentialManager(master_password='test_password')
    
    invalid_credentials = [
        {'api_key': '', 'api_secret': 'valid_secret'},  # Empty key
        {'api_key': 'short', 'api_secret': 'valid_secret_12345'},  # Too short
        {'api_key': 'your_api_key', 'api_secret': 'valid_secret_12345'},  # Invalid pattern
    ]
    
    for i, creds in enumerate(invalid_credentials, 1):
        is_valid = manager.validate_credentials(creds)
        logger.info(f"  Test {i}: Valid = {is_valid} (expected: False)")
    
    logger.info("=== Error handling demo completed ===")


async def main():
    """Main demo function."""
    try:
        await demonstrate_exchange_connectivity()
        await demonstrate_credential_management()
        await demonstrate_error_handling()
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")


if __name__ == '__main__':
    # Run the demo
    asyncio.run(main())