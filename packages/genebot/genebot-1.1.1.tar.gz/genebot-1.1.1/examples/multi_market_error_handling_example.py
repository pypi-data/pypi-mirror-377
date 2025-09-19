"""
Multi-Market Error Handling Example

This example demonstrates the comprehensive error handling system for
multi-market trading scenarios including market closures, broker failover,
and regulatory compliance.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.exceptions.multi_market_exceptions import (
    MarketType,
    MarketClosedException,
    BrokerConnectionException,
    RegulatoryViolationException
)

from src.exceptions.market_closure_handler import (
    MarketClosureHandler,
    OrderQueueManager,
    QueuedOrder
)

from src.exceptions.broker_failover import (
    BrokerFailoverManager,
    BrokerConfig,
    FailoverStrategy
)

from src.exceptions.regulatory_handler import (
    RegulatoryComplianceManager,
    RegulatoryRule,
    ActionType,
    ViolationType,
    Severity
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiMarketErrorHandlingDemo:
    """Demonstrates multi-market error handling capabilities."""
    
    def __init__(self):
        self.closure_handler = MarketClosureHandler()
        self.order_queue_manager = OrderQueueManager()
        self.failover_manager = BrokerFailoverManager(FailoverStrategy.PRIORITY_BASED)
        self.compliance_manager = RegulatoryComplianceManager()
        
        self._setup_components()
    
    def _setup_components(self):
        """Setup all error handling components."""
        # Setup market sessions
        forex_sessions = {
            "london": {
                "start": "08:00",
                "end": "17:00",
                "timezone": "UTC"
            },
            "new_york": {
                "start": "13:00",
                "end": "22:00",
                "timezone": "UTC"
            }
        }
        self.closure_handler.register_market_session(MarketType.FOREX, forex_sessions)
        
        # Setup brokers for failover
        primary_broker = BrokerConfig(
            name="OANDA",
            market_type=MarketType.FOREX,
            priority=1,
            max_retries=3,
            retry_delay=1.0,
            backoff_multiplier=2.0
        )
        
        backup_broker = BrokerConfig(
            name="MT5",
            market_type=MarketType.FOREX,
            priority=2,
            max_retries=3,
            retry_delay=1.0,
            backoff_multiplier=2.0
        )
        
        self.failover_manager.register_broker(primary_broker)
        self.failover_manager.register_broker(backup_broker)
        
        # Setup regulatory rules
        position_limit_rule = RegulatoryRule(
            id="forex_position_limit",
            name="Forex Position Limit",
            description="Maximum position size per forex pair",
            market_type=MarketType.FOREX,
            jurisdiction="US",
            violation_type=ViolationType.POSITION_LIMIT_EXCEEDED,
            severity=Severity.HIGH,
            threshold_value=100000.0
        )
        
        leverage_limit_rule = RegulatoryRule(
            id="forex_leverage_limit",
            name="Forex Leverage Limit",
            description="Maximum leverage for forex trading",
            market_type=MarketType.FOREX,
            jurisdiction="US",
            violation_type=ViolationType.LEVERAGE_LIMIT_EXCEEDED,
            severity=Severity.HIGH,
            threshold_value=50.0
        )
        
        self.compliance_manager.monitor.register_rule(position_limit_rule)
        self.compliance_manager.monitor.register_rule(leverage_limit_rule)
        
        # Set position limits
        self.compliance_manager.monitor.set_position_limits(
            MarketType.FOREX,
            {
                "EUR/USD": 100000.0,
                "GBP/USD": 80000.0,
                "USD/JPY": 120000.0
            }
        )
        
        # Register order execution callback
        self.order_queue_manager.register_order_callback("market", self._execute_market_order)
        self.order_queue_manager.register_order_callback("limit", self._execute_limit_order)
    
    async def _execute_market_order(self, order: QueuedOrder):
        """Mock market order execution."""
        logger.info(f"Executing market order: {order.symbol} {order.side} {order.amount}")
        
        # Simulate execution delay
        await asyncio.sleep(0.1)
        
        # Check for regulatory violations
        violation = self.compliance_manager.monitor.check_position_limits(
            order.market_type,
            order.symbol,
            current_position=0.0,  # Simplified
            proposed_change=order.amount
        )
        
        if violation:
            logger.warning(f"Regulatory violation detected: {violation.description}")
            raise RegulatoryViolationException(
                violation.description,
                violation.market_type,
                violation.violation_type.value,
                "Position Limit Rule"
            )
        
        logger.info(f"Order {order.id} executed successfully")
    
    async def _execute_limit_order(self, order: QueuedOrder):
        """Mock limit order execution."""
        logger.info(f"Executing limit order: {order.symbol} {order.side} {order.amount} @ {order.price}")
        
        # Simulate execution delay
        await asyncio.sleep(0.1)
        
        logger.info(f"Limit order {order.id} placed successfully")
    
    async def demonstrate_market_closure_handling(self):
        """Demonstrate market closure and order queuing."""
        logger.info("=== Market Closure Handling Demo ===")
        
        try:
            # Try to submit order when market might be closed
            order_id = await self.order_queue_manager.submit_order(
                market_type=MarketType.FOREX,
                broker_name="OANDA",
                symbol="EUR/USD",
                side="buy",
                amount=50000.0,
                order_type="market",
                priority=1,
                expires_in=timedelta(hours=24)
            )
            
            logger.info(f"Order {order_id} submitted successfully")
            
        except MarketClosedException as e:
            logger.info(f"Market closed, order queued: {e.message}")
            logger.info(f"Next market open: {e.next_open_time}")
            
            # Show queued orders
            queued_orders = self.closure_handler.get_queued_orders(MarketType.FOREX)
            logger.info(f"Orders in queue: {len(queued_orders)}")
    
    async def demonstrate_broker_failover(self):
        """Demonstrate broker failover mechanism."""
        logger.info("=== Broker Failover Demo ===")
        
        try:
            # Simulate broker failure
            logger.info("Simulating OANDA broker failure...")
            
            new_broker = await self.failover_manager.handle_broker_failure(
                "OANDA",
                BrokerConnectionException(
                    "Connection timeout",
                    MarketType.FOREX,
                    "OANDA",
                    connection_type="websocket"
                ),
                MarketType.FOREX
            )
            
            logger.info(f"Successfully failed over to: {new_broker}")
            
            # Show active broker
            active_broker = self.failover_manager.get_active_broker(MarketType.FOREX)
            logger.info(f"Current active broker: {active_broker}")
            
            # Show available brokers
            available_brokers = self.failover_manager.get_available_brokers(MarketType.FOREX)
            logger.info(f"Available brokers: {available_brokers}")
            
        except Exception as e:
            logger.error(f"Failover failed: {e}")
    
    async def demonstrate_regulatory_compliance(self):
        """Demonstrate regulatory compliance monitoring."""
        logger.info("=== Regulatory Compliance Demo ===")
        
        # Test position limit violation
        logger.info("Testing position limit violation...")
        
        violation = self.compliance_manager.monitor.check_position_limits(
            MarketType.FOREX,
            "EUR/USD",
            current_position=80000.0,
            proposed_change=50000.0  # Would exceed 100k limit
        )
        
        if violation:
            logger.warning(f"Position limit violation: {violation.description}")
            logger.info(f"Current: {violation.current_value}, Limit: {violation.threshold_value}")
            
            # Create corrective action
            action = await self.compliance_manager.action_handler.create_corrective_action(
                violation,
                ActionType.POSITION_REDUCTION,
                "Reduce EUR/USD position to comply with limits",
                {"symbol": "EUR/USD", "target_position": 90000.0}
            )
            
            logger.info(f"Corrective action created: {action.description}")
        
        # Test leverage limit violation
        logger.info("Testing leverage limit violation...")
        
        violation = self.compliance_manager.monitor.check_leverage_limits(
            MarketType.FOREX,
            "account_123",
            current_leverage=75.0,
            max_leverage=50.0
        )
        
        if violation:
            logger.warning(f"Leverage violation: {violation.description}")
            
            # Create corrective action
            action = await self.compliance_manager.action_handler.create_corrective_action(
                violation,
                ActionType.TRADING_HALT,
                "Halt trading due to excessive leverage",
                {"account": "account_123"}
            )
            
            logger.info(f"Corrective action created: {action.description}")
        
        # Test wash trading detection
        logger.info("Testing wash trading detection...")
        
        # Simulate suspicious trading pattern
        trades = [
            {"symbol": "BTC/USD", "side": "buy", "price": 50000.0, "amount": 1.0},
            {"symbol": "BTC/USD", "side": "sell", "price": 50010.0, "amount": 1.0},
            {"symbol": "BTC/USD", "side": "buy", "price": 50005.0, "amount": 1.0},
            {"symbol": "BTC/USD", "side": "sell", "price": 50015.0, "amount": 1.0},
        ]
        
        for trade in trades:
            self.compliance_manager.monitor.record_trade(trade)
        
        violation = self.compliance_manager.monitor.check_wash_trading("BTC/USD")
        
        if violation:
            logger.warning(f"Wash trading detected: {violation.description}")
            
            # Create corrective action
            action = await self.compliance_manager.action_handler.create_corrective_action(
                violation,
                ActionType.MANUAL_REVIEW,
                "Manual review required for potential wash trading",
                {"symbol": "BTC/USD"}
            )
            
            logger.info(f"Corrective action created: {action.description}")
    
    async def demonstrate_integrated_scenario(self):
        """Demonstrate integrated error handling scenario."""
        logger.info("=== Integrated Error Handling Scenario ===")
        
        try:
            # Start all components
            await self.closure_handler.start_monitoring()
            await self.failover_manager.start()
            await self.order_queue_manager.start()
            
            logger.info("All error handling components started")
            
            # Simulate complex scenario
            logger.info("Simulating complex multi-market scenario...")
            
            # 1. Try to place large order that violates position limits
            try:
                await self.order_queue_manager.submit_order(
                    market_type=MarketType.FOREX,
                    broker_name="OANDA",
                    symbol="EUR/USD",
                    side="buy",
                    amount=150000.0,  # Exceeds position limit
                    order_type="market"
                )
            except RegulatoryViolationException as e:
                logger.warning(f"Order rejected due to regulatory violation: {e.message}")
            
            # 2. Simulate broker failure during order execution
            logger.info("Simulating broker failure during order execution...")
            
            await self.failover_manager.handle_broker_failure(
                "OANDA",
                Exception("Network connection lost"),
                MarketType.FOREX
            )
            
            # 3. Show system recovery
            active_broker = self.failover_manager.get_active_broker(MarketType.FOREX)
            logger.info(f"System recovered, now using broker: {active_broker}")
            
            # 4. Show violation summary
            violations = self.compliance_manager.monitor.get_violations(resolved=False)
            logger.info(f"Unresolved violations: {len(violations)}")
            
            for violation in violations:
                logger.info(f"  - {violation.violation_type.value}: {violation.description}")
            
        finally:
            # Stop all components
            await self.closure_handler.stop_monitoring()
            await self.failover_manager.stop()
            await self.order_queue_manager.stop()
            
            logger.info("All error handling components stopped")
    
    async def run_demo(self):
        """Run the complete error handling demonstration."""
        logger.info("Starting Multi-Market Error Handling Demo")
        
        try:
            await self.demonstrate_market_closure_handling()
            await asyncio.sleep(1)
            
            await self.demonstrate_broker_failover()
            await asyncio.sleep(1)
            
            await self.demonstrate_regulatory_compliance()
            await asyncio.sleep(1)
            
            await self.demonstrate_integrated_scenario()
            
        except Exception as e:
            logger.error(f"Demo error: {e}")
        
        logger.info("Multi-Market Error Handling Demo completed")


async def main():
    """Main function to run the demo."""
    demo = MultiMarketErrorHandlingDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())