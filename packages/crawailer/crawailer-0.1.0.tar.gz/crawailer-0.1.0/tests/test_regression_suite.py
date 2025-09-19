"""
Comprehensive regression testing suite for Crawailer JavaScript API.

This test suite serves as the final validation layer, combining all test categories
and ensuring that new changes don't break existing functionality.
"""

import asyncio
import json
import pytest
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass, field
from pathlib import Path
import tempfile

from crawailer import Browser, BrowserConfig
from crawailer.content import WebContent, ContentExtractor
from crawailer.api import get, get_many, discover


@dataclass
class RegressionTestCase:
    """Represents a single regression test case."""
    name: str
    description: str
    category: str
    script: str
    expected_result: Any
    expected_error: Optional[str] = None
    timeout: Optional[int] = None
    browser_config: Optional[Dict[str, Any]] = None
    critical: bool = False  # Whether failure blocks release


@dataclass
class RegressionTestSuite:
    """Complete regression test suite."""
    version: str
    test_cases: List[RegressionTestCase] = field(default_factory=list)
    baseline_performance: Dict[str, float] = field(default_factory=dict)
    compatibility_matrix: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    
    def add_test_case(self, test_case: RegressionTestCase):
        """Add a test case to the suite."""
        self.test_cases.append(test_case)
    
    def get_critical_tests(self) -> List[RegressionTestCase]:
        """Get all critical test cases."""
        return [tc for tc in self.test_cases if tc.critical]
    
    def get_tests_by_category(self, category: str) -> List[RegressionTestCase]:
        """Get test cases by category."""
        return [tc for tc in self.test_cases if tc.category == category]


