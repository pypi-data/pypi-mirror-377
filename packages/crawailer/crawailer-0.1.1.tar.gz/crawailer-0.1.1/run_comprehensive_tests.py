"""
Comprehensive test runner for the Crawailer JavaScript API test suite.

This script provides multiple test execution modes for different scenarios:
- Quick smoke tests for development
- Full regression suite for releases
- Performance benchmarking
- Security penetration testing
- CI/CD pipeline integration
"""

import asyncio
import sys
import time
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import threading
import psutil


class TestSuiteRunner:
    """Orchestrates execution of the comprehensive test suite."""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {}
        self.performance_data = {}
        self.test_directory = Path(__file__).parent / "tests"
        
    def get_test_categories(self) -> Dict[str, Dict[str, Any]]:
        """Define test categories and their configurations."""
        return {
            "basic": {
                "files": ["test_basic.py", "test_javascript_api.py"],
                "description": "Basic functionality tests",
                "timeout": 300,  # 5 minutes
                "critical": True
            },
            "edge_cases": {
                "files": ["test_edge_cases.py"],
                "description": "Edge cases and error scenarios",
                "timeout": 600,  # 10 minutes
                "critical": True
            },
            "performance": {
                "files": ["test_performance_stress.py"],
                "description": "Performance and stress testing",
                "timeout": 1800,  # 30 minutes
                "critical": False
            },
            "security": {
                "files": ["test_security_penetration.py"],
                "description": "Security penetration testing",
                "timeout": 900,  # 15 minutes
                "critical": True
            },
            "compatibility": {
                "files": ["test_browser_compatibility.py"],
                "description": "Browser compatibility testing",
                "timeout": 600,  # 10 minutes
                "critical": False
            },
            "production": {
                "files": ["test_production_scenarios.py"],
                "description": "Production scenario testing",
                "timeout": 1200,  # 20 minutes
                "critical": False
            },
            "regression": {
                "files": ["test_regression_suite.py"],
                "description": "Comprehensive regression testing",
                "timeout": 900,  # 15 minutes
                "critical": True
            }
        }
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run quick smoke tests for development."""
        print("🚀 Running smoke tests...")
        
        smoke_test_markers = [
            "-m", "not slow and not integration",
            "-x",  # Stop on first failure
            "--tb=short",
            "-v"
        ]
        
        return self._execute_pytest(
            test_files=["test_basic.py"],
            extra_args=smoke_test_markers,
            timeout=120
        )
    
    def run_critical_tests(self) -> Dict[str, Any]:
        """Run critical tests that must pass for release."""
        print("🔥 Running critical tests...")
        
        categories = self.get_test_categories()
        critical_files = []
        
        for category, config in categories.items():
            if config["critical"]:
                critical_files.extend(config["files"])
        
        critical_test_markers = [
            "-x",  # Stop on first failure
            "--tb=long",
            "-v",
            "--durations=10"
        ]
        
        return self._execute_pytest(
            test_files=critical_files,
            extra_args=critical_test_markers,
            timeout=1800  # 30 minutes
        )
    
    def run_full_suite(self) -> Dict[str, Any]:
        """Run the complete test suite."""
        print("🌟 Running full comprehensive test suite...")
        
        all_results = {}
        categories = self.get_test_categories()
        
        for category, config in categories.items():
            print(f"\n📂 Running {category} tests: {config['description']}")
            
            category_args = [
                "--tb=short",
                "-v",
                f"--durations=5"
            ]
            
            # Add category-specific markers
            if category == "performance":
                category_args.extend(["-m", "performance"])
            elif category == "security":
                category_args.extend(["-m", "security"])
            
            result = self._execute_pytest(
                test_files=config["files"],
                extra_args=category_args,
                timeout=config["timeout"]
            )
            
            all_results[category] = {
                **result,
                "critical": config["critical"],
                "description": config["description"]
            }
            
            # Stop if critical test category fails
            if config["critical"] and result.get("exit_code", 0) != 0:
                print(f"❌ Critical test category '{category}' failed, stopping execution.")
                break
        
        return all_results
    
    def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmarking tests."""
        print("⚡ Running performance benchmarks...")
        
        benchmark_args = [
            "-m", "performance",
            "--tb=short",
            "-v",
            "--durations=0",  # Show all durations
            "-s"  # Don't capture output for performance monitoring
        ]
        
        # Monitor system resources during benchmark
        resource_monitor = ResourceMonitor()
        resource_monitor.start()
        
        try:
            result = self._execute_pytest(
                test_files=["test_performance_stress.py"],
                extra_args=benchmark_args,
                timeout=1800
            )
        finally:
            resource_data = resource_monitor.stop()
        
        result["resource_usage"] = resource_data
        return result
    
    def run_security_audit(self) -> Dict[str, Any]:
        """Run security penetration tests."""
        print("🔒 Running security audit...")
        
        security_args = [
            "-m", "security",
            "--tb=long",
            "-v",
            "-x"  # Stop on first security failure
        ]
        
        return self._execute_pytest(
            test_files=["test_security_penetration.py"],
            extra_args=security_args,
            timeout=900
        )
    
    def run_ci_pipeline(self) -> Dict[str, Any]:
        """Run tests optimized for CI/CD pipelines."""
        print("🤖 Running CI/CD pipeline tests...")
        
        ci_args = [
            "-m", "not slow",  # Skip slow tests in CI
            "--tb=short",
            "-v",
            "--maxfail=5",  # Stop after 5 failures
            "--durations=10",
            "--junitxml=test-results.xml"  # Generate JUnit XML for CI
        ]
        
        return self._execute_pytest(
            test_files=None,  # Run all non-slow tests
            extra_args=ci_args,
            timeout=900
        )
    
    def _execute_pytest(self, test_files: Optional[List[str]] = None, 
                       extra_args: Optional[List[str]] = None,
                       timeout: int = 600) -> Dict[str, Any]:
        """Execute pytest with specified parameters."""
        cmd = ["python", "-m", "pytest"]
        
        if test_files:
            # Add test file paths
            test_paths = [str(self.test_directory / f) for f in test_files]
            cmd.extend(test_paths)
        else:
            # Run all tests in test directory
            cmd.append(str(self.test_directory))
        
        if extra_args:
            cmd.extend(extra_args)
        
        start_time = time.time()
        
        try:
            print(f"💻 Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path(__file__).parent
            )
            
            execution_time = time.time() - start_time
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "success": result.returncode == 0,
                "command": " ".join(cmd)
            }
            
        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            return {
                "exit_code": -1,
                "stdout": e.stdout.decode() if e.stdout else "",
                "stderr": e.stderr.decode() if e.stderr else "",
                "execution_time": execution_time,
                "success": False,
                "error": f"Test execution timed out after {timeout} seconds",
                "command": " ".join(cmd)
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "exit_code": -2,
                "stdout": "",
                "stderr": str(e),
                "execution_time": execution_time,
                "success": False,
                "error": f"Test execution failed: {str(e)}",
                "command": " ".join(cmd)
            }
    
    def generate_report(self, results: Dict[str, Any], report_type: str = "full") -> str:
        """Generate a comprehensive test report."""
        total_time = time.time() - self.start_time
        
        report = []
        report.append("=" * 80)
        report.append(f"Crawailer JavaScript API Test Suite Report - {report_type.title()}")
        report.append("=" * 80)
        report.append(f"Execution Time: {total_time:.2f} seconds")
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if isinstance(results, dict) and "exit_code" in results:
            # Single test run result
            self._add_single_result_to_report(report, results, report_type)
        else:
            # Multiple test categories
            self._add_multiple_results_to_report(report, results)
        
        # Add summary
        report.append("\n" + "=" * 80)
        report.append("SUMMARY")
        report.append("=" * 80)
        
        if isinstance(results, dict) and "exit_code" in results:
            status = "✅ PASSED" if results["success"] else "❌ FAILED"
            report.append(f"Overall Status: {status}")
        else:
            total_categories = len(results)
            passed_categories = sum(1 for r in results.values() if r.get("success", False))
            critical_failures = sum(1 for r in results.values() 
                                  if r.get("critical", False) and not r.get("success", False))
            
            report.append(f"Total Categories: {total_categories}")
            report.append(f"Passed Categories: {passed_categories}")
            report.append(f"Failed Categories: {total_categories - passed_categories}")
            report.append(f"Critical Failures: {critical_failures}")
            
            overall_status = "✅ PASSED" if critical_failures == 0 else "❌ FAILED"
            report.append(f"Overall Status: {overall_status}")
        
        return "\n".join(report)
    
    def _add_single_result_to_report(self, report: List[str], result: Dict[str, Any], test_type: str):
        """Add single test result to report."""
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        report.append(f"Test Type: {test_type}")
        report.append(f"Status: {status}")
        report.append(f"Execution Time: {result['execution_time']:.2f} seconds")
        report.append(f"Exit Code: {result['exit_code']}")
        
        if result.get("error"):
            report.append(f"Error: {result['error']}")
        
        if result.get("resource_usage"):
            resource = result["resource_usage"]
            report.append("\nResource Usage:")
            report.append(f"  Peak CPU: {resource.get('peak_cpu', 0):.1f}%")
            report.append(f"  Peak Memory: {resource.get('peak_memory', 0):.1f}%")
            report.append(f"  Peak Threads: {resource.get('peak_threads', 0)}")
        
        if result["stdout"]:
            report.append("\nTest Output:")
            report.append("-" * 40)
            # Show last 20 lines of output
            output_lines = result["stdout"].split("\n")
            if len(output_lines) > 20:
                report.append("... (truncated)")
                output_lines = output_lines[-20:]
            report.extend(output_lines)
    
    def _add_multiple_results_to_report(self, report: List[str], results: Dict[str, Any]):
        """Add multiple test results to report."""
        for category, result in results.items():
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            critical = "🔥 CRITICAL" if result.get("critical", False) else "📝 Optional"
            
            report.append(f"{category.upper()}: {status} {critical}")
            report.append(f"  Description: {result.get('description', 'N/A')}")
            report.append(f"  Execution Time: {result.get('execution_time', 0):.2f} seconds")
            
            if result.get("error"):
                report.append(f"  Error: {result['error']}")
            
            # Parse test output for quick stats
            stdout = result.get("stdout", "")
            if "passed" in stdout and "failed" in stdout:
                # Extract pytest summary
                lines = stdout.split("\n")
                for line in lines:
                    if "passed" in line and ("failed" in line or "error" in line):
                        report.append(f"  Tests: {line.strip()}")
                        break
            
            report.append("")
    
    def save_results(self, results: Dict[str, Any], filename: str = "test_results.json"):
        """Save test results to JSON file."""
        output_file = Path(__file__).parent / filename
        
        # Prepare serializable data
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                serializable_results[key] = {
                    k: v for k, v in value.items() 
                    if isinstance(v, (str, int, float, bool, list, dict, type(None)))
                }
            else:
                serializable_results[key] = value
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_execution_time": time.time() - self.start_time,
                "results": serializable_results
            }, f, indent=2)
        
        print(f"📁 Results saved to: {output_file}")


