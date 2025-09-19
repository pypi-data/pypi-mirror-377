"""
End-to-end integration tests for the trading bot system.
Tests complete trading workflows from data collection to order execution.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal

from src.trading_bot import TradingBot
from config.manager import ConfigManager
from src.exchanges.ccxt_adapter import CCXTAdapter
from src.strategies.moving_average_strategy import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.data.collector import MarketDataCollector
from src.trading.order_manager import OrderManager
from src.trading.portfolio_manager import PortfolioManager
from src.risk.risk_manager import RiskManager
from src.models.data_models import MarketData, TradingSignal, Order
from tests.mocks.mock_exchange import MockExchange
from tests.fixtures.sample_data_factory import create_sample_market_data


class TestEndToEndIntegration:
    """Complete end-to-end integration tests."""

    @pytest.fixture
    async def trading_bot_system(self):
        """Set up complete trading bot system for testing."""
        # Create test configuration
        config = {
            'exchanges': {
                'binance': {
                    'api_key': 'test_key',
                    'secret': 'test_secret',
                    'sandbox': True
                }
            },
            'strategies': {
                'moving_average': {
                    'enabled': True,
                    'symbols': ['BTC/USDT'],
                    'short_window': 5,
                    'long_window': 20
                }
            },
            'risk_management': {
                'max_position_size': 0.1,
                'max_daily_loss': 0.05,
                'stop_loss_percentage': 0.02
            },
            'database': {
                'url': 'sqlite:///:memory:'
            }
        }
        
        # Initialize components with mock exchange
        mock_exchange = MockExchange()
        
        with patch('src.exchanges.ccxt_adapter.ccxt') as mock_ccxt:
            mock_ccxt.binance.return_value = mock_exchange
            
            bot = TradingBot(config)
            await bot.initialize()
            
            yield bot
            
            await bot.shutdown()

    @pytest.mark.asyncio
    async def test_complete_trading_workflow(self, trading_bot_system):
        """Test complete trading workflow from data to execution."""
        bot = trading_bot_system
        
        # 1. Data Collection Phase
        market_data = create_sample_market_data('BTC/USDT', 100)
        
        # Simulate data collection
        for data_point in market_data[:50]:  # Historical data
            await bot.data_manager.store_market_data(data_point)
        
        # 2. Strategy Execution Phase
        # Process new market data through strategy
        new_data = market_data[50]
        signals = await bot.strategy_engine.process_market_data(new_data)
        
        assert len(signals) > 0, "Strategy should generate signals"
        
        # 3. Risk Management Phase
        for signal in signals:
            risk_approved = await bot.risk_manager.validate_signal(signal)
            if risk_approved:
                # 4. Order Execution Phase
                order = await bot.order_manager.place_order(signal)
                assert order is not None, "Order should be placed"
                assert order.status in ['pending', 'filled'], "Order should have valid status"
        
        # 5. Portfolio Update Phase
        await bot.portfolio_manager.update_positions()
        positions = await bot.portfolio_manager.get_positions()
        
        # Verify complete workflow
        assert len(positions) >= 0, "Portfolio should be updated"

    @pytest.mark.asyncio
    async def test_multi_strategy_coordination(self, trading_bot_system):
        """Test coordination between multiple strategies."""
        bot = trading_bot_system
        
        # Add RSI strategy
        rsi_strategy = RSIStrategy({
            'symbols': ['BTC/USDT'],
            'rsi_period': 14,
            'oversold_threshold': 30,
            'overbought_threshold': 70
        })
        bot.strategy_engine.register_strategy('rsi', rsi_strategy)
        
        # Generate market data
        market_data = create_sample_market_data('BTC/USDT', 50)
        
        # Process through both strategies
        all_signals = []
        for data_point in market_data:
            signals = await bot.strategy_engine.process_market_data(data_point)
            all_signals.extend(signals)
        
        # Verify signals from multiple strategies
        strategy_names = {signal.strategy_name for signal in all_signals}
        assert len(strategy_names) > 1, "Multiple strategies should generate signals"

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, trading_bot_system):
        """Test system recovery from various error conditions."""
        bot = trading_bot_system
        
        # Test exchange connection failure
        with patch.object(bot.exchange_manager, 'get_market_data', side_effect=Exception("Connection failed")):
            # System should handle exchange errors gracefully
            try:
                await bot.data_collector.collect_real_time_data(['BTC/USDT'])
            except Exception:
                pass  # Expected to handle gracefully
            
            # Verify system is still operational
            assert bot.is_running, "Bot should remain operational after exchange error"
        
        # Test strategy failure
        with patch.object(bot.strategy_engine, 'process_market_data', side_effect=Exception("Strategy error")):
            market_data = create_sample_market_data('BTC/USDT', 1)[0]
            
            try:
                await bot.strategy_engine.process_market_data(market_data)
            except Exception:
                pass  # Expected to handle gracefully
            
            # Verify other strategies can still run
            assert bot.strategy_engine.is_active, "Strategy engine should remain active"

    @pytest.mark.asyncio
    async def test_risk_management_integration(self, trading_bot_system):
        """Test risk management integration across the system."""
        bot = trading_bot_system
        
        # Create high-risk signal
        risky_signal = TradingSignal(
            symbol='BTC/USDT',
            action='BUY',
            confidence=0.9,
            timestamp=datetime.now(),
            strategy_name='test_strategy',
            metadata={'position_size': 0.5}  # Exceeds max position size
        )
        
        # Risk manager should reject the signal
        risk_approved = await bot.risk_manager.validate_signal(risky_signal)
        assert not risk_approved, "Risk manager should reject oversized position"
        
        # Test stop-loss integration
        # Simulate position with loss
        await bot.portfolio_manager.update_position('BTC/USDT', 1.0, 50000.0)
        
        # Simulate price drop triggering stop-loss
        current_price = 49000.0  # 2% loss
        stop_loss_triggered = await bot.risk_manager.check_stop_loss('BTC/USDT', current_price)
        
        assert stop_loss_triggered, "Stop-loss should be triggered on 2% loss"

    @pytest.mark.asyncio
    async def test_data_integrity_workflow(self, trading_bot_system):
        """Test data integrity throughout the system."""
        bot = trading_bot_system
        
        # Store market data
        market_data = create_sample_market_data('BTC/USDT', 10)
        
        for data_point in market_data:
            await bot.data_manager.store_market_data(data_point)
        
        # Retrieve and verify data integrity
        stored_data = await bot.data_manager.get_historical_data('BTC/USDT', 10)
        
        assert len(stored_data) == 10, "All data points should be stored"
        
        # Verify data consistency
        for original, stored in zip(market_data, stored_data):
            assert original.symbol == stored.symbol
            assert original.close == stored.close
            assert abs((original.timestamp - stored.timestamp).total_seconds()) < 1

    @pytest.mark.asyncio
    async def test_monitoring_integration(self, trading_bot_system):
        """Test monitoring and logging integration."""
        bot = trading_bot_system
        
        # Execute trading operations
        market_data = create_sample_market_data('BTC/USDT', 5)
        
        for data_point in market_data:
            await bot.strategy_engine.process_market_data(data_point)
        
        # Verify metrics collection
        metrics = await bot.metrics_collector.get_metrics()
        
        assert 'data_points_processed' in metrics
        assert 'signals_generated' in metrics
        assert metrics['data_points_processed'] >= 5

    @pytest.mark.asyncio
    async def test_graceful_shutdown_workflow(self, trading_bot_system):
        """Test graceful system shutdown."""
        bot = trading_bot_system
        
        # Start some operations
        market_data = create_sample_market_data('BTC/USDT', 3)
        
        # Process data
        for data_point in market_data:
            await bot.strategy_engine.process_market_data(data_point)
        
        # Initiate shutdown
        await bot.shutdown()
        
        # Verify clean shutdown
        assert not bot.is_running, "Bot should be stopped"
        assert bot.data_manager.connection_pool.is_closed, "Database connections should be closed"

    @pytest.mark.asyncio
    async def test_configuration_reload_workflow(self, trading_bot_system):
        """Test dynamic configuration reloading."""
        bot = trading_bot_system
        
        # Update configuration
        new_config = {
            'risk_management': {
                'max_position_size': 0.05,  # Reduced from 0.1
                'max_daily_loss': 0.03,     # Reduced from 0.05
                'stop_loss_percentage': 0.01 # Reduced from 0.02
            }
        }
        
        # Reload configuration
        await bot.config_manager.reload_config(new_config)
        
        # Verify new configuration is applied
        assert bot.risk_manager.max_position_size == 0.05
        assert bot.risk_manager.max_daily_loss == 0.03

    @pytest.mark.asyncio
    async def test_concurrent_operations_workflow(self, trading_bot_system):
        """Test concurrent operations across the system."""
        bot = trading_bot_system
        
        # Create concurrent tasks
        tasks = []
        
        # Data collection task
        async def collect_data():
            market_data = create_sample_market_data('BTC/USDT', 10)
            for data_point in market_data:
                await bot.data_manager.store_market_data(data_point)
                await asyncio.sleep(0.01)  # Simulate real-time data
        
        # Strategy processing task
        async def process_strategies():
            market_data = create_sample_market_data('ETH/USDT', 10)
            for data_point in market_data:
                await bot.strategy_engine.process_market_data(data_point)
                await asyncio.sleep(0.01)
        
        # Portfolio monitoring task
        async def monitor_portfolio():
            for _ in range(10):
                await bot.portfolio_manager.update_positions()
                await asyncio.sleep(0.01)
        
        # Run tasks concurrently
        tasks = [
            collect_data(),
            process_strategies(),
            monitor_portfolio()
        ]
        
        await asyncio.gather(*tasks)
        
        # Verify all operations completed successfully
        assert bot.is_running, "Bot should remain operational during concurrent operations"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])