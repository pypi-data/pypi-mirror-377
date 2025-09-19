"""
Unit tests for configuration management system.
"""
import os
import tempfile
import yaml
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch, mock_open
import pytest
from pydantic import ValidationError

from config import (
    ConfigManager,
    ConfigurationError,
    TradingBotConfig,
    ExchangeConfig,
    StrategyConfig,
    RiskConfig,
    DatabaseConfig,
    LoggingConfig,
    BacktestConfig,
    ExchangeType,
    StrategyType,
    DatabaseType,
    LogLevel,
    LogFormat,
    get_config_manager,
    get_config
)


class TestConfigModels:
    """Test configuration model validation."""
    
    def test_exchange_config_valid(self):
        """Test valid exchange configuration."""
        config = ExchangeConfig(
            name="binance",
            exchange_type=ExchangeType.BINANCE,
            api_key="test_key",
            api_secret="test_secret",
            sandbox=True
        )
        assert config.name == "binance"
        assert config.exchange_type == ExchangeType.BINANCE
        assert config.sandbox is True
        assert config.enabled is True
        assert config.rate_limit == 1200
    
    def test_exchange_config_invalid_credentials(self):
        """Test exchange configuration with invalid credentials."""
        with pytest.raises(ValidationError):
            ExchangeConfig(
                name="binance",
                exchange_type=ExchangeType.BINANCE,
                api_key="",  # Empty key should fail
                api_secret="test_secret"
            )
    
    def test_exchange_config_invalid_rate_limit(self):
        """Test exchange configuration with invalid rate limit."""
        with pytest.raises(ValidationError):
            ExchangeConfig(
                name="binance",
                exchange_type=ExchangeType.BINANCE,
                api_key="test_key",
                api_secret="test_secret",
                rate_limit=0  # Should be positive
            )
    
    def test_strategy_config_valid(self):
        """Test valid strategy configuration."""
        config = StrategyConfig(
            name="ma_strategy",
            strategy_type=StrategyType.MOVING_AVERAGE,
            symbols=["BTC/USDT", "ETH/USDT"],
            timeframe="1h",
            parameters={"fast_period": 10, "slow_period": 20}
        )
        assert config.name == "ma_strategy"
        assert config.symbols == ["BTC/USDT", "ETH/USDT"]
        assert config.timeframe == "1h"
        assert config.enabled is True
    
    def test_strategy_config_invalid_symbols(self):
        """Test strategy configuration with invalid symbols."""
        with pytest.raises(ValidationError):
            StrategyConfig(
                name="ma_strategy",
                strategy_type=StrategyType.MOVING_AVERAGE,
                symbols=[],  # Empty symbols should fail
                timeframe="1h"
            )
    
    def test_strategy_config_invalid_timeframe(self):
        """Test strategy configuration with invalid timeframe."""
        with pytest.raises(ValidationError):
            StrategyConfig(
                name="ma_strategy",
                strategy_type=StrategyType.MOVING_AVERAGE,
                symbols=["BTC/USDT"],
                timeframe="invalid"  # Invalid timeframe
            )
    
    def test_risk_config_valid(self):
        """Test valid risk configuration."""
        config = RiskConfig(
            max_position_size=Decimal("0.1"),
            max_daily_loss=Decimal("0.05"),
            stop_loss_percentage=Decimal("0.02")
        )
        assert config.max_position_size == Decimal("0.1")
        assert config.max_daily_loss == Decimal("0.05")
        assert config.position_sizing_method == "fixed_fraction"
    
    def test_risk_config_invalid_percentages(self):
        """Test risk configuration with invalid percentages."""
        with pytest.raises(ValidationError):
            RiskConfig(
                max_position_size=Decimal("1.5")  # > 1.0 should fail
            )
    
    def test_database_config_valid(self):
        """Test valid database configuration."""
        config = DatabaseConfig(
            database_type=DatabaseType.SQLITE,
            database_url="sqlite:///test.db"
        )
        assert config.database_type == DatabaseType.SQLITE
        assert config.pool_size == 5
    
    def test_logging_config_valid(self):
        """Test valid logging configuration."""
        config = LoggingConfig(
            log_level=LogLevel.INFO,
            log_format=LogFormat.JSON,
            log_file="test.log"
        )
        assert config.log_level == LogLevel.INFO
        assert config.log_format == LogFormat.JSON
    
    def test_trading_bot_config_valid(self):
        """Test valid complete trading bot configuration."""
        exchange_config = ExchangeConfig(
            name="binance",
            exchange_type=ExchangeType.BINANCE,
            api_key="test_key",
            api_secret="test_secret"
        )
        
        strategy_config = StrategyConfig(
            name="ma_strategy",
            strategy_type=StrategyType.MOVING_AVERAGE,
            symbols=["BTC/USDT"],
            timeframe="1h"
        )
        
        config = TradingBotConfig(
            exchanges={"binance": exchange_config},
            strategies={"ma_strategy": strategy_config}
        )
        
        assert len(config.exchanges) == 1
        assert len(config.strategies) == 1
        assert config.dry_run is True
    
    def test_trading_bot_config_no_exchanges(self):
        """Test trading bot configuration without exchanges."""
        with pytest.raises(ValidationError):
            TradingBotConfig(
                exchanges={},  # No exchanges should fail
                strategies={}
            )
    
    def test_backtesting_config_valid(self):
        """Test valid backtesting configuration."""
        config = BacktestConfig(
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=Decimal("10000")
        )
        assert config.start_date == "2023-01-01"
        assert config.initial_capital == Decimal("10000")
    
    def test_backtesting_config_invalid_date(self):
        """Test backtesting configuration with invalid date format."""
        with pytest.raises(ValidationError):
            BacktestConfig(
                start_date="invalid-date",
                end_date="2023-12-31"
            )


