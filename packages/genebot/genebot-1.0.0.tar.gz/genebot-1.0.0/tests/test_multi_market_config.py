"""
Unit tests for multi-market configuration management.
"""
import os
import yaml
import pytest
import tempfile
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch, mock_open

from config.multi_market_models import (
    MultiMarketTradingBotConfig,
    CryptoMarketConfig,
    ForexMarketConfig,
    ForexBrokerConfig,
    MarketSessionConfig,
    HolidayConfig,
    CrossMarketRiskConfig,
    ComplianceConfig,
    EnvironmentSpecificConfig,
    MarketType,
    ForexBrokerType,
    SessionName
)
from config.multi_market_manager import (
    MultiMarketConfigManager,
    MultiMarketConfigurationError
)
from config.migration_tools import ConfigMigrationTool, ConfigMigrationError
from config.models import ExchangeConfig, StrategyConfig, RiskConfig


class TestMultiMarketModels:
    """Test multi-market configuration models."""
    
    def test_forex_broker_config_mt5(self):
        """Test MT5 forex broker configuration validation."""
        # Valid MT5 config
        config = ForexBrokerConfig(
            name="mt5_broker",
            broker_type=ForexBrokerType.MT5,
            server="MetaQuotes-Demo",
            login=12345,
            password="password123",
            sandbox=True
        )
        assert config.broker_type == ForexBrokerType.MT5
        assert config.server == "MetaQuotes-Demo"
        assert config.login == 12345
        
        # Invalid MT5 config (missing required fields)
        with pytest.raises(ValueError, match="MT5 broker requires"):
            ForexBrokerConfig(
                name="mt5_broker",
                broker_type=ForexBrokerType.MT5,
                server="MetaQuotes-Demo",
                # Missing login and password
                sandbox=True
            )
    
    def test_forex_broker_config_oanda(self):
        """Test OANDA forex broker configuration validation."""
        # Valid OANDA config
        config = ForexBrokerConfig(
            name="oanda_broker",
            broker_type=ForexBrokerType.OANDA,
            api_key="test_api_key",
            account_id="101-001-12345",
            sandbox=True
        )
        assert config.broker_type == ForexBrokerType.OANDA
        assert config.api_key == "test_api_key"
        assert config.account_id == "101-001-12345"
        
        # Invalid OANDA config (missing required fields)
        with pytest.raises(ValueError, match="OANDA broker requires"):
            ForexBrokerConfig(
                name="oanda_broker",
                broker_type=ForexBrokerType.OANDA,
                api_key="test_api_key",
                # Missing account_id
                sandbox=True
            )
    
    def test_forex_broker_config_ib(self):
        """Test Interactive Brokers configuration validation."""
        # Valid IB config
        config = ForexBrokerConfig(
            name="ib_broker",
            broker_type=ForexBrokerType.INTERACTIVE_BROKERS,
            host="127.0.0.1",
            port=7497,
            client_id=1,
            sandbox=True
        )
        assert config.broker_type == ForexBrokerType.INTERACTIVE_BROKERS
        assert config.host == "127.0.0.1"
        assert config.port == 7497
        assert config.client_id == 1
        
        # Invalid IB config (missing required fields)
        with pytest.raises(ValueError, match="IB broker requires"):
            ForexBrokerConfig(
                name="ib_broker",
                broker_type=ForexBrokerType.INTERACTIVE_BROKERS,
                host="",  # Empty host should fail validation
                sandbox=True
            )
    
    def test_market_session_config(self):
        """Test market session configuration validation."""
        # Valid session config
        config = MarketSessionConfig(
            name=SessionName.LONDON,
            start_time="08:00",
            end_time="17:00",
            timezone="UTC",
            enabled=True
        )
        assert config.name == SessionName.LONDON
        assert config.start_time == "08:00"
        assert config.end_time == "17:00"
        
        # Invalid time format
        with pytest.raises(ValueError, match="Time must be in HH:MM format"):
            MarketSessionConfig(
                name=SessionName.LONDON,
                start_time="8:00",  # Invalid format
                end_time="17:00",
                timezone="UTC"
            )
    
    def test_holiday_config(self):
        """Test holiday configuration validation."""
        # Valid holiday config
        config = HolidayConfig(
            name="New Year's Day",
            date="2024-01-01",
            markets=[MarketType.FOREX]
        )
        assert config.name == "New Year's Day"
        assert config.date == "2024-01-01"
        assert config.markets == [MarketType.FOREX]
        
        # Invalid date format
        with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
            HolidayConfig(
                name="Invalid Date",
                date="01/01/2024",  # Invalid format
                markets=[MarketType.FOREX]
            )
    
    def test_crypto_market_config(self):
        """Test crypto market configuration validation."""
        exchange_config = ExchangeConfig(
            name="binance",
            exchange_type="binance",
            api_key="test_key",
            api_secret="test_secret"
        )
        
        config = CryptoMarketConfig(
            enabled=True,
            exchanges={"binance": exchange_config},
            default_quote_currency="USDT",
            min_trade_amount=Decimal("10")
        )
        
        assert config.enabled is True
        assert config.default_quote_currency == "USDT"
        assert config.min_trade_amount == Decimal("10")
        assert "binance" in config.exchanges
        
        # Invalid quote currency
        with pytest.raises(ValueError, match="Quote currency must be one of"):
            CryptoMarketConfig(
                default_quote_currency="INVALID"
            )
    
    def test_forex_market_config(self):
        """Test forex market configuration validation."""
        broker_config = ForexBrokerConfig(
            name="oanda",
            broker_type=ForexBrokerType.OANDA,
            api_key="test_key",
            account_id="test_account"
        )
        
        session_config = MarketSessionConfig(
            name=SessionName.LONDON,
            start_time="08:00",
            end_time="17:00"
        )
        
        config = ForexMarketConfig(
            enabled=True,
            brokers={"oanda": broker_config},
            sessions={"london": session_config},
            default_lot_size=Decimal("0.01"),
            max_spread_pips=5
        )
        
        assert config.enabled is True
        assert config.default_lot_size == Decimal("0.01")
        assert config.max_spread_pips == 5
        assert "oanda" in config.brokers
        assert "london" in config.sessions
    
    def test_cross_market_risk_config(self):
        """Test cross-market risk configuration validation."""
        config = CrossMarketRiskConfig(
            max_total_exposure=Decimal("0.8"),
            max_correlation_exposure=Decimal("0.5"),
            correlation_threshold=Decimal("0.7"),
            crypto_max_allocation=Decimal("0.6"),
            forex_max_allocation=Decimal("0.4"),
            max_cross_market_positions=10,
            max_positions_per_market=5
        )
        
        assert config.max_total_exposure == Decimal("0.8")
        assert config.crypto_max_allocation == Decimal("0.6")
        assert config.forex_max_allocation == Decimal("0.4")
        
        # Invalid percentage values
        with pytest.raises(ValueError, match="Percentage values must be between 0 and 1"):
            CrossMarketRiskConfig(
                max_total_exposure=Decimal("1.5")  # Invalid
            )
    
    def test_compliance_config(self):
        """Test compliance configuration validation."""
        config = ComplianceConfig(
            enabled=True,
            generate_reports=True,
            report_frequency="daily",
            audit_retention_days=2555,
            position_reporting_threshold=Decimal("10000")
        )
        
        assert config.enabled is True
        assert config.report_frequency == "daily"
        assert config.audit_retention_days == 2555
        
        # Invalid report frequency
        with pytest.raises(ValueError, match="Report frequency must be one of"):
            ComplianceConfig(
                report_frequency="invalid"
            )
    
    def test_multi_market_trading_bot_config(self):
        """Test main multi-market configuration validation."""
        # Create crypto config with an exchange
        exchange_config = ExchangeConfig(
            name="binance",
            exchange_type="binance",
            api_key="test_key",
            api_secret="test_secret"
        )
        crypto_config = CryptoMarketConfig(
            enabled=True,
            exchanges={"binance": exchange_config}
        )
        forex_config = ForexMarketConfig(enabled=False)
        
        # Create cross-market risk config with valid allocations
        cross_market_risk = CrossMarketRiskConfig(
            crypto_max_allocation=Decimal("0.5"),
            forex_max_allocation=Decimal("0.5")
        )
        
        config = MultiMarketTradingBotConfig(
            app_name="TestBot",
            version="2.0.0",
            crypto=crypto_config,
            forex=forex_config,
            cross_market_risk=cross_market_risk,
            environment="development"
        )
        
        assert config.app_name == "TestBot"
        assert config.version == "2.0.0"
        assert config.environment == "development"
        assert config.crypto.enabled is True
        assert config.forex.enabled is False
        
        # Invalid environment
        with pytest.raises(ValueError, match="Environment must be one of"):
            MultiMarketTradingBotConfig(
                crypto=crypto_config,
                forex=forex_config,
                environment="invalid"
            )
        
        # Both markets disabled
        with pytest.raises(ValueError, match="At least one market type must be enabled"):
            MultiMarketTradingBotConfig(
                crypto=CryptoMarketConfig(enabled=False),
                forex=ForexMarketConfig(enabled=False),
                cross_market_risk=CrossMarketRiskConfig(
                    crypto_max_allocation=Decimal("0.5"),
                    forex_max_allocation=Decimal("0.5")
                )
            )


