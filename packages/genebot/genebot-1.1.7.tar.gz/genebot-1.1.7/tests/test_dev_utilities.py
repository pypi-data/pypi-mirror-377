"""
Tests for development and testing utilities.
"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tests.mocks.mock_exchange import MockExchange
from tests.utils.test_data_generators import (
    MarketDataGenerator, TradingScenarioGenerator, TestDataFactory
)
from tests.utils.config_validators import ConfigValidator, ConfigTestHelper
from tests.utils.test_helpers import (
    TestEnvironment, test_environment, ConfigTestManager, TestAssertions
)


class TestMockExchange:
    """Test the mock exchange implementation."""
    
    @pytest.mark.asyncio
    async def test_mock_exchange_connection(self):
        """Test mock exchange connection."""
        exchange = MockExchange("test")
        
        # Test initial state
        assert not exchange.is_connected()
        
        # Test connection
        result = await exchange.connect()
        assert result is True
        assert exchange.is_connected()
        
        # Test disconnection
        await exchange.disconnect()
        assert not exchange.is_connected()
    
    @pytest.mark.asyncio
    async def test_mock_exchange_balance(self):
        """Test mock exchange balance operations."""
        exchange = MockExchange("test")
        await exchange.connect()
        
        # Test getting balance
        balance = await exchange.get_balance()
        assert 'USD' in balance
        assert balance['USD']['total'] > 0
        
        # Test getting simple balance
        simple_balance = await exchange.get_simple_balance('USD')
        assert 'USD' in simple_balance
        assert simple_balance['USD'] > 0
    
    @pytest.mark.asyncio
    async def test_mock_exchange_market_data(self):
        """Test mock exchange market data."""
        exchange = MockExchange("test")
        await exchange.connect()
        
        # Test getting market data
        market_data = await exchange.get_market_data('BTC/USD')
        TestAssertions.assert_market_data_valid(market_data)
        
        # Test price movement simulation
        first_price = market_data.close
        second_data = await exchange.get_market_data('BTC/USD')
        # Prices should be different (simulated movement)
        assert second_data.close != first_price
    
    @pytest.mark.asyncio
    async def test_mock_exchange_orders(self):
        """Test mock exchange order operations."""
        exchange = MockExchange("test")
        await exchange.connect()
        
        # Test placing order
        order = await exchange.place_order(
            symbol='BTC/USD',
            side='BUY',
            amount=0.1,
            price=45000.0,
            order_type='limit'
        )
        
        TestAssertions.assert_order_valid(order)
        assert order.status == 'filled'  # Mock orders are immediately filled
        
        # Test getting order status
        order_status = await exchange.get_order_status(order.id)
        assert order_status.id == order.id
        assert order_status.status == 'filled'
    
    @pytest.mark.asyncio
    async def test_mock_exchange_failure_simulation(self):
        """Test mock exchange failure simulation."""
        exchange = MockExchange("test")
        exchange.set_failure_simulation(True, failure_rate=1.0)  # 100% failure rate
        
        # Connection should fail
        with pytest.raises(ConnectionError):
            await exchange.connect()
        
        # Disable failure simulation
        exchange.set_failure_simulation(False)
        await exchange.connect()
        
        # Should work normally now
        balance = await exchange.get_balance()
        assert balance is not None


class TestDataGenerators:
    """Test the data generators."""
    
    def test_market_data_generator_ohlcv(self):
        """Test OHLCV data generation."""
        start_date = datetime.now(timezone.utc) - timedelta(hours=24)
        end_date = datetime.now(timezone.utc)
        
        data = MarketDataGenerator.generate_ohlcv_data(
            symbol="BTC/USD",
            start_date=start_date,
            end_date=end_date,
            interval_minutes=60,
            initial_price=45000.0
        )
        
        assert len(data) == 25  # 24 hours of hourly data (inclusive range)
        
        for market_data in data:
            TestAssertions.assert_market_data_valid(market_data)
            assert market_data.symbol == "BTC/USD"
    
    def test_market_data_generator_trending(self):
        """Test trending data generation."""
        data = MarketDataGenerator.generate_trending_data(
            symbol="BTC/USD",
            periods=100,
            trend_strength=0.1,
            initial_price=45000.0
        )
        
        assert len(data) == 100
        
        # Check that there's generally an upward trend
        first_price = data[0].close
        last_price = data[-1].close
        assert last_price > first_price  # Should trend upward
        
        for market_data in data:
            TestAssertions.assert_market_data_valid(market_data)
    
    def test_market_data_generator_sideways(self):
        """Test sideways data generation."""
        price_range = (44000.0, 46000.0)
        data = MarketDataGenerator.generate_sideways_data(
            symbol="BTC/USD",
            periods=100,
            price_range=price_range,
            initial_price=45000.0
        )
        
        assert len(data) == 100
        
        # Check that prices stay within range (with some tolerance)
        for market_data in data:
            TestAssertions.assert_market_data_valid(market_data)
            # Allow some deviation from range
            assert price_range[0] * 0.9 <= market_data.close <= price_range[1] * 1.1
    
    def test_trading_scenario_generator_orders(self):
        """Test order generation."""
        symbols = ["BTC/USD", "ETH/USD"]
        orders = TradingScenarioGenerator.generate_orders(symbols, 20)
        
        assert len(orders) == 20
        
        for order in orders:
            TestAssertions.assert_order_valid(order)
            assert order.symbol in symbols
    
    def test_trading_scenario_generator_positions(self):
        """Test position generation."""
        symbols = ["BTC/USD", "ETH/USD"]
        positions = TradingScenarioGenerator.generate_positions(symbols, 10)
        
        assert len(positions) == 10
        
        for position in positions:
            TestAssertions.assert_position_valid(position)
            assert position.symbol in symbols
    
    def test_trading_scenario_generator_signals(self):
        """Test trading signal generation."""
        symbols = ["BTC/USD", "ETH/USD"]
        strategies = ["MovingAverage", "RSI"]
        signals = TradingScenarioGenerator.generate_trading_signals(
            symbols, strategies, 30
        )
        
        assert len(signals) == 30
        
        for signal in signals:
            TestAssertions.assert_trading_signal_valid(signal)
            assert signal.symbol in symbols
            assert signal.strategy_name in strategies
    
    def test_test_data_factory_scenarios(self):
        """Test test data factory scenarios."""
        # Test bull market scenario
        bull_scenario = TestDataFactory.create_bull_market_scenario()
        assert bull_scenario['scenario_type'] == 'bull_market'
        assert 'market_data' in bull_scenario
        assert 'orders' in bull_scenario
        
        # Test bear market scenario
        bear_scenario = TestDataFactory.create_bear_market_scenario()
        assert bear_scenario['scenario_type'] == 'bear_market'
        
        # Test volatile market scenario
        volatile_scenario = TestDataFactory.create_volatile_market_scenario()
        assert volatile_scenario['scenario_type'] == 'volatile_market'
        
        # Test multi-asset scenario
        multi_scenario = TestDataFactory.create_multi_asset_scenario()
        assert multi_scenario['scenario_type'] == 'multi_asset'
        assert isinstance(multi_scenario['market_data'], dict)


class TestConfigValidators:
    """Test configuration validators."""
    
    def test_config_validator_valid_config(self):
        """Test validation of valid configuration."""
        config = ConfigTestHelper.create_minimal_config()
        
        # Create temporary config file
        with test_environment() as env:
            config_manager = ConfigTestManager(env)
            config_path = config_manager.create_config_file(config)
            
            # Validate config file
            result = ConfigValidator.validate_config_file(str(config_path))
            
            if not result['valid']:
                print("Validation errors:", result['errors'])
            
            assert result['valid'] is True
            assert len(result['errors']) == 0
            assert result['config'] is not None
    
    def test_config_validator_invalid_config(self):
        """Test validation of invalid configuration."""
        config = ConfigTestHelper.create_invalid_config()
        
        with test_environment() as env:
            config_manager = ConfigTestManager(env)
            config_path = config_manager.create_config_file(config)
            
            # Validate config file
            result = ConfigValidator.validate_config_file(str(config_path))
            
            assert result['valid'] is False
            assert len(result['errors']) > 0
    
    def test_config_validator_missing_file(self):
        """Test validation of missing config file."""
        result = ConfigValidator.validate_config_file("nonexistent.yaml")
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert "not found" in result['errors'][0]
    
    def test_config_test_helper_minimal_config(self):
        """Test minimal config creation."""
        config = ConfigTestHelper.create_minimal_config()
        TestAssertions.assert_config_valid(config)
    
    def test_config_test_helper_invalid_config(self):
        """Test invalid config creation."""
        config = ConfigTestHelper.create_invalid_config()
        
        # Should have invalid values
        assert config['strategies']['moving_average']['max_positions'] < 0
        assert config['risk']['max_daily_loss'] > 1.0


class TestTestHelpers:
    """Test the test helper utilities."""
    
    def test_test_environment_temp_dir(self):
        """Test temporary directory creation."""
        with test_environment() as env:
            temp_dir = env.create_temp_dir("test_")
            assert temp_dir.exists()
            assert temp_dir.is_dir()
            assert "test_" in temp_dir.name
        
        # Directory should be cleaned up after context
        assert not temp_dir.exists()
    
    def test_test_environment_temp_file(self):
        """Test temporary file creation."""
        test_content = "test content"
        
        with test_environment() as env:
            temp_file = env.create_temp_file(test_content, ".txt")
            assert temp_file.exists()
            assert temp_file.is_file()
            
            # Check content
            with open(temp_file, 'r') as f:
                content = f.read()
            assert content == test_content
        
        # File should be cleaned up after context
        assert not temp_file.exists()
    
    def test_test_environment_mock_exchange(self):
        """Test mock exchange creation."""
        with test_environment() as env:
            exchange = env.create_mock_exchange("test_exchange")
            assert isinstance(exchange, MockExchange)
            assert exchange.name == "test_exchange"
    
    def test_config_test_manager(self):
        """Test configuration test manager."""
        with test_environment() as env:
            config_manager = ConfigTestManager(env)
            
            # Test config file creation
            config = config_manager.get_minimal_config()
            config_path = config_manager.create_config_file(config)
            
            assert config_path.exists()
            assert config_path.suffix == ".yaml"
            
            # Test env file creation
            env_vars = {"TEST_VAR": "test_value"}
            env_path = config_manager.create_env_file(env_vars)
            
            assert env_path.exists()
            with open(env_path, 'r') as f:
                content = f.read()
            assert "TEST_VAR=test_value" in content
    
    def test_test_assertions(self):
        """Test custom test assertions."""
        # Test market data assertion
        data = MarketDataGenerator.generate_ohlcv_data(
            symbol="BTC/USD",
            start_date=datetime.now(timezone.utc) - timedelta(hours=1),
            end_date=datetime.now(timezone.utc),
            interval_minutes=60
        )[0]
        
        # Should not raise
        TestAssertions.assert_market_data_valid(data)
        
        # Test order assertion
        orders = TradingScenarioGenerator.generate_orders(["BTC/USD"], 1)
        TestAssertions.assert_order_valid(orders[0])
        
        # Test position assertion
        positions = TradingScenarioGenerator.generate_positions(["BTC/USD"], 1)
        TestAssertions.assert_position_valid(positions[0])
        
        # Test signal assertion
        signals = TradingScenarioGenerator.generate_trading_signals(
            ["BTC/USD"], ["test"], 1
        )
        TestAssertions.assert_trading_signal_valid(signals[0])
        
        # Test config assertion
        config = ConfigTestHelper.create_minimal_config()
        TestAssertions.assert_config_valid(config)


@pytest.mark.asyncio
async def test_async_test_environment():
    """Test async test environment context manager."""
    from tests.utils.test_helpers import async_test_environment
    
    async with async_test_environment() as env:
        exchange = env.create_mock_exchange("async_test")
        await exchange.connect()
        assert exchange.is_connected()
    
    # Exchange should be disconnected and cleaned up
    assert not exchange.is_connected()


if __name__ == "__main__":
    pytest.main([__file__])