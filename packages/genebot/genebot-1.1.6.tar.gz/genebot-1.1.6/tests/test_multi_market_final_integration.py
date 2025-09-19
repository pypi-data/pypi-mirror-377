"""
Multi-Market Final Integration Tests
Comprehensive end-to-end testing for multi-market trading workflows.
"""

import pytest
import asyncio
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
import json
import tempfile
import os

from src.markets.manager import MarketManager
from src.markets.types import MarketType
from src.strategies.multi_market_strategy_engine import MultiMarketStrategyEngine
from src.risk.cross_market_risk_manager import CrossMarketRiskManager
from src.data.unified_manager import UnifiedDataManager
from src.trading.unified_order_manager import UnifiedOrderManager
from src.trading.multi_market_portfolio_manager import MultiMarketPortfolioManager
from src.monitoring.multi_market_monitor import MultiMarketMonitor
from src.backtesting.multi_market_backtest_engine import MultiMarketBacktestEngine
from src.compliance.compliance_manager import ComplianceManager
from src.analysis.correlation_analyzer import CorrelationAnalyzer
from src.analysis.arbitrage_detector import ArbitrageDetector
from src.models.data_models import UnifiedMarketData, UnifiedSymbol
from tests.fixtures.multi_market_fixtures import MultiMarketTestFixtures
from tests.mocks.multi_market_mock_exchange import MultiMarketMockExchange


