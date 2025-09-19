#!/usr/bin/env python3
"""
Example script demonstrating Trading Bot CLI usage.

This script shows how to programmatically use the CLI functionality
or integrate it into other applications.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.trading_bot_cli import TradingBotCLI


def run_cli_command(command_args):
    """Run a CLI command and return the result."""
    try:
        # Run the CLI command
        result = subprocess.run([
            sys.executable, 
            str(project_root / "scripts" / "trading_bot_cli.py")
        ] + command_args, 
        capture_output=True, 
        text=True, 
        cwd=project_root
        )
        
        print(f"Command: {' '.join(command_args)}")
        print(f"Return code: {result.returncode}")
        print(f"Output:\\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\\n{result.stderr}")
        print("-" * 60)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def demonstrate_account_management():
    """Demonstrate account management features."""
    print("🏦 ACCOUNT MANAGEMENT DEMONSTRATION")
    print("=" * 60)
    
    # 1. Add a crypto exchange (sandbox mode)
    print("\\n1. Adding Binance testnet account...")
    success = run_cli_command([
        "add-crypto",
        "--name", "binance-demo",
        "--exchange-type", "binance",
        "--api-key", "demo_api_key_12345",
        "--api-secret", "demo_api_secret_67890",
        "--sandbox",
        "--enabled",
        "--force"
    ])
    
    if not success:
        print("❌ Failed to add crypto exchange")
        return False
    
    # 2. Add a forex broker (sandbox mode)
    print("\\n2. Adding OANDA demo account...")
    success = run_cli_command([
        "add-forex",
        "--name", "oanda-demo",
        "--broker-type", "oanda",
        "--api-key", "demo_oanda_api_key",
        "--account-id", "101-001-12345678-001",
        "--sandbox",
        "--enabled",
        "--force"
    ])
    
    if not success:
        print("❌ Failed to add forex broker")
        return False
    
    # 3. List all accounts
    print("\\n3. Listing all configured accounts...")
    run_cli_command(["list-accounts"])
    
    # 4. Validate accounts
    print("\\n4. Validating account configurations...")
    run_cli_command(["validate-accounts"])
    
    # 5. Disable an account
    print("\\n5. Disabling OANDA account...")
    run_cli_command(["disable-account", "oanda-demo", "forex"])
    
    # 6. List accounts again to show disabled status
    print("\\n6. Listing accounts after disabling OANDA...")
    run_cli_command(["list-accounts"])
    
    # 7. Re-enable the account
    print("\\n7. Re-enabling OANDA account...")
    run_cli_command(["enable-account", "oanda-demo", "forex"])
    
    return True


def demonstrate_reporting():
    """Demonstrate reporting features."""
    print("\\n\\n📊 REPORTING DEMONSTRATION")
    print("=" * 60)
    
    # 1. Generate summary report
    print("\\n1. Generating summary report...")
    run_cli_command([
        "report",
        "--type", "summary",
        "--start-date", "2024-01-01",
        "--end-date", "2024-01-31"
    ])
    
    # 2. Generate detailed report
    print("\\n2. Generating detailed report...")
    run_cli_command([
        "report",
        "--type", "detailed",
        "--start-date", "2024-01-01",
        "--end-date", "2024-01-31"
    ])
    
    # 3. Generate performance report
    print("\\n3. Generating performance report...")
    run_cli_command([
        "report",
        "--type", "performance",
        "--start-date", "2024-01-01",
        "--end-date", "2024-01-31"
    ])
    
    # 4. Generate compliance report with output file
    print("\\n4. Generating compliance report with file output...")
    output_file = project_root / "reports" / "demo_compliance_report.txt"
    output_file.parent.mkdir(exist_ok=True)
    
    run_cli_command([
        "report",
        "--type", "compliance",
        "--start-date", "2024-01-01",
        "--end-date", "2024-01-31",
        "--output", str(output_file)
    ])
    
    if output_file.exists():
        print(f"✅ Report saved to: {output_file}")
        print("Report contents:")
        with open(output_file, 'r') as f:
            print(f.read()[:500] + "..." if len(f.read()) > 500 else f.read())


def demonstrate_bot_control():
    """Demonstrate bot control features."""
    print("\\n\\n🤖 BOT CONTROL DEMONSTRATION")
    print("=" * 60)
    
    # 1. Check bot status
    print("\\n1. Checking bot status...")
    run_cli_command(["status"])
    
    # 2. Attempt to start bot (will validate accounts first)
    print("\\n2. Starting trading bot...")
    run_cli_command(["start"])
    
    # 3. Check status again
    print("\\n3. Checking bot status after start...")
    run_cli_command(["status"])
    
    # 4. Stop the bot
    print("\\n4. Stopping trading bot...")
    run_cli_command(["stop"])


def demonstrate_programmatic_usage():
    """Demonstrate programmatic usage of CLI classes."""
    print("\\n\\n🐍 PROGRAMMATIC USAGE DEMONSTRATION")
    print("=" * 60)
    
    # Create CLI instance
    cli = TradingBotCLI()
    
    # Load accounts programmatically
    accounts = cli._load_accounts()
    
    print("\\nProgrammatically loaded accounts:")
    print(f"Crypto exchanges: {len(accounts.get('crypto_exchanges', {}))}")
    print(f"Forex brokers: {len(accounts.get('forex_brokers', {}))}")
    
    # Display account details
    for name, config in accounts.get('crypto_exchanges', {}).items():
        print(f"  📈 {name}: {config.get('exchange_type')} ({'enabled' if config.get('enabled') else 'disabled'})")
    
    for name, config in accounts.get('forex_brokers', {}).items():
        print(f"  💱 {name}: {config.get('broker_type')} ({'enabled' if config.get('enabled') else 'disabled'})")


def cleanup_demo_accounts():
    """Clean up demo accounts created during demonstration."""
    print("\\n\\n🧹 CLEANUP")
    print("=" * 60)
    
    print("\\nRemoving demo accounts...")
    
    # Remove demo accounts
    run_cli_command(["remove-account", "binance-demo", "crypto"])
    run_cli_command(["remove-account", "oanda-demo", "forex"])
    
    print("\\nFinal account list:")
    run_cli_command(["list-accounts"])


def main():
    """Main demonstration function."""
    print("🚀 TRADING BOT CLI DEMONSTRATION")
    print("=" * 80)
    print("This script demonstrates the key features of the Trading Bot CLI.")
    print("All operations use demo/sandbox accounts with real API connections.")
    print("=" * 80)
    
    try:
        # Demonstrate account management
        if not demonstrate_account_management():
            print("❌ Account management demonstration failed")
            return 1
        
        # Demonstrate reporting
        demonstrate_reporting()
        
        # Demonstrate bot control
        demonstrate_bot_control()
        
        # Demonstrate programmatic usage
        demonstrate_programmatic_usage()
        
        # Cleanup
        cleanup_demo_accounts()
        
        print("\\n\\n✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("\\nNext steps:")
        print("1. Replace demo credentials with real API keys")
        print("2. Configure your trading strategies")
        print("3. Start with sandbox mode for testing")
        print("4. Use the CLI to manage your live trading accounts")
        
        return 0
        
    except KeyboardInterrupt:
        print("\\n\\n⚠️  Demonstration interrupted by user")
        return 1
    except Exception as e:
        print(f"\\n\\n❌ Demonstration failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())