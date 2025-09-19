"""
Unit tests for forex broker adapters.

This module tests the forex broker adapter interfaces with mock brokers
to ensure proper functionality without requiring actual broker connections.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, Any

from src.exchanges.forex.base import ForexBrokerAdapter
from src.exchanges.forex.mt5_adapter import MT5Adapter
from src.exchanges.forex.oanda_adapter import OANDAAdapter
from src.exchanges.forex.ib_adapter import IBAdapter
from src.models.data_models import MarketSpecificOrder, Position, OrderSide, OrderType, OrderStatus, UnifiedMarketData
from src.markets.types import UnifiedSymbol, MarketType
from src.exceptions.base_exceptions import ConnectionException, AuthenticationException, OrderException


class MockForexAdapter(ForexBrokerAdapter):
    """Mock forex adapter for testing base functionality."""
    
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
        self._authenticated = False
    
    async def authenticate(self) -> bool:
        if not self._connected:
            await self.connect()
        self.mock_authenticated = True
        self._authenticated = True
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        return {
            'status': 'healthy' if self._connected and self._authenticated else 'unhealthy',
            'connected': self._connected,
            'authenticated': self._authenticated
        }
    
    async def get_instruments(self) -> Dict[str, Dict[str, Any]]:
        return {
            'EURUSD': {'name': 'EURUSD', 'base': 'EUR', 'quote': 'USD'},
            'GBPUSD': {'name': 'GBPUSD', 'base': 'GBP', 'quote': 'USD'}
        }
    
    async def get_quote(self, symbol: UnifiedSymbol) -> Dict[str, Any]:
        return {
            'symbol': symbol.native_symbol,
            'bid': Decimal('1.1000'),
            'ask': Decimal('1.1002'),
            'spread': Decimal('0.0002'),
            'timestamp': datetime.now(timezone.utc)
        }
    
    async def get_ohlcv(self, symbol: UnifiedSymbol, timeframe: str = '1H', 
                        since=None, limit=None):
        return [
            UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now(timezone.utc),
                open=Decimal('1.1000'),
                high=Decimal('1.1010'),
                low=Decimal('1.0990'),
                close=Decimal('1.1005'),
                volume=Decimal('1000'),
                source=self.name,
                market_type=MarketType.FOREX
            )
        ]
    
    async def get_account_info(self) -> Dict[str, Any]:
        return {
            'balance': Decimal('10000'),
            'equity': Decimal('10000'),
            'margin': Decimal('0'),
            'currency': 'USD'
        }
    
    async def get_balance(self) -> Dict[str, Decimal]:
        return {'USD': Decimal('10000')}
    
    # Implement remaining abstract methods with mock responses
    async def create_order(self, symbol, side, amount, order_type=OrderType.MARKET, 
                          price=None, stop_loss=None, take_profit=None, params=None):
        return MarketSpecificOrder(
            id='mock_order_1',
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            order_type=order_type,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(timezone.utc),
            source=self.name,
            market_type=MarketType.FOREX
        )
    
    async def modify_order(self, order_id, symbol, price=None, stop_loss=None, take_profit=None):
        return MarketSpecificOrder(
            id=order_id,
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal('1000'),
            price=price,
            order_type=OrderType.LIMIT,
            status=OrderStatus.OPEN,
            timestamp=datetime.now(timezone.utc),
            source=self.name,
            market_type=MarketType.FOREX
        )
    
    async def cancel_order(self, order_id, symbol):
        return MarketSpecificOrder(
            id=order_id,
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal('1000'),
            price=Decimal('1.1000'),
            order_type=OrderType.LIMIT,
            status=OrderStatus.CANCELLED,
            timestamp=datetime.now(timezone.utc),
            source=self.name,
            market_type=MarketType.FOREX
        )
    
    async def get_order(self, order_id, symbol):
        return MarketSpecificOrder(
            id=order_id,
            symbol=symbol,
            side=OrderSide.BUY,
            amount=Decimal('1000'),
            price=Decimal('1.1000'),
            order_type=OrderType.LIMIT,
            status=OrderStatus.OPEN,
            timestamp=datetime.now(timezone.utc),
            source=self.name,
            market_type=MarketType.FOREX
        )
    
    async def get_open_orders(self, symbol=None):
        return []
    
    async def get_order_history(self, symbol=None, since=None, limit=None):
        return []
    
    async def get_positions(self, symbol=None):
        return []
    
    async def close_position(self, symbol, amount=None):
        return MarketSpecificOrder(
            id='close_order_1',
            symbol=symbol,
            side=OrderSide.SELL,
            amount=amount or Decimal('1000'),
            price=None,
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            timestamp=datetime.now(timezone.utc),
            source=self.name,
            market_type=MarketType.FOREX
        )
    
    async def get_trade_history(self, symbol=None, since=None, limit=None):
        return []
    
    def validate_credentials(self) -> bool:
        return 'api_key' in self.config
    
    def get_trading_costs(self, symbol):
        return {
            'spread': Decimal('0.0002'),
            'commission': Decimal('0'),
            'swap_long': Decimal('-0.5'),
            'swap_short': Decimal('0.3')
        }
    
    def get_minimum_trade_size(self, symbol):
        return Decimal('1000')
    
    def get_pip_value(self, symbol, lot_size=Decimal('1.0')):
        return Decimal('10.0')
    
    def calculate_margin_required(self, symbol, amount):
        return amount * Decimal('0.02')  # 2% margin
    
    async def get_swap_rates(self, symbol):
        return {'long': Decimal('-0.5'), 'short': Decimal('0.3')}


class TestForexBrokerAdapter:
    """Test cases for the base ForexBrokerAdapter class."""
    
    @pytest.fixture
    def mock_adapter(self):
        """Create a mock forex adapter for testing."""
        config = {'api_key': 'test_key', 'account_id': 'test_account'}
        return MockForexAdapter('test_broker', config)
    
    @pytest.fixture
    def sample_symbol(self):
        """Create a sample forex symbol for testing."""
        return UnifiedSymbol.from_forex_symbol('EURUSD')
    
    def test_adapter_initialization(self, mock_adapter):
        """Test forex adapter initialization."""
        assert mock_adapter.name == 'test_broker'
        assert mock_adapter.market_type == MarketType.FOREX
        assert not mock_adapter.is_connected
        assert not mock_adapter.is_authenticated
    
    @pytest.mark.asyncio
    async def test_connection_workflow(self, mock_adapter):
        """Test connection and authentication workflow."""
        # Initially not connected
        assert not mock_adapter.is_connected
        assert not mock_adapter.is_authenticated
        
        # Connect
        result = await mock_adapter.connect()
        assert result is True
        assert mock_adapter.is_connected
        
        # Authenticate
        result = await mock_adapter.authenticate()
        assert result is True
        assert mock_adapter.is_authenticated
        
        # Health check
        health = await mock_adapter.health_check()
        assert health['status'] == 'healthy'
        assert health['connected'] is True
        assert health['authenticated'] is True
        
        # Disconnect
        await mock_adapter.disconnect()
        assert not mock_adapter.is_connected
        assert not mock_adapter.is_authenticated
    
    @pytest.mark.asyncio
    async def test_market_data_methods(self, mock_adapter, sample_symbol):
        """Test market data retrieval methods."""
        await mock_adapter.authenticate()
        
        # Test get_instruments
        instruments = await mock_adapter.get_instruments()
        assert isinstance(instruments, dict)
        assert 'EURUSD' in instruments
        
        # Test get_quote
        quote = await mock_adapter.get_quote(sample_symbol)
        assert 'bid' in quote
        assert 'ask' in quote
        assert 'spread' in quote
        assert isinstance(quote['bid'], Decimal)
        assert isinstance(quote['ask'], Decimal)
        
        # Test get_ohlcv
        ohlcv = await mock_adapter.get_ohlcv(sample_symbol, '1H', limit=10)
        assert isinstance(ohlcv, list)
        if ohlcv:
            assert isinstance(ohlcv[0], UnifiedMarketData)
            assert ohlcv[0].market_type == MarketType.FOREX
    
    @pytest.mark.asyncio
    async def test_account_methods(self, mock_adapter):
        """Test account information methods."""
        await mock_adapter.authenticate()
        
        # Test get_account_info
        account_info = await mock_adapter.get_account_info()
        assert isinstance(account_info, dict)
        assert 'balance' in account_info
        
        # Test get_balance
        balance = await mock_adapter.get_balance()
        assert isinstance(balance, dict)
        assert 'USD' in balance
        assert isinstance(balance['USD'], Decimal)
    
    @pytest.mark.asyncio
    async def test_order_management(self, mock_adapter, sample_symbol):
        """Test order management methods."""
        await mock_adapter.authenticate()
        
        # Test create_order
        order = await mock_adapter.create_order(
            symbol=sample_symbol,
            side=OrderSide.BUY,
            amount=Decimal('1000'),
            order_type=OrderType.MARKET
        )
        assert isinstance(order, MarketSpecificOrder)
        assert order.symbol == sample_symbol
        assert order.side == OrderSide.BUY
        assert order.market_type == MarketType.FOREX
        
        # Test get_order
        retrieved_order = await mock_adapter.get_order(order.id, sample_symbol)
        assert isinstance(retrieved_order, MarketSpecificOrder)
        
        # Test modify_order
        modified_order = await mock_adapter.modify_order(
            order.id, sample_symbol, price=Decimal('1.1010')
        )
        assert isinstance(modified_order, MarketSpecificOrder)
        
        # Test cancel_order
        cancelled_order = await mock_adapter.cancel_order(order.id, sample_symbol)
        assert isinstance(cancelled_order, MarketSpecificOrder)
        assert cancelled_order.status == OrderStatus.CANCELLED
    
    def test_utility_methods(self, mock_adapter, sample_symbol):
        """Test utility methods."""
        # Test validate_credentials
        assert mock_adapter.validate_credentials() is True
        
        # Test get_trading_costs
        costs = mock_adapter.get_trading_costs(sample_symbol)
        assert isinstance(costs, dict)
        assert 'spread' in costs
        assert 'commission' in costs
        
        # Test get_minimum_trade_size
        min_size = mock_adapter.get_minimum_trade_size(sample_symbol)
        assert isinstance(min_size, Decimal)
        assert min_size > 0
        
        # Test get_pip_value
        pip_value = mock_adapter.get_pip_value(sample_symbol)
        assert isinstance(pip_value, Decimal)
        
        # Test calculate_margin_required
        margin = mock_adapter.calculate_margin_required(sample_symbol, Decimal('1000'))
        assert isinstance(margin, Decimal)
    
    def test_string_representations(self, mock_adapter):
        """Test string representation methods."""
        str_repr = str(mock_adapter)
        assert 'MockForexAdapter' in str_repr
        assert 'test_broker' in str_repr
        
        repr_str = repr(mock_adapter)
        assert 'MockForexAdapter' in repr_str
        assert 'test_broker' in repr_str
        assert 'connected=' in repr_str
        assert 'authenticated=' in repr_str


class TestMT5Adapter:
    """Test cases for the MT5Adapter class."""
    
    @pytest.fixture
    def mt5_config(self):
        """Create MT5 configuration for testing."""
        return {
            'login': '12345',
            'password': 'test_password',
            'server': 'test_server',
            'path': '/path/to/mt5'
        }
    
    def test_mt5_initialization(self, mt5_config):
        """Test MT5 adapter initialization."""
        adapter = MT5Adapter('mt5_test', mt5_config)
        assert adapter.name == 'mt5_test'
        assert adapter.market_type == MarketType.FOREX
        assert adapter.config == mt5_config
    
    def test_mt5_initialization_missing_config(self):
        """Test MT5 adapter initialization with missing config."""
        incomplete_config = {'login': '12345'}  # Missing password and server
        
        with pytest.raises(ValueError, match="Missing required config key"):
            MT5Adapter('mt5_test', incomplete_config)
    
    def test_mt5_validate_credentials(self, mt5_config):
        """Test MT5 credential validation."""
        adapter = MT5Adapter('mt5_test', mt5_config)
        assert adapter.validate_credentials() is True
        
        # Test with invalid login (non-numeric)
        invalid_config = mt5_config.copy()
        invalid_config['login'] = 'invalid_login'
        adapter_invalid = MT5Adapter('mt5_test', invalid_config)
        assert adapter_invalid.validate_credentials() is False
    
    @pytest.mark.asyncio
    async def test_mt5_connection_without_package(self, mt5_config):
        """Test MT5 connection when package is not installed."""
        adapter = MT5Adapter('mt5_test', mt5_config)
        
        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(ConnectionException, match="MetaTrader5 package not installed"):
                await adapter.connect()
    
    @pytest.mark.asyncio
    async def test_mt5_connection_failure(self, mt5_config):
        """Test MT5 connection failure."""
        adapter = MT5Adapter('mt5_test', mt5_config)
        
        # Mock MT5 module
        mock_mt5 = Mock()
        mock_mt5.initialize.return_value = False
        mock_mt5.last_error.return_value = (1, "Connection failed")
        
        # Mock the import to return our mock MT5
        def mock_import(name, *args, **kwargs):
            if name == 'MetaTrader5':
                return mock_mt5
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(ConnectionException, match="MT5 initialization failed"):
                await adapter.connect()


class TestOANDAAdapter:
    """Test cases for the OANDAAdapter class."""
    
    @pytest.fixture
    def oanda_config(self):
        """Create OANDA configuration for testing."""
        return {
            'api_key': 'test_api_key_12345',
            'account_id': '123-456-789',
            'environment': 'practice'
        }
    
    def test_oanda_initialization(self, oanda_config):
        """Test OANDA adapter initialization."""
        adapter = OANDAAdapter('oanda_test', oanda_config)
        assert adapter.name == 'oanda_test'
        assert adapter.market_type == MarketType.FOREX
        assert adapter._base_url == 'https://api-fxpractice.oanda.com'
        assert adapter._stream_url == 'https://stream-fxpractice.oanda.com'
    
    def test_oanda_initialization_live_environment(self):
        """Test OANDA adapter initialization with live environment."""
        config = {
            'api_key': 'test_api_key',
            'account_id': '123-456-789',
            'environment': 'live'
        }
        adapter = OANDAAdapter('oanda_test', config)
        assert adapter._base_url == 'https://api-fxtrade.oanda.com'
        assert adapter._stream_url == 'https://stream-fxtrade.oanda.com'
    
    def test_oanda_initialization_missing_config(self):
        """Test OANDA adapter initialization with missing config."""
        incomplete_config = {'api_key': 'test_key'}  # Missing account_id
        
        with pytest.raises(ValueError, match="Missing required config key"):
            OANDAAdapter('oanda_test', incomplete_config)
    
    def test_oanda_validate_credentials(self, oanda_config):
        """Test OANDA credential validation."""
        adapter = OANDAAdapter('oanda_test', oanda_config)
        assert adapter.validate_credentials() is True
        
        # Test with short API key
        invalid_config = oanda_config.copy()
        invalid_config['api_key'] = 'short'
        adapter_invalid = OANDAAdapter('oanda_test', invalid_config)
        assert adapter_invalid.validate_credentials() is False
        
        # Test with invalid account ID (non-numeric with dashes)
        invalid_config = oanda_config.copy()
        invalid_config['account_id'] = 'invalid_account_id'
        adapter_invalid = OANDAAdapter('oanda_test', invalid_config)
        assert adapter_invalid.validate_credentials() is False
    
    @pytest.mark.asyncio
    async def test_oanda_connection(self, oanda_config):
        """Test OANDA connection."""
        adapter = OANDAAdapter('oanda_test', oanda_config)
        
        with patch('aiohttp.ClientSession') as mock_session:
            result = await adapter.connect()
            assert result is True
            assert adapter.is_connected
            mock_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_oanda_authentication_success(self, oanda_config):
        """Test successful OANDA authentication."""
        adapter = OANDAAdapter('oanda_test', oanda_config)
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'account': {'id': '123-456-789'}})
        
        # Create a proper async context manager mock
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_context_manager)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            await adapter.connect()
            result = await adapter.authenticate()
            assert result is True
            assert adapter.is_authenticated
    
    @pytest.mark.asyncio
    async def test_oanda_authentication_failure(self, oanda_config):
        """Test OANDA authentication failure."""
        adapter = OANDAAdapter('oanda_test', oanda_config)
        
        # Mock 401 response
        mock_response = AsyncMock()
        mock_response.status = 401
        
        # Create a proper async context manager mock
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_context_manager)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            await adapter.connect()
            with pytest.raises(AuthenticationException, match="Invalid OANDA API key"):
                await adapter.authenticate()


class TestIBAdapter:
    """Test cases for the IBAdapter class."""
    
    @pytest.fixture
    def ib_config(self):
        """Create IB configuration for testing."""
        return {
            'host': '127.0.0.1',
            'port': 7497,
            'client_id': 1,
            'account': 'DU123456'
        }
    
    def test_ib_initialization(self, ib_config):
        """Test IB adapter initialization."""
        adapter = IBAdapter('ib_test', ib_config)
        assert adapter.name == 'ib_test'
        assert adapter.market_type == MarketType.FOREX
        assert adapter.host == '127.0.0.1'
        assert adapter.port == 7497
        assert adapter.client_id == 1
        assert adapter.account == 'DU123456'
    
    def test_ib_initialization_defaults(self):
        """Test IB adapter initialization with defaults."""
        config = {}
        adapter = IBAdapter('ib_test', config)
        assert adapter.host == '127.0.0.1'
        assert adapter.port == 7497
        assert adapter.client_id == 1
        assert adapter.account is None
    
    def test_ib_validate_credentials(self, ib_config):
        """Test IB credential validation."""
        adapter = IBAdapter('ib_test', ib_config)
        assert adapter.validate_credentials() is True
        
        # Test with invalid port
        invalid_config = ib_config.copy()
        invalid_config['port'] = 'invalid_port'
        adapter_invalid = IBAdapter('ib_test', invalid_config)
        assert adapter_invalid.validate_credentials() is False
        
        # Test with invalid client_id
        invalid_config = ib_config.copy()
        invalid_config['client_id'] = 'invalid_client'
        adapter_invalid = IBAdapter('ib_test', invalid_config)
        assert adapter_invalid.validate_credentials() is False
    
    @pytest.mark.asyncio
    async def test_ib_connection_without_package(self, ib_config):
        """Test IB connection when package is not installed."""
        adapter = IBAdapter('ib_test', ib_config)
        
        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(ConnectionException, match="ib_insync package not installed"):
                await adapter.connect()
    
    @pytest.mark.asyncio
    async def test_ib_connection_success(self, ib_config):
        """Test successful IB connection."""
        adapter = IBAdapter('ib_test', ib_config)
        
        # Mock IB class
        mock_ib = AsyncMock()
        mock_ib.isConnected.return_value = True
        mock_ib.connectAsync = AsyncMock()
        
        # Mock the import to return our mock IB class
        def mock_import(name, *args, **kwargs):
            if name == 'ib_insync':
                mock_module = Mock()
                mock_module.IB = Mock(return_value=mock_ib)
                return mock_module
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            result = await adapter.connect()
            assert result is True
            assert adapter.is_connected
            mock_ib.connectAsync.assert_called_once_with(
                host='127.0.0.1', port=7497, clientId=1, timeout=20
            )
    
    @pytest.mark.asyncio
    async def test_ib_connection_failure(self, ib_config):
        """Test IB connection failure."""
        adapter = IBAdapter('ib_test', ib_config)
        
        # Mock IB class that fails to connect
        mock_ib = AsyncMock()
        mock_ib.isConnected.return_value = False
        mock_ib.connectAsync = AsyncMock()
        
        # Mock the import to return our mock IB class
        def mock_import(name, *args, **kwargs):
            if name == 'ib_insync':
                mock_module = Mock()
                mock_module.IB = Mock(return_value=mock_ib)
                return mock_module
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(ConnectionException, match="Failed to establish connection"):
                await adapter.connect()


@pytest.mark.asyncio
async def test_forex_adapter_integration():
    """Integration test for forex adapter workflow."""
    config = {'api_key': 'test_key', 'account_id': 'test_account'}
    adapter = MockForexAdapter('integration_test', config)
    
    # Test complete workflow
    await adapter.connect()
    await adapter.authenticate()
    
    # Test market data
    symbol = UnifiedSymbol.from_forex_symbol('EURUSD')
    quote = await adapter.get_quote(symbol)
    assert quote['symbol'] == 'EURUSD'
    
    # Test order creation
    order = await adapter.create_order(
        symbol=symbol,
        side=OrderSide.BUY,
        amount=Decimal('1000'),
        order_type=OrderType.MARKET
    )
    assert order.market_type == MarketType.FOREX
    
    # Test cleanup
    await adapter.disconnect()
    assert not adapter.is_connected


if __name__ == '__main__':
    pytest.main([__file__])