class TestConfigManager:
    """Test configuration manager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "config.yaml"
        self.env_file = Path(self.temp_dir) / ".env"
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_manager_init(self):
        """Test configuration manager initialization."""
        manager = ConfigManager(self.config_file, self.env_file)
        assert manager.config_file == self.config_file
        assert manager.env_file == self.env_file
    
    def test_load_yaml_config_empty_file(self):
        """Test loading from non-existent YAML file."""
        manager = ConfigManager(self.config_file)
        yaml_config = manager._load_yaml_config()
        assert yaml_config == {}
    
    def test_load_yaml_config_valid_file(self):
        """Test loading from valid YAML file."""
        config_data = {
            'app_name': 'TestBot',
            'debug': True,
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret'
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(self.config_file)
        yaml_config = manager._load_yaml_config()
        assert yaml_config['app_name'] == 'TestBot'
        assert yaml_config['debug'] is True
    
    def test_load_yaml_config_invalid_file(self):
        """Test loading from invalid YAML file."""
        with open(self.config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        manager = ConfigManager(self.config_file)
        with pytest.raises(ConfigurationError):
            manager._load_yaml_config()
    
    @patch.dict(os.environ, {
        'EXCHANGE_BINANCE_API_KEY': 'env_key',
        'EXCHANGE_BINANCE_API_SECRET': 'env_secret',
        'EXCHANGE_BINANCE_EXCHANGE_TYPE': 'binance'
    })
    def test_build_exchange_configs_from_env(self):
        """Test building exchange configs from environment variables."""
        manager = ConfigManager()
        exchanges = manager._build_exchange_configs({})
        
        assert 'binance' in exchanges
        assert exchanges['binance'].api_key == 'env_key'
        assert exchanges['binance'].api_secret == 'env_secret'
    
    @patch.dict(os.environ, {
        'STRATEGY_MA_STRATEGY_TYPE': 'moving_average',
        'STRATEGY_MA_SYMBOLS': 'BTC/USDT,ETH/USDT',
        'STRATEGY_MA_TIMEFRAME': '1h'
    })
    def test_build_strategy_configs_from_env(self):
        """Test building strategy configs from environment variables."""
        manager = ConfigManager()
        strategies = manager._build_strategy_configs({})
        
        assert 'ma' in strategies
        assert strategies['ma'].strategy_type == StrategyType.MOVING_AVERAGE
        assert strategies['ma'].symbols == ['BTC/USDT', 'ETH/USDT']
    
    @patch.dict(os.environ, {
        'RISK_MAX_POSITION_SIZE': '0.2',
        'RISK_STOP_LOSS_PERCENTAGE': '0.03'
    })
    def test_build_risk_config_from_env(self):
        """Test building risk config from environment variables."""
        manager = ConfigManager()
        risk_config = manager._build_risk_config({})
        
        assert risk_config.max_position_size == Decimal('0.2')
        assert risk_config.stop_loss_percentage == Decimal('0.03')
    
    @patch.dict(os.environ, {
        'DATABASE_TYPE': 'postgresql',
        'DATABASE_URL': 'postgresql://test:test@localhost/test'
    })
    def test_build_database_config_from_env(self):
        """Test building database config from environment variables."""
        manager = ConfigManager()
        db_config = manager._build_database_config({})
        
        assert db_config.database_type == DatabaseType.POSTGRESQL
        assert db_config.database_url == 'postgresql://test:test@localhost/test'
    
    @patch.dict(os.environ, {
        'LOG_LEVEL': 'DEBUG',
        'LOG_FORMAT': 'json'
    })
    def test_build_logging_config_from_env(self):
        """Test building logging config from environment variables."""
        manager = ConfigManager()
        log_config = manager._build_logging_config({})
        
        assert log_config.log_level == LogLevel.DEBUG
        assert log_config.log_format == LogFormat.JSON
    
    def test_load_config_minimal(self):
        """Test loading minimal valid configuration."""
        config_data = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret'
                }
            },
            'strategies': {
                'ma_strategy': {
                    'strategy_type': 'moving_average',
                    'symbols': ['BTC/USDT'],
                    'timeframe': '1h'
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(self.config_file)
        config = manager.load_config()
        
        assert isinstance(config, TradingBotConfig)
        assert len(config.exchanges) == 1
        assert len(config.strategies) == 1
        assert config.app_name == 'TradingBot'
    
    def test_get_config_caching(self):
        """Test that get_config caches the configuration."""
        config_data = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret'
                }
            },
            'strategies': {
                'ma_strategy': {
                    'strategy_type': 'moving_average',
                    'symbols': ['BTC/USDT'],
                    'timeframe': '1h'
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(self.config_file)
        
        # First call should load config
        config1 = manager.get_config()
        # Second call should return cached config
        config2 = manager.get_config()
        
        assert config1 is config2
    
    def test_reload_config(self):
        """Test configuration reloading."""
        config_data = {
            'app_name': 'TestBot1',
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret'
                }
            },
            'strategies': {
                'ma_strategy': {
                    'strategy_type': 'moving_average',
                    'symbols': ['BTC/USDT'],
                    'timeframe': '1h'
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(self.config_file)
        config1 = manager.get_config()
        assert config1.app_name == 'TestBot1'
        
        # Update config file
        config_data['app_name'] = 'TestBot2'
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Reload should pick up changes
        config2 = manager.reload_config()
        assert config2.app_name == 'TestBot2'
    
    def test_get_exchange_config(self):
        """Test getting specific exchange configuration."""
        config_data = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret'
                }
            },
            'strategies': {
                'ma_strategy': {
                    'strategy_type': 'moving_average',
                    'symbols': ['BTC/USDT'],
                    'timeframe': '1h'
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(self.config_file)
        
        binance_config = manager.get_exchange_config('binance')
        assert binance_config is not None
        assert binance_config.api_key == 'test_key'
        
        nonexistent_config = manager.get_exchange_config('nonexistent')
        assert nonexistent_config is None
    
    def test_get_enabled_exchanges(self):
        """Test getting enabled exchanges only."""
        config_data = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret',
                    'enabled': True
                },
                'coinbase': {
                    'exchange_type': 'coinbase',
                    'api_key': 'test_key2',
                    'api_secret': 'test_secret2',
                    'enabled': False
                }
            },
            'strategies': {
                'ma_strategy': {
                    'strategy_type': 'moving_average',
                    'symbols': ['BTC/USDT'],
                    'timeframe': '1h'
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(self.config_file)
        enabled_exchanges = manager.get_enabled_exchanges()
        
        assert len(enabled_exchanges) == 1
        assert 'binance' in enabled_exchanges
        assert 'coinbase' not in enabled_exchanges
    
    def test_save_config_template(self):
        """Test saving configuration template."""
        manager = ConfigManager()
        template_path = Path(self.temp_dir) / "template.yaml"
        
        manager.save_config_template(template_path)
        
        assert template_path.exists()
        
        with open(template_path, 'r') as f:
            template_data = yaml.safe_load(f)
        
        assert 'app_name' in template_data
        assert 'exchanges' in template_data
        assert 'strategies' in template_data
        assert 'risk' in template_data


class TestGlobalFunctions:
    """Test global configuration functions."""
    
    def test_get_config_manager_singleton(self):
        """Test that get_config_manager returns singleton."""
        # Clear any existing global instance
        import config.manager
        config.manager._config_manager = None
        
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        assert manager1 is manager2
    
    @patch('config.manager.get_config_manager')
    def test_get_config_function(self, mock_get_manager):
        """Test global get_config function."""
        mock_manager = ConfigManager()
        mock_get_manager.return_value = mock_manager
        
        # Mock the get_config method
        mock_config = TradingBotConfig(
            exchanges={'test': ExchangeConfig(
                name='test',
                exchange_type=ExchangeType.BINANCE,
                api_key='key',
                api_secret='secret'
            )},
            strategies={'test': StrategyConfig(
                name='test',
                strategy_type=StrategyType.MOVING_AVERAGE,
                symbols=['BTC/USDT'],
                timeframe='1h'
            )}
        )
        
        with patch.object(mock_manager, 'get_config', return_value=mock_config):
            config = get_config()
            assert config is mock_config


if __name__ == '__main__':
    pytest.main([__file__])