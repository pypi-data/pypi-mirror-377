"""
Comprehensive edge case and error scenario testing for Crawailer JavaScript API.

This test suite focuses on boundary conditions, malformed inputs, error handling,
and unusual scenarios that could break the JavaScript execution functionality.
"""

import asyncio
import json
import pytest
import time
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

from crawailer import Browser, BrowserConfig
from crawailer.content import WebContent, ContentExtractor
from crawailer.api import get, get_many, discover
from crawailer.utils import clean_text


class TestMalformedJavaScriptCodes:
    """Test handling of malformed, invalid, or dangerous JavaScript code."""
    
    @pytest.mark.asyncio
    async def test_syntax_error_javascript(self):
        """Test handling of JavaScript with syntax errors."""
        browser = Browser(BrowserConfig())
        
        # Mock browser setup
        mock_page = AsyncMock()
        mock_page.evaluate.side_effect = Exception("SyntaxError: Unexpected token '{'")
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test various syntax errors
        invalid_scripts = [
            "function() { return 'missing name'; }",  # Missing function name in declaration
            "if (true { console.log('missing paren'); }",  # Missing closing parenthesis
            "var x = 'unclosed string;",  # Unclosed string
            "function test() { return; extra_token }",  # Extra token after return
            "{ invalid: json, syntax }",  # Invalid object syntax
            "for (let i = 0; i < 10 i++) { }",  # Missing semicolon
            "document.querySelector('div').map(x => x.text)",  # Calling array method on NodeList
        ]
        
        for script in invalid_scripts:
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            # Should contain some form of syntax error information
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["syntax", "unexpected", "error"])
    
    @pytest.mark.asyncio
    async def test_infinite_loop_javascript(self):
        """Test handling of JavaScript with infinite loops."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        # Simulate timeout due to infinite loop
        mock_page.evaluate.side_effect = asyncio.TimeoutError("Script execution timeout")
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Scripts that could cause infinite loops
        infinite_scripts = [
            "while(true) { console.log('infinite'); }",
            "for(;;) { var x = 1; }",
            "function recurse() { recurse(); } recurse();",
            "let x = 0; while(x >= 0) { x++; }",
        ]
        
        for script in infinite_scripts:
            with pytest.raises(asyncio.TimeoutError):
                await browser.execute_script("https://example.com", script, timeout=1000)
    
    @pytest.mark.asyncio
    async def test_memory_exhaustion_javascript(self):
        """Test handling of JavaScript that attempts to exhaust memory."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        # Simulate out of memory error
        mock_page.evaluate.side_effect = Exception("RangeError: Maximum call stack size exceeded")
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Scripts that could exhaust memory
        memory_exhausting_scripts = [
            "var arr = []; while(true) { arr.push(new Array(1000000)); }",
            "var str = 'x'; while(true) { str += str; }",
            "var obj = {}; for(let i = 0; i < 1000000; i++) { obj[i] = new Array(1000); }",
        ]
        
        for script in memory_exhausting_scripts:
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["memory", "stack", "range", "error"])
    
    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self):
        """Test JavaScript execution with Unicode and special characters."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test various Unicode and special character scenarios
        unicode_scripts = [
            "return '测试中文字符'",  # Chinese characters
            "return 'emoji test 🚀🔥⭐'",  # Emoji
            "return 'áéíóú ñ ü'",  # Accented characters
            "return 'null\\x00char'",  # Null character
            "return 'quote\\\"escape\\\"test'",  # Escaped quotes
            "return `template\\nliteral\\twith\\ttabs`",  # Template literal with escapes
            "return JSON.stringify({key: '测试', emoji: '🔥'})",  # Unicode in JSON
        ]
        
        for i, script in enumerate(unicode_scripts):
            # Mock different return values for each test
            expected_results = [
                "测试中文字符", "emoji test 🚀🔥⭐", "áéíóú ñ ü", 
                "null\x00char", 'quote"escape"test', "template\nliteral\twith\ttabs",
                '{"key":"测试","emoji":"🔥"}'
            ]
            mock_page.evaluate.return_value = expected_results[i]
            
            result = await browser.execute_script("https://example.com", script)
            assert result == expected_results[i]
    
    @pytest.mark.asyncio 
    async def test_extremely_large_javascript_results(self):
        """Test handling of JavaScript that returns extremely large data."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Simulate large result (1MB string)
        large_result = "x" * (1024 * 1024)
        mock_page.evaluate.return_value = large_result
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        result = await browser.execute_script(
            "https://example.com", 
            "return 'x'.repeat(1024 * 1024)"
        )
        
        assert len(result) == 1024 * 1024
        assert result == large_result
    
    @pytest.mark.asyncio
    async def test_circular_reference_javascript(self):
        """Test JavaScript that returns circular references."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock error for circular reference
        mock_page.evaluate.side_effect = Exception("Converting circular structure to JSON")
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        circular_script = """
        var obj = {};
        obj.self = obj;
        return obj;
        """
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script("https://example.com", circular_script)
        
        assert "circular" in str(exc_info.value).lower()


class TestNetworkFailureScenarios:
    """Test JavaScript execution during various network failure conditions."""
    
    @pytest.mark.asyncio
    async def test_network_timeout_during_page_load(self):
        """Test script execution when page load times out."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto.side_effect = asyncio.TimeoutError("Navigation timeout")
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        with pytest.raises(asyncio.TimeoutError):
            await browser.execute_script(
                "https://very-slow-site.com", 
                "return document.title",
                timeout=1000
            )
    
    @pytest.mark.asyncio
    async def test_dns_resolution_failure(self):
        """Test handling of DNS resolution failures."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto.side_effect = Exception("net::ERR_NAME_NOT_RESOLVED")
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script(
                "https://nonexistent-domain-12345.invalid",
                "return true"
            )
        
        assert "name_not_resolved" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_connection_refused(self):
        """Test handling of connection refused errors."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto.side_effect = Exception("net::ERR_CONNECTION_REFUSED")
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script(
                "http://localhost:99999",  # Unlikely to be open
                "return document.body.innerHTML"
            )
        
        assert "connection" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_ssl_certificate_error(self):
        """Test handling of SSL certificate errors."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto.side_effect = Exception("net::ERR_CERT_AUTHORITY_INVALID")
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script(
                "https://self-signed.badssl.com/",
                "return location.hostname"
            )
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in ["cert", "ssl", "authority"])
    
    @pytest.mark.asyncio
    async def test_network_interruption_during_script(self):
        """Test network interruption while script is executing."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Simulate network interruption during script execution
        mock_page.evaluate.side_effect = Exception("net::ERR_NETWORK_CHANGED")
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script(
                "https://example.com",
                "await fetch('/api/data'); return 'success'"
            )
        
        assert "network" in str(exc_info.value).lower()


