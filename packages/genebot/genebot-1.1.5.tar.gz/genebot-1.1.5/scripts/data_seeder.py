#!/usr/bin/env python3
"""
Data seeding script for development and testing.
"""
import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tests.utils.test_data_generators import (
    MarketDataGenerator, TradingScenarioGenerator, TestDataFactory
)


class DataSeeder:
    """Seed database with various types of test data."""
    
    def __init__(self):
        self.scenarios = {
            'bull_market': self._seed_bull_market,
            'bear_market': self._seed_bear_market,
            'volatile_market': self._seed_volatile_market,
            'sideways_market': self._seed_sideways_market,
            'multi_asset': self._seed_multi_asset,
            'comprehensive': self._seed_comprehensive
        }
    
    async def seed_scenario(self, scenario_name: str, **kwargs):
        """Seed a specific market scenario."""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        print(f"Seeding {scenario_name} scenario...")
        await self.scenarios[scenario_name](**kwargs)
        print(f"✅ {scenario_name} scenario seeded successfully")
    
    async def _seed_bull_market(self, days: int = 30, **kwargs):
        """Seed bull market scenario."""
        scenario = TestDataFactory.create_bull_market_scenario()
        
        # Extend with more data
        extended_data = MarketDataGenerator.generate_trending_data(
            symbol="BTC/USD",
            periods=days * 24,
            trend_strength=0.15,
            noise_level=0.02,
            initial_price=40000.0
        )
        
        print(f"Generated {len(extended_data)} bull market data points")
        await self._store_scenario_data(scenario, extended_data)
    
    async def _seed_bear_market(self, days: int = 30, **kwargs):
        """Seed bear market scenario."""
        scenario = TestDataFactory.create_bear_market_scenario()
        
        # Extend with more data
        extended_data = MarketDataGenerator.generate_trending_data(
            symbol="BTC/USD",
            periods=days * 24,
            trend_strength=-0.12,
            noise_level=0.03,
            initial_price=50000.0
        )
        
        print(f"Generated {len(extended_data)} bear market data points")
        await self._store_scenario_data(scenario, extended_data)
    
    async def _seed_volatile_market(self, days: int = 30, **kwargs):
        """Seed volatile market scenario."""
        scenario = TestDataFactory.create_volatile_market_scenario()
        
        # Generate high volatility data
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        volatile_data = MarketDataGenerator.generate_ohlcv_data(
            symbol="BTC/USD",
            start_date=start_date,
            end_date=end_date,
            interval_minutes=30,
            initial_price=45000.0,
            volatility=0.06,  # High volatility
            trend=0.0
        )
        
        print(f"Generated {len(volatile_data)} volatile market data points")
        await self._store_scenario_data(scenario, volatile_data)
    
    async def _seed_sideways_market(self, days: int = 30, **kwargs):
        """Seed sideways/ranging market scenario."""
        sideways_data = MarketDataGenerator.generate_sideways_data(
            symbol="BTC/USD",
            periods=days * 24,
            price_range=(42000.0, 48000.0),
            initial_price=45000.0
        )
        
        # Generate corresponding orders for ranging market
        orders = TradingScenarioGenerator.generate_orders(
            symbols=["BTC/USD"],
            count=days * 5  # More frequent trading in ranging market
        )
        
        scenario = {
            'market_data': sideways_data,
            'orders': orders,
            'scenario_type': 'sideways_market'
        }
        
        print(f"Generated {len(sideways_data)} sideways market data points")
        await self._store_scenario_data(scenario, sideways_data)
    
    async def _seed_multi_asset(self, days: int = 30, **kwargs):
        """Seed multi-asset scenario."""
        scenario = TestDataFactory.create_multi_asset_scenario()
        
        # Generate additional data for multiple assets
        symbols = ["BTC/USD", "ETH/USD", "BTC/ETH", "LTC/USD", "ADA/USD"]
        base_prices = {
            "BTC/USD": 45000.0,
            "ETH/USD": 3000.0,
            "BTC/ETH": 15.0,
            "LTC/USD": 150.0,
            "ADA/USD": 1.2
        }
        
        all_market_data = {}
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        for symbol in symbols:
            market_data = MarketDataGenerator.generate_ohlcv_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval_minutes=60,
                initial_price=base_prices[symbol],
                volatility=0.03,
                trend=0.01 if 'BTC' in symbol else -0.005  # BTC trending up, others down
            )
            all_market_data[symbol] = market_data
        
        # Generate cross-asset trading scenarios
        all_orders = TradingScenarioGenerator.generate_orders(symbols, days * 10)
        all_positions = TradingScenarioGenerator.generate_positions(symbols, 20)
        
        extended_scenario = {
            'market_data': all_market_data,
            'orders': all_orders,
            'positions': all_positions,
            'scenario_type': 'multi_asset_extended'
        }
        
        total_data_points = sum(len(data) for data in all_market_data.values())
        print(f"Generated {total_data_points} multi-asset data points across {len(symbols)} symbols")
        await self._store_scenario_data(extended_scenario)
    
    async def _seed_comprehensive(self, days: int = 90, **kwargs):
        """Seed comprehensive scenario with all market conditions."""
        print("Seeding comprehensive scenario with all market conditions...")
        
        # Divide time period into different market phases
        phase_days = days // 3
        
        # Phase 1: Bull market
        await self._seed_bull_market(days=phase_days)
        
        # Phase 2: Bear market
        await self._seed_bear_market(days=phase_days)
        
        # Phase 3: Sideways market
        await self._seed_sideways_market(days=phase_days)
        
        # Add some volatile periods
        await self._seed_volatile_market(days=7)
        
        # Add multi-asset data
        await self._seed_multi_asset(days=days)
        
        print("Comprehensive scenario includes all market conditions")
    
    async def _store_scenario_data(self, scenario: Dict[str, Any], 
                                  additional_data: List = None):
        """Store scenario data (mock implementation)."""
        # In a real implementation, this would store data in the database
        # For now, we'll just log what would be stored
        
        if 'market_data' in scenario:
            if isinstance(scenario['market_data'], dict):
                total_points = sum(len(data) for data in scenario['market_data'].values())
            else:
                total_points = len(scenario['market_data'])
            print(f"Would store {total_points} market data points")
        
        if 'orders' in scenario:
            print(f"Would store {len(scenario['orders'])} orders")
        
        if 'positions' in scenario:
            print(f"Would store {len(scenario['positions'])} positions")
        
        if 'signals' in scenario:
            print(f"Would store {len(scenario['signals'])} trading signals")
        
        if additional_data:
            print(f"Would store {len(additional_data)} additional data points")
    
    async def clear_test_data(self):
        """Clear all test data from database."""
        print("Clearing test data...")
        # In a real implementation, this would clear test data from database
        print("✅ Test data cleared")
    
    def list_scenarios(self):
        """List available seeding scenarios."""
        print("Available seeding scenarios:")
        for scenario in self.scenarios.keys():
            print(f"  - {scenario}")


async def main():
    parser = argparse.ArgumentParser(description='Trading Bot Data Seeder')
    parser.add_argument('scenario', nargs='?', help='Scenario to seed')
    parser.add_argument('--days', type=int, default=30, help='Number of days of data')
    parser.add_argument('--list', action='store_true', help='List available scenarios')
    parser.add_argument('--clear', action='store_true', help='Clear test data')
    
    args = parser.parse_args()
    
    seeder = DataSeeder()
    
    if args.list:
        seeder.list_scenarios()
        return
    
    if args.clear:
        await seeder.clear_test_data()
        return
    
    if not args.scenario:
        print("Please specify a scenario to seed or use --list to see available scenarios")
        seeder.list_scenarios()
        return
    
    try:
        await seeder.seed_scenario(args.scenario, days=args.days)
    except ValueError as e:
        print(f"Error: {e}")
        seeder.list_scenarios()
    except Exception as e:
        print(f"Seeding failed: {e}")


if __name__ == '__main__':
    asyncio.run(main())