"""
Unit tests for multi-market monitoring functionality.

Tests the enhanced monitoring system including:
- Market-specific metrics collection
- Cross-market correlation monitoring
- Session transition alerts
- Regulatory compliance monitoring
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

from src.monitoring.multi_market_monitor import (
    MultiMarketMonitor, AlertType, MarketMetrics, CrossMarketAlert
)
from src.monitoring.notification_system import NotificationLevel
from src.markets.types import MarketType
from src.markets.sessions import SessionInfo, SessionStatus
from src.compliance.compliance_manager import ComplianceCheck, ComplianceStatus


class TestMultiMarketMonitor:
    """Test cases for MultiMarketMonitor."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            'base_monitoring': {
                'monitoring_interval': 60,
                'prometheus_interval': 30
            },
            'session_config_path': 'config/sessions.yaml',
            'correlation': {
                'correlation_lookback_days': 30
            },
            'compliance': {
                'rules': {},
                'jurisdictions': ['US']
            },
            'monitoring_interval': 10,
            'correlation_alert_threshold': 0.8,
            'session_alerts_enabled': True,
            'compliance_alerts_enabled': True
        }
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock dependencies for MultiMarketMonitor."""
        with patch('src.monitoring.multi_market_monitor.MonitoringManager') as mock_base, \
             patch('src.monitoring.multi_market_monitor.NotificationSystem') as mock_notif, \
             patch('src.monitoring.multi_market_monitor.SessionManager') as mock_session, \
             patch('src.monitoring.multi_market_monitor.CorrelationMonitor') as mock_corr, \
             patch('src.monitoring.multi_market_monitor.ComplianceManager') as mock_comp:
            
            yield {
                'base_monitor': mock_base.return_value,
                'notification_system': mock_notif.return_value,
                'session_manager': mock_session.return_value,
                'correlation_monitor': mock_corr.return_value,
                'compliance_manager': mock_comp.return_value
            }
    
    @pytest.fixture
    def monitor(self, mock_config, mock_dependencies):
        """Create MultiMarketMonitor instance for testing."""
        return MultiMarketMonitor(mock_config)
    
    def test_initialization(self, mock_config, mock_dependencies):
        """Test MultiMarketMonitor initialization."""
        monitor = MultiMarketMonitor(mock_config)
        
        assert monitor.config == mock_config
        assert monitor.monitoring_interval == 10
        assert monitor.correlation_threshold == 0.8
        assert monitor.session_alert_enabled is True
        assert monitor.compliance_alert_enabled is True
        assert not monitor._running
        assert len(monitor.market_metrics) == 0
        assert len(monitor.active_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, monitor, mock_dependencies):
        """Test starting multi-market monitoring."""
        # Mock the monitoring loop to prevent infinite execution
        with patch.object(monitor, '_monitoring_loop') as mock_loop:
            mock_loop.return_value = asyncio.create_task(asyncio.sleep(0))
            
            await monitor.start_monitoring()
            
            assert monitor._running is True
            mock_dependencies['base_monitor'].start_monitoring.assert_called_once()
            mock_dependencies['notification_system'].start_processing.assert_called_once()
            assert monitor._monitoring_task is not None
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, monitor, mock_dependencies):
        """Test stopping multi-market monitoring."""
        # Start monitoring first
        with patch.object(monitor, '_monitoring_loop') as mock_loop:
            mock_loop.return_value = asyncio.create_task(asyncio.sleep(0))
            await monitor.start_monitoring()
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        assert monitor._running is False
        mock_dependencies['base_monitor'].stop_monitoring.assert_called_once()
        mock_dependencies['notification_system'].stop_processing.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_market_metrics(self, monitor):
        """Test updating market metrics."""
        with patch.object(monitor, '_get_market_session_info') as mock_session_info:
            mock_session_info.return_value = {
                'is_active': True,
                'status': 'open',
                'active_symbols': 100,
                'volume_24h': 1000000.0,
                'price_change_24h': 0.02,
                'error_rate': 0.001,
                'latency_ms': 50.0,
                'spread_average': 0.001,
                'liquidity_score': 0.95,
                'volatility_index': 0.3
            }
            
            await monitor._update_market_metrics()
            
            # Check that metrics were created for both market types
            assert MarketType.CRYPTO in monitor.market_metrics
            assert MarketType.FOREX in monitor.market_metrics
            
            crypto_metrics = monitor.market_metrics[MarketType.CRYPTO]
            assert crypto_metrics.market_type == MarketType.CRYPTO
            assert crypto_metrics.is_active is True
            assert crypto_metrics.active_symbols == 100
    
    @pytest.mark.asyncio
    async def test_session_transition_alerts(self, monitor, mock_dependencies):
        """Test session transition alert generation."""
        # Mock session manager to return session info
        mock_session_info = SessionInfo(
            session_name="london",
            is_active=True,
            status=SessionStatus.OPEN,
            next_close=datetime.utcnow() + timedelta(minutes=10)
        )
        
        mock_dependencies['session_manager'].get_market_sessions.return_value = {
            'london': mock_session_info
        }
        
        # Set up previous session state
        monitor._last_session_check['london'] = {
            'status': 'closed',
            'timestamp': datetime.utcnow() - timedelta(minutes=5)
        }
        
        with patch.object(monitor, '_send_session_alert') as mock_send_alert:
            await monitor._check_session_transitions()
            
            # Should detect transition from closed to open
            mock_send_alert.assert_called()
            call_args = mock_send_alert.call_args[0]
            assert "Market Opened" in call_args[0]
    
    @pytest.mark.asyncio
    async def test_correlation_monitoring(self, monitor, mock_dependencies):
        """Test correlation monitoring and alerts."""
        # Mock high correlations
        high_correlations = [
            {
                'symbol1': 'BTC/USD',
                'symbol2': 'ETH/USD',
                'correlation': 0.85,
                'confidence': 0.9,
                'last_updated': datetime.utcnow().isoformat(),
                'data_points': 100
            }
        ]
        
        mock_dependencies['correlation_monitor'].get_high_correlations.return_value = high_correlations
        
        with patch.object(monitor, '_send_correlation_alert') as mock_send_alert:
            await monitor._monitor_correlations()
            
            # Should send correlation alert for high correlation
            mock_send_alert.assert_called()
            call_args = mock_send_alert.call_args[0]
            assert "High Correlation Detected" in call_args[0]
    
    @pytest.mark.asyncio
    async def test_compliance_monitoring(self, monitor, mock_dependencies):
        """Test compliance monitoring and alerts."""
        # Mock compliance violation
        violation = ComplianceCheck(
            rule_id="position_size_limit",
            status=ComplianceStatus.VIOLATION,
            message="Position size exceeds limit",
            timestamp=datetime.utcnow(),
            market_type=MarketType.CRYPTO,
            severity="high"
        )
        
        mock_dependencies['compliance_manager'].active_violations = [violation]
        
        with patch.object(monitor, '_send_alert') as mock_send_alert:
            await monitor._check_compliance_status()
            
            # Should send compliance violation alert
            mock_send_alert.assert_called()
            call_args = mock_send_alert.call_args
            assert call_args[0][0] == AlertType.COMPLIANCE_VIOLATION
            assert "Compliance Violation" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_volume_anomaly_detection(self, monitor):
        """Test volume anomaly detection."""
        # Set up market metrics with high volume
        monitor.market_metrics[MarketType.CRYPTO] = MarketMetrics(
            market_type=MarketType.CRYPTO,
            is_active=True,
            session_status='open',
            active_symbols=100,
            total_volume_24h=3000000.0,  # High volume
            price_change_24h=0.02,
            error_rate=0.001,
            latency_ms=50.0,
            last_updated=datetime.utcnow()
        )
        
        with patch.object(monitor, '_send_alert') as mock_send_alert:
            await monitor._check_volume_anomalies()
            
            # Should send volume anomaly alert
            mock_send_alert.assert_called()
            call_args = mock_send_alert.call_args
            assert call_args[0][0] == AlertType.VOLUME_ANOMALY
            assert "High Volume Alert" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_market_health_monitoring(self, monitor):
        """Test market health monitoring."""
        # Set up market metrics with high error rate
        monitor.market_metrics[MarketType.FOREX] = MarketMetrics(
            market_type=MarketType.FOREX,
            is_active=True,
            session_status='open',
            active_symbols=50,
            total_volume_24h=500000.0,
            price_change_24h=0.01,
            error_rate=0.06,  # High error rate
            latency_ms=1500.0,  # High latency
            last_updated=datetime.utcnow()
        )
        
        with patch.object(monitor, '_send_alert') as mock_send_alert:
            await monitor._check_market_health()
            
            # Should send alerts for both high error rate and high latency
            assert mock_send_alert.call_count == 2
            
            # Check alert types
            call_args_list = mock_send_alert.call_args_list
            alert_types = [call[0][0] for call in call_args_list]
            assert AlertType.MARKET_DISCONNECT in alert_types
    
    @pytest.mark.asyncio
    async def test_send_alert(self, monitor, mock_dependencies):
        """Test alert sending functionality."""
        await monitor._send_alert(
            AlertType.SESSION_TRANSITION,
            "Test Alert",
            "Test message",
            NotificationLevel.INFO,
            [MarketType.CRYPTO],
            {'test_key': 'test_value'}
        )
        
        # Check that alert was stored
        assert len(monitor.active_alerts) == 1
        assert len(monitor.alert_history) == 1
        
        # Check notification was sent
        mock_dependencies['notification_system'].send_notification.assert_called_once()
        call_args = mock_dependencies['notification_system'].send_notification.call_args[1]
        assert call_args['title'] == "Test Alert"
        assert call_args['message'] == "Test message"
        assert call_args['level'] == NotificationLevel.INFO
    
    def test_get_market_metrics(self, monitor):
        """Test getting market metrics."""
        # Add test metrics
        monitor.market_metrics[MarketType.CRYPTO] = MarketMetrics(
            market_type=MarketType.CRYPTO,
            is_active=True,
            session_status='open',
            active_symbols=100,
            total_volume_24h=1000000.0,
            price_change_24h=0.02,
            error_rate=0.001,
            latency_ms=50.0,
            last_updated=datetime.utcnow()
        )
        
        # Test getting specific market metrics
        crypto_metrics = monitor.get_market_metrics(MarketType.CRYPTO)
        assert crypto_metrics['market_type'] == 'crypto'
        assert crypto_metrics['is_active'] is True
        assert crypto_metrics['active_symbols'] == 100
        
        # Test getting all market metrics
        all_metrics = monitor.get_market_metrics()
        assert 'crypto' in all_metrics
        assert all_metrics['crypto']['active_symbols'] == 100
    
    def test_get_active_alerts(self, monitor):
        """Test getting active alerts."""
        # Add test alert
        alert = CrossMarketAlert(
            alert_type=AlertType.CORRELATION_SPIKE,
            title="Test Alert",
            message="Test message",
            severity=NotificationLevel.WARNING,
            markets_affected=[MarketType.CRYPTO],
            timestamp=datetime.utcnow(),
            metadata={'test': 'data'}
        )
        
        monitor.active_alerts['test_alert'] = alert
        
        active_alerts = monitor.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0]['title'] == "Test Alert"
        assert active_alerts[0]['alert_type'] == 'correlation_spike'
    
    def test_get_alert_history(self, monitor):
        """Test getting alert history."""
        # Add test alerts to history
        old_alert = CrossMarketAlert(
            alert_type=AlertType.SESSION_TRANSITION,
            title="Old Alert",
            message="Old message",
            severity=NotificationLevel.INFO,
            markets_affected=[MarketType.FOREX],
            timestamp=datetime.utcnow() - timedelta(hours=25),  # Older than 24h
            metadata={}
        )
        
        recent_alert = CrossMarketAlert(
            alert_type=AlertType.VOLUME_ANOMALY,
            title="Recent Alert",
            message="Recent message",
            severity=NotificationLevel.WARNING,
            markets_affected=[MarketType.CRYPTO],
            timestamp=datetime.utcnow() - timedelta(hours=1),  # Within 24h
            metadata={}
        )
        
        monitor.alert_history.extend([old_alert, recent_alert])
        
        # Test default 24h history
        history = monitor.get_alert_history()
        assert len(history) == 1
        assert history[0]['title'] == "Recent Alert"
        
        # Test custom time period
        history_48h = monitor.get_alert_history(hours=48)
        assert len(history_48h) == 2
    
    def test_cleanup_old_alerts(self, monitor):
        """Test cleanup of old alerts."""
        # Add old alert
        old_alert = CrossMarketAlert(
            alert_type=AlertType.SESSION_TRANSITION,
            title="Old Alert",
            message="Old message",
            severity=NotificationLevel.INFO,
            markets_affected=[MarketType.FOREX],
            timestamp=datetime.utcnow() - timedelta(hours=25),
            metadata={}
        )
        
        # Add recent alert
        recent_alert = CrossMarketAlert(
            alert_type=AlertType.VOLUME_ANOMALY,
            title="Recent Alert",
            message="Recent message",
            severity=NotificationLevel.WARNING,
            markets_affected=[MarketType.CRYPTO],
            timestamp=datetime.utcnow() - timedelta(hours=1),
            metadata={}
        )
        
        monitor.active_alerts['old'] = old_alert
        monitor.active_alerts['recent'] = recent_alert
        
        # Run cleanup
        monitor._cleanup_old_alerts()
        
        # Only recent alert should remain
        assert len(monitor.active_alerts) == 1
        assert 'recent' in monitor.active_alerts
        assert 'old' not in monitor.active_alerts
    
    def test_get_monitoring_status(self, monitor):
        """Test getting monitoring status."""
        # Set up some state
        monitor._running = True
        monitor.active_alerts['test'] = Mock()
        
        # Create proper mock alerts with all required attributes
        mock_alert1 = Mock()
        mock_alert1.timestamp = datetime.utcnow() - timedelta(hours=1)
        mock_alert1.alert_type.value = 'test_alert'
        mock_alert1.title = 'Test Alert 1'
        mock_alert1.message = 'Test message 1'
        mock_alert1.severity.value = 'info'
        mock_alert1.markets_affected = [MarketType.CRYPTO]
        mock_alert1.metadata = {}
        
        mock_alert2 = Mock()
        mock_alert2.timestamp = datetime.utcnow() - timedelta(hours=2)
        mock_alert2.alert_type.value = 'test_alert'
        mock_alert2.title = 'Test Alert 2'
        mock_alert2.message = 'Test message 2'
        mock_alert2.severity.value = 'warning'
        mock_alert2.markets_affected = [MarketType.FOREX]
        mock_alert2.metadata = {}
        
        monitor.alert_history.extend([mock_alert1, mock_alert2])
        
        # Create proper mock metrics with last_updated attribute
        mock_crypto_metrics = Mock()
        mock_crypto_metrics.last_updated = datetime.utcnow()
        mock_forex_metrics = Mock()
        mock_forex_metrics.last_updated = datetime.utcnow() - timedelta(minutes=5)
        
        monitor.market_metrics[MarketType.CRYPTO] = mock_crypto_metrics
        monitor.market_metrics[MarketType.FOREX] = mock_forex_metrics
        
        status = monitor.get_monitoring_status()
        
        assert status['running'] is True
        assert status['session_alerts_enabled'] is True
        assert status['compliance_alerts_enabled'] is True
        assert status['monitoring_interval'] == 10
        assert status['active_alerts_count'] == 1
        assert len(status['markets_monitored']) == 2


class TestMarketMetrics:
    """Test cases for MarketMetrics dataclass."""
    
    def test_market_metrics_creation(self):
        """Test MarketMetrics creation."""
        metrics = MarketMetrics(
            market_type=MarketType.CRYPTO,
            is_active=True,
            session_status='open',
            active_symbols=100,
            total_volume_24h=1000000.0,
            price_change_24h=0.02,
            error_rate=0.001,
            latency_ms=50.0,
            last_updated=datetime.utcnow()
        )
        
        assert metrics.market_type == MarketType.CRYPTO
        assert metrics.is_active is True
        assert metrics.active_symbols == 100
        assert metrics.spread_average == 0.0  # Default value
        assert metrics.liquidity_score == 0.0  # Default value
        assert metrics.volatility_index == 0.0  # Default value


class TestCrossMarketAlert:
    """Test cases for CrossMarketAlert dataclass."""
    
    def test_cross_market_alert_creation(self):
        """Test CrossMarketAlert creation."""
        alert = CrossMarketAlert(
            alert_type=AlertType.CORRELATION_SPIKE,
            title="Test Alert",
            message="Test message",
            severity=NotificationLevel.WARNING,
            markets_affected=[MarketType.CRYPTO, MarketType.FOREX],
            timestamp=datetime.utcnow(),
            metadata={'correlation': 0.85}
        )
        
        assert alert.alert_type == AlertType.CORRELATION_SPIKE
        assert alert.title == "Test Alert"
        assert len(alert.markets_affected) == 2
        assert alert.metadata['correlation'] == 0.85
        assert alert.auto_resolved is False  # Default value


@pytest.mark.integration
class TestMultiMarketMonitoringIntegration:
    """Integration tests for multi-market monitoring."""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_cycle(self):
        """Test a complete monitoring cycle."""
        config = {
            'base_monitoring': {},
            'session_config_path': None,
            'correlation': {},
            'compliance': {'rules': {}, 'jurisdictions': ['US']},
            'monitoring_interval': 1,  # Short interval for testing
            'correlation_alert_threshold': 0.8,
            'session_alerts_enabled': True,
            'compliance_alerts_enabled': True
        }
        
        with patch('src.monitoring.multi_market_monitor.MonitoringManager'), \
             patch('src.monitoring.multi_market_monitor.NotificationSystem'), \
             patch('src.monitoring.multi_market_monitor.SessionManager'), \
             patch('src.monitoring.multi_market_monitor.CorrelationMonitor'), \
             patch('src.monitoring.multi_market_monitor.ComplianceManager'):
            
            monitor = MultiMarketMonitor(config)
            
            # Start monitoring
            await monitor.start_monitoring()
            
            # Let it run for a short time
            await asyncio.sleep(0.1)
            
            # Stop monitoring
            await monitor.stop_monitoring()
            
            # Verify state
            assert not monitor._running
    
    def test_prometheus_metrics_integration(self):
        """Test integration with Prometheus metrics."""
        from src.monitoring.prometheus_exporter import PrometheusExporter
        
        # Create exporter
        exporter = PrometheusExporter()
        
        # Test multi-market metrics
        exporter.update_market_metrics(
            MarketType.CRYPTO, 100, 1000000.0, 0.001, 50.0
        )
        
        exporter.update_session_status(
            MarketType.FOREX, "london", True
        )
        
        exporter.update_correlation(
            "BTC/USD", "ETH/USD", MarketType.CRYPTO, MarketType.CRYPTO, 0.85
        )
        
        exporter.record_compliance_violation(
            MarketType.FOREX, "position_size_limit", "high"
        )
        
        exporter.record_multi_market_alert(
            "correlation_spike", "warning", MarketType.CRYPTO
        )
        
        # Get metrics and verify they contain multi-market data
        metrics_data = exporter.get_metrics()
        assert b'trading_bot_market_active_symbols' in metrics_data
        assert b'trading_bot_session_status' in metrics_data
        assert b'trading_bot_correlation_coefficient' in metrics_data
        assert b'trading_bot_compliance_violations_total' in metrics_data
        assert b'trading_bot_multi_market_alerts_total' in metrics_data


if __name__ == '__main__':
    pytest.main([__file__])