class TestConcurrencyAndResourceLimits:
    """Test concurrent execution and resource management."""
    
    @pytest.mark.asyncio
    async def test_concurrent_script_execution_limits(self):
        """Test behavior at concurrency limits."""
        browser = Browser(BrowserConfig())
        
        # Mock setup for multiple concurrent requests
        mock_pages = []
        for i in range(20):  # Create 20 mock pages
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.evaluate.return_value = f"result_{i}"
            mock_page.close = AsyncMock()
            mock_pages.append(mock_page)
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = mock_pages
        browser._browser = mock_browser
        browser._is_started = True
        
        # Launch many concurrent script executions
        tasks = []
        for i in range(20):
            task = browser.execute_script(
                f"https://example.com/page{i}",
                f"return 'result_{i}'"
            )
            tasks.append(task)
        
        # Should handle all concurrent requests
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful results vs exceptions
        successful = [r for r in results if not isinstance(r, Exception)]
        errors = [r for r in results if isinstance(r, Exception)]
        
        # Most should succeed, but some might fail due to resource limits
        assert len(successful) >= 10  # At least half should succeed
        assert len(errors) <= 10    # Not all should fail
    
    @pytest.mark.asyncio
    async def test_browser_crash_recovery(self):
        """Test recovery when browser process crashes."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # First call succeeds
        mock_page.evaluate.return_value = "success"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # First execution succeeds
        result1 = await browser.execute_script("https://example.com", "return 'success'")
        assert result1 == "success"
        
        # Simulate browser crash on second call
        mock_page.evaluate.side_effect = Exception("Browser process crashed")
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script("https://example.com", "return 'test'")
        
        assert "crashed" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self):
        """Test that pages are properly cleaned up to prevent memory leaks."""
        browser = Browser(BrowserConfig())
        
        created_pages = []
        
        def create_mock_page():
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.evaluate.return_value = "success"
            mock_page.close = AsyncMock()
            created_pages.append(mock_page)
            return mock_page
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = create_mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Execute multiple scripts
        for i in range(10):
            await browser.execute_script(f"https://example.com/page{i}", "return 'test'")
        
        # Verify all pages were closed
        assert len(created_pages) == 10
        for page in created_pages:
            page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_page_resource_exhaustion(self):
        """Test handling when page resources are exhausted."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Simulate resource exhaustion
        mock_page.evaluate.side_effect = Exception("Target closed")
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script("https://example.com", "return 'test'")
        
        assert "closed" in str(exc_info.value).lower()