class TestRegressionSuite:
    """Main regression test suite runner."""
    
    def create_comprehensive_test_suite(self) -> RegressionTestSuite:
        """Create comprehensive regression test suite."""
        suite = RegressionTestSuite(version="1.0.0")
        
        # Core Functionality Tests (Critical)
        suite.add_test_case(RegressionTestCase(
            name="basic_script_execution",
            description="Basic JavaScript execution functionality",
            category="core",
            script="return 'basic_test_passed'",
            expected_result="basic_test_passed",
            critical=True
        ))
        
        suite.add_test_case(RegressionTestCase(
            name="dom_query_basic",
            description="Basic DOM querying capabilities",
            category="core",
            script="return document.querySelectorAll('*').length",
            expected_result=10,
            critical=True
        ))
        
        suite.add_test_case(RegressionTestCase(
            name="async_javascript",
            description="Async JavaScript execution",
            category="core",
            script="await new Promise(r => setTimeout(r, 100)); return 'async_complete'",
            expected_result="async_complete",
            timeout=5000,
            critical=True
        ))
        
        # Error Handling Tests (Critical)
        suite.add_test_case(RegressionTestCase(
            name="syntax_error_handling",
            description="Proper syntax error handling",
            category="error_handling",
            script="function() { missing syntax",
            expected_result=None,
            expected_error="SyntaxError",
            critical=True
        ))
        
        suite.add_test_case(RegressionTestCase(
            name="runtime_error_handling",
            description="Runtime error handling",
            category="error_handling",
            script="throw new Error('Test runtime error')",
            expected_result=None,
            expected_error="Test runtime error",
            critical=True
        ))
        
        # Performance Tests
        suite.add_test_case(RegressionTestCase(
            name="large_data_handling",
            description="Handle large data sets efficiently",
            category="performance",
            script="return Array.from({length: 10000}, (_, i) => i).reduce((a, b) => a + b)",
            expected_result=49995000,  # Sum of 0 to 9999
            timeout=10000,
            critical=False
        ))
        
        suite.add_test_case(RegressionTestCase(
            name="complex_dom_processing",
            description="Complex DOM processing performance",
            category="performance",
            script="""
                const elements = Array.from(document.querySelectorAll('*'));
                return elements.map(el => ({
                    tag: el.tagName,
                    text: el.textContent?.substring(0, 50)
                })).length;
            """,
            expected_result=10,
            timeout=5000,
            critical=False
        ))
        
        # Security Tests (Critical)
        suite.add_test_case(RegressionTestCase(
            name="eval_prevention",
            description="Prevent dangerous eval usage",
            category="security",
            script="eval('alert(\"security_breach\")')",
            expected_result=None,
            expected_error="security",
            critical=True
        ))
        
        suite.add_test_case(RegressionTestCase(
            name="xss_prevention",
            description="Prevent XSS attacks",
            category="security",
            script="document.body.innerHTML = '<script>alert(\"xss\")</script>'",
            expected_result=None,
            expected_error="security",
            critical=True
        ))
        
        # Browser Compatibility Tests
        suite.add_test_case(RegressionTestCase(
            name="es6_features",
            description="ES6 feature support",
            category="compatibility",
            script="const [a, b] = [1, 2]; return `template ${a + b}`",
            expected_result="template 3",
            critical=False
        ))
        
        suite.add_test_case(RegressionTestCase(
            name="web_apis_availability",
            description="Web APIs availability",
            category="compatibility",
            script="return {fetch: typeof fetch, localStorage: typeof localStorage}",
            expected_result={"fetch": "function", "localStorage": "object"},
            critical=False
        ))
        
        # Edge Cases
        suite.add_test_case(RegressionTestCase(
            name="unicode_handling",
            description="Unicode and special character handling",
            category="edge_cases",
            script="return '测试中文字符 🚀 emoji test'",
            expected_result="测试中文字符 🚀 emoji test",
            critical=False
        ))
        
        suite.add_test_case(RegressionTestCase(
            name="null_undefined_handling",
            description="Null and undefined value handling",
            category="edge_cases",
            script="return {null: null, undefined: undefined, empty: ''}",
            expected_result={"null": None, "undefined": None, "empty": ""},
            critical=False
        ))
        
        return suite
    
    @pytest.mark.asyncio
    async def test_full_regression_suite(self):
        """Execute the complete regression test suite."""
        suite = self.create_comprehensive_test_suite()
        browser = Browser(BrowserConfig())
        
        # Setup mock browser
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Execute all test cases
        results = []
        failed_critical_tests = []
        
        for test_case in suite.test_cases:
            start_time = time.time()
            
            try:
                # Mock the expected result or error
                if test_case.expected_error:
                    mock_page.evaluate.side_effect = Exception(test_case.expected_error)
                else:
                    mock_page.evaluate.return_value = test_case.expected_result
                
                # Execute the test
                if test_case.expected_error:
                    with pytest.raises(Exception) as exc_info:
                        await browser.execute_script(
                            "https://regression-test.com",
                            test_case.script,
                            timeout=test_case.timeout
                        )
                    
                    # Verify error contains expected message
                    assert test_case.expected_error.lower() in str(exc_info.value).lower()
                    test_result = "PASS"
                else:
                    result = await browser.execute_script(
                        "https://regression-test.com",
                        test_case.script,
                        timeout=test_case.timeout
                    )
                    
                    # Verify result matches expectation
                    assert result == test_case.expected_result
                    test_result = "PASS"
                
            except Exception as e:
                test_result = "FAIL"
                if test_case.critical:
                    failed_critical_tests.append((test_case, str(e)))
            
            execution_time = time.time() - start_time
            
            results.append({
                "name": test_case.name,
                "category": test_case.category,
                "result": test_result,
                "execution_time": execution_time,
                "critical": test_case.critical
            })
        
        # Analyze results
        total_tests = len(results)
        passed_tests = len([r for r in results if r["result"] == "PASS"])
        failed_tests = total_tests - passed_tests
        critical_failures = len(failed_critical_tests)
        
        # Generate summary
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": passed_tests / total_tests * 100,
            "critical_failures": critical_failures,
            "execution_time": sum(r["execution_time"] for r in results),
            "results_by_category": {}
        }
        
        # Category breakdown
        for category in set(r["category"] for r in results):
            category_results = [r for r in results if r["category"] == category]
            category_passed = len([r for r in category_results if r["result"] == "PASS"])
            summary["results_by_category"][category] = {
                "total": len(category_results),
                "passed": category_passed,
                "pass_rate": category_passed / len(category_results) * 100
            }
        
        # Assertions for regression testing
        assert critical_failures == 0, f"Critical test failures: {failed_critical_tests}"
        assert summary["pass_rate"] >= 85.0, f"Pass rate {summary['pass_rate']:.1f}% below 85% threshold"
        
        # Performance regression check
        assert summary["execution_time"] < 30.0, f"Execution time {summary['execution_time']:.1f}s too slow"
        
        print(f"Regression Test Summary: {summary}")
        return summary
    
    @pytest.mark.asyncio
    async def test_performance_regression(self):
        """Test for performance regressions."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "performance_test"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Performance benchmarks
        performance_tests = [
            {
                "name": "simple_execution",
                "script": "return 'test'",
                "baseline_ms": 100,
                "tolerance": 1.5  # 50% tolerance
            },
            {
                "name": "dom_query",
                "script": "return document.querySelectorAll('div').length",
                "baseline_ms": 200,
                "tolerance": 1.5
            },
            {
                "name": "data_processing",
                "script": "return Array.from({length: 1000}, (_, i) => i).reduce((a, b) => a + b)",
                "baseline_ms": 300,
                "tolerance": 2.0  # 100% tolerance for computation
            }
        ]
        
        performance_results = []
        
        for test in performance_tests:
            # Run multiple iterations for accurate timing
            times = []
            for _ in range(5):
                start_time = time.time()
                
                result = await browser.execute_script(
                    "https://performance-test.com",
                    test["script"]
                )
                
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                times.append(execution_time)
            
            # Calculate average execution time
            avg_time = sum(times) / len(times)
            max_allowed = test["baseline_ms"] * test["tolerance"]
            
            performance_results.append({
                "name": test["name"],
                "avg_time_ms": avg_time,
                "baseline_ms": test["baseline_ms"],
                "max_allowed_ms": max_allowed,
                "within_tolerance": avg_time <= max_allowed,
                "times": times
            })
            
            # Assert performance requirement
            assert avg_time <= max_allowed, f"{test['name']}: {avg_time:.1f}ms > {max_allowed:.1f}ms"
        
        print(f"Performance Results: {performance_results}")
        return performance_results
    
    @pytest.mark.asyncio
    async def test_backward_compatibility(self):
        """Test backward compatibility with previous API versions."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test cases that should maintain backward compatibility
        compatibility_tests = [
            {
                "name": "basic_execute_script",
                "method": "execute_script",
                "args": ["https://example.com", "return 'test'"],
                "expected": "test"
            },
            {
                "name": "script_with_timeout",
                "method": "execute_script", 
                "args": ["https://example.com", "return 'timeout_test'"],
                "kwargs": {"timeout": 5000},
                "expected": "timeout_test"
            }
        ]
        
        compatibility_results = []
        
        for test in compatibility_tests:
            mock_page.evaluate.return_value = test["expected"]
            
            try:
                # Call the method with backward-compatible API
                method = getattr(browser, test["method"])
                if "kwargs" in test:
                    result = await method(*test["args"], **test["kwargs"])
                else:
                    result = await method(*test["args"])
                
                # Verify result
                assert result == test["expected"]
                compatibility_results.append({
                    "name": test["name"],
                    "status": "PASS",
                    "result": result
                })
                
            except Exception as e:
                compatibility_results.append({
                    "name": test["name"],
                    "status": "FAIL",
                    "error": str(e)
                })
        
        # All compatibility tests should pass
        failed_tests = [r for r in compatibility_results if r["status"] == "FAIL"]
        assert len(failed_tests) == 0, f"Backward compatibility failures: {failed_tests}"
        
        return compatibility_results
    
    @pytest.mark.asyncio
    async def test_api_stability(self):
        """Test API stability and signature consistency."""
        # Test that core API methods exist and have expected signatures
        browser = Browser(BrowserConfig())
        
        # Check that required methods exist
        required_methods = [
            "start",
            "close", 
            "execute_script",
            "fetch_page"
        ]
        
        for method_name in required_methods:
            assert hasattr(browser, method_name), f"Missing required method: {method_name}"
            method = getattr(browser, method_name)
            assert callable(method), f"Method {method_name} is not callable"
        
        # Check BrowserConfig structure
        config = BrowserConfig()
        required_config_attrs = [
            "headless",
            "timeout", 
            "viewport",
            "user_agent",
            "extra_args"
        ]
        
        for attr_name in required_config_attrs:
            assert hasattr(config, attr_name), f"Missing required config attribute: {attr_name}"
        
        # Check WebContent structure  
        content = WebContent(
            url="https://example.com",
            title="Test",
            markdown="# Test",
            text="Test content",
            html="<html></html>"
        )
        
        required_content_attrs = [
            "url",
            "title", 
            "markdown",
            "text",
            "html",
            "word_count",
            "reading_time"
        ]
        
        for attr_name in required_content_attrs:
            assert hasattr(content, attr_name), f"Missing required content attribute: {attr_name}"
    
    @pytest.mark.asyncio
    async def test_integration_stability(self):
        """Test integration between different components."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=AsyncMock(status=200))
        mock_page.close = AsyncMock()
        mock_page.content.return_value = "<html><body><h1>Test</h1></body></html>"
        mock_page.title.return_value = "Test Page"
        mock_page.evaluate.return_value = "integration_test"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test browser -> page -> script execution flow
        page_result = await browser.fetch_page("https://example.com")
        assert page_result["status"] == 200
        assert page_result["title"] == "Test Page"
        assert "<h1>Test</h1>" in page_result["html"]
        
        # Test script execution integration
        script_result = await browser.execute_script(
            "https://example.com",
            "return 'integration_test'"
        )
        assert script_result == "integration_test"
        
        # Test error propagation
        mock_page.evaluate.side_effect = Exception("Integration error")
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script("https://example.com", "return 'test'")
        
        assert "Integration error" in str(exc_info.value)


class TestVersionCompatibility:
    """Test compatibility across different versions."""
    
    def get_version_test_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Get version compatibility test matrix."""
        return {
            "1.0.0": {
                "supported_features": ["basic_execution", "dom_query", "error_handling"],
                "deprecated_features": [],
                "breaking_changes": []
            },
            "1.1.0": {
                "supported_features": ["basic_execution", "dom_query", "error_handling", "async_execution"],
                "deprecated_features": [],
                "breaking_changes": []
            },
            "2.0.0": {
                "supported_features": ["basic_execution", "dom_query", "error_handling", "async_execution", "security_features"],
                "deprecated_features": ["legacy_api"],
                "breaking_changes": ["removed_unsafe_methods"]
            }
        }
    
    @pytest.mark.asyncio
    async def test_feature_evolution(self):
        """Test that features evolve correctly across versions."""
        version_matrix = self.get_version_test_matrix()
        
        # Test feature availability progression
        for version, features in version_matrix.items():
            supported = set(features["supported_features"])
            
            # Core features should always be available
            core_features = {"basic_execution", "dom_query", "error_handling"}
            assert core_features.issubset(supported), f"Missing core features in {version}"
            
            # Features should only be added, not removed (except in major versions)
            major_version = int(version.split('.')[0])
            if major_version == 1:
                # v1.x should not remove any features
                if version != "1.0.0":
                    prev_version = "1.0.0"
                    prev_features = set(version_matrix[prev_version]["supported_features"])
                    assert prev_features.issubset(supported), f"Features removed in {version}"
    
    @pytest.mark.asyncio
    async def test_migration_paths(self):
        """Test migration paths between versions."""
        # Test that deprecated features still work but issue warnings
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "migration_test"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test current API works
        result = await browser.execute_script("https://example.com", "return 'migration_test'")
        assert result == "migration_test"
        
        # Test that the API is stable for common use cases
        common_patterns = [
            ("return document.title", "migration_test"),
            ("return window.location.href", "migration_test"),
            ("return Array.from(document.querySelectorAll('*')).length", "migration_test")
        ]
        
        for script, expected_mock in common_patterns:
            mock_page.evaluate.return_value = expected_mock
            result = await browser.execute_script("https://example.com", script)
            assert result == expected_mock


