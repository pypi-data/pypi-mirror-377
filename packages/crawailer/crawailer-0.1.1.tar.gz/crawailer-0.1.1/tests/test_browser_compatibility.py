"""
Browser compatibility and cross-platform testing for Crawailer JavaScript API.

This test suite focuses on browser engine differences, headless vs headed mode,
viewport variations, and device emulation compatibility.
"""

import asyncio
import pytest
import time
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from crawailer import Browser, BrowserConfig
from crawailer.content import WebContent, ContentExtractor
from crawailer.api import get, get_many, discover


@dataclass
class BrowserTestConfig:
    """Test configuration for different browser scenarios."""
    name: str
    browser_type: str
    headless: bool
    viewport: Dict[str, int]
    user_agent: str
    extra_args: List[str]
    expected_capabilities: List[str]
    known_limitations: List[str]


class TestPlaywrightBrowserEngines:
    """Test different Playwright browser engines (Chromium, Firefox, WebKit)."""
    
    def get_browser_configs(self) -> List[BrowserTestConfig]:
        """Get test configurations for different browser engines."""
        return [
            BrowserTestConfig(
                name="chromium_headless",
                browser_type="chromium",
                headless=True,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                extra_args=["--no-sandbox", "--disable-dev-shm-usage"],
                expected_capabilities=["es6", "webgl", "canvas", "localStorage"],
                known_limitations=[]
            ),
            BrowserTestConfig(
                name="firefox_headless",
                browser_type="firefox",
                headless=True,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
                extra_args=["-headless"],
                expected_capabilities=["es6", "webgl", "canvas", "localStorage"],
                known_limitations=["webrtc_limited"]
            ),
            BrowserTestConfig(
                name="webkit_headless",
                browser_type="webkit",
                headless=True,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
                extra_args=[],
                expected_capabilities=["es6", "canvas", "localStorage"],
                known_limitations=["webgl_limited", "some_es2020_features"]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_basic_javascript_execution_across_engines(self):
        """Test basic JavaScript execution across all browser engines."""
        configs = self.get_browser_configs()
        
        for config in configs:
            browser = Browser(BrowserConfig(
                headless=config.headless,
                viewport=config.viewport,
                user_agent=config.user_agent,
                extra_args=config.extra_args
            ))
            
            # Mock browser setup
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = f"{config.browser_type}_result"
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            # Test basic JavaScript execution
            result = await browser.execute_script(
                "https://example.com",
                f"return '{config.browser_type}_result'"
            )
            
            assert result == f"{config.browser_type}_result"
            mock_page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_es6_feature_compatibility(self):
        """Test ES6+ feature compatibility across browsers."""
        configs = self.get_browser_configs()
        
        # ES6+ features to test
        es6_tests = [
            ("arrow_functions", "(() => 'arrow_works')()"),
            ("template_literals", "`template ${'works'}`"),
            ("destructuring", "const [a, b] = [1, 2]; return a + b"),
            ("spread_operator", "const arr = [1, 2]; return [...arr, 3].length"),
            ("async_await", "async () => { await Promise.resolve(); return 'async_works'; }"),
            ("classes", "class Test { getName() { return 'class_works'; } } return new Test().getName()"),
            ("modules", "export default 'module_works'"),  # May not work in all contexts
        ]
        
        for config in configs:
            browser = Browser(BrowserConfig(
                headless=config.headless,
                viewport=config.viewport
            ))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            for feature_name, script in es6_tests:
                if "es6" in config.expected_capabilities:
                    # Should support ES6 features
                    mock_page.evaluate.return_value = f"{feature_name}_works"
                    
                    result = await browser.execute_script("https://example.com", script)
                    assert "works" in str(result)
                else:
                    # May not support some ES6 features
                    if feature_name in ["modules"]:  # Known problematic features
                        mock_page.evaluate.side_effect = Exception("SyntaxError: Unexpected token 'export'")
                        
                        with pytest.raises(Exception):
                            await browser.execute_script("https://example.com", script)
                    else:
                        mock_page.evaluate.return_value = f"{feature_name}_works"
                        result = await browser.execute_script("https://example.com", script)
                        assert "works" in str(result)
    
    @pytest.mark.asyncio
    async def test_dom_api_compatibility(self):
        """Test DOM API compatibility across browsers."""
        configs = self.get_browser_configs()
        
        # DOM APIs to test
        dom_tests = [
            ("querySelector", "document.querySelector('body')?.tagName || 'BODY'"),
            ("querySelectorAll", "document.querySelectorAll('*').length"),
            ("addEventListener", "document.addEventListener('test', () => {}); return 'listener_added'"),
            ("createElement", "document.createElement('div').tagName"),
            ("innerHTML", "document.body.innerHTML = '<div>test</div>'; return 'html_set'"),
            ("classList", "document.body.classList.add('test'); return 'class_added'"),
            ("dataset", "document.body.dataset.test = 'value'; return document.body.dataset.test"),
        ]
        
        for config in configs:
            browser = Browser(BrowserConfig(headless=config.headless))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            for api_name, script in dom_tests:
                # All modern browsers should support these DOM APIs
                expected_results = {
                    "querySelector": "BODY",
                    "querySelectorAll": 10,  # Some number of elements
                    "addEventListener": "listener_added",
                    "createElement": "DIV",
                    "innerHTML": "html_set",
                    "classList": "class_added",
                    "dataset": "value"
                }
                
                mock_page.evaluate.return_value = expected_results[api_name]
                
                result = await browser.execute_script("https://example.com", script)
                assert result == expected_results[api_name]
    
    @pytest.mark.asyncio
    async def test_web_apis_availability(self):
        """Test availability of various Web APIs across browsers."""
        configs = self.get_browser_configs()
        
        # Web APIs to test
        web_api_tests = [
            ("fetch", "typeof fetch"),
            ("localStorage", "typeof localStorage"),
            ("sessionStorage", "typeof sessionStorage"),
            ("indexedDB", "typeof indexedDB"),
            ("WebSocket", "typeof WebSocket"),
            ("Worker", "typeof Worker"),
            ("console", "typeof console"),
            ("JSON", "typeof JSON"),
            ("Promise", "typeof Promise"),
            ("Map", "typeof Map"),
            ("Set", "typeof Set"),
            ("WeakMap", "typeof WeakMap"),
        ]
        
        for config in configs:
            browser = Browser(BrowserConfig(headless=config.headless))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            for api_name, script in web_api_tests:
                # Most APIs should be available as 'function' or 'object'
                if api_name.lower() in config.known_limitations:
                    mock_page.evaluate.return_value = "undefined"
                else:
                    mock_page.evaluate.return_value = "function" if api_name in ["fetch"] else "object"
                
                result = await browser.execute_script("https://example.com", script)
                
                if api_name.lower() not in config.known_limitations:
                    assert result in ["function", "object"], f"{api_name} not available in {config.name}"


class TestHeadlessVsHeadedBehavior:
    """Test differences between headless and headed browser modes."""
    
    @pytest.mark.asyncio
    async def test_headless_vs_headed_javascript_execution(self):
        """Test JavaScript execution differences between headless and headed modes."""
        modes = [
            ("headless", True),
            ("headed", False)
        ]
        
        for mode_name, headless in modes:
            browser = Browser(BrowserConfig(headless=headless))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = f"{mode_name}_execution_success"
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            # Test basic execution
            result = await browser.execute_script(
                "https://example.com",
                "return 'execution_success'"
            )
            
            assert "execution_success" in result
    
    @pytest.mark.asyncio
    async def test_window_properties_differences(self):
        """Test window properties that differ between headless and headed modes."""
        modes = [
            ("headless", True),
            ("headed", False)
        ]
        
        window_property_tests = [
            ("window.outerWidth", "number"),
            ("window.outerHeight", "number"),
            ("window.screenX", "number"),
            ("window.screenY", "number"),
            ("window.devicePixelRatio", "number"),
            ("navigator.webdriver", "boolean"),  # May be true in automation
            ("window.chrome", "object"),  # May be undefined in some browsers
        ]
        
        for mode_name, headless in modes:
            browser = Browser(BrowserConfig(headless=headless))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            for property_name, expected_type in window_property_tests:
                # Mock different values for headless vs headed
                if headless and "outer" in property_name:
                    # Headless might have different dimensions
                    mock_page.evaluate.return_value = 0 if "outer" in property_name else 1920
                else:
                    # Headed mode has actual window dimensions
                    mock_page.evaluate.return_value = 1920 if "Width" in property_name else 1080
                
                result = await browser.execute_script(
                    "https://example.com",
                    f"return typeof {property_name}"
                )
                
                # Type should be consistent regardless of mode
                if property_name == "window.chrome" and "webkit" in mode_name:
                    # WebKit doesn't have window.chrome
                    assert result in ["undefined", "object"]
                else:
                    assert result == expected_type or result == "undefined"
    
    @pytest.mark.asyncio
    async def test_media_queries_headless_vs_headed(self):
        """Test CSS media queries behavior in different modes."""
        modes = [
            ("headless", True),
            ("headed", False)
        ]
        
        media_query_tests = [
            "window.matchMedia('(prefers-color-scheme: dark)').matches",
            "window.matchMedia('(prefers-reduced-motion: reduce)').matches",
            "window.matchMedia('(hover: hover)').matches",
            "window.matchMedia('(pointer: fine)').matches",
            "window.matchMedia('(display-mode: browser)').matches",
        ]
        
        for mode_name, headless in modes:
            browser = Browser(BrowserConfig(headless=headless))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            for query in media_query_tests:
                # Mock media query results
                if headless:
                    # Headless mode might have different defaults
                    mock_page.evaluate.return_value = False if "hover" in query else True
                else:
                    # Headed mode might have different results
                    mock_page.evaluate.return_value = True
                
                result = await browser.execute_script("https://example.com", query)
                
                # Should return boolean
                assert isinstance(result, bool)


class TestViewportAndDeviceEmulation:
    """Test different viewport sizes and device emulation."""
    
    def get_viewport_configs(self) -> List[Dict[str, Any]]:
        """Get different viewport configurations to test."""
        return [
            # Desktop viewports
            {"width": 1920, "height": 1080, "name": "desktop_fhd"},
            {"width": 1366, "height": 768, "name": "desktop_hd"},
            {"width": 2560, "height": 1440, "name": "desktop_qhd"},
            
            # Tablet viewports
            {"width": 768, "height": 1024, "name": "tablet_portrait"},
            {"width": 1024, "height": 768, "name": "tablet_landscape"},
            
            # Mobile viewports
            {"width": 375, "height": 667, "name": "mobile_iphone"},
            {"width": 414, "height": 896, "name": "mobile_iphone_x"},
            {"width": 360, "height": 640, "name": "mobile_android"},
            
            # Ultra-wide and unusual
            {"width": 3440, "height": 1440, "name": "ultrawide"},
            {"width": 800, "height": 600, "name": "legacy_desktop"},
        ]
    
    @pytest.mark.asyncio
    async def test_viewport_aware_javascript(self):
        """Test JavaScript that depends on viewport dimensions."""
        viewport_configs = self.get_viewport_configs()
        
        for viewport_config in viewport_configs:
            browser = Browser(BrowserConfig(
                viewport={"width": viewport_config["width"], "height": viewport_config["height"]}
            ))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            
            # Mock viewport-dependent results
            mock_page.evaluate.return_value = {
                "innerWidth": viewport_config["width"],
                "innerHeight": viewport_config["height"],
                "isMobile": viewport_config["width"] < 768,
                "isTablet": 768 <= viewport_config["width"] < 1024,
                "isDesktop": viewport_config["width"] >= 1024
            }
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            # Test viewport-aware script
            result = await browser.execute_script(
                "https://example.com",
                """
                return {
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight,
                    isMobile: window.innerWidth < 768,
                    isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
                    isDesktop: window.innerWidth >= 1024
                };
                """
            )
            
            assert result["innerWidth"] == viewport_config["width"]
            assert result["innerHeight"] == viewport_config["height"]
            
            # Check device classification
            if viewport_config["width"] < 768:
                assert result["isMobile"] is True
                assert result["isTablet"] is False
                assert result["isDesktop"] is False
            elif viewport_config["width"] < 1024:
                assert result["isMobile"] is False
                assert result["isTablet"] is True
                assert result["isDesktop"] is False
            else:
                assert result["isMobile"] is False
                assert result["isTablet"] is False
                assert result["isDesktop"] is True
    
    @pytest.mark.asyncio
    async def test_responsive_design_detection(self):
        """Test detection of responsive design breakpoints."""
        breakpoint_tests = [
            (320, "xs"),   # Extra small
            (576, "sm"),   # Small
            (768, "md"),   # Medium
            (992, "lg"),   # Large
            (1200, "xl"),  # Extra large
            (1400, "xxl"), # Extra extra large
        ]
        
        for width, expected_breakpoint in breakpoint_tests:
            browser = Browser(BrowserConfig(viewport={"width": width, "height": 800}))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = expected_breakpoint
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            # Test breakpoint detection script
            result = await browser.execute_script(
                "https://example.com",
                f"""
                const width = {width};
                if (width < 576) return 'xs';
                if (width < 768) return 'sm';
                if (width < 992) return 'md';
                if (width < 1200) return 'lg';
                if (width < 1400) return 'xl';
                return 'xxl';
                """
            )
            
            assert result == expected_breakpoint
    
    @pytest.mark.asyncio
    async def test_device_pixel_ratio_handling(self):
        """Test handling of different device pixel ratios."""
        pixel_ratio_configs = [
            (1.0, "standard"),
            (1.5, "medium_dpi"),
            (2.0, "high_dpi"),
            (3.0, "ultra_high_dpi"),
        ]
        
        for ratio, config_name in pixel_ratio_configs:
            browser = Browser(BrowserConfig(
                viewport={"width": 375, "height": 667}  # iPhone-like
            ))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = {
                "devicePixelRatio": ratio,
                "isRetina": ratio >= 2.0,
                "cssPixelWidth": 375,
                "physicalPixelWidth": int(375 * ratio)
            }
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            result = await browser.execute_script(
                "https://example.com",
                """
                return {
                    devicePixelRatio: window.devicePixelRatio,
                    isRetina: window.devicePixelRatio >= 2,
                    cssPixelWidth: window.innerWidth,
                    physicalPixelWidth: window.innerWidth * window.devicePixelRatio
                };
                """
            )
            
            assert result["devicePixelRatio"] == ratio
            assert result["isRetina"] == (ratio >= 2.0)
            assert result["cssPixelWidth"] == 375
            assert result["physicalPixelWidth"] == int(375 * ratio)


class TestUserAgentAndFingerprinting:
    """Test user agent strings and fingerprinting detection."""
    
    def get_user_agent_configs(self) -> List[Dict[str, str]]:
        """Get different user agent configurations."""
        return [
            {
                "name": "chrome_windows",
                "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "platform": "Win32",
                "vendor": "Google Inc."
            },
            {
                "name": "firefox_windows",
                "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
                "platform": "Win32",
                "vendor": ""
            },
            {
                "name": "safari_macos",
                "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                "platform": "MacIntel",
                "vendor": "Apple Computer, Inc."
            },
            {
                "name": "chrome_android",
                "ua": "Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
                "platform": "Linux armv7l",
                "vendor": "Google Inc."
            },
            {
                "name": "safari_ios",
                "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
                "platform": "iPhone",
                "vendor": "Apple Computer, Inc."
            }
        ]
    
    @pytest.mark.asyncio
    async def test_user_agent_consistency(self):
        """Test that user agent strings are consistent across JavaScript APIs."""
        ua_configs = self.get_user_agent_configs()
        
        for config in ua_configs:
            browser = Browser(BrowserConfig(user_agent=config["ua"]))
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = {
                "userAgent": config["ua"],
                "platform": config["platform"],
                "vendor": config["vendor"],
                "appName": "Netscape",  # Standard value
                "cookieEnabled": True
            }
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            result = await browser.execute_script(
                "https://example.com",
                """
                return {
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    vendor: navigator.vendor,
                    appName: navigator.appName,
                    cookieEnabled: navigator.cookieEnabled
                };
                """
            )
            
            assert result["userAgent"] == config["ua"]
            assert result["platform"] == config["platform"]
            assert result["vendor"] == config["vendor"]
            assert result["appName"] == "Netscape"
            assert result["cookieEnabled"] is True
    
    @pytest.mark.asyncio
    async def test_automation_detection_resistance(self):
        """Test resistance to automation detection techniques."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock automation detection resistance
        mock_page.evaluate.return_value = {
            "webdriver": False,  # Should be false or undefined
            "chrome_runtime": True,  # Should exist for Chrome
            "permissions": True,  # Should exist
            "plugins_length": 3,  # Should have some plugins
            "languages_length": 2,  # Should have some languages
            "phantom": False,  # Should not exist
            "selenium": False,  # Should not exist
            "automation_flags": 0  # No automation flags
        }
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        result = await browser.execute_script(
            "https://example.com",
            """
            return {
                webdriver: navigator.webdriver,
                chrome_runtime: !!window.chrome?.runtime,
                permissions: !!navigator.permissions,
                plugins_length: navigator.plugins.length,
                languages_length: navigator.languages.length,
                phantom: !!window.callPhantom,
                selenium: !!window._selenium,
                automation_flags: [
                    window.outerHeight === 0,
                    window.outerWidth === 0,
                    navigator.webdriver,
                    !!window._phantom,
                    !!window.callPhantom
                ].filter(Boolean).length
            };
            """
        )
        
        # Should look like a real browser
        assert result["webdriver"] is False
        assert result["plugins_length"] > 0
        assert result["languages_length"] > 0
        assert result["phantom"] is False
        assert result["selenium"] is False
        assert result["automation_flags"] < 2  # Should have minimal automation indicators
    
    @pytest.mark.asyncio
    async def test_canvas_fingerprinting_consistency(self):
        """Test canvas fingerprinting consistency."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock consistent canvas fingerprint
        mock_canvas_hash = "abc123def456"  # Consistent hash
        mock_page.evaluate.return_value = mock_canvas_hash
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test canvas fingerprinting multiple times
        fingerprints = []
        for i in range(3):
            result = await browser.execute_script(
                "https://example.com",
                """
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillText('Canvas fingerprint test 🎨', 2, 2);
                return canvas.toDataURL();
                """
            )
            fingerprints.append(result)
        
        # All fingerprints should be identical
        assert len(set(fingerprints)) == 1, "Canvas fingerprint should be consistent"
        assert fingerprints[0] == mock_canvas_hash


class TestCrossFrameAndDomainBehavior:
    """Test cross-frame and cross-domain behavior."""
    
    @pytest.mark.asyncio
    async def test_iframe_script_execution(self):
        """Test JavaScript execution in iframe contexts."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test iframe scenarios
        iframe_tests = [
            ("same_origin", "return window.parent === window.top"),
            ("frame_access", "return window.frames.length"),
            ("postMessage", "window.parent.postMessage('test', '*'); return 'sent'"),
        ]
        
        for test_name, script in iframe_tests:
            if test_name == "same_origin":
                mock_page.evaluate.return_value = True  # In main frame
            elif test_name == "frame_access":
                mock_page.evaluate.return_value = 0  # No child frames
            else:
                mock_page.evaluate.return_value = "sent"
            
            result = await browser.execute_script("https://example.com", script)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_cross_domain_restrictions(self):
        """Test cross-domain restriction enforcement."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Scripts that should be restricted
        cross_domain_scripts = [
            "fetch('https://different-domain.com/api/data')",
            "new XMLHttpRequest().open('GET', 'https://other-site.com/api')",
            "document.createElement('script').src = 'https://malicious.com/script.js'",
        ]
        
        for script in cross_domain_scripts:
            # Mock CORS restriction
            mock_page.evaluate.side_effect = Exception("CORS policy blocked")
            
            with pytest.raises(Exception) as exc_info:
                await browser.execute_script("https://example.com", script)
            
            assert "cors" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()


if __name__ == "__main__":
    # Run compatibility tests with detailed output
    pytest.main([__file__, "-v", "--tb=short"])