class TestInvalidParameterCombinations:
    """Test various invalid parameter combinations and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_urls(self):
        """Test handling of various invalid URL formats."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        invalid_urls = [
            "",  # Empty string
            "not-a-url",  # Not a URL
            "ftp://example.com",  # Unsupported protocol
            "javascript:alert('test')",  # JavaScript URL
            "data:text/html,<h1>Test</h1>",  # Data URL
            "file:///etc/passwd",  # File URL
            "http://",  # Incomplete URL
            "https://",  # Incomplete URL
            "http://user:pass@example.com",  # URL with credentials
            "http://192.168.1.1:99999",  # Invalid port
        ]
        
        for url in invalid_urls:
            mock_page.goto.side_effect = Exception(f"Invalid URL: {url}")
            
            with pytest.raises(Exception):
                await browser.execute_script(url, "return true")
    
    @pytest.mark.asyncio
    async def test_empty_and_none_scripts(self):
        """Test handling of empty, None, and whitespace-only scripts."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test various empty script scenarios
        empty_scripts = [
            None,
            "",
            "   ",  # Whitespace only
            "\n\t  \n",  # Mixed whitespace
            "//comment only",
            "/* block comment */",
            "// comment\n  // another comment",
        ]
        
        for script in empty_scripts:
            if script is None:
                # None script should be handled gracefully
                mock_page.evaluate.return_value = None
                result = await browser.execute_script("https://example.com", script)
                assert result is None
            else:
                # Empty scripts might cause syntax errors
                mock_page.evaluate.side_effect = Exception("SyntaxError: Unexpected end of input")
                with pytest.raises(Exception):
                    await browser.execute_script("https://example.com", script)
    
    @pytest.mark.asyncio
    async def test_invalid_timeout_values(self):
        """Test handling of invalid timeout values."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.evaluate.return_value = "success"
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test various invalid timeout values
        invalid_timeouts = [
            -1,        # Negative
            0,         # Zero
            float('inf'),  # Infinity
            float('nan'),  # NaN
            "5000",    # String instead of number
            [],        # Wrong type
            {},        # Wrong type
        ]
        
        for timeout in invalid_timeouts:
            # Some may raise ValueError, others might be handled gracefully
            try:
                result = await browser.execute_script(
                    "https://example.com", 
                    "return 'test'",
                    timeout=timeout
                )
                # If no exception, verify the result
                assert result == "success"
            except (ValueError, TypeError) as e:
                # Expected for invalid types/values
                assert str(e)  # Just verify we get an error message
    
    def test_browser_config_edge_cases(self):
        """Test browser configuration with edge case values."""
        # Test with extreme values
        configs = [
            BrowserConfig(timeout=-1),  # Negative timeout
            BrowserConfig(timeout=0),   # Zero timeout
            BrowserConfig(timeout=999999999),  # Very large timeout
            BrowserConfig(viewport={"width": -100, "height": -100}),  # Negative dimensions
            BrowserConfig(viewport={"width": 99999, "height": 99999}),  # Huge dimensions
            BrowserConfig(extra_args=["--invalid-flag", "--another-invalid-flag"]),  # Invalid flags
            BrowserConfig(user_agent=""),  # Empty user agent
            BrowserConfig(user_agent="x" * 10000),  # Very long user agent
        ]
        
        for config in configs:
            # Should create without throwing exception
            browser = Browser(config)
            assert browser.config == config


