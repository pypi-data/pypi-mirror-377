"""
Performance and stress testing for Crawailer JavaScript API.

This test suite focuses on performance characteristics, stress testing,
resource usage, and ensuring the system can handle production workloads.
"""

import asyncio
import time
import pytest
import psutil
import threading
import gc
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed
import memory_profiler

from crawailer import Browser, BrowserConfig
from crawailer.content import WebContent, ContentExtractor
from crawailer.api import get, get_many, discover


class PerformanceMetrics:
    """Helper class to collect and analyze performance metrics."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.cpu_usage = []
        self.active_threads = []
        
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.memory_usage = [psutil.virtual_memory().percent]
        self.cpu_usage = [psutil.cpu_percent()]
        self.active_threads = [threading.active_count()]
        
    def stop_monitoring(self):
        """Stop monitoring and calculate metrics."""
        self.end_time = time.time()
        self.memory_usage.append(psutil.virtual_memory().percent)
        self.cpu_usage.append(psutil.cpu_percent())
        self.active_threads.append(threading.active_count())
        
    @property
    def duration(self):
        """Total execution duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    @property
    def memory_delta(self):
        """Memory usage change in percentage."""
        if len(self.memory_usage) >= 2:
            return self.memory_usage[-1] - self.memory_usage[0]
        return 0
    
    @property
    def avg_cpu_usage(self):
        """Average CPU usage during test."""
        return sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
    
    @property
    def thread_delta(self):
        """Change in active thread count."""
        if len(self.active_threads) >= 2:
            return self.active_threads[-1] - self.active_threads[0]
        return 0


