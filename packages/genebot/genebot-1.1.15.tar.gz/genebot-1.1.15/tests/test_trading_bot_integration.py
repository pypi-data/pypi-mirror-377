"""
Integration tests for the complete Trading Bot application workflow.

These tests verify that all components work together correctly and that
the main application orchestrator functions as expected.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import the main trading bot
from src.trading_bot import TradingBot, TradingBotState
from src.monitoring.health_server import HealthCheckServer

# Import test utilities
from .test_utils import (
    create_test_config,
    create_mock_market_data,
    create_mock_trading_signal,
    MockExchange,
    MockDatabase
)


class TestTradingBotIntegration:
    """Integration tests for the complete Trading Bot system."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = create_test_config()
            import yaml
            yaml.dump(config_data, f)
            config_file = f.name
        
        yield config_file
        
        # Cleanup
        os.unlink(config_file)
    
    @pytest.fixture
    def temp_env_file(self):
        """Create a temporary environment file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("DEBUG=true\n")
            f.write("DRY_RUN=true\n")
            f.write("LOG_LEVEL=DEBUG\n")
            env_file = f.name
        
        yield env_file
        
        # Cleanup
        os.unlink(env_file)
    
    @pytest.fixture
    def mock_components(self):
        """Mock external components for testing."""
        mocks = {}
        
        # Mock database
        mocks['database'] = MockDatabase()
        
        # Mock exchange
        mocks['exchange'] = MockExchange()
        
        return mocks
    
    @pytest.fixture
    def trading_bot(self, temp_config_file, temp_env_file, mock_components):
        """Create a trading bot instance for testing."""
        with patch('src.database.connection.DatabaseManager', return_value=mock_components['database']):
            with patch('src.exchanges.ccxt_adapter.CCXTAdapter', return_value=mock_components['exchange']):
                bot = TradingBot(config_file=temp_config_file, env_file=temp_env_file)
                yield bot
                
                # Cleanup will be handled by the test
    
    @pytest.mark.asyncio
    async def test_bot_initialization(self, trading_bot):
        """Test that the bot initializes correctly."""
        assert trading_bot.state == TradingBotState.STOPPED
        assert trading_bot.config is not None
        assert trading_bot.config.app_name == "TestTradingBot"
        assert trading_bot.config.dry_run is True
    
    @pytest.mark.asyncio
    async def test_bot_startup_sequence(self, trading_bot, mock_components):
        """Test the enhanced bot startup sequence."""
        # Mock component initialization
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        mock_components['exchange'].health_check = AsyncMock(return_value={'status': 'ok'})
        
        # Start the bot
        success = await trading_bot.start()
        
        assert success is True
        assert trading_bot.state == TradingBotState.RUNNING
        assert trading_bot.start_time is not None
        assert trading_bot.last_heartbeat is not None
        
        # Verify error tracking is reset
        assert trading_bot._consecutive_errors == 0
        assert trading_bot._recovery_attempts == 0
        
        # Verify components were initialized
        mock_components['database'].initialize.assert_called_once()
        mock_components['exchange'].connect.assert_called_once()
        mock_components['exchange'].authenticate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bot_shutdown_sequence(self, trading_bot, mock_components):
        """Test the complete bot shutdown sequence."""
        # Start the bot first
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        mock_components['exchange'].disconnect = AsyncMock(return_value=True)
        mock_components['database'].close = AsyncMock(return_value=True)
        
        await trading_bot.start()
        assert trading_bot.state == TradingBotState.RUNNING
        
        # Stop the bot
        success = await trading_bot.stop()
        
        assert success is True
        assert trading_bot.state == TradingBotState.STOPPED
        
        # Verify components were cleaned up
        mock_components['exchange'].disconnect.assert_called_once()
        mock_components['database'].close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bot_error_handling_during_startup(self, trading_bot, mock_components):
        """Test enhanced error handling during bot startup."""
        # Mock a component failure
        mock_components['database'].initialize = AsyncMock(side_effect=Exception("Database connection failed"))
        
        # Attempt to start the bot
        success = await trading_bot.start()
        
        assert success is False
        assert trading_bot.state == TradingBotState.STOPPED
        
        # Verify error tracking
        assert hasattr(trading_bot, '_consecutive_errors')
        assert hasattr(trading_bot, '_circuit_breakers')
    
    @pytest.mark.asyncio
    async def test_main_trading_loop(self, trading_bot, mock_components):
        """Test the main trading loop functionality."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        
        # Mock data collection
        mock_market_data = [create_mock_market_data()]
        
        with patch.object(trading_bot, '_collect_market_data', return_value=mock_market_data):
            with patch.object(trading_bot, '_process_strategies', return_value=[]):
                with patch.object(trading_bot, '_apply_risk_management', return_value=[]):
                    with patch.object(trading_bot, '_execute_trades', return_value=None):
                        with patch.object(trading_bot, '_update_portfolio', return_value=None):
                            with patch.object(trading_bot, '_collect_metrics', return_value=None):
                                
                                # Start the bot
                                await trading_bot.start()
                                
                                # Let it run for a short time
                                await asyncio.sleep(0.1)
                                
                                # Stop the bot
                                await trading_bot.stop()
                                
                                # Verify the loop ran
                                assert trading_bot.last_heartbeat is not None
    
    @pytest.mark.asyncio
    async def test_signal_processing_workflow(self, trading_bot, mock_components):
        """Test the complete signal processing workflow."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        
        # Create mock signal
        mock_signal = create_mock_trading_signal()
        mock_market_data = [create_mock_market_data()]
        
        # Mock the workflow steps
        with patch.object(trading_bot, '_collect_market_data', return_value=mock_market_data):
            with patch.object(trading_bot, '_process_strategies', return_value=[mock_signal]) as mock_process:
                with patch.object(trading_bot, '_apply_risk_management', return_value=[mock_signal]) as mock_risk:
                    with patch.object(trading_bot, '_execute_trades', return_value=None) as mock_execute:
                        with patch.object(trading_bot, '_update_portfolio', return_value=None):
                            with patch.object(trading_bot, '_collect_metrics', return_value=None):
                                
                                # Start the bot
                                await trading_bot.start()
                                
                                # Let it process one cycle
                                await asyncio.sleep(0.1)
                                
                                # Stop the bot
                                await trading_bot.stop()
                                
                                # Verify the workflow was executed
                                mock_process.assert_called()
                                mock_risk.assert_called()
                                mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_recovery_in_main_loop(self, trading_bot, mock_components):
        """Test error recovery in the main trading loop."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        
        # Mock an error in data collection
        error_count = 0
        
        async def mock_collect_data():
            nonlocal error_count
            error_count += 1
            if error_count <= 2:
                raise Exception("Temporary data collection error")
            return [create_mock_market_data()]
        
        with patch.object(trading_bot, '_collect_market_data', side_effect=mock_collect_data):
            with patch.object(trading_bot, '_process_strategies', return_value=[]):
                with patch.object(trading_bot, '_apply_risk_management', return_value=[]):
                    with patch.object(trading_bot, '_execute_trades', return_value=None):
                        with patch.object(trading_bot, '_update_portfolio', return_value=None):
                            with patch.object(trading_bot, '_collect_metrics', return_value=None):
                                
                                # Start the bot
                                await trading_bot.start()
                                
                                # Let it run and recover from errors
                                await asyncio.sleep(0.2)
                                
                                # Stop the bot
                                await trading_bot.stop()
                                
                                # Verify it recovered and continued running
                                assert error_count > 2
                                assert trading_bot.last_heartbeat is not None
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, trading_bot, mock_components):
        """Test graceful shutdown functionality."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        mock_components['exchange'].disconnect = AsyncMock(return_value=True)
        mock_components['database'].close = AsyncMock(return_value=True)
        
        # Mock order manager and portfolio manager
        mock_order_manager = Mock()
        mock_order_manager.cancel_all_orders = AsyncMock()
        mock_order_manager.close = AsyncMock()
        
        mock_portfolio_manager = Mock()
        mock_portfolio_manager.close_all_positions = AsyncMock()
        
        trading_bot.order_manager = mock_order_manager
        trading_bot.portfolio_manager = mock_portfolio_manager
        
        # Start the bot
        await trading_bot.start()
        
        # Perform graceful shutdown
        await trading_bot.shutdown_gracefully()
        
        # Verify graceful shutdown steps
        mock_order_manager.cancel_all_orders.assert_called_once()
        assert trading_bot.state == TradingBotState.STOPPED
    
    @pytest.mark.asyncio
    async def test_status_reporting(self, trading_bot, mock_components):
        """Test status reporting functionality."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        
        # Test status when stopped
        status = trading_bot.get_status()
        assert status['state'] == TradingBotState.STOPPED.value
        assert status['uptime_seconds'] is None
        
        # Start the bot
        await trading_bot.start()
        
        # Test status when running
        status = trading_bot.get_status()
        assert status['state'] == TradingBotState.RUNNING.value
        assert status['uptime_seconds'] is not None
        assert status['start_time'] is not None
        assert status['config']['app_name'] == "TestTradingBot"
        
        # Stop the bot
        await trading_bot.stop()
    
    @pytest.mark.asyncio
    async def test_performance_summary(self, trading_bot, mock_components):
        """Test performance summary functionality."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        
        # Mock portfolio manager
        mock_portfolio_manager = Mock()
        mock_portfolio_manager.get_portfolio_summary = Mock(return_value={
            'total_value': 100000.0,
            'pnl': 5000.0,
            'positions': 3
        })
        
        trading_bot.portfolio_manager = mock_portfolio_manager
        
        # Start the bot
        await trading_bot.start()
        
        # Get performance summary
        performance = trading_bot.get_performance_summary()
        
        assert 'portfolio' in performance
        assert performance['portfolio']['total_value'] == 100000.0
        
        # Stop the bot
        await trading_bot.stop()
    
    @pytest.mark.asyncio
    async def test_enhanced_error_recovery(self, trading_bot, mock_components):
        """Test the enhanced error recovery mechanisms."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        mock_components['exchange'].health_check = AsyncMock(return_value={'status': 'ok'})
        mock_components['exchange'].disconnect = AsyncMock(return_value=True)
        mock_components['database'].close = AsyncMock(return_value=True)
        
        # Start the bot
        await trading_bot.start()
        
        # Simulate component error
        test_error = Exception("Test component failure")
        await trading_bot._handle_component_error("exchanges", test_error, "test_context")
        
        # Verify error tracking
        assert trading_bot._consecutive_errors > 0
        assert trading_bot._last_error_time is not None
        assert 'exchanges' in trading_bot._circuit_breakers
        
        # Stop the bot
        await trading_bot.stop()
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, trading_bot, mock_components):
        """Test circuit breaker functionality."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        mock_components['exchange'].health_check = AsyncMock(return_value={'status': 'ok'})
        
        # Start the bot
        await trading_bot.start()
        
        # Trigger multiple errors to open circuit breaker
        test_error = Exception("Repeated failure")
        for _ in range(4):  # Exceed the failure threshold
            await trading_bot._handle_component_error("exchanges", test_error)
        
        # Verify circuit breaker is open
        assert trading_bot._circuit_breakers['exchanges']['state'] == 'open'
        assert trading_bot._circuit_breakers['exchanges']['failures'] >= 3
        
        # Test circuit breaker check
        assert not trading_bot._check_circuit_breakers()
        
        # Stop the bot
        await trading_bot.stop()
    
    @pytest.mark.asyncio
    async def test_enhanced_health_checks(self, trading_bot, mock_components):
        """Test enhanced health check functionality."""
        # Setup mocks with health check methods
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['database'].health_check = AsyncMock(return_value={'status': 'ok'})
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        mock_components['exchange'].health_check = AsyncMock(return_value={'status': 'ok'})
        
        # Start the bot
        await trading_bot.start()
        
        # Perform health check
        health_status = await trading_bot._perform_health_checks()
        
        # Verify health check structure
        assert 'timestamp' in health_status
        assert 'overall_status' in health_status
        assert 'components' in health_status
        assert 'circuit_breakers' in health_status
        assert 'error_stats' in health_status
        
        # Verify component health checks
        assert 'main_loop' in health_status['components']
        assert len(health_status['components']) > 0
        
        # Stop the bot
        await trading_bot.stop()
    
    @pytest.mark.asyncio
    async def test_enhanced_graceful_shutdown(self, trading_bot, mock_components):
        """Test enhanced graceful shutdown functionality."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        mock_components['exchange'].health_check = AsyncMock(return_value={'status': 'ok'})
        mock_components['exchange'].disconnect = AsyncMock(return_value=True)
        mock_components['database'].close = AsyncMock(return_value=True)
        
        # Mock order and portfolio managers
        mock_order_manager = Mock()
        mock_order_manager.cancel_all_orders = AsyncMock(return_value=[])
        
        mock_portfolio_manager = Mock()
        mock_portfolio_manager.get_portfolio_summary = Mock(return_value={'total_value': 100000})
        
        trading_bot.order_manager = mock_order_manager
        trading_bot.portfolio_manager = mock_portfolio_manager
        
        # Start the bot
        await trading_bot.start()
        
        # Perform graceful shutdown
        await trading_bot.shutdown_gracefully()
        
        # Verify graceful shutdown steps were executed
        mock_order_manager.cancel_all_orders.assert_called_once()
        assert trading_bot.state == TradingBotState.STOPPED
        
        # Verify cleanup
        assert trading_bot._consecutive_errors == 0
        assert trading_bot._recovery_attempts == 0
    
    @pytest.mark.asyncio
    async def test_comprehensive_status_reporting(self, trading_bot, mock_components):
        """Test comprehensive status reporting."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        mock_components['exchange'].health_check = AsyncMock(return_value={'status': 'ok'})
        
        # Start the bot
        await trading_bot.start()
        
        # Test enhanced status reporting
        status = trading_bot.get_status()
        
        # Verify enhanced status structure
        assert 'error_stats' in status
        assert 'circuit_breakers' in status
        assert 'components' in status
        assert 'database_connected' in status['components']
        assert 'risk_manager_active' in status['components']
        assert 'portfolio_manager_active' in status['components']
        
        # Test performance summary
        performance = trading_bot.get_performance_summary()
        
        # Verify performance summary structure
        assert 'timestamp' in performance
        assert 'bot_state' in performance
        assert 'uptime_seconds' in performance
        assert 'health' in performance
        
        # Stop the bot
        await trading_bot.stop()
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, trading_bot, mock_components):
        """Test the retry mechanism for operations."""
        # Setup mocks
        mock_components['database'].initialize = AsyncMock(return_value=True)
        mock_components['exchange'].connect = AsyncMock(return_value=True)
        mock_components['exchange'].authenticate = AsyncMock(return_value=True)
        
        # Create a mock operation that fails twice then succeeds
        call_count = 0
        async def mock_operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            return "success"
        
        # Start the bot
        await trading_bot.start()
        
        # Test retry mechanism
        result = await trading_bot._retry_operation(mock_operation, 'exchange_operations')
        
        # Verify operation succeeded after retries
        assert result == "success"
        assert call_count == 3  # Failed twice, succeeded on third attempt
        
        # Stop the bot
        await trading_bot.stop()


class TestHealthCheckServer:
    """Tests for the health check HTTP server."""
    
    @pytest.fixture
    async def mock_trading_bot(self):
        """Create a mock trading bot for testing."""
        bot = Mock()
        bot.get_status = Mock(return_value={
            'state': TradingBotState.RUNNING,
            'uptime_seconds': 3600,
            'start_time': datetime.now().isoformat(),
            'last_heartbeat': datetime.now().isoformat(),
            'config': {
                'app_name': 'TestBot',
                'version': '1.0.0',
                'dry_run': True,
                'debug': False
            },
            'components': {
                'exchanges': 1,
                'active_symbols': 5,
                'strategies': 3
            }
        })
        
        bot.get_performance_summary = Mock(return_value={
            'portfolio': {'total_value': 100000.0},
            'strategies': {},
            'risk': {}
        })
        
        bot.exchanges = {'binance': Mock()}
        bot.database_manager = Mock()
        bot.strategy_engine = Mock()
        bot.risk_manager = Mock()
        bot.metrics_collector = Mock()
        
        # Mock health checks
        bot.exchanges['binance'].health_check = AsyncMock(return_value={'status': 'ok'})
        bot.database_manager.health_check = AsyncMock(return_value={'status': 'ok'})
        bot.strategy_engine.get_engine_stats = Mock(return_value={'running': True})
        bot.risk_manager.get_status = Mock(return_value={'active': True})
        bot.metrics_collector.get_current_metrics = AsyncMock(return_value={})
        
        return bot
    
    @pytest.fixture
    async def health_server(self, mock_trading_bot):
        """Create a health check server for testing."""
        server = HealthCheckServer(mock_trading_bot, host="127.0.0.1", port=0)  # Use port 0 for random port
        await server.start()
        
        yield server
        
        await server.stop()
    
    @pytest.mark.asyncio
    async def test_basic_health_check(self, health_server):
        """Test basic health check endpoint."""
        import aiohttp
        
        # Get the actual port
        port = health_server.site._server.sockets[0].getsockname()[1]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://127.0.0.1:{port}/health') as response:
                assert response.status == 200
                data = await response.json()
                assert data['status'] == 'healthy'
                assert 'timestamp' in data
    
    @pytest.mark.asyncio
    async def test_detailed_health_check(self, health_server):
        """Test detailed health check endpoint."""
        import aiohttp
        
        # Get the actual port
        port = health_server.site._server.sockets[0].getsockname()[1]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://127.0.0.1:{port}/health/detailed') as response:
                assert response.status == 200
                data = await response.json()
                assert data['status'] == 'healthy'
                assert 'components' in data
                assert 'bot_state' in data
    
    @pytest.mark.asyncio
    async def test_status_endpoint(self, health_server):
        """Test status endpoint."""
        import aiohttp
        
        # Get the actual port
        port = health_server.site._server.sockets[0].getsockname()[1]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://127.0.0.1:{port}/status') as response:
                assert response.status == 200
                data = await response.json()
                assert data['state'] == TradingBotState.RUNNING
                assert 'uptime_seconds' in data
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, health_server):
        """Test metrics endpoint."""
        import aiohttp
        
        # Get the actual port
        port = health_server.site._server.sockets[0].getsockname()[1]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://127.0.0.1:{port}/metrics') as response:
                assert response.status == 200
                data = await response.json()
                assert 'timestamp' in data
                assert 'uptime_seconds' in data
                assert 'state' in data
    
    @pytest.mark.asyncio
    async def test_readiness_probe(self, health_server):
        """Test Kubernetes-style readiness probe."""
        import aiohttp
        
        # Get the actual port
        port = health_server.site._server.sockets[0].getsockname()[1]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://127.0.0.1:{port}/ready') as response:
                assert response.status == 200
                data = await response.json()
                assert data['status'] == 'ready'
    
    @pytest.mark.asyncio
    async def test_liveness_probe(self, health_server):
        """Test Kubernetes-style liveness probe."""
        import aiohttp
        
        # Get the actual port
        port = health_server.site._server.sockets[0].getsockname()[1]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://127.0.0.1:{port}/live') as response:
                assert response.status == 200
                data = await response.json()
                assert data['status'] == 'alive'


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""
    
    @pytest.mark.asyncio
    async def test_complete_trading_workflow(self):
        """Test a complete trading workflow from start to finish."""
        # This test would simulate a complete trading cycle:
        # 1. Bot startup
        # 2. Market data collection
        # 3. Strategy signal generation
        # 4. Risk management filtering
        # 5. Order execution
        # 6. Portfolio updates
        # 7. Performance monitoring
        # 8. Graceful shutdown
        
        # For now, this is a placeholder for a comprehensive integration test
        # that would require more extensive mocking and setup
        pass
    
    @pytest.mark.asyncio
    async def test_error_scenarios_and_recovery(self):
        """Test various error scenarios and recovery mechanisms."""
        # This test would cover:
        # 1. Exchange disconnections
        # 2. Database failures
        # 3. Strategy errors
        # 4. Network issues
        # 5. Recovery mechanisms
        
        # For now, this is a placeholder for comprehensive error testing
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])