class TestEncodingAndSpecialCharacterHandling:
    """Test handling of various text encodings and special characters."""
    
    @pytest.mark.asyncio
    async def test_different_text_encodings(self):
        """Test JavaScript execution with different text encodings."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test various encoding scenarios
        encoding_tests = [
            ("UTF-8", "return 'Hello 世界 🌍'"),
            ("UTF-16", "return 'Testing UTF-16 ñáéíóú'"),
            ("Latin-1", "return 'Café résumé naïve'"),
            ("ASCII", "return 'Simple ASCII text'"),
        ]
        
        for encoding, script in encoding_tests:
            # Mock the expected result
            if "世界" in script:
                mock_page.evaluate.return_value = "Hello 世界 🌍"
            elif "UTF-16" in script:
                mock_page.evaluate.return_value = "Testing UTF-16 ñáéíóú"
            elif "Café" in script:
                mock_page.evaluate.return_value = "Café résumé naïve"
            else:
                mock_page.evaluate.return_value = "Simple ASCII text"
            
            result = await browser.execute_script("https://example.com", script)
            assert result is not None
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_binary_data_handling(self):
        """Test handling of binary data in JavaScript results."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock binary data as base64
        binary_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        mock_page.evaluate.return_value = binary_data
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        script = """
        // Simulate extracting image data
        return document.querySelector('img')?.src || 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
        """
        
        result = await browser.execute_script("https://example.com", script)
        assert result == binary_data
        assert result.startswith("data:image/")
    
    @pytest.mark.asyncio
    async def test_control_characters_and_escapes(self):
        """Test handling of control characters and escape sequences."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test various control characters and escapes
        control_tests = [
            ("return 'line1\\nline2\\nline3'", "line1\nline2\nline3"),
            ("return 'tab\\tseparated\\tvalues'", "tab\tseparated\tvalues"),
            ("return 'quote\"within\"string'", 'quote"within"string'),
            ("return 'backslash\\\\test'", "backslash\\test"),
            ("return 'null\\x00character'", "null\x00character"),
            ("return 'carriage\\rreturn'", "carriage\rreturn"),
            ("return 'form\\ffeed'", "form\ffeed"),
            ("return 'vertical\\vtab'", "vertical\vtab"),
        ]
        
        for script, expected in control_tests:
            mock_page.evaluate.return_value = expected
            result = await browser.execute_script("https://example.com", script)
            assert result == expected


class TestComplexDOMManipulationEdgeCases:
    """Test edge cases in DOM manipulation and querying."""
    
    @pytest.mark.asyncio
    async def test_missing_dom_elements(self):
        """Test scripts that try to access non-existent DOM elements."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Scripts that access non-existent elements
        missing_element_scripts = [
            "return document.querySelector('.nonexistent').innerText",  # Should cause error
            "return document.getElementById('missing')?.value || 'default'",  # Safe access
            "return document.querySelectorAll('.missing').length",  # Should return 0
            "return Array.from(document.querySelectorAll('nonexistent')).map(e => e.text)",  # Empty array
        ]
        
        for i, script in enumerate(missing_element_scripts):
            if "?" in script or "length" in script or "Array.from" in script:
                # Safe access patterns should work
                mock_page.evaluate.return_value = "default" if "default" in script else 0 if "length" in script else []
                result = await browser.execute_script("https://example.com", script)
                assert result is not None
            else:
                # Unsafe access should cause error
                mock_page.evaluate.side_effect = Exception("Cannot read property 'innerText' of null")
                with pytest.raises(Exception) as exc_info:
                    await browser.execute_script("https://example.com", script)
                assert "null" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_iframe_and_cross_frame_access(self):
        """Test scripts that try to access iframe content or cross-frame elements."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Scripts that access iframe content
        iframe_scripts = [
            "return document.querySelector('iframe').contentDocument.body.innerHTML",  # Cross-frame access
            "return window.frames[0].document.title",  # Frame access
            "return parent.document.title",  # Parent frame access
            "return top.document.location.href",  # Top frame access
        ]
        
        for script in iframe_scripts:
            # These typically cause security errors
            mock_page.evaluate.side_effect = Exception("Blocked a frame with origin")
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["blocked", "frame", "origin", "security"])
    
    @pytest.mark.asyncio
    async def test_shadow_dom_access(self):
        """Test scripts that interact with Shadow DOM."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Scripts that work with Shadow DOM
        shadow_dom_scripts = [
            "return document.querySelector('custom-element').shadowRoot.innerHTML",
            "return document.querySelector('web-component').shadowRoot.querySelector('.internal').text",
            "return Array.from(document.querySelectorAll('*')).find(e => e.shadowRoot)?.tagName",
        ]
        
        for i, script in enumerate(shadow_dom_scripts):
            if "?" in script:
                # Safe access with optional chaining
                mock_page.evaluate.return_value = None
                result = await browser.execute_script("https://example.com", script)
                assert result is None
            else:
                # Unsafe access might fail
                mock_page.evaluate.side_effect = Exception("Cannot read property 'innerHTML' of null")
                with pytest.raises(Exception):
                    await browser.execute_script("https://example.com", script)


if __name__ == "__main__":
    # Run tests with verbose output and detailed error reporting
    pytest.main([__file__, "-v", "--tb=long", "--capture=no"])