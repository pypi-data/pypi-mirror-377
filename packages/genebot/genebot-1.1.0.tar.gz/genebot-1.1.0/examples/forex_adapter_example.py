#!/usr/bin/env python3
"""
Example demonstrating forex broker adapter usage.

This example shows how to use the forex broker adapters to connect to
different forex brokers and retrieve market data.
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.exchanges.forex import MT5Adapter, OANDAAdapter, IBAdapter
from src.markets.types import UnifiedSymbol, MarketType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_mt5_adapter():
    """Demonstrate MT5 adapter usage."""
    print("\n=== MetaTrader 5 Adapter Demo ===")
    
    # Configuration for MT5 (demo values)
    mt5_config = {
        'login': '12345',
        'password': 'demo_password',
        'server': 'demo_server',
        'path': '/path/to/mt5'  # Optional
    }
    
    adapter = MT5Adapter('mt5_demo', mt5_config)
    
    try:
        # Test connection (will fail without actual MT5 installation)
        print(f"Adapter: {adapter}")
        print(f"Market Type: {adapter.market_type}")
        print(f"Validates credentials: {adapter.validate_credentials()}")
        
        # Create a forex symbol
        symbol = UnifiedSymbol.from_forex_symbol('EURUSD')
        print(f"Symbol: {symbol}")
        
        # Test utility methods
        costs = adapter.get_trading_costs(symbol)
        print(f"Trading costs: {costs}")
        
        min_size = adapter.get_minimum_trade_size(symbol)
        print(f"Minimum trade size: {min_size}")
        
        pip_value = adapter.get_pip_value(symbol, Decimal('1.0'))
        print(f"Pip value: {pip_value}")
        
    except Exception as e:
        print(f"MT5 Demo error (expected): {e}")


async def demo_oanda_adapter():
    """Demonstrate OANDA adapter usage."""
    print("\n=== OANDA Adapter Demo ===")
    
    # Configuration for OANDA (demo values)
    oanda_config = {
        'api_key': 'demo_api_key_1234567890abcdef',
        'account_id': '123-456-789',
        'environment': 'practice'  # or 'live'
    }
    
    adapter = OANDAAdapter('oanda_demo', oanda_config)
    
    try:
        print(f"Adapter: {adapter}")
        print(f"Market Type: {adapter.market_type}")
        print(f"Base URL: {adapter._base_url}")
        print(f"Validates credentials: {adapter.validate_credentials()}")
        
        # Create a forex symbol
        symbol = UnifiedSymbol.from_forex_symbol('GBPUSD')
        print(f"Symbol: {symbol}")
        
        # Test utility methods
        costs = adapter.get_trading_costs(symbol)
        print(f"Trading costs: {costs}")
        
        min_size = adapter.get_minimum_trade_size(symbol)
        print(f"Minimum trade size: {min_size}")
        
    except Exception as e:
        print(f"OANDA Demo error (expected): {e}")


async def demo_ib_adapter():
    """Demonstrate Interactive Brokers adapter usage."""
    print("\n=== Interactive Brokers Adapter Demo ===")
    
    # Configuration for IB (demo values)
    ib_config = {
        'host': '127.0.0.1',
        'port': 7497,  # Paper trading port
        'client_id': 1,
        'account': 'DU123456'  # Demo account
    }
    
    adapter = IBAdapter('ib_demo', ib_config)
    
    try:
        print(f"Adapter: {adapter}")
        print(f"Market Type: {adapter.market_type}")
        print(f"Host: {adapter.host}:{adapter.port}")
        print(f"Validates credentials: {adapter.validate_credentials()}")
        
        # Create a forex symbol
        symbol = UnifiedSymbol.from_forex_symbol('USDJPY')
        print(f"Symbol: {symbol}")
        
        # Test utility methods
        costs = adapter.get_trading_costs(symbol)
        print(f"Trading costs: {costs}")
        
        min_size = adapter.get_minimum_trade_size(symbol)
        print(f"Minimum trade size: {min_size}")
        
    except Exception as e:
        print(f"IB Demo error (expected): {e}")


async def demo_unified_symbol():
    """Demonstrate UnifiedSymbol usage for forex."""
    print("\n=== UnifiedSymbol Demo ===")
    
    # Create symbols from different formats
    symbols = [
        UnifiedSymbol.from_forex_symbol('EURUSD'),
        UnifiedSymbol.from_forex_symbol('GBPJPY'),
        UnifiedSymbol.from_forex_symbol('AUDUSD'),
        UnifiedSymbol.from_standard_format('USD/CHF', MarketType.FOREX, 'USDCHF')
    ]
    
    for symbol in symbols:
        print(f"Symbol: {symbol}")
        print(f"  Standard format: {symbol.to_standard_format()}")
        print(f"  Forex format: {symbol.to_forex_format()}")
        print(f"  Base: {symbol.base_asset}, Quote: {symbol.quote_asset}")
        print(f"  Market type: {symbol.market_type}")
        print(f"  Native: {symbol.native_symbol}")
        print()


async def demo_adapter_comparison():
    """Compare different adapter features."""
    print("\n=== Adapter Comparison ===")
    
    adapters = [
        MT5Adapter('mt5', {'login': '123', 'password': 'pass', 'server': 'server'}),
        OANDAAdapter('oanda', {'api_key': 'key123456789012345', 'account_id': '123-456'}),
        IBAdapter('ib', {'host': '127.0.0.1', 'port': 7497, 'client_id': 1})
    ]
    
    symbol = UnifiedSymbol.from_forex_symbol('EURUSD')
    
    print(f"{'Adapter':<15} {'Valid Creds':<12} {'Min Size':<12} {'Pip Value':<12}")
    print("-" * 60)
    
    for adapter in adapters:
        try:
            valid_creds = adapter.validate_credentials()
            min_size = adapter.get_minimum_trade_size(symbol)
            pip_value = adapter.get_pip_value(symbol)
            
            print(f"{adapter.name:<15} {valid_creds:<12} {min_size:<12} {pip_value:<12}")
        except Exception as e:
            print(f"{adapter.name:<15} Error: {str(e)[:40]}")


async def main():
    """Run all demos."""
    print("Forex Broker Adapter Examples")
    print("=" * 50)
    
    await demo_unified_symbol()
    await demo_mt5_adapter()
    await demo_oanda_adapter()
    await demo_ib_adapter()
    await demo_adapter_comparison()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("\nNote: These are demonstration examples with mock configurations.")
    print("To use with real brokers, you'll need:")
    print("- MT5: Valid login credentials and MT5 installation")
    print("- OANDA: Valid API key and account ID")
    print("- IB: Running TWS/Gateway and valid account")


if __name__ == '__main__':
    asyncio.run(main())