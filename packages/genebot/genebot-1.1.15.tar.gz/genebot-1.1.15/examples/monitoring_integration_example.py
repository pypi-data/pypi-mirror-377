"""
Example demonstrating how to integrate monitoring and alerting into the trading bot.
"""
import asyncio
import yaml
from datetime import datetime
from typing import Dict, Any

from src.monitoring.monitoring_integration import MonitoringManager
from src.monitoring.notification_system import NotificationLevel
from config.logging import get_logger


class TradingBotWithMonitoring:
    """Example trading bot with integrated monitoring."""
    
    def __init__(self, config_path: str = "config/monitoring_config.yaml"):
        """
        Initialize trading bot with monitoring.
        
        Args:
            config_path: Path to monitoring configuration file
        """
        self._logger = get_logger("trading_bot.example")
        
        # Load monitoring configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize monitoring manager
        self.monitoring = MonitoringManager(config.get('monitoring', {}))
        
        # Example trading components (mocked for demonstration)
        self.exchanges = {}
        self.strategies = {}
        self.portfolio = {}
        
        self._running = False
    
    async def start(self):
        """Start the trading bot with monitoring."""
        try:
            self._logger.info("Starting trading bot with monitoring...")
            
            # Start monitoring first
            self.monitoring.start_monitoring()
            
            # Initialize trading components
            await self._initialize_trading_components()
            
            # Start main trading loop
            self._running = True
            await self._main_trading_loop()
            
        except Exception as e:
            self._logger.error(f"Error starting trading bot: {e}", exc_info=True)
            
            # Send critical alert
            self.monitoring.send_alert(
                title="Trading Bot Startup Failed",
                message=f"Failed to start trading bot: {e}",
                level=NotificationLevel.CRITICAL,
                component="startup"
            )
            raise
    
    async def stop(self):
        """Stop the trading bot and monitoring."""
        self._logger.info("Stopping trading bot...")
        
        self._running = False
        
        # Stop monitoring
        self.monitoring.stop_monitoring()
        
        self._logger.info("Trading bot stopped")
    
    async def _initialize_trading_components(self):
        """Initialize trading components with monitoring."""
        self._logger.info("Initializing trading components...")
        
        # Example: Initialize exchanges with monitoring
        with self.monitoring.create_performance_timer("initialization", "exchanges"):
            await self._initialize_exchanges()
        
        # Example: Initialize strategies with monitoring
        with self.monitoring.create_performance_timer("initialization", "strategies"):
            await self._initialize_strategies()
        
        # Send initialization complete notification
        self.monitoring.send_alert(
            title="Trading Bot Initialized",
            message="All trading components have been successfully initialized",
            level=NotificationLevel.INFO,
            component="initialization"
        )
    
    async def _initialize_exchanges(self):
        """Initialize exchange connections."""
        # Mock exchange initialization
        exchanges = ["binance", "coinbase", "kraken"]
        
        for exchange_name in exchanges:
            try:
                # Simulate exchange connection
                await asyncio.sleep(0.1)  # Simulate connection time
                
                # Mock successful connection
                self.exchanges[exchange_name] = {
                    'connected': True,
                    'last_ping': datetime.utcnow()
                }
                
                # Update connection metrics
                self.monitoring.prometheus_exporter.update_exchange_connection(
                    exchange_name, "connected", 1
                )
                
                self._logger.info(f"Connected to {exchange_name}")
                
            except Exception as e:
                self._logger.error(f"Failed to connect to {exchange_name}: {e}")
                
                # Update connection metrics
                self.monitoring.prometheus_exporter.update_exchange_connection(
                    exchange_name, "error", 0
                )
                
                # Send alert for connection failure
                self.monitoring.send_alert(
                    title=f"Exchange Connection Failed",
                    message=f"Failed to connect to {exchange_name}: {e}",
                    level=NotificationLevel.ERROR,
                    component="exchange",
                    exchange=exchange_name
                )
    
    async def _initialize_strategies(self):
        """Initialize trading strategies."""
        # Mock strategy initialization
        strategies = ["moving_average", "rsi", "momentum"]
        
        for strategy_name in strategies:
            try:
                # Simulate strategy initialization
                await asyncio.sleep(0.05)
                
                self.strategies[strategy_name] = {
                    'active': True,
                    'last_signal': None,
                    'performance': {'return': 0.0, 'trades': 0}
                }
                
                self._logger.info(f"Initialized strategy: {strategy_name}")
                
            except Exception as e:
                self._logger.error(f"Failed to initialize strategy {strategy_name}: {e}")
                
                self.monitoring.send_alert(
                    title="Strategy Initialization Failed",
                    message=f"Failed to initialize {strategy_name}: {e}",
                    level=NotificationLevel.WARNING,
                    component="strategy",
                    strategy=strategy_name
                )
    
    async def _main_trading_loop(self):
        """Main trading loop with monitoring."""
        self._logger.info("Starting main trading loop...")
        
        loop_count = 0
        
        while self._running:
            try:
                loop_count += 1
                
                # Monitor loop performance
                with self.monitoring.create_performance_timer("trading", "main_loop"):
                    await self._trading_cycle()
                
                # Update system metrics periodically
                if loop_count % 10 == 0:
                    await self._update_system_metrics()
                
                # Check for alerts periodically
                if loop_count % 20 == 0:
                    await self._check_alert_conditions()
                
                # Sleep between cycles
                await asyncio.sleep(1)
                
            except Exception as e:
                self._logger.error(f"Error in trading loop: {e}", exc_info=True)
                
                # Track error
                with self.monitoring.create_error_context("trading", "main_loop"):
                    raise e
                
                # Send error alert
                self.monitoring.send_alert(
                    title="Trading Loop Error",
                    message=f"Error in main trading loop: {e}",
                    level=NotificationLevel.ERROR,
                    component="trading"
                )
                
                # Continue after error
                await asyncio.sleep(5)
    
    async def _trading_cycle(self):
        """Execute one trading cycle."""
        # Example trading cycle with monitoring
        
        # 1. Collect market data
        with self.monitoring.create_performance_timer("data", "market_data_collection"):
            market_data = await self._collect_market_data()
        
        # 2. Generate strategy signals
        signals = []
        for strategy_name, strategy in self.strategies.items():
            if strategy['active']:
                with self.monitoring.create_performance_timer("strategy", f"{strategy_name}_signal"):
                    signal = await self._generate_strategy_signal(strategy_name, market_data)
                    if signal:
                        signals.append(signal)
                        
                        # Record strategy signal
                        self.monitoring.record_strategy_signal(
                            strategy_name, signal['type'], signal['symbol']
                        )
        
        # 3. Execute trades based on signals
        for signal in signals:
            await self._execute_trade_signal(signal)
        
        # 4. Update portfolio metrics
        await self._update_portfolio_metrics()
    
    async def _collect_market_data(self) -> Dict[str, Any]:
        """Collect market data from exchanges."""
        # Mock market data collection
        await asyncio.sleep(0.01)  # Simulate API call
        
        return {
            'BTC/USDT': {'price': 50000, 'volume': 1000},
            'ETH/USDT': {'price': 3000, 'volume': 500}
        }
    
    async def _generate_strategy_signal(self, strategy_name: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal from strategy."""
        # Mock signal generation
        await asyncio.sleep(0.005)  # Simulate computation
        
        # Randomly generate signals for demonstration
        import random
        if random.random() < 0.1:  # 10% chance of signal
            signal_type = random.choice(['buy', 'sell'])
            symbol = random.choice(list(market_data.keys()))
            
            return {
                'strategy': strategy_name,
                'type': signal_type,
                'symbol': symbol,
                'confidence': random.uniform(0.6, 0.9)
            }
        
        return None
    
    async def _execute_trade_signal(self, signal: Dict[str, Any]):
        """Execute a trading signal."""
        try:
            with self.monitoring.create_performance_timer("trading", "order_execution"):
                # Execute actual trade through exchange adapter
                trade_data = await self._execute_real_trade(signal)
                
                if not trade_data:
                    logger.warning("Trade execution failed")
                    return
                
                # Record trade event
                self.monitoring.record_trade_event(
                    'order_filled',
                    signal['symbol'],
                    trade_data.get('exchange', 'unknown')
                    **trade_data
                )
                
                self._logger.info(f"Executed trade: {signal}")
                
        except Exception as e:
            self._logger.error(f"Failed to execute trade signal: {e}")
            
            # Send trade execution alert
            self.monitoring.send_alert(
                title="Trade Execution Failed",
                message=f"Failed to execute {signal['type']} order for {signal['symbol']}: {e}",
                level=NotificationLevel.ERROR,
                component="trading",
                symbol=signal['symbol'],
                strategy=signal['strategy']
            )
    
    async def _execute_real_trade(self, signal):
        """Execute actual trade through exchange adapter"""
        try:
            # Import exchange adapters
            from src.exchanges.ccxt_adapter import CCXTAdapter
            from src.exchanges.base import ExchangeAdapter
            import os
            
            # Get exchange configuration from environment
            exchange_name = os.getenv('EXCHANGE_NAME', 'binance')
            api_key = os.getenv('EXCHANGE_API_KEY')
            api_secret = os.getenv('EXCHANGE_API_SECRET')
            sandbox_mode = os.getenv('EXCHANGE_SANDBOX', 'true').lower() == 'true'
            
            if not api_key or not api_secret:
                logger.warning("Exchange credentials not configured, using paper trading mode")
                return self._execute_paper_trade(signal)
            
            try:
                # Initialize exchange adapter
                adapter = CCXTAdapter(
                    exchange_name=exchange_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    sandbox=sandbox_mode
                )
                
                # Execute the trade
                order_result = await adapter.place_order(
                    symbol=signal['symbol'],
                    side=signal['type'].lower(),
                    amount=signal.get('quantity', 0.01),
                    order_type='market'
                )
                
                if order_result:
                    logger.info(f"Trade executed successfully: {order_result}")
                    return order_result
                else:
                    logger.error("Trade execution returned no result")
                    return None
                    
            except Exception as exchange_error:
                logger.error(f"Exchange adapter failed: {exchange_error}")
                logger.info("Falling back to paper trading mode")
                return self._execute_paper_trade(signal)
            
        except ImportError as import_error:
            logger.warning(f"Exchange adapters not available: {import_error}")
            logger.info("Using paper trading mode")
            return self._execute_paper_trade(signal)
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return None
    
    def _execute_paper_trade(self, signal):
        """Execute paper trade for testing/demo purposes"""
        import uuid
        from datetime import datetime
        
        # Simulate trade execution
        trade_id = str(uuid.uuid4())[:8]
        
        paper_trade = {
            'id': trade_id,
            'symbol': signal['symbol'],
            'side': signal['type'].lower(),
            'amount': signal.get('quantity', 0.01),
            'price': signal.get('price', 100.0),
            'timestamp': datetime.now().isoformat(),
            'status': 'filled',
            'type': 'paper_trade'
        }
        
        logger.info(f"Paper trade executed: {paper_trade}")
        return paper_trade
    
    async def _update_portfolio_metrics(self):
        """Update portfolio metrics."""
        # Get real portfolio data from exchange adapters
        try:
            from src.exchanges.ccxt_adapter import CCXTAdapter
            import os
            
            # Get exchange configuration
            exchange_name = os.getenv('EXCHANGE_NAME', 'binance')
            api_key = os.getenv('EXCHANGE_API_KEY')
            api_secret = os.getenv('EXCHANGE_API_SECRET')
            sandbox_mode = os.getenv('EXCHANGE_SANDBOX', 'true').lower() == 'true'
            
            if not api_key or not api_secret:
                logger.warning("Exchange credentials not configured, using mock portfolio data")
                self._update_mock_portfolio_metrics()
                return
            
            try:
                # Initialize exchange adapter
                adapter = CCXTAdapter(
                    exchange_name=exchange_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    sandbox=sandbox_mode
                )
                
                # Get account balance
                balance = await adapter.get_balance()
                
                # Get open positions
                positions = await adapter.get_positions()
                
                # Calculate portfolio metrics
                total_balance = sum(balance.values()) if balance else 0
                total_positions = len(positions) if positions else 0
                
                # Update metrics
                portfolio_metrics = {
                    'total_balance': total_balance,
                    'available_balance': balance.get('free', {}).get('USDT', 0) if balance else 0,
                    'total_positions': total_positions,
                    'unrealized_pnl': sum(pos.get('unrealizedPnl', 0) for pos in positions) if positions else 0
                }
                
                # Send metrics to monitoring system
                for metric_name, value in portfolio_metrics.items():
                    self.monitoring.record_metric(f"portfolio.{metric_name}", value)
                
                logger.debug(f"Portfolio metrics updated: {portfolio_metrics}")
                
            except Exception as exchange_error:
                logger.error(f"Failed to retrieve real portfolio data: {exchange_error}")
                logger.info("Using mock portfolio data")
                self._update_mock_portfolio_metrics()
                
        except ImportError:
            logger.warning("Exchange adapters not available, using mock portfolio data")
            self._update_mock_portfolio_metrics()
        except Exception as e:
            logger.error(f"Failed to retrieve portfolio data: {e}")
            self._update_mock_portfolio_metrics()
    
    def _update_mock_portfolio_metrics(self):
        """Update portfolio metrics with mock data for testing"""
        import random
        
        # Generate realistic mock portfolio data
        mock_metrics = {
            'total_balance': round(random.uniform(9500, 10500), 2),
            'available_balance': round(random.uniform(1000, 3000), 2),
            'total_positions': random.randint(2, 8),
            'unrealized_pnl': round(random.uniform(-200, 300), 2)
        }
        
        # Send mock metrics to monitoring system
        for metric_name, value in mock_metrics.items():
            self.monitoring.record_metric(f"portfolio.{metric_name}", value)
        
        logger.debug(f"Mock portfolio metrics updated: {mock_metrics}")
        

    
    async def _update_system_metrics(self):
        """Update system-level metrics."""
        # System metrics are automatically collected by PerformanceMonitor
        # This is just for demonstration of manual updates if needed
        pass
    
    async def _check_alert_conditions(self):
        """Check for alert conditions."""
        # Get current health status
        health_status = self.monitoring.get_health_status()
        
        # Check for critical conditions
        if health_status['overall_status'] == 'critical':
            self.monitoring.send_alert(
                title="Critical System Health Alert",
                message=f"System health is critical. Issues: {', '.join(health_status['issues'])}",
                level=NotificationLevel.CRITICAL,
                component="system"
            )
        
        # Check portfolio value
        portfolio_value = health_status.get('portfolio_value', 0)
        if portfolio_value < 1000:  # Example threshold
            self.monitoring.send_alert(
                title="Low Portfolio Value Alert",
                message=f"Portfolio value has dropped to ${portfolio_value:.2f}",
                level=NotificationLevel.WARNING,
                component="portfolio",
                portfolio_value=portfolio_value
            )
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status."""
        return {
            'health_status': self.monitoring.get_health_status(),
            'performance_report': self.monitoring.get_performance_report(hours=1),
            'notification_providers': self.monitoring.notification_system.get_provider_status()
        }


async def main():
    """Main function demonstrating the monitoring integration."""
    # Create trading bot with monitoring
    bot = TradingBotWithMonitoring()
    
    try:
        # Start the bot
        await bot.start()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        await bot.stop()
    
    except Exception as e:
        print(f"Error: {e}")
        await bot.stop()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())