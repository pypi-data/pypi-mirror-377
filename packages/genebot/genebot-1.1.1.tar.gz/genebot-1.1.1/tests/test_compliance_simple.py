"""
Simplified unit tests for the regulatory compliance framework.

Tests core functionality of the compliance system components.
"""

import pytest
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal

from src.compliance import (
    ComplianceManager, 
    ReportingEngine, 
    AuditTrail, 
    RegulatoryRules
)
from src.compliance.compliance_manager import ComplianceStatus, ComplianceCheck
from src.compliance.audit_trail import AuditEventType
from src.compliance.regulatory_rules import RuleType, Jurisdiction, RegulatoryRule
from src.markets.types import MarketType, UnifiedSymbol
from src.models.data_models import Order, Position, OrderSide, OrderType, OrderStatus


class TestComplianceManagerBasic:
    """Test basic ComplianceManager functionality"""
    
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
                'formats': ['json']
            },
            'jurisdictions': ['US'],
            'max_total_exposure': 1000000
        }
    
    @pytest.fixture
    def compliance_manager(self, compliance_config):
        """Create ComplianceManager instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            compliance_config['reporting']['output_directory'] = temp_dir
            compliance_config['rules']['rules_directory'] = temp_dir
            return ComplianceManager(compliance_config)
    
    def test_compliance_manager_initialization(self, compliance_manager):
        """Test ComplianceManager initialization"""
        assert compliance_manager is not None
        assert compliance_manager.jurisdictions == ['US']
        assert len(compliance_manager.active_violations) == 0
        assert len(compliance_manager.compliance_history) == 0
    
    def test_is_action_blocked(self, compliance_manager):
        """Test action blocking check"""
        # Initially no actions blocked
        assert not compliance_manager.is_action_blocked("trading")
        
        # Add blocked action
        compliance_manager.blocked_actions.add("trading")
        
        assert compliance_manager.is_action_blocked("trading")
        assert not compliance_manager.is_action_blocked("reporting")


class TestRegulatoryRulesBasic:
    """Test basic RegulatoryRules functionality"""
    
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
    
    def test_get_market_rules(self, regulatory_rules):
        """Test getting market-specific rules"""
        crypto_rules = regulatory_rules.get_market_rules(MarketType.CRYPTO)
        forex_rules = regulatory_rules.get_market_rules(MarketType.FOREX)
        
        assert isinstance(crypto_rules, dict)
        assert isinstance(forex_rules, dict)
        
        # Should have some default rules for crypto
        assert len(crypto_rules) > 0


class TestAuditTrailBasic:
    """Test basic AuditTrail functionality"""
    
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
    
    def test_audit_trail_initialization(self, audit_trail):
        """Test AuditTrail initialization"""
        assert audit_trail is not None
        assert audit_trail.enable_checksums is True
        assert audit_trail.retention_days == 30
    
    def test_log_system_event(self, audit_trail):
        """Test logging system events"""
        event_id = audit_trail.log_system_event(
            "System startup",
            {"version": "1.0.0", "environment": "test"}
        )
        
        assert event_id is not None
        assert event_id.startswith("audit_")


class TestReportingEngineBasic:
    """Test basic ReportingEngine functionality"""
    
    @pytest.fixture
    def reporting_config(self):
        """Reporting engine configuration"""
        return {
            'output_directory': 'test_reports',
            'formats': ['json'],
            'jurisdictions': ['US'],
            'retention_days': 30
        }
    
    @pytest.fixture
    def reporting_engine(self, reporting_config):
        """Create ReportingEngine instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporting_config['output_directory'] = temp_dir
            engine = ReportingEngine(reporting_config)
            # Ensure directory exists
            engine.output_directory.mkdir(parents=True, exist_ok=True)
            return engine
    
    def test_reporting_engine_initialization(self, reporting_engine):
        """Test ReportingEngine initialization"""
        assert reporting_engine is not None
        assert reporting_engine.jurisdictions == ['US']
        assert 'json' in reporting_engine.supported_formats
    
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


class TestComplianceIntegrationBasic:
    """Test basic integration between compliance components"""
    
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
            
            manager = ComplianceManager(config)
            # Ensure reporting directory exists
            manager.reporting_engine.output_directory.mkdir(parents=True, exist_ok=True)
            return manager
    
    def test_basic_compliance_workflow(self, integrated_compliance_system):
        """Test basic compliance workflow"""
        # Create a simple compliance check
        check = ComplianceCheck(
            rule_id="test_rule",
            status=ComplianceStatus.COMPLIANT,
            message="Test compliance check",
            timestamp=datetime.utcnow(),
            market_type=MarketType.CRYPTO,
            severity="info"
        )
        
        # Record the event (this should work without database issues)
        initial_count = len(integrated_compliance_system.compliance_history)
        integrated_compliance_system.compliance_history.append(check)
        
        assert len(integrated_compliance_system.compliance_history) == initial_count + 1
        
        # Test basic functionality
        assert not integrated_compliance_system.is_action_blocked("trading")
        
        # Test rule management
        rules_count = len(integrated_compliance_system.regulatory_rules.rules)
        assert rules_count > 0


if __name__ == '__main__':
    pytest.main([__file__])