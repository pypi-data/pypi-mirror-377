"""
Tests for logging and monitoring functionality.
"""
import json
import logging
import tempfile
import threading
import time
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from config.logging import (
    setup_logging, get_logger, get_trade_logger, get_performance_logger,
    get_error_logger, LogContext, StructuredJSONFormatter, TradingBotFilter
)
from src.monitoring import (
    MetricsCollector, PerformanceMetrics, PerformanceTimer,
    ErrorTracker, ErrorEvent, ErrorContext,
    TradeLogger, TradeEvent, PositionSnapshot,
    PerformanceMonitor, HealthStatus
)


class TestStructuredLogging:
    """Test structured logging functionality."""
    
    def test_log_context_creation(self):
        """Test LogContext creation and usage."""
        context = LogContext(
            component="test_component",
            operation="test_operation",
            symbol="BTC/USD",
            exchange="binance"
        )
        
        assert context.component == "test_component"
        assert context.operation == "test_operation"
        assert context.symbol == "BTC/USD"
        assert context.exchange == "binance"
    
    def test_structured_json_formatter(self):
        """Test JSON formatter output."""
        formatter = StructuredJSONFormatter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add context
        record.context = LogContext(component="test", operation="format")
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse JSON
        log_data = json.loads(formatted)
        
        assert log_data['level'] == 'INFO'
        assert log_data['message'] == 'Test message'
        assert log_data['logger'] == 'test_logger'
        assert 'timestamp' in log_data
        assert 'context' in log_data
        assert log_data['context']['component'] == 'test'
    
    def test_structured_json_formatter_with_exception(self):
        """Test JSON formatter with exception information."""
        formatter = StructuredJSONFormatter()
        
        try:
            raise ValueError("Test error")
        except ValueError:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=True
            )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert 'exception' in log_data
        assert log_data['exception']['type'] == 'ValueError'
        assert log_data['exception']['message'] == 'Test error'
        assert 'traceback' in log_data['exception']
    
    def test_trading_bot_filter(self):
        """Test custom trading bot filter."""
        filter_obj = TradingBotFilter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Filter should add session_id
        result = filter_obj.filter(record)
        
        assert result is True
        assert hasattr(record, 'session_id')
    
    def test_contextual_logger(self):
        """Test contextual logger functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(log_file=str(log_file), log_format="json")
            
            context = LogContext(component="test", operation="logging")
            logger = get_logger("test_logger", context)
            
            logger.info("Test message")
            
            # Verify log file was created
            assert log_file.exists()
            
            # Read and verify log content
            with open(log_file, 'r') as f:
                log_line = f.readline().strip()
                log_data = json.loads(log_line)
                
                assert log_data['message'] == 'Test message'
                assert 'context' in log_data
    
    def test_contextual_logger_with_context_update(self):
        """Test contextual logger with context updates."""
        context = LogContext(component="test", operation="logging")
        logger = get_logger("test_logger", context)
        
        # Create new logger with updated context
        updated_logger = logger.with_context(symbol="BTC/USD", exchange="binance")
        
        assert updated_logger.context.symbol == "BTC/USD"
        assert updated_logger.context.exchange == "binance"
        assert updated_logger.context.component == "test"  # Original value preserved


class TestMetricsCollector:
    """Test metrics collection functionality."""
    
    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            collector = MetricsCollector(max_metrics=100, storage_path=temp_dir)
            
            assert collector.max_metrics == 100
            assert collector.storage_path == Path(temp_dir)
    
    def test_record_operation_metric(self):
        """Test recording operation metrics."""
        collector = MetricsCollector(max_metrics=100)
        
        collector.record_operation(
            component="exchange",
            operation="place_order",
            duration_ms=150.5,
            success=True,
            symbol="BTC/USD"
        )
        
        # Check operation stats
        stats = collector.get_operation_stats("exchange", "place_order")
        key = "exchange.place_order"
        
        assert key in stats
        assert stats[key]['count'] == 1
        assert stats[key]['success_count'] == 1
        assert stats[key]['avg_duration'] == 150.5
    
    def test_record_system_metrics(self):
        """Test recording system metrics."""
        collector = MetricsCollector(max_metrics=100)
        
        collector.record_system_metrics(
            cpu_usage=45.2,
            memory_usage=67.8,
            active_threads=12,
            open_connections=5,
            pending_orders=3,
            active_positions=2
        )
        
        # Get recent system metrics
        metrics = collector.get_system_metrics(minutes=1)
        
        assert len(metrics) == 1
        assert metrics[0].cpu_usage == 45.2
        assert metrics[0].memory_usage == 67.8
    
    def test_performance_timer(self):
        """Test performance timer context manager."""
        collector = MetricsCollector(max_metrics=100)
        
        with PerformanceTimer(collector, "test", "operation") as timer:
            time.sleep(0.01)  # Small delay
        
        stats = collector.get_operation_stats("test", "operation")
        key = "test.operation"
        
        assert key in stats
        assert stats[key]['count'] == 1
        assert stats[key]['avg_duration'] > 0
    
    def test_performance_timer_with_error(self):
        """Test performance timer with error handling."""
        collector = MetricsCollector(max_metrics=100)
        
        with pytest.raises(ValueError):
            with PerformanceTimer(collector, "test", "operation") as timer:
                raise ValueError("Test error")
        
        stats = collector.get_operation_stats("test", "operation")
        key = "test.operation"
        
        assert key in stats
        assert stats[key]['count'] == 1
        assert stats[key]['error_count'] == 1
    
    def test_get_performance_summary(self):
        """Test performance summary generation."""
        collector = MetricsCollector(max_metrics=100)
        
        # Record some metrics
        collector.record_operation("test", "op1", 100, True)
        collector.record_operation("test", "op2", 200, False)
        collector.record_operation("test", "op1", 150, True)
        
        summary = collector.get_performance_summary()
        
        assert summary['total_operations'] == 3
        assert summary['total_errors'] == 1
        assert summary['success_rate'] > 0


class TestErrorTracker:
    """Test error tracking functionality."""
    
    def test_error_tracker_initialization(self):
        """Test ErrorTracker initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ErrorTracker(max_errors=100, storage_path=temp_dir)
            
            assert tracker.max_errors == 100
            assert tracker.storage_path == Path(temp_dir)
    
    def test_track_error(self):
        """Test error tracking."""
        tracker = ErrorTracker(max_errors=100)
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error_id = tracker.track_error(
                component="test",
                operation="test_op",
                error=e,
                context={"symbol": "BTC/USD"}
            )
        
        assert error_id is not None
        
        # Check error stats
        stats = tracker.get_error_stats("ValueError")
        
        assert "ValueError" in stats
        assert stats["ValueError"]["count"] == 1
    
    def test_track_custom_error(self):
        """Test custom error tracking."""
        tracker = ErrorTracker(max_errors=100)
        
        error_id = tracker.track_custom_error(
            component="test",
            operation="test_op",
            error_type="CustomError",
            error_message="Custom error message",
            severity="WARNING"
        )
        
        assert error_id is not None
        
        stats = tracker.get_error_stats("CustomError")
        assert "CustomError" in stats
    
    def test_error_context_manager(self):
        """Test error context manager."""
        tracker = ErrorTracker(max_errors=100)
        
        with pytest.raises(ValueError):
            with ErrorContext(tracker, "test", "operation"):
                raise ValueError("Test error")
        
        # Check that error was tracked
        recent_errors = tracker.get_recent_errors(minutes=1)
        assert len(recent_errors) == 1
        assert recent_errors[0].error_type == "ValueError"
    
    def test_get_error_trends(self):
        """Test error trend analysis."""
        tracker = ErrorTracker(max_errors=100)
        
        # Track some errors
        tracker.track_custom_error("test", "op1", "Error1", "Message 1")
        tracker.track_custom_error("test", "op2", "Error2", "Message 2")
        tracker.track_custom_error("test", "op1", "Error1", "Message 3")
        
        trends = tracker.get_error_trends(hours=1)
        
        assert trends['total_errors'] == 3
        assert len(trends['top_error_types']) > 0
        assert trends['top_error_types'][0][0] == "Error1"  # Most frequent
    
    def test_mark_error_resolved(self):
        """Test marking errors as resolved."""
        tracker = ErrorTracker(max_errors=100)
        
        error_id = tracker.track_custom_error(
            "test", "op", "TestError", "Test message"
        )
        
        # Mark as resolved
        result = tracker.mark_error_resolved(error_id, "Fixed by update")
        assert result is True
        
        # Check unresolved errors
        unresolved = tracker.get_unresolved_errors()
        assert len(unresolved) == 0