class TestLargeScriptExecution:
    """Test execution of large JavaScript code and large result handling."""
    
    @pytest.mark.asyncio
    async def test_very_large_javascript_code(self):
        """Test execution of very large JavaScript code (>100KB)."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "large_script_executed"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Generate a large JavaScript script (100KB+)
        base_script = """
        function processLargeDataSet() {
            var results = [];
            for (let i = 0; i < 10000; i++) {
                results.push({
                    id: i,
                    value: Math.random(),
                    processed: true,
                    metadata: {
                        timestamp: Date.now(),
                        category: 'test_data_' + (i % 100)
                    }
                });
            }
            return 'large_script_executed';
        }
        """
        
        # Repeat the function many times to create a large script
        large_script = (base_script + "\n") * 100 + "return processLargeDataSet();"
        
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # Execute the large script
        result = await browser.execute_script("https://example.com", large_script)
        
        metrics.stop_monitoring()
        
        assert result == "large_script_executed"
        # Script should execute within reasonable time (10 seconds max)
        assert metrics.duration < 10.0
        
    @pytest.mark.asyncio
    async def test_large_result_data_handling(self):
        """Test handling of JavaScript that returns very large data (>10MB)."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Generate large result data (10MB array)
        large_array = ["x" * 1000 for _ in range(10000)]  # 10MB of data
        mock_page.evaluate.return_value = large_array
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        script = """
        // Generate large array
        var largeArray = [];
        for (let i = 0; i < 10000; i++) {
            largeArray.push('x'.repeat(1000));
        }
        return largeArray;
        """
        
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        result = await browser.execute_script("https://example.com", script)
        
        metrics.stop_monitoring()
        
        assert len(result) == 10000
        assert len(result[0]) == 1000
        # Should handle large data efficiently
        assert metrics.duration < 30.0
        
    @pytest.mark.asyncio
    async def test_complex_dom_processing(self):
        """Test performance with complex DOM processing operations."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock complex DOM processing result
        complex_result = {
            "elements_found": 5000,
            "text_extracted": "x" * 50000,  # 50KB of text
            "links": [f"https://example.com/page{i}" for i in range(1000)],
            "processing_time": 150  # milliseconds
        }
        mock_page.evaluate.return_value = complex_result
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        script = """
        // Complex DOM processing
        const startTime = performance.now();
        
        // Process all elements
        const allElements = document.querySelectorAll('*');
        const elementData = Array.from(allElements).map(el => ({
            tag: el.tagName,
            text: el.textContent?.substring(0, 100),
            attributes: Array.from(el.attributes).map(attr => ({
                name: attr.name,
                value: attr.value
            }))
        }));
        
        // Extract all links
        const links = Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
        
        // Extract all text content
        const textContent = document.body.textContent;
        
        const processingTime = performance.now() - startTime;
        
        return {
            elements_found: elementData.length,
            text_extracted: textContent,
            links: links,
            processing_time: processingTime
        };
        """
        
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        result = await browser.execute_script("https://example.com", script)
        
        metrics.stop_monitoring()
        
        assert result["elements_found"] == 5000
        assert len(result["text_extracted"]) == 50000
        assert len(result["links"]) == 1000
        # Should complete within reasonable time
        assert metrics.duration < 5.0


class TestHighConcurrencyStress:
    """Test system behavior under high concurrency loads."""
    
    @pytest.mark.asyncio
    async def test_concurrent_script_execution_100(self):
        """Test 100 concurrent JavaScript executions."""
        browser = Browser(BrowserConfig())
        
        # Create 100 mock pages
        mock_pages = []
        for i in range(100):
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = f"result_{i}"
            mock_pages.append(mock_page)
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = mock_pages
        browser._browser = mock_browser
        browser._is_started = True
        
        async def execute_single_script(index):
            """Execute a single script with timing."""
            start_time = time.time()
            result = await browser.execute_script(
                f"https://example.com/page{index}",
                f"return 'result_{index}'"
            )
            duration = time.time() - start_time
            return {"result": result, "duration": duration, "index": index}
        
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # Launch 100 concurrent executions
        tasks = [execute_single_script(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics.stop_monitoring()
        
        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        # At least 80% should succeed
        success_rate = len(successful_results) / len(results)
        assert success_rate >= 0.8, f"Success rate {success_rate:.2%} below 80%"
        
        # Check performance characteristics
        if successful_results:
            durations = [r["duration"] for r in successful_results]
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            # Average should be reasonable
            assert avg_duration < 2.0, f"Average duration {avg_duration:.2f}s too high"
            assert max_duration < 10.0, f"Max duration {max_duration:.2f}s too high"
        
        # Overall test should complete within reasonable time
        assert metrics.duration < 60.0
        
    @pytest.mark.asyncio
    async def test_memory_usage_under_stress(self):
        """Test memory usage patterns under stress conditions."""
        browser = Browser(BrowserConfig())
        
        # Setup mock browser with memory tracking
        created_pages = []
        
        def create_page_with_memory():
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = "x" * 10000  # 10KB result per call
            created_pages.append(mock_page)
            return mock_page
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = create_page_with_memory
        browser._browser = mock_browser
        browser._is_started = True
        
        # Track memory usage
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_readings = [initial_memory]
        
        # Execute scripts in batches to monitor memory
        for batch in range(10):  # 10 batches of 10 scripts each
            batch_tasks = []
            for i in range(10):
                script_index = batch * 10 + i
                task = browser.execute_script(
                    f"https://example.com/page{script_index}",
                    f"return 'x'.repeat(10000)"  # Generate 10KB string
                )
                batch_tasks.append(task)
            
            # Execute batch
            await asyncio.gather(*batch_tasks)
            
            # Force garbage collection and measure memory
            gc.collect()
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_readings.append(current_memory)
            
            # Brief pause between batches
            await asyncio.sleep(0.1)
        
        final_memory = memory_readings[-1]
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 500MB for 100 operations)
        assert memory_growth < 500, f"Memory growth {memory_growth:.1f}MB too high"
        
        # All pages should have been closed
        assert len(created_pages) == 100
        for page in created_pages:
            page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_thread_pool_stress(self):
        """Test thread pool behavior under stress."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "thread_test_result"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        initial_thread_count = threading.active_count()
        max_thread_count = initial_thread_count
        
        async def monitor_threads():
            """Monitor thread count during execution."""
            nonlocal max_thread_count
            while True:
                current_count = threading.active_count()
                max_thread_count = max(max_thread_count, current_count)
                await asyncio.sleep(0.1)
        
        # Start thread monitoring
        monitor_task = asyncio.create_task(monitor_threads())
        
        try:
            # Execute many concurrent operations
            tasks = []
            for i in range(50):
                task = browser.execute_script(
                    f"https://example.com/thread_test_{i}",
                    "return 'thread_test_result'"
                )
                tasks.append(task)
            
            # Execute all tasks
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 50
            assert all(r == "thread_test_result" for r in results)
            
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        # Thread count should return to near original after completion
        await asyncio.sleep(1)  # Allow cleanup time
        final_thread_count = threading.active_count()
        thread_growth = final_thread_count - initial_thread_count
        
        # Some growth is expected but should be bounded
        assert thread_growth < 20, f"Thread growth {thread_growth} too high"
        
        # Max threads during execution should be reasonable
        max_growth = max_thread_count - initial_thread_count
        assert max_growth < 100, f"Max thread growth {max_growth} too high"


