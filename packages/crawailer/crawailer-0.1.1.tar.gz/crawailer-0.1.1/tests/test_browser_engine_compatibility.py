"""
Browser engine compatibility test suite.

Tests JavaScript execution compatibility across different browser engines,
versions, and configurations. Validates API differences, performance variations,
and engine-specific behaviors between Chromium, Firefox, Safari, and Edge.
"""
import pytest
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

from crawailer import get, get_many
from crawailer.browser import Browser
from crawailer.config import BrowserConfig


class TestBrowserEngineCompatibility:
    """Test JavaScript execution across different browser engines."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for local test server."""
        return "http://localhost:8083"
    
    @pytest.fixture
    def engine_configs(self):
        """Browser configurations for different engines."""
        return {
            'chromium_latest': BrowserConfig(
                headless=True,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ),
            'chromium_legacy': BrowserConfig(
                headless=True,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
            ),
            'firefox_simulation': BrowserConfig(
                headless=True,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0'
            ),
            'safari_simulation': BrowserConfig(
                headless=True,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
            ),
            'edge_simulation': BrowserConfig(
                headless=True,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
            )
        }

    # Core Engine Detection and Features
    
    @pytest.mark.asyncio
    async def test_engine_detection_accuracy(self, base_url, engine_configs):
        """Test accurate detection of browser engines and their capabilities."""
        engine_results = {}
        
        for engine_name, config in engine_configs.items():
            content = await get(
                f"{base_url}/react/",
                script="""
                    // Comprehensive engine detection
                    const engineDetector = {
                        userAgent: navigator.userAgent,
                        vendor: navigator.vendor || '',
                        
                        // Primary engine detection
                        detection: {
                            isChromium: !!window.chrome || /Chrome|Chromium/.test(navigator.userAgent),
                            isGecko: typeof InstallTrigger !== 'undefined' || /Firefox|Gecko/.test(navigator.userAgent),
                            isWebKit: /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent),
                            isBlink: !!window.chrome && !!window.chrome.runtime,
                            isEdge: /Edg/.test(navigator.userAgent) || /Edge/.test(navigator.userAgent),
                            isOpera: /OPR|Opera/.test(navigator.userAgent)
                        },
                        
                        // Version extraction
                        versions: {
                            chrome: navigator.userAgent.match(/Chrome\\/(\\d+\\.\\d+\\.\\d+\\.\\d+)/)?.[1],
                            firefox: navigator.userAgent.match(/Firefox\\/(\\d+\\.\\d+)/)?.[1],
                            safari: navigator.userAgent.match(/Version\\/(\\d+\\.\\d+)/)?.[1],
                            edge: navigator.userAgent.match(/Edg\\/(\\d+\\.\\d+\\.\\d+\\.\\d+)/)?.[1]
                        },
                        
                        // Engine-specific global objects
                        globalObjects: {
                            chrome: typeof window.chrome !== 'undefined',
                            InstallTrigger: typeof InstallTrigger !== 'undefined',
                            safari: typeof window.safari !== 'undefined',
                            opera: typeof window.opera !== 'undefined'
                        },
                        
                        // CSS engine prefixes
                        cssSupport: {
                            webkit: CSS.supports('-webkit-appearance', 'none'),
                            moz: CSS.supports('-moz-appearance', 'none'),
                            ms: CSS.supports('-ms-filter', 'blur(5px)'),
                            o: CSS.supports('-o-transform', 'rotate(45deg)')
                        },
                        
                        // JavaScript engine features
                        jsEngineFeatures: {
                            v8: typeof window.chrome !== 'undefined',
                            spiderMonkey: typeof netscape !== 'undefined',
                            javaScriptCore: /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent),
                            chakra: /Edge/.test(navigator.userAgent) && /Trident/.test(navigator.userAgent)
                        },
                        
                        // Performance characteristics
                        performanceSignature: {
                            startTime: performance.now(),
                            memoryInfo: performance.memory ? {
                                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                                totalJSHeapSize: performance.memory.totalJSHeapSize,
                                usedJSHeapSize: performance.memory.usedJSHeapSize
                            } : null,
                            timing: performance.timing ? {
                                navigationStart: performance.timing.navigationStart,
                                loadEventEnd: performance.timing.loadEventEnd,
                                domContentLoadedEventEnd: performance.timing.domContentLoadedEventEnd
                            } : null
                        }
                    };
                    
                    // Additional engine-specific tests
                    const engineSpecificTests = {
                        chromium: {
                            hasChrome: !!window.chrome,
                            hasWebkitRequestFileSystem: !!window.webkitRequestFileSystem,
                            hasWebkitStorageInfo: !!(navigator.webkitTemporaryStorage || navigator.webkitPersistentStorage),
                            hasWebkitSpeechRecognition: !!window.webkitSpeechRecognition
                        },
                        
                        gecko: {
                            hasMozGetUserMedia: !!navigator.mozGetUserMedia,
                            hasMozRequestFullScreen: !!document.documentElement.mozRequestFullScreen,
                            hasMozIndexedDB: !!window.mozIndexedDB,
                            hasMozConnection: !!navigator.mozConnection
                        },
                        
                        webkit: {
                            hasWebkitOverflowScrolling: CSS.supports('-webkit-overflow-scrolling', 'touch'),
                            hasWebkitTextSizeAdjust: CSS.supports('-webkit-text-size-adjust', '100%'),
                            hasWebkitBackfaceVisibility: CSS.supports('-webkit-backface-visibility', 'hidden'),
                            hasWebkitTransform3d: CSS.supports('-webkit-transform', 'translate3d(0,0,0)')
                        }
                    };
                    
                    return {
                        engineDetector,
                        engineSpecificTests,
                        detectedEngine: Object.keys(engineDetector.detection).find(key => 
                            engineDetector.detection[key] === true
                        ),
                        confidence: Object.values(engineDetector.detection).filter(Boolean).length
                    };
                """,
                config=config
            )
            
            if content.script_result:
                engine_results[engine_name] = {
                    'config': engine_name,
                    'result': content.script_result,
                    'success': True
                }
            else:
                engine_results[engine_name] = {
                    'config': engine_name,
                    'error': 'Failed to detect engine',
                    'success': False
                }
        
        # Verify engine detection results
        assert len(engine_results) > 0
        
        successful_results = {k: v for k, v in engine_results.items() if v['success']}
        assert len(successful_results) > 0
        
        # Verify detection accuracy
        for engine_name, result in successful_results.items():
            detection_result = result['result']
            
            assert 'engineDetector' in detection_result
            assert 'detectedEngine' in detection_result
            assert 'confidence' in detection_result
            
            # Check that at least one engine was detected
            assert detection_result['confidence'] >= 1
            
            # Verify engine-specific features
            engine_detector = detection_result['engineDetector']
            assert 'detection' in engine_detector
            assert 'versions' in engine_detector
            assert 'globalObjects' in engine_detector
            assert 'cssSupport' in engine_detector
    
    @pytest.mark.asyncio
    async def test_javascript_api_compatibility(self, base_url, engine_configs):
        """Test JavaScript API compatibility across different engines."""
        api_compatibility_results = {}
        
        # Test a subset of engines for performance
        test_configs = {k: v for i, (k, v) in enumerate(engine_configs.items()) if i < 3}
        
        for engine_name, config in test_configs.items():
            content = await get(
                f"{base_url}/vue/",
                script="""
                    // Comprehensive JavaScript API compatibility testing
                    const apiCompatibility = {
                        coreFeatures: {
                            // ES6+ Features
                            arrow_functions: (() => true)(),
                            template_literals: `template ${1 + 1}` === 'template 2',
                            destructuring: (() => { const [a] = [1]; return a === 1; })(),
                            spread_operator: (() => { const arr = [1, 2]; return [...arr].length === 2; })(),
                            classes: typeof class TestClass {} === 'function',
                            async_await: typeof (async () => {}) === 'function',
                            
                            // Promises
                            promises: typeof Promise !== 'undefined',
                            promise_allSettled: typeof Promise.allSettled === 'function',
                            promise_any: typeof Promise.any === 'function',
                            
                            // Modern JavaScript
                            bigint: typeof BigInt !== 'undefined',
                            weakMap: typeof WeakMap !== 'undefined',
                            weakSet: typeof WeakSet !== 'undefined',
                            proxy: typeof Proxy !== 'undefined',
                            symbol: typeof Symbol !== 'undefined',
                            map: typeof Map !== 'undefined',
                            set: typeof Set !== 'undefined'
                        },
                        
                        domApi: {
                            // DOM Level 4
                            querySelector: typeof document.querySelector === 'function',
                            querySelectorAll: typeof document.querySelectorAll === 'function',
                            getElementsByClassName: typeof document.getElementsByClassName === 'function',
                            getElementById: typeof document.getElementById === 'function',
                            
                            // Modern DOM APIs
                            customElements: typeof customElements !== 'undefined',
                            shadowDOM: typeof Element.prototype.attachShadow === 'function',
                            intersectionObserver: typeof IntersectionObserver !== 'undefined',
                            mutationObserver: typeof MutationObserver !== 'undefined',
                            resizeObserver: typeof ResizeObserver !== 'undefined',
                            
                            // Event APIs
                            addEventListener: typeof EventTarget.prototype.addEventListener === 'function',
                            customEvent: typeof CustomEvent !== 'undefined',
                            eventTarget: typeof EventTarget !== 'undefined'
                        },
                        
                        webApis: {
                            // Storage APIs
                            localStorage: typeof localStorage !== 'undefined',
                            sessionStorage: typeof sessionStorage !== 'undefined',
                            indexedDB: typeof indexedDB !== 'undefined',
                            
                            // Network APIs
                            fetch: typeof fetch !== 'undefined',
                            xmlHttpRequest: typeof XMLHttpRequest !== 'undefined',
                            websocket: typeof WebSocket !== 'undefined',
                            
                            // Media APIs
                            getUserMedia: !!(navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia),
                            mediaDevices: typeof navigator.mediaDevices !== 'undefined',
                            audioContext: !!(window.AudioContext || window.webkitAudioContext),
                            
                            // Graphics APIs
                            canvas: typeof HTMLCanvasElement !== 'undefined',
                            webgl: (() => {
                                try {
                                    const canvas = document.createElement('canvas');
                                    return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
                                } catch { return false; }
                            })(),
                            webgl2: (() => {
                                try {
                                    const canvas = document.createElement('canvas');
                                    return !!canvas.getContext('webgl2');
                                } catch { return false; }
                            })(),
                            
                            // Worker APIs
                            worker: typeof Worker !== 'undefined',
                            sharedWorker: typeof SharedWorker !== 'undefined',
                            serviceWorker: typeof navigator.serviceWorker !== 'undefined',
                            
                            // Performance APIs
                            performance: typeof performance !== 'undefined',
                            performanceObserver: typeof PerformanceObserver !== 'undefined',
                            requestAnimationFrame: typeof requestAnimationFrame !== 'undefined',
                            requestIdleCallback: typeof requestIdleCallback !== 'undefined'
                        },
                        
                        modernFeatures: {
                            // ES2020+
                            optional_chaining: (() => { try { return ({})?.nonexistent === undefined; } catch { return false; } })(),
                            nullish_coalescing: (() => { try { return (null ?? 'default') === 'default'; } catch { return false; } })(),
                            dynamic_import: typeof import === 'function',
                            
                            // Web Components
                            htmlTemplateElement: typeof HTMLTemplateElement !== 'undefined',
                            htmlSlotElement: typeof HTMLSlotElement !== 'undefined',
                            
                            // CSS APIs
                            cssStyleSheet: typeof CSSStyleSheet !== 'undefined',
                            cssSupports: typeof CSS !== 'undefined' && typeof CSS.supports === 'function',
                            
                            // Module APIs
                            importMaps: HTMLScriptElement.supports && HTMLScriptElement.supports('importmap'),
                            topLevelAwait: (() => { try { eval('await Promise.resolve()'); return true; } catch { return false; } })()
                        },
                        
                        securityFeatures: {
                            // CSP and Security
                            contentSecurityPolicy: typeof SecurityPolicyViolationEvent !== 'undefined',
                            subresourceIntegrity: (() => {
                                const script = document.createElement('script');
                                return typeof script.integrity !== 'undefined';
                            })(),
                            
                            // Crypto APIs
                            crypto: typeof crypto !== 'undefined',
                            subtle: typeof crypto?.subtle !== 'undefined',
                            
                            // Origin and CORS
                            crossOriginIsolated: typeof crossOriginIsolated !== 'undefined',
                            trustedTypes: typeof trustedTypes !== 'undefined'
                        }
                    };
                    
                    // Calculate compatibility scores
                    const calculateScore = (category) => {
                        const features = Object.values(category);
                        const supported = features.filter(Boolean).length;
                        return {
                            supported,
                            total: features.length,
                            percentage: (supported / features.length) * 100
                        };
                    };
                    
                    const compatibilityScores = {
                        coreFeatures: calculateScore(apiCompatibility.coreFeatures),
                        domApi: calculateScore(apiCompatibility.domApi),
                        webApis: calculateScore(apiCompatibility.webApis),
                        modernFeatures: calculateScore(apiCompatibility.modernFeatures),
                        securityFeatures: calculateScore(apiCompatibility.securityFeatures)
                    };
                    
                    const overallScore = {
                        supported: Object.values(compatibilityScores).reduce((sum, score) => sum + score.supported, 0),
                        total: Object.values(compatibilityScores).reduce((sum, score) => sum + score.total, 0),
                        percentage: 0
                    };
                    overallScore.percentage = (overallScore.supported / overallScore.total) * 100;
                    
                    return {
                        apiCompatibility,
                        compatibilityScores,
                        overallScore,
                        userAgent: navigator.userAgent,
                        testTimestamp: Date.now()
                    };
                """,
                config=config
            )
            
            if content.script_result:
                api_compatibility_results[engine_name] = content.script_result
        
        # Verify API compatibility results
        assert len(api_compatibility_results) > 0
        
        for engine_name, result in api_compatibility_results.items():
            assert 'overallScore' in result
            assert 'compatibilityScores' in result
            
            overall_score = result['overallScore']
            assert overall_score['supported'] > 0
            assert overall_score['total'] > 0
            assert overall_score['percentage'] > 0
            assert overall_score['percentage'] <= 100
            
            # Check individual category scores
            scores = result['compatibilityScores']
            for category_name, category_score in scores.items():
                assert category_score['supported'] >= 0
                assert category_score['total'] > 0
                assert category_score['percentage'] >= 0
                assert category_score['percentage'] <= 100
            
            # Core features should have high compatibility
            assert scores['coreFeatures']['percentage'] > 80
            assert scores['domApi']['percentage'] > 90
    
    @pytest.mark.asyncio
    async def test_performance_characteristics_comparison(self, base_url, engine_configs):
        """Test performance characteristics across different browser engines."""
        performance_results = {}
        
        # Test first 3 configs to avoid excessive test time
        test_configs = {k: v for i, (k, v) in enumerate(engine_configs.items()) if i < 3}
        
        for engine_name, config in test_configs.items():
            content = await get(
                f"{base_url}/angular/",
                script="""
                    // Comprehensive performance testing across engines
                    class EnginePerformanceTester {
                        constructor() {
                            this.results = {};
                        }
                        
                        async testJavaScriptPerformance() {
                            const tests = {
                                arithmetic: await this.testArithmetic(),
                                stringManipulation: await this.testStringManipulation(),
                                arrayOperations: await this.testArrayOperations(),
                                objectOperations: await this.testObjectOperations(),
                                functionCalls: await this.testFunctionCalls()
                            };
                            
                            return tests;
                        }
                        
                        async testArithmetic() {
                            const iterations = 100000;
                            const start = performance.now();
                            
                            let result = 0;
                            for (let i = 0; i < iterations; i++) {
                                result += Math.sqrt(i) * Math.sin(i) + Math.cos(i);
                            }
                            
                            const end = performance.now();
                            
                            return {
                                duration: end - start,
                                iterations,
                                operationsPerSecond: iterations / ((end - start) / 1000),
                                result: result % 1000
                            };
                        }
                        
                        async testStringManipulation() {
                            const iterations = 10000;
                            const start = performance.now();
                            
                            let result = '';
                            for (let i = 0; i < iterations; i++) {
                                result += `String ${i} - ${Math.random().toString(36).substr(2, 9)}`;
                                if (i % 100 === 0) {
                                    result = result.substr(-1000); // Prevent memory buildup
                                }
                            }
                            
                            const end = performance.now();
                            
                            return {
                                duration: end - start,
                                iterations,
                                operationsPerSecond: iterations / ((end - start) / 1000),
                                finalLength: result.length
                            };
                        }
                        
                        async testArrayOperations() {
                            const size = 10000;
                            const start = performance.now();
                            
                            // Create array
                            const array = new Array(size).fill(0).map((_, i) => i);
                            
                            // Perform operations
                            const filtered = array.filter(x => x % 2 === 0);
                            const mapped = array.map(x => x * 2);
                            const reduced = array.reduce((sum, x) => sum + x, 0);
                            const sorted = [...array].sort((a, b) => b - a);
                            
                            const end = performance.now();
                            
                            return {
                                duration: end - start,
                                arraySize: size,
                                operations: 4,
                                operationsPerSecond: (size * 4) / ((end - start) / 1000),
                                results: {
                                    filteredLength: filtered.length,
                                    mappedLength: mapped.length,
                                    reducedValue: reduced,
                                    sortedFirst: sorted[0]
                                }
                            };
                        }
                        
                        async testObjectOperations() {
                            const iterations = 5000;
                            const start = performance.now();
                            
                            const objects = [];
                            
                            // Create objects
                            for (let i = 0; i < iterations; i++) {
                                objects.push({
                                    id: i,
                                    data: { value: Math.random(), computed: i * 2 },
                                    methods: {
                                        getValue: function() { return this.data.value; },
                                        getComputed: function() { return this.data.computed; }
                                    }
                                });
                            }
                            
                            // Access and manipulate
                            let sum = 0;
                            for (const obj of objects) {
                                sum += obj.methods.getValue() + obj.methods.getComputed();
                                obj.data.accessed = true;
                            }
                            
                            const end = performance.now();
                            
                            return {
                                duration: end - start,
                                iterations,
                                operationsPerSecond: iterations / ((end - start) / 1000),
                                sum,
                                objectCount: objects.length
                            };
                        }
                        
                        async testFunctionCalls() {
                            const iterations = 50000;
                            
                            const testFunction = (a, b, c) => a + b * c;
                            const testArrowFunction = (a, b, c) => a + b * c;
                            const testMethodCall = { method: function(a, b, c) { return a + b * c; } };
                            
                            const start = performance.now();
                            
                            let result = 0;
                            for (let i = 0; i < iterations; i++) {
                                result += testFunction(i, i + 1, i + 2);
                                result += testArrowFunction(i, i + 1, i + 2);
                                result += testMethodCall.method(i, i + 1, i + 2);
                            }
                            
                            const end = performance.now();
                            
                            return {
                                duration: end - start,
                                iterations: iterations * 3, // 3 function calls per iteration
                                operationsPerSecond: (iterations * 3) / ((end - start) / 1000),
                                result: result % 1000000
                            };
                        }
                        
                        async testDOMPerformance() {
                            const iterations = 1000;
                            const start = performance.now();
                            
                            const container = document.createElement('div');
                            container.style.display = 'none';
                            document.body.appendChild(container);
                            
                            // Create elements
                            for (let i = 0; i < iterations; i++) {
                                const element = document.createElement('div');
                                element.className = `test-element-${i}`;
                                element.textContent = `Element ${i}`;
                                container.appendChild(element);
                            }
                            
                            // Query elements
                            const elements = container.querySelectorAll('.test-element-1, .test-element-10, .test-element-100');
                            
                            // Modify elements
                            elements.forEach(el => {
                                el.style.backgroundColor = 'red';
                                el.style.padding = '5px';
                            });
                            
                            const end = performance.now();
                            
                            // Cleanup
                            document.body.removeChild(container);
                            
                            return {
                                duration: end - start,
                                elementsCreated: iterations,
                                elementsQueried: elements.length,
                                operationsPerSecond: (iterations + elements.length) / ((end - start) / 1000)
                            };
                        }
                        
                        async testMemoryPerformance() {
                            const memoryInfo = performance.memory ? {
                                initial: {
                                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                                    usedJSHeapSize: performance.memory.usedJSHeapSize
                                }
                            } : { available: false };
                            
                            if (!memoryInfo.available) {
                                return memoryInfo;
                            }
                            
                            // Allocate memory
                            const allocations = [];
                            const start = performance.now();
                            
                            for (let i = 0; i < 1000; i++) {
                                allocations.push(new Array(1000).fill(Math.random()));
                            }
                            
                            const middle = performance.now();
                            
                            memoryInfo.afterAllocation = {
                                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                                totalJSHeapSize: performance.memory.totalJSHeapSize,
                                usedJSHeapSize: performance.memory.usedJSHeapSize
                            };
                            
                            // Clear allocations
                            allocations.length = 0;
                            
                            const end = performance.now();
                            
                            memoryInfo.afterCleanup = {
                                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                                totalJSHeapSize: performance.memory.totalJSHeapSize,
                                usedJSHeapSize: performance.memory.usedJSHeapSize
                            };
                            
                            memoryInfo.performance = {
                                allocationTime: middle - start,
                                cleanupTime: end - middle,
                                totalTime: end - start
                            };
                            
                            return memoryInfo;
                        }
                        
                        async runAllTests() {
                            const results = {
                                startTime: Date.now(),
                                userAgent: navigator.userAgent,
                                platform: navigator.platform,
                                hardwareConcurrency: navigator.hardwareConcurrency,
                                tests: {}
                            };
                            
                            try {
                                results.tests.javascript = await this.testJavaScriptPerformance();
                                results.tests.dom = await this.testDOMPerformance();
                                results.tests.memory = await this.testMemoryPerformance();
                            } catch (error) {
                                results.error = error.message;
                            }
                            
                            results.endTime = Date.now();
                            results.totalDuration = results.endTime - results.startTime;
                            
                            return results;
                        }
                    }
                    
                    const tester = new EnginePerformanceTester();
                    return await tester.runAllTests();
                """,
                config=config
            )
            
            if content.script_result:
                performance_results[engine_name] = content.script_result
        
        # Verify performance results
        assert len(performance_results) > 0
        
        for engine_name, result in performance_results.items():
            assert 'tests' in result
            assert 'totalDuration' in result
            assert result['totalDuration'] > 0
            
            tests = result['tests']
            
            # Check JavaScript performance tests
            if 'javascript' in tests:
                js_tests = tests['javascript']
                for test_name, test_result in js_tests.items():
                    assert 'duration' in test_result
                    assert 'operationsPerSecond' in test_result
                    assert test_result['duration'] > 0
                    assert test_result['operationsPerSecond'] > 0
            
            # Check DOM performance
            if 'dom' in tests:
                dom_test = tests['dom']
                assert 'elementsCreated' in dom_test
                assert 'operationsPerSecond' in dom_test
                assert dom_test['elementsCreated'] > 0
            
            # Check memory performance (if available)
            if 'memory' in tests and tests['memory'].get('available', True):
                memory_test = tests['memory']
                assert 'initial' in memory_test
                assert 'afterAllocation' in memory_test


