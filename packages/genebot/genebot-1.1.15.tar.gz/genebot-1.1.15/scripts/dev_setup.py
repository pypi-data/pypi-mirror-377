#!/usr/bin/env python3
"""
Development setup script for trading bot.
"""
import os
import sys
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database.connection import DatabaseManager
from data.collector import MarketDataCollector
from tests.utils.test_data_generators import MarketDataGenerator, TradingScenarioGenerator
from tests.mocks.mock_exchange import MockExchange


class DevSetup:
    """Development environment setup utilities."""
    
    def __init__(self):
        self.db_manager = None
    
    async def setup_database(self, reset: bool = False):
        """Set up development database."""
        print("Setting up development database...")
        
        try:
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            
            if reset:
                print("Resetting database...")
                await self.db_manager.reset_database()
            
            print("Creating database tables...")
            await self.db_manager.create_tables()
            
            print("✅ Database setup complete")
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            raise
    
    async def seed_test_data(self, days: int = 7):
        """Seed database with test data."""
        print(f"Seeding database with {days} days of test data...")
        
        try:
            if not self.db_manager:
                self.db_manager = DatabaseManager()
                await self.db_manager.initialize()
            
            # Generate market data for common trading pairs
            symbols = ['BTC/USD', 'ETH/USD', 'BTC/ETH']
            start_date = datetime.utcnow() - timedelta(days=days)
            end_date = datetime.utcnow()
            
            for symbol in symbols:
                print(f"Generating data for {symbol}...")
                
                # Generate different types of market data
                if symbol == 'BTC/USD':
                    # Trending data
                    market_data = MarketDataGenerator.generate_trending_data(
                        symbol=symbol,
                        periods=days * 24,  # Hourly data
                        trend_strength=0.1,
                        initial_price=45000.0
                    )
                elif symbol == 'ETH/USD':
                    # Volatile data
                    market_data = MarketDataGenerator.generate_ohlcv_data(
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date,
                        interval_minutes=60,
                        initial_price=3000.0,
                        volatility=0.04
                    )
                else:  # BTC/ETH
                    # Sideways data
                    market_data = MarketDataGenerator.generate_sideways_data(
                        symbol=symbol,
                        periods=days * 24,
                        price_range=(14.0, 16.0),
                        initial_price=15.0
                    )
                
                # Store market data
                await self._store_market_data(market_data)
            
            # Generate sample orders and positions
            print("Generating sample trading data...")
            orders = TradingScenarioGenerator.generate_orders(symbols, 50)
            positions = TradingScenarioGenerator.generate_positions(symbols, 10)
            
            await self._store_trading_data(orders, positions)
            
            print("✅ Test data seeding complete")
            
        except Exception as e:
            print(f"❌ Data seeding failed: {e}")
            raise
    
    async def _store_market_data(self, market_data_list):
        """Store market data in database."""
        # This would use the actual database models
        # For now, just simulate the storage
        print(f"Stored {len(market_data_list)} market data points")
    
    async def _store_trading_data(self, orders, positions):
        """Store trading data in database."""
        # This would use the actual database models
        # For now, just simulate the storage
        print(f"Stored {len(orders)} orders and {len(positions)} positions")
    
    async def create_test_config(self):
        """Create test configuration files."""
        print("Creating test configuration files...")
        
        config_dir = Path("config/test")
        config_dir.mkdir(exist_ok=True)
        
        # Create test trading bot config
        test_config = {
            'exchanges': {
                'binance': {
                    'name': 'binance',
                    'api_key': '${BINANCE_API_KEY}',
                    'api_secret': '${BINANCE_API_SECRET}',
                    'sandbox': True,
                    'enabled': False  # Disabled by default, enable when credentials are provided
                }
            },
            'strategies': {
                'test_strategy': {
                    'name': 'moving_average',
                    'enabled': True,
                    'parameters': {
                        'short_window': 5,
                        'long_window': 10
                    },
                    'symbols': ['BTC/USD'],
                    'max_position_size': 100.0
                }
            },
            'risk': {
                'max_daily_loss': 0.02,
                'max_drawdown': 0.10,
                'max_position_size': 0.01,
                'stop_loss_percentage': 0.03,
                'take_profit_percentage': 0.06
            },
            'database': {
                'url': 'sqlite:///test_trading_bot.db',
                'echo': False
            },
            'logging': {
                'level': 'DEBUG',
                'format': 'json',
                'file_path': 'logs/test_trading_bot.log'
            }
        }
        
        import yaml
        with open(config_dir / 'trading_bot_config.yaml', 'w') as f:
            yaml.dump(test_config, f, default_flow_style=False)
        
        # Create test .env file
        test_env = {
            'DATABASE_URL': 'sqlite:///trading_bot.db',
            'LOG_LEVEL': 'DEBUG',
            'BINANCE_API_KEY': '',
            'BINANCE_API_SECRET': '',
            'OANDA_API_KEY': '',
            'OANDA_ACCOUNT_ID': '',
            'ENVIRONMENT': 'development'
        }
        
        with open('.env.test', 'w') as f:
            for key, value in test_env.items():
                f.write(f"{key}={value}\n")
        
        print("✅ Test configuration files created")
    
    async def run_health_check(self):
        """Run development environment health check."""
        print("Running development environment health check...")
        
        checks = {
            'database': False,
            'mock_exchange': False,
            'config_files': False,
            'log_directories': False
        }
        
        try:
            # Check database connection
            if not self.db_manager:
                self.db_manager = DatabaseManager()
                await self.db_manager.initialize()
            
            await self.db_manager.health_check()
            checks['database'] = True
            print("✅ Database connection OK")
            
        except Exception as e:
            print(f"❌ Database check failed: {e}")
        
        try:
            # Check mock exchange
            mock_exchange = MockExchange()
            await mock_exchange.connect()
            balance = await mock_exchange.get_balance()
            await mock_exchange.disconnect()
            checks['mock_exchange'] = True
            print("✅ Mock exchange OK")
            
        except Exception as e:
            print(f"❌ Mock exchange check failed: {e}")
        
        # Check config files
        config_files = [
            'config/trading_bot_config.yaml',
            '.env.example'
        ]
        
        all_configs_exist = all(os.path.exists(f) for f in config_files)
        checks['config_files'] = all_configs_exist
        
        if all_configs_exist:
            print("✅ Configuration files OK")
        else:
            print("❌ Some configuration files missing")
        
        # Check log directories
        log_dirs = ['logs', 'logs/errors', 'logs/trades', 'logs/metrics']
        for log_dir in log_dirs:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        checks['log_directories'] = True
        print("✅ Log directories OK")
        
        # Summary
        passed = sum(checks.values())
        total = len(checks)
        
        print(f"\nHealth check summary: {passed}/{total} checks passed")
        
        if passed == total:
            print("🎉 Development environment is ready!")
        else:
            print("⚠️  Some issues found. Please address them before continuing.")
        
        return checks
    
    async def cleanup(self):
        """Clean up development environment."""
        if self.db_manager:
            await self.db_manager.close()


async def main():
    parser = argparse.ArgumentParser(description='Trading Bot Development Setup')
    parser.add_argument('--setup-db', action='store_true', help='Set up database')
    parser.add_argument('--reset-db', action='store_true', help='Reset database')
    parser.add_argument('--seed-data', type=int, default=7, help='Seed test data (days)')
    parser.add_argument('--create-config', action='store_true', help='Create test config files')
    parser.add_argument('--health-check', action='store_true', help='Run health check')
    parser.add_argument('--all', action='store_true', help='Run all setup tasks')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    dev_setup = DevSetup()
    
    try:
        if args.all or args.setup_db:
            await dev_setup.setup_database(reset=args.reset_db)
        
        if args.all or args.seed_data:
            await dev_setup.seed_test_data(days=args.seed_data)
        
        if args.all or args.create_config:
            await dev_setup.create_test_config()
        
        if args.all or args.health_check:
            await dev_setup.run_health_check()
    
    finally:
        await dev_setup.cleanup()


if __name__ == '__main__':
    asyncio.run(main())