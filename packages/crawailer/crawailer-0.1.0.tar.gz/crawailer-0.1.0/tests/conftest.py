"""
Pytest configuration and shared fixtures for the comprehensive Crawailer test suite.

This file provides shared fixtures, configuration, and utilities used across
all test modules in the production-grade test suite.
"""

import asyncio
import pytest
import tempfile
import sqlite3
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock
import psutil
import time
import threading

from crawailer import Browser, BrowserConfig
from crawailer.content import WebContent


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: marks tests as edge case tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and configure execution."""
    # Add markers based on test file names and test names
    for item in items:
        # Mark tests based on file names
        if "performance" in item.fspath.basename:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "security" in item.fspath.basename:
            item.add_marker(pytest.mark.security)
        elif "edge_cases" in item.fspath.basename:
            item.add_marker(pytest.mark.edge_case)
        elif "production" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
        elif "regression" in item.fspath.basename:
            item.add_marker(pytest.mark.regression)
        
        # Mark tests based on test names
        if "stress" in item.name or "concurrent" in item.name:
            item.add_marker(pytest.mark.slow)
        if "timeout" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)


# Shared fixtures
@pytest.fixture
def browser_config():
    """Provide a standard browser configuration for tests."""
    return BrowserConfig(
        headless=True,
        timeout=30000,
        viewport={"width": 1920, "height": 1080},
        extra_args=["--no-sandbox", "--disable-dev-shm-usage"]
    )


@pytest.fixture
async def mock_browser():
    """Provide a fully configured mock browser instance."""
    browser = Browser(BrowserConfig())
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock(return_value=AsyncMock(status=200))
    mock_page.close = AsyncMock()
    mock_page.evaluate.return_value = "mock_result"
    mock_page.content.return_value = "<html><body>Mock content</body></html>"
    mock_page.title.return_value = "Mock Page"
    
    mock_browser_instance = AsyncMock()
    mock_browser_instance.new_page.return_value = mock_page
    
    browser._browser = mock_browser_instance
    browser._is_started = True
    
    yield browser


@pytest.fixture
async def mock_multiple_pages():
    """Provide multiple mock pages for concurrent testing."""
    pages = []
    for i in range(10):
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=AsyncMock(status=200))
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = f"page_{i}_result"
        mock_page.content.return_value = f"<html><body>Page {i} content</body></html>"
        mock_page.title.return_value = f"Page {i}"
        pages.append(mock_page)
    
    return pages


@pytest.fixture
def temp_database():
    """Provide a temporary SQLite database for testing."""
    db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_file.close()
    
    # Initialize database
    conn = sqlite3.connect(db_file.name)
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute("""
        CREATE TABLE test_data (
            id INTEGER PRIMARY KEY,
            url TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE execution_logs (
            id INTEGER PRIMARY KEY,
            test_name TEXT,
            execution_time REAL,
            success BOOLEAN,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_file.name
    
    # Cleanup
    if os.path.exists(db_file.name):
        os.unlink(db_file.name)


@pytest.fixture
def temp_directory():
    """Provide a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def performance_monitor():
    """Provide performance monitoring utilities."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None
            self.start_threads = None
            self.end_threads = None
        
        def start_monitoring(self):
            self.start_time = time.time()
            self.start_memory = psutil.virtual_memory().percent
            self.start_threads = threading.active_count()
        
        def stop_monitoring(self):
            self.end_time = time.time()
            self.end_memory = psutil.virtual_memory().percent
            self.end_threads = threading.active_count()
        
        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0
        
        @property
        def memory_delta(self):
            if self.start_memory is not None and self.end_memory is not None:
                return self.end_memory - self.start_memory
            return 0
        
        @property
        def thread_delta(self):
            if self.start_threads is not None and self.end_threads is not None:
                return self.end_threads - self.start_threads
            return 0
    
    return PerformanceMonitor()


@pytest.fixture
def mock_html_pages():
    """Provide mock HTML pages for testing various scenarios."""
    return {
        "simple": """
            <!DOCTYPE html>
            <html>
            <head><title>Simple Page</title></head>
            <body>
                <h1>Hello World</h1>
                <p>This is a simple test page.</p>
            </body>
            </html>
        """,
        
        "complex": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Complex Page</title>
                <meta charset="utf-8">
            </head>
            <body>
                <nav>
                    <a href="/home">Home</a>
                    <a href="/about">About</a>
                </nav>
                <main>
                    <article>
                        <h1>Article Title</h1>
                        <p>Article content with <strong>bold</strong> text.</p>
                        <ul>
                            <li>Item 1</li>
                            <li>Item 2</li>
                        </ul>
                    </article>
                </main>
                <footer>
                    <p>&copy; 2024 Test Site</p>
                </footer>
            </body>
            </html>
        """,
        
        "javascript_heavy": """
            <!DOCTYPE html>
            <html>
            <head><title>JS Heavy Page</title></head>
            <body>
                <div id="content">Loading...</div>
                <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.getElementById('content').innerHTML = 'Loaded by JavaScript';
                        window.testData = { loaded: true, timestamp: Date.now() };
                    });
                </script>
            </body>
            </html>
        """,
        
        "forms": """
            <!DOCTYPE html>
            <html>
            <head><title>Form Page</title></head>
            <body>
                <form id="testForm">
                    <input type="text" name="username" placeholder="Username">
                    <input type="password" name="password" placeholder="Password">
                    <select name="role">
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                    </select>
                    <button type="submit">Submit</button>
                </form>
            </body>
            </html>
        """
    }


@pytest.fixture
def mock_web_content():
    """Provide mock WebContent objects for testing."""
    def create_content(url="https://example.com", title="Test Page", content="Test content"):
        return WebContent(
            url=url,
            title=title,
            markdown=f"# {title}\n\n{content}",
            text=content,
            html=f"<html><head><title>{title}</title></head><body><p>{content}</p></body></html>",
            word_count=len(content.split()),
            reading_time="1 min read"
        )
    
    return create_content


@pytest.fixture
def error_injection():
    """Provide utilities for error injection testing."""
    class ErrorInjection:
        @staticmethod
        def network_error():
            return Exception("Network connection failed")
        
        @staticmethod
        def timeout_error():
            return asyncio.TimeoutError("Operation timed out")
        
        @staticmethod
        def javascript_error():
            return Exception("JavaScript execution failed: ReferenceError: undefined is not defined")
        
        @staticmethod
        def security_error():
            return Exception("Security policy violation: Cross-origin request blocked")
        
        @staticmethod
        def memory_error():
            return Exception("Out of memory: Cannot allocate buffer")
        
        @staticmethod
        def syntax_error():
            return Exception("SyntaxError: Unexpected token '{'")
    
    return ErrorInjection()


@pytest.fixture
def test_urls():
    """Provide a set of test URLs for various scenarios."""
    return {
        "valid": [
            "https://example.com",
            "https://www.google.com",
            "https://github.com",
            "http://httpbin.org/get"
        ],
        "invalid": [
            "not-a-url",
            "ftp://example.com",
            "javascript:alert('test')",
            "file:///etc/passwd"
        ],
        "problematic": [
            "https://very-slow-site.example.com",
            "https://nonexistent-domain-12345.invalid",
            "https://self-signed.badssl.com",
            "http://localhost:99999"
        ]
    }


@pytest.fixture(scope="session")
def test_session_info():
    """Provide session-wide test information."""
    return {
        "start_time": time.time(),
        "python_version": ".".join(map(str, __import__("sys").version_info[:3])),
        "platform": __import__("platform").platform(),
        "test_environment": "pytest"
    }


# Utility functions for tests
def assert_performance_within_bounds(duration: float, max_duration: float, test_name: str = ""):
    """Assert that performance is within acceptable bounds."""
    assert duration <= max_duration, f"{test_name} took {duration:.2f}s, expected <= {max_duration:.2f}s"


def assert_memory_usage_reasonable(memory_delta: float, max_delta: float = 100.0, test_name: str = ""):
    """Assert that memory usage is reasonable."""
    assert abs(memory_delta) <= max_delta, f"{test_name} memory delta {memory_delta:.1f}MB exceeds {max_delta}MB"


def assert_no_resource_leaks(thread_delta: int, max_delta: int = 5, test_name: str = ""):
    """Assert that there are no significant resource leaks."""
    assert abs(thread_delta) <= max_delta, f"{test_name} thread delta {thread_delta} exceeds {max_delta}"


# Async test utilities
async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
    """Wait for a condition to become true within a timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
            return True
        await asyncio.sleep(interval)
    return False


async def execute_with_timeout(coro, timeout: float):
    """Execute a coroutine with a timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(f"Operation timed out after {timeout} seconds")


# Test data generators
def generate_test_scripts(count: int = 10):
    """Generate test JavaScript scripts."""
    scripts = []
    for i in range(count):
        scripts.append(f"return 'test_script_{i}_result'")
    return scripts


def generate_large_data(size_mb: int = 1):
    """Generate large test data."""
    return "x" * (size_mb * 1024 * 1024)


def generate_unicode_test_strings():
    """Generate Unicode test strings."""
    return [
        "Hello, 世界! 🌍",
        "Café résumé naïve",
        "Тест на русском языке",
        "اختبار باللغة العربية",
        "עברית בדיקה",
        "ひらがな カタカナ 漢字"
    ]


# Custom assertions
def assert_valid_web_content(content):
    """Assert that a WebContent object is valid."""
    assert isinstance(content, WebContent)
    assert content.url
    assert content.title
    assert content.text
    assert content.html
    assert content.word_count >= 0
    assert content.reading_time


def assert_script_result_valid(result, expected_type=None):
    """Assert that a script execution result is valid."""
    if expected_type:
        assert isinstance(result, expected_type)
    # Result should be JSON serializable
    import json
    try:
        json.dumps(result)
    except (TypeError, ValueError):
        pytest.fail(f"Script result {result} is not JSON serializable")