class TestTradeLogger:
    """Test trade logging functionality."""
    
    def test_trade_logger_initialization(self):
        """Test TradeLogger initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = TradeLogger(max_events=100, storage_path=temp_dir)
            
            assert logger.max_events == 100
            assert logger.storage_path == Path(temp_dir)
    
    def test_log_order_placed(self):
        """Test order placement logging."""
        logger = TradeLogger(max_events=100)
        
        logger.log_order_placed(
            symbol="BTC/USD",
            exchange="binance",
            strategy="test_strategy",
            order_id="order_123",
            side="buy",
            quantity=Decimal("0.1"),
            price=Decimal("50000")
        )
        
        history = logger.get_trade_history(hours=1)
        assert len(history) == 1
        assert history[0].event_type == "order_placed"
        assert history[0].symbol == "BTC/USD"
    
    def test_log_order_filled(self):
        """Test order fill logging."""
        logger = TradeLogger(max_events=100)
        
        logger.log_order_filled(
            symbol="BTC/USD",
            exchange="binance",
            strategy="test_strategy",
            order_id="order_123",
            trade_id="trade_456",
            side="buy",
            quantity=Decimal("0.1"),
            price=Decimal("50000"),
            fee=Decimal("5.0"),
            fee_currency="USD"
        )
        
        history = logger.get_trade_history(hours=1)
        assert len(history) == 1
        assert history[0].event_type == "order_filled"
        assert history[0].fee == Decimal("5.0")
    
    def test_log_position_opened_closed(self):
        """Test position logging."""
        logger = TradeLogger(max_events=100)
        
        # Open position
        logger.log_position_opened(
            symbol="BTC/USD",
            exchange="binance",
            strategy="test_strategy",
            size=Decimal("0.1"),
            entry_price=Decimal("50000")
        )
        
        # Check active positions
        positions = logger.get_active_positions()
        assert len(positions) == 1
        assert positions[0].symbol == "BTC/USD"
        
        # Close position
        logger.log_position_closed(
            symbol="BTC/USD",
            exchange="binance",
            strategy="test_strategy",
            size=Decimal("0.1"),
            exit_price=Decimal("51000"),
            pnl=Decimal("100"),
            portfolio_value=Decimal("10100")
        )
        
        # Check positions are cleared
        positions = logger.get_active_positions()
        assert len(positions) == 0
        
        # Check strategy performance
        performance = logger.get_strategy_performance("test_strategy")
        assert performance['total_trades'] == '1'
        assert performance['winning_trades'] == '1'
    
    def test_get_trading_summary(self):
        """Test trading summary generation."""
        logger = TradeLogger(max_events=100)
        
        # Log some events
        logger.log_order_placed("BTC/USD", "binance", "strategy1", "order1", "buy", Decimal("0.1"), Decimal("50000"))
        logger.log_order_filled("BTC/USD", "binance", "strategy1", "order1", "trade1", "buy", Decimal("0.1"), Decimal("50000"), Decimal("5"), "USD")
        
        summary = logger.get_trading_summary()
        
        assert summary['total_events'] == 2
        assert 'order_placed' in summary['event_type_distribution']
        assert 'order_filled' in summary['event_type_distribution']


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""
    
    def test_performance_monitor_initialization(self):
        """Test PerformanceMonitor initialization."""
        monitor = PerformanceMonitor()
        
        assert monitor.metrics_collector is not None
        assert monitor.error_tracker is not None
        assert monitor.trade_logger is not None
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_health_status(self, mock_disk, mock_memory, mock_cpu):
        """Test health status checking."""
        # Mock system metrics
        mock_cpu.return_value = 45.0
        mock_memory.return_value = Mock(percent=60.0)
        mock_disk.return_value = Mock(used=500, total=1000)
        
        monitor = PerformanceMonitor()
        health = monitor.get_health_status()
        
        assert health.overall_status == "healthy"
        assert health.cpu_usage == 45.0
        assert health.memory_usage == 60.0
        assert health.disk_usage == 50.0
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_health_status_with_issues(self, mock_disk, mock_memory, mock_cpu):
        """Test health status with performance issues."""
        # Mock high resource usage
        mock_cpu.return_value = 95.0
        mock_memory.return_value = Mock(percent=90.0)
        mock_disk.return_value = Mock(used=950, total=1000)
        
        monitor = PerformanceMonitor()
        health = monitor.get_health_status()
        
        assert health.overall_status in ["warning", "critical"]
        assert len(health.issues) > 0
    
    def test_create_performance_timer(self):
        """Test performance timer creation."""
        monitor = PerformanceMonitor()
        
        timer = monitor.create_performance_timer("test", "operation")
        assert isinstance(timer, PerformanceTimer)
    
    def test_create_error_context(self):
        """Test error context creation."""
        monitor = PerformanceMonitor()
        
        context = monitor.create_error_context("test", "operation")
        assert isinstance(context, ErrorContext)
    
    def test_alert_thresholds(self):
        """Test alert threshold management."""
        monitor = PerformanceMonitor()
        
        # Get default thresholds
        thresholds = monitor.get_alert_thresholds()
        assert 'cpu_usage' in thresholds
        
        # Set new threshold
        monitor.set_alert_threshold('cpu_usage', 90.0)
        updated_thresholds = monitor.get_alert_thresholds()
        assert updated_thresholds['cpu_usage'] == 90.0
    
    def test_connection_tracking(self):
        """Test connection and position tracking."""
        monitor = PerformanceMonitor()
        
        monitor.update_connection_count(5)
        monitor.update_pending_orders(3)
        monitor.update_active_positions(2)
        
        assert monitor._active_connections == 5
        assert monitor._pending_orders == 3
        assert monitor._active_positions == 2
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_performance_report(self, mock_disk, mock_memory, mock_cpu):
        """Test performance report generation."""
        # Mock system metrics
        mock_cpu.return_value = 45.0
        mock_memory.return_value = Mock(percent=60.0)
        mock_disk.return_value = Mock(used=500, total=1000)
        
        monitor = PerformanceMonitor()
        report = monitor.get_performance_report(hours=1)
        
        assert 'report_timestamp' in report
        assert 'health_status' in report
        assert 'performance_metrics' in report
        assert 'error_analysis' in report
        assert 'trading_activity' in report


class TestIntegration:
    """Integration tests for logging and monitoring."""
    
    def test_full_logging_pipeline(self):
        """Test complete logging pipeline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup logging
            log_file = Path(temp_dir) / "test.log"
            setup_logging(log_file=str(log_file), log_format="json")
            
            # Create loggers
            trade_logger = get_trade_logger()
            performance_logger = get_performance_logger()
            error_logger = get_error_logger()
            
            # Log various events
            trade_logger.info("Trade executed", extra={'symbol': 'BTC/USD'})
            performance_logger.info("Performance metric", extra={'duration': 150})
            error_logger.error("Error occurred", extra={'error_type': 'ValueError'})
            
            # Verify log file exists and contains data
            assert log_file.exists()
            
            with open(log_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) >= 3
                
                # Verify JSON format
                for line in lines:
                    log_data = json.loads(line.strip())
                    assert 'timestamp' in log_data
                    assert 'level' in log_data
                    assert 'message' in log_data
    
    def test_monitoring_integration(self):
        """Test integration between monitoring components."""
        monitor = PerformanceMonitor()
        
        # Record some metrics
        with monitor.create_performance_timer("test", "operation"):
            time.sleep(0.01)
        
        # Track an error
        with pytest.raises(ValueError):
            with monitor.create_error_context("test", "operation"):
                raise ValueError("Test error")
        
        # Log a trade
        monitor.trade_logger.log_order_placed(
            "BTC/USD", "binance", "test", "order1", "buy", Decimal("0.1"), Decimal("50000")
        )
        
        # Generate performance report
        report = monitor.get_performance_report(hours=1)
        
        assert report['performance_metrics']['total_operations'] >= 1
        assert report['error_analysis']['total_errors'] >= 1
        assert report['trading_activity']['total_events'] >= 1


if __name__ == "__main__":
    pytest.main([__file__])