"""
Load testing for concurrent strategy execution and system stress testing.
Enhanced with multi-market load testing capabilities.
"""

import pytest
import asyncio
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict
import psutil

from src.strategies.strategy_engine import StrategyEngine
from src.strategies.moving_average_strategy import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.data.manager import DataManager
from src.trading.order_manager import OrderManager
from src.trading.portfolio_manager import PortfolioManager
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


class TestLoadTesting:
    """Load testing suite for concurrent operations."""

    @pytest.fixture
    def load_test_config(self):
        """Configuration for load testing."""
        return {
            'max_concurrent_strategies': 20,
            'max_concurrent_symbols': 50,
            'stress_test_duration': 30,  # seconds
            'max_orders_per_second': 100,
            'max_data_points_per_second': 1000
        }

    @pytest.fixture
    def multi_market_load_test_config(self):
        """Configuration for multi-market load testing."""
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
            'load_testing': {
                'max_concurrent_strategies': 30,
                'max_concurrent_symbols': 75,
                'stress_test_duration': 45,  # seconds
                'max_orders_per_second': 150,
                'max_data_points_per_second': 1500,
                'multi_market_processing': True
            },
            'database': {
                'url': 'sqlite:///:memory:'
            }
        }

    @pytest.fixture
    async def strategy_engine_cluster(self):
        """Set up multiple strategy engines for load testing."""
        engines = []
        for i in range(5):
            engine = StrategyEngine({})
            await engine.initialize()
            engines.append(engine)
        
        yield engines
        
        for engine in engines:
            await engine.shutdown()

    @pytest.fixture
    async def data_manager_pool(self):
        """Set up multiple data managers for load testing."""
        managers = []
        for i in range(3):
            config = {'database': {'url': f'sqlite:///test_load_{i}.db'}}
            manager = DataManager(config)
            await manager.initialize()
            managers.append(manager)
        
        yield managers
        
        for manager in managers:
            await manager.close()

    @pytest.mark.asyncio
    async def test_concurrent_strategy_load(self, strategy_engine_cluster, load_test_config):
        """Test concurrent execution of multiple strategies under load."""
        max_strategies = load_test_config['max_concurrent_strategies']
        max_symbols = load_test_config['max_concurrent_symbols']
        
        # Distribute strategies across engines
        strategy_count = 0
        for engine in strategy_engine_cluster:
            strategies_per_engine = max_strategies // len(strategy_engine_cluster)
            
            for i in range(strategies_per_engine):
                # Alternate between strategy types
                if strategy_count % 2 == 0:
                    strategy = MovingAverageStrategy({
                        'symbols': [f'PAIR{j}/USDT' for j in range(random.randint(1, 5))],
                        'short_window': random.randint(5, 15),
                        'long_window': random.randint(20, 50)
                    })
                else:
                    strategy = RSIStrategy({
                        'symbols': [f'PAIR{j}/USDT' for j in range(random.randint(1, 5))],
                        'rsi_period': random.randint(10, 20),
                        'oversold_threshold': random.randint(25, 35),
                        'overbought_threshold': random.randint(65, 75)
                    })
                
                engine.register_strategy(f'strategy_{strategy_count}', strategy)
                strategy_count += 1
        
        # Generate market data for all symbols
        symbols = [f'PAIR{i}/USDT' for i in range(max_symbols)]
        market_data_sets = {}
        
        for symbol in symbols:
            market_data_sets[symbol] = create_sample_market_data(symbol, 100)
        
        # Execute concurrent load test
        start_time = time.time()
        tasks = []
        
        # Create tasks for each engine processing different data
        for engine_idx, engine in enumerate(strategy_engine_cluster):
            # Assign subset of symbols to each engine
            engine_symbols = symbols[engine_idx::len(strategy_engine_cluster)]
            
            for symbol in engine_symbols:
                for data_point in market_data_sets[symbol]:
                    task = engine.process_market_data(data_point)
                    tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        error_results = [r for r in results if isinstance(r, Exception)]
        
        success_rate = len(successful_results) / len(results) * 100
        throughput = len(results) / execution_time
        
        print(f"Load Test Results:")
        print(f"  Total tasks: {len(results)}")
        print(f"  Execution time: {execution_time:.2f}s")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Error count: {len(error_results)}")
        print(f"  Throughput: {throughput:.2f} tasks/second")
        
        # Load test assertions
        assert success_rate > 95, f"Success rate {success_rate:.1f}% below 95% threshold"
        assert throughput > 50, f"Throughput {throughput:.2f} below minimum 50 tasks/second"

    @pytest.mark.asyncio
    async def test_high_frequency_data_ingestion(self, data_manager_pool, load_test_config):
        """Test high-frequency data ingestion across multiple data managers."""
        max_data_rate = load_test_config['max_data_points_per_second']
        test_duration = 10  # seconds
        
        # Generate continuous stream of market data
        symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT']
        
        async def data_generator():
            """Generate continuous market data stream."""
            data_points = []
            start_time = time.time()
            
            while time.time() - start_time < test_duration:
                for symbol in symbols:
                    data_point = MarketData(
                        symbol=symbol,
                        timestamp=datetime.now(),
                        open=random.uniform(100, 1000),
                        high=random.uniform(100, 1000),
                        low=random.uniform(100, 1000),
                        close=random.uniform(100, 1000),
                        volume=random.uniform(1000, 10000),
                        exchange='test'
                    )
                    data_points.append(data_point)
                
                # Control data rate
                await asyncio.sleep(len(symbols) / max_data_rate)
            
            return data_points
        
        # Generate data and distribute across managers
        data_points = await data_generator()
        
        # Distribute data points across managers
        tasks = []
        for i, data_point in enumerate(data_points):
            manager = data_manager_pool[i % len(data_manager_pool)]
            task = manager.store_market_data(data_point)
            tasks.append(task)
        
        # Execute data ingestion
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        ingestion_time = end_time - start_time
        successful_ingestions = len([r for r in results if not isinstance(r, Exception)])
        ingestion_rate = successful_ingestions / ingestion_time
        
        print(f"Data Ingestion Results:")
        print(f"  Data points generated: {len(data_points)}")
        print(f"  Successful ingestions: {successful_ingestions}")
        print(f"  Ingestion time: {ingestion_time:.2f}s")
        print(f"  Ingestion rate: {ingestion_rate:.2f} points/second")
        
        # Performance assertions
        assert ingestion_rate > max_data_rate * 0.8, \
            f"Ingestion rate {ingestion_rate:.2f} below 80% of target rate"

    @pytest.mark.asyncio
    async def test_order_processing_under_load(self, load_test_config):
        """Test order processing system under high load."""
        max_orders_per_second = load_test_config['max_orders_per_second']
        test_duration = 15  # seconds
        
        # Set up multiple order managers
        order_managers = []
        for i in range(3):
            mock_exchange = MockExchange()
            manager = OrderManager({'exchanges': {f'exchange_{i}': mock_exchange}})
            await manager.initialize()
            order_managers.append(manager)
        
        try:
            # Generate high-frequency trading signals
            async def signal_generator():
                """Generate continuous trading signals."""
                signals = []
                start_time = time.time()
                signal_id = 0
                
                while time.time() - start_time < test_duration:
                    signal = TradingSignal(
                        symbol=random.choice(['BTC/USDT', 'ETH/USDT', 'ADA/USDT']),
                        action=random.choice(['BUY', 'SELL']),
                        confidence=random.uniform(0.6, 0.9),
                        timestamp=datetime.now(),
                        strategy_name=f'load_test_strategy_{signal_id % 5}',
                        metadata={'position_size': random.uniform(0.01, 0.1)}
                    )
                    signals.append(signal)
                    signal_id += 1
                    
                    # Control signal generation rate
                    await asyncio.sleep(1 / max_orders_per_second)
                
                return signals
            
            # Generate signals
            signals = await signal_generator()
            
            # Process orders across multiple managers
            tasks = []
            for i, signal in enumerate(signals):
                manager = order_managers[i % len(order_managers)]
                task = manager.place_order(signal)
                tasks.append(task)
            
            # Execute order processing
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            processing_time = end_time - start_time
            successful_orders = len([r for r in results if r is not None and not isinstance(r, Exception)])
            order_rate = successful_orders / processing_time
            
            print(f"Order Processing Results:")
            print(f"  Signals generated: {len(signals)}")
            print(f"  Successful orders: {successful_orders}")
            print(f"  Processing time: {processing_time:.2f}s")
            print(f"  Order processing rate: {order_rate:.2f} orders/second")
            
            # Performance assertions
            assert order_rate > max_orders_per_second * 0.7, \
                f"Order rate {order_rate:.2f} below 70% of target rate"
        
        finally:
            # Cleanup
            for manager in order_managers:
                await manager.shutdown()

    @pytest.mark.asyncio
    async def test_stress_test_sustained_load(self, load_test_config):
        """Test system behavior under sustained high load."""
        stress_duration = load_test_config['stress_test_duration']
        
        # Set up system components
        strategy_engine = StrategyEngine({})
        await strategy_engine.initialize()
        
        data_manager = DataManager({'database': {'url': 'sqlite:///:memory:'}})
        await data_manager.initialize()
        
        try:
            # Register multiple strategies
            for i in range(10):
                strategy = MovingAverageStrategy({
                    'symbols': [f'STRESS{j}/USDT' for j in range(5)],
                    'short_window': 5 + i,
                    'long_window': 20 + i * 2
                })
                strategy_engine.register_strategy(f'stress_strategy_{i}', strategy)
            
            # Sustained load test
            start_time = time.time()
            total_operations = 0
            error_count = 0
            
            while time.time() - start_time < stress_duration:
                # Generate batch of operations
                batch_tasks = []
                
                # Data ingestion tasks
                for _ in range(50):
                    data_point = MarketData(
                        symbol=f'STRESS{random.randint(0, 4)}/USDT',
                        timestamp=datetime.now(),
                        open=random.uniform(100, 1000),
                        high=random.uniform(100, 1000),
                        low=random.uniform(100, 1000),
                        close=random.uniform(100, 1000),
                        volume=random.uniform(1000, 10000),
                        exchange='stress_test'
                    )
                    
                    # Store data
                    batch_tasks.append(data_manager.store_market_data(data_point))
                    
                    # Process through strategies
                    batch_tasks.append(strategy_engine.process_market_data(data_point))
                
                # Execute batch
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Count operations and errors
                total_operations += len(batch_results)
                error_count += len([r for r in batch_results if isinstance(r, Exception)])
                
                # Brief pause between batches
                await asyncio.sleep(0.1)
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            # Calculate metrics
            operations_per_second = total_operations / actual_duration
            error_rate = error_count / total_operations * 100
            
            print(f"Stress Test Results:")
            print(f"  Duration: {actual_duration:.2f}s")
            print(f"  Total operations: {total_operations}")
            print(f"  Operations per second: {operations_per_second:.2f}")
            print(f"  Error count: {error_count}")
            print(f"  Error rate: {error_rate:.2f}%")
            
            # Stress test assertions
            assert operations_per_second > 100, \
                f"Operations per second {operations_per_second:.2f} below minimum threshold"
            assert error_rate < 5, f"Error rate {error_rate:.2f}% exceeds 5% threshold"
        
        finally:
            await strategy_engine.shutdown()
            await data_manager.close()

    def test_thread_safety_concurrent_access(self):
        """Test thread safety under concurrent access patterns."""
        # Shared data structure to test thread safety
        shared_data = defaultdict(list)
        lock = threading.Lock()
        
        def worker_thread(thread_id, iterations=1000):
            """Worker thread that performs concurrent operations."""
            for i in range(iterations):
                # Simulate concurrent data access
                with lock:
                    shared_data[thread_id].append(i)
                    # Read from other threads' data
                    for other_id in shared_data:
                        if other_id != thread_id and shared_data[other_id]:
                            _ = shared_data[other_id][-1]
        
        # Run multiple threads concurrently
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            
            start_time = time.time()
            
            for thread_id in range(num_threads):
                future = executor.submit(worker_thread, thread_id)
                futures.append(future)
            
            # Wait for all threads to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    pytest.fail(f"Thread safety test failed: {e}")
            
            end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verify data integrity
        total_items = sum(len(items) for items in shared_data.values())
        expected_items = num_threads * 1000
        
        print(f"Thread Safety Test Results:")
        print(f"  Threads: {num_threads}")
        print(f"  Execution time: {execution_time:.2f}s")
        print(f"  Total items: {total_items}")
        print(f"  Expected items: {expected_items}")
        
        # Thread safety assertions
        assert total_items == expected_items, \
            f"Data integrity compromised: {total_items} != {expected_items}"
        assert len(shared_data) == num_threads, \
            f"Thread data isolation failed: {len(shared_data)} != {num_threads}"

    # Multi-Market Load Testing

    @pytest.mark.asyncio
    async def test_multi_market_concurrent_strategy_load(self, multi_market_load_test_config):
        """Test concurrent execution of multi-market strategies under load."""
        strategy_engine = MultiMarketStrategyEngine(multi_market_load_test_config)
        await strategy_engine.initialize()
        
        fixtures = MultiMarketTestFixtures()
        
        try:
            max_strategies = multi_market_load_test_config['load_testing']['max_concurrent_strategies']
            max_symbols = multi_market_load_test_config['load_testing']['max_concurrent_symbols']
            
            # Register strategies for both markets
            crypto_symbols = [f'CRYPTO{i}/USDT' for i in range(max_symbols // 2)]
            forex_symbols = [f'FOREX{i}/USD' for i in range(max_symbols // 2)]
            
            # Generate market data for all symbols
            crypto_data_sets = {}
            forex_data_sets = {}
            
            for symbol in crypto_symbols:
                crypto_data_sets[symbol] = fixtures.create_crypto_market_data(symbol, 100)
            
            for symbol in forex_symbols:
                forex_data_sets[symbol] = fixtures.create_forex_market_data(symbol, 100)
            
            # Execute concurrent multi-market load test
            start_time = time.time()
            tasks = []
            
            # Create tasks for crypto market processing
            for symbol, data_list in crypto_data_sets.items():
                for data_point in data_list:
                    task = strategy_engine.generate_signals(MarketType.CRYPTO, [data_point])
                    tasks.append(task)
            
            # Create tasks for forex market processing
            for symbol, data_list in forex_data_sets.items():
                for data_point in data_list:
                    task = strategy_engine.generate_signals(MarketType.FOREX, [data_point])
                    tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Analyze results
            successful_results = [r for r in results if not isinstance(r, Exception)]
            error_results = [r for r in results if isinstance(r, Exception)]
            
            success_rate = len(successful_results) / len(results) * 100
            throughput = len(results) / execution_time
            
            print(f"Multi-Market Load Test Results:")
            print(f"  Total tasks: {len(results)}")
            print(f"  Crypto data points: {sum(len(data) for data in crypto_data_sets.values())}")
            print(f"  Forex data points: {sum(len(data) for data in forex_data_sets.values())}")
            print(f"  Execution time: {execution_time:.2f}s")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Error count: {len(error_results)}")
            print(f"  Throughput: {throughput:.2f} tasks/second")
            
            # Multi-market load test assertions
            assert success_rate > 90, f"Multi-market success rate {success_rate:.1f}% below 90% threshold"
            assert throughput > 75, f"Multi-market throughput {throughput:.2f} below minimum 75 tasks/second"
        
        finally:
            await strategy_engine.shutdown()

    @pytest.mark.asyncio
    async def test_multi_market_high_frequency_data_ingestion(self, multi_market_load_test_config):
        """Test high-frequency data ingestion across multiple markets."""
        data_manager = UnifiedDataManager(multi_market_load_test_config)
        await data_manager.initialize()
        
        fixtures = MultiMarketTestFixtures()
        
        try:
            max_data_rate = multi_market_load_test_config['load_testing']['max_data_points_per_second']
            test_duration = 15  # seconds
            
            # Generate continuous stream of multi-market data
            crypto_symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT']
            forex_symbols = ['EUR/USD', 'GBP/USD', 'USD/JPY']
            
            async def multi_market_data_generator():
                """Generate continuous multi-market data stream."""
                data_points = []
                start_time = time.time()
                
                while time.time() - start_time < test_duration:
                    # Generate crypto data
                    for symbol in crypto_symbols:
                        data_point = fixtures.create_single_crypto_data_point(symbol)
                        data_points.append(data_point)
                    
                    # Generate forex data
                    for symbol in forex_symbols:
                        data_point = fixtures.create_single_forex_data_point(symbol)
                        data_points.append(data_point)
                    
                    # Control data rate
                    total_symbols = len(crypto_symbols) + len(forex_symbols)
                    await asyncio.sleep(total_symbols / max_data_rate)
                
                return data_points
            
            # Generate multi-market data
            data_points = await multi_market_data_generator()
            
            # Ingest data concurrently
            tasks = []
            for data_point in data_points:
                task = data_manager.store_market_data(data_point)
                tasks.append(task)
            
            # Execute data ingestion
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            ingestion_time = end_time - start_time
            successful_ingestions = len([r for r in results if not isinstance(r, Exception)])
            ingestion_rate = successful_ingestions / ingestion_time
            
            # Count by market type
            crypto_points = len([dp for dp in data_points if dp.market_type == MarketType.CRYPTO])
            forex_points = len([dp for dp in data_points if dp.market_type == MarketType.FOREX])
            
            print(f"Multi-Market Data Ingestion Results:")
            print(f"  Total data points: {len(data_points)}")
            print(f"  Crypto data points: {crypto_points}")
            print(f"  Forex data points: {forex_points}")
            print(f"  Successful ingestions: {successful_ingestions}")
            print(f"  Ingestion time: {ingestion_time:.2f}s")
            print(f"  Ingestion rate: {ingestion_rate:.2f} points/second")
            
            # Performance assertions for multi-market
            assert ingestion_rate > max_data_rate * 0.75, \
                f"Multi-market ingestion rate {ingestion_rate:.2f} below 75% of target rate"
        
        finally:
            await data_manager.shutdown()

    @pytest.mark.asyncio
    async def test_multi_market_order_processing_under_load(self, multi_market_load_test_config):
        """Test multi-market order processing system under high load."""
        order_manager = UnifiedOrderManager(multi_market_load_test_config)
        await order_manager.initialize()
        
        fixtures = MultiMarketTestFixtures()
        
        try:
            max_orders_per_second = multi_market_load_test_config['load_testing']['max_orders_per_second']
            test_duration = 20  # seconds
            
            # Generate high-frequency multi-market trading signals
            async def multi_market_signal_generator():
                """Generate continuous multi-market trading signals."""
                signals = []
                start_time = time.time()
                signal_id = 0
                
                crypto_symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT']
                forex_symbols = ['EUR/USD', 'GBP/USD', 'USD/JPY']
                
                while time.time() - start_time < test_duration:
                    # Generate crypto signals
                    crypto_signal = fixtures.create_single_trading_signal(
                        MarketType.CRYPTO, 
                        random.choice(crypto_symbols)
                    )
                    signals.append(crypto_signal)
                    
                    # Generate forex signals
                    forex_signal = fixtures.create_single_trading_signal(
                        MarketType.FOREX,
                        random.choice(forex_symbols)
                    )
                    signals.append(forex_signal)
                    
                    signal_id += 2
                    
                    # Control signal generation rate
                    await asyncio.sleep(2 / max_orders_per_second)
                
                return signals
            
            # Generate signals
            signals = await multi_market_signal_generator()
            
            # Process orders across markets
            tasks = []
            for signal in signals:
                task = order_manager.place_order(signal)
                tasks.append(task)
            
            # Execute order processing
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            processing_time = end_time - start_time
            successful_orders = len([r for r in results if r is not None and not isinstance(r, Exception)])
            order_rate = successful_orders / processing_time
            
            # Count by market type
            crypto_signals = len([s for s in signals if hasattr(s, 'market_type') and s.market_type == MarketType.CRYPTO])
            forex_signals = len([s for s in signals if hasattr(s, 'market_type') and s.market_type == MarketType.FOREX])
            
            print(f"Multi-Market Order Processing Results:")
            print(f"  Total signals: {len(signals)}")
            print(f"  Crypto signals: {crypto_signals}")
            print(f"  Forex signals: {forex_signals}")
            print(f"  Successful orders: {successful_orders}")
            print(f"  Processing time: {processing_time:.2f}s")
            print(f"  Order processing rate: {order_rate:.2f} orders/second")
            
            # Performance assertions for multi-market
            assert order_rate > max_orders_per_second * 0.6, \
                f"Multi-market order rate {order_rate:.2f} below 60% of target rate"
        
        finally:
            await order_manager.shutdown()

    @pytest.mark.asyncio
    async def test_multi_market_stress_test_sustained_load(self, multi_market_load_test_config):
        """Test multi-market system behavior under sustained high load."""
        stress_duration = multi_market_load_test_config['load_testing']['stress_test_duration']
        
        # Set up multi-market system components
        data_manager = UnifiedDataManager(multi_market_load_test_config)
        strategy_engine = MultiMarketStrategyEngine(multi_market_load_test_config)
        
        await data_manager.initialize()
        await strategy_engine.initialize()
        
        fixtures = MultiMarketTestFixtures()
        
        try:
            # Sustained multi-market load test
            start_time = time.time()
            total_operations = 0
            error_count = 0
            crypto_operations = 0
            forex_operations = 0
            
            # Monitor system resources
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            while time.time() - start_time < stress_duration:
                # Generate batch of multi-market operations
                batch_tasks = []
                
                # Crypto market operations
                for _ in range(25):
                    crypto_data = fixtures.create_single_crypto_data_point(f'STRESS{random.randint(0, 4)}/USDT')
                    
                    # Store data
                    batch_tasks.append(data_manager.store_market_data(crypto_data))
                    
                    # Process through strategies
                    batch_tasks.append(strategy_engine.generate_signals(MarketType.CRYPTO, [crypto_data]))
                    
                    crypto_operations += 2
                
                # Forex market operations
                for _ in range(25):
                    forex_data = fixtures.create_single_forex_data_point(f'STRESS{random.randint(0, 4)}/USD')
                    
                    # Store data
                    batch_tasks.append(data_manager.store_market_data(forex_data))
                    
                    # Process through strategies
                    batch_tasks.append(strategy_engine.generate_signals(MarketType.FOREX, [forex_data]))
                    
                    forex_operations += 2
                
                # Execute batch
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Count operations and errors
                total_operations += len(batch_results)
                error_count += len([r for r in batch_results if isinstance(r, Exception)])
                
                # Brief pause between batches
                await asyncio.sleep(0.1)
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            # Calculate metrics
            operations_per_second = total_operations / actual_duration
            error_rate = error_count / total_operations * 100 if total_operations > 0 else 0
            
            # Check memory usage
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_growth = final_memory - initial_memory
            
            print(f"Multi-Market Stress Test Results:")
            print(f"  Duration: {actual_duration:.2f}s")
            print(f"  Total operations: {total_operations}")
            print(f"  Crypto operations: {crypto_operations}")
            print(f"  Forex operations: {forex_operations}")
            print(f"  Operations per second: {operations_per_second:.2f}")
            print(f"  Error count: {error_count}")
            print(f"  Error rate: {error_rate:.2f}%")
            print(f"  Memory growth: {memory_growth:.2f}MB")
            
            # Multi-market stress test assertions
            assert operations_per_second > 150, \
                f"Multi-market operations per second {operations_per_second:.2f} below minimum threshold"
            assert error_rate < 8, f"Multi-market error rate {error_rate:.2f}% exceeds 8% threshold"
            assert memory_growth < 200, f"Memory growth {memory_growth:.2f}MB indicates potential leak"
        
        finally:
            await strategy_engine.shutdown()
            await data_manager.shutdown()

    @pytest.mark.asyncio
    async def test_multi_market_resource_utilization_under_load(self, multi_market_load_test_config):
        """Test resource utilization during multi-market load testing."""
        data_manager = UnifiedDataManager(multi_market_load_test_config)
        strategy_engine = MultiMarketStrategyEngine(multi_market_load_test_config)
        
        await data_manager.initialize()
        await strategy_engine.initialize()
        
        fixtures = MultiMarketTestFixtures()
        
        try:
            # Monitor resource utilization
            resource_snapshots = []
            test_duration = 30
            
            start_time = time.time()
            
            while time.time() - start_time < test_duration:
                cycle_start = time.time()
                
                # Generate and process multi-market data
                crypto_data = fixtures.create_crypto_market_data('BTC/USDT', 20)
                forex_data = fixtures.create_forex_market_data('EUR/USD', 20)
                
                # Process both markets concurrently
                async def process_crypto():
                    for data_point in crypto_data:
                        await data_manager.store_market_data(data_point)
                        await strategy_engine.generate_signals(MarketType.CRYPTO, [data_point])
                
                async def process_forex():
                    for data_point in forex_data:
                        await data_manager.store_market_data(data_point)
                        await strategy_engine.generate_signals(MarketType.FOREX, [data_point])
                
                await asyncio.gather(process_crypto(), process_forex())
                
                # Take resource snapshot
                process = psutil.Process()
                snapshot = {
                    'timestamp': time.time() - start_time,
                    'memory_mb': process.memory_info().rss / 1024 / 1024,
                    'cpu_percent': process.cpu_percent(),
                    'crypto_points': len(crypto_data),
                    'forex_points': len(forex_data)
                }
                resource_snapshots.append(snapshot)
                
                # Maintain target rate
                cycle_time = time.time() - cycle_start
                if cycle_time < 1.0:
                    await asyncio.sleep(1.0 - cycle_time)
            
            # Analyze resource utilization
            memory_usage = [s['memory_mb'] for s in resource_snapshots]
            cpu_usage = [s['cpu_percent'] for s in resource_snapshots]
            
            avg_memory = sum(memory_usage) / len(memory_usage)
            max_memory = max(memory_usage)
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            max_cpu = max(cpu_usage)
            
            total_crypto_points = sum(s['crypto_points'] for s in resource_snapshots)
            total_forex_points = sum(s['forex_points'] for s in resource_snapshots)
            
            print(f"Multi-Market Resource Utilization Results:")
            print(f"  Test duration: {test_duration}s")
            print(f"  Total crypto points: {total_crypto_points}")
            print(f"  Total forex points: {total_forex_points}")
            print(f"  Average memory: {avg_memory:.2f}MB")
            print(f"  Peak memory: {max_memory:.2f}MB")
            print(f"  Average CPU: {avg_cpu:.1f}%")
            print(f"  Peak CPU: {max_cpu:.1f}%")
            
            # Resource utilization assertions
            assert max_memory < 800, f"Peak memory {max_memory:.2f}MB exceeds reasonable limit for multi-market"
            assert avg_cpu < 90, f"Average CPU usage {avg_cpu:.1f}% too high for sustained multi-market operations"
            
            # Check for resource efficiency
            total_points = total_crypto_points + total_forex_points
            memory_per_point = avg_memory / (total_points / len(resource_snapshots)) if total_points > 0 else 0
            
            assert memory_per_point < 5, f"Memory per data point {memory_per_point:.2f}MB indicates inefficiency"
        
        finally:
            await strategy_engine.shutdown()
            await data_manager.shutdown()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])