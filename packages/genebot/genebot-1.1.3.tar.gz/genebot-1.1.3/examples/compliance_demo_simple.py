#!/usr/bin/env python3
"""
Simple Compliance Framework Demo

Demonstrates basic functionality of the regulatory compliance framework.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime, timedelta

from src.compliance import ComplianceManager, RegulatoryRules
from src.compliance.compliance_manager import ComplianceStatus, ComplianceCheck
from src.compliance.regulatory_rules import RuleType, Jurisdiction, RegulatoryRule
from src.markets.types import MarketType

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
            'formats': ['json'],
            'retention_days': 2555
        },
        'jurisdictions': ['US'],
        'max_total_exposure': 1000000,  # $1M
        'max_single_position_concentration': 0.2  # 20%
    }


def demonstrate_regulatory_rules():
    """Demonstrate regulatory rules management"""
    logger.info("=== Regulatory Rules Demo ===")
    
    # Initialize regulatory rules
    rules_config = {'rules_directory': 'config/regulatory_rules'}
    regulatory_rules = RegulatoryRules(rules_config)
    
    # Display existing rules count
    logger.info(f"Loaded {len(regulatory_rules.rules)} default rules")
    
    # Add custom rule
    custom_rule = RegulatoryRule(
        rule_id="demo_crypto_limit",
        rule_type=RuleType.POSITION_LIMIT,
        jurisdiction=Jurisdiction.US,
        market_type=MarketType.CRYPTO,
        description="Demo crypto position limit",
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
        "demo_crypto_limit",
        test_context
    )
    
    logger.info(f"Rule compliance test:")
    logger.info(f"  Compliant: {compliance_result['compliant']}")
    logger.info(f"  Message: {compliance_result['message']}")
    logger.info(f"  Severity: {compliance_result['severity']}")


def demonstrate_compliance_manager():
    """Demonstrate compliance manager functionality"""
    logger.info("\n=== Compliance Manager Demo ===")
    
    # Initialize compliance manager
    config = create_compliance_config()
    compliance_manager = ComplianceManager(config)
    
    logger.info(f"Compliance manager initialized for jurisdictions: {compliance_manager.jurisdictions}")
    
    # Create a compliance check
    check = ComplianceCheck(
        rule_id="demo_rule",
        status=ComplianceStatus.COMPLIANT,
        message="Demo compliance check passed",
        timestamp=datetime.utcnow(),
        market_type=MarketType.CRYPTO,
        severity="info"
    )
    
    # Record the event
    compliance_manager.compliance_history.append(check)
    logger.info(f"Recorded compliance event: {check.rule_id}")
    
    # Test action blocking
    logger.info(f"Is trading blocked: {compliance_manager.is_action_blocked('trading')}")
    
    # Add a violation
    violation = ComplianceCheck(
        rule_id="demo_violation",
        status=ComplianceStatus.VIOLATION,
        message="Demo violation for testing",
        timestamp=datetime.utcnow(),
        market_type=MarketType.CRYPTO,
        severity="high",
        action_required="block trading"
    )
    
    compliance_manager.active_violations.append(violation)
    compliance_manager.blocked_actions.add("trading")
    
    logger.info(f"After violation - Is trading blocked: {compliance_manager.is_action_blocked('trading')}")
    
    # Resolve violation
    success = compliance_manager.resolve_violation("demo_violation", "Demo resolution")
    logger.info(f"Violation resolved: {success}")
    logger.info(f"After resolution - Is trading blocked: {compliance_manager.is_action_blocked('trading')}")


def demonstrate_audit_trail():
    """Demonstrate audit trail functionality"""
    logger.info("\n=== Audit Trail Demo ===")
    
    # Initialize compliance manager (includes audit trail)
    config = create_compliance_config()
    compliance_manager = ComplianceManager(config)
    
    # Log system event
    event_id = compliance_manager.audit_trail.log_system_event(
        "Demo system startup",
        {
            "version": "1.0.0",
            "environment": "demo",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    logger.info(f"System event logged: {event_id}")
    
    # Log user action
    user_event_id = compliance_manager.audit_trail.log_user_action(
        "demo_login",
        "demo_user",
        session_id="demo_session",
        additional_data={"ip_address": "127.0.0.1"}
    )
    logger.info(f"User action logged: {user_event_id}")
    
    # Retrieve audit trail
    start_date = datetime.utcnow() - timedelta(hours=1)
    end_date = datetime.utcnow() + timedelta(hours=1)
    
    events = compliance_manager.audit_trail.get_audit_trail(start_date, end_date)
    logger.info(f"Retrieved {len(events)} audit events")


def demonstrate_reporting():
    """Demonstrate reporting functionality"""
    logger.info("\n=== Reporting Demo ===")
    
    # Initialize compliance manager
    config = create_compliance_config()
    compliance_manager = ComplianceManager(config)
    
    # Ensure reporting directory exists
    compliance_manager.reporting_engine.output_directory.mkdir(parents=True, exist_ok=True)
    
    # Create some compliance events
    events = [
        ComplianceCheck(
            rule_id="demo_rule_1",
            status=ComplianceStatus.COMPLIANT,
            message="Demo compliant event",
            timestamp=datetime.utcnow(),
            market_type=MarketType.CRYPTO,
            severity="info"
        ),
        ComplianceCheck(
            rule_id="demo_rule_2",
            status=ComplianceStatus.WARNING,
            message="Demo warning event",
            timestamp=datetime.utcnow(),
            market_type=MarketType.FOREX,
            severity="medium"
        )
    ]
    
    # Add events to history
    compliance_manager.compliance_history.extend(events)
    
    # Generate compliance report
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()
    
    try:
        report = compliance_manager.generate_compliance_report(start_date, end_date)
        logger.info(f"Compliance report generated: {report['file_path']}")
        logger.info(f"Total events in report: {report['metadata']['total_records']}")
    except Exception as e:
        logger.error(f"Error generating report: {e}")
    
    # Generate violation report
    violation = ComplianceCheck(
        rule_id="demo_violation",
        status=ComplianceStatus.VIOLATION,
        message="Demo violation for reporting",
        timestamp=datetime.utcnow(),
        market_type=MarketType.CRYPTO,
        severity="high",
        action_required="Immediate action required"
    )
    
    try:
        violation_report = compliance_manager.reporting_engine.generate_violation_report(violation)
        logger.info(f"Violation report generated: {violation_report['violation_id']}")
    except Exception as e:
        logger.error(f"Error generating violation report: {e}")


def main():
    """Main demo function"""
    logger.info("Starting Simple Compliance Framework Demo")
    logger.info("=" * 50)
    
    try:
        # Run demonstrations
        demonstrate_regulatory_rules()
        demonstrate_compliance_manager()
        demonstrate_audit_trail()
        demonstrate_reporting()
        
        logger.info("\n" + "=" * 50)
        logger.info("Simple Compliance Framework Demo Completed Successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()