class TestLongRunningScriptTimeouts:
    """Test timeout handling and long-running script scenarios."""
    
    @pytest.mark.asyncio
    async def test_script_timeout_precision(self):
        """Test precision of timeout handling."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Simulate timeout after specified delay
        async def simulate_timeout(delay_ms):
            await asyncio.sleep(delay_ms / 1000)
            raise asyncio.TimeoutError(f"Script timeout after {delay_ms}ms")
        
        mock_page.evaluate.side_effect = lambda script: simulate_timeout(1500)
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test timeout with 1 second limit
        start_time = time.time()
        
        with pytest.raises(asyncio.TimeoutError):
            await browser.execute_script(
                "https://example.com",
                "await new Promise(r => setTimeout(r, 5000))",  # 5 second script
                timeout=1000  # 1 second timeout
            )
        
        actual_duration = time.time() - start_time
        
        # Should timeout close to the specified time (within 500ms tolerance)
        assert 0.8 < actual_duration < 2.0, f"Timeout duration {actual_duration:.2f}s not precise"
    
    @pytest.mark.asyncio
    async def test_multiple_timeout_scenarios(self):
        """Test various timeout scenarios."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        timeout_scenarios = [
            (100, "very_short"),    # 100ms - very short
            (500, "short"),         # 500ms - short
            (2000, "medium"),       # 2s - medium  
            (5000, "long"),         # 5s - long
        ]
        
        for timeout_ms, scenario_name in timeout_scenarios:
            # Mock timeout behavior
            mock_page.evaluate.side_effect = asyncio.TimeoutError(
                f"Timeout in {scenario_name} scenario"
            )
            
            start_time = time.time()
            
            with pytest.raises(asyncio.TimeoutError):
                await browser.execute_script(
                    f"https://example.com/{scenario_name}",
                    f"await new Promise(r => setTimeout(r, {timeout_ms * 2}))",
                    timeout=timeout_ms
                )
            
            duration = time.time() - start_time
            expected_duration = timeout_ms / 1000
            
            # Duration should be close to expected (50% tolerance)
            tolerance = expected_duration * 0.5
            assert (expected_duration - tolerance) <= duration <= (expected_duration + tolerance * 3)
    
    @pytest.mark.asyncio
    async def test_timeout_cleanup_and_recovery(self):
        """Test that timeouts don't leak resources and allow recovery."""
        browser = Browser(BrowserConfig())
        
        timeout_pages = []
        success_pages = []
        
        def create_timeout_page():
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.side_effect = asyncio.TimeoutError("Script timeout")
            timeout_pages.append(mock_page)
            return mock_page
        
        def create_success_page():
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = "success"
            success_pages.append(mock_page)
            return mock_page
        
        # Alternate between timeout and success page creation
        page_creators = [create_timeout_page, create_success_page] * 10
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = page_creators
        browser._browser = mock_browser
        browser._is_started = True
        
        results = []
        
        # Execute scripts alternating timeout and success
        for i in range(20):
            try:
                if i % 2 == 0:  # Even indices - expect timeout
                    await browser.execute_script(
                        f"https://example.com/timeout_{i}",
                        "await new Promise(r => setTimeout(r, 10000))",
                        timeout=100
                    )
                    results.append("unexpected_success")
                else:  # Odd indices - expect success
                    result = await browser.execute_script(
                        f"https://example.com/success_{i}",
                        "return 'success'"
                    )
                    results.append(result)
            except asyncio.TimeoutError:
                results.append("timeout")
        
        # Verify pattern: timeout, success, timeout, success, ...
        expected_pattern = ["timeout", "success"] * 10
        assert results == expected_pattern
        
        # All pages should be properly closed
        for page in timeout_pages + success_pages:
            page.close.assert_called_once()


class TestResourceLeakDetection:
    """Test for resource leaks and proper cleanup."""
    
    @pytest.mark.asyncio
    async def test_page_cleanup_after_errors(self):
        """Test that pages are cleaned up even when errors occur."""
        browser = Browser(BrowserConfig())
        
        created_pages = []
        
        def create_failing_page():
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.side_effect = Exception("Random script error")
            created_pages.append(mock_page)
            return mock_page
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = create_failing_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Execute scripts that will all fail
        failed_count = 0
        for i in range(20):
            try:
                await browser.execute_script(
                    f"https://example.com/fail_{i}",
                    "return 'should_fail'"
                )
            except Exception:
                failed_count += 1
        
        # All should have failed
        assert failed_count == 20
        
        # All pages should have been created and closed
        assert len(created_pages) == 20
        for page in created_pages:
            page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "x" * 1000  # 1KB result
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Measure memory before operations
        gc.collect()  # Force garbage collection
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        for batch in range(20):  # 20 batches of 10 operations
            batch_tasks = []
            for i in range(10):
                task = browser.execute_script(
                    f"https://example.com/batch_{batch}_item_{i}",
                    "return 'x'.repeat(1000)"
                )
                batch_tasks.append(task)
            
            await asyncio.gather(*batch_tasks)
            
            # Periodic cleanup
            if batch % 5 == 0:
                gc.collect()
        
        # Final memory measurement
        gc.collect()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be minimal for 200 operations
        assert memory_growth < 100, f"Potential memory leak: {memory_growth:.1f}MB growth"
    
    @pytest.mark.asyncio
    async def test_file_descriptor_leaks(self):
        """Test for file descriptor leaks."""
        import resource
        
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "fd_test"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Measure file descriptors before
        try:
            initial_fds = resource.getrlimit(resource.RLIMIT_NOFILE)[0]  # Current limit
            # Count actual open file descriptors
            import os
            initial_open_fds = len(os.listdir('/proc/self/fd')) if os.path.exists('/proc/self/fd') else 0
        except (OSError, AttributeError):
            # Skip test if we can't measure file descriptors
            pytest.skip("Cannot measure file descriptors on this system")
        
        # Perform operations
        for i in range(50):
            await browser.execute_script(
                f"https://example.com/fd_test_{i}",
                "return 'fd_test'"
            )
        
        # Measure file descriptors after
        try:
            final_open_fds = len(os.listdir('/proc/self/fd')) if os.path.exists('/proc/self/fd') else 0
            fd_growth = final_open_fds - initial_open_fds
            
            # File descriptor growth should be minimal
            assert fd_growth < 20, f"Potential FD leak: {fd_growth} FDs opened"
        except OSError:
            # Can't measure on this system, skip assertion
            pass