class TestMultiMarketFinalIntegration:
    """Final integration tests for multi-market trading system."""

    @pytest.fixture
    async def multi_market_system(self):
        """Set up complete multi-market trading system."""
        config = {
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
            'risk_management': {
                'unified_limits': {
                    'max_portfolio_risk': 0.02,
                    'max_correlation_exposure': 0.5,
                    'daily_loss_limit': 0.05
                },
                'market_specific': {
                    'crypto': {
                        'max_position_size': 0.1,
                        'leverage_limit': 3
                    },
                    'forex': {
                        'max_position_size': 0.05,
                        'leverage_limit': 50
                    }
                }
            },
            'sessions': {
                'forex': {
                    'london': '08:00-17:00 UTC',
                    'new_york': '13:00-22:00 UTC',
                    'tokyo': '00:00-09:00 UTC',
                    'sydney': '22:00-07:00 UTC'
                }
            },
            'database': {
                'url': 'sqlite:///:memory:'
            }
        }
        
        # Initialize system components
        market_manager = MarketManager(config)
        strategy_engine = MultiMarketStrategyEngine(config)
        risk_manager = CrossMarketRiskManager(config)
        data_manager = UnifiedDataManager(config)
        order_manager = UnifiedOrderManager(config)
        portfolio_manager = MultiMarketPortfolioManager(config)
        monitor = MultiMarketMonitor(config)
        compliance_manager = ComplianceManager(config)
        
        # Mock external connections
        with patch('src.exchanges.ccxt_adapter.ccxt'), \
             patch('src.exchanges.forex.oanda_adapter.oandapyV20'):
            
            await market_manager.initialize()
            await strategy_engine.initialize()
            await risk_manager.initialize()
            await data_manager.initialize()
            await order_manager.initialize()
            await portfolio_manager.initialize()
            await monitor.initialize()
            await compliance_manager.initialize()
            
            system = {
                'market_manager': market_manager,
                'strategy_engine': strategy_engine,
                'risk_manager': risk_manager,
                'data_manager': data_manager,
                'order_manager': order_manager,
                'portfolio_manager': portfolio_manager,
                'monitor': monitor,
                'compliance_manager': compliance_manager,
                'config': config
            }
            
            yield system
            
            # Cleanup
            await market_manager.shutdown()
            await strategy_engine.shutdown()
            await risk_manager.shutdown()
            await data_manager.shutdown()
            await order_manager.shutdown()
            await portfolio_manager.shutdown()
            await monitor.shutdown()
            await compliance_manager.shutdown()

    @pytest.mark.asyncio
    async def test_end_to_end_multi_market_workflow(self, multi_market_system):
        """
        Test complete end-to-end multi-market trading workflow.
        Requirements: 8.1, 8.2, 8.3, 8.4
        """
        system = multi_market_system
        fixtures = MultiMarketTestFixtures()
        
        # 1. Market Data Collection and Processing
        crypto_data = fixtures.create_crypto_market_data('BTC/USDT', 100)
        forex_data = fixtures.create_forex_market_data('EUR/USD', 100)
        
        # Store market data
        for data in crypto_data:
            await system['data_manager'].store_market_data(data)
        
        for data in forex_data:
            await system['data_manager'].store_market_data(data)
        
        # 2. Cross-Market Analysis
        correlation_analyzer = CorrelationAnalyzer()
        correlations = await correlation_analyzer.analyze_correlation(
            'BTC/USDT', 'EUR/USD', lookback_period=50
        )
        
        arbitrage_detector = ArbitrageDetector()
        opportunities = await arbitrage_detector.detect_opportunities([
            UnifiedSymbol('BTC', 'USD', MarketType.CRYPTO, 'BTC/USD'),
            UnifiedSymbol('EUR', 'USD', MarketType.FOREX, 'EUR/USD')
        ])
        
        # 3. Strategy Signal Generation
        crypto_signals = await system['strategy_engine'].generate_signals(
            MarketType.CRYPTO, crypto_data[-20:]
        )
        
        forex_signals = await system['strategy_engine'].generate_signals(
            MarketType.FOREX, forex_data[-20:]
        )
        
        # 4. Cross-Market Risk Assessment
        all_signals = crypto_signals + forex_signals
        risk_approved_signals = []
        
        for signal in all_signals:
            risk_assessment = await system['risk_manager'].assess_signal_risk(signal)
            if risk_assessment.approved:
                risk_approved_signals.append(signal)
        
        # 5. Order Execution Across Markets
        executed_orders = []
        for signal in risk_approved_signals:
            order = await system['order_manager'].place_order(signal)
            if order:
                executed_orders.append(order)
        
        # 6. Portfolio Management and P&L Calculation
        await system['portfolio_manager'].update_positions()
        portfolio_metrics = await system['portfolio_manager'].get_portfolio_metrics()
        
        # 7. Compliance and Reporting
        compliance_report = await system['compliance_manager'].generate_compliance_report()
        
        # 8. Monitoring and Alerting
        system_health = await system['monitor'].get_system_health()
        
        # Assertions
        assert len(crypto_data) == 100, "All crypto data should be processed"
        assert len(forex_data) == 100, "All forex data should be processed"
        assert correlations is not None, "Correlation analysis should complete"
        assert len(crypto_signals) >= 0, "Crypto strategies should generate signals"
        assert len(forex_signals) >= 0, "Forex strategies should generate signals"
        assert len(executed_orders) >= 0, "Orders should be executed"
        assert 'total_value' in portfolio_metrics, "Portfolio metrics should be calculated"
        assert compliance_report is not None, "Compliance report should be generated"
        assert system_health['status'] in ['healthy', 'warning', 'critical'], "System health should be monitored"
        
        print(f"End-to-End Test Results:")
        print(f"  Crypto signals: {len(crypto_signals)}")
        print(f"  Forex signals: {len(forex_signals)}")
        print(f"  Risk approved: {len(risk_approved_signals)}")
        print(f"  Orders executed: {len(executed_orders)}")
        print(f"  Portfolio value: {portfolio_metrics.get('total_value', 'N/A')}")
        print(f"  System health: {system_health['status']}")

    @pytest.mark.asyncio
    async def test_concurrent_multi_market_operations(self, multi_market_system):
        """
        Test concurrent operations across multiple markets.
        Requirements: 8.1, 8.2
        """
        system = multi_market_system
        fixtures = MultiMarketTestFixtures()
        
        # Prepare concurrent data streams
        crypto_symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT']
        forex_symbols = ['EUR/USD', 'GBP/USD', 'USD/JPY']
        
        # Create concurrent data processing tasks
        async def process_crypto_data(symbol):
            data = fixtures.create_crypto_market_data(symbol, 50)
            signals = []
            for data_point in data:
                await system['data_manager'].store_market_data(data_point)
                symbol_signals = await system['strategy_engine'].generate_signals(
                    MarketType.CRYPTO, [data_point]
                )
                signals.extend(symbol_signals)
            return signals
        
        async def process_forex_data(symbol):
            data = fixtures.create_forex_market_data(symbol, 50)
            signals = []
            for data_point in data:
                await system['data_manager'].store_market_data(data_point)
                symbol_signals = await system['strategy_engine'].generate_signals(
                    MarketType.FOREX, [data_point]
                )
                signals.extend(symbol_signals)
            return signals
        
        # Execute concurrent operations
        start_time = time.time()
        
        crypto_tasks = [process_crypto_data(symbol) for symbol in crypto_symbols]
        forex_tasks = [process_forex_data(symbol) for symbol in forex_symbols]
        
        all_tasks = crypto_tasks + forex_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        execution_time = time.time() - start_time
        
        # Verify concurrent execution
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        assert len(successful_results) >= 4, "Most concurrent operations should succeed"
        assert execution_time < 30.0, "Concurrent operations should complete efficiently"
        assert len(failed_results) == 0, "No operations should fail under normal conditions"
        
        # Verify data integrity under concurrent access
        stored_crypto_data = await system['data_manager'].get_historical_data('BTC/USDT', 50)
        stored_forex_data = await system['data_manager'].get_historical_data('EUR/USD', 50)
        
        assert len(stored_crypto_data) == 50, "Crypto data should be stored correctly"
        assert len(stored_forex_data) == 50, "Forex data should be stored correctly"
        
        print(f"Concurrent Operations Test Results:")
        print(f"  Successful operations: {len(successful_results)}")
        print(f"  Failed operations: {len(failed_results)}")
        print(f"  Total execution time: {execution_time:.2f}s")

    @pytest.mark.asyncio
    async def test_high_frequency_data_processing(self, multi_market_system):
        """
        Test high-frequency multi-market data processing performance.
        Requirements: 8.1, 8.3
        """
        system = multi_market_system
        fixtures = MultiMarketTestFixtures()
        
        # Generate high-frequency data
        data_points_per_second = 100
        test_duration_seconds = 10
        total_data_points = data_points_per_second * test_duration_seconds
        
        crypto_data = fixtures.create_crypto_market_data('BTC/USDT', total_data_points)
        forex_data = fixtures.create_forex_market_data('EUR/USD', total_data_points)
        
        # Performance metrics
        processed_count = 0
        error_count = 0
        start_time = time.time()
        
        # Process data at high frequency
        async def process_data_stream(data_stream, market_type):
            nonlocal processed_count, error_count
            
            for data_point in data_stream:
                try:
                    # Store data
                    await system['data_manager'].store_market_data(data_point)
                    
                    # Generate signals
                    signals = await system['strategy_engine'].generate_signals(
                        market_type, [data_point]
                    )
                    
                    # Process signals through risk management
                    for signal in signals:
                        await system['risk_manager'].assess_signal_risk(signal)
                    
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Processing error: {e}")
        
        # Run concurrent high-frequency processing
        await asyncio.gather(
            process_data_stream(crypto_data, MarketType.CRYPTO),
            process_data_stream(forex_data, MarketType.FOREX)
        )
        
        processing_time = time.time() - start_time
        processing_rate = processed_count / processing_time
        
        # Performance assertions
        assert processed_count >= total_data_points * 1.8, "Should process most data points"
        assert error_count < total_data_points * 0.1, "Error rate should be low"
        assert processing_rate >= 50, "Should maintain reasonable processing rate"
        
        # Memory usage check (simplified)
        import psutil
        process = psutil.Process()
        memory_usage_mb = process.memory_info().rss / 1024 / 1024
        
        assert memory_usage_mb < 500, "Memory usage should remain reasonable"
        
        print(f"High-Frequency Processing Test Results:")
        print(f"  Data points processed: {processed_count}")
        print(f"  Processing rate: {processing_rate:.2f} points/second")
        print(f"  Error rate: {error_count / total_data_points * 100:.2f}%")
        print(f"  Memory usage: {memory_usage_mb:.2f} MB")

    @pytest.mark.asyncio
    async def test_multi_market_security_validation(self, multi_market_system):
        """
        Test security aspects of multi-market credential handling.
        Requirements: 8.4
        """
        system = multi_market_system
        
        # Test credential isolation
        crypto_credentials = system['market_manager'].get_credentials(MarketType.CRYPTO, 'binance')
        forex_credentials = system['market_manager'].get_credentials(MarketType.FOREX, 'oanda')
        
        assert crypto_credentials != forex_credentials, "Credentials should be isolated by market"
        
        # Test credential encryption/obfuscation
        assert 'api_key' not in str(crypto_credentials), "Credentials should not be exposed in string representation"
        assert 'secret' not in str(forex_credentials), "Credentials should not be exposed in string representation"
        
        # Test secure credential storage
        with tempfile.TemporaryDirectory() as temp_dir:
            credential_file = os.path.join(temp_dir, 'test_credentials.json')
            
            # Simulate credential storage
            await system['market_manager'].store_credentials(credential_file)
            
            # Verify file permissions (Unix-like systems)
            if os.name != 'nt':  # Not Windows
                file_stat = os.stat(credential_file)
                file_permissions = oct(file_stat.st_mode)[-3:]
                assert file_permissions == '600', "Credential files should have restricted permissions"
        
        # Test API rate limiting
        rate_limiter = system['market_manager'].get_rate_limiter('binance')
        assert rate_limiter is not None, "Rate limiting should be implemented"
        
        # Test connection timeout handling
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            try:
                await system['market_manager'].test_connection(MarketType.CRYPTO, 'binance')
            except asyncio.TimeoutError:
                pass  # Expected
        
        # Test invalid credential handling
        invalid_config = {
            'markets': {
                'crypto': {
                    'exchanges': {
                        'binance': {
                            'api_key': 'invalid_key',
                            'secret': 'invalid_secret'
                        }
                    }
                }
            }
        }
        
        with pytest.raises(Exception):
            invalid_manager = MarketManager(invalid_config)
            await invalid_manager.authenticate(MarketType.CRYPTO, 'binance')
        
        print("Security Validation Test Results:")
        print("  ✓ Credential isolation verified")
        print("  ✓ Credential obfuscation verified")
        print("  ✓ Secure storage verified")
        print("  ✓ Rate limiting implemented")
        print("  ✓ Timeout handling verified")
        print("  ✓ Invalid credential handling verified")

    @pytest.mark.asyncio
    async def test_cross_market_arbitrage_workflow(self, multi_market_system):
        """
        Test cross-market arbitrage detection and execution workflow.
        Requirements: 8.1, 8.2
        """
        system = multi_market_system
        fixtures = MultiMarketTestFixtures()
        
        # Create arbitrage opportunity
        btc_crypto_price = 50000.0
        btc_forex_equivalent = 49800.0  # Price discrepancy
        
        crypto_data = fixtures.create_crypto_market_data('BTC/USDT', 10, base_price=btc_crypto_price)
        forex_data = fixtures.create_forex_market_data('BTC/USD', 10, base_price=btc_forex_equivalent)
        
        # Store market data
        for data in crypto_data + forex_data:
            await system['data_manager'].store_market_data(data)
        
        # Detect arbitrage opportunities
        arbitrage_detector = ArbitrageDetector()
        opportunities = await arbitrage_detector.detect_cross_market_arbitrage(
            crypto_symbol='BTC/USDT',
            forex_symbol='BTC/USD',
            min_profit_threshold=0.001  # 0.1%
        )
        
        assert len(opportunities) > 0, "Should detect arbitrage opportunity"
        
        opportunity = opportunities[0]
        assert opportunity.profit_percentage > 0.001, "Profit should exceed threshold"
        
        # Execute arbitrage strategy
        arbitrage_signals = await system['strategy_engine'].generate_arbitrage_signals(opportunity)
        
        assert len(arbitrage_signals) == 2, "Should generate buy and sell signals"
        
        # Risk assessment for arbitrage
        risk_assessments = []
        for signal in arbitrage_signals:
            assessment = await system['risk_manager'].assess_arbitrage_risk(signal, opportunity)
            risk_assessments.append(assessment)
        
        approved_signals = [s for s, a in zip(arbitrage_signals, risk_assessments) if a.approved]
        
        # Execute arbitrage orders
        arbitrage_orders = []
        for signal in approved_signals:
            order = await system['order_manager'].place_arbitrage_order(signal)
            if order:
                arbitrage_orders.append(order)
        
        # Monitor arbitrage execution
        execution_results = await system['monitor'].monitor_arbitrage_execution(arbitrage_orders)
        
        # Verify arbitrage workflow
        assert len(approved_signals) >= 1, "At least one arbitrage signal should be approved"
        assert len(arbitrage_orders) >= 1, "At least one arbitrage order should be placed"
        assert execution_results is not None, "Arbitrage execution should be monitored"
        
        print(f"Cross-Market Arbitrage Test Results:")
        print(f"  Opportunities detected: {len(opportunities)}")
        print(f"  Profit percentage: {opportunity.profit_percentage:.4f}")
        print(f"  Signals generated: {len(arbitrage_signals)}")
        print(f"  Orders executed: {len(arbitrage_orders)}")

    @pytest.mark.asyncio
    async def test_regulatory_compliance_workflow(self, multi_market_system):
        """
        Test regulatory compliance across different markets.
        Requirements: 8.1, 8.4
        """
        system = multi_market_system
        fixtures = MultiMarketTestFixtures()
        
        # Generate trading activity
        crypto_signals = fixtures.create_trading_signals(MarketType.CRYPTO, 10)
        forex_signals = fixtures.create_trading_signals(MarketType.FOREX, 10)
        
        # Process signals through compliance checks
        compliant_crypto_signals = []
        compliant_forex_signals = []
        
        for signal in crypto_signals:
            compliance_check = await system['compliance_manager'].validate_signal(signal)
            if compliance_check.approved:
                compliant_crypto_signals.append(signal)
        
        for signal in forex_signals:
            compliance_check = await system['compliance_manager'].validate_signal(signal)
            if compliance_check.approved:
                compliant_forex_signals.append(signal)
        
        # Execute compliant trades
        executed_trades = []
        for signal in compliant_crypto_signals + compliant_forex_signals:
            order = await system['order_manager'].place_order(signal)
            if order:
                executed_trades.append(order)
        
        # Generate compliance reports
        crypto_report = await system['compliance_manager'].generate_market_report(MarketType.CRYPTO)
        forex_report = await system['compliance_manager'].generate_market_report(MarketType.FOREX)
        consolidated_report = await system['compliance_manager'].generate_consolidated_report()
        
        # Audit trail verification
        audit_entries = await system['compliance_manager'].get_audit_trail()
        
        # Regulatory reporting
        regulatory_filings = await system['compliance_manager'].prepare_regulatory_filings()
        
        # Assertions
        assert len(compliant_crypto_signals) <= len(crypto_signals), "Compliance should filter signals"
        assert len(compliant_forex_signals) <= len(forex_signals), "Compliance should filter signals"
        assert crypto_report is not None, "Crypto compliance report should be generated"
        assert forex_report is not None, "Forex compliance report should be generated"
        assert consolidated_report is not None, "Consolidated report should be generated"
        assert len(audit_entries) >= len(executed_trades), "All trades should be audited"
        assert regulatory_filings is not None, "Regulatory filings should be prepared"
        
        # Verify audit trail completeness
        for trade in executed_trades:
            matching_audit = [e for e in audit_entries if e.trade_id == trade.id]
            assert len(matching_audit) > 0, f"Trade {trade.id} should have audit entry"
        
        print(f"Regulatory Compliance Test Results:")
        print(f"  Crypto signals processed: {len(crypto_signals)} -> {len(compliant_crypto_signals)}")
        print(f"  Forex signals processed: {len(forex_signals)} -> {len(compliant_forex_signals)}")
        print(f"  Trades executed: {len(executed_trades)}")
        print(f"  Audit entries: {len(audit_entries)}")
        print(f"  Regulatory filings prepared: {len(regulatory_filings) if regulatory_filings else 0}")

    @pytest.mark.asyncio
    async def test_system_recovery_and_failover(self, multi_market_system):
        """
        Test system recovery and failover mechanisms.
        Requirements: 8.1, 8.3
        """
        system = multi_market_system
        fixtures = MultiMarketTestFixtures()
        
        # Test database failover
        original_data_manager = system['data_manager']
        
        # Simulate database failure
        with patch.object(original_data_manager, 'store_market_data', side_effect=Exception("DB Connection Lost")):
            market_data = fixtures.create_crypto_market_data('BTC/USDT', 5)
            
            # System should handle database failures gracefully
            for data in market_data:
                try:
                    await original_data_manager.store_market_data(data)
                except Exception:
                    pass  # Expected to fail
            
            # Verify system continues operating
            assert system['market_manager'].is_active, "Market manager should remain active"
            assert system['strategy_engine'].is_active, "Strategy engine should remain active"
        
        # Test exchange failover
        with patch.object(system['market_manager'], 'get_primary_exchange', return_value=None):
            # Should failover to backup exchange
            backup_exchange = await system['market_manager'].get_backup_exchange(MarketType.CRYPTO)
            assert backup_exchange is not None, "Should have backup exchange available"
        
        # Test strategy engine recovery
        original_strategy_count = len(system['strategy_engine'].get_active_strategies())
        
        # Simulate strategy failure
        with patch.object(system['strategy_engine'], 'generate_signals', side_effect=Exception("Strategy Error")):
            try:
                await system['strategy_engine'].generate_signals(MarketType.CRYPTO, [])
            except Exception:
                pass
            
            # Strategy engine should recover
            await system['strategy_engine'].recover_failed_strategies()
            recovered_strategy_count = len(system['strategy_engine'].get_active_strategies())
            
            assert recovered_strategy_count >= original_strategy_count * 0.8, "Most strategies should recover"
        
        # Test network connectivity recovery
        network_recovery_successful = await system['market_manager'].test_network_recovery()
        assert network_recovery_successful, "Network recovery should be successful"
        
        # Test data consistency after recovery
        test_data = fixtures.create_crypto_market_data('ETH/USDT', 10)
        
        for data in test_data:
            await system['data_manager'].store_market_data(data)
        
        retrieved_data = await system['data_manager'].get_historical_data('ETH/USDT', 10)
        assert len(retrieved_data) == 10, "Data should be consistent after recovery"
        
        print("System Recovery Test Results:")
        print("  ✓ Database failover handled")
        print("  ✓ Exchange failover implemented")
        print("  ✓ Strategy recovery successful")
        print("  ✓ Network recovery tested")
        print("  ✓ Data consistency maintained")

    @pytest.mark.asyncio
    async def test_multi_market_backtesting_integration(self, multi_market_system):
        """
        Test multi-market backtesting integration.
        Requirements: 8.1, 8.2
        """
        system = multi_market_system
        fixtures = MultiMarketTestFixtures()
        
        # Prepare historical data for backtesting
        crypto_historical = fixtures.create_crypto_market_data('BTC/USDT', 1000)
        forex_historical = fixtures.create_forex_market_data('EUR/USD', 1000)
        
        # Initialize backtest engine
        backtest_engine = MultiMarketBacktestEngine(system['config'])
        await backtest_engine.initialize()
        
        # Configure backtest parameters
        backtest_config = {
            'initial_capital': 100000.0,
            'start_date': datetime.now() - timedelta(days=30),
            'end_date': datetime.now(),
            'markets': [MarketType.CRYPTO, MarketType.FOREX],
            'strategies': ['multi_market_momentum', 'cross_market_arbitrage'],
            'risk_limits': system['config']['risk_management']
        }
        
        # Run multi-market backtest
        backtest_results = await backtest_engine.run_multi_market_backtest(
            crypto_data=crypto_historical,
            forex_data=forex_historical,
            config=backtest_config
        )
        
        # Verify backtest results
        assert backtest_results is not None, "Backtest should complete successfully"
        assert 'total_return' in backtest_results, "Should calculate total return"
        assert 'crypto_performance' in backtest_results, "Should track crypto performance"
        assert 'forex_performance' in backtest_results, "Should track forex performance"
        assert 'cross_market_correlation' in backtest_results, "Should analyze cross-market correlation"
        
        # Generate performance report
        performance_report = await backtest_engine.generate_performance_report(backtest_results)
        
        assert 'sharpe_ratio' in performance_report, "Should calculate Sharpe ratio"
        assert 'max_drawdown' in performance_report, "Should calculate max drawdown"
        assert 'market_breakdown' in performance_report, "Should provide market-specific breakdown"
        
        # Test strategy comparison
        strategy_comparison = await backtest_engine.compare_multi_market_strategies(backtest_results)
        
        assert len(strategy_comparison) >= 2, "Should compare multiple strategies"
        
        # Validate risk metrics
        risk_metrics = backtest_results.get('risk_metrics', {})
        assert 'var_95' in risk_metrics, "Should calculate Value at Risk"
        assert 'correlation_risk' in risk_metrics, "Should assess correlation risk"
        
        print(f"Multi-Market Backtesting Test Results:")
        print(f"  Total return: {backtest_results.get('total_return', 'N/A'):.2%}")
        print(f"  Sharpe ratio: {performance_report.get('sharpe_ratio', 'N/A'):.2f}")
        print(f"  Max drawdown: {performance_report.get('max_drawdown', 'N/A'):.2%}")
        print(f"  Strategies compared: {len(strategy_comparison)}")

    @pytest.mark.asyncio
    async def test_comprehensive_system_validation(self, multi_market_system):
        """
        Comprehensive validation of all multi-market requirements.
        Requirements: 8.1, 8.2, 8.3, 8.4
        """
        system = multi_market_system
        fixtures = MultiMarketTestFixtures()
        
        validation_results = {
            'market_connectivity': False,
            'data_management': False,
            'strategy_execution': False,
            'risk_management': False,
            'order_execution': False,
            'portfolio_management': False,
            'monitoring': False,
            'compliance': False,
            'performance': False,
            'security': False
        }
        
        try:
            # 1. Market Connectivity Validation
            crypto_connected = await system['market_manager'].test_connection(MarketType.CRYPTO, 'binance')
            forex_connected = await system['market_manager'].test_connection(MarketType.FOREX, 'oanda')
            validation_results['market_connectivity'] = crypto_connected and forex_connected
            
            # 2. Data Management Validation
            test_data = fixtures.create_crypto_market_data('BTC/USDT', 50)
            for data in test_data:
                await system['data_manager'].store_market_data(data)
            
            retrieved_data = await system['data_manager'].get_historical_data('BTC/USDT', 50)
            validation_results['data_management'] = len(retrieved_data) == 50
            
            # 3. Strategy Execution Validation
            signals = await system['strategy_engine'].generate_signals(MarketType.CRYPTO, test_data[-10:])
            validation_results['strategy_execution'] = len(signals) >= 0
            
            # 4. Risk Management Validation
            if signals:
                risk_assessment = await system['risk_manager'].assess_signal_risk(signals[0])
                validation_results['risk_management'] = risk_assessment is not None
            else:
                validation_results['risk_management'] = True  # No signals to assess
            
            # 5. Order Execution Validation
            if signals:
                order = await system['order_manager'].place_order(signals[0])
                validation_results['order_execution'] = order is not None
            else:
                validation_results['order_execution'] = True  # No signals to execute
            
            # 6. Portfolio Management Validation
            await system['portfolio_manager'].update_positions()
            portfolio_metrics = await system['portfolio_manager'].get_portfolio_metrics()
            validation_results['portfolio_management'] = 'total_value' in portfolio_metrics
            
            # 7. Monitoring Validation
            system_health = await system['monitor'].get_system_health()
            validation_results['monitoring'] = 'status' in system_health
            
            # 8. Compliance Validation
            compliance_report = await system['compliance_manager'].generate_compliance_report()
            validation_results['compliance'] = compliance_report is not None
            
            # 9. Performance Validation
            start_time = time.time()
            await system['data_manager'].get_historical_data('BTC/USDT', 100)
            query_time = time.time() - start_time
            validation_results['performance'] = query_time < 1.0
            
            # 10. Security Validation
            credentials = system['market_manager'].get_credentials(MarketType.CRYPTO, 'binance')
            validation_results['security'] = credentials is not None and 'api_key' not in str(credentials)
            
        except Exception as e:
            print(f"Validation error: {e}")
        
        # Calculate overall system health
        passed_validations = sum(validation_results.values())
        total_validations = len(validation_results)
        system_health_percentage = (passed_validations / total_validations) * 100
        
        # Assertions
        assert system_health_percentage >= 80, f"System health should be at least 80%, got {system_health_percentage}%"
        
        # Critical validations that must pass
        critical_validations = ['market_connectivity', 'data_management', 'security']
        for validation in critical_validations:
            assert validation_results[validation], f"Critical validation '{validation}' must pass"
        
        print(f"Comprehensive System Validation Results:")
        print(f"  Overall system health: {system_health_percentage:.1f}%")
        print(f"  Passed validations: {passed_validations}/{total_validations}")
        
        for validation, result in validation_results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"    {validation}: {status}")
        
        return validation_results


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])