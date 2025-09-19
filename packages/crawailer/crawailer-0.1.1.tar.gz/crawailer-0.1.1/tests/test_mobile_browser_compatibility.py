"""
Mobile browser compatibility test suite.

Tests JavaScript execution across different mobile browsers, device configurations,
touch interactions, viewport handling, and mobile-specific web APIs.
"""
import pytest
import asyncio
from typing import Dict, Any, List, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

from crawailer import get, get_many
from crawailer.browser import Browser
from crawailer.config import BrowserConfig


class TestMobileBrowserCompatibility:
    """Test JavaScript execution across mobile browser configurations."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for local test server."""
        return "http://localhost:8083"
    
    @pytest.fixture
    def mobile_configs(self):
        """Mobile browser configurations for testing."""
        return {
            'iphone_13': BrowserConfig(
                viewport={'width': 375, 'height': 812},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                device_scale_factor=3.0
            ),
            'iphone_se': BrowserConfig(
                viewport={'width': 375, 'height': 667},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                device_scale_factor=2.0
            ),
            'android_pixel': BrowserConfig(
                viewport={'width': 393, 'height': 851},
                user_agent='Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Mobile Safari/537.36',
                device_scale_factor=2.75
            ),
            'android_galaxy': BrowserConfig(
                viewport={'width': 360, 'height': 740},
                user_agent='Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36',
                device_scale_factor=3.0
            ),
            'ipad_air': BrowserConfig(
                viewport={'width': 820, 'height': 1180},
                user_agent='Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                device_scale_factor=2.0
            ),
            'android_tablet': BrowserConfig(
                viewport={'width': 768, 'height': 1024},
                user_agent='Mozilla/5.0 (Linux; Android 11; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36',
                device_scale_factor=2.0
            )
        }
    
    @pytest.fixture
    async def mobile_browser(self, mobile_configs):
        """Mobile browser instance for testing."""
        config = mobile_configs['iphone_13']  # Default to iPhone 13
        browser = Browser(config)
        await browser.start()
        yield browser
        await browser.stop()

    # Device Detection and Capabilities
    
    @pytest.mark.asyncio
    async def test_mobile_device_detection(self, base_url, mobile_configs):
        """Test mobile device detection across different configurations."""
        results = {}
        
        for device_name, config in mobile_configs.items():
            browser = Browser(config)
            await browser.start()
            
            try:
                result = await browser.execute_script(
                    f"{base_url}/react/",
                    """
                        return {
                            userAgent: navigator.userAgent,
                            viewport: {
                                width: window.innerWidth,
                                height: window.innerHeight
                            },
                            devicePixelRatio: window.devicePixelRatio,
                            touchSupported: 'ontouchstart' in window,
                            orientation: screen.orientation ? screen.orientation.angle : 'unknown',
                            platform: navigator.platform,
                            isMobile: /Mobi|Android/i.test(navigator.userAgent),
                            isTablet: /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent),
                            screenSize: {
                                width: screen.width,
                                height: screen.height
                            }
                        };
                    """
                )
                
                results[device_name] = result
                
            finally:
                await browser.stop()
        
        # Verify device detection works correctly
        assert len(results) >= 4  # Should test at least 4 devices
        
        # Check iPhone devices
        iphone_devices = [k for k in results.keys() if 'iphone' in k]
        for device in iphone_devices:
            result = results[device]
            assert result['touchSupported'] is True
            assert result['isMobile'] is True
            assert 'iPhone' in result['userAgent']
            assert result['devicePixelRatio'] >= 2.0
        
        # Check Android devices
        android_devices = [k for k in results.keys() if 'android' in k]
        for device in android_devices:
            result = results[device]
            assert result['touchSupported'] is True
            assert 'Android' in result['userAgent']
            assert result['devicePixelRatio'] >= 2.0
    
    @pytest.mark.asyncio
    async def test_viewport_handling(self, base_url, mobile_configs):
        """Test viewport handling and responsive behavior."""
        viewport_tests = []
        
        for device_name, config in list(mobile_configs.items())[:3]:  # Test first 3 for performance
            content = await get(
                f"{base_url}/vue/",
                script="""
                    const viewport = {
                        width: window.innerWidth,
                        height: window.innerHeight,
                        availWidth: screen.availWidth,
                        availHeight: screen.availHeight,
                        orientationType: screen.orientation ? screen.orientation.type : 'unknown',
                        visualViewport: window.visualViewport ? {
                            width: window.visualViewport.width,
                            height: window.visualViewport.height,
                            scale: window.visualViewport.scale
                        } : null
                    };
                    
                    // Test responsive breakpoints
                    const breakpoints = {
                        isMobile: window.innerWidth < 768,
                        isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
                        isDesktop: window.innerWidth >= 1024
                    };
                    
                    return { viewport, breakpoints, deviceName: '""" + device_name + """' };
                """,
                config=config
            )
            
            viewport_tests.append(content.script_result)
        
        # Verify viewport handling
        assert len(viewport_tests) >= 3
        
        for result in viewport_tests:
            assert result['viewport']['width'] > 0
            assert result['viewport']['height'] > 0
            
            # Check responsive breakpoint logic
            width = result['viewport']['width']
            if width < 768:
                assert result['breakpoints']['isMobile'] is True
            elif width >= 768 and width < 1024:
                assert result['breakpoints']['isTablet'] is True
            else:
                assert result['breakpoints']['isDesktop'] is True

    # Touch and Gesture Support
    
    @pytest.mark.asyncio
    async def test_touch_event_support(self, base_url, mobile_configs):
        """Test touch event support and gesture handling."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Test touch event support
                const touchEvents = {
                    touchstart: 'ontouchstart' in window,
                    touchmove: 'ontouchmove' in window,
                    touchend: 'ontouchend' in window,
                    touchcancel: 'ontouchcancel' in window
                };
                
                // Test pointer events (modern touch handling)
                const pointerEvents = {
                    pointerdown: 'onpointerdown' in window,
                    pointermove: 'onpointermove' in window,
                    pointerup: 'onpointerup' in window,
                    pointercancel: 'onpointercancel' in window
                };
                
                // Test gesture support
                const gestureSupport = {
                    gesturestart: 'ongesturestart' in window,
                    gesturechange: 'ongesturechange' in window,
                    gestureend: 'ongestureend' in window
                };
                
                // Simulate touch interaction
                const simulateTouchTap = () => {
                    const button = document.querySelector('[data-testid="increment-btn"]');
                    if (button && touchEvents.touchstart) {
                        const touch = new Touch({
                            identifier: 1,
                            target: button,
                            clientX: 100,
                            clientY: 100
                        });
                        
                        const touchEvent = new TouchEvent('touchstart', {
                            touches: [touch],
                            targetTouches: [touch],
                            changedTouches: [touch],
                            bubbles: true
                        });
                        
                        button.dispatchEvent(touchEvent);
                        return true;
                    }
                    return false;
                };
                
                return {
                    touchEvents,
                    pointerEvents,
                    gestureSupport,
                    touchSimulation: simulateTouchTap()
                };
            """,
            config=mobile_configs['iphone_13']
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify touch support
        assert result['touchEvents']['touchstart'] is True
        assert result['touchEvents']['touchmove'] is True
        assert result['touchEvents']['touchend'] is True
        
        # Modern browsers should support pointer events
        assert result['pointerEvents']['pointerdown'] is True
    
    @pytest.mark.asyncio
    async def test_mobile_scroll_behavior(self, base_url, mobile_configs):
        """Test mobile scroll behavior and momentum scrolling."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Test scroll properties
                const scrollProperties = {
                    scrollX: window.scrollX,
                    scrollY: window.scrollY,
                    pageXOffset: window.pageXOffset,
                    pageYOffset: window.pageYOffset,
                    documentHeight: document.documentElement.scrollHeight,
                    viewportHeight: window.innerHeight,
                    isScrollable: document.documentElement.scrollHeight > window.innerHeight
                };
                
                // Test CSS scroll behavior support
                const scrollBehaviorSupport = CSS.supports('scroll-behavior', 'smooth');
                
                // Test momentum scrolling (iOS Safari)
                const momentumScrolling = getComputedStyle(document.body).webkitOverflowScrolling === 'touch';
                
                // Simulate scroll event
                let scrollEventFired = false;
                window.addEventListener('scroll', () => {
                    scrollEventFired = true;
                }, { once: true });
                
                // Trigger scroll
                window.scrollTo(0, 100);
                
                return {
                    scrollProperties,
                    scrollBehaviorSupport,
                    momentumScrolling,
                    scrollEventFired
                };
            """,
            config=mobile_configs['iphone_13']
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert 'scrollProperties' in result
        assert result['scrollProperties']['documentHeight'] > 0
        assert result['scrollProperties']['viewportHeight'] > 0

    # Mobile-Specific Web APIs
    
    @pytest.mark.asyncio
    async def test_mobile_web_apis(self, base_url, mobile_configs):
        """Test mobile-specific web APIs availability."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                // Test device orientation API
                const deviceOrientationAPI = {
                    supported: 'DeviceOrientationEvent' in window,
                    currentOrientation: screen.orientation ? screen.orientation.type : 'unknown',
                    orientationAngle: screen.orientation ? screen.orientation.angle : 0
                };
                
                // Test device motion API
                const deviceMotionAPI = {
                    supported: 'DeviceMotionEvent' in window,
                    accelerometer: 'DeviceMotionEvent' in window && 'acceleration' in DeviceMotionEvent.prototype,
                    gyroscope: 'DeviceMotionEvent' in window && 'rotationRate' in DeviceMotionEvent.prototype
                };
                
                // Test geolocation API
                const geolocationAPI = {
                    supported: 'geolocation' in navigator,
                    permissions: 'permissions' in navigator
                };
                
                // Test battery API
                const batteryAPI = {
                    supported: 'getBattery' in navigator || 'battery' in navigator
                };
                
                // Test vibration API
                const vibrationAPI = {
                    supported: 'vibrate' in navigator
                };
                
                // Test network information API
                const networkAPI = {
                    supported: 'connection' in navigator,
                    connectionType: navigator.connection ? navigator.connection.effectiveType : 'unknown',
                    downlink: navigator.connection ? navigator.connection.downlink : null
                };
                
                // Test clipboard API
                const clipboardAPI = {
                    supported: 'clipboard' in navigator,
                    readText: navigator.clipboard && 'readText' in navigator.clipboard,
                    writeText: navigator.clipboard && 'writeText' in navigator.clipboard
                };
                
                return {
                    deviceOrientationAPI,
                    deviceMotionAPI,
                    geolocationAPI,
                    batteryAPI,
                    vibrationAPI,
                    networkAPI,
                    clipboardAPI
                };
            """,
            config=mobile_configs['android_pixel']
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Check API availability
        assert 'deviceOrientationAPI' in result
        assert 'geolocationAPI' in result
        assert result['geolocationAPI']['supported'] is True
        
        # Network API is commonly supported
        assert 'networkAPI' in result
    
    @pytest.mark.asyncio
    async def test_mobile_media_queries(self, base_url, mobile_configs):
        """Test CSS media queries and responsive design detection."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Test common mobile media queries
                const mediaQueries = {
                    isMobile: window.matchMedia('(max-width: 767px)').matches,
                    isTablet: window.matchMedia('(min-width: 768px) and (max-width: 1023px)').matches,
                    isDesktop: window.matchMedia('(min-width: 1024px)').matches,
                    isPortrait: window.matchMedia('(orientation: portrait)').matches,
                    isLandscape: window.matchMedia('(orientation: landscape)').matches,
                    isRetina: window.matchMedia('(-webkit-min-device-pixel-ratio: 2)').matches,
                    isHighDPI: window.matchMedia('(min-resolution: 192dpi)').matches,
                    hasHover: window.matchMedia('(hover: hover)').matches,
                    hasFinePointer: window.matchMedia('(pointer: fine)').matches,
                    hasCoarsePointer: window.matchMedia('(pointer: coarse)').matches
                };
                
                // Test CSS feature queries
                const cssFeatures = {
                    supportsGrid: CSS.supports('display', 'grid'),
                    supportsFlexbox: CSS.supports('display', 'flex'),
                    supportsCustomProperties: CSS.supports('color', 'var(--test)'),
                    supportsViewportUnits: CSS.supports('width', '100vw'),
                    supportsCalc: CSS.supports('width', 'calc(100% - 10px)')
                };
                
                return {
                    mediaQueries,
                    cssFeatures,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                };
            """,
            config=mobile_configs['iphone_se']
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify media query logic
        viewport_width = result['viewport']['width']
        
        if viewport_width <= 767:
            assert result['mediaQueries']['isMobile'] is True
        elif viewport_width >= 768 and viewport_width <= 1023:
            assert result['mediaQueries']['isTablet'] is True
        else:
            assert result['mediaQueries']['isDesktop'] is True
        
        # Check modern CSS support
        assert result['cssFeatures']['supportsFlexbox'] is True
        assert result['cssFeatures']['supportsGrid'] is True

    # Performance on Mobile Devices
    
    @pytest.mark.asyncio
    async def test_mobile_performance_characteristics(self, base_url, mobile_configs):
        """Test performance characteristics on mobile devices."""
        results = []
        
        # Test on different mobile configurations
        test_configs = ['iphone_13', 'android_pixel', 'ipad_air']
        
        for device_name in test_configs:
            config = mobile_configs[device_name]
            
            content = await get(
                f"{base_url}/vue/",
                script="""
                    const performanceStart = performance.now();
                    
                    // Simulate heavy DOM operations (mobile-typical workload)
                    for (let i = 0; i < 50; i++) {
                        window.testData.simulateUserAction('add-todo');
                    }
                    
                    const performanceEnd = performance.now();
                    
                    // Test memory performance
                    const memoryInfo = performance.memory ? {
                        usedJSHeapSize: performance.memory.usedJSHeapSize,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                    } : null;
                    
                    // Test frame rate
                    let frameCount = 0;
                    const frameStart = performance.now();
                    
                    const countFrames = () => {
                        frameCount++;
                        const elapsed = performance.now() - frameStart;
                        if (elapsed < 1000) {
                            requestAnimationFrame(countFrames);
                        }
                    };
                    
                    return new Promise(resolve => {
                        requestAnimationFrame(countFrames);
                        setTimeout(() => {
                            resolve({
                                operationTime: performanceEnd - performanceStart,
                                memoryInfo,
                                estimatedFPS: frameCount,
                                devicePixelRatio: window.devicePixelRatio,
                                deviceName: '""" + device_name + """'
                            });
                        }, 1100);
                    });
                """,
                config=config
            )
            
            if content.script_result:
                results.append(content.script_result)
        
        # Verify performance results
        assert len(results) >= 2
        
        for result in results:
            assert result['operationTime'] > 0
            assert result['devicePixelRatio'] >= 1.0
            
            # Mobile devices should complete operations in reasonable time
            assert result['operationTime'] < 5000  # Less than 5 seconds
            
            # FPS should be reasonable (not perfect due to testing environment)
            if result['estimatedFPS'] > 0:
                assert result['estimatedFPS'] >= 10  # At least 10 FPS

    # Mobile Browser-Specific Quirks
    
    @pytest.mark.asyncio
    async def test_safari_mobile_quirks(self, base_url, mobile_configs):
        """Test Safari mobile-specific behavior and quirks."""
        content = await get(
            f"{base_url}/react/",
            script="""
                const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);
                
                // Test Safari-specific features
                const safariFeatures = {
                    isSafari,
                    hasWebkitOverflowScrolling: CSS.supports('-webkit-overflow-scrolling', 'touch'),
                    hasWebkitAppearance: CSS.supports('-webkit-appearance', 'none'),
                    hasWebkitTextSizeAdjust: CSS.supports('-webkit-text-size-adjust', '100%'),
                    safariVersion: isSafari ? navigator.userAgent.match(/Version\/([\\d.]+)/)?.[1] : null
                };
                
                // Test iOS-specific viewport behavior
                const viewportBehavior = {
                    initialScale: document.querySelector('meta[name="viewport"]')?.content.includes('initial-scale'),
                    userScalable: document.querySelector('meta[name="viewport"]')?.content.includes('user-scalable'),
                    viewportHeight: window.innerHeight,
                    visualViewportHeight: window.visualViewport ? window.visualViewport.height : null,
                    heightDifference: window.visualViewport ? 
                        Math.abs(window.innerHeight - window.visualViewport.height) : 0
                };
                
                // Test date input quirks (Safari mobile has unique behavior)
                const dateInputSupport = {
                    supportsDateInput: (() => {
                        const input = document.createElement('input');
                        input.type = 'date';
                        return input.type === 'date';
                    })(),
                    supportsDatetimeLocal: (() => {
                        const input = document.createElement('input');
                        input.type = 'datetime-local';
                        return input.type === 'datetime-local';
                    })()
                };
                
                return {
                    safariFeatures,
                    viewportBehavior,
                    dateInputSupport
                };
            """,
            config=mobile_configs['iphone_13']
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Check Safari detection
        safari_features = result['safariFeatures']
        if safari_features['isSafari']:
            assert safari_features['hasWebkitOverflowScrolling'] is True
            assert safari_features['safariVersion'] is not None
    
    @pytest.mark.asyncio
    async def test_android_chrome_quirks(self, base_url, mobile_configs):
        """Test Android Chrome-specific behavior and quirks."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                const isAndroidChrome = /Android/.test(navigator.userAgent) && /Chrome/.test(navigator.userAgent);
                
                // Test Android Chrome-specific features
                const chromeFeatures = {
                    isAndroidChrome,
                    chromeVersion: isAndroidChrome ? navigator.userAgent.match(/Chrome\/([\\d.]+)/)?.[1] : null,
                    hasWebShare: 'share' in navigator,
                    hasWebShareTarget: 'serviceWorker' in navigator,
                    hasInstallPrompt: 'onbeforeinstallprompt' in window
                };
                
                // Test Android-specific viewport behavior
                const androidViewport = {
                    hasMetaViewport: !!document.querySelector('meta[name="viewport"]'),
                    densityDPI: screen.pixelDepth || screen.colorDepth,
                    screenDensity: window.devicePixelRatio
                };
                
                // Test Chrome mobile address bar behavior
                const addressBarBehavior = {
                    documentHeight: document.documentElement.clientHeight,
                    windowHeight: window.innerHeight,
                    screenHeight: screen.height,
                    availHeight: screen.availHeight,
                    heightRatio: window.innerHeight / screen.height
                };
                
                return {
                    chromeFeatures,
                    androidViewport,
                    addressBarBehavior
                };
            """,
            config=mobile_configs['android_pixel']
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Check Android Chrome detection
        chrome_features = result['chromeFeatures']
        if chrome_features['isAndroidChrome']:
            assert chrome_features['chromeVersion'] is not None
            # Web Share API is commonly supported on Android Chrome
            assert 'hasWebShare' in chrome_features

    # Cross-Device Compatibility
    
    @pytest.mark.asyncio
    async def test_cross_device_javascript_consistency(self, base_url, mobile_configs):
        """Test JavaScript execution consistency across mobile devices."""
        framework_results = {}
        
        # Test same script across multiple devices
        test_script = """
            const testResults = {
                basicMath: 2 + 2,
                stringManipulation: 'Hello World'.toLowerCase(),
                arrayMethods: [1, 2, 3].map(x => x * 2),
                objectSpread: {...{a: 1}, b: 2},
                promiseSupport: typeof Promise !== 'undefined',
                arrowFunctions: (() => 'arrow function test')(),
                templateLiterals: `Template literal test: ${42}`,
                destructuring: (() => {
                    const [a, b] = [1, 2];
                    return a + b;
                })()
            };
            
            return testResults;
        """
        
        devices_to_test = ['iphone_13', 'android_pixel', 'ipad_air']
        
        for device_name in devices_to_test:
            config = mobile_configs[device_name]
            
            content = await get(
                f"{base_url}/react/",
                script=test_script,
                config=config
            )
            
            if content.script_result:
                framework_results[device_name] = content.script_result
        
        # Verify consistency across devices
        assert len(framework_results) >= 2
        
        # All devices should produce identical results
        expected_results = {
            'basicMath': 4,
            'stringManipulation': 'hello world',
            'arrayMethods': [2, 4, 6],
            'objectSpread': {'a': 1, 'b': 2},
            'promiseSupport': True,
            'arrowFunctions': 'arrow function test',
            'templateLiterals': 'Template literal test: 42',
            'destructuring': 3
        }
        
        for device_name, result in framework_results.items():
            for key, expected_value in expected_results.items():
                assert result[key] == expected_value, f"Inconsistency on {device_name} for {key}"


class TestTabletSpecificFeatures:
    """Test tablet-specific features and behaviors."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8083"
    
    @pytest.mark.asyncio
    async def test_tablet_viewport_behavior(self, base_url):
        """Test tablet viewport and responsive behavior."""
        tablet_config = BrowserConfig(
            viewport={'width': 768, 'height': 1024},
            user_agent='Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            device_scale_factor=2.0
        )
        
        content = await get(
            f"{base_url}/angular/",
            script="""
                return {
                    isTabletViewport: window.innerWidth >= 768 && window.innerWidth < 1024,
                    supportsHover: window.matchMedia('(hover: hover)').matches,
                    hasFinePointer: window.matchMedia('(pointer: fine)').matches,
                    orientation: screen.orientation ? screen.orientation.type : 'unknown',
                    aspectRatio: window.innerWidth / window.innerHeight
                };
            """,
            config=tablet_config
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['isTabletViewport'] is True
        assert result['aspectRatio'] > 0


class TestMobileTestingInfrastructure:
    """Test mobile testing infrastructure integration."""
    
    @pytest.mark.asyncio
    async def test_mobile_with_existing_test_patterns(self):
        """Test mobile configurations with existing test infrastructure."""
        from tests.test_javascript_api import MockHTTPServer
        
        server = MockHTTPServer()
        await server.start()
        
        mobile_config = BrowserConfig(
            viewport={'width': 375, 'height': 667},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'
        )
        
        try:
            content = await get(
                f"http://localhost:{server.port}/mobile-test",
                script="""
                    return {
                        isMobile: window.innerWidth < 768,
                        touchSupported: 'ontouchstart' in window,
                        userAgent: navigator.userAgent
                    };
                """,
                config=mobile_config
            )
            
            assert content.script_result is not None
            result = content.script_result
            
            assert result['isMobile'] is True
            assert result['touchSupported'] is True
            assert 'iPhone' in result['userAgent']
            
        finally:
            await server.stop()
    
    @pytest.mark.asyncio
    async def test_mobile_framework_integration(self, mobile_configs):
        """Test mobile configurations with framework testing."""
        mobile_config = mobile_configs['android_galaxy']
        
        browser = Browser(mobile_config)
        await browser.start()
        
        try:
            # Test framework detection on mobile
            result = await browser.execute_script(
                "http://localhost:8083/vue/",
                """
                    const mobileFeatures = {
                        framework: window.testData.framework,
                        isMobile: window.innerWidth < 768,
                        touchEvents: 'ontouchstart' in window,
                        devicePixelRatio: window.devicePixelRatio
                    };
                    
                    return mobileFeatures;
                """
            )
            
            assert result is not None
            assert result['framework'] == 'vue'
            assert result['isMobile'] is True
            assert result['touchEvents'] is True
            assert result['devicePixelRatio'] >= 2.0
            
        finally:
            await browser.stop()