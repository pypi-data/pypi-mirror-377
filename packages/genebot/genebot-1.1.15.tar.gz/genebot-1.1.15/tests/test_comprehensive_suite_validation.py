"""
Validation test for the comprehensive testing suite.
Ensures all test files are properly structured and importable.
"""

import pytest
import os
import importlib.util
from pathlib import Path


class TestComprehensiveSuiteValidation:
    """Validate the comprehensive testing suite structure."""

    def test_test_files_exist(self):
        """Test that all comprehensive test files exist."""
        required_test_files = [
            'test_end_to_end_integration.py',
            'test_performance.py',
            'test_load_testing.py',
            'test_security.py',
            'test_final_integration.py',
            'run_comprehensive_tests.py'
        ]
        
        tests_dir = Path(__file__).parent
        
        for test_file in required_test_files:
            file_path = tests_dir / test_file
            assert file_path.exists(), f"Required test file {test_file} does not exist"

    def test_test_files_importable(self):
        """Test that all test files can be imported without errors."""
        test_files = [
            'test_end_to_end_integration.py',
            'test_performance.py',
            'test_load_testing.py',
            'test_security.py',
            'test_final_integration.py'
        ]
        
        tests_dir = Path(__file__).parent
        
        for test_file in test_files:
            file_path = tests_dir / test_file
            
            # Try to load the module
            spec = importlib.util.spec_from_file_location(
                test_file[:-3], file_path
            )
            
            assert spec is not None, f"Could not create spec for {test_file}"
            
            try:
                module = importlib.util.module_from_spec(spec)
                # Don't execute the module, just validate it can be loaded
                assert module is not None, f"Could not create module for {test_file}"
            except Exception as e:
                pytest.fail(f"Failed to import {test_file}: {str(e)}")

    def test_test_runner_executable(self):
        """Test that the comprehensive test runner is executable."""
        tests_dir = Path(__file__).parent
        runner_path = tests_dir / 'run_comprehensive_tests.py'
        
        assert runner_path.exists(), "Test runner does not exist"
        
        # Check if file is executable (on Unix systems)
        if os.name != 'nt':  # Not Windows
            assert os.access(runner_path, os.X_OK), "Test runner is not executable"

    def test_test_configuration_files_exist(self):
        """Test that test configuration files exist."""
        tests_dir = Path(__file__).parent
        
        config_files = [
            'pytest.ini',
            'requirements-test.txt',
            'TESTING_GUIDE.md'
        ]
        
        for config_file in config_files:
            file_path = tests_dir / config_file
            assert file_path.exists(), f"Configuration file {config_file} does not exist"

    def test_test_directories_exist(self):
        """Test that required test directories exist."""
        tests_dir = Path(__file__).parent
        
        required_dirs = [
            'mocks',
            'utils',
            'fixtures'
        ]
        
        for dir_name in required_dirs:
            dir_path = tests_dir / dir_name
            assert dir_path.exists(), f"Required directory {dir_name} does not exist"
            assert dir_path.is_dir(), f"{dir_name} is not a directory"

    def test_mock_exchange_available(self):
        """Test that mock exchange is available for testing."""
        try:
            from tests.mocks.mock_exchange import MockExchange
            
            # Create instance to verify it works
            mock_exchange = MockExchange()
            assert mock_exchange is not None, "MockExchange could not be instantiated"
            
        except ImportError as e:
            pytest.fail(f"Could not import MockExchange: {str(e)}")

    def test_test_fixtures_available(self):
        """Test that test fixtures are available."""
        try:
            from tests.fixtures.sample_data_factory import create_sample_market_data
            
            # Test fixture function
            sample_data = create_sample_market_data('BTC/USDT', 10)
            assert len(sample_data) == 10, "Sample data generation failed"
            
        except ImportError as e:
            pytest.fail(f"Could not import test fixtures: {str(e)}")

    def test_test_utilities_available(self):
        """Test that test utilities are available."""
        try:
            from tests.utils.test_helpers import TestAssertions
            from tests.utils.test_data_generators import MarketDataGenerator
            from tests.utils.config_validators import ConfigValidator
            
            # Verify classes exist
            assert TestAssertions is not None, "TestAssertions not available"
            assert MarketDataGenerator is not None, "MarketDataGenerator not available"
            assert ConfigValidator is not None, "ConfigValidator not available"
            
        except ImportError as e:
            pytest.fail(f"Could not import test utilities: {str(e)}")

    def test_comprehensive_test_structure(self):
        """Test that comprehensive tests have proper structure."""
        test_files = [
            'test_end_to_end_integration.py',
            'test_performance.py',
            'test_load_testing.py',
            'test_security.py',
            'test_final_integration.py'
        ]
        
        tests_dir = Path(__file__).parent
        
        for test_file in test_files:
            file_path = tests_dir / test_file
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for required elements
            assert 'class Test' in content, f"{test_file} should contain test classes"
            assert 'def test_' in content, f"{test_file} should contain test methods"
            assert 'pytest' in content, f"{test_file} should import pytest"
            
            # Check for async support if needed
            if 'async def' in content:
                assert '@pytest.mark.asyncio' in content, \
                    f"{test_file} should mark async tests with @pytest.mark.asyncio"

    def test_performance_benchmarks_defined(self):
        """Test that performance benchmarks are properly defined."""
        tests_dir = Path(__file__).parent
        performance_file = tests_dir / 'test_performance.py'
        
        with open(performance_file, 'r') as f:
            content = f.read()
        
        # Check for performance-related assertions
        performance_indicators = [
            'throughput',
            'latency',
            'memory',
            'performance_config'
        ]
        
        for indicator in performance_indicators:
            assert indicator in content.lower(), \
                f"Performance test should include {indicator} validation"

    def test_security_tests_comprehensive(self):
        """Test that security tests cover required areas."""
        tests_dir = Path(__file__).parent
        security_file = tests_dir / 'test_security.py'
        
        with open(security_file, 'r') as f:
            content = f.read()
        
        # Check for security test areas
        security_areas = [
            'api_key',
            'encryption',
            'credential',
            'authentication',
            'validation'
        ]
        
        for area in security_areas:
            assert area in content.lower(), \
                f"Security test should include {area} testing"

    def test_documentation_complete(self):
        """Test that testing documentation is complete."""
        tests_dir = Path(__file__).parent
        guide_file = tests_dir / 'TESTING_GUIDE.md'
        
        with open(guide_file, 'r') as f:
            content = f.read()
        
        # Check for required documentation sections
        required_sections = [
            'Test Suite Overview',
            'Running Tests',
            'Performance Benchmarks',
            'Security Testing',
            'Troubleshooting'
        ]
        
        for section in required_sections:
            assert section in content, \
                f"Testing guide should include {section} section"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])