class TestPerformanceRegression:
    """Test performance regression and benchmarking."""
    
    @pytest.mark.asyncio
    async def test_baseline_performance_metrics(self):
        """Establish baseline performance metrics for regression testing."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "performance_test"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test basic performance characteristics
        performance_tests = [
            ("simple_script", "return 'test'", 10),
            ("dom_query", "return document.querySelectorAll('*').length", 10),
            ("data_processing", "return Array.from({length: 1000}, (_, i) => i).reduce((a, b) => a + b)", 5),
            ("async_operation", "await new Promise(r => setTimeout(r, 10)); return 'done'", 5),
        ]
        
        baseline_metrics = {}
        
        for test_name, script, iterations in performance_tests:
            durations = []
            
            for i in range(iterations):
                start_time = time.time()
                
                result = await browser.execute_script(
                    f"https://example.com/{test_name}_{i}",
                    script
                )
                
                duration = time.time() - start_time
                durations.append(duration)
                
                assert result == "performance_test"  # Mock always returns this
            
            # Calculate statistics
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            baseline_metrics[test_name] = {
                "avg": avg_duration,
                "max": max_duration,
                "min": min_duration,
                "iterations": iterations
            }
            
            # Performance assertions (baseline expectations)
            assert avg_duration < 1.0, f"{test_name} avg duration {avg_duration:.3f}s too slow"
            assert max_duration < 2.0, f"{test_name} max duration {max_duration:.3f}s too slow"
        
        # Store baseline metrics for future comparison
        # In a real test suite, you'd save these to a file for comparison
        print(f"Baseline metrics: {baseline_metrics}")
    
    @pytest.mark.asyncio
    async def test_throughput_measurement(self):
        """Measure throughput (operations per second)."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "throughput_test"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Measure serial throughput
        operations = 50
        start_time = time.time()
        
        for i in range(operations):
            await browser.execute_script(
                f"https://example.com/throughput_{i}",
                "return 'throughput_test'"
            )
        
        serial_duration = time.time() - start_time
        serial_ops_per_sec = operations / serial_duration
        
        # Measure concurrent throughput
        start_time = time.time()
        
        concurrent_tasks = [
            browser.execute_script(
                f"https://example.com/concurrent_{i}",
                "return 'throughput_test'"
            )
            for i in range(operations)
        ]
        
        await asyncio.gather(*concurrent_tasks)
        
        concurrent_duration = time.time() - start_time
        concurrent_ops_per_sec = operations / concurrent_duration
        
        # Concurrent should be faster than serial
        speedup_ratio = serial_duration / concurrent_duration
        
        print(f"Serial: {serial_ops_per_sec:.1f} ops/sec")
        print(f"Concurrent: {concurrent_ops_per_sec:.1f} ops/sec") 
        print(f"Speedup: {speedup_ratio:.1f}x")
        
        # Performance expectations
        assert serial_ops_per_sec > 10, f"Serial throughput {serial_ops_per_sec:.1f} ops/sec too low"
        assert concurrent_ops_per_sec > 20, f"Concurrent throughput {concurrent_ops_per_sec:.1f} ops/sec too low"
        assert speedup_ratio > 1.5, f"Concurrency speedup {speedup_ratio:.1f}x insufficient"


if __name__ == "__main__":
    # Run performance tests with detailed output
    pytest.main([__file__, "-v", "--tb=short", "-s"])