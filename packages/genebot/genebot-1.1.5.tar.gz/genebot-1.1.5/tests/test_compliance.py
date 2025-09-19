"""
Unit tests for the regulatory compliance framework.

Tests all components of the compliance system including ComplianceManager,
ReportingEngine, AuditTrail, and RegulatoryRules.
"""

import pytest
import tempfile
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from src.compliance import (
    ComplianceManager, 
    ReportingEngine, 
    AuditTrail, 
    RegulatoryRules
)
from src.compliance.compliance_manager import ComplianceStatus, ComplianceCheck
from src.compliance.audit_trail import AuditEventType, AuditEvent
from src.compliance.regulatory_rules import RuleType, Jurisdiction, RegulatoryRule
from src.markets.types import MarketType, UnifiedSymbol
from src.models.data_models import Order, Position, OrderSide, OrderType, OrderStatus


class TestComplianceManager:
    """Test ComplianceManager functionality"""
    
    @pytest.fixture
    def compliance_config(self):
        """Compliance manager configuration"""
        return {
            'rules': {
                'rules_directory': 'test_rules'
            },
            'audit': {
                'db_path': ':memory:',
                'enable_checksums': True
            },
            'reporting': {
                'output_directory': 'test_reports',
                'formats': ['json', 'csv']
            },
            'jurisdictions': ['US'],
            'max_total_exposure': 1000000,
            'max_single_position_concentration': 0.2
        }
    
    @pytest.fixture
    def compliance_manager(self, compliance_config):
        """Create ComplianceManager instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            compliance_config['reporting']['output_directory'] = temp_dir
            compliance_config['rules']['rules_directory'] = temp_dir
            return ComplianceManager(compliance_config)
    
    @pytest.fixture
    def sample_order(self):
        """Create sample order for testing"""
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USD",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSD"
        )
        
        return Order(
            id="test_order_1",
            symbol=symbol,
            side="buy",
            amount=1.0,
            price=50000.0,
            order_type="market",
            status="pending",
            timestamp=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_position(self):
        """Create sample position for testing"""
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USD",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSD"
        )
        
        return Position(
            symbol=symbol,
            amount=1.0,
            current_price=50000.0
        )
    
    def test_compliance_manager_initialization(self, compliance_manager):
        """Test ComplianceManager initialization"""
        assert compliance_manager is not None
        assert compliance_manager.jurisdictions == ['US']
        assert len(compliance_manager.active_violations) == 0
        assert len(compliance_manager.compliance_history) == 0
    
    def test_validate_trade_compliant(self, compliance_manager, sample_order):
        """Test trade validation for compliant trade"""
        result = compliance_manager.validate_trade(sample_order)
        
        assert isinstance(result, ComplianceCheck)
        assert result.status == ComplianceStatus.COMPLIANT
        assert result.market_type == MarketType.CRYPTO
        assert "passes all compliance checks" in result.message
    
    def test_validate_trade_position_size_violation(self, compliance_manager, sample_order):
        """Test trade validation with position size violation"""
        # Mock market rules to have a low position size limit
        compliance_manager.regulatory_rules.market_rules[MarketType.CRYPTO] = {
            'max_position_size': 0.5  # Lower than order amount
        }
        
        result = compliance_manager.validate_trade(sample_order)
        
        assert result.status == ComplianceStatus.VIOLATION
        assert result.rule_id == "position_size_limit"
        assert result.severity == "high"
        assert "exceeds maximum position size" in result.message
    
    def test_validate_trade_leverage_violation(self, compliance_manager, sample_order):
        """Test trade validation with leverage violation"""
        # Add leverage to order
        sample_order.leverage = 10
        
        # Mock market rules to have a low leverage limit
        compliance_manager.regulatory_rules.market_rules[MarketType.CRYPTO] = {
            'max_leverage': 5
        }
        
        result = compliance_manager.validate_trade(sample_order)
        
        assert result.status == ComplianceStatus.VIOLATION
        assert result.rule_id == "leverage_limit"
        assert result.severity == "high"
        assert "exceeds maximum" in result.message
    
    def test_record_compliance_event(self, compliance_manager):
        """Test recording compliance events"""
        check = ComplianceCheck(
            rule_id="test_rule",
            status=ComplianceStatus.WARNING,
            message="Test warning",
            timestamp=datetime.utcnow(),
            market_type=MarketType.CRYPTO,
            severity="medium"
        )
        
        compliance_manager.record_compliance_event(check)
        
        assert len(compliance_manager.compliance_history) == 1
        assert compliance_manager.compliance_history[0] == check
    
    def test_record_violation_blocks_actions(self, compliance_manager):
        """Test that violations can block actions"""
        violation = ComplianceCheck(
            rule_id="blocking_rule",
            status=ComplianceStatus.VIOLATION,
            message="Test violation",
            timestamp=datetime.utcnow(),
            market_type=MarketType.CRYPTO,
            severity="high",
            action_required="block trading"
        )
        
        compliance_manager.record_compliance_event(violation)
        
        assert len(compliance_manager.active_violations) == 1
        assert "blocking_rule" in compliance_manager.blocked_actions
    
    def test_check_portfolio_compliance(self, compliance_manager, sample_position):
        """Test portfolio compliance checking"""
        positions = [sample_position]
        
        checks = compliance_manager.check_portfolio_compliance(positions)
        
        assert isinstance(checks, list)
        # Should pass with default limits
        assert all(check.status != ComplianceStatus.VIOLATION for check in checks)
    
    def test_check_portfolio_exposure_violation(self, compliance_manager, sample_position):
        """Test portfolio compliance with exposure violation"""
        # Create position that exceeds total exposure limit
        sample_position.amount = 100  # $5M exposure with $50k price
        positions = [sample_position]
        
        checks = compliance_manager.check_portfolio_compliance(positions)
        
        # Should have violation for total exposure
        violation_checks = [c for c in checks if c.status == ComplianceStatus.VIOLATION]
        assert len(violation_checks) > 0
        assert any("Total exposure" in c.message for c in violation_checks)
    
    def test_resolve_violation(self, compliance_manager):
        """Test violation resolution"""
        # Create and record a violation
        violation = ComplianceCheck(
            rule_id="test_violation",
            status=ComplianceStatus.VIOLATION,
            message="Test violation",
            timestamp=datetime.utcnow(),
            market_type=MarketType.CRYPTO,
            severity="high"
        )
        
        compliance_manager.record_compliance_event(violation)
        assert len(compliance_manager.active_violations) == 1
        
        # Resolve the violation
        result = compliance_manager.resolve_violation("test_violation", "Issue resolved")
        
        assert result is True
        assert len(compliance_manager.active_violations) == 0
    
    def test_is_action_blocked(self, compliance_manager):
        """Test action blocking check"""
        # Initially no actions blocked
        assert not compliance_manager.is_action_blocked("trading")
        
        # Add blocked action
        compliance_manager.blocked_actions.add("trading")
        
        assert compliance_manager.is_action_blocked("trading")
        assert not compliance_manager.is_action_blocked("reporting")


class TestReportingEngine:
    """Test ReportingEngine functionality"""
    
    @pytest.fixture
    def reporting_config(self):
        """Reporting engine configuration"""
        return {
            'output_directory': 'test_reports',
            'formats': ['json', 'csv', 'xml'],
            'jurisdictions': ['US', 'EU'],
            'retention_days': 30
        }
    
    @pytest.fixture
    def reporting_engine(self, reporting_config):
        """Create ReportingEngine instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporting_config['output_directory'] = temp_dir
            return ReportingEngine(reporting_config)
    
    @pytest.fixture
    def sample_compliance_events(self):
        """Create sample compliance events"""
        events = []
        for i in range(5):
            event = ComplianceCheck(
                rule_id=f"rule_{i}",
                status=ComplianceStatus.COMPLIANT if i % 2 == 0 else ComplianceStatus.WARNING,
                message=f"Test event {i}",
                timestamp=datetime.utcnow() - timedelta(hours=i),
                market_type=MarketType.CRYPTO,
                severity="medium"
            )
            events.append(event)
        return events
    
    def test_reporting_engine_initialization(self, reporting_engine):
        """Test ReportingEngine initialization"""
        assert reporting_engine is not None
        assert reporting_engine.jurisdictions == ['US', 'EU']
        assert 'json' in reporting_engine.supported_formats
        assert reporting_engine.output_directory.exists()
    
    def test_generate_compliance_report(self, reporting_engine, sample_compliance_events):
        """Test compliance report generation"""
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()
        
        report = reporting_engine.generate_compliance_report(
            sample_compliance_events,
            start_date,
            end_date
        )
        
        assert 'metadata' in report
        assert 'data' in report
        assert 'file_path' in report
        
        # Check metadata
        metadata = report['metadata']
        assert metadata['report_type'] == 'compliance_summary'
        assert metadata['total_records'] == len(sample_compliance_events)
        
        # Check data structure
        data = report['data']
        assert 'summary' in data
        assert 'events' in data
        assert data['summary']['total_events'] == len(sample_compliance_events)
    
    def test_generate_violation_report(self, reporting_engine):
        """Test violation report generation"""
        violation = ComplianceCheck(
            rule_id="test_violation",
            status=ComplianceStatus.VIOLATION,
            message="Test violation",
            timestamp=datetime.utcnow(),
            market_type=MarketType.CRYPTO,
            severity="high",
            action_required="Immediate action required"
        )
        
        report = reporting_engine.generate_violation_report(violation)
        
        assert 'violation_id' in report
        assert report['rule_id'] == "test_violation"
        assert report['status'] == "violation"
        assert report['severity'] == "high"
    
    def test_generate_trade_report_us(self, reporting_engine):
        """Test US trade report generation"""
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USD",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSD"
        )
        
        trades = [
            Order(
                id="trade_1",
                symbol=symbol,
                side="buy",
                amount=1.0,
                price=50000.0,
                order_type="market",
                status="filled",
                timestamp=datetime.utcnow()
            )
        ]
        
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()
        
        report = reporting_engine.generate_trade_report(
            trades, start_date, end_date, 'US'
        )
        
        assert 'metadata' in report
        assert 'data' in report
        
        data = report['data']
        assert data['jurisdiction'] == 'US'
        assert len(data['trades']) == 1
        assert data['trades'][0]['trade_id'] == 'trade_1'
    
    def test_generate_position_report(self, reporting_engine):
        """Test position report generation"""
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USD",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSD"
        )
        
        positions = [
            Position(
                symbol=symbol,
                amount=1.0,
                current_price=50000.0
            )
        ]
        
        report_date = datetime.utcnow()
        
        report = reporting_engine.generate_position_report(positions, report_date)
        
        assert 'metadata' in report
        assert 'data' in report
        
        data = report['data']
        assert data['total_positions'] == 1
        assert data['total_exposure'] == 50000.0
        assert len(data['positions']) == 1