class TestMultiMarketConfigManager:
    """Test multi-market configuration manager."""
    
    def test_init(self):
        """Test configuration manager initialization."""
        manager = MultiMarketConfigManager(
            config_file="test_config.yaml",
            environment="development"
        )
        
        assert manager.config_file == Path("test_config.yaml")
        assert manager.environment == "development"
        assert manager._config is None
    
    @patch.dict(os.environ, {
        'CRYPTO_ENABLED': 'true',
        'FOREX_ENABLED': 'false',
        'DEBUG': 'true'
    })
    def test_get_env_value(self):
        """Test environment variable retrieval and conversion."""
        manager = MultiMarketConfigManager()
        
        # Boolean conversion
        assert manager._get_env_value('CRYPTO_ENABLED') is True
        assert manager._get_env_value('FOREX_ENABLED') is False
        assert manager._get_env_value('DEBUG') is True
        
        # Default value
        assert manager._get_env_value('NONEXISTENT', 'default') == 'default'
        
        # String value
        os.environ['TEST_STRING'] = 'test_value'
        assert manager._get_env_value('TEST_STRING') == 'test_value'
    
    def test_load_yaml_config_file_not_found(self):
        """Test loading YAML config when file doesn't exist."""
        manager = MultiMarketConfigManager(config_file="nonexistent.yaml")
        config = manager._load_yaml_config()
        assert config == {}
    
    def test_load_yaml_config_invalid_yaml(self):
        """Test loading invalid YAML configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            manager = MultiMarketConfigManager(config_file=f.name)
            
            with pytest.raises(MultiMarketConfigurationError, match="Failed to parse YAML"):
                manager._load_yaml_config()
            
            os.unlink(f.name)
    
    def test_build_crypto_market_config(self):
        """Test building crypto market configuration."""
        manager = MultiMarketConfigManager()
        
        yaml_config = {
            'crypto': {
                'enabled': True,
                'default_quote_currency': 'USDT',
                'exchanges': {
                    'binance': {
                        'exchange_type': 'binance',
                        'api_key': 'test_key',
                        'api_secret': 'test_secret',
                        'enabled': True
                    }
                }
            }
        }
        
        crypto_config = manager._build_crypto_market_config(yaml_config)
        
        assert crypto_config.enabled is True
        assert crypto_config.default_quote_currency == 'USDT'
        assert 'binance' in crypto_config.exchanges
        assert crypto_config.exchanges['binance'].api_key == 'test_key'
    
    def test_build_forex_market_config(self):
        """Test building forex market configuration."""
        manager = MultiMarketConfigManager()
        
        yaml_config = {
            'forex': {
                'enabled': True,
                'brokers': {
                    'oanda': {
                        'broker_type': 'oanda',
                        'api_key': 'test_key',
                        'account_id': 'test_account',
                        'enabled': True
                    }
                }
            }
        }
        
        forex_config = manager._build_forex_market_config(yaml_config)
        
        assert forex_config.enabled is True
        assert 'oanda' in forex_config.brokers
        assert forex_config.brokers['oanda'].api_key == 'test_key'
        
        # Should have default sessions
        assert len(forex_config.sessions) == 4
        assert 'sydney' in forex_config.sessions
        assert 'london' in forex_config.sessions
    
    def test_validate_forex_broker_credentials(self):
        """Test forex broker credential validation."""
        manager = MultiMarketConfigManager()
        
        # Create a config with valid OANDA broker
        forex_config = ForexMarketConfig(
            enabled=True,
            brokers={
                'oanda': ForexBrokerConfig(
                    name='oanda',
                    broker_type=ForexBrokerType.OANDA,
                    api_key='test_key',
                    account_id='test_account'
                )
            }
        )
        
        # Create crypto config with exchange
        exchange_config = ExchangeConfig(
            name="binance",
            exchange_type="binance", 
            api_key="test_key",
            api_secret="test_secret"
        )
        crypto_config = CryptoMarketConfig(
            enabled=True,
            exchanges={"binance": exchange_config}
        )
        
        config = MultiMarketTradingBotConfig(
            crypto=crypto_config,
            forex=forex_config,
            cross_market_risk=CrossMarketRiskConfig(
                crypto_max_allocation=Decimal("0.5"),
                forex_max_allocation=Decimal("0.5")
            )
        )
        
        manager._config = config
        
        # Valid credentials
        assert manager.validate_forex_broker_credentials('oanda') is True
        
        # Broker not found
        with pytest.raises(MultiMarketConfigurationError, match="Broker 'nonexistent' not found"):
            manager.validate_forex_broker_credentials('nonexistent')
    
    def test_get_enabled_crypto_exchanges(self):
        """Test getting enabled crypto exchanges."""
        manager = MultiMarketConfigManager()
        
        exchange_config = ExchangeConfig(
            name="binance",
            exchange_type="binance",
            api_key="test_key",
            api_secret="test_secret",
            enabled=True
        )
        
        crypto_config = CryptoMarketConfig(
            enabled=True,
            exchanges={"binance": exchange_config}
        )
        
        config = MultiMarketTradingBotConfig(
            crypto=crypto_config,
            forex=ForexMarketConfig(enabled=False),
            cross_market_risk=CrossMarketRiskConfig(
                crypto_max_allocation=Decimal("0.5"),
                forex_max_allocation=Decimal("0.5")
            )
        )
        
        manager._config = config
        
        enabled_exchanges = manager.get_enabled_crypto_exchanges()
        assert len(enabled_exchanges) == 1
        assert "binance" in enabled_exchanges
        
        # Test when crypto is disabled
        config.crypto.enabled = False
        enabled_exchanges = manager.get_enabled_crypto_exchanges()
        assert len(enabled_exchanges) == 0
    
    def test_get_enabled_forex_brokers(self):
        """Test getting enabled forex brokers."""
        manager = MultiMarketConfigManager()
        
        broker_config = ForexBrokerConfig(
            name="oanda",
            broker_type=ForexBrokerType.OANDA,
            api_key="test_key",
            account_id="test_account",
            enabled=True
        )
        
        forex_config = ForexMarketConfig(
            enabled=True,
            brokers={"oanda": broker_config}
        )
        
        # Create crypto config with exchange
        exchange_config = ExchangeConfig(
            name="binance",
            exchange_type="binance", 
            api_key="test_key",
            api_secret="test_secret"
        )
        crypto_config = CryptoMarketConfig(
            enabled=True,
            exchanges={"binance": exchange_config}
        )
        
        config = MultiMarketTradingBotConfig(
            crypto=crypto_config,
            forex=forex_config,
            cross_market_risk=CrossMarketRiskConfig(
                crypto_max_allocation=Decimal("0.5"),
                forex_max_allocation=Decimal("0.5")
            )
        )
        
        manager._config = config
        
        enabled_brokers = manager.get_enabled_forex_brokers()
        assert len(enabled_brokers) == 1
        assert "oanda" in enabled_brokers
        
        # Test when forex is disabled
        config.forex.enabled = False
        enabled_brokers = manager.get_enabled_forex_brokers()
        assert len(enabled_brokers) == 0


class TestConfigMigrationTool:
    """Test configuration migration tools."""
    
    def test_init(self):
        """Test migration tool initialization."""
        tool = ConfigMigrationTool()
        assert tool.backup_dir == Path("config/backups")
        
        custom_backup_dir = Path("custom/backup")
        tool = ConfigMigrationTool(backup_dir=custom_backup_dir)
        assert tool.backup_dir == custom_backup_dir
    
    def test_create_backup(self):
        """Test creating configuration backup."""
        tool = ConfigMigrationTool()
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("test: config")
            f.flush()
            
            config_file = Path(f.name)
            
            # Create backup
            backup_path = tool.create_backup(config_file)
            
            assert backup_path.exists()
            assert backup_path.parent == tool.backup_dir
            assert "backup" in backup_path.name
            
            # Cleanup
            os.unlink(f.name)
            if backup_path.exists():
                os.unlink(backup_path)
        
        # Test file not found
        with pytest.raises(ConfigMigrationError, match="Configuration file not found"):
            tool.create_backup(Path("nonexistent.yaml"))
    
    def test_load_legacy_config(self):
        """Test loading legacy configuration."""
        tool = ConfigMigrationTool()
        
        legacy_config = {
            'app_name': 'LegacyBot',
            'exchanges': {
                'binance': {
                    'api_key': 'test_key',
                    'api_secret': 'test_secret'
                }
            }
        }
        
        # Create temporary legacy config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(legacy_config, f)
            f.flush()
            
            config_file = Path(f.name)
            loaded_config = tool.load_legacy_config(config_file)
            
            assert loaded_config['app_name'] == 'LegacyBot'
            assert 'binance' in loaded_config['exchanges']
            
            # Cleanup
            os.unlink(f.name)
    
    def test_migrate_exchanges_to_crypto_market(self):
        """Test migrating exchanges to crypto market configuration."""
        tool = ConfigMigrationTool()
        
        legacy_exchanges = {
            'binance': {
                'api_key': 'test_key',
                'api_secret': 'test_secret',
                'enabled': True
            },
            'coinbase': {
                'api_key': 'cb_key',
                'api_secret': 'cb_secret',
                'api_passphrase': 'cb_pass',
                'enabled': False
            }
        }
        
        crypto_config = tool.migrate_exchanges_to_crypto_market(legacy_exchanges)
        
        assert crypto_config.enabled is True
        assert len(crypto_config.exchanges) == 2
        assert 'binance' in crypto_config.exchanges
        assert 'coinbase' in crypto_config.exchanges
        assert crypto_config.exchanges['binance'].api_key == 'test_key'
        assert crypto_config.exchanges['coinbase'].enabled is False
    
    def test_migrate_risk_config(self):
        """Test migrating risk configuration."""
        tool = ConfigMigrationTool()
        
        legacy_risk = {
            'max_position_size': 0.1,
            'max_daily_loss': 0.05,
            'stop_loss_percentage': 0.02,
            'max_open_positions': 5
        }
        
        base_risk, cross_market_risk = tool.migrate_risk_config(legacy_risk)
        
        # Check base risk migration
        assert base_risk.max_position_size == Decimal('0.1')
        assert base_risk.max_daily_loss == Decimal('0.05')
        assert base_risk.stop_loss_percentage == Decimal('0.02')
        assert base_risk.max_open_positions == 5
        
        # Check cross-market risk defaults
        assert cross_market_risk.max_total_exposure == Decimal('0.8')
        assert cross_market_risk.crypto_max_allocation == Decimal('0.6')
        assert cross_market_risk.forex_max_allocation == Decimal('0.4')
        assert cross_market_risk.max_cross_market_positions == 5
    
    def test_create_default_forex_config(self):
        """Test creating default forex configuration."""
        tool = ConfigMigrationTool()
        
        forex_config = tool.create_default_forex_config()
        
        assert forex_config.enabled is False  # Disabled by default
        assert len(forex_config.sessions) == 4  # All major sessions
        assert 'sydney' in forex_config.sessions
        assert 'tokyo' in forex_config.sessions
        assert 'london' in forex_config.sessions
        assert 'new_york' in forex_config.sessions
        assert forex_config.default_lot_size == Decimal('0.01')
        assert forex_config.max_spread_pips == 5
    
    def test_migrate_strategies(self):
        """Test migrating strategy configurations."""
        tool = ConfigMigrationTool()
        
        legacy_strategies = {
            'ma_strategy': {
                'enabled': True,
                'symbols': 'BTC/USDT,ETH/USDT',
                'timeframe': '1h',
                'parameters': {'fast': 10, 'slow': 20}
            },
            'rsi_strategy': {
                'enabled': False,
                'symbols': ['ADA/USDT'],
                'timeframe': '15m'
            }
        }
        
        migrated_strategies = tool.migrate_strategies(legacy_strategies)
        
        assert len(migrated_strategies) == 2
        assert 'ma_strategy' in migrated_strategies
        assert 'rsi_strategy' in migrated_strategies
        
        # Check MA strategy migration
        ma_strategy = migrated_strategies['ma_strategy']
        assert ma_strategy.enabled is True
        assert ma_strategy.symbols == ['BTC/USDT', 'ETH/USDT']
        assert ma_strategy.strategy_type == 'moving_average'  # Inferred from name
        
        # Check RSI strategy migration
        rsi_strategy = migrated_strategies['rsi_strategy']
        assert rsi_strategy.enabled is False
        assert rsi_strategy.symbols == ['ADA/USDT']
        assert rsi_strategy.strategy_type == 'rsi'  # Inferred from name
    
    def test_generate_migration_report(self):
        """Test generating migration report."""
        tool = ConfigMigrationTool()
        
        legacy_config = {
            'exchanges': {'binance': {}, 'coinbase': {}},
            'strategies': {'ma_strategy': {}, 'rsi_strategy': {}}
        }
        
        # Create minimal migrated config
        crypto_config = CryptoMarketConfig(
            enabled=True,
            exchanges={
                'binance': ExchangeConfig(
                    name='binance',
                    exchange_type='binance',
                    api_key='key',
                    api_secret='secret'
                )
            }
        )
        
        migrated_config = MultiMarketTradingBotConfig(
            crypto=crypto_config,
            forex=ForexMarketConfig(enabled=False),
            strategies={
                'ma_strategy': StrategyConfig(
                    name='ma_strategy',
                    strategy_type='moving_average',
                    symbols=['BTC/USDT']
                )
            },
            cross_market_risk=CrossMarketRiskConfig(
                crypto_max_allocation=Decimal("0.5"),
                forex_max_allocation=Decimal("0.5")
            )
        )
        
        report = tool.generate_migration_report(legacy_config, migrated_config)
        
        assert "Configuration Migration Report" in report
        assert "Exchanges Migrated: 1/2" in report
        assert "Strategies Migrated: 1/2" in report
        assert "✓ binance" in report
        assert "✗ coinbase" in report
        assert "New Multi-Market Features Added" in report
        assert "Next Steps" in report


if __name__ == "__main__":
    pytest.main([__file__])