"""
Performance tests for high-frequency data processing and system throughput.
Enhanced with multi-market testing capabilities.
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

from src.data.collector import MarketDataCollector
from src.data.manager import DataManager
from src.strategies.moving_average_strategy import MovingAverageStrategy
from src.strategies.strategy_engine import StrategyEngine
from src.trading.order_manager import OrderManager
from src.models.data_models import MarketData, TradingSignal
from tests.fixtures.sample_data_factory import create_sample_market_data
from tests.mocks.mock_exchange import MockExchange

# Multi-market imports
from src.markets.manager import MarketManager
from src.markets.types import MarketType
from src.data.unified_manager import UnifiedDataManager
from src.strategies.multi_market_strategy_engine import MultiMarketStrategyEngine
from src.trading.unified_order_manager import UnifiedOrderManager
from tests.fixtures.multi_market_fixtures import MultiMarketTestFixtures
from tests.mocks.multi_market_mock_exchange import MultiMarketMockExchange


class TestPerformance:
    """Performance and load testing suite."""

    @pytest.fixture
    def performance_config(self):
        """Configuration for performance testing."""
        return {
            'high_frequency_data_points': 10000,
            'concurrent_strategies': 5,
            'concurrent_symbols': 10,
            'memory_threshold_mb': 500,
            'latency_threshold_ms': 100
        }

    @pytest.fixture
    def multi_market_performance_config(self):
        """Configuration for multi-market performance testing."""
        return {
            'markets': {
                'crypto': {
                    'enabled': True,
                    'exchanges': {
                        'binance': {
                            'api_key': 'test_crypto_key',
                            'secret': 'test_crypto_secret',
                            'sandbox': True
                        }
                    }
                },
                'forex': {
                    'enabled': True,
                    'brokers': {
                        'oanda': {
                            'api_key': 'test_forex_key',
                            'account_id': 'test_account',
                            'environment': 'practice'
                        }
                    }
                }
            },
            'performance': {
                'high_frequency_data_points': 15000,
                'concurrent_strategies': 8,
                'concurrent_symbols': 15,
                'memory_threshold_mb': 750,
                'latency_threshold_ms': 150,
                'multi_market_processing': True
            },
            'database': {
                'url': 'sqlite:///:memory:'
            }
        }

    @pytest.fixture
    async def data_manager(self):
        """Set up data manager for performance testing."""
        config = {'database': {'url': 'sqlite:///:memory:'}}
        manager = DataManager(config)
        await manager.initialize()
        yield manager
        await manager.close()

    @pytest.fixture
    async def strategy_engine(self):
        """Set up strategy engine for performance testing."""
        engine = StrategyEngine({})
        await engine.initialize()
        yield engine
        await engine.shutdown()

    @pytest.mark.asyncio
    async def test_high_frequency_data_processing(self, data_manager, performance_config):
        """Test processing high-frequency market data."""
        data_points = performance_config['high_frequency_data_points']
        
        # Generate large dataset
        market_data = create_sample_market_data('BTC/USDT', data_points)
        
        # Measure processing time
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Process data in batches
        batch_size = 1000
        for i in range(0, len(market_data), batch_size):
            batch = market_data[i:i + batch_size]
            await data_manager.store_market_data_batch(batch)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Performance assertions
        processing_time = end_time - start_time
        throughput = data_points / processing_time
        memory_usage = end_memory - start_memory
        
        print(f"Processed {data_points} data points in {processing_time:.2f}s")
        print(f"Throughput: {throughput:.2f} data points/second")
        print(f"Memory usage: {memory_usage:.2f} MB")
        
        # Performance requirements
        assert throughput > 1000, f"Throughput {throughput:.2f} below minimum 1000 points/second"
        assert memory_usage < performance_config['memory_threshold_mb'], \
            f"Memory usage {memory_usage:.2f}MB exceeds threshold"

    @pytest.mark.asyncio
    async def test_concurrent_strategy_execution(self, strategy_engine, performance_config):
        """Test concurrent execution of multiple strategies."""
        num_strategies = performance_config['concurrent_strategies']
        num_symbols = performance_config['concurrent_symbols']
        
        # Create multiple strategies
        strategies = []
        for i in range(num_strategies):
            strategy = MovingAverageStrategy({
                'symbols': [f'SYMBOL{j}/USDT' for j in range(num_symbols)],
                'short_window': 5 + i,
                'long_window': 20 + i * 2
            })
            strategies.append(strategy)
            strategy_engine.register_strategy(f'ma_strategy_{i}', strategy)
        
        # Generate market data for all symbols
        all_market_data = {}
        for j in range(num_symbols):
            symbol = f'SYMBOL{j}/USDT'
            all_market_data[symbol] = create_sample_market_data(symbol, 100)
        
        # Measure concurrent processing
        start_time = time.time()
        
        # Process data concurrently across strategies
        tasks = []
        for symbol, data_list in all_market_data.items():
            for data_point in data_list:
                task = strategy_engine.process_market_data(data_point)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Count successful processing
        successful_results = [r for r in results if not isinstance(r, Exception)]
        error_count = len(results) - len(successful_results)
        
        print(f"Processed {len(tasks)} data points across {num_strategies} strategies")
        print(f"Processing time: {processing_time:.2f}s")
        print(f"Success rate: {len(successful_results)/len(tasks)*100:.1f}%")
        print(f"Errors: {error_count}")
        
        # Performance requirements
        assert processing_time < 30, f"Processing time {processing_time:.2f}s exceeds 30s limit"
        assert error_count < len(tasks) * 0.05, f"Error rate {error_count/len(tasks)*100:.1f}% too high"

    @pytest.mark.asyncio
    async def test_order_processing_latency(self, performance_config):
        """Test order processing latency under load."""
        mock_exchange = MockExchange()
        order_manager = OrderManager({'exchanges': {'test': mock_exchange}})
        await order_manager.initialize()
        
        # Generate trading signals
        signals = []
        for i in range(1000):
            signal = TradingSignal(
                symbol='BTC/USDT',
                action='BUY' if i % 2 == 0 else 'SELL',
                confidence=0.8,
                timestamp=datetime.now(),
                strategy_name='test_strategy',
                metadata={'position_size': 0.01}
            )
            signals.append(signal)
        
        # Measure order processing latency
        latencies = []
        
        for signal in signals[:100]:  # Test subset for latency measurement
            start_time = time.time()
            
            try:
                order = await order_manager.place_order(signal)
                end_time = time.time()
                
                if order:
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
            except Exception as e:
                print(f"Order processing error: {e}")
        
        # Calculate latency statistics
        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
            max_latency = max(latencies)
            
            print(f"Average latency: {avg_latency:.2f}ms")
            print(f"95th percentile latency: {p95_latency:.2f}ms")
            print(f"Maximum latency: {max_latency:.2f}ms")
            
            # Performance requirements
            assert avg_latency < performance_config['latency_threshold_ms'], \
                f"Average latency {avg_latency:.2f}ms exceeds threshold"
            assert p95_latency < performance_config['latency_threshold_ms'] * 2, \
                f"95th percentile latency {p95_latency:.2f}ms too high"
        
        await order_manager.shutdown()

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, data_manager, performance_config):
        """Test memory usage during extended operations."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Simulate extended operation
        for cycle in range(10):
            # Generate and process data
            market_data = create_sample_market_data('BTC/USDT', 1000)
            
            for data_point in market_data:
                await data_manager.store_market_data(data_point)
            
            # Check memory usage
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_growth = current_memory - initial_memory
            
            print(f"Cycle {cycle + 1}: Memory usage {current_memory:.2f}MB "
                  f"(growth: {memory_growth:.2f}MB)")
            
            # Force garbage collection
            gc.collect()
            
            # Memory growth should be reasonable
            assert memory_growth < performance_config['memory_threshold_mb'], \
                f"Memory growth {memory_growth:.2f}MB exceeds threshold"

    @pytest.mark.asyncio
    async def test_database_performance(self, data_manager):
        """Test database performance under high load."""
        # Test bulk insert performance
        market_data = create_sample_market_data('BTC/USDT', 5000)
        
        start_time = time.time()
        await data_manager.store_market_data_batch(market_data)
        insert_time = time.time() - start_time
        
        insert_rate = len(market_data) / insert_time
        print(f"Database insert rate: {insert_rate:.2f} records/second")
        
        # Test query performance
        start_time = time.time()
        retrieved_data = await data_manager.get_historical_data('BTC/USDT', 5000)
        query_time = time.time() - start_time
        
        query_rate = len(retrieved_data) / query_time
        print(f"Database query rate: {query_rate:.2f} records/second")
        
        # Performance requirements
        assert insert_rate > 500, f"Insert rate {insert_rate:.2f} below minimum"
        assert query_rate > 1000, f"Query rate {query_rate:.2f} below minimum"

    def test_cpu_usage_monitoring(self):
        """Test CPU usage during intensive operations."""
        # Monitor CPU usage during computation-intensive task
        cpu_percentages = []
        
        def cpu_monitor():
            for _ in range(10):
                cpu_percentages.append(psutil.cpu_percent(interval=0.1))
        
        # Start CPU monitoring in background
        with ThreadPoolExecutor() as executor:
            monitor_future = executor.submit(cpu_monitor)
            
            # Perform CPU-intensive task
            strategy = MovingAverageStrategy({
                'symbols': ['BTC/USDT'],
                'short_window': 10,
                'long_window': 50
            })
            
            market_data = create_sample_market_data('BTC/USDT', 1000)
            
            # Process data synchronously to stress CPU
            for data_point in market_data:
                # Simulate CPU-intensive calculation
                strategy._calculate_moving_averages(data_point)
            
            monitor_future.result()
        
        avg_cpu = statistics.mean(cpu_percentages)
        max_cpu = max(cpu_percentages)
        
        print(f"Average CPU usage: {avg_cpu:.1f}%")
        print(f"Maximum CPU usage: {max_cpu:.1f}%")
        
        # CPU usage should be reasonable
        assert avg_cpu < 80, f"Average CPU usage {avg_cpu:.1f}% too high"

    @pytest.mark.asyncio
    async def test_throughput_scaling(self, strategy_engine):
        """Test system throughput scaling with load."""
        throughput_results = []
        
        # Test different load levels
        load_levels = [100, 500, 1000, 2000]
        
        for load in load_levels:
            market_data = create_sample_market_data('BTC/USDT', load)
            
            start_time = time.time()
            
            # Process all data points
            tasks = []
            for data_point in market_data:
                task = strategy_engine.process_market_data(data_point)
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            processing_time = end_time - start_time
            throughput = load / processing_time
            
            throughput_results.append((load, throughput))
            print(f"Load: {load}, Throughput: {throughput:.2f} points/second")
        
        # Verify throughput scales reasonably
        for i in range(1, len(throughput_results)):
            prev_load, prev_throughput = throughput_results[i-1]
            curr_load, curr_throughput = throughput_results[i]
            
            # Throughput shouldn't degrade significantly with increased load
            degradation = (prev_throughput - curr_throughput) / prev_throughput
            assert degradation < 0.5, \
                f"Throughput degradation {degradation*100:.1f}% too high at load {curr_load}"

    # Multi-Market Performance Tests

    @pytest.mark.asyncio
    async def test_multi_market_high_frequency_processing(self, multi_market_performance_config):
        """Test high-frequency processing across multiple markets."""
        data_manager = UnifiedDataManager(multi_market_performance_config)
        await data_manager.initialize()
        
        fixtures = MultiMarketTestFixtures()
        
        # Generate high-frequency data for both markets
        crypto_points = multi_market_performance_config['performance']['high_frequency_data_points'] // 2
        forex_points = multi_market_performance_config['performance']['high_frequency_data_points'] // 2
        
        crypto_data = fixtures.create_crypto_market_data('BTC/USDT', crypto_points)
        forex_data = fixtures.create_forex_market_data('EUR/USD', forex_points)
        
        # Measure concurrent processing performance
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        async def process_crypto_data():
            batch_size = 500
            for i in range(0, len(crypto_data), batch_size):
                batch = crypto_data[i:i + batch_size]
                for data_point in batch:
                    await data_manager.store_market_data(data_point)
        
        async def process_forex_data():
            batch_size = 500
            for i in range(0, len(forex_data), batch_size):
                batch = forex_data[i:i + batch_size]
                for data_point in batch:
                    await data_manager.store_market_data(data_point)
        
        # Process both markets concurrently
        await asyncio.gather(process_crypto_data(), process_forex_data())
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Calculate performance metrics
        processing_time = end_time - start_time
        total_points = crypto_points + forex_points
        throughput = total_points / processing_time
        memory_usage = end_memory - start_memory
        
        print(f"Multi-Market Processing Results:")
        print(f"  Processed {total_points} data points in {processing_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} points/second")
        print(f"  Memory usage: {memory_usage:.2f} MB")
        
        # Performance assertions
        assert throughput > 1500, f"Multi-market throughput {throughput:.2f} below minimum 1500 points/second"
        assert memory_usage < multi_market_performance_config['performance']['memory_threshold_mb'], \
            f"Memory usage {memory_usage:.2f}MB exceeds threshold"
        
        await data_manager.shutdown()

    @pytest.mark.asyncio
    async def test_multi_market_concurrent_strategy_execution(self, multi_market_performance_config):
        """Test concurrent execution of strategies across multiple markets."""
        strategy_engine = MultiMarketStrategyEngine(multi_market_performance_config)
        await strategy_engine.initialize()
        
        fixtures = MultiMarketTestFixtures()
        
        # Create data for multiple symbols across markets
        crypto_symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT']
        forex_symbols = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD']
        
        crypto_data_streams = {}
        forex_data_streams = {}
        
        for symbol in crypto_symbols:
            crypto_data_streams[symbol] = fixtures.create_crypto_market_data(symbol, 200)
        
        for symbol in forex_symbols:
            forex_data_streams[symbol] = fixtures.create_forex_market_data(symbol, 200)
        
        # Measure concurrent multi-market processing
        start_time = time.time()
        
        async def process_crypto_symbol(symbol, data):
            signals = []
            for data_point in data:
                symbol_signals = await strategy_engine.generate_signals(MarketType.CRYPTO, [data_point])
                signals.extend(symbol_signals)
            return signals
        
        async def process_forex_symbol(symbol, data):
            signals = []
            for data_point in data:
                symbol_signals = await strategy_engine.generate_signals(MarketType.FOREX, [data_point])
                signals.extend(symbol_signals)
            return signals
        
        # Execute all strategies concurrently
        tasks = []
        
        for symbol, data in crypto_data_streams.items():
            task = process_crypto_symbol(symbol, data)
            tasks.append(task)
        
        for symbol, data in forex_data_streams.items():
            task = process_forex_symbol(symbol, data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        total_data_points = sum(len(data) for data in crypto_data_streams.values()) + \
                           sum(len(data) for data in forex_data_streams.values())
        
        print(f"Multi-Market Strategy Execution Results:")
        print(f"  Processed {total_data_points} data points across {len(tasks)} symbol streams")
        print(f"  Processing time: {processing_time:.2f}s")
        print(f"  Success rate: {len(successful_results)/len(tasks)*100:.1f}%")
        
        # Performance requirements
        assert processing_time < 45, f"Multi-market processing time {processing_time:.2f}s exceeds 45s limit"
        assert len(successful_results) >= len(tasks) * 0.9, "At least 90% of strategy executions should succeed"
        
        await strategy_engine.shutdown()

    @pytest.mark.asyncio
    async def test_multi_market_order_processing_latency(self, multi_market_performance_config):
        """Test order processing latency across multiple markets."""
        order_manager = UnifiedOrderManager(multi_market_performance_config)
        await order_manager.initialize()
        
        fixtures = MultiMarketTestFixtures()
        
        # Generate signals for both markets
        crypto_signals = fixtures.create_trading_signals(MarketType.CRYPTO, 100)
        forex_signals = fixtures.create_trading_signals(MarketType.FOREX, 100)
        
        all_signals = crypto_signals + forex_signals
        
        # Measure order processing latency
        crypto_latencies = []
        forex_latencies = []
        
        for signal in crypto_signals[:50]:  # Test subset
            start_time = time.time()
            
            try:
                order = await order_manager.place_order(signal)
                end_time = time.time()
                
                if order:
                    latency_ms = (end_time - start_time) * 1000
                    crypto_latencies.append(latency_ms)
            except Exception as e:
                print(f"Crypto order processing error: {e}")
        
        for signal in forex_signals[:50]:  # Test subset
            start_time = time.time()
            
            try:
                order = await order_manager.place_order(signal)
                end_time = time.time()
                
                if order:
                    latency_ms = (end_time - start_time) * 1000
                    forex_latencies.append(latency_ms)
            except Exception as e:
                print(f"Forex order processing error: {e}")
        
        # Calculate latency statistics
        if crypto_latencies:
            crypto_avg = statistics.mean(crypto_latencies)
            crypto_p95 = statistics.quantiles(crypto_latencies, n=20)[18] if len(crypto_latencies) >= 20 else max(crypto_latencies)
            print(f"Crypto - Average latency: {crypto_avg:.2f}ms, 95th percentile: {crypto_p95:.2f}ms")
        
        if forex_latencies:
            forex_avg = statistics.mean(forex_latencies)
            forex_p95 = statistics.quantiles(forex_latencies, n=20)[18] if len(forex_latencies) >= 20 else max(forex_latencies)
            print(f"Forex - Average latency: {forex_avg:.2f}ms, 95th percentile: {forex_p95:.2f}ms")
        
        # Performance requirements
        latency_threshold = multi_market_performance_config['performance']['latency_threshold_ms']
        
        if crypto_latencies:
            assert crypto_avg < latency_threshold, f"Crypto average latency {crypto_avg:.2f}ms exceeds threshold"
        
        if forex_latencies:
            assert forex_avg < latency_threshold, f"Forex average latency {forex_avg:.2f}ms exceeds threshold"
        
        await order_manager.shutdown()

    @pytest.mark.asyncio
    async def test_multi_market_memory_usage_under_load(self, multi_market_performance_config):
        """Test memory usage during extended multi-market operations."""
        data_manager = UnifiedDataManager(multi_market_performance_config)
        await data_manager.initialize()
        
        fixtures = MultiMarketTestFixtures()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Simulate extended multi-market operation
        for cycle in range(15):
            # Generate data for both markets
            crypto_data = fixtures.create_crypto_market_data('BTC/USDT', 500)
            forex_data = fixtures.create_forex_market_data('EUR/USD', 500)
            
            # Process data concurrently
            async def store_crypto_data():
                for data_point in crypto_data:
                    await data_manager.store_market_data(data_point)
            
            async def store_forex_data():
                for data_point in forex_data:
                    await data_manager.store_market_data(data_point)
            
            await asyncio.gather(store_crypto_data(), store_forex_data())
            
            # Check memory usage
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_growth = current_memory - initial_memory
            
            print(f"Multi-Market Cycle {cycle + 1}: Memory usage {current_memory:.2f}MB "
                  f"(growth: {memory_growth:.2f}MB)")
            
            # Force garbage collection
            gc.collect()
            
            # Memory growth should be reasonable for multi-market operations
            memory_threshold = multi_market_performance_config['performance']['memory_threshold_mb']
            assert memory_growth < memory_threshold, \
                f"Multi-market memory growth {memory_growth:.2f}MB exceeds threshold {memory_threshold}MB"
        
        await data_manager.shutdown()

    @pytest.mark.asyncio
    async def test_multi_market_throughput_scaling(self, multi_market_performance_config):
        """Test multi-market system throughput scaling with load."""
        data_manager = UnifiedDataManager(multi_market_performance_config)
        strategy_engine = MultiMarketStrategyEngine(multi_market_performance_config)
        
        await data_manager.initialize()
        await strategy_engine.initialize()
        
        fixtures = MultiMarketTestFixtures()
        throughput_results = []
        
        # Test different load levels for multi-market processing
        load_levels = [50, 150, 300, 600, 1000]  # Per market
        
        for load in load_levels:
            crypto_data = fixtures.create_crypto_market_data('BTC/USDT', load)
            forex_data = fixtures.create_forex_market_data('EUR/USD', load)
            
            start_time = time.time()
            
            # Process data concurrently across markets
            async def process_crypto():
                tasks = []
                for data_point in crypto_data:
                    await data_manager.store_market_data(data_point)
                    task = strategy_engine.generate_signals(MarketType.CRYPTO, [data_point])
                    tasks.append(task)
                await asyncio.gather(*tasks, return_exceptions=True)
            
            async def process_forex():
                tasks = []
                for data_point in forex_data:
                    await data_manager.store_market_data(data_point)
                    task = strategy_engine.generate_signals(MarketType.FOREX, [data_point])
                    tasks.append(task)
                await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.gather(process_crypto(), process_forex())
            
            end_time = time.time()
            processing_time = end_time - start_time
            total_load = load * 2  # Both markets
            throughput = total_load / processing_time
            
            throughput_results.append((total_load, throughput))
            print(f"Multi-Market Load: {total_load}, Throughput: {throughput:.2f} points/second")
        
        # Verify multi-market throughput scales reasonably
        for i in range(1, len(throughput_results)):
            prev_load, prev_throughput = throughput_results[i-1]
            curr_load, curr_throughput = throughput_results[i]
            
            # Allow for more degradation in multi-market scenarios
            degradation = (prev_throughput - curr_throughput) / prev_throughput
            assert degradation < 0.7, \
                f"Multi-market throughput degradation {degradation*100:.1f}% too high at load {curr_load}"
        
        await data_manager.shutdown()
        await strategy_engine.shutdown()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])