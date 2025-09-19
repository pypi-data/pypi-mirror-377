"""Unit tests for exchange adapters and related functionality."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, Any

from src.exchanges.base import ExchangeAdapter
from src.exchanges.ccxt_adapter import CCXTAdapter
from src.exchanges.credential_manager import CredentialManager
from src.exchanges.exceptions import (
    ExchangeException, ConnectionException, AuthenticationException,
    RateLimitException, InsufficientFundsException, OrderException
)
from src.models.data_models import MarketData, Order, Position, OrderSide, OrderType, OrderStatus


class MockExchangeAdapter(ExchangeAdapter):
    """Mock implementation of ExchangeAdapter for testing."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.mock_connected = False
        self.mock_authenticated = False
    
    async def connect(self) -> bool:
        self.mock_connected = True
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        self.mock_connected = False
        self._connected = False
    
    async def authenticate(self) -> bool:
        self.mock_authenticated = True
        self._authenticated = True
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        return {'status': 'healthy', 'exchange': self.name}
    
    async def get_markets(self) -> Dict[str, Dict[str, Any]]:
        return {'BTC/USDT': {'id': 'BTCUSDT', 'symbol': 'BTC/USDT'}}
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        return {'symbol': symbol, 'last': 50000.0}
    
    async def get_orderbook(self, symbol: str, limit=None) -> Dict[str, Any]:
        return {'bids': [[49000, 1.0]], 'asks': [[51000, 1.0]]}
    
    async def get_ohlcv(self, symbol: str, timeframe: str = '1h', since=None, limit=None):
        return [MarketData(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            open=Decimal('50000'),
            high=Decimal('51000'),
            low=Decimal('49000'),
            close=Decimal('50500'),
            volume=Decimal('100'),
            exchange=self.name
        )]
    
    async def get_balance(self) -> Dict[str, Dict[str, Decimal]]:
        return {
            'USDT': {'free': Decimal('1000'), 'used': Decimal('0'), 'total': Decimal('1000')},
            'BTC': {'free': Decimal('0.1'), 'used': Decimal('0'), 'total': Decimal('0.1')}
        }
    
    async def create_order(self, symbol: str, side: OrderSide, amount: Decimal,
                          order_type: OrderType = OrderType.MARKET, price=None, params=None):
        return Order(
            id='test_order_123',
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            order_type=order_type,
            status=OrderStatus.OPEN,
            timestamp=datetime.now(timezone.utc),
            exchange=self.name
        )
    
    async def cancel_order(self, order_id: str, symbol: str):
        return Order(
            id=order_id,
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal('1'),
            price=Decimal('50000'),
            order_type=OrderType.LIMIT,
            status=OrderStatus.CANCELLED,
            timestamp=datetime.now(timezone.utc),
            exchange=self.name
        )
    
    async def get_order(self, order_id: str, symbol: str):
        return Order(
            id=order_id,
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal('1'),
            price=Decimal('50000'),
            order_type=OrderType.LIMIT,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(timezone.utc),
            exchange=self.name
        )
    
    async def get_open_orders(self, symbol=None):
        return []
    
    async def get_order_history(self, symbol=None, since=None, limit=None):
        return []
    
    async def get_positions(self, symbol=None):
        return []
    
    async def get_trades(self, symbol=None, since=None, limit=None):
        return []
    
    def validate_credentials(self) -> bool:
        return True
    
    def get_trading_fees(self, symbol=None):
        return {'maker': Decimal('0.001'), 'taker': Decimal('0.001')}
    
    def get_minimum_order_size(self, symbol: str):
        return Decimal('0.001')


