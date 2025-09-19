"""
Tests for monitoring and alerting functionality.
"""
import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from prometheus_client import CollectorRegistry

from src.monitoring.prometheus_exporter import PrometheusExporter
from src.monitoring.notification_system import (
    NotificationSystem, NotificationEvent, NotificationLevel, NotificationChannel,
    EmailNotificationProvider, SlackNotificationProvider, DiscordNotificationProvider,
    WebhookNotificationProvider, ConsoleNotificationProvider
)
from src.monitoring.metrics_collector import MetricsCollector, PerformanceTimer
from src.monitoring.performance_monitor import PerformanceMonitor, HealthStatus


class TestPrometheusExporter:
    """Test Prometheus metrics exporter."""
    
    @pytest.fixture
    def registry(self):
        """Create a test registry."""
        return CollectorRegistry()
    
    @pytest.fixture
    def mock_metrics_collector(self):
        """Create mock metrics collector."""
        collector = Mock(spec=MetricsCollector)
        collector.get_operation_stats.return_value = {
            'exchange.place_order': {
                'count': 10,
                'avg_duration': 150.0,
                'success_count': 9,
                'error_count': 1
            }
        }
        return collector
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Create mock performance monitor."""
        monitor = Mock(spec=PerformanceMonitor)
        monitor.get_health_status.return_value = HealthStatus(
            timestamp=datetime.utcnow(),
            overall_status="healthy",
            cpu_usage=45.0,
            memory_usage=60.0,
            disk_usage=30.0,
            active_connections=3,
            error_rate=0.5,
            trade_success_rate=95.0,
            issues=[]
        )
        return monitor
    
    @pytest.fixture
    def exporter(self, registry, mock_metrics_collector, mock_performance_monitor):
        """Create Prometheus exporter."""
        return PrometheusExporter(
            metrics_collector=mock_metrics_collector,
            performance_monitor=mock_performance_monitor,
            registry=registry
        )
    
    def test_initialization(self, exporter):
        """Test exporter initialization."""
        assert exporter.metrics_collector is not None
        assert exporter.performance_monitor is not None
        assert exporter.registry is not None
        
        # Check that metrics are initialized
        assert exporter.trades_total is not None
        assert exporter.system_cpu_usage is not None
        assert exporter.error_rate is not None
    
    def test_record_trade(self, exporter):
        """Test recording a trade."""
        exporter.record_trade(
            exchange="binance",
            symbol="BTC/USDT",
            side="buy",
            volume=1.5,
            pnl=100.0,
            strategy="test_strategy"
        )
        
        # Verify metrics were updated
        metrics = exporter.get_metrics().decode('utf-8')
        assert 'trading_bot_trades_total' in metrics
        assert 'exchange="binance"' in metrics
        assert 'symbol="BTC/USDT"' in metrics
    
    def test_record_order(self, exporter):
        """Test recording an order."""
        exporter.record_order(
            exchange="binance",
            symbol="BTC/USDT",
            side="buy",
            status="filled"
        )
        
        metrics = exporter.get_metrics().decode('utf-8')
        assert 'trading_bot_orders_total' in metrics
        assert 'status="filled"' in metrics
    
    def test_update_metrics(self, exporter, mock_performance_monitor):
        """Test updating metrics from data sources."""
        exporter.update_metrics()
        
        # Verify health status was queried
        mock_performance_monitor.get_health_status.assert_called_once()
        
        # Check that system metrics were updated
        metrics = exporter.get_metrics().decode('utf-8')
        assert 'trading_bot_system_cpu_usage_percent' in metrics
        assert 'trading_bot_system_memory_usage_percent' in metrics
    
    def test_background_updates(self, exporter):
        """Test background metric updates."""
        exporter.start_background_updates(interval_seconds=0.1)
        
        # Wait a bit for background thread to run
        import time
        time.sleep(0.2)
        
        exporter.stop_background_updates()
        
        # Verify updates occurred
        assert exporter.performance_monitor.get_health_status.call_count > 0


class TestNotificationSystem:
    """Test notification system."""
    
    @pytest.fixture
    def notification_system(self):
        """Create notification system."""
        return NotificationSystem()
    
    @pytest.fixture
    def mock_email_provider(self):
        """Create mock email provider."""
        provider = Mock(spec=EmailNotificationProvider)
        provider.is_configured.return_value = True
        provider.send_notification = AsyncMock(return_value=True)
        return provider
    
    @pytest.fixture
    def mock_slack_provider(self):
        """Create mock Slack provider."""
        provider = Mock(spec=SlackNotificationProvider)
        provider.is_configured.return_value = True
        provider.send_notification = AsyncMock(return_value=True)
        return provider
    
    def test_add_provider(self, notification_system, mock_email_provider):
        """Test adding a notification provider."""
        notification_system.add_provider(NotificationChannel.EMAIL, mock_email_provider)
        
        assert NotificationChannel.EMAIL in notification_system._providers
        assert notification_system._providers[NotificationChannel.EMAIL] == mock_email_provider
    
    def test_add_unconfigured_provider(self, notification_system):
        """Test adding an unconfigured provider."""
        provider = Mock(spec=EmailNotificationProvider)
        provider.is_configured.return_value = False
        
        notification_system.add_provider(NotificationChannel.EMAIL, provider)
        
        # Should not be added
        assert NotificationChannel.EMAIL not in notification_system._providers
    
    @pytest.mark.asyncio
    async def test_send_notification(self, notification_system, mock_email_provider):
        """Test sending a notification."""
        notification_system.add_provider(NotificationChannel.EMAIL, mock_email_provider)
        
        await notification_system.send_notification(
            title="Test Alert",
            message="This is a test",
            level=NotificationLevel.WARNING,
            channels=[NotificationChannel.EMAIL]
        )
        
        # Wait for async processing
        await asyncio.sleep(0.1)
        
        # Verify provider was called
        mock_email_provider.send_notification.assert_called_once()
    
    def test_send_system_alert(self, notification_system):
        """Test sending a system alert."""
        with patch.object(notification_system, 'send_notification') as mock_send:
            notification_system.send_system_alert(
                title="System Error",
                message="Critical system error occurred"
            )
            
            # Verify send_notification was called with correct parameters
            assert mock_send.called
    
    def test_rate_limiting(self, notification_system):
        """Test notification rate limiting."""
        # Set a low rate limit for testing
        notification_system._max_notifications_per_hour = 2
        
        event = NotificationEvent(
            title="Test",
            message="Test message",
            level=NotificationLevel.INFO,
            component="test"
        )
        
        # First two should not be rate limited
        assert not notification_system._is_rate_limited(event)
        assert not notification_system._is_rate_limited(event)
        
        # Third should be rate limited
        assert notification_system._is_rate_limited(event)


class TestEmailNotificationProvider:
    """Test email notification provider."""
    
    @pytest.fixture
    def email_provider(self):
        """Create email provider."""
        return EmailNotificationProvider(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="password",
            from_email="test@example.com",
            to_emails=["recipient@example.com"]
        )
    
    def test_is_configured(self, email_provider):
        """Test configuration check."""
        assert email_provider.is_configured()
        
        # Test with missing configuration
        incomplete_provider = EmailNotificationProvider(
            smtp_server="",
            smtp_port=587,
            username="test@example.com",
            password="password",
            from_email="test@example.com",
            to_emails=["recipient@example.com"]
        )
        assert not incomplete_provider.is_configured()
    
    @pytest.mark.asyncio
    async def test_send_notification(self, email_provider):
        """Test sending email notification."""
        event = NotificationEvent(
            title="Test Alert",
            message="This is a test notification",
            level=NotificationLevel.WARNING,
            component="test",
            metadata={"key": "value"}
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value = mock_server
            
            result = await email_provider.send_notification(event)
            
            assert result is True
            mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test@example.com", "password")
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
    
    def test_format_email_body(self, email_provider):
        """Test email body formatting."""
        event = NotificationEvent(
            title="Test Alert",
            message="This is a test",
            level=NotificationLevel.CRITICAL,
            component="trading",
            metadata={"symbol": "BTC/USDT", "price": 50000}
        )
        
        body = email_provider._format_email_body(event)
        
        assert "Test Alert" in body
        assert "This is a test" in body
        assert "CRITICAL" in body
        assert "trading" in body
        assert "BTC/USDT" in body
        assert "50000" in body


class TestSlackNotificationProvider:
    """Test Slack notification provider."""
    
    @pytest.fixture
    def slack_provider(self):
        """Create Slack provider."""
        return SlackNotificationProvider(
            webhook_url="https://hooks.slack.com/test",
            channel="#alerts",
            username="Trading Bot"
        )
    
    def test_is_configured(self, slack_provider):
        """Test configuration check."""
        assert slack_provider.is_configured()
        
        # Test with missing webhook URL
        incomplete_provider = SlackNotificationProvider(webhook_url="")
        assert not incomplete_provider.is_configured()
    
    @pytest.mark.asyncio
    async def test_send_notification(self, slack_provider):
        """Test sending Slack notification."""
        event = NotificationEvent(
            title="Test Alert",
            message="This is a test notification",
            level=NotificationLevel.ERROR,
            component="exchange"
        )
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await slack_provider.send_notification(event)
            
            assert result is True
    
    def test_create_slack_payload(self, slack_provider):
        """Test Slack payload creation."""
        event = NotificationEvent(
            title="Test Alert",
            message="This is a test",
            level=NotificationLevel.WARNING,
            component="strategy",
            metadata={"strategy": "RSI", "symbol": "ETH/USDT"}
        )
        
        payload = slack_provider._create_slack_payload(event)
        
        assert payload["username"] == "Trading Bot"
        assert payload["channel"] == "#alerts"
        assert len(payload["attachments"]) == 1
        
        attachment = payload["attachments"][0]
        assert attachment["title"] == "Test Alert"
        assert attachment["text"] == "This is a test"
        assert attachment["color"] == "#ff9500"  # Warning color


class TestConsoleNotificationProvider:
    """Test console notification provider."""
    
    @pytest.fixture
    def console_provider(self):
        """Create console provider."""
        return ConsoleNotificationProvider()
    
    def test_is_configured(self, console_provider):
        """Test configuration check."""
        assert console_provider.is_configured()
    
    @pytest.mark.asyncio
    async def test_send_notification(self, console_provider, capsys):
        """Test sending console notification."""
        event = NotificationEvent(
            title="Test Alert",
            message="This is a test notification",
            level=NotificationLevel.INFO,
            component="test",
            metadata={"key": "value"}
        )
        
        result = await console_provider.send_notification(event)
        
        assert result is True
        
        # Check console output
        captured = capsys.readouterr()
        assert "Test Alert" in captured.out
        assert "This is a test notification" in captured.out
        assert "INFO" in captured.out


class TestMetricsCollector:
    """Test metrics collector."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector."""
        return MetricsCollector(max_metrics=100)
    
    def test_record_operation(self, metrics_collector):
        """Test recording an operation."""
        metrics_collector.record_operation(
            component="exchange",
            operation="place_order",
            duration_ms=150.0,
            success=True,
            metadata={"symbol": "BTC/USDT"}
        )
        
        # Check that metric was recorded
        assert len(metrics_collector._metrics) == 1
        
        # Check operation stats
        stats = metrics_collector.get_operation_stats("exchange", "place_order")
        assert "exchange.place_order" in stats
        assert stats["exchange.place_order"]["count"] == 1
        assert stats["exchange.place_order"]["avg_duration"] == 150.0
    
    def test_performance_timer(self, metrics_collector):
        """Test performance timer context manager."""
        with metrics_collector.create_performance_timer("test", "operation") as timer:
            import time
            time.sleep(0.01)  # Small delay
        
        # Check that metric was recorded
        assert len(metrics_collector._metrics) == 1
        
        metric = list(metrics_collector._metrics)[0]
        assert metric.component == "test"
        assert metric.operation == "operation"
        assert metric.duration_ms > 0
        assert metric.success is True
    
    def test_performance_timer_with_error(self, metrics_collector):
        """Test performance timer with exception."""
        try:
            with metrics_collector.create_performance_timer("test", "operation") as timer:
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Check that error was recorded
        assert len(metrics_collector._metrics) == 1
        
        metric = list(metrics_collector._metrics)[0]
        assert metric.success is False
        assert metric.error_message == "Test error"
    
    def test_get_performance_summary(self, metrics_collector):
        """Test performance summary generation."""
        # Record some operations
        metrics_collector.record_operation("test", "op1", 100.0, True)
        metrics_collector.record_operation("test", "op2", 200.0, False, "Error")
        metrics_collector.record_operation("test", "op1", 150.0, True)
        
        summary = metrics_collector.get_performance_summary()
        
        assert summary["total_operations"] == 3
        assert summary["total_errors"] == 1
        assert summary["success_rate"] == pytest.approx(66.67, rel=1e-2)
        assert len(summary["slowest_operations"]) > 0
        assert len(summary["error_prone_operations"]) > 0