class TestAuditTrail:
    """Test AuditTrail functionality"""
    
    @pytest.fixture
    def audit_config(self):
        """Audit trail configuration"""
        return {
            'db_path': ':memory:',
            'enable_checksums': True,
            'retention_days': 30,
            'batch_size': 10
        }
    
    @pytest.fixture
    def audit_trail(self, audit_config):
        """Create AuditTrail instance"""
        return AuditTrail(audit_config)
    
    @pytest.fixture
    def sample_order(self):
        """Create sample order for testing"""
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USD",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSD"
        )
        
        return Order(
            id="test_order_1",
            symbol=symbol,
            side="buy",
            amount=1.0,
            price=50000.0,
            order_type="market",
            status="pending",
            timestamp=datetime.utcnow()
        )
    
    def test_audit_trail_initialization(self, audit_trail):
        """Test AuditTrail initialization"""
        assert audit_trail is not None
        assert audit_trail.enable_checksums is True
        assert audit_trail.retention_days == 30
    
    def test_log_trade_execution(self, audit_trail, sample_order):
        """Test logging trade execution"""
        event_id = audit_trail.log_trade_execution(
            sample_order,
            execution_price=49500.0,
            execution_amount=1.0,
            user_id="test_user",
            session_id="test_session"
        )
        
        assert event_id is not None
        assert event_id.startswith("audit_")
    
    def test_log_order_placement(self, audit_trail, sample_order):
        """Test logging order placement"""
        event_id = audit_trail.log_order_placement(
            sample_order,
            user_id="test_user",
            session_id="test_session"
        )
        
        assert event_id is not None
        assert event_id.startswith("audit_")
    
    def test_log_compliance_event(self, audit_trail):
        """Test logging compliance events"""
        compliance_check = ComplianceCheck(
            rule_id="test_rule",
            status=ComplianceStatus.WARNING,
            message="Test compliance event",
            timestamp=datetime.utcnow(),
            market_type=MarketType.CRYPTO,
            severity="medium"
        )
        
        event_id = audit_trail.log_compliance_event(compliance_check)
        
        assert event_id is not None
        assert event_id.startswith("audit_")
    
    def test_get_audit_trail(self, audit_trail, sample_order):
        """Test retrieving audit trail"""
        # Log some events
        audit_trail.log_order_placement(sample_order, user_id="test_user")
        audit_trail.log_trade_execution(sample_order, 49500.0, 1.0, user_id="test_user")
        
        # Retrieve events
        start_date = datetime.utcnow() - timedelta(hours=1)
        end_date = datetime.utcnow() + timedelta(hours=1)
        
        events = audit_trail.get_audit_trail(start_date, end_date)
        
        assert len(events) == 2
        assert all(isinstance(event, AuditEvent) for event in events)
    
    def test_verify_integrity(self, audit_trail, sample_order):
        """Test event integrity verification"""
        event_id = audit_trail.log_order_placement(sample_order, user_id="test_user")
        
        # Verify integrity
        is_valid = audit_trail.verify_integrity(event_id)
        assert is_valid is True
    
    def test_log_system_event(self, audit_trail):
        """Test logging system events"""
        event_id = audit_trail.log_system_event(
            "System startup",
            {"version": "1.0.0", "environment": "test"}
        )
        
        assert event_id is not None
        assert event_id.startswith("audit_")
    
    def test_log_user_action(self, audit_trail):
        """Test logging user actions"""
        event_id = audit_trail.log_user_action(
            "login",
            "test_user",
            session_id="test_session",
            additional_data={"ip_address": "127.0.0.1"}
        )
        
        assert event_id is not None
        assert event_id.startswith("audit_")


