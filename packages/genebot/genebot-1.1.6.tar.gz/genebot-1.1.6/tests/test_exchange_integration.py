"""Integration tests for exchange connectivity with configuration system."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from decimal import Decimal

from config.models import ExchangeConfig, ExchangeType
from src.exchanges.ccxt_adapter import CCXTAdapter
from src.exchanges.credential_manager import CredentialManager
from src.models.data_models import OrderSide, OrderType


class TestExchangeIntegration:
    """Integration tests for exchange connectivity."""
    
    @pytest.fixture
    def exchange_config(self):
        """Create a valid exchange configuration."""
        return ExchangeConfig(
            name="demo_binance",
            exchange_type=ExchangeType.BINANCE,
            api_key="valid_api_key_12345678",
            api_secret="valid_api_secret_87654321",
            sandbox=True,
            rate_limit=1200,
            timeout=30,
            enabled=True
        )
    
    @pytest.fixture
    def mock_ccxt_exchange(self):
        """Create a mock CCXT exchange for testing."""
        mock_exchange = AsyncMock()
        mock_exchange.markets = {
            'BTC/USDT': {
                'id': 'BTCUSDT',
                'symbol': 'BTC/USDT',
                'maker': 0.001,
                'taker': 0.001,
                'limits': {'amount': {'min': 0.001}}
            }
        }
        mock_exchange.fees = {
            'trading': {'maker': 0.001, 'taker': 0.001}
        }
        mock_exchange.fetch_time.return_value = 1640995200000
        mock_exchange.fetch_balance.return_value = {
            'USDT': {'free': 1000, 'used': 0, 'total': 1000},
            'BTC': {'free': 0.1, 'used': 0, 'total': 0.1}
        }
        return mock_exchange
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_exchange_adapter_with_pydantic_config(self, mock_ccxt, exchange_config, mock_ccxt_exchange):
        """Test exchange adapter integration with Pydantic configuration."""
        mock_ccxt.binance = lambda config: mock_ccxt_exchange
        
        # Convert Pydantic config to dictionary
        config_dict = {
            'exchange_type': exchange_config.exchange_type.value,
            'api_key': exchange_config.api_key,
            'api_secret': exchange_config.api_secret,
            'sandbox': exchange_config.sandbox,
            'rate_limit': exchange_config.rate_limit,
            'timeout': exchange_config.timeout
        }
        
        # Create adapter with Pydantic-derived config
        adapter = CCXTAdapter(exchange_config.name, config_dict)
        adapter.exchange = mock_ccxt_exchange
        
        # Test connection flow
        await adapter.connect()
        assert adapter.is_connected
        
        await adapter.authenticate()
        assert adapter.is_authenticated
        
        # Test health check
        health = await adapter.health_check()
        assert health['status'] == 'healthy'
        assert health['exchange'] == exchange_config.name
        
        # Test balance retrieval
        balance = await adapter.get_balance()
        assert 'USDT' in balance
        assert balance['USDT']['total'] == Decimal('1000')
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_credential_manager_integration(self, exchange_config):
        """Test credential manager integration with exchange config."""
        manager = CredentialManager(master_password='test_integration_password')
        
        # Extract credentials from Pydantic config
        credentials = {
            'api_key': exchange_config.api_key,
            'api_secret': exchange_config.api_secret
        }
        
        # Test validation
        assert manager.validate_credentials(credentials)
        
        # Test encryption/decryption
        encrypted = manager.encrypt_credentials(credentials)
        decrypted = manager.decrypt_credentials(encrypted)
        
        assert decrypted == credentials
        
        # Test masking
        masked = manager.mask_credentials(credentials)
        assert 'vali...5678' in masked['api_key']
        assert 'vali...4321' in masked['api_secret']
    
    def test_exchange_config_validation(self):
        """Test Pydantic exchange configuration validation."""
        # Valid configuration
        valid_config = ExchangeConfig(
            name="test_exchange",
            exchange_type=ExchangeType.BINANCE,
            api_key="valid_api_key_12345",
            api_secret="valid_api_secret_67890",
            sandbox=True
        )
        assert valid_config.name == "test_exchange"
        assert valid_config.enabled is True  # Default value
        
        # Test validation errors
        with pytest.raises(ValueError):
            ExchangeConfig(
                name="test_exchange",
                exchange_type=ExchangeType.BINANCE,
                api_key="",  # Empty API key should fail
                api_secret="valid_secret",
                sandbox=True
            )
        
        with pytest.raises(ValueError):
            ExchangeConfig(
                name="test_exchange",
                exchange_type=ExchangeType.BINANCE,
                api_key="valid_key",
                api_secret="valid_secret",
                rate_limit=-1,  # Negative rate limit should fail
                sandbox=True
            )
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_multiple_exchange_adapters(self, mock_ccxt, mock_ccxt_exchange):
        """Test managing multiple exchange adapters."""
        mock_ccxt.binance = lambda config: mock_ccxt_exchange
        mock_ccxt.coinbase = lambda config: mock_ccxt_exchange
        
        # Create configurations for multiple exchanges
        binance_config = {
            'exchange_type': 'binance',
            'api_key': 'binance_key_12345',
            'api_secret': 'binance_secret_67890',
            'sandbox': True
        }
        
        coinbase_config = {
            'exchange_type': 'coinbase',
            'api_key': 'coinbase_key_12345',
            'api_secret': 'coinbase_secret_67890',
            'sandbox': True
        }
        
        # Create adapters
        binance_adapter = CCXTAdapter('binance', binance_config)
        coinbase_adapter = CCXTAdapter('coinbase', coinbase_config)
        
        binance_adapter.exchange = mock_ccxt_exchange
        coinbase_adapter.exchange = mock_ccxt_exchange
        
        adapters = [binance_adapter, coinbase_adapter]
        
        try:
            # Connect all adapters
            for adapter in adapters:
                await adapter.connect()
                assert adapter.is_connected
            
            # Test health checks
            health_results = []
            for adapter in adapters:
                health = await adapter.health_check()
                health_results.append(health)
                assert health['status'] == 'healthy'
            
            assert len(health_results) == 2
            
        finally:
            # Disconnect all adapters
            for adapter in adapters:
                await adapter.disconnect()
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_exchange_error_scenarios(self, mock_ccxt, exchange_config, mock_ccxt_exchange):
        """Test error handling in exchange integration."""
        from src.exchanges.exceptions import ConnectionException, AuthenticationException
        import ccxt
        
        mock_ccxt.binance = lambda config: mock_ccxt_exchange
        mock_ccxt.NetworkError = ccxt.NetworkError
        mock_ccxt.AuthenticationError = ccxt.AuthenticationError
        
        config_dict = {
            'exchange_type': exchange_config.exchange_type.value,
            'api_key': exchange_config.api_key,
            'api_secret': exchange_config.api_secret,
            'sandbox': exchange_config.sandbox
        }
        
        adapter = CCXTAdapter(exchange_config.name, config_dict)
        adapter.exchange = mock_ccxt_exchange
        
        # Test connection failure
        mock_ccxt_exchange.load_markets.side_effect = ccxt.NetworkError("Network error")
        
        with pytest.raises(ConnectionException):
            await adapter.connect()
        
        # Reset for authentication test
        mock_ccxt_exchange.load_markets.side_effect = None
        mock_ccxt_exchange.fetch_balance.side_effect = ccxt.AuthenticationError("Invalid API key")
        
        await adapter.connect()  # Should succeed now
        
        with pytest.raises(AuthenticationException):
            await adapter.authenticate()
    
    def test_credential_manager_error_scenarios(self):
        """Test error handling in credential manager."""
        from src.exchanges.exceptions import AuthenticationException
        
        # Test without master password
        manager = CredentialManager()
        
        credentials = {'api_key': 'test_key', 'api_secret': 'test_secret'}
        
        with pytest.raises(AuthenticationException):
            manager.encrypt_credentials(credentials)
        
        # Test with invalid encrypted data
        manager_with_password = CredentialManager(master_password='test_password')
        
        with pytest.raises(AuthenticationException):
            manager_with_password.decrypt_credentials('invalid_encrypted_data')


if __name__ == '__main__':
    pytest.main([__file__])