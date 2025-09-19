#!/usr/bin/env python3
"""
Command-line interface for multi-market configuration management.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.multi_market_manager import MultiMarketConfigManager, get_multi_market_config_manager
from config.migration_tools import ConfigMigrationTool
from config.validation_utils import validate_config_file


def create_template_config(args):
    """Create a template configuration file."""
    template_path = Path("config/templates/multi_market_config_template.yaml")
    output_path = Path(args.output)
    
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}")
        return 1
    
    if output_path.exists() and not args.force:
        print(f"❌ Output file already exists: {output_path}")
        print("Use --force to overwrite")
        return 1
    
    try:
        # Copy template to output location
        import shutil
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_path, output_path)
        
        print(f"✅ Created configuration template: {output_path}")
        print("\nNext steps:")
        print("1. Edit the configuration file with your specific settings")
        print("2. Set up environment variables for sensitive credentials")
        print("3. Validate the configuration with: python scripts/config_manager_cli.py validate")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to create template: {e}")
        return 1


def validate_config(args):
    """Validate a configuration file."""
    config_file = Path(args.config_file)
    
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return 1
    
    print(f"Validating configuration: {config_file}")
    print(f"Environment: {args.environment}")
    print("-" * 50)
    
    result = validate_config_file(config_file, args.environment)
    
    if args.verbose or not result.is_valid:
        print(result.get_summary())
    else:
        if result.is_valid:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has errors")
            for error in result.errors:
                print(f"  ❌ {error}")
    
    return 0 if result.is_valid else 1


def migrate_config(args):
    """Migrate legacy configuration to multi-market format."""
    legacy_config = Path(args.legacy_config)
    output_config = Path(args.output)
    
    if not legacy_config.exists():
        print(f"❌ Legacy configuration file not found: {legacy_config}")
        return 1
    
    if output_config.exists() and not args.force:
        print(f"❌ Output file already exists: {output_config}")
        print("Use --force to overwrite")
        return 1
    
    try:
        migration_tool = ConfigMigrationTool()
        
        print(f"Migrating configuration from: {legacy_config}")
        print(f"Output file: {output_config}")
        
        # Load legacy config for report
        legacy_config_data = migration_tool.load_legacy_config(legacy_config)
        
        # Perform migration
        migrated_config = migration_tool.migrate_configuration(
            legacy_config,
            output_config,
            create_backup=not args.no_backup
        )
        
        # Create environment configs if requested
        if args.create_env_configs:
            migration_tool.create_environment_configs(migrated_config)
            print("✅ Created environment-specific configuration files")
        
        # Generate and display report
        report = migration_tool.generate_migration_report(legacy_config_data, migrated_config)
        print("\n" + report)
        
        print(f"\n✅ Migration completed successfully!")
        print(f"New configuration saved to: {output_config}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 1


def show_config_info(args):
    """Show information about the current configuration."""
    config_file = Path(args.config_file) if args.config_file else None
    
    try:
        config_manager = MultiMarketConfigManager(
            config_file=config_file,
            environment=args.environment
        )
        
        config = config_manager.get_config()
        
        print(f"Configuration Information")
        print("=" * 40)
        print(f"App Name: {config.app_name}")
        print(f"Version: {config.version}")
        print(f"Environment: {config.environment}")
        print(f"Debug Mode: {config.debug}")
        print(f"Dry Run: {config.dry_run}")
        print(f"Base Currency: {config.base_currency}")
        print()
        
        # Market information
        print("Market Configuration:")
        print(f"  Crypto Enabled: {config.crypto.enabled}")
        if config.crypto.enabled:
            enabled_exchanges = config_manager.get_enabled_crypto_exchanges()
            print(f"  Crypto Exchanges: {len(enabled_exchanges)} enabled")
            for name in enabled_exchanges:
                print(f"    - {name}")
        
        print(f"  Forex Enabled: {config.forex.enabled}")
        if config.forex.enabled:
            enabled_brokers = config_manager.get_enabled_forex_brokers()
            print(f"  Forex Brokers: {len(enabled_brokers)} enabled")
            for name in enabled_brokers:
                print(f"    - {name}")
            
            active_sessions = config_manager.get_active_forex_sessions()
            print(f"  Active Sessions: {len(active_sessions)}")
            for name in active_sessions:
                print(f"    - {name}")
        
        print()
        
        # Strategy information
        enabled_strategies = config_manager.get_enabled_strategies()
        print(f"Strategies: {len(enabled_strategies)} enabled")
        for name, strategy in enabled_strategies.items():
            print(f"  - {name} ({strategy.strategy_type})")
            print(f"    Symbols: {', '.join(strategy.symbols[:3])}{'...' if len(strategy.symbols) > 3 else ''}")
            print(f"    Timeframe: {strategy.timeframe}")
        
        print()
        
        # Risk information
        print("Risk Management:")
        print(f"  Max Position Size: {config.risk.max_position_size}")
        print(f"  Max Daily Loss: {config.risk.max_daily_loss}")
        print(f"  Stop Loss: {config.risk.stop_loss_percentage}")
        print(f"  Max Open Positions: {config.risk.max_open_positions}")
        print(f"  Cross-Market Max Exposure: {config.cross_market_risk.max_total_exposure}")
        
        print()
        
        # Compliance information
        print("Compliance:")
        print(f"  Enabled: {config.compliance.enabled}")
        print(f"  Generate Reports: {config.compliance.generate_reports}")
        print(f"  Report Frequency: {config.compliance.report_frequency}")
        print(f"  Audit Trail: {config.compliance.audit_trail_enabled}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return 1


def test_connections(args):
    """Test connections to exchanges and brokers."""
    config_file = Path(args.config_file) if args.config_file else None
    
    try:
        config_manager = MultiMarketConfigManager(
            config_file=config_file,
            environment=args.environment
        )
        
        config = config_manager.get_config()
        
        print("Testing Connections")
        print("=" * 40)
        
        # Test crypto exchanges
        if config.crypto.enabled:
            print("\nCrypto Exchanges:")
            enabled_exchanges = config_manager.get_enabled_crypto_exchanges()
            
            for name, exchange_config in enabled_exchanges.items():
                print(f"  Testing {name}...")
                
                # Basic credential check
                if not exchange_config.api_key or not exchange_config.api_secret:
                    print(f"    ❌ Missing credentials")
                    continue
                
                # Check for placeholder values
                placeholder_patterns = ['${', 'your_', 'test_', 'placeholder']
                has_placeholder = any(pattern in exchange_config.api_key.lower() or 
                                    pattern in exchange_config.api_secret.lower() 
                                    for pattern in placeholder_patterns)
                
                if has_placeholder:
                    print(f"    ⚠️  Appears to have placeholder credentials")
                else:
                    print(f"    ✅ Credentials configured")
                
                print(f"    Sandbox: {exchange_config.sandbox}")
        
        # Test forex brokers
        if config.forex.enabled:
            print("\nForex Brokers:")
            enabled_brokers = config_manager.get_enabled_forex_brokers()
            
            for name, broker_config in enabled_brokers.items():
                print(f"  Testing {name} ({broker_config.broker_type})...")
                
                try:
                    config_manager.validate_forex_broker_credentials(name)
                    print(f"    ✅ Credentials configured")
                except Exception as e:
                    print(f"    ❌ {e}")
                
                print(f"    Sandbox: {broker_config.sandbox}")
        
        print("\n✅ Connection test completed")
        print("Note: This only validates configuration, not actual connectivity")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to test connections: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Market Trading Bot Configuration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new configuration from template
  python scripts/config_manager_cli.py create-template -o config/my_config.yaml
  
  # Validate a configuration file
  python scripts/config_manager_cli.py validate config/my_config.yaml
  
  # Migrate legacy configuration
  python scripts/config_manager_cli.py migrate config/old_config.yaml -o config/new_config.yaml
  
  # Show configuration information
  python scripts/config_manager_cli.py info config/my_config.yaml
  
  # Test connections
  python scripts/config_manager_cli.py test-connections config/my_config.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create template command
    create_parser = subparsers.add_parser('create-template', help='Create configuration template')
    create_parser.add_argument('-o', '--output', default='config/multi_market_config.yaml',
                              help='Output configuration file')
    create_parser.add_argument('--force', action='store_true',
                              help='Overwrite existing file')
    create_parser.set_defaults(func=create_template_config)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.add_argument('config_file', help='Configuration file to validate')
    validate_parser.add_argument('-e', '--environment', default='development',
                                choices=['development', 'staging', 'production'],
                                help='Environment to validate for')
    validate_parser.add_argument('-v', '--verbose', action='store_true',
                                help='Show detailed validation results')
    validate_parser.set_defaults(func=validate_config)
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate legacy configuration')
    migrate_parser.add_argument('legacy_config', help='Legacy configuration file')
    migrate_parser.add_argument('-o', '--output', default='config/multi_market_config.yaml',
                               help='Output configuration file')
    migrate_parser.add_argument('--force', action='store_true',
                               help='Overwrite existing file')
    migrate_parser.add_argument('--no-backup', action='store_true',
                               help='Skip creating backup')
    migrate_parser.add_argument('--create-env-configs', action='store_true',
                               help='Create environment-specific configs')
    migrate_parser.set_defaults(func=migrate_config)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show configuration information')
    info_parser.add_argument('config_file', nargs='?', help='Configuration file')
    info_parser.add_argument('-e', '--environment', default='development',
                            choices=['development', 'staging', 'production'],
                            help='Environment')
    info_parser.set_defaults(func=show_config_info)
    
    # Test connections command
    test_parser = subparsers.add_parser('test-connections', help='Test exchange/broker connections')
    test_parser.add_argument('config_file', nargs='?', help='Configuration file')
    test_parser.add_argument('-e', '--environment', default='development',
                            choices=['development', 'staging', 'production'],
                            help='Environment')
    test_parser.set_defaults(func=test_connections)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    exit(main())