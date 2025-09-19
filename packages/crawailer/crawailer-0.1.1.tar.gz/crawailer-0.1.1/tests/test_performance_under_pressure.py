"""
Performance under pressure test suite.

Tests JavaScript execution performance under extreme conditions including
high CPU load, memory pressure, concurrent operations, resource exhaustion,
and stress testing scenarios that simulate production peak loads.
"""
import pytest
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, patch
import time

from crawailer import get, get_many
from crawailer.browser import Browser
from crawailer.config import BrowserConfig


class TestPerformanceUnderPressure:
    """Test JavaScript execution performance under extreme conditions."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for local test server."""
        return "http://localhost:8083"
    
    @pytest.fixture
    def stress_config(self):
        """Browser configuration for stress testing."""
        return BrowserConfig(
            headless=True,
            viewport={'width': 1920, 'height': 1080},
            timeout=120000,  # 2 minute timeout for stress tests
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

    # High CPU Load Scenarios
    
    @pytest.mark.asyncio 
    async def test_extreme_cpu_load_scenarios(self, base_url):
        """Test JavaScript execution under extreme CPU load conditions."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Extreme CPU load testing
                class CPUStressTester {
                    constructor() {
                        this.testResults = {};
                        this.performanceBaseline = null;
                        this.stressTestResults = [];
                    }
                    
                    async establishBaseline() {
                        // Establish performance baseline under normal conditions
                        const baselineTests = {
                            simpleArithmetic: this.testSimpleArithmetic(1000),
                            arrayOperations: this.testArrayOperations(1000),
                            objectManipulation: this.testObjectManipulation(1000),
                            domOperations: this.testDOMOperations(100)
                        };
                        
                        const baseline = {};
                        for (const [testName, testPromise] of Object.entries(baselineTests)) {
                            baseline[testName] = await testPromise;
                        }
                        
                        this.performanceBaseline = baseline;
                        return baseline;
                    }
                    
                    async testSimpleArithmetic(iterations) {
                        const start = performance.now();
                        let result = 0;
                        
                        for (let i = 0; i < iterations; i++) {
                            result += Math.sqrt(i) * Math.sin(i) + Math.cos(i * 2);
                        }
                        
                        const end = performance.now();
                        
                        return {
                            duration: end - start,
                            iterations,
                            operationsPerSecond: iterations / ((end - start) / 1000),
                            result: result % 1000000 // Prevent overflow display issues
                        };
                    }
                    
                    async testArrayOperations(size) {
                        const start = performance.now();
                        
                        // Create large array
                        const array = new Array(size).fill(0).map((_, i) => ({
                            id: i,
                            value: Math.random(),
                            computed: Math.sqrt(i)
                        }));
                        
                        // Perform various array operations
                        const filtered = array.filter(item => item.value > 0.5);
                        const mapped = array.map(item => ({ ...item, doubled: item.value * 2 }));
                        const reduced = array.reduce((sum, item) => sum + item.value, 0);
                        const sorted = [...array].sort((a, b) => a.value - b.value);
                        
                        const end = performance.now();
                        
                        return {
                            duration: end - start,
                            arraySize: size,
                            operationsPerformed: 4,
                            filteredCount: filtered.length,
                            reducedSum: reduced,
                            operationsPerSecond: (size * 4) / ((end - start) / 1000)
                        };
                    }
                    
                    async testObjectManipulation(count) {
                        const start = performance.now();
                        
                        const objects = [];
                        
                        // Create objects with complex nested structures
                        for (let i = 0; i < count; i++) {
                            const obj = {
                                id: i,
                                data: {
                                    level1: {
                                        level2: {
                                            level3: {
                                                value: Math.random(),
                                                array: new Array(10).fill(i),
                                                timestamp: Date.now()
                                            }
                                        }
                                    }
                                },
                                methods: {
                                    calculate: function() {
                                        return this.data.level1.level2.level3.value * 100;
                                    },
                                    transform: function() {
                                        return JSON.stringify(this.data);
                                    }
                                }
                            };
                            
                            objects.push(obj);
                        }
                        
                        // Perform object manipulations
                        const calculations = objects.map(obj => obj.methods.calculate());
                        const transformations = objects.map(obj => obj.methods.transform());
                        const serializations = objects.map(obj => JSON.parse(JSON.stringify(obj.data)));
                        
                        const end = performance.now();
                        
                        return {
                            duration: end - start,
                            objectCount: count,
                            operationsPerformed: 3,
                            avgCalculation: calculations.reduce((sum, val) => sum + val, 0) / calculations.length,
                            serializationSize: transformations.join('').length,
                            operationsPerSecond: (count * 3) / ((end - start) / 1000)
                        };
                    }
                    
                    async testDOMOperations(count) {
                        const start = performance.now();
                        
                        const container = document.createElement('div');
                        container.className = 'stress-test-container';
                        document.body.appendChild(container);
                        
                        // Create complex DOM structure
                        for (let i = 0; i < count; i++) {
                            const element = document.createElement('div');
                            element.className = `stress-element-${i}`;
                            element.innerHTML = `
                                <h3>Element ${i}</h3>
                                <p>Content for element ${i}</p>
                                <ul>
                                    <li>Item 1</li>
                                    <li>Item 2</li>
                                    <li>Item 3</li>
                                </ul>
                                <button onclick="console.log('clicked ${i}')">Button ${i}</button>
                            `;
                            container.appendChild(element);
                        }
                        
                        // Perform DOM queries and manipulations
                        const elements = container.querySelectorAll('.stress-element-1, .stress-element-5, .stress-element-10');
                        elements.forEach(el => {
                            el.style.backgroundColor = 'lightblue';
                            el.style.padding = '10px';
                            el.style.margin = '5px';
                        });
                        
                        // Clone and move elements
                        const firstElement = container.firstElementChild;
                        if (firstElement) {
                            const clone = firstElement.cloneNode(true);
                            container.appendChild(clone);
                        }
                        
                        const end = performance.now();
                        
                        // Cleanup
                        document.body.removeChild(container);
                        
                        return {
                            duration: end - start,
                            elementsCreated: count,
                            elementsModified: elements.length,
                            operationsPerSecond: (count + elements.length) / ((end - start) / 1000)
                        };
                    }
                    
                    async createCPUPressure(intensity = 'medium') {
                        // Create background CPU pressure
                        const pressureConfig = {
                            light: { workers: 1, iterations: 10000 },
                            medium: { workers: 2, iterations: 50000 },
                            heavy: { workers: 4, iterations: 100000 },
                            extreme: { workers: 8, iterations: 200000 }
                        };
                        
                        const config = pressureConfig[intensity] || pressureConfig.medium;
                        const workers = [];
                        
                        try {
                            for (let i = 0; i < config.workers; i++) {
                                const workerCode = `
                                    let running = true;
                                    self.onmessage = function(e) {
                                        if (e.data === 'stop') {
                                            running = false;
                                            self.postMessage('stopped');
                                            return;
                                        }
                                        
                                        let result = 0;
                                        let iterations = 0;
                                        const start = Date.now();
                                        
                                        while (running && iterations < ${config.iterations}) {
                                            result += Math.sqrt(iterations) * Math.sin(iterations);
                                            iterations++;
                                            
                                            // Yield occasionally
                                            if (iterations % 1000 === 0) {
                                                if (Date.now() - start > 5000) break; // Max 5 seconds
                                            }
                                        }
                                        
                                        self.postMessage({ result, iterations, duration: Date.now() - start });
                                    };
                                `;
                                
                                const blob = new Blob([workerCode], { type: 'application/javascript' });
                                const workerUrl = URL.createObjectURL(blob);
                                const worker = new Worker(workerUrl);
                                
                                workers.push({ worker, url: workerUrl });
                                worker.postMessage('start');
                            }
                            
                            return workers;
                        } catch (error) {
                            // Cleanup on error
                            workers.forEach(({ worker, url }) => {
                                worker.terminate();
                                URL.revokeObjectURL(url);
                            });
                            throw error;
                        }
                    }
                    
                    async stopCPUPressure(workers) {
                        const results = [];
                        
                        for (const { worker, url } of workers) {
                            try {
                                const result = await new Promise((resolve, reject) => {
                                    const timeout = setTimeout(() => {
                                        reject(new Error('Worker stop timeout'));
                                    }, 2000);
                                    
                                    worker.onmessage = (e) => {
                                        clearTimeout(timeout);
                                        resolve(e.data);
                                    };
                                    
                                    worker.postMessage('stop');
                                });
                                
                                results.push(result);
                            } catch (error) {
                                results.push({ error: error.message });
                            } finally {
                                worker.terminate();
                                URL.revokeObjectURL(url);
                            }
                        }
                        
                        return results;
                    }
                    
                    async testUnderCPUPressure(intensity = 'medium') {
                        const workers = await this.createCPUPressure(intensity);
                        
                        try {
                            // Wait a moment for CPU pressure to build
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            
                            // Run the same tests under pressure
                            const stressTests = {
                                simpleArithmetic: await this.testSimpleArithmetic(1000),
                                arrayOperations: await this.testArrayOperations(1000),
                                objectManipulation: await this.testObjectManipulation(1000),
                                domOperations: await this.testDOMOperations(100)
                            };
                            
                            const workerResults = await this.stopCPUPressure(workers);
                            
                            return {
                                intensity,
                                stressTests,
                                workerResults,
                                workersUsed: workers.length
                            };
                        } catch (error) {
                            await this.stopCPUPressure(workers);
                            throw error;
                        }
                    }
                    
                    comparePerformance(baseline, stressed) {
                        const comparison = {};
                        
                        for (const testName in baseline) {
                            if (stressed[testName]) {
                                const baseOps = baseline[testName].operationsPerSecond;
                                const stressOps = stressed[testName].operationsPerSecond;
                                
                                comparison[testName] = {
                                    baselineOps: baseOps,
                                    stressedOps: stressOps,
                                    performanceDrop: ((baseOps - stressOps) / baseOps) * 100,
                                    slowdownFactor: baseOps / stressOps,
                                    durationIncrease: stressed[testName].duration - baseline[testName].duration
                                };
                            }
                        }
                        
                        return comparison;
                    }
                    
                    async runComprehensiveStressTest() {
                        const results = {
                            startTime: Date.now(),
                            baseline: null,
                            stressTests: [],
                            comparisons: [],
                            summary: {}
                        };
                        
                        try {
                            // Establish baseline
                            results.baseline = await this.establishBaseline();
                            
                            // Test under different stress levels
                            const stressLevels = ['light', 'medium', 'heavy'];
                            
                            for (const level of stressLevels) {
                                try {
                                    const stressResult = await this.testUnderCPUPressure(level);
                                    results.stressTests.push(stressResult);
                                    
                                    const comparison = this.comparePerformance(results.baseline, stressResult.stressTests);
                                    results.comparisons.push({
                                        level,
                                        comparison
                                    });
                                } catch (error) {
                                    results.stressTests.push({
                                        level,
                                        error: error.message
                                    });
                                }
                                
                                // Rest between stress tests
                                await new Promise(resolve => setTimeout(resolve, 2000));
                            }
                            
                            // Calculate summary statistics
                            const avgPerformanceDrops = [];
                            results.comparisons.forEach(comp => {
                                Object.values(comp.comparison).forEach(test => {
                                    if (typeof test.performanceDrop === 'number' && !isNaN(test.performanceDrop)) {
                                        avgPerformanceDrops.push(test.performanceDrop);
                                    }
                                });
                            });
                            
                            results.summary = {
                                totalTests: results.stressTests.length,
                                successfulTests: results.stressTests.filter(t => !t.error).length,
                                averagePerformanceDrop: avgPerformanceDrops.length > 0 ? 
                                    avgPerformanceDrops.reduce((sum, drop) => sum + drop, 0) / avgPerformanceDrops.length : 0,
                                maxPerformanceDrop: avgPerformanceDrops.length > 0 ? Math.max(...avgPerformanceDrops) : 0,
                                testDuration: Date.now() - results.startTime
                            };
                            
                        } catch (error) {
                            results.error = error.message;
                        }
                        
                        return results;
                    }
                }
                
                const cpuTester = new CPUStressTester();
                return await cpuTester.runComprehensiveStressTest();
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify stress test structure
        assert 'baseline' in result
        assert 'stressTests' in result
        assert 'comparisons' in result
        assert 'summary' in result
        
        # Check baseline was established
        baseline = result['baseline']
        expected_baseline_tests = ['simpleArithmetic', 'arrayOperations', 'objectManipulation', 'domOperations']
        for test_name in expected_baseline_tests:
            assert test_name in baseline
            assert baseline[test_name]['duration'] > 0
            assert baseline[test_name]['operationsPerSecond'] > 0
        
        # Verify stress tests were performed
        stress_tests = result['stressTests']
        assert len(stress_tests) >= 1  # At least one stress level should complete
        
        # Check successful stress tests
        successful_tests = [t for t in stress_tests if 'error' not in t]
        if successful_tests:
            for stress_test in successful_tests:
                assert 'intensity' in stress_test
                assert 'stressTests' in stress_test
                assert 'workerResults' in stress_test
                
                # Verify the same tests were run under stress
                for test_name in expected_baseline_tests:
                    assert test_name in stress_test['stressTests']
        
        # Check performance comparisons
        comparisons = result['comparisons']
        if comparisons:
            for comparison in comparisons:
                assert 'level' in comparison
                assert 'comparison' in comparison
                
                # Check individual test comparisons
                for test_name, test_comparison in comparison['comparison'].items():
                    assert 'baselineOps' in test_comparison
                    assert 'stressedOps' in test_comparison
                    assert 'performanceDrop' in test_comparison
                    assert test_comparison['baselineOps'] > 0
                    assert test_comparison['stressedOps'] > 0
        
        # Verify summary statistics
        summary = result['summary']
        assert summary['totalTests'] >= 0
        assert summary['successfulTests'] >= 0
        assert summary['testDuration'] > 0
        assert summary['averagePerformanceDrop'] >= 0
    
    @pytest.mark.asyncio
    async def test_concurrent_operation_stress(self, base_url):
        """Test handling of many concurrent JavaScript operations."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Test concurrent operation handling under stress
                class ConcurrencyStressTester {
                    constructor() {
                        this.maxConcurrency = navigator.hardwareConcurrency || 4;
                        this.testResults = {};
                    }
                    
                    async testPromiseConcurrency() {
                        const concurrencyLevels = [10, 50, 100, 500, 1000];
                        const results = [];
                        
                        for (const level of concurrencyLevels) {
                            const start = performance.now();
                            
                            try {
                                // Create many concurrent promises
                                const promises = [];
                                for (let i = 0; i < level; i++) {
                                    promises.push(this.createAsyncOperation(i, level));
                                }
                                
                                const promiseResults = await Promise.allSettled(promises);
                                const end = performance.now();
                                
                                const successful = promiseResults.filter(r => r.status === 'fulfilled').length;
                                const failed = promiseResults.filter(r => r.status === 'rejected').length;
                                
                                results.push({
                                    concurrencyLevel: level,
                                    duration: end - start,
                                    successful,
                                    failed,
                                    successRate: (successful / level) * 100,
                                    operationsPerSecond: level / ((end - start) / 1000)
                                });
                                
                            } catch (error) {
                                const end = performance.now();
                                results.push({
                                    concurrencyLevel: level,
                                    duration: end - start,
                                    error: error.message,
                                    failed: true
                                });
                            }
                            
                            // Brief pause between tests
                            await new Promise(resolve => setTimeout(resolve, 100));
                        }
                        
                        return results;
                    }
                    
                    async createAsyncOperation(id, totalOps) {
                        // Simulate varying async operation types
                        const operationType = id % 4;
                        
                        switch (operationType) {
                            case 0:
                                // CPU-bound operation
                                return new Promise(resolve => {
                                    setTimeout(() => {
                                        let result = 0;
                                        for (let i = 0; i < 1000; i++) {
                                            result += Math.sqrt(i);
                                        }
                                        resolve({ id, type: 'cpu', result });
                                    }, Math.random() * 10);
                                });
                                
                            case 1:
                                // Memory allocation operation
                                return new Promise(resolve => {
                                    setTimeout(() => {
                                        const data = new Array(100).fill(Math.random());
                                        resolve({ id, type: 'memory', size: data.length });
                                    }, Math.random() * 20);
                                });
                                
                            case 2:
                                // DOM operation
                                return new Promise(resolve => {
                                    setTimeout(() => {
                                        const element = document.createElement('div');
                                        element.textContent = `Element ${id}`;
                                        document.body.appendChild(element);
                                        
                                        // Clean up immediately
                                        document.body.removeChild(element);
                                        
                                        resolve({ id, type: 'dom', created: true });
                                    }, Math.random() * 5);
                                });
                                
                            case 3:
                                // JSON processing operation
                                return new Promise(resolve => {
                                    setTimeout(() => {
                                        const obj = { id, data: new Array(50).fill(0).map(() => Math.random()) };
                                        const serialized = JSON.stringify(obj);
                                        const parsed = JSON.parse(serialized);
                                        resolve({ id, type: 'json', size: serialized.length });
                                    }, Math.random() * 15);
                                });
                                
                            default:
                                return Promise.resolve({ id, type: 'default' });
                        }
                    }
                    
                    async testSetTimeoutStress() {
                        const results = {
                            scheduled: 0,
                            executed: 0,
                            timeouts: [],
                            averageDelay: 0,
                            maxDelay: 0
                        };
                        
                        const testCount = 1000;
                        const scheduledTimes = [];
                        
                        // Schedule many timeouts simultaneously
                        for (let i = 0; i < testCount; i++) {
                            const scheduledTime = Date.now();
                            scheduledTimes.push(scheduledTime);
                            
                            setTimeout(() => {
                                const executedTime = Date.now();
                                const delay = executedTime - scheduledTime;
                                
                                results.executed++;
                                results.timeouts.push(delay);
                                
                                if (delay > results.maxDelay) {
                                    results.maxDelay = delay;
                                }
                            }, Math.random() * 100); // Random timeout between 0-100ms
                            
                            results.scheduled++;
                        }
                        
                        // Wait for all timeouts to complete
                        await new Promise(resolve => {
                            const checkCompletion = () => {
                                if (results.executed >= testCount * 0.95) { // Allow for 5% timeout loss
                                    resolve();
                                } else if (Date.now() - scheduledTimes[0] > 5000) { // Max 5 second wait
                                    resolve();
                                } else {
                                    setTimeout(checkCompletion, 50);
                                }
                            };
                            checkCompletion();
                        });
                        
                        // Calculate statistics
                        if (results.timeouts.length > 0) {
                            results.averageDelay = results.timeouts.reduce((sum, delay) => sum + delay, 0) / results.timeouts.length;
                            results.completionRate = (results.executed / results.scheduled) * 100;
                        }
                        
                        return results;
                    }
                    
                    async testRequestAnimationFrameStress() {
                        const results = {
                            requested: 0,
                            executed: 0,
                            frames: [],
                            averageFrameTime: 0,
                            droppedFrames: 0
                        };
                        
                        const frameCount = 120; // Attempt 120 frames (2 seconds at 60fps)
                        let lastFrameTime = performance.now();
                        
                        return new Promise(resolve => {
                            const frameCallback = (currentTime) => {
                                const frameTime = currentTime - lastFrameTime;
                                results.frames.push(frameTime);
                                results.executed++;
                                
                                // Detect dropped frames (> 20ms indicates frame drop at 60fps)
                                if (frameTime > 20) {
                                    results.droppedFrames++;
                                }
                                
                                lastFrameTime = currentTime;
                                
                                if (results.executed < frameCount) {
                                    // Do some work each frame to create stress
                                    for (let i = 0; i < 1000; i++) {
                                        Math.sqrt(i);
                                    }
                                    
                                    requestAnimationFrame(frameCallback);
                                    results.requested++;
                                } else {
                                    // Calculate final statistics
                                    if (results.frames.length > 1) {
                                        results.averageFrameTime = results.frames.slice(1).reduce((sum, time) => sum + time, 0) / (results.frames.length - 1);
                                        results.estimatedFPS = 1000 / results.averageFrameTime;
                                        results.frameDropRate = (results.droppedFrames / results.executed) * 100;
                                    }
                                    
                                    resolve(results);
                                }
                            };
                            
                            requestAnimationFrame(frameCallback);
                            results.requested++;
                        });
                    }
                    
                    async testEventListenerStress() {
                        const results = {
                            listenersCreated: 0,
                            eventsDispatched: 0,
                            eventsReceived: 0,
                            averageEventTime: 0,
                            maxEventTime: 0
                        };
                        
                        const eventTarget = document.createElement('div');
                        document.body.appendChild(eventTarget);
                        
                        const eventTimes = [];
                        const listenerCount = 1000;
                        
                        // Create many event listeners
                        for (let i = 0; i < listenerCount; i++) {
                            eventTarget.addEventListener('testEvent', (e) => {
                                const eventTime = performance.now() - e.detail.startTime;
                                eventTimes.push(eventTime);
                                results.eventsReceived++;
                                
                                if (eventTime > results.maxEventTime) {
                                    results.maxEventTime = eventTime;
                                }
                            });
                            results.listenersCreated++;
                        }
                        
                        // Dispatch many events
                        const eventCount = 100;
                        for (let i = 0; i < eventCount; i++) {
                            const event = new CustomEvent('testEvent', {
                                detail: { startTime: performance.now(), eventId: i }
                            });
                            
                            eventTarget.dispatchEvent(event);
                            results.eventsDispatched++;
                            
                            // Small delay to prevent overwhelming
                            if (i % 10 === 0) {
                                await new Promise(resolve => setTimeout(resolve, 1));
                            }
                        }
                        
                        // Wait for all events to be processed
                        await new Promise(resolve => setTimeout(resolve, 100));
                        
                        // Calculate statistics
                        if (eventTimes.length > 0) {
                            results.averageEventTime = eventTimes.reduce((sum, time) => sum + time, 0) / eventTimes.length;
                            results.eventProcessingRate = (results.eventsReceived / results.eventsDispatched) * 100;
                            results.expectedEvents = results.eventsDispatched * results.listenersCreated;
                            results.actualEventExecutions = results.eventsReceived;
                        }
                        
                        // Cleanup
                        document.body.removeChild(eventTarget);
                        
                        return results;
                    }
                    
                    async runAllConcurrencyTests() {
                        const allResults = {
                            startTime: Date.now(),
                            systemInfo: {
                                hardwareConcurrency: navigator.hardwareConcurrency,
                                userAgent: navigator.userAgent,
                                memoryInfo: performance.memory ? {
                                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                                    usedJSHeapSize: performance.memory.usedJSHeapSize
                                } : null
                            },
                            tests: {}
                        };
                        
                        try {
                            allResults.tests.promiseConcurrency = await this.testPromiseConcurrency();
                            allResults.tests.setTimeoutStress = await this.testSetTimeoutStress();
                            allResults.tests.animationFrameStress = await this.testRequestAnimationFrameStress();
                            allResults.tests.eventListenerStress = await this.testEventListenerStress();
                        } catch (error) {
                            allResults.error = error.message;
                        }
                        
                        allResults.endTime = Date.now();
                        allResults.totalDuration = allResults.endTime - allResults.startTime;
                        
                        return allResults;
                    }
                }
                
                const concurrencyTester = new ConcurrencyStressTester();
                return await concurrencyTester.runAllConcurrencyTests();
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify concurrency test structure
        assert 'systemInfo' in result
        assert 'tests' in result
        assert 'totalDuration' in result
        
        # Check system info
        system_info = result['systemInfo']
        assert 'hardwareConcurrency' in system_info
        assert system_info['hardwareConcurrency'] >= 1
        
        # Verify individual tests
        tests = result['tests']
        
        # Check promise concurrency test
        if 'promiseConcurrency' in tests:
            promise_test = tests['promiseConcurrency']
            assert len(promise_test) > 0
            
            for level_result in promise_test:
                if 'error' not in level_result:
                    assert level_result['concurrencyLevel'] > 0
                    assert level_result['duration'] > 0
                    assert 'successful' in level_result
                    assert 'failed' in level_result
                    assert level_result['successRate'] >= 0
                    assert level_result['successRate'] <= 100
        
        # Check setTimeout stress test
        if 'setTimeoutStress' in tests:
            timeout_test = tests['setTimeoutStress']
            assert timeout_test['scheduled'] > 0
            assert timeout_test['executed'] >= 0
            assert timeout_test['averageDelay'] >= 0
        
        # Check animation frame stress test
        if 'animationFrameStress' in tests:
            raf_test = tests['animationFrameStress']
            assert raf_test['requested'] > 0
            assert raf_test['executed'] > 0
            if raf_test['frames']:
                assert raf_test['averageFrameTime'] > 0
                assert 'estimatedFPS' in raf_test
        
        # Check event listener stress test
        if 'eventListenerStress' in tests:
            event_test = tests['eventListenerStress']
            assert event_test['listenersCreated'] > 0
            assert event_test['eventsDispatched'] > 0
            assert event_test['eventsReceived'] >= 0
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_scenarios(self, base_url):
        """Test behavior when system resources are nearly exhausted."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                // Test resource exhaustion scenarios
                class ResourceExhaustionTester {
                    constructor() {
                        this.originalMemory = this.getMemorySnapshot();
                        this.resourceTests = {};
                    }
                    
                    getMemorySnapshot() {
                        if (performance.memory) {
                            return {
                                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                                totalJSHeapSize: performance.memory.totalJSHeapSize,
                                usedJSHeapSize: performance.memory.usedJSHeapSize,
                                timestamp: Date.now()
                            };
                        }
                        return { timestamp: Date.now(), unavailable: true };
                    }
                    
                    async testMemoryExhaustion() {
                        const memoryTest = {
                            phase: 'memory_exhaustion',
                            startMemory: this.getMemorySnapshot(),
                            allocations: [],
                            maxAllocation: 0,
                            allocationFailures: 0,
                            recoveryAttempts: 0
                        };
                        
                        try {
                            // Gradually increase memory allocation until we hit limits
                            let allocationSize = 1024 * 1024; // Start with 1MB
                            let totalAllocated = 0;
                            
                            while (allocationSize <= 64 * 1024 * 1024 && memoryTest.allocations.length < 100) { // Max 64MB per allocation, max 100 allocations
                                try {
                                    const start = performance.now();
                                    const allocation = new ArrayBuffer(allocationSize);
                                    const view = new Uint8Array(allocation);
                                    
                                    // Write to the memory to ensure it's actually allocated
                                    for (let i = 0; i < Math.min(view.length, 1000); i += 100) {
                                        view[i] = i % 256;
                                    }
                                    
                                    const end = performance.now();
                                    
                                    memoryTest.allocations.push({
                                        size: allocationSize,
                                        allocTime: end - start,
                                        memoryAfter: this.getMemorySnapshot()
                                    });
                                    
                                    totalAllocated += allocationSize;
                                    if (allocationSize > memoryTest.maxAllocation) {
                                        memoryTest.maxAllocation = allocationSize;
                                    }
                                    
                                    // Increase allocation size gradually
                                    allocationSize = Math.floor(allocationSize * 1.2);
                                    
                                    // Brief pause to allow for memory management
                                    await new Promise(resolve => setTimeout(resolve, 10));
                                    
                                } catch (error) {
                                    memoryTest.allocationFailures++;
                                    
                                    // Try recovery
                                    if (memoryTest.recoveryAttempts < 3) {
                                        memoryTest.recoveryAttempts++;
                                        
                                        // Clear some allocations
                                        const clearedCount = Math.floor(memoryTest.allocations.length * 0.3);
                                        memoryTest.allocations.splice(0, clearedCount);
                                        
                                        // Try garbage collection hint
                                        if (window.gc) {
                                            window.gc();
                                        }
                                        
                                        // Reduce allocation size
                                        allocationSize = Math.floor(allocationSize * 0.5);
                                        
                                        await new Promise(resolve => setTimeout(resolve, 100));
                                    } else {
                                        break;
                                    }
                                }
                            }
                            
                            memoryTest.endMemory = this.getMemorySnapshot();
                            memoryTest.totalAllocated = totalAllocated;
                            
                        } catch (error) {
                            memoryTest.error = error.message;
                            memoryTest.endMemory = this.getMemorySnapshot();
                        }
                        
                        return memoryTest;
                    }
                    
                    async testDOMNodeExhaustion() {
                        const domTest = {
                            phase: 'dom_exhaustion',
                            nodesCreated: 0,
                            maxDepth: 0,
                            creationFailures: 0,
                            performanceDegradation: []
                        };
                        
                        const container = document.createElement('div');
                        container.style.display = 'none'; // Hide to prevent layout thrashing
                        document.body.appendChild(container);
                        
                        try {
                            let batchSize = 1000;
                            let currentDepth = 0;
                            let parent = container;
                            
                            // Create nodes in batches until we hit performance issues
                            while (domTest.nodesCreated < 50000 && batchSize > 10) {
                                const batchStart = performance.now();
                                let batchCreated = 0;
                                
                                try {
                                    for (let i = 0; i < batchSize; i++) {
                                        const element = document.createElement('div');
                                        element.className = `stress-node-${domTest.nodesCreated + i}`;
                                        element.textContent = `Node ${domTest.nodesCreated + i}`;
                                        
                                        // Create nested structure occasionally
                                        if (i % 100 === 0 && currentDepth < 50) {
                                            parent = element;
                                            currentDepth++;
                                            if (currentDepth > domTest.maxDepth) {
                                                domTest.maxDepth = currentDepth;
                                            }
                                        }
                                        
                                        parent.appendChild(element);
                                        batchCreated++;
                                    }
                                    
                                    domTest.nodesCreated += batchCreated;
                                    
                                } catch (error) {
                                    domTest.creationFailures++;
                                    domTest.nodesCreated += batchCreated;
                                }
                                
                                const batchEnd = performance.now();
                                const batchTime = batchEnd - batchStart;
                                
                                domTest.performanceDegradation.push({
                                    nodesCreated: batchCreated,
                                    timePerNode: batchTime / batchCreated,
                                    totalNodes: domTest.nodesCreated,
                                    batchTime
                                });
                                
                                // Reduce batch size if performance is degrading
                                if (batchTime > 1000) { // If batch takes more than 1 second
                                    batchSize = Math.floor(batchSize * 0.8);
                                }
                                
                                // Brief pause
                                await new Promise(resolve => setTimeout(resolve, 10));
                            }
                            
                        } catch (error) {
                            domTest.error = error.message;
                        }
                        
                        // Cleanup
                        try {
                            document.body.removeChild(container);
                        } catch (error) {
                            domTest.cleanupError = error.message;
                        }
                        
                        return domTest;
                    }
                    
                    async testFileHandleExhaustion() {
                        const fileTest = {
                            phase: 'file_handle_exhaustion',
                            urlsCreated: 0,
                            urlsRevoked: 0,
                            creationFailures: 0,
                            activeUrls: []
                        };
                        
                        try {
                            // Create many blob URLs (which consume file handles)
                            const maxUrls = 10000;
                            
                            for (let i = 0; i < maxUrls; i++) {
                                try {
                                    const data = `Blob data ${i} - ${new Array(100).fill('x').join('')}`;
                                    const blob = new Blob([data], { type: 'text/plain' });
                                    const url = URL.createObjectURL(blob);
                                    
                                    fileTest.activeUrls.push(url);
                                    fileTest.urlsCreated++;
                                    
                                    // Occasionally revoke some URLs
                                    if (i % 1000 === 0 && fileTest.activeUrls.length > 500) {
                                        const urlsToRevoke = fileTest.activeUrls.splice(0, 200);
                                        urlsToRevoke.forEach(url => {
                                            URL.revokeObjectURL(url);
                                            fileTest.urlsRevoked++;
                                        });
                                    }
                                    
                                } catch (error) {
                                    fileTest.creationFailures++;
                                    if (fileTest.creationFailures > 100) {
                                        break; // Stop if too many failures
                                    }
                                }
                                
                                // Brief pause every 100 creations
                                if (i % 100 === 0) {
                                    await new Promise(resolve => setTimeout(resolve, 1));
                                }
                            }
                            
                        } catch (error) {
                            fileTest.error = error.message;
                        }
                        
                        // Cleanup remaining URLs
                        try {
                            fileTest.activeUrls.forEach(url => {
                                URL.revokeObjectURL(url);
                                fileTest.urlsRevoked++;
                            });
                        } catch (error) {
                            fileTest.cleanupError = error.message;
                        }
                        
                        return fileTest;
                    }
                    
                    async testEventListenerExhaustion() {
                        const eventTest = {
                            phase: 'event_listener_exhaustion',
                            elementsCreated: 0,
                            listenersCreated: 0,
                            eventsDispatched: 0,
                            memorySnapshots: []
                        };
                        
                        const elements = [];
                        
                        try {
                            eventTest.memorySnapshots.push({
                                label: 'start',
                                memory: this.getMemorySnapshot()
                            });
                            
                            // Create many elements with multiple event listeners
                            for (let i = 0; i < 5000; i++) {
                                const element = document.createElement('div');
                                element.style.display = 'none';
                                document.body.appendChild(element);
                                
                                // Add multiple event listeners to each element
                                const eventTypes = ['click', 'mouseover', 'mouseout', 'focus', 'blur'];
                                
                                eventTypes.forEach(eventType => {
                                    const handler = (e) => {
                                        // Do some work in the handler
                                        for (let j = 0; j < 10; j++) {
                                            Math.sqrt(j);
                                        }
                                    };
                                    
                                    element.addEventListener(eventType, handler);
                                    eventTest.listenersCreated++;
                                });
                                
                                elements.push(element);
                                eventTest.elementsCreated++;
                                
                                // Take memory snapshots periodically
                                if (i % 1000 === 0) {
                                    eventTest.memorySnapshots.push({
                                        label: `elements_${i}`,
                                        memory: this.getMemorySnapshot()
                                    });
                                }
                                
                                // Brief pause
                                if (i % 100 === 0) {
                                    await new Promise(resolve => setTimeout(resolve, 1));
                                }
                            }
                            
                            // Dispatch events to test performance
                            const sampleElements = elements.slice(0, 100);
                            for (const element of sampleElements) {
                                const event = new Event('click');
                                element.dispatchEvent(event);
                                eventTest.eventsDispatched++;
                            }
                            
                            eventTest.memorySnapshots.push({
                                label: 'after_events',
                                memory: this.getMemorySnapshot()
                            });
                            
                        } catch (error) {
                            eventTest.error = error.message;
                        }
                        
                        // Cleanup
                        try {
                            elements.forEach(element => {
                                document.body.removeChild(element);
                            });
                        } catch (error) {
                            eventTest.cleanupError = error.message;
                        }
                        
                        eventTest.memorySnapshots.push({
                            label: 'after_cleanup',
                            memory: this.getMemorySnapshot()
                        });
                        
                        return eventTest;
                    }
                    
                    async runAllExhaustionTests() {
                        const results = {
                            startTime: Date.now(),
                            originalMemory: this.originalMemory,
                            tests: {}
                        };
                        
                        try {
                            results.tests.memoryExhaustion = await this.testMemoryExhaustion();
                            
                            // Brief pause between tests
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            
                            results.tests.domNodeExhaustion = await this.testDOMNodeExhaustion();
                            
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            
                            results.tests.fileHandleExhaustion = await this.testFileHandleExhaustion();
                            
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            
                            results.tests.eventListenerExhaustion = await this.testEventListenerExhaustion();
                            
                        } catch (error) {
                            results.error = error.message;
                        }
                        
                        results.endTime = Date.now();
                        results.totalDuration = results.endTime - results.startTime;
                        results.finalMemory = this.getMemorySnapshot();
                        
                        return results;
                    }
                }
                
                const exhaustionTester = new ResourceExhaustionTester();
                return await exhaustionTester.runAllExhaustionTests();
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify resource exhaustion test structure
        assert 'originalMemory' in result
        assert 'tests' in result
        assert 'finalMemory' in result
        assert 'totalDuration' in result
        
        # Check individual exhaustion tests
        tests = result['tests']
        
        # Memory exhaustion test
        if 'memoryExhaustion' in tests:
            memory_test = tests['memoryExhaustion']
            assert memory_test['phase'] == 'memory_exhaustion'
            assert 'startMemory' in memory_test
            assert 'allocations' in memory_test
            assert memory_test['allocationFailures'] >= 0
            assert memory_test['recoveryAttempts'] >= 0
        
        # DOM node exhaustion test
        if 'domNodeExhaustion' in tests:
            dom_test = tests['domNodeExhaustion']
            assert dom_test['phase'] == 'dom_exhaustion'
            assert dom_test['nodesCreated'] > 0
            assert 'performanceDegradation' in dom_test
            assert len(dom_test['performanceDegradation']) > 0
        
        # File handle exhaustion test
        if 'fileHandleExhaustion' in tests:
            file_test = tests['fileHandleExhaustion']
            assert file_test['phase'] == 'file_handle_exhaustion'
            assert file_test['urlsCreated'] > 0
            assert file_test['urlsRevoked'] >= 0
            assert file_test['creationFailures'] >= 0
        
        # Event listener exhaustion test
        if 'eventListenerExhaustion' in tests:
            event_test = tests['eventListenerExhaustion']
            assert event_test['phase'] == 'event_listener_exhaustion'
            assert event_test['elementsCreated'] > 0
            assert event_test['listenersCreated'] > 0
            assert 'memorySnapshots' in event_test
            assert len(event_test['memorySnapshots']) > 0


<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Implement Phase 2: Production Optimization", "status": "in_progress", "activeForm": "Implementing Phase 2: Production Optimization"}, {"content": "Create comprehensive network resilience test suite", "status": "completed", "activeForm": "Creating comprehensive network resilience test suite"}, {"content": "Build platform-specific edge case tests", "status": "completed", "activeForm": "Building platform-specific edge case tests"}, {"content": "Implement performance under pressure test suite", "status": "completed", "activeForm": "Implementing performance under pressure test suite"}, {"content": "Create browser engine compatibility tests", "status": "in_progress", "activeForm": "Creating browser engine compatibility tests"}, {"content": "Build memory management and leak detection tests", "status": "pending", "activeForm": "Building memory management and leak detection tests"}]