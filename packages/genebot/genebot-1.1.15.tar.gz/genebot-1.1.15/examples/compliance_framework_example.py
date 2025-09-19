#!/usr/bin/env python3
"""
Compliance Framework Example

Demonstrates how to use the regulatory compliance framework
for multi-market trading operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.compliance import ComplianceManager, RegulatoryRules
from src.compliance.regulatory_rules import RuleType, Jurisdiction, RegulatoryRule
from src.markets.types import MarketType, UnifiedSymbol
from src.models.data_models import Order, Position, OrderSide, OrderType, OrderStatus
from decimal import Decimal


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_compliance_config():
    """Create compliance configuration"""
    return {
        'rules': {
            'rules_directory': 'config/regulatory_rules'
        },
        'audit': {
            'db_path': 'compliance_audit.db',
            'enable_checksums': True,
            'retention_days': 2555
        },
        'reporting': {
            'output_directory': 'reports/compliance',
            'formats': ['json', 'csv'],
            'retention_days': 2555
        },
        'jurisdictions': ['US', 'EU'],
        'max_total_exposure': 10000000,  # $10M
        'max_single_position_concentration': 0.15  # 15%
    }


def create_sample_orders():
    """Create sample orders for testing"""
    # Crypto order
    crypto_symbol = UnifiedSymbol(
        base_asset="BTC",
        quote_asset="USD",
        market_type=MarketType.CRYPTO,
        native_symbol="BTCUSD"
    )
    
    crypto_order = Order(
        id="crypto_order_1",
        symbol="BTCUSD",
        side=OrderSide.BUY,
        amount=Decimal("2.0"),
        price=Decimal("50000.0"),
        order_type=OrderType.MARKET,
        status=OrderStatus.PENDING,
        timestamp=datetime.utcnow(),
        exchange="demo_exchange"
    )
    
    # Forex order
    forex_symbol = UnifiedSymbol(
        base_asset="EUR",
        quote_asset="USD",
        market_type=MarketType.FOREX,
        native_symbol="EURUSD"
    )
    
    forex_order = Order(
        id="forex_order_1",
        symbol="EURUSD",
        side=OrderSide.BUY,
        amount=Decimal("100000.0"),  # 100k EUR
        price=Decimal("1.1000"),
        order_type=OrderType.MARKET,
        status=OrderStatus.PENDING,
        timestamp=datetime.utcnow(),
        exchange="demo_broker"
    )
    
    return [crypto_order, forex_order]


def create_sample_positions():
    """Create sample positions for portfolio compliance testing"""
    positions = []
    
    # Large BTC position
    btc_symbol = UnifiedSymbol(
        base_asset="BTC",
        quote_asset="USD",
        market_type=MarketType.CRYPTO,
        native_symbol="BTCUSD"
    )
    
    btc_position = Position(
        symbol="BTCUSD",
        size=Decimal("50.0"),  # 50 BTC
        entry_price=Decimal("48000.0"),
        current_price=Decimal("50000.0"),
        timestamp=datetime.utcnow(),
        exchange="demo_exchange"
    )
    positions.append(btc_position)
    
    # EUR/USD position
    eur_symbol = UnifiedSymbol(
        base_asset="EUR",
        quote_asset="USD",
        market_type=MarketType.FOREX,
        native_symbol="EURUSD"
    )
    
    eur_position = Position(
        symbol="EURUSD",
        size=Decimal("500000.0"),  # 500k EUR
        entry_price=Decimal("1.0950"),
        current_price=Decimal("1.1000"),
        timestamp=datetime.utcnow(),
        exchange="demo_broker"
    )
    positions.append(eur_position)
    
    return positions


async def demonstrate_compliance_validation():
    """Demonstrate trade compliance validation"""
    logger.info("=== Trade Compliance Validation Demo ===")
    
    # Initialize compliance manager
    config = create_compliance_config()
    compliance_manager = ComplianceManager(config)
    
    # Create sample orders
    orders = create_sample_orders()
    
    for order in orders:
        logger.info(f"\nValidating {order.symbol.market_type.value} order: {order.id}")
        logger.info(f"Symbol: {order.symbol.to_standard_format()}")
        logger.info(f"Amount: {order.amount}")
        logger.info(f"Price: {order.price}")
        
        # Validate trade
        result = compliance_manager.validate_trade(order)
        
        logger.info(f"Compliance Status: {result.status.value}")
        logger.info(f"Rule ID: {result.rule_id}")
        logger.info(f"Message: {result.message}")
        logger.info(f"Severity: {result.severity}")
        
        if result.action_required:
            logger.warning(f"Action Required: {result.action_required}")
        
        # Record compliance event
        compliance_manager.record_compliance_event(result)


async def demonstrate_portfolio_compliance():
    """Demonstrate portfolio compliance checking"""
    logger.info("\n=== Portfolio Compliance Demo ===")
    
    # Initialize compliance manager
    config = create_compliance_config()
    compliance_manager = ComplianceManager(config)
    
    # Create sample positions
    positions = create_sample_positions()
    
    logger.info("Current Portfolio:")
    total_exposure = 0
    for position in positions:
        exposure = abs(position.amount * position.current_price)
        total_exposure += exposure
        logger.info(f"  {position.symbol.to_standard_format()}: "
                   f"{position.amount} @ ${position.current_price} = ${exposure:,.2f}")
    
    logger.info(f"Total Exposure: ${total_exposure:,.2f}")
    
    # Check portfolio compliance
    compliance_checks = compliance_manager.check_portfolio_compliance(positions)
    
    logger.info(f"\nPortfolio Compliance Checks: {len(compliance_checks)}")
    for check in compliance_checks:
        logger.info(f"  Rule: {check.rule_id}")
        logger.info(f"  Status: {check.status.value}")
        logger.info(f"  Message: {check.message}")
        logger.info(f"  Severity: {check.severity}")
        if check.action_required:
            logger.warning(f"  Action Required: {check.action_required}")
        logger.info("")


async def demonstrate_regulatory_rules():
    """Demonstrate regulatory rules management"""
    logger.info("\n=== Regulatory Rules Demo ===")
    
    # Initialize regulatory rules
    rules_config = {'rules_directory': 'config/regulatory_rules'}
    regulatory_rules = RegulatoryRules(rules_config)
    
    # Display existing rules
    logger.info("Existing Rules:")
    for rule_id, rule in regulatory_rules.rules.items():
        logger.info(f"  {rule_id}: {rule.description}")
        logger.info(f"    Jurisdiction: {rule.jurisdiction.value}")
        logger.info(f"    Market: {rule.market_type.value}")
        logger.info(f"    Type: {rule.rule_type.value}")
        logger.info("")
    
    # Add custom rule
    custom_rule = RegulatoryRule(
        rule_id="custom_crypto_limit",
        rule_type=RuleType.POSITION_LIMIT,
        jurisdiction=Jurisdiction.US,
        market_type=MarketType.CRYPTO,
        description="Custom crypto position limit for demo",
        parameters={
            'max_position_size': 75000,  # $75k limit
            'concentration_limit': 0.1   # 10% max
        },
        effective_date=datetime.utcnow(),
        severity="high",
        enforcement_action="block"
    )
    
    logger.info("Adding custom rule...")
    success = regulatory_rules.add_rule(custom_rule)
    logger.info(f"Custom rule added: {success}")
    
    # Test rule compliance
    test_context = {
        'position_size': 100000  # Above limit
    }
    
    compliance_result = regulatory_rules.check_rule_compliance(
        "custom_crypto_limit",
        test_context
    )
    
    logger.info(f"Rule compliance test:")
    logger.info(f"  Compliant: {compliance_result['compliant']}")
    logger.info(f"  Message: {compliance_result['message']}")
    logger.info(f"  Severity: {compliance_result['severity']}")


async def demonstrate_audit_trail():
    """Demonstrate audit trail functionality"""
    logger.info("\n=== Audit Trail Demo ===")
    
    # Initialize compliance manager (includes audit trail)
    config = create_compliance_config()
    compliance_manager = ComplianceManager(config)
    
    # Create sample order
    orders = create_sample_orders()
    sample_order = orders[0]
    
    # Log various events
    logger.info("Logging audit events...")
    
    # Log order placement
    order_event_id = compliance_manager.audit_trail.log_order_placement(
        sample_order,
        user_id="demo_user",
        session_id="demo_session"
    )
    logger.info(f"Order placement logged: {order_event_id}")
    
    # Log trade execution
    trade_event_id = compliance_manager.audit_trail.log_trade_execution(
        sample_order,
        execution_price=49500.0,
        execution_amount=2.0,
        user_id="demo_user",
        session_id="demo_session"
    )
    logger.info(f"Trade execution logged: {trade_event_id}")
    
    # Log system event
    system_event_id = compliance_manager.audit_trail.log_system_event(
        "Compliance demo completed",
        {
            "demo_type": "audit_trail",
            "timestamp": datetime.utcnow().isoformat(),
            "success": True
        }
    )
    logger.info(f"System event logged: {system_event_id}")
    
    # Retrieve audit trail
    start_date = datetime.utcnow() - timedelta(hours=1)
    end_date = datetime.utcnow() + timedelta(hours=1)
    
    events = compliance_manager.audit_trail.get_audit_trail(start_date, end_date)
    
    logger.info(f"\nRetrieved {len(events)} audit events:")
    for event in events:
        logger.info(f"  {event.event_id}: {event.event_type.value}")
        logger.info(f"    Timestamp: {event.timestamp}")
        logger.info(f"    Market: {event.market_type.value}")
        logger.info(f"    User: {event.user_id}")
        logger.info("")


async def demonstrate_compliance_reporting():
    """Demonstrate compliance reporting"""
    logger.info("\n=== Compliance Reporting Demo ===")
    
    # Initialize compliance manager
    config = create_compliance_config()
    compliance_manager = ComplianceManager(config)
    
    # Generate some compliance events
    orders = create_sample_orders()
    for order in orders:
        result = compliance_manager.validate_trade(order)
        compliance_manager.record_compliance_event(result)
    
    # Generate compliance report
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()
    
    logger.info("Generating compliance report...")
    report = compliance_manager.generate_compliance_report(start_date, end_date)
    
    logger.info(f"Report generated: {report['file_path']}")
    logger.info(f"Report ID: {report['metadata']['report_id']}")
    logger.info(f"Total records: {report['metadata']['total_records']}")
    
    # Display report summary
    summary = report['data']['summary']
    logger.info(f"\nCompliance Summary:")
    logger.info(f"  Total events: {summary['total_events']}")
    logger.info(f"  Compliant: {summary.get('compliant', 0)}")
    logger.info(f"  Warnings: {summary.get('warnings', 0)}")
    logger.info(f"  Violations: {summary.get('violations', 0)}")
    
    # Display by market breakdown
    by_market = report['data']['by_market']
    logger.info(f"\nBy Market:")
    for market, stats in by_market.items():
        logger.info(f"  {market}: {stats}")


async def demonstrate_violation_handling():
    """Demonstrate violation handling and resolution"""
    logger.info("\n=== Violation Handling Demo ===")
    
    # Initialize compliance manager with strict limits
    config = create_compliance_config()
    config['max_total_exposure'] = 50000  # Very low limit to trigger violation
    compliance_manager = ComplianceManager(config)
    
    # Create positions that will violate limits
    positions = create_sample_positions()
    
    # Check portfolio compliance (should trigger violations)
    compliance_checks = compliance_manager.check_portfolio_compliance(positions)
    
    violations = [check for check in compliance_checks 
                 if check.status.value == 'violation']
    
    logger.info(f"Found {len(violations)} violations:")
    for violation in violations:
        logger.warning(f"  Violation: {violation.rule_id}")
        logger.warning(f"  Message: {violation.message}")
        logger.warning(f"  Action Required: {violation.action_required}")
        
        # Record violation
        compliance_manager.record_compliance_event(violation)
    
    logger.info(f"\nActive violations: {len(compliance_manager.active_violations)}")
    logger.info(f"Blocked actions: {list(compliance_manager.blocked_actions)}")
    
    # Resolve violations
    for violation in violations:
        logger.info(f"Resolving violation: {violation.rule_id}")
        success = compliance_manager.resolve_violation(
            violation.rule_id,
            "Demo violation resolved - positions reduced"
        )
        logger.info(f"Resolution success: {success}")
    
    logger.info(f"Active violations after resolution: {len(compliance_manager.active_violations)}")


async def main():
    """Main demo function"""
    logger.info("Starting Compliance Framework Demo")
    logger.info("=" * 50)
    
    try:
        # Run all demonstrations
        await demonstrate_compliance_validation()
        await demonstrate_portfolio_compliance()
        await demonstrate_regulatory_rules()
        await demonstrate_audit_trail()
        await demonstrate_compliance_reporting()
        await demonstrate_violation_handling()
        
        logger.info("\n" + "=" * 50)
        logger.info("Compliance Framework Demo Completed Successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())