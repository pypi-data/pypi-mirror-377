#!/usr/bin/env python3
"""
Tests for the Trading Bot CLI.
"""

import os
import sys
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.trading_bot_cli import TradingBotCLI
from config.models import ExchangeConfig, ExchangeType
from config.multi_market_models import ForexBrokerConfig, ForexBrokerType


class TestTradingBotCLI:
    """Test cases for the Trading Bot CLI."""
    
    @pytest.fixture
    def cli(self):
        """Create a CLI instance with temporary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cli = TradingBotCLI()
            cli.config_file = Path(temp_dir) / "config.yaml"
            cli.accounts_file = Path(temp_dir) / "accounts.yaml"
            yield cli
    
    @pytest.fixture
    def sample_accounts(self):
        """Sample account configuration."""
        return {
            "crypto_exchanges": {
                "binance": {
                    "name": "binance",
                    "exchange_type": "binance",
                    "api_key": "test_api_key",
                    "api_secret": "test_api_secret",
                    "sandbox": True,
                    "rate_limit": 1200,
                    "timeout": 30,
                    "enabled": True
                }
            },
            "forex_brokers": {
                "oanda": {
                    "name": "oanda",
                    "broker_type": "oanda",
                    "api_key": "test_oanda_key",
                    "account_id": "test_account_id",
                    "sandbox": True,
                    "timeout": 30,
                    "enabled": True
                }
            }
        }
    
    def test_load_accounts_empty(self, cli):
        """Test loading accounts when file doesn't exist."""
        accounts = cli._load_accounts()
        assert accounts == {"crypto_exchanges": {}, "forex_brokers": {}}
    
    def test_save_and_load_accounts(self, cli, sample_accounts):
        """Test saving and loading accounts."""
        cli._save_accounts(sample_accounts)
        loaded_accounts = cli._load_accounts()
        assert loaded_accounts == sample_accounts
    
    def test_add_crypto_exchange_validation(self, cli):
        """Test crypto exchange validation."""
        # Test valid configuration
        config = {
            "name": "binance",
            "exchange_type": "binance",
            "api_key": "valid_key",
            "api_secret": "valid_secret",
            "sandbox": True,
            "rate_limit": 1200,
            "timeout": 30,
            "enabled": True
        }
        
        # Should not raise exception
        exchange_config = ExchangeConfig(**config)
        assert exchange_config.name == "binance"
        assert exchange_config.exchange_type == ExchangeType.BINANCE
    
    def test_add_forex_broker_validation(self, cli):
        """Test forex broker validation."""
        # Test valid OANDA configuration
        config = {
            "name": "oanda",
            "broker_type": "oanda",
            "api_key": "valid_key",
            "account_id": "valid_account",
            "sandbox": True,
            "timeout": 30,
            "enabled": True
        }
        
        # Should not raise exception
        broker_config = ForexBrokerConfig(**config)
        assert broker_config.name == "oanda"
        assert broker_config.broker_type == ForexBrokerType.OANDA
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_add_crypto_exchange_interactive(self, mock_getpass, mock_input, cli):
        """Test adding crypto exchange in interactive mode."""
        # Mock user inputs
        mock_input.side_effect = [
            "binance",  # exchange name
            "1",        # exchange type choice (binance)
            "y"         # sandbox mode
        ]
        mock_getpass.side_effect = [
            "test_api_key",     # API key
            "test_api_secret"   # API secret
        ]
        
        # Create mock args
        args = Mock()
        args.name = None
        args.exchange_type = None
        args.api_key = None
        args.api_secret = None
        args.api_passphrase = None
        args.sandbox = None
        args.rate_limit = None
        args.timeout = None
        args.enabled = None
        args.force = False
        
        # Test adding exchange
        result = cli.add_crypto_exchange(args)
        assert result == 0
        
        # Verify account was saved
        accounts = cli._load_accounts()
        assert "binance" in accounts["crypto_exchanges"]
        assert accounts["crypto_exchanges"]["binance"]["api_key"] == "test_api_key"
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_add_forex_broker_interactive(self, mock_getpass, mock_input, cli):
        """Test adding forex broker in interactive mode."""
        # Mock user inputs
        mock_input.side_effect = [
            "oanda",           # broker name
            "1",               # broker type choice (oanda)
            "test_account_id"  # account ID
        ]
        mock_getpass.side_effect = [
            "test_api_key"     # API key
        ]
        
        # Create mock args
        args = Mock()
        args.name = None
        args.broker_type = None
        args.api_key = None
        args.account_id = None
        args.server = None
        args.login = None
        args.password = None
        args.host = None
        args.port = None
        args.client_id = None
        args.sandbox = None
        args.timeout = None
        args.enabled = None
        args.force = False
        
        # Test adding broker
        result = cli.add_forex_broker(args)
        assert result == 0
        
        # Verify account was saved
        accounts = cli._load_accounts()
        assert "oanda" in accounts["forex_brokers"]
        assert accounts["forex_brokers"]["oanda"]["api_key"] == "test_api_key"
    
    def test_list_accounts(self, cli, sample_accounts, capsys):
        """Test listing accounts."""
        cli._save_accounts(sample_accounts)
        
        args = Mock()
        result = cli.list_accounts(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "binance" in captured.out
        assert "oanda" in captured.out
    
    def test_remove_account(self, cli, sample_accounts):
        """Test removing accounts."""
        cli._save_accounts(sample_accounts)
        
        # Remove crypto exchange
        args = Mock()
        args.name = "binance"
        args.type = "crypto"
        
        result = cli.remove_account(args)
        assert result == 0
        
        accounts = cli._load_accounts()
        assert "binance" not in accounts["crypto_exchanges"]
        assert "oanda" in accounts["forex_brokers"]  # Should still exist
    
    def test_enable_disable_account(self, cli, sample_accounts):
        """Test enabling and disabling accounts."""
        cli._save_accounts(sample_accounts)
        
        # Disable account
        args = Mock()
        args.name = "binance"
        args.type = "crypto"
        
        result = cli.disable_account(args)
        assert result == 0
        
        accounts = cli._load_accounts()
        assert accounts["crypto_exchanges"]["binance"]["enabled"] is False
        
        # Enable account
        result = cli.enable_account(args)
        assert result == 0
        
        accounts = cli._load_accounts()
        assert accounts["crypto_exchanges"]["binance"]["enabled"] is True
    
    def test_validate_accounts(self, cli, sample_accounts, capsys):
        """Test account validation."""
        cli._save_accounts(sample_accounts)
        
        args = Mock()
        result = cli.validate_accounts(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Configuration valid" in captured.out
    
    def test_validate_accounts_with_placeholder(self, cli, capsys):
        """Test validation with placeholder credentials."""
        accounts_with_placeholder = {
            "crypto_exchanges": {
                "binance": {
                    "name": "binance",
                    "exchange_type": "binance",
                    "api_key": "your_api_key_here",  # Placeholder
                    "api_secret": "your_api_secret_here",  # Placeholder
                    "sandbox": True,
                    "rate_limit": 1200,
                    "timeout": 30,
                    "enabled": True
                }
            },
            "forex_brokers": {}
        }
        
        cli._save_accounts(accounts_with_placeholder)
        
        args = Mock()
        result = cli.validate_accounts(args)
        
        assert result == 0  # Should succeed but with warnings
        captured = capsys.readouterr()
        assert "placeholder credentials" in captured.out
    
    @patch('scripts.trading_bot_cli.TradingBotCLI._get_trades_from_db')
    def test_generate_summary_report(self, mock_get_trades, cli, capsys):
        """Test generating summary report."""
        # Mock trade data
        mock_trades = [
            {
                'id': 1,
                'symbol': 'BTC/USDT',
                'side': 'BUY',
                'amount': 0.1,
                'price': 45000.0,
                'timestamp': datetime.now() - timedelta(days=1),
                'pnl': 500.0,
                'strategy': 'TestStrategy',
                'exchange': 'binance'
            },
            {
                'id': 2,
                'symbol': 'ETH/USDT',
                'side': 'SELL',
                'amount': 2.0,
                'price': 3000.0,
                'timestamp': datetime.now(),
                'pnl': -150.0,
                'strategy': 'TestStrategy',
                'exchange': 'binance'
            }
        ]
        mock_get_trades.return_value = mock_trades
        
        # Mock database manager
        with patch.object(cli, '_load_db_manager'):
            args = Mock()
            args.report_type = "summary"
            args.start_date = "2024-01-01"
            args.end_date = "2024-01-31"
            args.output = None
            
            result = cli.generate_report(args)
            assert result == 0
            
            captured = capsys.readouterr()
            assert "Trading Summary Report" in captured.out
            assert "Total Trades: 2" in captured.out
            assert "$350.00" in captured.out  # Total P&L
    
    @patch('scripts.trading_bot_cli.TradingBotCLI._get_trades_from_db')
    def test_generate_detailed_report(self, mock_get_trades, cli, capsys):
        """Test generating detailed report."""
        mock_trades = [
            {
                'id': 1,
                'symbol': 'BTC/USDT',
                'side': 'BUY',
                'amount': 0.1,
                'price': 45000.0,
                'timestamp': datetime.now(),
                'pnl': 500.0,
                'strategy': 'TestStrategy',
                'exchange': 'binance'
            }
        ]
        mock_get_trades.return_value = mock_trades
        
        with patch.object(cli, '_load_db_manager'):
            args = Mock()
            args.report_type = "detailed"
            args.start_date = "2024-01-01"
            args.end_date = "2024-01-31"
            args.output = None
            
            result = cli.generate_report(args)
            assert result == 0
            
            captured = capsys.readouterr()
            assert "Detailed Trading Report" in captured.out
            assert "BTC/USDT" in captured.out
    
    @patch('scripts.trading_bot_cli.TradingBotCLI._get_trades_from_db')
    def test_generate_performance_report(self, mock_get_trades, cli, capsys):
        """Test generating performance report."""
        mock_trades = [
            {
                'id': 1,
                'symbol': 'BTC/USDT',
                'side': 'BUY',
                'amount': 0.1,
                'price': 45000.0,
                'timestamp': datetime.now(),
                'pnl': 500.0,
                'strategy': 'TestStrategy',
                'exchange': 'binance'
            },
            {
                'id': 2,
                'symbol': 'ETH/USDT',
                'side': 'SELL',
                'amount': 2.0,
                'price': 3000.0,
                'timestamp': datetime.now(),
                'pnl': -150.0,
                'strategy': 'TestStrategy',
                'exchange': 'binance'
            }
        ]
        mock_get_trades.return_value = mock_trades
        
        with patch.object(cli, '_load_db_manager'):
            args = Mock()
            args.report_type = "performance"
            args.start_date = "2024-01-01"
            args.end_date = "2024-01-31"
            args.output = None
            
            result = cli.generate_report(args)
            assert result == 0
            
            captured = capsys.readouterr()
            assert "Performance Analysis Report" in captured.out
            assert "Win Rate:" in captured.out
            assert "Best Trade:" in captured.out
    
    def test_generate_report_no_trades(self, cli, capsys):
        """Test generating report with no trades."""
        with patch.object(cli, '_load_db_manager'), \
             patch.object(cli, '_get_trades_from_db', return_value=[]):
            
            args = Mock()
            args.report_type = "summary"
            args.start_date = "2024-01-01"
            args.end_date = "2024-01-31"
            args.output = None
            
            result = cli.generate_report(args)
            assert result == 0
            
            captured = capsys.readouterr()
            assert "No trades found" in captured.out
    
    def test_start_bot_no_accounts(self, cli, capsys):
        """Test starting bot with no accounts configured."""
        args = Mock()
        
        with patch.object(cli, 'validate_accounts', return_value=0):
            result = cli.start_bot(args)
            assert result == 1
            
            captured = capsys.readouterr()
            assert "No enabled accounts found" in captured.out
    
    def test_start_bot_with_accounts(self, cli, sample_accounts, capsys):
        """Test starting bot with valid accounts."""
        cli._save_accounts(sample_accounts)
        
        args = Mock()
        
        with patch.object(cli, 'validate_accounts', return_value=0):
            result = cli.start_bot(args)
            assert result == 0
            
            captured = capsys.readouterr()
            assert "Trading bot started successfully" in captured.out
    
    def test_stop_bot(self, cli, capsys):
        """Test stopping bot."""
        args = Mock()
        result = cli.stop_bot(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Trading bot stopped successfully" in captured.out
    
    def test_bot_status(self, cli, capsys):
        """Test bot status command."""
        args = Mock()
        result = cli.bot_status(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Bot Status:" in captured.out
    
    def test_invalid_account_type(self, cli):
        """Test operations with invalid account type."""
        args = Mock()
        args.name = "test"
        args.type = "invalid"
        
        result = cli.remove_account(args)
        assert result == 1
        
        result = cli.enable_account(args)
        assert result == 1
        
        result = cli.disable_account(args)
        assert result == 1
    
    def test_account_not_found(self, cli):
        """Test operations on non-existent accounts."""
        args = Mock()
        args.name = "nonexistent"
        args.type = "crypto"
        
        result = cli.remove_account(args)
        assert result == 1
        
        result = cli.enable_account(args)
        assert result == 1
        
        result = cli.disable_account(args)
        assert result == 1
    
    def test_force_overwrite(self, cli, sample_accounts):
        """Test force overwriting existing accounts."""
        cli._save_accounts(sample_accounts)
        
        # Try to add existing account without force
        args = Mock()
        args.name = "binance"
        args.exchange_type = "binance"
        args.api_key = "new_key"
        args.api_secret = "new_secret"
        args.api_passphrase = None
        args.sandbox = True
        args.rate_limit = 1200
        args.timeout = 30
        args.enabled = True
        args.force = False
        
        result = cli.add_crypto_exchange(args)
        assert result == 1  # Should fail without force
        
        # Try again with force
        args.force = True
        result = cli.add_crypto_exchange(args)
        assert result == 0  # Should succeed with force
        
        # Verify account was updated
        accounts = cli._load_accounts()
        assert accounts["crypto_exchanges"]["binance"]["api_key"] == "new_key"


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_full_workflow(self):
        """Test a complete CLI workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cli = TradingBotCLI()
            cli.config_file = Path(temp_dir) / "config.yaml"
            cli.accounts_file = Path(temp_dir) / "accounts.yaml"
            
            # 1. Start with empty accounts
            accounts = cli._load_accounts()
            assert len(accounts["crypto_exchanges"]) == 0
            assert len(accounts["forex_brokers"]) == 0
            
            # 2. Add accounts programmatically
            sample_accounts = {
                "crypto_exchanges": {
                    "binance": {
                        "name": "binance",
                        "exchange_type": "binance",
                        "api_key": "test_key",
                        "api_secret": "test_secret",
                        "sandbox": True,
                        "rate_limit": 1200,
                        "timeout": 30,
                        "enabled": True
                    }
                },
                "forex_brokers": {
                    "oanda": {
                        "name": "oanda",
                        "broker_type": "oanda",
                        "api_key": "test_oanda_key",
                        "account_id": "test_account",
                        "sandbox": True,
                        "timeout": 30,
                        "enabled": True
                    }
                }
            }
            cli._save_accounts(sample_accounts)
            
            # 3. Validate accounts
            args = Mock()
            result = cli.validate_accounts(args)
            assert result == 0
            
            # 4. Disable an account
            args.name = "oanda"
            args.type = "forex"
            result = cli.disable_account(args)
            assert result == 0
            
            # 5. Verify account is disabled
            accounts = cli._load_accounts()
            assert accounts["forex_brokers"]["oanda"]["enabled"] is False
            
            # 6. Remove an account
            result = cli.remove_account(args)
            assert result == 0
            
            # 7. Verify account is removed
            accounts = cli._load_accounts()
            assert "oanda" not in accounts["forex_brokers"]
            assert "binance" in accounts["crypto_exchanges"]


if __name__ == "__main__":
    pytest.main([__file__])