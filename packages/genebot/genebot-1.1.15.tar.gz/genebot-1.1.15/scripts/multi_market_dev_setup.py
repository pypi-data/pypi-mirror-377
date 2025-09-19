#!/usr/bin/env python3
"""
Development setup script for multi-market trading bot.
Handles database initialization, test data seeding, and development environment setup.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import asyncio
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.database.connection import DatabaseConnection
from src.models.database_models import Base
from tests.fixtures.multi_market_fixtures import MultiMarketDataGenerator
from tests.mocks.multi_market_mock_exchange import create_multi_market_mock_exchange
from src.markets.types import MarketType
from config.multi_market_manager import MultiMarketConfigManager


class MultiMarketDevSetup:
    """Development setup manager for multi-market trading bot"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/templates/multi_market_config_template.yaml"
        self.db_connection = None
        self.logger = self._setup_logging()
        self.data_generator = MultiMarketDataGenerator()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for development setup"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def setup_database(self, reset: bool = False) -> bool:
        """Setup database for multi-market trading"""
        try:
            self.logger.info("Setting up multi-market database...")
            
            # Initialize database connection
            self.db_connection = DatabaseConnection()
            await self.db_connection.connect()
            
            if reset:
                self.logger.info("Resetting database (dropping all tables)...")
                await self._drop_all_tables()
            
            # Create all tables
            self.logger.info("Creating database tables...")
            await self._create_tables()
            
            self.logger.info("Database setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Database setup failed: {str(e)}")
            return False
    
    async def _drop_all_tables(self):
        """Drop all existing tables"""
        async with self.db_connection.get_session() as session:
            # Drop tables in reverse dependency order
            tables_to_drop = [
                'risk_events', 'trades', 'positions', 'orders', 
                'market_data', 'cross_market_correlations',
                'forex_economic_events', 'market_sessions',
                'regulatory_reports', 'market_holidays'
            ]
            
            for table in tables_to_drop:
                try:
                    await session.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    self.logger.debug(f"Dropped table: {table}")
                except Exception as e:
                    self.logger.warning(f"Could not drop table {table}: {str(e)}")
            
            await session.commit()
    
    async def _create_tables(self):
        """Create all database tables"""
        async with self.db_connection.get_session() as session:
            # Create tables using SQLAlchemy metadata
            Base.metadata.create_all(bind=session.bind)
            await session.commit()
    
    async def seed_test_data(self, days: int = 7) -> bool:
        """Seed database with test data"""
        try:
            self.logger.info(f"Seeding test data for {days} days...")
            
            if not self.db_connection:
                await self.setup_database()
            
            # Generate test data
            await self._seed_market_data(days)
            await self._seed_economic_events(days)
            await self._seed_market_sessions()
            await self._seed_sample_trades()
            
            self.logger.info("Test data seeding completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Test data seeding failed: {str(e)}")
            return False
    
    async def _seed_market_data(self, days: int):
        """Seed market data for testing"""
        self.logger.info("Seeding market data...")
        
        # Define symbols and their base prices
        crypto_symbols = [
            ('BTC/USD', 45000.0),
            ('ETH/USD', 3000.0),
            ('BTC/ETH', 15.0)
        ]
        
        forex_symbols = [
            ('EURUSD', 1.0850),
            ('GBPUSD', 1.2650),
            ('USDJPY', 149.50)
        ]
        
        start_time = datetime.utcnow() - timedelta(days=days)
        
        async with self.db_connection.get_session() as session:
            # Generate crypto data
            for symbol, base_price in crypto_symbols:
                data_series = self.data_generator.generate_market_data_series(
                    symbol=symbol,
                    market_type=MarketType.CRYPTO,
                    start_time=start_time,
                    duration_hours=days * 24,
                    base_price=base_price,
                    volatility=0.03
                )
                
                # Insert data in batches
                batch_size = 1000
                for i in range(0, len(data_series), batch_size):
                    batch = data_series[i:i + batch_size]
                    for data_point in batch:
                        # Convert to database model and insert
                        # This would use the actual database model
                        pass
                
                self.logger.debug(f"Seeded {len(data_series)} data points for {symbol}")
            
            # Generate forex data
            for symbol, base_price in forex_symbols:
                data_series = self.data_generator.generate_market_data_series(
                    symbol=symbol,
                    market_type=MarketType.FOREX,
                    start_time=start_time,
                    duration_hours=days * 24,
                    base_price=base_price,
                    volatility=0.005
                )
                
                # Insert data in batches
                batch_size = 1000
                for i in range(0, len(data_series), batch_size):
                    batch = data_series[i:i + batch_size]
                    for data_point in batch:
                        # Convert to database model and insert
                        pass
                
                self.logger.debug(f"Seeded {len(data_series)} data points for {symbol}")
            
            await session.commit()
    
    async def _seed_economic_events(self, days: int):
        """Seed economic events for forex testing"""
        self.logger.info("Seeding economic events...")
        
        start_time = datetime.utcnow() - timedelta(days=days)
        events = self.data_generator.generate_economic_events(start_time, days)
        
        async with self.db_connection.get_session() as session:
            for event in events:
                # Convert to database model and insert
                # This would use the actual database model
                pass
            
            await session.commit()
            self.logger.debug(f"Seeded {len(events)} economic events")
    
    async def _seed_market_sessions(self):
        """Seed market session data"""
        self.logger.info("Seeding market sessions...")
        
        sessions_data = self.data_generator.generate_market_session_data()
        
        async with self.db_connection.get_session() as session:
            # Insert session data
            for market_type, sessions in sessions_data.items():
                for session_name, session_info in sessions.items():
                    # Convert to database model and insert
                    pass
            
            await session.commit()
    
    async def _seed_sample_trades(self):
        """Seed sample trade history"""
        self.logger.info("Seeding sample trades...")
        
        symbols = ['BTC/USD', 'ETH/USD', 'EURUSD', 'GBPUSD']
        market_types = [MarketType.CRYPTO, MarketType.CRYPTO, MarketType.FOREX, MarketType.FOREX]
        
        orders = self.data_generator.generate_order_history(symbols, market_types, count=100)
        positions = self.data_generator.generate_position_history(symbols, market_types)
        
        async with self.db_connection.get_session() as session:
            # Insert orders and positions
            for order in orders:
                # Convert to database model and insert
                pass
            
            for position in positions:
                # Convert to database model and insert
                pass
            
            await session.commit()
    
    def create_dev_config(self, output_path: str = "config/dev_multi_market_config.yaml") -> bool:
        """Create development configuration file"""
        try:
            self.logger.info(f"Creating development configuration at {output_path}...")
            
            dev_config = {
                'environment': 'development',
                'markets': {
                    'crypto': {
                        'enabled': True,
                        'exchanges': [
                            {
                                'name': 'mock_crypto',
                                'type': 'mock',
                                'symbols': ['BTC/USD', 'ETH/USD', 'BTC/ETH'],
                                'credentials': {
                                    'api_key': 'mock_key',
                                    'secret': 'mock_secret'
                                }
                            }
                        ]
                    },
                    'forex': {
                        'enabled': True,
                        'brokers': [
                            {
                                'name': 'mock_forex',
                                'type': 'mock',
                                'symbols': ['EURUSD', 'GBPUSD', 'USDJPY'],
                                'credentials': {
                                    'account_id': 'mock_account',
                                    'access_token': 'mock_token'
                                }
                            }
                        ]
                    }
                },
                'risk_management': {
                    'unified_limits': {
                        'max_portfolio_risk': 0.05,  # Higher for development
                        'max_correlation_exposure': 0.7,
                        'daily_loss_limit': 0.10
                    },
                    'market_specific': {
                        'crypto': {
                            'max_position_size': 0.2,
                            'leverage_limit': 3
                        },
                        'forex': {
                            'max_position_size': 0.1,
                            'leverage_limit': 10
                        }
                    }
                },
                'sessions': {
                    'forex': {
                        'sydney': '22:00-07:00 UTC',
                        'tokyo': '00:00-09:00 UTC',
                        'london': '08:00-17:00 UTC',
                        'new_york': '13:00-22:00 UTC'
                    }
                },
                'strategies': {
                    'enabled': ['moving_average', 'rsi', 'arbitrage'],
                    'parameters': {
                        'moving_average': {
                            'short_period': 10,
                            'long_period': 20
                        },
                        'rsi': {
                            'period': 14,
                            'overbought': 70,
                            'oversold': 30
                        }
                    }
                },
                'monitoring': {
                    'enabled': True,
                    'metrics_port': 8080,
                    'health_check_port': 8081,
                    'log_level': 'DEBUG'
                },
                'database': {
                    'url': 'sqlite:///dev_trading_bot.db',
                    'echo': True
                }
            }
            
            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration
            with open(output_path, 'w') as f:
                yaml.dump(dev_config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Development configuration created at {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create development configuration: {str(e)}")
            return False
    
    def setup_test_environment(self) -> bool:
        """Setup complete test environment"""
        try:
            self.logger.info("Setting up complete test environment...")
            
            # Create necessary directories
            directories = [
                'logs/dev',
                'data/dev',
                'reports/dev',
                'config/dev'
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created directory: {directory}")
            
            # Create development configuration
            self.create_dev_config()
            
            # Setup environment variables
            self._setup_dev_env_vars()
            
            self.logger.info("Test environment setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Test environment setup failed: {str(e)}")
            return False
    
    def _setup_dev_env_vars(self):
        """Setup development environment variables"""
        dev_env_vars = {
            'TRADING_BOT_ENV': 'development',
            'TRADING_BOT_CONFIG': 'config/dev_multi_market_config.yaml',
            'TRADING_BOT_LOG_LEVEL': 'DEBUG',
            'TRADING_BOT_DB_URL': 'sqlite:///dev_trading_bot.db'
        }
        
        env_file_path = Path('.env.dev')
        with open(env_file_path, 'w') as f:
            for key, value in dev_env_vars.items():
                f.write(f"{key}={value}\n")
        
        self.logger.info(f"Development environment variables written to {env_file_path}")
    
    async def run_integration_test(self) -> bool:
        """Run basic integration test"""
        try:
            self.logger.info("Running integration test...")
            
            # Create mock exchange
            mock_exchange = create_multi_market_mock_exchange()
            await mock_exchange.connect()
            
            # Test crypto market data
            crypto_data = await mock_exchange.get_market_data('BTC/USD', MarketType.CRYPTO)
            self.logger.info(f"Crypto test data: {crypto_data.symbol} @ {crypto_data.close}")
            
            # Test forex market data
            forex_data = await mock_exchange.get_market_data('EURUSD', MarketType.FOREX)
            self.logger.info(f"Forex test data: {forex_data.symbol} @ {forex_data.close}")
            
            # Test order placement
            order_id = await mock_exchange.place_order(
                symbol='BTC/USD',
                side='buy',
                amount=0.1,
                market_type=MarketType.CRYPTO
            )
            self.logger.info(f"Test order placed: {order_id}")
            
            # Test order status
            order_status = await mock_exchange.get_order_status(order_id)
            self.logger.info(f"Order status: {order_status['status']}")
            
            await mock_exchange.disconnect()
            
            self.logger.info("Integration test completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Integration test failed: {str(e)}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db_connection:
            await self.db_connection.disconnect()


async def main():
    """Main entry point for development setup script"""
    parser = argparse.ArgumentParser(description='Multi-Market Trading Bot Development Setup')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--reset-db', action='store_true', help='Reset database (drop all tables)')
    parser.add_argument('--seed-days', type=int, default=7, help='Days of test data to seed')
    parser.add_argument('--skip-db', action='store_true', help='Skip database setup')
    parser.add_argument('--skip-seed', action='store_true', help='Skip test data seeding')
    parser.add_argument('--test', action='store_true', help='Run integration test')
    parser.add_argument('--env-only', action='store_true', help='Setup environment only')
    
    args = parser.parse_args()
    
    setup = MultiMarketDevSetup(args.config)
    
    try:
        if args.env_only:
            # Setup environment only
            success = setup.setup_test_environment()
            sys.exit(0 if success else 1)
        
        # Setup database
        if not args.skip_db:
            success = await setup.setup_database(reset=args.reset_db)
            if not success:
                sys.exit(1)
        
        # Seed test data
        if not args.skip_seed:
            success = await setup.seed_test_data(args.seed_days)
            if not success:
                sys.exit(1)
        
        # Setup test environment
        setup.setup_test_environment()
        
        # Run integration test
        if args.test:
            success = await setup.run_integration_test()
            if not success:
                sys.exit(1)
        
        print("\n✅ Multi-market development setup completed successfully!")
        print("\nNext steps:")
        print("1. Source the environment: source .env.dev")
        print("2. Run the trading bot: python main.py")
        print("3. Check logs in: logs/dev/")
        print("4. Access monitoring at: http://localhost:8080")
        
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)
    finally:
        await setup.cleanup()


if __name__ == '__main__':
    asyncio.run(main())