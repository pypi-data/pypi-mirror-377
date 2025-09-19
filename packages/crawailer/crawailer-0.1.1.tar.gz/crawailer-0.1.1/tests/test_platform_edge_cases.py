"""
Platform-specific edge case test suite.

Tests JavaScript execution across different operating systems, browser engines,
hardware configurations, and edge cases specific to Linux, Windows, macOS,
mobile platforms, and embedded environments.
"""
import pytest
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, patch
import json
import platform
import sys

from crawailer import get, get_many
from crawailer.browser import Browser
from crawailer.config import BrowserConfig


class TestPlatformEdgeCases:
    """Test platform-specific edge cases and browser behavior differences."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for local test server."""
        return "http://localhost:8083"
    
    @pytest.fixture
    def platform_info(self):
        """Current platform information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'architecture': platform.architecture()
        }

    # Operating System Specific Tests
    
    @pytest.mark.asyncio
    async def test_linux_specific_behaviors(self, base_url, platform_info):
        """Test Linux-specific browser behaviors and edge cases."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Detect Linux-specific features and behaviors
                const linuxFeatures = {
                    platform: navigator.platform,
                    userAgent: navigator.userAgent,
                    isLinux: navigator.platform.includes('Linux') || navigator.userAgent.includes('Linux'),
                    
                    // Linux-specific capabilities
                    hasWayland: false, // Can't directly detect, but we can test rendering
                    hasX11: false,     // Can't directly detect
                    
                    // Font rendering and display
                    fontRendering: {
                        hasSubpixelAntialiasing: CSS.supports('font-smooth', 'subpixel-antialiased'),
                        hasSystemFonts: CSS.supports('font-family', 'system-ui'),
                        canvasTextRendering: null
                    },
                    
                    // Hardware acceleration
                    hardwareAcceleration: {
                        hasWebGL: !!window.WebGLRenderingContext,
                        webglRenderer: null,
                        webglVendor: null,
                        canvas2dAccelerated: null
                    },
                    
                    // Memory and performance characteristics
                    memoryInfo: performance.memory ? {
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        usedJSHeapSize: performance.memory.usedJSHeapSize
                    } : null,
                    
                    // File system behaviors
                    fileSystem: {
                        caseSensitive: null, // Will test below
                        pathSeparator: '/', // Linux default
                        homeDirectory: null, // Can't access directly from browser
                        supportsSymlinks: null // Can't test directly
                    }
                };
                
                // Test WebGL capabilities
                if (linuxFeatures.hardwareAcceleration.hasWebGL) {
                    try {
                        const canvas = document.createElement('canvas');
                        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        if (gl) {
                            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                            if (debugInfo) {
                                linuxFeatures.hardwareAcceleration.webglRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                                linuxFeatures.hardwareAcceleration.webglVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                            }
                        }
                    } catch (error) {
                        linuxFeatures.hardwareAcceleration.webglError = error.message;
                    }
                }
                
                // Test canvas text rendering quality
                try {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = 200;
                    canvas.height = 50;
                    
                    // Test different text rendering modes
                    ctx.font = '16px Arial';
                    ctx.textBaseline = 'top';
                    
                    // Default rendering
                    ctx.fillText('Test Text Default', 10, 10);
                    
                    // With text rendering optimizations
                    ctx.textRenderingOptimization = 'optimizeLegibility';
                    ctx.fillText('Test Text Optimized', 10, 30);
                    
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const hasRenderedContent = Array.from(imageData.data).some(pixel => pixel !== 0);
                    
                    linuxFeatures.fontRendering.canvasTextRendering = {
                        success: hasRenderedContent,
                        canvasSupported: true
                    };
                } catch (error) {
                    linuxFeatures.fontRendering.canvasTextRendering = {
                        success: false,
                        error: error.message
                    };
                }
                
                // Test file case sensitivity (limited browser test)
                try {
                    // This is a very indirect test - testing URL case sensitivity
                    const testUrl1 = '/API/test';
                    const testUrl2 = '/api/test';
                    // Note: This doesn't actually test filesystem, just URL handling
                    linuxFeatures.fileSystem.urlCaseSensitive = testUrl1 !== testUrl2;
                } catch (error) {
                    linuxFeatures.fileSystem.caseSensitivityTestError = error.message;
                }
                
                // Test Linux-specific performance characteristics
                const performanceTest = {
                    startTime: performance.now(),
                    iterations: 10000,
                    results: []
                };
                
                // CPU-intensive operation
                for (let i = 0; i < performanceTest.iterations; i++) {
                    Math.sqrt(i);
                }
                
                performanceTest.endTime = performance.now();
                performanceTest.duration = performanceTest.endTime - performanceTest.startTime;
                performanceTest.operationsPerSecond = performanceTest.iterations / (performanceTest.duration / 1000);
                
                linuxFeatures.performanceCharacteristics = performanceTest;
                
                // Test process and thread information (limited in browser)
                linuxFeatures.processInfo = {
                    hardwareConcurrency: navigator.hardwareConcurrency,
                    maxTouchPoints: navigator.maxTouchPoints,
                    cookieEnabled: navigator.cookieEnabled,
                    onLine: navigator.onLine
                };
                
                return linuxFeatures;
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify Linux detection and features
        if platform_info['system'] == 'Linux':
            assert result['isLinux'] is True
            assert 'Linux' in result['userAgent'] or 'Linux' in result['platform']
        
        # Check hardware acceleration
        hw_accel = result['hardwareAcceleration']
        assert 'hasWebGL' in hw_accel
        
        # Check font rendering
        font_rendering = result['fontRendering']
        assert 'canvasTextRendering' in font_rendering
        
        # Check performance characteristics
        perf_test = result['performanceCharacteristics']
        assert perf_test['duration'] > 0
        assert perf_test['operationsPerSecond'] > 0
        
        # Check process info
        process_info = result['processInfo']
        assert 'hardwareConcurrency' in process_info
        assert process_info['hardwareConcurrency'] >= 1
    
    @pytest.mark.asyncio
    async def test_browser_engine_differences(self, base_url):
        """Test differences between browser engines (Chromium, Firefox, Safari)."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Detect browser engine and test engine-specific behaviors
                const engineDetection = {
                    userAgent: navigator.userAgent,
                    vendor: navigator.vendor,
                    
                    // Engine detection
                    isChromium: !!window.chrome || navigator.userAgent.includes('Chrome'),
                    isGecko: navigator.userAgent.includes('Gecko') && !navigator.userAgent.includes('Chrome'),
                    isWebKit: navigator.userAgent.includes('Safari') && !navigator.userAgent.includes('Chrome'),
                    isBlink: !!window.chrome, // Chromium uses Blink engine
                    
                    // Engine-specific features
                    engineFeatures: {},
                    
                    // API availability differences
                    apiSupport: {
                        webkitFeatures: {},
                        mozFeatures: {},
                        chromiumFeatures: {}
                    },
                    
                    // Performance characteristics by engine
                    performanceTests: {},
                    
                    // Rendering differences
                    renderingTests: {}
                };
                
                // Test Chromium/Blink specific features
                if (engineDetection.isChromium) {
                    engineDetection.engineFeatures.chromium = {
                        hasChrome: !!window.chrome,
                        hasChromeRuntime: !!(window.chrome && window.chrome.runtime),
                        hasWebkitRequestFileSystem: !!window.webkitRequestFileSystem,
                        hasWebkitStorageInfo: !!(navigator.webkitTemporaryStorage || navigator.webkitPersistentStorage),
                        chromeVersion: navigator.userAgent.match(/Chrome\/([\\d.]+)/)?.[1] || 'unknown'
                    };
                    
                    // Test Chromium-specific APIs
                    engineDetection.apiSupport.chromiumFeatures = {
                        fileSystemAccess: !!window.showOpenFilePicker,
                        webShare: !!navigator.share,
                        webSerial: !!navigator.serial,
                        webUSB: !!navigator.usb,
                        webBluetooth: !!navigator.bluetooth,
                        webNFC: !!window.NDEFReader,
                        webLocks: !!navigator.locks,
                        broadcastChannel: !!window.BroadcastChannel,
                        intersectionObserver: !!window.IntersectionObserver,
                        resizeObserver: !!window.ResizeObserver
                    };
                }
                
                // Test Gecko/Firefox specific features  
                if (engineDetection.isGecko) {
                    engineDetection.engineFeatures.gecko = {
                        hasMoz: typeof navigator.mozGetUserMedia !== 'undefined',
                        firefoxVersion: navigator.userAgent.match(/Firefox\/([\\d.]+)/)?.[1] || 'unknown',
                        mozInnerScreenX: typeof window.mozInnerScreenX !== 'undefined',
                        mozPaintCount: typeof window.mozPaintCount !== 'undefined'
                    };
                    
                    // Test Firefox-specific APIs
                    engineDetection.apiSupport.mozFeatures = {
                        mozGetUserMedia: !!navigator.mozGetUserMedia,
                        mozRequestFullScreen: !!document.documentElement.mozRequestFullScreen,
                        mozIndexedDB: !!window.mozIndexedDB,
                        mozRTCPeerConnection: !!window.mozRTCPeerConnection
                    };
                }
                
                // Test WebKit/Safari specific features
                if (engineDetection.isWebKit) {
                    engineDetection.engineFeatures.webkit = {
                        hasWebkit: navigator.userAgent.includes('WebKit'),
                        safariVersion: navigator.userAgent.match(/Version\/([\\d.]+)/)?.[1] || 'unknown',
                        webkitAppearance: CSS.supports('-webkit-appearance', 'none'),
                        webkitOverflowScrolling: CSS.supports('-webkit-overflow-scrolling', 'touch')
                    };
                    
                    // Test WebKit-specific APIs
                    engineDetection.apiSupport.webkitFeatures = {
                        webkitRequestFileSystem: !!window.webkitRequestFileSystem,
                        webkitSpeechRecognition: !!window.webkitSpeechRecognition,
                        webkitAudioContext: !!window.webkitAudioContext,
                        webkitGetUserMedia: !!navigator.webkitGetUserMedia,
                        webkitRequestAnimationFrame: !!window.webkitRequestAnimationFrame
                    };
                }
                
                // Test performance differences between engines
                const performanceTests = {
                    domManipulation: await testDOMPerformance(),
                    jsExecution: await testJSPerformance(),
                    canvasRendering: await testCanvasPerformance(),
                    memoryUsage: testMemoryUsage()
                };
                
                async function testDOMPerformance() {
                    const start = performance.now();
                    
                    // Create and manipulate DOM elements
                    const container = document.createElement('div');
                    for (let i = 0; i < 1000; i++) {
                        const element = document.createElement('div');
                        element.textContent = `Element ${i}`;
                        element.className = 'test-element';
                        container.appendChild(element);
                    }
                    
                    document.body.appendChild(container);
                    
                    // Query and modify elements
                    const elements = container.querySelectorAll('.test-element');
                    elements.forEach((el, index) => {
                        if (index % 2 === 0) {
                            el.style.backgroundColor = 'lightblue';
                        }
                    });
                    
                    const end = performance.now();
                    
                    // Cleanup
                    document.body.removeChild(container);
                    
                    return {
                        duration: end - start,
                        elementsCreated: 1000,
                        elementsPerSecond: 1000 / ((end - start) / 1000)
                    };
                }
                
                async function testJSPerformance() {
                    const start = performance.now();
                    
                    // CPU-intensive JavaScript operations
                    let result = 0;
                    for (let i = 0; i < 100000; i++) {
                        result += Math.sqrt(i) * Math.sin(i);
                    }
                    
                    const end = performance.now();
                    
                    return {
                        duration: end - start,
                        operations: 100000,
                        operationsPerSecond: 100000 / ((end - start) / 1000),
                        result: result
                    };
                }
                
                async function testCanvasPerformance() {
                    const start = performance.now();
                    
                    const canvas = document.createElement('canvas');
                    canvas.width = 500;
                    canvas.height = 500;
                    const ctx = canvas.getContext('2d');
                    
                    // Draw performance test
                    for (let i = 0; i < 1000; i++) {
                        ctx.beginPath();
                        ctx.arc(Math.random() * 500, Math.random() * 500, 10, 0, 2 * Math.PI);
                        ctx.fillStyle = `hsl(${i % 360}, 50%, 50%)`;
                        ctx.fill();
                    }
                    
                    const end = performance.now();
                    
                    return {
                        duration: end - start,
                        shapesDrawn: 1000,
                        shapesPerSecond: 1000 / ((end - start) / 1000),
                        canvasSize: '500x500'
                    };
                }
                
                function testMemoryUsage() {
                    if (performance.memory) {
                        return {
                            jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                            totalJSHeapSize: performance.memory.totalJSHeapSize,
                            usedJSHeapSize: performance.memory.usedJSHeapSize,
                            memoryPressure: performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit
                        };
                    }
                    return { available: false };
                }
                
                engineDetection.performanceTests = performanceTests;
                
                // Test CSS rendering differences
                const cssTests = {
                    flexboxSupport: CSS.supports('display', 'flex'),
                    gridSupport: CSS.supports('display', 'grid'),
                    customPropertiesSupport: CSS.supports('color', 'var(--test)'),
                    scrollSnapSupport: CSS.supports('scroll-snap-type', 'x mandatory'),
                    backdropFilterSupport: CSS.supports('backdrop-filter', 'blur(10px)'),
                    containerQueriesSupport: CSS.supports('container-type', 'inline-size')
                };
                
                engineDetection.cssSupport = cssTests;
                
                return engineDetection;
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify engine detection
        engines = ['isChromium', 'isGecko', 'isWebKit', 'isBlink']
        detected_engines = [engine for engine in engines if result.get(engine)]
        assert len(detected_engines) >= 1  # At least one engine should be detected
        
        # Check API support
        api_support = result['apiSupport']
        assert 'chromiumFeatures' in api_support
        assert 'mozFeatures' in api_support
        assert 'webkitFeatures' in api_support
        
        # Check performance tests
        perf_tests = result['performanceTests']
        assert 'domManipulation' in perf_tests
        assert 'jsExecution' in perf_tests
        assert 'canvasRendering' in perf_tests
        
        # Verify DOM performance
        dom_perf = perf_tests['domManipulation']
        assert dom_perf['duration'] > 0
        assert dom_perf['elementsCreated'] == 1000
        assert dom_perf['elementsPerSecond'] > 0
        
        # Verify JS performance
        js_perf = perf_tests['jsExecution']
        assert js_perf['duration'] > 0
        assert js_perf['operations'] == 100000
        assert js_perf['operationsPerSecond'] > 0
        
        # Verify canvas performance
        canvas_perf = perf_tests['canvasRendering']
        assert canvas_perf['duration'] > 0
        assert canvas_perf['shapesDrawn'] == 1000
        assert canvas_perf['shapesPerSecond'] > 0
        
        # Check CSS support
        css_support = result['cssSupport']
        assert css_support['flexboxSupport'] is True  # Modern browsers should support flexbox
        assert css_support['gridSupport'] is True     # Modern browsers should support grid
    
    @pytest.mark.asyncio
    async def test_hardware_acceleration_edge_cases(self, base_url):
        """Test hardware acceleration edge cases and GPU-related issues."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                // Test hardware acceleration and GPU-related edge cases
                const hardwareTests = {
                    webglSupport: {
                        webgl1: false,
                        webgl2: false,
                        extensions: [],
                        rendererInfo: null,
                        limits: {}
                    },
                    
                    canvasAcceleration: {
                        canvas2d: null,
                        offscreenCanvas: !!window.OffscreenCanvas,
                        transferableObjects: false
                    },
                    
                    gpuInfo: {
                        vendor: null,
                        renderer: null,
                        maxTextureSize: null,
                        maxViewportDims: null
                    },
                    
                    performanceTests: {
                        hardwareAccelerated: null,
                        softwareRendered: null,
                        comparison: null
                    },
                    
                    memoryTests: {
                        textureMemory: null,
                        bufferMemory: null,
                        vertexArrays: null
                    }
                };
                
                // Test WebGL 1.0 support
                try {
                    const canvas1 = document.createElement('canvas');
                    const gl1 = canvas1.getContext('webgl') || canvas1.getContext('experimental-webgl');
                    
                    if (gl1) {
                        hardwareTests.webglSupport.webgl1 = true;
                        
                        // Get available extensions
                        hardwareTests.webglSupport.extensions = gl1.getSupportedExtensions() || [];
                        
                        // Get renderer info if available
                        const debugInfo = gl1.getExtension('WEBGL_debug_renderer_info');
                        if (debugInfo) {
                            hardwareTests.gpuInfo.vendor = gl1.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                            hardwareTests.gpuInfo.renderer = gl1.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                        }
                        
                        // Get WebGL limits
                        hardwareTests.webglSupport.limits = {
                            maxTextureSize: gl1.getParameter(gl1.MAX_TEXTURE_SIZE),
                            maxViewportDims: gl1.getParameter(gl1.MAX_VIEWPORT_DIMS),
                            maxVertexAttribs: gl1.getParameter(gl1.MAX_VERTEX_ATTRIBS),
                            maxTextureImageUnits: gl1.getParameter(gl1.MAX_TEXTURE_IMAGE_UNITS),
                            maxFragmentUniformVectors: gl1.getParameter(gl1.MAX_FRAGMENT_UNIFORM_VECTORS),
                            maxVertexUniformVectors: gl1.getParameter(gl1.MAX_VERTEX_UNIFORM_VECTORS)
                        };
                        
                        // Store GPU info
                        hardwareTests.gpuInfo.maxTextureSize = hardwareTests.webglSupport.limits.maxTextureSize;
                        hardwareTests.gpuInfo.maxViewportDims = hardwareTests.webglSupport.limits.maxViewportDims;
                        
                        // Test texture creation and memory usage
                        const testTextureMemory = () => {
                            try {
                                const texture = gl1.createTexture();
                                gl1.bindTexture(gl1.TEXTURE_2D, texture);
                                
                                // Create a moderately sized texture to test memory
                                const size = Math.min(1024, hardwareTests.webglSupport.limits.maxTextureSize / 4);
                                const data = new Uint8Array(size * size * 4); // RGBA
                                
                                gl1.texImage2D(gl1.TEXTURE_2D, 0, gl1.RGBA, size, size, 0, gl1.RGBA, gl1.UNSIGNED_BYTE, data);
                                
                                const error = gl1.getError();
                                gl1.deleteTexture(texture);
                                
                                return {
                                    success: error === gl1.NO_ERROR,
                                    textureSize: size,
                                    memoryUsed: size * size * 4,
                                    error: error !== gl1.NO_ERROR ? error : null
                                };
                            } catch (e) {
                                return { success: false, error: e.message };
                            }
                        };
                        
                        hardwareTests.memoryTests.textureMemory = testTextureMemory();
                        
                        // Test buffer creation
                        const testBufferMemory = () => {
                            try {
                                const buffer = gl1.createBuffer();
                                gl1.bindBuffer(gl1.ARRAY_BUFFER, buffer);
                                
                                const bufferData = new Float32Array(10000); // 40KB buffer
                                gl1.bufferData(gl1.ARRAY_BUFFER, bufferData, gl1.STATIC_DRAW);
                                
                                const error = gl1.getError();
                                gl1.deleteBuffer(buffer);
                                
                                return {
                                    success: error === gl1.NO_ERROR,
                                    bufferSize: bufferData.byteLength,
                                    error: error !== gl1.NO_ERROR ? error : null
                                };
                            } catch (e) {
                                return { success: false, error: e.message };
                            }
                        };
                        
                        hardwareTests.memoryTests.bufferMemory = testBufferMemory();
                    }
                } catch (error) {
                    hardwareTests.webglSupport.webgl1Error = error.message;
                }
                
                // Test WebGL 2.0 support
                try {
                    const canvas2 = document.createElement('canvas');
                    const gl2 = canvas2.getContext('webgl2');
                    
                    if (gl2) {
                        hardwareTests.webglSupport.webgl2 = true;
                        
                        // Test WebGL 2.0 specific features
                        hardwareTests.webglSupport.webgl2Features = {
                            maxDrawBuffers: gl2.getParameter(gl2.MAX_DRAW_BUFFERS),
                            maxColorAttachments: gl2.getParameter(gl2.MAX_COLOR_ATTACHMENTS),
                            maxSamples: gl2.getParameter(gl2.MAX_SAMPLES),
                            maxTransformFeedbackInterleavedComponents: gl2.getParameter(gl2.MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS)
                        };
                        
                        // Test vertex array objects
                        const testVertexArrays = () => {
                            try {
                                const vao = gl2.createVertexArray();
                                gl2.bindVertexArray(vao);
                                
                                const buffer = gl2.createBuffer();
                                gl2.bindBuffer(gl2.ARRAY_BUFFER, buffer);
                                
                                const vertices = new Float32Array([0, 0, 1, 0, 0.5, 1]);
                                gl2.bufferData(gl2.ARRAY_BUFFER, vertices, gl2.STATIC_DRAW);
                                
                                gl2.enableVertexAttribArray(0);
                                gl2.vertexAttribPointer(0, 2, gl2.FLOAT, false, 0, 0);
                                
                                gl2.bindVertexArray(null);
                                gl2.deleteVertexArray(vao);
                                gl2.deleteBuffer(buffer);
                                
                                const error = gl2.getError();
                                
                                return {
                                    success: error === gl2.NO_ERROR,
                                    error: error !== gl2.NO_ERROR ? error : null
                                };
                            } catch (e) {
                                return { success: false, error: e.message };
                            }
                        };
                        
                        hardwareTests.memoryTests.vertexArrays = testVertexArrays();
                    }
                } catch (error) {
                    hardwareTests.webglSupport.webgl2Error = error.message;
                }
                
                // Test Canvas 2D hardware acceleration
                const testCanvas2DAcceleration = () => {
                    try {
                        const canvas = document.createElement('canvas');
                        canvas.width = 500;
                        canvas.height = 500;
                        const ctx = canvas.getContext('2d');
                        
                        // Test if context is hardware accelerated (indirect test)
                        const start = performance.now();
                        
                        // Draw complex graphics that benefit from hardware acceleration
                        for (let i = 0; i < 1000; i++) {
                            ctx.save();
                            ctx.translate(250, 250);
                            ctx.rotate(i * 0.1);
                            ctx.scale(1 + Math.sin(i * 0.1) * 0.1, 1 + Math.cos(i * 0.1) * 0.1);
                            
                            const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, 50);
                            gradient.addColorStop(0, `hsl(${i % 360}, 70%, 50%)`);
                            gradient.addColorStop(1, `hsl(${(i + 180) % 360}, 70%, 30%)`);
                            
                            ctx.fillStyle = gradient;
                            ctx.fillRect(-25, -25, 50, 50);
                            
                            ctx.restore();
                        }
                        
                        const end = performance.now();
                        
                        return {
                            renderTime: end - start,
                            operationsPerSecond: 1000 / ((end - start) / 1000),
                            likelyHardwareAccelerated: (end - start) < 100 // Heuristic
                        };
                    } catch (error) {
                        return { success: false, error: error.message };
                    }
                };
                
                hardwareTests.canvasAcceleration.canvas2d = testCanvas2DAcceleration();
                
                // Test OffscreenCanvas and transferable objects
                if (hardwareTests.canvasAcceleration.offscreenCanvas) {
                    try {
                        const offscreen = new OffscreenCanvas(256, 256);
                        const ctx = offscreen.getContext('2d');
                        
                        if (ctx) {
                            ctx.fillStyle = 'red';
                            ctx.fillRect(0, 0, 256, 256);
                            
                            hardwareTests.canvasAcceleration.transferableObjects = typeof offscreen.transferControlToOffscreen === 'function';
                        }
                    } catch (error) {
                        hardwareTests.canvasAcceleration.offscreenError = error.message;
                    }
                }
                
                // Performance comparison test
                const performanceComparison = async () => {
                    const results = {
                        webglTest: null,
                        canvas2dTest: null,
                        comparison: null
                    };
                    
                    // WebGL performance test
                    if (hardwareTests.webglSupport.webgl1) {
                        const canvas = document.createElement('canvas');
                        canvas.width = 500;
                        canvas.height = 500;
                        const gl = canvas.getContext('webgl');
                        
                        if (gl) {
                            const start = performance.now();
                            
                            // Simple WebGL rendering test
                            gl.clearColor(0.0, 0.0, 0.0, 1.0);
                            gl.clear(gl.COLOR_BUFFER_BIT);
                            
                            // Create and use a simple shader program would go here
                            // For this test, we'll just do multiple clear operations
                            for (let i = 0; i < 1000; i++) {
                                gl.clearColor(Math.random(), Math.random(), Math.random(), 1.0);
                                gl.clear(gl.COLOR_BUFFER_BIT);
                            }
                            
                            const end = performance.now();
                            
                            results.webglTest = {
                                duration: end - start,
                                operationsPerSecond: 1000 / ((end - start) / 1000)
                            };
                        }
                    }
                    
                    // Canvas 2D performance test
                    const canvas2d = document.createElement('canvas');
                    canvas2d.width = 500;
                    canvas2d.height = 500;
                    const ctx2d = canvas2d.getContext('2d');
                    
                    const start2d = performance.now();
                    
                    for (let i = 0; i < 1000; i++) {
                        ctx2d.fillStyle = `hsl(${i % 360}, 50%, 50%)`;
                        ctx2d.fillRect(0, 0, 500, 500);
                    }
                    
                    const end2d = performance.now();
                    
                    results.canvas2dTest = {
                        duration: end2d - start2d,
                        operationsPerSecond: 1000 / ((end2d - start2d) / 1000)
                    };
                    
                    // Compare performance
                    if (results.webglTest && results.canvas2dTest) {
                        results.comparison = {
                            webglFaster: results.webglTest.operationsPerSecond > results.canvas2dTest.operationsPerSecond,
                            speedRatio: results.webglTest.operationsPerSecond / results.canvas2dTest.operationsPerSecond,
                            webglAdvantage: results.webglTest.operationsPerSecond - results.canvas2dTest.operationsPerSecond
                        };
                    }
                    
                    return results;
                };
                
                hardwareTests.performanceTests = await performanceComparison();
                
                return hardwareTests;
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify WebGL support testing
        webgl_support = result['webglSupport']
        assert 'webgl1' in webgl_support
        assert 'webgl2' in webgl_support
        
        if webgl_support['webgl1']:
            assert 'limits' in webgl_support
            limits = webgl_support['limits']
            assert 'maxTextureSize' in limits
            assert limits['maxTextureSize'] > 0
            
            # Check memory tests
            memory_tests = result['memoryTests']
            if memory_tests['textureMemory']:
                assert 'success' in memory_tests['textureMemory']
            if memory_tests['bufferMemory']:
                assert 'success' in memory_tests['bufferMemory']
        
        # Verify Canvas 2D acceleration testing
        canvas_accel = result['canvasAcceleration']
        assert 'canvas2d' in canvas_accel
        
        if canvas_accel['canvas2d'] and 'renderTime' in canvas_accel['canvas2d']:
            canvas2d_test = canvas_accel['canvas2d']
            assert canvas2d_test['renderTime'] > 0
            assert canvas2d_test['operationsPerSecond'] > 0
        
        # Check performance tests
        perf_tests = result['performanceTests']
        if perf_tests and perf_tests['canvas2dTest']:
            canvas2d_perf = perf_tests['canvas2dTest']
            assert canvas2d_perf['duration'] > 0
            assert canvas2d_perf['operationsPerSecond'] > 0

    # Memory and Resource Management Edge Cases
    
    @pytest.mark.asyncio
    async def test_memory_pressure_scenarios(self, base_url):
        """Test behavior under various memory pressure scenarios."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Test memory pressure scenarios and garbage collection
                class MemoryPressureTester {
                    constructor() {
                        this.memorySnapshots = [];
                        this.testResults = {};
                        this.originalMemory = this.getMemoryInfo();
                    }
                    
                    getMemoryInfo() {
                        if (performance.memory) {
                            return {
                                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                                totalJSHeapSize: performance.memory.totalJSHeapSize,
                                usedJSHeapSize: performance.memory.usedJSHeapSize,
                                timestamp: Date.now()
                            };
                        }
                        return {
                            jsHeapSizeLimit: null,
                            totalJSHeapSize: null,
                            usedJSHeapSize: null,
                            timestamp: Date.now(),
                            unavailable: true
                        };
                    }
                    
                    takeMemorySnapshot(label) {
                        const snapshot = {
                            label,
                            ...this.getMemoryInfo()
                        };
                        this.memorySnapshots.push(snapshot);
                        return snapshot;
                    }
                    
                    async testGradualMemoryIncrease() {
                        const testData = [];
                        const phases = [
                            { name: 'baseline', allocations: 0 },
                            { name: 'small_load', allocations: 1000 },
                            { name: 'medium_load', allocations: 10000 },
                            { name: 'large_load', allocations: 100000 }
                        ];
                        
                        for (const phase of phases) {
                            this.takeMemorySnapshot(`start_${phase.name}`);
                            
                            // Allocate memory gradually
                            const allocatedData = [];
                            for (let i = 0; i < phase.allocations; i++) {
                                allocatedData.push({
                                    id: i,
                                    data: new Array(100).fill(Math.random()),
                                    metadata: {
                                        created: Date.now(),
                                        type: 'test_data',
                                        phase: phase.name
                                    }
                                });
                                
                                // Yield occasionally to prevent blocking
                                if (i % 1000 === 0) {
                                    await new Promise(resolve => setTimeout(resolve, 1));
                                }
                            }
                            
                            const endSnapshot = this.takeMemorySnapshot(`end_${phase.name}`);
                            
                            testData.push({
                                phase: phase.name,
                                allocations: phase.allocations,
                                dataSize: allocatedData.length,
                                memorySnapshot: endSnapshot
                            });
                            
                            // Clean up some data but not all (simulate memory leaks)
                            if (Math.random() > 0.3) { // 70% chance to clean up
                                allocatedData.length = Math.floor(allocatedData.length * 0.7);
                            }
                            
                            // Wait a bit between phases
                            await new Promise(resolve => setTimeout(resolve, 100));
                        }
                        
                        return testData;
                    }
                    
                    async testMemoryFragmentation() {
                        this.takeMemorySnapshot('fragmentation_start');
                        
                        const fragmentationTest = {
                            allocations: [],
                            deallocations: 0,
                            reallocations: 0
                        };
                        
                        // Create lots of small allocations
                        for (let i = 0; i < 5000; i++) {
                            const allocation = {
                                id: i,
                                smallData: new Array(Math.floor(Math.random() * 50) + 10).fill(i),
                                timestamp: Date.now()
                            };
                            fragmentationTest.allocations.push(allocation);
                        }
                        
                        this.takeMemorySnapshot('fragmentation_allocated');
                        
                        // Randomly deallocate some objects (simulate fragmentation)
                        for (let i = 0; i < 2000; i++) {
                            const randomIndex = Math.floor(Math.random() * fragmentationTest.allocations.length);
                            if (fragmentationTest.allocations[randomIndex]) {
                                delete fragmentationTest.allocations[randomIndex];
                                fragmentationTest.deallocations++;
                            }
                        }
                        
                        this.takeMemorySnapshot('fragmentation_deallocated');
                        
                        // Reallocate in the gaps
                        for (let i = 0; i < 1000; i++) {
                            const allocation = {
                                id: 'realloc_' + i,
                                reallocData: new Array(Math.floor(Math.random() * 100) + 20).fill('realloc'),
                                timestamp: Date.now()
                            };
                            fragmentationTest.allocations.push(allocation);
                            fragmentationTest.reallocations++;
                        }
                        
                        this.takeMemorySnapshot('fragmentation_reallocated');
                        
                        return fragmentationTest;
                    }
                    
                    async testMemoryLeakSimulation() {
                        this.takeMemorySnapshot('leak_test_start');
                        
                        const leakTest = {
                            intentionalLeaks: [],
                            eventListeners: [],
                            intervals: [],
                            circularReferences: []
                        };
                        
                        // Simulate memory leaks
                        
                        // 1. Intentional data retention
                        for (let i = 0; i < 1000; i++) {
                            const leakyData = {
                                id: i,
                                largeData: new Array(1000).fill(Math.random()),
                                references: []
                            };
                            
                            // Keep reference (simulating leak)
                            leakTest.intentionalLeaks.push(leakyData);
                        }
                        
                        this.takeMemorySnapshot('leak_data_accumulated');
                        
                        // 2. Event listener leaks
                        for (let i = 0; i < 100; i++) {
                            const element = document.createElement('div');
                            const handler = () => console.log('Leaked handler');
                            element.addEventListener('click', handler);
                            
                            // Don't remove listener (simulating leak)
                            leakTest.eventListeners.push({ element, handler });
                        }
                        
                        // 3. Timer leaks
                        for (let i = 0; i < 10; i++) {
                            const intervalId = setInterval(() => {
                                // Do some work that references external data
                                leakTest.intentionalLeaks.forEach(data => data.accessCount = (data.accessCount || 0) + 1);
                            }, 100);
                            
                            leakTest.intervals.push(intervalId);
                        }
                        
                        // 4. Circular references
                        for (let i = 0; i < 500; i++) {
                            const obj1 = { id: i, type: 'obj1' };
                            const obj2 = { id: i, type: 'obj2' };
                            
                            obj1.reference = obj2;
                            obj2.reference = obj1;
                            
                            leakTest.circularReferences.push(obj1, obj2);
                        }
                        
                        this.takeMemorySnapshot('leak_test_end');
                        
                        // Cleanup some leaks (but not all)
                        leakTest.intervals.forEach(id => clearInterval(id));
                        leakTest.intervals = [];
                        
                        return leakTest;
                    }
                    
                    async testLowMemoryRecovery() {
                        this.takeMemorySnapshot('recovery_test_start');
                        
                        const recoveryTest = {
                            preCleanupMemory: null,
                            postCleanupMemory: null,
                            cleanupActions: [],
                            recoverySuccess: false
                        };
                        
                        // Create memory pressure
                        const pressureData = [];
                        for (let i = 0; i < 50000; i++) {
                            pressureData.push({
                                id: i,
                                data: new Array(200).fill(Math.random()),
                                timestamp: Date.now()
                            });
                        }
                        
                        recoveryTest.preCleanupMemory = this.takeMemorySnapshot('pre_cleanup');
                        
                        // Simulate cleanup actions
                        const cleanupActions = [
                            () => {
                                // Clear large arrays
                                pressureData.length = Math.floor(pressureData.length * 0.5);
                                return 'cleared_half_pressure_data';
                            },
                            () => {
                                // Remove unused event listeners
                                const elements = document.querySelectorAll('.temporary-element');
                                elements.forEach(el => el.remove());
                                return `removed_${elements.length}_elements`;
                            },
                            () => {
                                // Clear caches
                                if (window.testCache) {
                                    window.testCache.clear();
                                }
                                return 'cleared_test_cache';
                            },
                            () => {
                                // Force garbage collection hint
                                if (window.gc) {
                                    window.gc();
                                    return 'forced_gc';
                                }
                                return 'gc_not_available';
                            }
                        ];
                        
                        for (const action of cleanupActions) {
                            try {
                                const result = action();
                                recoveryTest.cleanupActions.push(result);
                                await new Promise(resolve => setTimeout(resolve, 50));
                            } catch (error) {
                                recoveryTest.cleanupActions.push(`error: ${error.message}`);
                            }
                        }
                        
                        recoveryTest.postCleanupMemory = this.takeMemorySnapshot('post_cleanup');
                        
                        // Check if recovery was successful
                        if (recoveryTest.preCleanupMemory.usedJSHeapSize && recoveryTest.postCleanupMemory.usedJSHeapSize) {
                            const memoryReduced = recoveryTest.preCleanupMemory.usedJSHeapSize > recoveryTest.postCleanupMemory.usedJSHeapSize;
                            const reductionAmount = recoveryTest.preCleanupMemory.usedJSHeapSize - recoveryTest.postCleanupMemory.usedJSHeapSize;
                            
                            recoveryTest.recoverySuccess = memoryReduced && reductionAmount > 0;
                            recoveryTest.memoryReduced = reductionAmount;
                            recoveryTest.reductionPercentage = (reductionAmount / recoveryTest.preCleanupMemory.usedJSHeapSize) * 100;
                        }
                        
                        return recoveryTest;
                    }
                    
                    async runAllTests() {
                        const results = {
                            startTime: Date.now(),
                            originalMemory: this.originalMemory,
                            tests: {}
                        };
                        
                        try {
                            results.tests.gradualIncrease = await this.testGradualMemoryIncrease();
                            results.tests.fragmentation = await this.testMemoryFragmentation();
                            results.tests.leakSimulation = await this.testMemoryLeakSimulation();
                            results.tests.lowMemoryRecovery = await this.testLowMemoryRecovery();
                        } catch (error) {
                            results.error = error.message;
                        }
                        
                        results.endTime = Date.now();
                        results.totalDuration = results.endTime - results.startTime;
                        results.finalMemory = this.getMemoryInfo();
                        results.memorySnapshots = this.memorySnapshots;
                        
                        return results;
                    }
                }
                
                const memoryTester = new MemoryPressureTester();
                return await memoryTester.runAllTests();
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify memory pressure testing
        assert 'originalMemory' in result
        assert 'tests' in result
        assert 'finalMemory' in result
        assert 'memorySnapshots' in result
        
        # Check individual tests
        tests = result['tests']
        
        # Verify gradual memory increase test
        if 'gradualIncrease' in tests:
            gradual_test = tests['gradualIncrease']
            assert len(gradual_test) >= 4  # Should have tested 4 phases
            
            for phase in gradual_test:
                assert 'phase' in phase
                assert 'allocations' in phase
                assert 'memorySnapshot' in phase
        
        # Verify fragmentation test
        if 'fragmentation' in tests:
            frag_test = tests['fragmentation']
            assert 'allocations' in frag_test
            assert 'deallocations' in frag_test
            assert 'reallocations' in frag_test
            assert frag_test['deallocations'] > 0
            assert frag_test['reallocations'] > 0
        
        # Verify leak simulation test
        if 'leakSimulation' in tests:
            leak_test = tests['leakSimulation']
            assert 'intentionalLeaks' in leak_test
            assert 'eventListeners' in leak_test
            assert 'intervals' in leak_test
            assert 'circularReferences' in leak_test
        
        # Verify low memory recovery test
        if 'lowMemoryRecovery' in tests:
            recovery_test = tests['lowMemoryRecovery']
            assert 'preCleanupMemory' in recovery_test
            assert 'postCleanupMemory' in recovery_test
            assert 'cleanupActions' in recovery_test
            assert len(recovery_test['cleanupActions']) > 0
        
        # Check memory snapshots were taken
        snapshots = result['memorySnapshots']
        assert len(snapshots) > 0
        
        for snapshot in snapshots:
            assert 'label' in snapshot
            assert 'timestamp' in snapshot


class TestConcurrencyEdgeCases:
    """Test concurrency and threading edge cases."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8083"
    
    @pytest.mark.asyncio
    async def test_web_worker_edge_cases(self, base_url):
        """Test Web Worker edge cases and limitations."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Test Web Worker functionality and edge cases
                const workerTests = {
                    support: {
                        webWorkers: typeof Worker !== 'undefined',
                        sharedWorkers: typeof SharedWorker !== 'undefined',
                        serviceWorkers: typeof navigator.serviceWorker !== 'undefined'
                    },
                    
                    tests: {},
                    errors: []
                };
                
                if (workerTests.support.webWorkers) {
                    try {
                        // Test basic Web Worker creation
                        const workerCode = `
                            self.onmessage = function(e) {
                                const { type, data } = e.data;
                                
                                switch (type) {
                                    case 'cpu_intensive':
                                        let result = 0;
                                        for (let i = 0; i < data.iterations; i++) {
                                            result += Math.sqrt(i);
                                        }
                                        self.postMessage({ type: 'cpu_result', result, iterations: data.iterations });
                                        break;
                                        
                                    case 'memory_test':
                                        const memoryData = new Array(data.size).fill(Math.random());
                                        self.postMessage({ type: 'memory_result', size: memoryData.length });
                                        break;
                                        
                                    case 'error_test':
                                        throw new Error('Intentional worker error');
                                        
                                    default:
                                        self.postMessage({ type: 'unknown', original: e.data });
                                }
                            };
                        `;
                        
                        const blob = new Blob([workerCode], { type: 'application/javascript' });
                        const workerUrl = URL.createObjectURL(blob);
                        
                        const testWorker = async (testType, testData) => {
                            return new Promise((resolve, reject) => {
                                const worker = new Worker(workerUrl);
                                const timeout = setTimeout(() => {
                                    worker.terminate();
                                    reject(new Error('Worker timeout'));
                                }, 5000);
                                
                                worker.onmessage = (e) => {
                                    clearTimeout(timeout);
                                    worker.terminate();
                                    resolve(e.data);
                                };
                                
                                worker.onerror = (error) => {
                                    clearTimeout(timeout);
                                    worker.terminate();
                                    reject(error);
                                };
                                
                                worker.postMessage({ type: testType, data: testData });
                            });
                        };
                        
                        // Test CPU-intensive work
                        const cpuTest = await testWorker('cpu_intensive', { iterations: 100000 });
                        workerTests.tests.cpuIntensive = {
                            success: true,
                            result: cpuTest
                        };
                        
                        // Test memory allocation
                        const memoryTest = await testWorker('memory_test', { size: 10000 });
                        workerTests.tests.memoryAllocation = {
                            success: true,
                            result: memoryTest
                        };
                        
                        // Test error handling
                        try {
                            await testWorker('error_test', {});
                        } catch (error) {
                            workerTests.tests.errorHandling = {
                                success: true,
                                errorCaught: true,
                                errorMessage: error.message || 'Worker error caught'
                            };
                        }
                        
                        // Clean up
                        URL.revokeObjectURL(workerUrl);
                        
                    } catch (error) {
                        workerTests.errors.push(`Web Worker test failed: ${error.message}`);
                    }
                }
                
                // Test SharedWorker if supported
                if (workerTests.support.sharedWorkers) {
                    try {
                        const sharedWorkerCode = `
                            const connections = [];
                            
                            self.onconnect = function(e) {
                                const port = e.ports[0];
                                connections.push(port);
                                
                                port.onmessage = function(event) {
                                    const { type, data } = event.data;
                                    
                                    if (type === 'broadcast') {
                                        connections.forEach(p => {
                                            if (p !== port) {
                                                p.postMessage({ type: 'broadcast_received', data });
                                            }
                                        });
                                    }
                                    
                                    port.postMessage({ type: 'shared_response', original: event.data });
                                };
                                
                                port.start();
                            };
                        `;
                        
                        const sharedBlob = new Blob([sharedWorkerCode], { type: 'application/javascript' });
                        const sharedWorkerUrl = URL.createObjectURL(sharedBlob);
                        
                        const sharedWorker = new SharedWorker(sharedWorkerUrl);
                        
                        const sharedWorkerTest = new Promise((resolve, reject) => {
                            const timeout = setTimeout(() => {
                                reject(new Error('SharedWorker timeout'));
                            }, 3000);
                            
                            sharedWorker.port.onmessage = (e) => {
                                clearTimeout(timeout);
                                resolve(e.data);
                            };
                            
                            sharedWorker.port.onerror = (error) => {
                                clearTimeout(timeout);
                                reject(error);
                            };
                            
                            sharedWorker.port.start();
                            sharedWorker.port.postMessage({ type: 'test', data: 'shared worker test' });
                        });
                        
                        const sharedResult = await sharedWorkerTest;
                        workerTests.tests.sharedWorker = {
                            success: true,
                            result: sharedResult
                        };
                        
                        URL.revokeObjectURL(sharedWorkerUrl);
                        
                    } catch (error) {
                        workerTests.errors.push(`SharedWorker test failed: ${error.message}`);
                    }
                }
                
                return workerTests;
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify Web Worker support detection
        support = result['support']
        assert 'webWorkers' in support
        assert 'sharedWorkers' in support
        assert 'serviceWorkers' in support
        
        # If Web Workers are supported, verify tests
        if support['webWorkers']:
            tests = result['tests']
            
            if 'cpuIntensive' in tests:
                cpu_test = tests['cpuIntensive']
                assert cpu_test['success'] is True
                assert 'result' in cpu_test
            
            if 'memoryAllocation' in tests:
                memory_test = tests['memoryAllocation']
                assert memory_test['success'] is True
                assert 'result' in memory_test
            
            if 'errorHandling' in tests:
                error_test = tests['errorHandling']
                assert error_test['success'] is True
                assert error_test['errorCaught'] is True


<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Implement Phase 2: Production Optimization", "status": "in_progress", "activeForm": "Implementing Phase 2: Production Optimization"}, {"content": "Create comprehensive network resilience test suite", "status": "completed", "activeForm": "Creating comprehensive network resilience test suite"}, {"content": "Build platform-specific edge case tests", "status": "completed", "activeForm": "Building platform-specific edge case tests"}, {"content": "Implement performance under pressure test suite", "status": "in_progress", "activeForm": "Implementing performance under pressure test suite"}, {"content": "Create browser engine compatibility tests", "status": "pending", "activeForm": "Creating browser engine compatibility tests"}, {"content": "Build memory management and leak detection tests", "status": "pending", "activeForm": "Building memory management and leak detection tests"}]