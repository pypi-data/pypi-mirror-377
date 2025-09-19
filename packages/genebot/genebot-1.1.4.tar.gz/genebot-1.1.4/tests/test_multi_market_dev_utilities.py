"""
Test suite for multi-market development utilities.
Demonstrates and validates all development and testing utilities.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import yaml
from typing import Dict, Any

from src.markets.types import MarketType
from tests.mocks.multi_market_mock_exchange import (
    MultiMarketMockExchange,
    create_multi_market_mock_exchange,
    create_crypto_mock_config,
    create_forex_mock_config
)
from tests.fixtures.multi_market_fixtures import (
    MultiMarketDataGenerator,
    MultiMarketTestScenarios
)
from tests.utils.multi_market_config_validators import (
    MultiMarketConfigValidator,
    ConfigurationTester,
    validate_config_dict
)
from tests.utils.multi_market_test_utilities import (
    MultiMarketTestContext,
    MultiMarketAssertions,
    MultiMarketTestHelpers,
    MultiMarketTestRunner,
    MultiMarketPerformanceTester,
    test_cross_market_correlation_scenario,
    test_arbitrage_detection_scenario
)


class TestMultiMarketMockExchange:
    """Test the multi-market mock exchange functionality"""
    
    @pytest.mark.asyncio
    async def test_mock_exchange_creation(self):
        """Test creating multi-market mock exchange"""
        exchange = create_multi_market_mock_exchange()
        assert exchange is not None
        assert not exchange.is_connected
        
        # Test connection
        success = await exchange.connect()
        assert success
        assert exchange.is_connected
        
        await exchange.disconnect()
        assert not exchange.is_connected
    
    @pytest.mark.asyncio
    async def test_crypto_market_data(self):
        """Test crypto market data generation"""
        exchange = create_multi_market_mock_exchange()
        await exchange.connect()
        
        # Get crypto market data
        data = await exchange.get_market_data('BTC/USD', MarketType.CRYPTO)
        
        assert data.symbol == 'BTC/USD'
        assert data.close > 0
        assert data.volume > 0
        assert data.high >= data.low
        assert data.bid < data.ask
        
        await exchange.disconnect()
    
    @pytest.mark.asyncio
    async def test_forex_market_data(self):
        """Test forex market data generation"""
        exchange = create_multi_market_mock_exchange()
        await exchange.connect()
        
        # Get forex market data
        data = await exchange.get_market_data('EURUSD', MarketType.FOREX)
        
        assert data.symbol == 'EURUSD'
        assert data.close > 0
        assert data.volume > 0
        assert data.high >= data.low
        assert data.bid < data.ask
        
        await exchange.disconnect()
    
    @pytest.mark.asyncio
    async def test_order_placement_and_execution(self):
        """Test order placement and execution"""
        exchange = create_multi_market_mock_exchange()
        await exchange.connect()
        
        # Place crypto order
        order_id = await exchange.place_order(
            symbol='BTC/USD',
            side='buy',
            amount=0.1,
            market_type=MarketType.CRYPTO
        )
        
        assert order_id is not None
        
        # Check order status
        status = await exchange.get_order_status(order_id)
        assert status['id'] == order_id
        assert status['symbol'] == 'BTC/USD'
        assert status['side'] == 'buy'
        assert status['amount'] == 0.1
        
        await exchange.disconnect()
    
    @pytest.mark.asyncio
    async def test_market_session_handling(self):
        """Test market session handling"""
        # Create forex config with specific session hours
        forex_config = create_forex_mock_config()
        forex_config.session_hours = (9, 17)  # 9 AM to 5 PM UTC
        
        exchange = MultiMarketMockExchange([forex_config])
        
        # Test market open check
        is_open = exchange.is_market_open(MarketType.FOREX)
        assert isinstance(is_open, bool)
        
        # Crypto should always be open
        crypto_config = create_crypto_mock_config()
        exchange = MultiMarketMockExchange([crypto_config])
        assert exchange.is_market_open(MarketType.CRYPTO) == True


class TestMultiMarketDataGenerator:
    """Test the multi-market data generator"""
    
    def test_data_generator_creation(self):
        """Test creating data generator"""
        generator = MultiMarketDataGenerator(seed=42)
        assert generator is not None
    
    def test_market_data_series_generation(self):
        """Test generating market data series"""
        generator = MultiMarketDataGenerator(seed=42)
        
        start_time = datetime.utcnow() - timedelta(hours=1)
        data_series = generator.generate_market_data_series(
            symbol='BTC/USD',
            market_type=MarketType.CRYPTO,
            start_time=start_time,
            duration_hours=1,
            interval_minutes=1,
            base_price=45000.0,
            volatility=0.02
        )
        
        assert len(data_series) == 60  # 60 minutes
        assert all(d.symbol == 'BTC/USD' for d in data_series)
        assert all(d.close > 0 for d in data_series)
        assert all(d.volume > 0 for d in data_series)
    
    def test_correlated_data_generation(self):
        """Test generating correlated market data"""
        generator = MultiMarketDataGenerator(seed=42)
        
        symbols = ['BTC/USD', 'ETH/USD']
        market_types = [MarketType.CRYPTO, MarketType.CRYPTO]
        correlation_matrix = [[1.0, 0.8], [0.8, 1.0]]
        
        start_time = datetime.utcnow() - timedelta(hours=1)
        correlated_data = generator.generate_correlated_data(
            symbols=symbols,
            market_types=market_types,
            correlation_matrix=correlation_matrix,
            start_time=start_time,
            duration_hours=1
        )
        
        assert 'BTC/USD' in correlated_data
        assert 'ETH/USD' in correlated_data
        assert len(correlated_data['BTC/USD']) == 60
        assert len(correlated_data['ETH/USD']) == 60
    
    def test_economic_events_generation(self):
        """Test generating economic events"""
        generator = MultiMarketDataGenerator(seed=42)
        
        start_time = datetime.utcnow()
        events = generator.generate_economic_events(start_time, duration_days=1)
        
        assert len(events) >= 2  # At least 2 events per day
        assert all('timestamp' in event for event in events)
        assert all('currency' in event for event in events)
        assert all('event' in event for event in events)
    
    def test_order_history_generation(self):
        """Test generating order history"""
        generator = MultiMarketDataGenerator(seed=42)
        
        symbols = ['BTC/USD', 'EURUSD']
        market_types = [MarketType.CRYPTO, MarketType.FOREX]
        orders = generator.generate_order_history(symbols, market_types, count=10)
        
        assert len(orders) == 10
        assert all(hasattr(order, 'symbol') for order in orders)
        assert all(hasattr(order, 'side') for order in orders)
        assert all(order.amount > 0 for order in orders)


class TestMultiMarketConfigValidator:
    """Test the configuration validator"""
    
    def test_validator_creation(self):
        """Test creating config validator"""
        validator = MultiMarketConfigValidator()
        assert validator is not None
    
    def test_valid_config_validation(self):
        """Test validating a valid configuration"""
        valid_config = {
            'markets': {
                'crypto': {
                    'enabled': True,
                    'exchanges': [
                        {
                            'name': 'binance',
                            'type': 'live',
                            'credentials': {'api_key': 'test', 'secret': 'test'}
                        }
                    ],
                    'symbols': ['BTC/USD', 'ETH/USD']
                },
                'forex': {
                    'enabled': True,
                    'brokers': [
                        {
                            'name': 'oanda',
                            'type': 'live',
                            'credentials': {'account_id': 'test', 'token': 'test'}
                        }
                    ],
                    'symbols': ['EURUSD', 'GBPUSD']
                }
            },
            'risk_management': {
                'unified_limits': {
                    'max_portfolio_risk': 0.02,
                    'daily_loss_limit': 0.05
                },
                'market_specific': {
                    'crypto': {'max_position_size': 0.1},
                    'forex': {'max_position_size': 0.05}
                }
            },
            'sessions': {
                'forex': {
                    'london': '08:00-17:00 UTC',
                    'new_york': '13:00-22:00 UTC'
                }
            }
        }
        
        result = validate_config_dict(valid_config)
        assert result.is_valid
        assert len(result.get_errors()) == 0
    
    def test_invalid_config_validation(self):
        """Test validating an invalid configuration"""
        invalid_config = {
            'markets': {
                'crypto': {
                    'enabled': True,
                    # Missing exchanges
                }
            }
            # Missing risk_management
        }
        
        result = validate_config_dict(invalid_config)
        assert not result.is_valid
        assert len(result.get_errors()) > 0
    
    def test_config_file_validation(self):
        """Test validating configuration file"""
        # Create temporary config file
        config_data = {
            'markets': {
                'crypto': {
                    'enabled': True,
                    'exchanges': [{'name': 'mock_crypto', 'type': 'mock'}]
                }
            },
            'risk_management': {
                'unified_limits': {'max_portfolio_risk': 0.02, 'daily_loss_limit': 0.05}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            tester = ConfigurationTester()
            result = tester.test_config_file(Path(temp_path))
            assert result is not None
        finally:
            Path(temp_path).unlink()


class TestMultiMarketTestUtilities:
    """Test the multi-market test utilities"""
    
    @pytest.mark.asyncio
    async def test_test_context_creation(self):
        """Test creating test context"""
        async with MultiMarketTestContext() as context:
            assert context is not None
            
            # Setup mock exchange
            exchange = await context.setup_mock_exchange()
            assert exchange is not None
            assert exchange.is_connected
    
    def test_assertions(self):
        """Test multi-market assertions"""
        assertions = MultiMarketAssertions()
        
        # Test market data assertion
        test_data = MultiMarketTestHelpers.create_test_market_data(
            'BTC/USD', MarketType.CRYPTO, 45000.0
        )
        assertions.assert_market_data_valid(test_data, MarketType.CRYPTO)
        
        # Test order assertion
        test_order = MultiMarketTestHelpers.create_test_order('BTC/USD', 'buy', 0.1, 45000.0)
        assertions.assert_order_valid(test_order, MarketType.CRYPTO)
        
        # Test correlation assertion
        assertions.assert_correlation_in_range(0.8)
        
        # Test risk limits assertion
        assertions.assert_risk_limits_respected(0.01, 0.02)
    
    def test_helpers(self):
        """Test multi-market helpers"""
        helpers = MultiMarketTestHelpers()
        
        # Test correlation calculation
        data1 = [1, 2, 3, 4, 5]
        data2 = [2, 4, 6, 8, 10]  # Perfect positive correlation
        correlation = helpers.calculate_correlation(data1, data2)
        assert abs(correlation - 1.0) < 0.01
        
        # Test volatility calculation
        prices = [100, 101, 99, 102, 98, 103, 97]
        volatility = helpers.calculate_volatility(prices)
        assert volatility > 0
        
        # Test market event simulation
        event = helpers.simulate_market_event('news_release', 0.05)
        assert event['type'] == 'news'
        assert event['impact'] == 0.05
    
    @pytest.mark.asyncio
    async def test_scenario_runner(self):
        """Test scenario test runner"""
        runner = MultiMarketTestRunner()
        
        # Run correlation scenario test
        result = await runner.run_scenario_test(
            'correlation_test',
            test_cross_market_correlation_scenario,
            correlation_threshold=0.5
        )
        
        assert result['scenario'] == 'correlation_test'
        assert result['status'] in ['passed', 'failed']
        assert 'duration' in result
        
        # Get test summary
        summary = runner.get_test_summary()
        assert summary['total_tests'] == 1
        assert 'success_rate' in summary
    
    @pytest.mark.asyncio
    async def test_performance_tester(self):
        """Test performance testing utilities"""
        tester = MultiMarketPerformanceTester()
        
        # Mock operation
        async def mock_operation():
            await asyncio.sleep(0.001)  # 1ms delay
        
        # Measure latency
        latency_metrics = await tester.measure_latency(mock_operation, iterations=10)
        assert 'avg_latency' in latency_metrics
        assert latency_metrics['avg_latency'] > 0
        
        # Measure throughput
        throughput_metrics = await tester.measure_throughput(mock_operation, duration_seconds=1)
        assert 'operations_per_second' in throughput_metrics
        assert throughput_metrics['operations_per_second'] > 0


class TestMultiMarketTestScenarios:
    """Test pre-defined test scenarios"""
    
    def test_scenario_definitions(self):
        """Test scenario definitions"""
        scenarios = MultiMarketTestScenarios()
        
        # Test high correlation scenario
        high_corr = scenarios.high_correlation_scenario()
        assert high_corr['name'] == 'high_correlation'
        assert 'correlation_matrix' in high_corr
        
        # Test market stress scenario
        stress = scenarios.market_stress_scenario()
        assert stress['name'] == 'market_stress'
        assert stress['volatility_multiplier'] > 1.0
        
        # Test session overlap scenario
        overlap = scenarios.session_overlap_scenario()
        assert overlap['name'] == 'session_overlap'
        assert 'active_sessions' in overlap
        
        # Test arbitrage scenario
        arbitrage = scenarios.arbitrage_opportunity_scenario()
        assert arbitrage['name'] == 'arbitrage_opportunity'
        assert 'price_differences' in arbitrage


@pytest.mark.asyncio
async def test_integration_scenario():
    """Integration test using all utilities together"""
    # Create test context
    async with MultiMarketTestContext() as context:
        # Setup mock exchange
        exchange = await context.setup_mock_exchange()
        
        # Generate test data
        test_data = context.generate_test_data('correlated_markets', correlation=0.8)
        
        # Test crypto market operations
        crypto_data = await exchange.get_market_data('BTC/USD', MarketType.CRYPTO)
        MultiMarketAssertions.assert_market_data_valid(crypto_data, MarketType.CRYPTO)
        
        # Test forex market operations
        forex_data = await exchange.get_market_data('EURUSD', MarketType.FOREX)
        MultiMarketAssertions.assert_market_data_valid(forex_data, MarketType.FOREX)
        
        # Place test orders
        crypto_order_id = await exchange.place_order(
            symbol='BTC/USD',
            side='buy',
            amount=0.1,
            market_type=MarketType.CRYPTO
        )
        
        forex_order_id = await exchange.place_order(
            symbol='EURUSD',
            side='buy',
            amount=1000.0,
            market_type=MarketType.FOREX
        )
        
        # Verify orders
        crypto_order_status = await exchange.get_order_status(crypto_order_id)
        forex_order_status = await exchange.get_order_status(forex_order_id)
        
        assert crypto_order_status['status'] == 'filled'
        assert forex_order_status['status'] == 'filled'
        
        # Check positions and balances
        crypto_positions = exchange.get_positions(MarketType.CRYPTO)
        forex_positions = exchange.get_positions(MarketType.FOREX)
        
        crypto_balances = exchange.get_balances(MarketType.CRYPTO)
        forex_balances = exchange.get_balances(MarketType.FOREX)
        
        assert isinstance(crypto_positions, dict)
        assert isinstance(forex_positions, dict)
        assert isinstance(crypto_balances, dict)
        assert isinstance(forex_balances, dict)


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])