class TestRegulatoryRules:
    """Test RegulatoryRules functionality"""
    
    @pytest.fixture
    def rules_config(self):
        """Regulatory rules configuration"""
        return {
            'rules_directory': 'test_rules'
        }
    
    @pytest.fixture
    def regulatory_rules(self, rules_config):
        """Create RegulatoryRules instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_config['rules_directory'] = temp_dir
            return RegulatoryRules(rules_config)
    
    @pytest.fixture
    def sample_rule(self):
        """Create sample regulatory rule"""
        return RegulatoryRule(
            rule_id="test_position_limit",
            rule_type=RuleType.POSITION_LIMIT,
            jurisdiction=Jurisdiction.US,
            market_type=MarketType.CRYPTO,
            description="Test position limit rule",
            parameters={
                'max_position_size': 100000,
                'concentration_limit': 0.2
            },
            effective_date=datetime.utcnow() - timedelta(days=1),
            severity="high",
            enforcement_action="block"
        )
    
    def test_regulatory_rules_initialization(self, regulatory_rules):
        """Test RegulatoryRules initialization"""
        assert regulatory_rules is not None
        assert len(regulatory_rules.rules) > 0  # Should have default rules
        assert MarketType.CRYPTO in regulatory_rules.market_rules
        assert MarketType.FOREX in regulatory_rules.market_rules
    
    def test_add_rule(self, regulatory_rules, sample_rule):
        """Test adding a regulatory rule"""
        initial_count = len(regulatory_rules.rules)
        
        result = regulatory_rules.add_rule(sample_rule)
        
        assert result is True
        assert len(regulatory_rules.rules) == initial_count + 1
        assert sample_rule.rule_id in regulatory_rules.rules
    
    def test_get_rule(self, regulatory_rules, sample_rule):
        """Test retrieving a specific rule"""
        regulatory_rules.add_rule(sample_rule)
        
        retrieved_rule = regulatory_rules.get_rule(sample_rule.rule_id)
        
        assert retrieved_rule is not None
        assert retrieved_rule.rule_id == sample_rule.rule_id
        assert retrieved_rule.rule_type == sample_rule.rule_type
    
    def test_update_rule(self, regulatory_rules, sample_rule):
        """Test updating a rule"""
        regulatory_rules.add_rule(sample_rule)
        
        updates = {
            'description': 'Updated description',
            'severity': 'medium'
        }
        
        result = regulatory_rules.update_rule(sample_rule.rule_id, updates)
        
        assert result is True
        
        updated_rule = regulatory_rules.get_rule(sample_rule.rule_id)
        assert updated_rule.description == 'Updated description'
        assert updated_rule.severity == 'medium'
    
    def test_remove_rule(self, regulatory_rules, sample_rule):
        """Test removing a rule"""
        regulatory_rules.add_rule(sample_rule)
        initial_count = len(regulatory_rules.rules)
        
        result = regulatory_rules.remove_rule(sample_rule.rule_id)
        
        assert result is True
        assert len(regulatory_rules.rules) == initial_count - 1
        assert sample_rule.rule_id not in regulatory_rules.rules
    
    def test_get_market_rules(self, regulatory_rules):
        """Test getting market-specific rules"""
        crypto_rules = regulatory_rules.get_market_rules(MarketType.CRYPTO)
        forex_rules = regulatory_rules.get_market_rules(MarketType.FOREX)
        
        assert isinstance(crypto_rules, dict)
        assert isinstance(forex_rules, dict)
        
        # Should have some default rules
        assert len(crypto_rules) > 0
        assert len(forex_rules) > 0
    
    def test_get_jurisdiction_rules(self, regulatory_rules):
        """Test getting jurisdiction-specific rules"""
        us_rules = regulatory_rules.get_jurisdiction_rules(Jurisdiction.US)
        
        assert isinstance(us_rules, list)
        assert len(us_rules) > 0  # Should have default US rules
        
        # All rules should be for US jurisdiction
        assert all(rule.jurisdiction == Jurisdiction.US for rule in us_rules)
    
    def test_get_applicable_rules(self, regulatory_rules):
        """Test getting applicable rules for market and jurisdiction"""
        applicable_rules = regulatory_rules.get_applicable_rules(
            MarketType.CRYPTO,
            Jurisdiction.US
        )
        
        assert isinstance(applicable_rules, list)
        assert len(applicable_rules) > 0
        
        # All rules should match criteria
        for rule in applicable_rules:
            assert rule.market_type == MarketType.CRYPTO
            assert rule.jurisdiction == Jurisdiction.US
    
    def test_check_rule_compliance(self, regulatory_rules, sample_rule):
        """Test rule compliance checking"""
        regulatory_rules.add_rule(sample_rule)
        
        # Test compliant context
        compliant_context = {
            'position_size': 50000  # Below limit
        }
        
        result = regulatory_rules.check_rule_compliance(
            sample_rule.rule_id,
            compliant_context
        )
        
        assert result['compliant'] is True
        assert result['severity'] == 'info'
        
        # Test non-compliant context
        non_compliant_context = {
            'position_size': 150000  # Above limit
        }
        
        result = regulatory_rules.check_rule_compliance(
            sample_rule.rule_id,
            non_compliant_context
        )
        
        assert result['compliant'] is False
        assert 'exceeds limit' in result['message']
    
    def test_export_import_rules(self, regulatory_rules, sample_rule):
        """Test exporting and importing rules"""
        regulatory_rules.add_rule(sample_rule)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            export_path = Path(f.name)
        
        try:
            # Export rules
            export_result = regulatory_rules.export_rules(export_path)
            assert export_result is True
            assert export_path.exists()
            
            # Create new instance and import
            new_rules = RegulatoryRules({'rules_directory': 'test'})
            import_result = new_rules.import_rules(export_path)
            assert import_result is True
            
            # Verify imported rule
            imported_rule = new_rules.get_rule(sample_rule.rule_id)
            assert imported_rule is not None
            assert imported_rule.description == sample_rule.description
            
        finally:
            if export_path.exists():
                export_path.unlink()


class TestComplianceIntegration:
    """Test integration between compliance components"""
    
    @pytest.fixture
    def integrated_compliance_system(self):
        """Create integrated compliance system"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                'rules': {
                    'rules_directory': temp_dir
                },
                'audit': {
                    'db_path': ':memory:',
                    'enable_checksums': True
                },
                'reporting': {
                    'output_directory': temp_dir,
                    'formats': ['json']
                },
                'jurisdictions': ['US'],
                'max_total_exposure': 1000000
            }
            
            return ComplianceManager(config)
    
    def test_end_to_end_compliance_workflow(self, integrated_compliance_system):
        """Test complete compliance workflow"""
        # Create test order
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USD",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSD"
        )
        
        order = Order(
            id="integration_test_order",
            symbol=symbol,
            side="buy",
            amount=1.0,
            price=50000.0,
            order_type="market",
            status="pending",
            timestamp=datetime.utcnow()
        )
        
        # 1. Validate trade
        validation_result = integrated_compliance_system.validate_trade(order)
        assert validation_result.status == ComplianceStatus.COMPLIANT
        
        # 2. Record compliance event
        integrated_compliance_system.record_compliance_event(validation_result)
        assert len(integrated_compliance_system.compliance_history) == 1
        
        # 3. Generate compliance report
        start_date = datetime.utcnow() - timedelta(hours=1)
        end_date = datetime.utcnow() + timedelta(hours=1)
        
        report = integrated_compliance_system.generate_compliance_report(
            start_date, end_date
        )
        
        assert 'metadata' in report
        assert 'data' in report
        assert report['data']['summary']['total_events'] == 1
        
        # 4. Verify audit trail
        audit_events = integrated_compliance_system.audit_trail.get_audit_trail(
            start_date, end_date
        )
        
        assert len(audit_events) == 1
        assert audit_events[0].event_type == AuditEventType.COMPLIANCE_CHECK


if __name__ == '__main__':
    pytest.main([__file__])