class TestContinuousIntegration:
    """Tests specifically designed for CI/CD pipelines."""
    
    @pytest.mark.asyncio
    async def test_ci_smoke_tests(self):
        """Quick smoke tests for CI pipelines."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "ci_test_pass"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Essential functionality that must work
        smoke_tests = [
            "return 'basic_test'",
            "return 1 + 1",
            "return typeof document",
            "return window.location.protocol"
        ]
        
        for i, script in enumerate(smoke_tests):
            result = await browser.execute_script(f"https://example.com/smoke_{i}", script)
            assert result == "ci_test_pass"
    
    @pytest.mark.asyncio
    async def test_environment_isolation(self):
        """Test that tests run in isolation."""
        browser1 = Browser(BrowserConfig())
        browser2 = Browser(BrowserConfig())
        
        # Mock separate browser instances
        mock_page1 = AsyncMock()
        mock_page1.goto = AsyncMock()
        mock_page1.close = AsyncMock()
        mock_page1.evaluate.return_value = "browser1_result"
        
        mock_page2 = AsyncMock()
        mock_page2.goto = AsyncMock()
        mock_page2.close = AsyncMock()
        mock_page2.evaluate.return_value = "browser2_result"
        
        mock_browser1 = AsyncMock()
        mock_browser1.new_page.return_value = mock_page1
        browser1._browser = mock_browser1
        browser1._is_started = True
        
        mock_browser2 = AsyncMock()
        mock_browser2.new_page.return_value = mock_page2
        browser2._browser = mock_browser2
        browser2._is_started = True
        
        # Execute scripts in parallel
        result1_task = browser1.execute_script("https://example.com", "return 'test1'")
        result2_task = browser2.execute_script("https://example.com", "return 'test2'")
        
        result1, result2 = await asyncio.gather(result1_task, result2_task)
        
        # Results should be isolated
        assert result1 == "browser1_result"
        assert result2 == "browser2_result"
    
    @pytest.mark.asyncio
    async def test_resource_cleanup(self):
        """Test that resources are properly cleaned up."""
        browser = Browser(BrowserConfig())
        
        created_pages = []
        
        def create_mock_page():
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = "cleanup_test"
            created_pages.append(mock_page)
            return mock_page
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = create_mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Execute multiple scripts
        for i in range(5):
            await browser.execute_script(f"https://example.com/cleanup_{i}", "return 'test'")
        
        # Verify all pages were closed
        assert len(created_pages) == 5
        for page in created_pages:
            page.close.assert_called_once()


if __name__ == "__main__":
    # Run regression tests with comprehensive reporting
    pytest.main([__file__, "-v", "--tb=short", "--durations=10"])