class TestExchangeAdapter:
    """Test cases for ExchangeAdapter base class."""
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        config = {'api_key': 'test_key', 'api_secret': 'test_secret'}
        adapter = MockExchangeAdapter('test_exchange', config)
        
        assert adapter.name == 'test_exchange'
        assert adapter.config == config
        assert not adapter.is_connected
        assert not adapter.is_authenticated
    
    @pytest.mark.asyncio
    async def test_adapter_connection_flow(self):
        """Test connection and disconnection flow."""
        config = {'api_key': 'test_key', 'api_secret': 'test_secret'}
        adapter = MockExchangeAdapter('test_exchange', config)
        
        # Test connection
        result = await adapter.connect()
        assert result is True
        assert adapter.is_connected
        
        # Test disconnection
        await adapter.disconnect()
        assert not adapter.is_connected
    
    @pytest.mark.asyncio
    async def test_adapter_authentication(self):
        """Test authentication flow."""
        config = {'api_key': 'test_key', 'api_secret': 'test_secret'}
        adapter = MockExchangeAdapter('test_exchange', config)
        
        result = await adapter.authenticate()
        assert result is True
        assert adapter.is_authenticated
    
    @pytest.mark.asyncio
    async def test_adapter_market_data_methods(self):
        """Test market data retrieval methods."""
        config = {'api_key': 'test_key', 'api_secret': 'test_secret'}
        adapter = MockExchangeAdapter('test_exchange', config)
        
        # Test get_markets
        markets = await adapter.get_markets()
        assert 'BTC/USDT' in markets
        
        # Test get_ticker
        ticker = await adapter.get_ticker('BTC/USDT')
        assert ticker['symbol'] == 'BTC/USDT'
        
        # Test get_orderbook
        orderbook = await adapter.get_orderbook('BTC/USDT')
        assert 'bids' in orderbook
        assert 'asks' in orderbook
        
        # Test get_ohlcv
        ohlcv = await adapter.get_ohlcv('BTC/USDT')
        assert len(ohlcv) > 0
        assert isinstance(ohlcv[0], MarketData)
    
    @pytest.mark.asyncio
    async def test_adapter_trading_methods(self):
        """Test trading-related methods."""
        config = {'api_key': 'test_key', 'api_secret': 'test_secret'}
        adapter = MockExchangeAdapter('test_exchange', config)
        
        # Test get_balance
        balance = await adapter.get_balance()
        assert 'USDT' in balance
        assert 'BTC' in balance
        
        # Test create_order
        order = await adapter.create_order(
            'BTC/USDT', OrderSide.BUY, Decimal('0.1'), OrderType.MARKET
        )
        assert isinstance(order, Order)
        assert order.symbol == 'BTC/USDT'
        assert order.side == OrderSide.BUY
        
        # Test cancel_order
        cancelled_order = await adapter.cancel_order('test_order_123', 'BTC/USDT')
        assert cancelled_order.status == OrderStatus.CANCELLED
        
        # Test get_order
        fetched_order = await adapter.get_order('test_order_123', 'BTC/USDT')
        assert fetched_order.id == 'test_order_123'
    
    def test_adapter_string_representations(self):
        """Test string representations of adapter."""
        config = {'api_key': 'test_key', 'api_secret': 'test_secret'}
        adapter = MockExchangeAdapter('test_exchange', config)
        
        str_repr = str(adapter)
        assert 'MockExchangeAdapter' in str_repr
        assert 'test_exchange' in str_repr
        
        repr_str = repr(adapter)
        assert 'MockExchangeAdapter' in repr_str
        assert 'test_exchange' in repr_str
        assert 'connected=False' in repr_str