class TestEngineSpecificBehaviors:
    """Test engine-specific behaviors and quirks."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8083"
    
    @pytest.mark.asyncio
    async def test_chromium_specific_features(self, base_url):
        """Test Chromium/Blink-specific features and behaviors."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Test Chromium-specific features
                const chromiumFeatures = {
                    detection: {
                        isChromium: !!window.chrome || /Chrome/.test(navigator.userAgent),
                        userAgent: navigator.userAgent,
                        vendor: navigator.vendor
                    },
                    
                    apis: {
                        // File System Access API
                        fileSystemAccess: typeof window.showOpenFilePicker !== 'undefined',
                        
                        // Web Serial API
                        webSerial: typeof navigator.serial !== 'undefined',
                        
                        // Web USB API
                        webUSB: typeof navigator.usb !== 'undefined',
                        
                        // Web Bluetooth API
                        webBluetooth: typeof navigator.bluetooth !== 'undefined',
                        
                        // Web Share API
                        webShare: typeof navigator.share !== 'undefined',
                        
                        // Web Locks API
                        webLocks: typeof navigator.locks !== 'undefined',
                        
                        // Broadcast Channel API
                        broadcastChannel: typeof BroadcastChannel !== 'undefined',
                        
                        // Web NFC API
                        webNFC: typeof NDEFReader !== 'undefined',
                        
                        // Origin Private File System API
                        originPrivateFileSystem: typeof navigator.storage?.getDirectory !== 'undefined',
                        
                        // Web Streams API
                        webStreams: typeof ReadableStream !== 'undefined',
                        
                        // Compression Streams API
                        compressionStreams: typeof CompressionStream !== 'undefined'
                    },
                    
                    cssFeatures: {
                        // CSS Container Queries
                        containerQueries: CSS.supports('container-type', 'inline-size'),
                        
                        // CSS Subgrid
                        subgrid: CSS.supports('grid-template-rows', 'subgrid'),
                        
                        // CSS Cascade Layers
                        cascadeLayers: CSS.supports('@layer', 'base'),
                        
                        // CSS :has() selector
                        hasPseudoClass: CSS.supports('selector(:has(div))'),
                        
                        // CSS Color Level 4
                        colorLevel4: CSS.supports('color', 'oklch(0.7 0.15 180)'),
                        
                        // CSS Scroll Timeline
                        scrollTimeline: CSS.supports('animation-timeline', 'scroll()'),
                        
                        // CSS View Transitions
                        viewTransitions: typeof document.startViewTransition !== 'undefined'
                    },
                    
                    performanceFeatures: {
                        // Performance Observer
                        performanceObserver: typeof PerformanceObserver !== 'undefined',
                        
                        // User Timing Level 3
                        userTimingL3: typeof performance.mark !== 'undefined',
                        
                        // Navigation Timing Level 2
                        navigationTimingL2: typeof PerformanceNavigationTiming !== 'undefined',
                        
                        // Resource Timing Level 2
                        resourceTimingL2: typeof PerformanceResourceTiming !== 'undefined',
                        
                        // Paint Timing
                        paintTiming: typeof PerformancePaintTiming !== 'undefined',
                        
                        // Layout Instability API
                        layoutInstability: typeof LayoutShift !== 'undefined'
                    },
                    
                    securityFeatures: {
                        // Trusted Types
                        trustedTypes: typeof trustedTypes !== 'undefined',
                        
                        // Origin Trial
                        originTrial: typeof OriginTrialToken !== 'undefined',
                        
                        // Cross Origin Embedder Policy
                        crossOriginEmbedderPolicy: typeof crossOriginIsolated !== 'undefined',
                        
                        // Permissions Policy
                        permissionsPolicy: typeof document.permissionsPolicy !== 'undefined'
                    }
                };
                
                // Test Chromium-specific behavior
                const chromiumBehaviors = {
                    // V8 specific features
                    v8Features: {
                        hasV8: typeof window.chrome !== 'undefined',
                        errorStackTraceLimit: typeof Error.stackTraceLimit !== 'undefined',
                        v8Debug: typeof window.v8debug !== 'undefined'
                    },
                    
                    // Blink rendering engine specifics
                    blinkFeatures: {
                        webkitPrefixes: {
                            webkitRequestFullscreen: typeof Element.prototype.webkitRequestFullscreen !== 'undefined',
                            webkitExitFullscreen: typeof document.webkitExitFullscreen !== 'undefined',
                            webkitGetUserMedia: typeof navigator.webkitGetUserMedia !== 'undefined'
                        },
                        
                        blinkSpecific: {
                            webkitStorageInfo: typeof navigator.webkitTemporaryStorage !== 'undefined',
                            webkitRequestFileSystem: typeof window.webkitRequestFileSystem !== 'undefined'
                        }
                    }
                };
                
                return {
                    chromiumFeatures,
                    chromiumBehaviors,
                    testTimestamp: Date.now()
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify Chromium feature detection
        assert 'chromiumFeatures' in result
        assert 'chromiumBehaviors' in result
        
        features = result['chromiumFeatures']
        assert 'detection' in features
        assert 'apis' in features
        assert 'cssFeatures' in features
        
        # If this is actually Chromium, verify some expected features
        if features['detection']['isChromium']:
            apis = features['apis']
            
            # These APIs are commonly available in Chromium
            expected_apis = ['broadcastChannel', 'webStreams']
            for api in expected_apis:
                assert api in apis
            
            css_features = features['cssFeatures']
            assert 'containerQueries' in css_features
            assert 'hasPseudoClass' in css_features
    
    @pytest.mark.asyncio
    async def test_cross_engine_javascript_execution(self, base_url):
        """Test that the same JavaScript executes consistently across engines."""
        test_script = """
            // Cross-engine compatibility test script
            const compatibilityTest = {
                // Basic JavaScript features
                basicFeatures: {
                    variables: (() => { let x = 1; const y = 2; var z = 3; return x + y + z; })(),
                    functions: (() => { function test() { return 42; } return test(); })(),
                    arrays: [1, 2, 3].map(x => x * 2).filter(x => x > 2).reduce((a, b) => a + b, 0),
                    objects: (() => { const obj = { a: 1, b: 2 }; return obj.a + obj.b; })(),
                    loops: (() => { let sum = 0; for (let i = 0; i < 10; i++) { sum += i; } return sum; })()
                },
                
                // Modern JavaScript features
                modernFeatures: {
                    asyncAwait: (async () => { return await Promise.resolve(42); })(),
                    destructuring: (() => { const [a, b] = [1, 2]; const {x, y} = {x: 3, y: 4}; return a + b + x + y; })(),
                    templateLiterals: (() => { const name = 'test'; return `Hello ${name}!`; })(),
                    arrowFunctions: (() => { const fn = x => x * 2; return fn(21); })(),
                    spreadOperator: (() => { const arr1 = [1, 2]; const arr2 = [3, 4]; return [...arr1, ...arr2].length; })()
                },
                
                // DOM operations
                domOperations: (() => {
                    const div = document.createElement('div');
                    div.textContent = 'Test';
                    div.className = 'test-class';
                    div.style.display = 'none';
                    
                    document.body.appendChild(div);
                    const found = document.querySelector('.test-class');
                    const result = found !== null && found.textContent === 'Test';
                    
                    document.body.removeChild(div);
                    return result;
                })(),
                
                // Math operations
                mathOperations: {
                    basic: Math.sqrt(16) + Math.pow(2, 3),
                    trigonometry: Math.sin(Math.PI / 2) + Math.cos(0),
                    random: Math.random() > 0 && Math.random() < 1,
                    precision: 0.1 + 0.2 !== 0.3 // JavaScript precision quirk
                },
                
                // Date operations
                dateOperations: (() => {
                    const date = new Date('2023-01-01T00:00:00.000Z');
                    return {
                        year: date.getFullYear(),
                        month: date.getMonth(),
                        timestamp: date.getTime(),
                        iso: date.toISOString()
                    };
                })(),
                
                // JSON operations
                jsonOperations: (() => {
                    const obj = { a: 1, b: [2, 3], c: { d: 4 } };
                    const json = JSON.stringify(obj);
                    const parsed = JSON.parse(json);
                    return parsed.a === 1 && parsed.b.length === 2 && parsed.c.d === 4;
                })(),
                
                // Regular expressions
                regexOperations: (() => {
                    const regex = /test(\\d+)/i;
                    const match = 'Test123'.match(regex);
                    return match !== null && match[1] === '123';
                })(),
                
                // Type checking
                typeChecking: {
                    typeof_number: typeof 42 === 'number',
                    typeof_string: typeof 'test' === 'string',
                    typeof_boolean: typeof true === 'boolean',
                    typeof_object: typeof {} === 'object',
                    typeof_function: typeof (() => {}) === 'function',
                    typeof_undefined: typeof undefined === 'undefined',
                    instanceof_array: [] instanceof Array,
                    instanceof_date: new Date() instanceof Date
                }
            };
            
            // Wait for async operations to complete
            return Promise.all([
                compatibilityTest.modernFeatures.asyncAwait
            ]).then(([asyncResult]) => {
                compatibilityTest.modernFeatures.asyncAwait = asyncResult;
                return compatibilityTest;
            });
        """
        
        # Test with the default configuration
        content = await get(f"{base_url}/vue/", script=test_script)
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify all test categories completed
        expected_categories = ['basicFeatures', 'modernFeatures', 'domOperations', 'mathOperations', 'dateOperations', 'jsonOperations', 'regexOperations', 'typeChecking']
        
        for category in expected_categories:
            assert category in result, f"Missing category: {category}"
        
        # Verify basic features
        basic = result['basicFeatures']
        assert basic['variables'] == 6  # 1 + 2 + 3
        assert basic['functions'] == 42
        assert basic['arrays'] == 10  # [2, 4, 6] filtered to [4, 6] summed to 10
        assert basic['objects'] == 3   # 1 + 2
        assert basic['loops'] == 45     # sum of 0-9
        
        # Verify modern features
        modern = result['modernFeatures']
        assert modern['asyncAwait'] == 42
        assert modern['destructuring'] == 10  # 1 + 2 + 3 + 4
        assert modern['templateLiterals'] == 'Hello test!'
        assert modern['arrowFunctions'] == 42  # 21 * 2
        assert modern['spreadOperator'] == 4   # [1, 2, 3, 4].length
        
        # Verify DOM operations worked
        assert result['domOperations'] is True
        
        # Verify math operations
        math = result['mathOperations']
        assert math['basic'] == 12  # sqrt(16) + pow(2,3) = 4 + 8
        assert math['trigonometry'] == 2  # sin(π/2) + cos(0) = 1 + 1
        assert math['random'] is True
        assert math['precision'] is True  # JavaScript floating point quirk
        
        # Verify date operations
        date = result['dateOperations']
        assert date['year'] == 2023
        assert date['month'] == 0  # January is 0
        assert date['iso'] == '2023-01-01T00:00:00.000Z'
        
        # Verify JSON operations
        assert result['jsonOperations'] is True
        
        # Verify regex operations
        assert result['regexOperations'] is True
        
        # Verify type checking
        types = result['typeChecking']
        for check_name, check_result in types.items():
            assert check_result is True, f"Type check failed: {check_name}"


<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Complete Phase 2: Production Optimization", "status": "in_progress", "activeForm": "Completing Phase 2: Production Optimization"}, {"content": "Create comprehensive network resilience test suite", "status": "completed", "activeForm": "Creating comprehensive network resilience test suite"}, {"content": "Build platform-specific edge case tests", "status": "completed", "activeForm": "Building platform-specific edge case tests"}, {"content": "Implement performance under pressure test suite", "status": "completed", "activeForm": "Implementing performance under pressure test suite"}, {"content": "Create browser engine compatibility tests", "status": "completed", "activeForm": "Creating browser engine compatibility tests"}, {"content": "Build memory management and leak detection tests", "status": "in_progress", "activeForm": "Building memory management and leak detection tests"}, {"content": "Document cloud testing infrastructure requirements", "status": "completed", "activeForm": "Documenting cloud testing infrastructure requirements"}]