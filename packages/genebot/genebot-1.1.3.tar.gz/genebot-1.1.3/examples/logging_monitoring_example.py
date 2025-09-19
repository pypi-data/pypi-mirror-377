"""
Example demonstrating comprehensive logging and monitoring functionality.
"""
import time
from decimal import Decimal
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.logging import setup_logging, get_logger, LogContext
from src.monitoring import (
    MetricsCollector, ErrorTracker, TradeLogger, PerformanceMonitor, ErrorContext
)


def main():
    """Demonstrate logging and monitoring features."""
    print("=== Trading Bot Logging and Monitoring Example ===\n")
    
    # Setup structured logging
    setup_logging(
        log_level="INFO",
        log_format="json",
        log_file="logs/example.log",
        enable_structured_logging=True
    )
    
    # Create logger with context
    context = LogContext(
        component="example",
        operation="demonstration",
        symbol="BTC/USD",
        exchange="binance"
    )
    logger = get_logger("trading_bot.example", context)
    
    print("1. Structured Logging Example")
    print("=" * 40)
    
    # Log various message types
    logger.info("Starting trading bot example")
    logger.debug("Debug information", extra={'debug_data': {'key': 'value'}})
    logger.warning("This is a warning message")
    
    # Log with updated context
    updated_logger = logger.with_context(strategy="moving_average")
    updated_logger.info("Strategy initialized", extra={'parameters': {'period': 20}})
    
    print("✓ Structured logs written to logs/example.log\n")
    
    # Initialize monitoring components
    print("2. Performance Metrics Collection")
    print("=" * 40)
    
    metrics_collector = MetricsCollector(max_metrics=1000)
    
    # Record some operation metrics
    metrics_collector.record_operation(
        component="exchange",
        operation="place_order",
        duration_ms=125.5,
        success=True,
        symbol="BTC/USD",
        order_type="market"
    )
    
    metrics_collector.record_operation(
        component="strategy",
        operation="calculate_signal",
        duration_ms=45.2,
        success=True,
        strategy="moving_average"
    )
    
    # Use performance timer
    with metrics_collector.create_performance_timer("example", "timed_operation") as timer:
        time.sleep(0.1)  # Simulate work
        print("✓ Timed operation completed")
    
    # Record system metrics
    metrics_collector.record_system_metrics(
        cpu_usage=45.2,
        memory_usage=67.8,
        active_threads=12,
        open_connections=5,
        pending_orders=3,
        active_positions=2
    )
    
    # Display metrics summary
    summary = metrics_collector.get_performance_summary()
    print(f"✓ Total operations recorded: {summary['total_operations']}")
    print(f"✓ Success rate: {summary['success_rate']:.1f}%\n")
    
    print("3. Error Tracking")
    print("=" * 40)
    
    error_tracker = ErrorTracker(max_errors=1000)
    
    # Track a custom error
    error_id = error_tracker.track_custom_error(
        component="exchange",
        operation="connect",
        error_type="ConnectionError",
        error_message="Failed to connect to exchange API",
        context={"exchange": "binance", "retry_count": 3},
        severity="ERROR"
    )
    print(f"✓ Error tracked with ID: {error_id}")
    
    # Use error context manager
    try:
        with ErrorContext(error_tracker, "example", "error_demo"):
            raise ValueError("This is a demonstration error")
    except ValueError:
        pass  # Error was automatically tracked
    
    # Display error statistics
    error_stats = error_tracker.get_error_stats()
    print(f"✓ Error types tracked: {len(error_stats)}")
    
    # Get error trends
    trends = error_tracker.get_error_trends(hours=1)
    print(f"✓ Total errors in last hour: {trends['total_errors']}\n")
    
    print("4. Trade Execution Logging")
    print("=" * 40)
    
    trade_logger = TradeLogger(max_events=10000)
    
    # Log order placement
    trade_logger.log_order_placed(
        symbol="BTC/USD",
        exchange="binance",
        strategy="moving_average",
        order_id="order_12345",
        side="buy",
        quantity=Decimal("0.1"),
        price=Decimal("50000"),
        order_type="market"
    )
    print("✓ Order placement logged")
    
    # Log order fill
    trade_logger.log_order_filled(
        symbol="BTC/USD",
        exchange="binance",
        strategy="moving_average",
        order_id="order_12345",
        trade_id="trade_67890",
        side="buy",
        quantity=Decimal("0.1"),
        price=Decimal("50050"),
        fee=Decimal("5.0"),
        fee_currency="USD"
    )
    print("✓ Order fill logged")
    
    # Log position opening
    trade_logger.log_position_opened(
        symbol="BTC/USD",
        exchange="binance",
        strategy="moving_average",
        size=Decimal("0.1"),
        entry_price=Decimal("50050")
    )
    print("✓ Position opening logged")
    
    # Simulate position update
    trade_logger.update_position(
        symbol="BTC/USD",
        exchange="binance",
        strategy="moving_average",
        current_price=Decimal("51000"),
        unrealized_pnl=Decimal("95")
    )
    
    # Log position closing
    trade_logger.log_position_closed(
        symbol="BTC/USD",
        exchange="binance",
        strategy="moving_average",
        size=Decimal("0.1"),
        exit_price=Decimal("51000"),
        pnl=Decimal("95"),
        portfolio_value=Decimal("10095")
    )
    print("✓ Position closing logged")
    
    # Display trading summary
    trading_summary = trade_logger.get_trading_summary()
    print(f"✓ Total trade events: {trading_summary['total_events']}")
    
    # Display strategy performance
    performance = trade_logger.get_strategy_performance("moving_average")
    if performance:
        print(f"✓ Strategy trades: {performance['total_trades']}")
        print(f"✓ Strategy PnL: {performance['total_pnl']}\n")
    
    print("5. Comprehensive Performance Monitoring")
    print("=" * 40)
    
    # Create performance monitor with all components
    monitor = PerformanceMonitor(
        metrics_collector=metrics_collector,
        error_tracker=error_tracker,
        trade_logger=trade_logger
    )
    
    # Update connection tracking
    monitor.update_connection_count(5)
    monitor.update_pending_orders(2)
    monitor.update_active_positions(1)
    
    # Get health status
    health = monitor.get_health_status()
    print(f"✓ System health: {health.overall_status}")
    print(f"✓ CPU usage: {health.cpu_usage:.1f}%")
    print(f"✓ Memory usage: {health.memory_usage:.1f}%")
    print(f"✓ Error rate: {health.error_rate:.2f} errors/min")
    print(f"✓ Trade success rate: {health.trade_success_rate:.1f}%")
    
    if health.issues:
        print(f"⚠ Issues detected: {', '.join(health.issues)}")
    
    # Generate comprehensive performance report
    print("\n6. Performance Report Generation")
    print("=" * 40)
    
    report = monitor.get_performance_report(hours=1)
    print(f"✓ Report generated for last {report['report_period_hours']} hour(s)")
    print(f"✓ Health status: {report['health_status']['overall_status']}")
    print(f"✓ Total operations: {report['performance_metrics']['total_operations']}")
    print(f"✓ Total errors: {report['error_analysis']['total_errors']}")
    print(f"✓ Trading events: {report['trading_activity']['total_events']}")
    
    # Demonstrate alert threshold management
    print("\n7. Alert Threshold Management")
    print("=" * 40)
    
    # Get current thresholds
    thresholds = monitor.get_alert_thresholds()
    print("Current alert thresholds:")
    for metric, threshold in thresholds.items():
        print(f"  {metric}: {threshold}")
    
    # Update a threshold
    monitor.set_alert_threshold('cpu_usage', 90.0)
    print("✓ CPU usage threshold updated to 90%")
    
    print("\n8. Context Managers for Automatic Tracking")
    print("=" * 40)
    
    # Use performance timer context manager
    with monitor.create_performance_timer("example", "context_demo", demo=True):
        time.sleep(0.05)
        print("✓ Operation timed automatically")
    
    # Use error context manager (will catch and track errors)
    try:
        with monitor.create_error_context("example", "error_context_demo"):
            # This error will be automatically tracked
            raise RuntimeError("Demonstration error for context manager")
    except RuntimeError:
        print("✓ Error automatically tracked by context manager")
    
    print("\n=== Example Complete ===")
    print("\nCheck the following files for logged data:")
    print("- logs/example.log (structured JSON logs)")
    print("- logs/trades/ (trade execution logs)")
    print("- logs/errors/ (error tracking data)")
    print("- logs/metrics/ (performance metrics)")
    
    print("\nKey Features Demonstrated:")
    print("✓ Structured JSON logging with context")
    print("✓ Performance metrics collection and analysis")
    print("✓ Comprehensive error tracking and trends")
    print("✓ Trade execution audit trail")
    print("✓ System health monitoring")
    print("✓ Automated performance reporting")
    print("✓ Context managers for automatic tracking")


if __name__ == "__main__":
    main()