class TestCCXTAdapter:
    """Test cases for CCXTAdapter."""
    
    @pytest.fixture
    def mock_ccxt_exchange(self):
        """Create a mock CCXT exchange."""
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
        return mock_exchange
    
    @pytest.fixture
    def adapter_config(self):
        """Create adapter configuration."""
        return {
            'exchange_type': 'binance',
            'api_key': 'test_api_key_12345',
            'api_secret': 'test_api_secret_67890',
            'sandbox': True,
            'rate_limit': 1200,
            'timeout': 30
        }
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    def test_ccxt_adapter_initialization(self, mock_ccxt, adapter_config):
        """Test CCXT adapter initialization."""
        mock_exchange_class = Mock()
        mock_ccxt.binance = mock_exchange_class
        
        adapter = CCXTAdapter('test_binance', adapter_config)
        
        assert adapter.name == 'test_binance'
        assert adapter.config == adapter_config
        mock_exchange_class.assert_called_once()
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_ccxt_adapter_connection(self, mock_ccxt, adapter_config, mock_ccxt_exchange):
        """Test CCXT adapter connection."""
        mock_ccxt.binance = Mock(return_value=mock_ccxt_exchange)
        
        adapter = CCXTAdapter('test_binance', adapter_config)
        adapter.exchange = mock_ccxt_exchange
        
        # Test successful connection
        result = await adapter.connect()
        assert result is True
        assert adapter.is_connected
        mock_ccxt_exchange.load_markets.assert_called_once()
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_ccxt_adapter_connection_failure(self, mock_ccxt, adapter_config, mock_ccxt_exchange):
        """Test CCXT adapter connection failure."""
        mock_ccxt.binance = Mock(return_value=mock_ccxt_exchange)
        mock_ccxt_exchange.load_markets.side_effect = Exception("Connection failed")
        
        adapter = CCXTAdapter('test_binance', adapter_config)
        adapter.exchange = mock_ccxt_exchange
        
        with pytest.raises(ConnectionException):
            await adapter.connect()
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_ccxt_adapter_authentication(self, mock_ccxt, adapter_config, mock_ccxt_exchange):
        """Test CCXT adapter authentication."""
        mock_ccxt.binance = Mock(return_value=mock_ccxt_exchange)
        mock_ccxt_exchange.fetch_balance.return_value = {'USDT': {'free': 1000}}
        
        adapter = CCXTAdapter('test_binance', adapter_config)
        adapter.exchange = mock_ccxt_exchange
        
        result = await adapter.authenticate()
        assert result is True
        assert adapter.is_authenticated
        mock_ccxt_exchange.fetch_balance.assert_called_once()
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_ccxt_adapter_authentication_failure(self, mock_ccxt, adapter_config, mock_ccxt_exchange):
        """Test CCXT adapter authentication failure."""
        import ccxt
        
        mock_ccxt.binance = Mock(return_value=mock_ccxt_exchange)
        mock_ccxt.AuthenticationError = ccxt.AuthenticationError
        mock_ccxt_exchange.fetch_balance.side_effect = ccxt.AuthenticationError("Invalid API key")
        
        adapter = CCXTAdapter('test_binance', adapter_config)
        adapter.exchange = mock_ccxt_exchange
        
        with pytest.raises(AuthenticationException):
            await adapter.authenticate()
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_ccxt_adapter_health_check(self, mock_ccxt, adapter_config, mock_ccxt_exchange):
        """Test CCXT adapter health check."""
        mock_ccxt.binance = Mock(return_value=mock_ccxt_exchange)
        mock_ccxt_exchange.fetch_time.return_value = 1640995200000  # 2022-01-01 00:00:00 UTC
        
        adapter = CCXTAdapter('test_binance', adapter_config)
        adapter.exchange = mock_ccxt_exchange
        adapter._connected = True
        
        health = await adapter.health_check()
        
        assert health['exchange'] == 'test_binance'
        assert health['status'] == 'healthy'
        assert 'latency_ms' in health
        assert 'server_time' in health
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_ccxt_adapter_get_ohlcv(self, mock_ccxt, adapter_config, mock_ccxt_exchange):
        """Test CCXT adapter OHLCV data retrieval."""
        mock_ccxt.binance = Mock(return_value=mock_ccxt_exchange)
        
        # Mock OHLCV data: [timestamp, open, high, low, close, volume]
        mock_ohlcv = [
            [1640995200000, 50000.0, 51000.0, 49000.0, 50500.0, 100.0],
            [1640998800000, 50500.0, 51500.0, 49500.0, 51000.0, 150.0]
        ]
        mock_ccxt_exchange.fetch_ohlcv.return_value = mock_ohlcv
        
        adapter = CCXTAdapter('test_binance', adapter_config)
        adapter.exchange = mock_ccxt_exchange
        
        market_data = await adapter.get_ohlcv('BTC/USDT', '1h')
        
        assert len(market_data) == 2
        assert isinstance(market_data[0], MarketData)
        assert market_data[0].symbol == 'BTC/USDT'
        assert market_data[0].open == Decimal('50000.0')
        assert market_data[0].exchange == 'test_binance'
    
    @patch('src.exchanges.ccxt_adapter.ccxt')
    @pytest.mark.asyncio
    async def test_ccxt_adapter_create_order(self, mock_ccxt, adapter_config, mock_ccxt_exchange):
        """Test CCXT adapter order creation."""
        mock_ccxt.binance = Mock(return_value=mock_ccxt_exchange)
        
        mock_order_result = {
            'id': 'order_123',
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'amount': 0.1,
            'price': 50000.0,
            'type': 'limit',
            'status': 'open',
            'timestamp': 1640995200000,
            'filled': 0.0,
            'average': None,
            'fee': {'cost': 0.05}
        }
        mock_ccxt_exchange.create_order.return_value = mock_order_result
        
        adapter = CCXTAdapter('test_binance', adapter_config)
        adapter.exchange = mock_ccxt_exchange
        
        order = await adapter.create_order(
            'BTC/USDT', OrderSide.BUY, Decimal('0.1'), OrderType.LIMIT, Decimal('50000')
        )
        
        assert isinstance(order, Order)
        assert order.id == 'order_123'
        assert order.symbol == 'BTC/USDT'
        assert order.side == OrderSide.BUY
        assert order.amount == Decimal('0.1')
        assert order.price == Decimal('50000.0')
    
    def test_ccxt_adapter_validate_credentials(self, adapter_config):
        """Test credential validation."""
        with patch('src.exchanges.ccxt_adapter.ccxt'):
            adapter = CCXTAdapter('test_binance', adapter_config)
            
            # Valid credentials
            assert adapter.validate_credentials() is True
            
            # Invalid credentials
            adapter.config['api_key'] = ''
            assert adapter.validate_credentials() is False
            
            adapter.config['api_key'] = 'test_key'
            adapter.config['api_secret'] = ''
            assert adapter.validate_credentials() is False


