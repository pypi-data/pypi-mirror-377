#!/usr/bin/env python3
"""
Multi-Market Monitoring Example

This example demonstrates the enhanced monitoring capabilities for multi-market operations:
- Market-specific metrics collection
- Cross-market correlation monitoring
- Market session transition alerts
- Regulatory compliance monitoring
- Real-time alerting and notifications

Usage:
    python examples/multi_market_monitoring_example.py
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.monitoring.multi_market_monitor import MultiMarketMonitor, AlertType
from src.monitoring.notification_system import NotificationLevel
from src.markets.types import MarketType
from src.compliance.compliance_manager import ComplianceCheck, ComplianceStatus
from config.logging import setup_logging


class MultiMarketMonitoringDemo:
    """Demonstration of multi-market monitoring capabilities."""
    
    def __init__(self):
        """Initialize the monitoring demo."""
        self.logger = logging.getLogger(__name__)
        
        # Configuration for multi-market monitoring
        self.config = {
            'base_monitoring': {
                'monitoring_interval': 60,
                'prometheus_interval': 30,
                'max_metrics': 10000,
                'metrics_storage_path': 'logs/metrics'
            },
            'session_config_path': 'config/sessions.yaml',
            'correlation': {
                'correlation_lookback_days': 30,
                'min_data_points': 10
            },
            'compliance': {
                'rules': {
                    'crypto': {
                        'max_position_size': 10000,
                        'max_leverage': 3
                    },
                    'forex': {
                        'max_position_size': 50000,
                        'max_leverage': 50
                    }
                },
                'jurisdictions': ['US'],
                'max_total_exposure': 100000,
                'max_single_position_concentration': 0.2
            },
            'monitoring_interval': 30,  # seconds
            'correlation_alert_threshold': 0.8,
            'session_alerts_enabled': True,
            'compliance_alerts_enabled': True,
            'notifications': {
                'max_notifications_per_hour': 100,
                'console': {'enabled': True},
                'email': {'enabled': False},
                'slack': {'enabled': False}
            }
        }
        
        self.monitor = None
    
    async def run_demo(self):
        """Run the multi-market monitoring demonstration."""
        self.logger.info("Starting Multi-Market Monitoring Demo")
        
        try:
            # Initialize monitoring system
            await self._initialize_monitoring()
            
            # Demonstrate various monitoring scenarios
            await self._demo_market_metrics()
            await self._demo_session_transitions()
            await self._demo_correlation_monitoring()
            await self._demo_compliance_monitoring()
            await self._demo_cross_market_alerts()
            
            # Show monitoring dashboard
            await self._show_monitoring_dashboard()
            
            # Run monitoring for a period
            await self._run_monitoring_period()
            
        except Exception as e:
            self.logger.error(f"Demo failed: {e}", exc_info=True)
        finally:
            if self.monitor:
                await self.monitor.stop_monitoring()
            self.logger.info("Multi-Market Monitoring Demo completed")
    
    async def _initialize_monitoring(self):
        """Initialize the multi-market monitoring system."""
        self.logger.info("Initializing multi-market monitoring system...")
        
        # Create monitor instance
        self.monitor = MultiMarketMonitor(self.config)
        
        # Start monitoring
        await self.monitor.start_monitoring()
        
        self.logger.info("Multi-market monitoring system initialized")
    
    async def _demo_market_metrics(self):
        """Demonstrate market-specific metrics collection."""
        self.logger.info("=== Market Metrics Demo ===")
        
        # Simulate updating market metrics
        await self.monitor._update_market_metrics()
        
        # Display current metrics
        crypto_metrics = self.monitor.get_market_metrics(MarketType.CRYPTO)
        forex_metrics = self.monitor.get_market_metrics(MarketType.FOREX)
        
        print("\n📊 Current Market Metrics:")
        print(f"Crypto Market:")
        print(f"  - Active: {crypto_metrics.get('is_active', 'N/A')}")
        print(f"  - Symbols: {crypto_metrics.get('active_symbols', 'N/A')}")
        print(f"  - 24h Volume: ${crypto_metrics.get('total_volume_24h', 0):,.2f}")
        print(f"  - Error Rate: {crypto_metrics.get('error_rate', 0):.3%}")
        print(f"  - Latency: {crypto_metrics.get('latency_ms', 0):.1f}ms")
        
        print(f"\nForex Market:")
        print(f"  - Active: {forex_metrics.get('is_active', 'N/A')}")
        print(f"  - Symbols: {forex_metrics.get('active_symbols', 'N/A')}")
        print(f"  - 24h Volume: ${forex_metrics.get('total_volume_24h', 0):,.2f}")
        print(f"  - Error Rate: {forex_metrics.get('error_rate', 0):.3%}")
        print(f"  - Latency: {forex_metrics.get('latency_ms', 0):.1f}ms")
        
        await asyncio.sleep(2)
    
    async def _demo_session_transitions(self):
        """Demonstrate session transition monitoring."""
        self.logger.info("=== Session Transition Demo ===")
        
        print("\n🕐 Session Transition Monitoring:")
        print("Monitoring forex market sessions for transitions...")
        
        # Simulate session transition alert
        await self.monitor._send_alert(
            AlertType.SESSION_TRANSITION,
            "London Session Opening",
            "London forex session is now open for trading",
            NotificationLevel.INFO,
            [MarketType.FOREX],
            {
                'session_name': 'london',
                'transition': 'closed -> open',
                'next_close': (datetime.utcnow() + timedelta(hours=8)).isoformat()
            }
        )
        
        print("✅ Session transition alert generated")
        await asyncio.sleep(2)
    
    async def _demo_correlation_monitoring(self):
        """Demonstrate cross-market correlation monitoring."""
        self.logger.info("=== Correlation Monitoring Demo ===")
        
        print("\n📈 Cross-Market Correlation Monitoring:")
        
        # Simulate high correlation detection
        correlation_data = {
            'symbol1': 'BTC/USD',
            'symbol2': 'EUR/USD',
            'correlation': 0.87,
            'confidence': 0.92,
            'data_points': 150,
            'market1': 'crypto',
            'market2': 'forex'
        }
        
        await self.monitor._send_correlation_alert(
            "High Cross-Market Correlation Detected",
            f"Correlation between {correlation_data['symbol1']} and {correlation_data['symbol2']} "
            f"has reached {correlation_data['correlation']:.3f}",
            NotificationLevel.WARNING,
            correlation_data
        )
        
        print(f"⚠️  High correlation detected: {correlation_data['symbol1']} ↔ {correlation_data['symbol2']}")
        print(f"   Correlation: {correlation_data['correlation']:.3f}")
        print(f"   Confidence: {correlation_data['confidence']:.3f}")
        
        await asyncio.sleep(2)
    
    async def _demo_compliance_monitoring(self):
        """Demonstrate regulatory compliance monitoring."""
        self.logger.info("=== Compliance Monitoring Demo ===")
        
        print("\n⚖️  Regulatory Compliance Monitoring:")
        
        # Simulate compliance violation
        await self.monitor._send_alert(
            AlertType.COMPLIANCE_VIOLATION,
            "Position Size Limit Violation",
            "Crypto position size exceeds regulatory limit of $10,000",
            NotificationLevel.CRITICAL,
            [MarketType.CRYPTO],
            {
                'rule_id': 'position_size_limit',
                'severity': 'high',
                'current_size': 15000,
                'limit': 10000,
                'action_required': 'Reduce position size immediately'
            }
        )
        
        print("🚨 Compliance violation detected:")
        print("   Rule: Position Size Limit")
        print("   Market: Crypto")
        print("   Severity: High")
        print("   Action: Reduce position size")
        
        await asyncio.sleep(2)
    
    async def _demo_cross_market_alerts(self):
        """Demonstrate various cross-market alerts."""
        self.logger.info("=== Cross-Market Alerts Demo ===")
        
        print("\n🔔 Cross-Market Alert Examples:")
        
        # Volume anomaly alert
        await self.monitor._send_alert(
            AlertType.VOLUME_ANOMALY,
            "Crypto Volume Spike",
            "Crypto market 24h volume is 300% above normal levels",
            NotificationLevel.INFO,
            [MarketType.CRYPTO],
            {
                'current_volume': 3000000,
                'normal_volume': 1000000,
                'spike_percentage': 300
            }
        )
        print("📊 Volume anomaly alert sent")
        
        # Market disconnect alert
        await self.monitor._send_alert(
            AlertType.MARKET_DISCONNECT,
            "Forex Market High Latency",
            "Forex market latency has increased to 1500ms",
            NotificationLevel.WARNING,
            [MarketType.FOREX],
            {
                'current_latency': 1500,
                'normal_latency': 100,
                'threshold': 1000
            }
        )
        print("⚠️  Market connectivity alert sent")
        
        # Arbitrage opportunity alert
        await self.monitor._send_alert(
            AlertType.CROSS_MARKET_ARBITRAGE,
            "Cross-Market Arbitrage Opportunity",
            "Price discrepancy detected between crypto and forex EUR/USD pairs",
            NotificationLevel.INFO,
            [MarketType.CRYPTO, MarketType.FOREX],
            {
                'symbol': 'EUR/USD',
                'crypto_price': 1.0850,
                'forex_price': 1.0845,
                'spread': 0.0005,
                'profit_potential': 50
            }
        )
        print("💰 Arbitrage opportunity alert sent")
        
        await asyncio.sleep(2)
    
    async def _show_monitoring_dashboard(self):
        """Display monitoring dashboard information."""
        self.logger.info("=== Monitoring Dashboard ===")
        
        print("\n📋 Multi-Market Monitoring Dashboard:")
        
        # Get monitoring status
        status = self.monitor.get_monitoring_status()
        print(f"Status: {'🟢 Running' if status['running'] else '🔴 Stopped'}")
        print(f"Monitoring Interval: {status['monitoring_interval']}s")
        print(f"Markets Monitored: {len(status['markets_monitored'])}")
        print(f"Active Alerts: {status['active_alerts_count']}")
        print(f"24h Alert Count: {status['total_alerts_24h']}")
        
        # Show active alerts
        active_alerts = self.monitor.get_active_alerts()
        if active_alerts:
            print(f"\n🚨 Active Alerts ({len(active_alerts)}):")
            for alert in active_alerts[-5:]:  # Show last 5
                severity_emoji = {
                    'info': 'ℹ️',
                    'warning': '⚠️',
                    'error': '❌',
                    'critical': '🚨'
                }.get(alert['severity'], '❓')
                
                print(f"  {severity_emoji} {alert['title']}")
                print(f"     Type: {alert['alert_type']}")
                print(f"     Markets: {', '.join(alert['markets_affected'])}")
                print(f"     Time: {alert['timestamp']}")
        
        # Show market metrics summary
        all_metrics = self.monitor.get_market_metrics()
        if all_metrics:
            print(f"\n📊 Market Summary:")
            for market, metrics in all_metrics.items():
                status_emoji = '🟢' if metrics['is_active'] else '🔴'
                print(f"  {status_emoji} {market.upper()}: "
                      f"{metrics['active_symbols']} symbols, "
                      f"{metrics['error_rate']:.3%} error rate")
        
        await asyncio.sleep(3)
    
    async def _run_monitoring_period(self):
        """Run monitoring for a demonstration period."""
        self.logger.info("=== Live Monitoring Period ===")
        
        print("\n⏱️  Running live monitoring for 30 seconds...")
        print("   (In production, this would run continuously)")
        
        # Let monitoring run for demonstration
        for i in range(6):  # 30 seconds with 5-second intervals
            await asyncio.sleep(5)
            
            # Show periodic status
            active_count = len(self.monitor.get_active_alerts())
            print(f"   [{(i+1)*5}s] Active alerts: {active_count}")
            
            # Simulate occasional alerts
            if i == 2:  # At 15 seconds
                await self.monitor._send_alert(
                    AlertType.VOLUME_ANOMALY,
                    "Periodic Volume Check",
                    "Regular volume monitoring check completed",
                    NotificationLevel.INFO,
                    [MarketType.CRYPTO],
                    {'check_type': 'periodic'}
                )
        
        print("✅ Live monitoring period completed")
    
    def _setup_logging(self):
        """Set up logging for the demo."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/multi_market_monitoring_demo.log')
            ]
        )


async def main():
    """Main function to run the multi-market monitoring demo."""
    print("🚀 Multi-Market Monitoring System Demo")
    print("=" * 50)
    
    demo = MultiMarketMonitoringDemo()
    demo._setup_logging()
    
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        logging.error(f"Demo failed: {e}", exc_info=True)
    
    print("\n👋 Thank you for trying the Multi-Market Monitoring Demo!")


if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Run the demo
    asyncio.run(main())