class TestPerformanceMonitor:
    """Test performance monitor."""
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()
    
    def test_get_health_status(self, performance_monitor):
        """Test health status retrieval."""
        health_status = performance_monitor.get_health_status()
        
        assert isinstance(health_status, HealthStatus)
        assert health_status.overall_status in ["healthy", "warning", "critical"]
        assert health_status.cpu_usage >= 0
        assert health_status.memory_usage >= 0
        assert health_status.disk_usage >= 0
    
    def test_update_connection_count(self, performance_monitor):
        """Test updating connection count."""
        performance_monitor.update_connection_count(5)
        assert performance_monitor._active_connections == 5
    
    def test_create_performance_timer(self, performance_monitor):
        """Test creating performance timer."""
        timer = performance_monitor.create_performance_timer("test", "operation")
        assert isinstance(timer, PerformanceTimer)
    
    def test_monitoring_lifecycle(self, performance_monitor):
        """Test starting and stopping monitoring."""
        performance_monitor.start_monitoring(interval_seconds=0.1)
        assert performance_monitor._monitoring_active is True
        
        # Wait a bit
        import time
        time.sleep(0.2)
        
        performance_monitor.stop_monitoring()
        assert performance_monitor._monitoring_active is False


@pytest.mark.integration
class TestMonitoringIntegration:
    """Integration tests for monitoring components."""
    
    @pytest.fixture
    def integrated_system(self):
        """Create integrated monitoring system."""
        metrics_collector = MetricsCollector()
        performance_monitor = PerformanceMonitor(metrics_collector=metrics_collector)
        notification_system = NotificationSystem()
        
        # Add console provider for testing
        console_provider = ConsoleNotificationProvider()
        notification_system.add_provider(NotificationChannel.CONSOLE, console_provider)
        
        return {
            'metrics_collector': metrics_collector,
            'performance_monitor': performance_monitor,
            'notification_system': notification_system
        }
    
    def test_end_to_end_monitoring(self, integrated_system):
        """Test end-to-end monitoring workflow."""
        metrics_collector = integrated_system['metrics_collector']
        performance_monitor = integrated_system['performance_monitor']
        notification_system = integrated_system['notification_system']
        
        # Record some operations
        with metrics_collector.create_performance_timer("exchange", "place_order"):
            import time
            time.sleep(0.01)
        
        # Get health status
        health_status = performance_monitor.get_health_status()
        assert health_status is not None
        
        # Send notification based on health status
        if health_status.overall_status != "healthy":
            asyncio.run(notification_system.send_notification(
                title="Health Check Alert",
                message=f"System status: {health_status.overall_status}",
                level=NotificationLevel.WARNING
            ))
        
        # Verify metrics were collected
        stats = metrics_collector.get_operation_stats()
        assert "exchange.place_order" in stats
        assert stats["exchange.place_order"]["count"] == 1