class TestCredentialManager:
    """Test cases for CredentialManager."""
    
    @pytest.fixture
    def credential_manager(self):
        """Create credential manager with test master password."""
        return CredentialManager(master_password='test_master_password_123')
    
    def test_credential_manager_initialization(self):
        """Test credential manager initialization."""
        manager = CredentialManager(master_password='test_password')
        assert manager._master_password == 'test_password'
        assert manager._cipher_suite is not None
    
    def test_encrypt_decrypt_credentials(self, credential_manager):
        """Test credential encryption and decryption."""
        credentials = {
            'api_key': 'test_api_key_12345',
            'api_secret': 'test_api_secret_67890'
        }
        
        # Encrypt credentials
        encrypted = credential_manager.encrypt_credentials(credentials)
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
        
        # Decrypt credentials
        decrypted = credential_manager.decrypt_credentials(encrypted)
        assert decrypted == credentials
    
    def test_validate_credentials(self, credential_manager):
        """Test credential validation."""
        # Valid credentials
        valid_creds = {
            'api_key': 'valid_api_key_12345',
            'api_secret': 'valid_api_secret_67890'
        }
        assert credential_manager.validate_credentials(valid_creds) is True
        
        # Missing api_key
        invalid_creds = {'api_secret': 'valid_secret'}
        assert credential_manager.validate_credentials(invalid_creds) is False
        
        # Empty api_key
        invalid_creds = {'api_key': '', 'api_secret': 'valid_secret'}
        assert credential_manager.validate_credentials(invalid_creds) is False
        
        # Too short api_key
        invalid_creds = {'api_key': 'short', 'api_secret': 'valid_secret_12345'}
        assert credential_manager.validate_credentials(invalid_creds) is False
        
        # Invalid patterns
        invalid_creds = {'api_key': 'your_api_key', 'api_secret': 'valid_secret_12345'}
        assert credential_manager.validate_credentials(invalid_creds) is False
    
    @patch.dict('os.environ', {
        'BINANCE_API_KEY': 'env_api_key_12345',
        'BINANCE_API_SECRET': 'env_api_secret_67890'
    })
    def test_load_credentials_from_env(self, credential_manager):
        """Test loading credentials from environment variables."""
        credentials = credential_manager.load_credentials_from_env('binance')
        
        assert credentials['api_key'] == 'env_api_key_12345'
        assert credentials['api_secret'] == 'env_api_secret_67890'
    
    def test_mask_credentials(self, credential_manager):
        """Test credential masking for logging."""
        credentials = {
            'api_key': 'very_long_api_key_12345',
            'api_secret': 'very_long_api_secret_67890',
            'other_field': 'not_masked'
        }
        
        masked = credential_manager.mask_credentials(credentials)
        
        assert masked['api_key'] == 'very...2345'
        assert masked['api_secret'] == 'very...7890'
        assert masked['other_field'] == 'not_masked'
    
    def test_generate_master_key(self):
        """Test master key generation."""
        key = CredentialManager.generate_master_key()
        
        assert isinstance(key, str)
        assert len(key) > 0
        
        # Should be able to create manager with generated key
        manager = CredentialManager(master_password=key)
        assert manager._cipher_suite is not None


class TestExchangeExceptions:
    """Test cases for exchange exceptions."""
    
    def test_exchange_exception(self):
        """Test base ExchangeException."""
        exc = ExchangeException(
            "Test error", 
            exchange="test_exchange", 
            error_code="TEST_001",
            details={'key': 'value'}
        )
        
        assert str(exc) == "Test error"
        assert exc.exchange == "test_exchange"
        assert exc.error_code == "TEST_001"
        assert exc.details == {'key': 'value'}
    
    def test_rate_limit_exception(self):
        """Test RateLimitException with retry_after."""
        exc = RateLimitException(
            "Rate limit exceeded",
            exchange="test_exchange",
            retry_after=60
        )
        
        assert str(exc) == "Rate limit exceeded"
        assert exc.exchange == "test_exchange"
        assert exc.retry_after == 60
    
    def test_connection_exception(self):
        """Test ConnectionException."""
        exc = ConnectionException("Connection failed", exchange="test_exchange")
        
        assert str(exc) == "Connection failed"
        assert exc.exchange == "test_exchange"
    
    def test_authentication_exception(self):
        """Test AuthenticationException."""
        exc = AuthenticationException("Auth failed", exchange="test_exchange")
        
        assert str(exc) == "Auth failed"
        assert exc.exchange == "test_exchange"
    
    def test_order_exception(self):
        """Test OrderException."""
        exc = OrderException("Order failed", exchange="test_exchange")
        
        assert str(exc) == "Order failed"
        assert exc.exchange == "test_exchange"
    
    def test_insufficient_funds_exception(self):
        """Test InsufficientFundsException."""
        exc = InsufficientFundsException("Insufficient funds", exchange="test_exchange")
        
        assert str(exc) == "Insufficient funds"
        assert exc.exchange == "test_exchange"


if __name__ == '__main__':
    pytest.main([__file__])