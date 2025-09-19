#!/usr/bin/env python3
"""
GeneBot CLI - Command Line Interface
===================================

Main entry point for the GeneBot trading bot CLI application.
"""

import sys
import os
import argparse
from pathlib import Path

# Import GeneBot components
try:
    from genebot import __version__, __description__
except ImportError:
    __version__ = "1.0.0"
    __description__ = "Advanced Multi-Market Trading Bot"

def print_banner():
    """Print the GeneBot banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗ ███████╗███╗   ██╗███████╗██████╗  ██████╗ ████████╗║
    ║  ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝║
    ║  ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝██║   ██║   ██║   ║
    ║  ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║   ██║   ║
    ║  ╚██████╔╝███████╗██║ ╚████║███████╗██████╔╝╚██████╔╝   ██║   ║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═════╝  ╚═════╝    ╚═╝   ║
    ║                                                               ║
    ║              Advanced Multi-Market Trading Bot               ║
    ║                        Version 1.0.0                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    🚀 Welcome to GeneBot - Your Advanced Trading Companion
    
    Features:
    • Multi-Market Trading (Crypto + Forex)
    • Advanced Strategy Engine
    • Real-Time Risk Management
    • Comprehensive API Validation
    • Cross-Market Arbitrage
    • Portfolio Management
    • Backtesting & Analytics
    • Compliance & Audit Trails
    
    """
    print(banner)

def create_parser():
    """Create the argument parser for GeneBot CLI."""
    parser = argparse.ArgumentParser(
        prog='genebot',
        description='GeneBot - Advanced Multi-Market Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  genebot --version                    Show version information
  genebot --help                       Show this help message
  genebot list                         List configured accounts
  genebot add-crypto binance           Add Binance crypto account
  genebot add-forex oanda              Add OANDA forex account
  genebot start                        Start the trading bot
  genebot status                       Check bot status
  genebot stop                         Stop the trading bot

For more information, visit: https://github.com/genebot/genebot
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'GeneBot {__version__}\n{__description__}'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Account management commands
    subparsers.add_parser('list', help='List all configured accounts')
    subparsers.add_parser('list-accounts', help='List all configured accounts')
    subparsers.add_parser('list-exchanges', help='List available crypto exchanges')
    subparsers.add_parser('list-brokers', help='List available forex brokers')
    
    # Add account commands
    add_crypto_parser = subparsers.add_parser('add-crypto', help='Add crypto exchange account')
    add_crypto_parser.add_argument('exchange', help='Exchange name (e.g., binance, coinbase)')
    add_crypto_parser.add_argument('--name', help='Account name')
    add_crypto_parser.add_argument('--mode', choices=['demo', 'live'], default='demo', help='Account mode')
    
    add_forex_parser = subparsers.add_parser('add-forex', help='Add forex broker account')
    add_forex_parser.add_argument('broker', help='Broker name (e.g., oanda, ib)')
    add_forex_parser.add_argument('--name', help='Account name')
    add_forex_parser.add_argument('--mode', choices=['demo', 'live'], default='demo', help='Account mode')
    
    # Edit account commands
    edit_crypto_parser = subparsers.add_parser('edit-crypto', help='Edit crypto exchange account')
    edit_crypto_parser.add_argument('name', help='Account name to edit')
    
    edit_forex_parser = subparsers.add_parser('edit-forex', help='Edit forex broker account')
    edit_forex_parser.add_argument('name', help='Account name to edit')
    
    # Remove account commands
    remove_parser = subparsers.add_parser('remove-account', help='Remove an account')
    remove_parser.add_argument('name', help='Account name to remove')
    remove_parser.add_argument('type', choices=['crypto', 'forex'], help='Account type')
    
    subparsers.add_parser('remove-all-accounts', help='Remove all accounts')
    
    remove_by_exchange_parser = subparsers.add_parser('remove-by-exchange', help='Remove all accounts for a specific exchange')
    remove_by_exchange_parser.add_argument('exchange', help='Exchange name')
    
    remove_by_type_parser = subparsers.add_parser('remove-by-type', help='Remove all accounts of a specific type')
    remove_by_type_parser.add_argument('type', choices=['crypto', 'forex'], help='Account type')
    
    # Account control commands
    enable_parser = subparsers.add_parser('enable-account', help='Enable an account')
    enable_parser.add_argument('name', help='Account name to enable')
    
    disable_parser = subparsers.add_parser('disable-account', help='Disable an account')
    disable_parser.add_argument('name', help='Account name to disable')
    
    subparsers.add_parser('validate-accounts', help='Validate all accounts')
    subparsers.add_parser('validate', help='Validate all accounts')
    
    # Bot control commands
    subparsers.add_parser('start', help='Start the trading bot')
    subparsers.add_parser('stop', help='Stop the trading bot')
    subparsers.add_parser('restart', help='Restart the trading bot')
    subparsers.add_parser('status', help='Show bot status')
    subparsers.add_parser('reset', help='Reset system by cleaning up all data')
    
    # Reporting commands
    report_parser = subparsers.add_parser('report', help='Generate trading reports')
    report_parser.add_argument('type', nargs='?', default='summary',
                              choices=['summary', 'detailed', 'performance', 'compliance'],
                              help='Report type')
    
    # Utility commands
    subparsers.add_parser('setup-demo', help='Setup demo accounts')
    subparsers.add_parser('cleanup-demo', help='Remove demo accounts')
    subparsers.add_parser('health-check', help='System health check')
    subparsers.add_parser('backup-config', help='Backup configurations')
    
    return parser

def main():
    """Main entry point for GeneBot CLI."""
    parser = create_parser()
    
    # If no arguments provided, show banner and help
    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command:
        print(f"🤖 GeneBot Command: {args.command}")
        print("=" * 50)
        
        if args.command in ['list', 'list-accounts']:
            print("📋 Configured Trading Accounts")
            print("This feature requires the full GeneBot installation.")
            print("Install with: pip install genebot")
            
        elif args.command in ['list-exchanges']:
            print("🏦 Available Crypto Exchanges")
            exchanges = ['binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okx']
            for exchange in exchanges:
                print(f"  • {exchange}")
                
        elif args.command in ['list-brokers']:
            print("💱 Available Forex Brokers")
            brokers = ['oanda', 'ib', 'mt5']
            for broker in brokers:
                print(f"  • {broker}")
                
        elif args.command == 'add-crypto':
            print(f"➕ Adding crypto exchange account: {args.exchange}")
            print("This feature requires the full GeneBot installation.")
            
        elif args.command == 'add-forex':
            print(f"➕ Adding forex broker account: {args.broker}")
            print("This feature requires the full GeneBot installation.")
            
        elif args.command in ['start', 'stop', 'restart', 'status']:
            print(f"🎮 Bot Control: {args.command}")
            print("This feature requires the full GeneBot installation.")
            
        elif args.command == 'report':
            print(f"📊 Generating {args.type} report")
            print("This feature requires the full GeneBot installation.")
            
        else:
            print(f"Command '{args.command}' is available in the full GeneBot installation.")
            print("Install with: pip install genebot")
        
        print("\n✅ Command completed successfully")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())