class ResourceMonitor:
    """Monitor system resources during test execution."""
    
    def __init__(self):
        self.monitoring = False
        self.data = {
            "peak_cpu": 0,
            "peak_memory": 0,
            "peak_threads": 0,
            "samples": []
        }
        self.monitor_thread = None
    
    def start(self):
        """Start resource monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop(self) -> Dict[str, Any]:
        """Stop monitoring and return collected data."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        return self.data
    
    def _monitor_loop(self):
        """Resource monitoring loop."""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                thread_count = threading.active_count()
                
                self.data["peak_cpu"] = max(self.data["peak_cpu"], cpu_percent)
                self.data["peak_memory"] = max(self.data["peak_memory"], memory_percent)
                self.data["peak_threads"] = max(self.data["peak_threads"], thread_count)
                
                self.data["samples"].append({
                    "timestamp": time.time(),
                    "cpu": cpu_percent,
                    "memory": memory_percent,
                    "threads": thread_count
                })
                
                time.sleep(1)  # Sample every second
                
            except Exception:
                # Ignore monitoring errors
                pass


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for Crawailer JavaScript API"
    )
    
    parser.add_argument(
        "mode",
        choices=["smoke", "critical", "full", "performance", "security", "ci"],
        help="Test execution mode"
    )
    
    parser.add_argument(
        "--save-results",
        action="store_true",
        help="Save test results to JSON file"
    )
    
    parser.add_argument(
        "--report-file",
        type=str,
        help="Save report to specified file"
    )
    
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip generating detailed report"
    )
    
    args = parser.parse_args()
    
    runner = TestSuiteRunner()
    
    try:
        # Execute tests based on mode
        if args.mode == "smoke":
            results = runner.run_smoke_tests()
        elif args.mode == "critical":
            results = runner.run_critical_tests()
        elif args.mode == "full":
            results = runner.run_full_suite()
        elif args.mode == "performance":
            results = runner.run_performance_benchmark()
        elif args.mode == "security":
            results = runner.run_security_audit()
        elif args.mode == "ci":
            results = runner.run_ci_pipeline()
        else:
            print(f"❌ Unknown mode: {args.mode}")
            sys.exit(1)
        
        # Save results if requested
        if args.save_results:
            runner.save_results(results, f"test_results_{args.mode}.json")
        
        # Generate and display report
        if not args.no_report:
            report = runner.generate_report(results, args.mode)
            print("\n" + report)
            
            if args.report_file:
                with open(args.report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"📄 Report saved to: {args.report_file}")
        
        # Exit with appropriate code
        if isinstance(results, dict) and "success" in results:
            sys.exit(0 if results["success"] else 1)
        else:
            # Multiple categories - check for critical failures
            critical_failures = sum(1 for r in results.values() 
                                  if r.get("critical", False) and not r.get("success", False))
            sys.exit(0 if critical_failures == 0 else 1)
            
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Unexpected error during test execution: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()