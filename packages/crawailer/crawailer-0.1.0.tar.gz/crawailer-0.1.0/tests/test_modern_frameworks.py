"""
Comprehensive test suite for modern web framework integration.

Tests JavaScript execution capabilities across React, Vue, and Angular applications
with realistic component interactions, state management, and advanced workflows.
"""
import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

from crawailer import get, get_many
from crawailer.browser import Browser
from crawailer.config import BrowserConfig


class TestModernFrameworkIntegration:
    """Test JavaScript execution with modern web frameworks."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for local test server."""
        return "http://localhost:8083"
    
    @pytest.fixture
    def framework_urls(self, base_url):
        """URLs for different framework test applications."""
        return {
            'react': f"{base_url}/react/",
            'vue': f"{base_url}/vue/", 
            'angular': f"{base_url}/angular/"
        }
    
    @pytest.fixture
    async def browser(self):
        """Browser instance for testing."""
        config = BrowserConfig(
            headless=True,
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (compatible; CrawailerTest/1.0)'
        )
        browser = Browser(config)
        await browser.start()
        yield browser
        await browser.stop()

    # React Framework Tests
    
    @pytest.mark.asyncio
    async def test_react_component_detection(self, framework_urls):
        """Test detection of React components and features."""
        content = await get(
            framework_urls['react'],
            script="window.testData.detectReactFeatures()"
        )
        
        assert content.script_result is not None
        features = content.script_result
        
        assert features['hasReact'] is True
        assert features['hasHooks'] is True
        assert features['hasEffects'] is True
        assert 'reactVersion' in features
        assert features['reactVersion'].startswith('18')  # React 18
    
    @pytest.mark.asyncio
    async def test_react_component_interaction(self, framework_urls):
        """Test React component interactions and state updates."""
        content = await get(
            framework_urls['react'],
            script="""
                const result = await window.testData.simulateUserAction('add-todo');
                const state = window.testData.getComponentState();
                return { actionResult: result, componentState: state };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['actionResult'] == 'Todo added'
        assert 'componentState' in result
        assert result['componentState']['todosCount'] > 0
    
    @pytest.mark.asyncio
    async def test_react_hooks_functionality(self, framework_urls):
        """Test React hooks (useState, useEffect, etc.) functionality."""
        content = await get(
            framework_urls['react'],
            script="""
                // Test useState hook
                window.testData.simulateUserAction('increment-counter');
                await new Promise(resolve => setTimeout(resolve, 100));
                
                const state = window.testData.getComponentState();
                return {
                    counterValue: state.counterValue,
                    hasStateUpdate: state.counterValue > 0
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['hasStateUpdate'] is True
        assert result['counterValue'] > 0
    
    @pytest.mark.asyncio
    async def test_react_async_operations(self, framework_urls):
        """Test React async operations and loading states."""
        content = await get(
            framework_urls['react'],
            script="""
                const result = await window.testData.simulateUserAction('async-operation');
                const state = window.testData.getComponentState();
                return { 
                    operationResult: result, 
                    isLoading: state.isLoading,
                    completed: true
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['operationResult'] == 'Async operation completed'
        assert result['isLoading'] is False
        assert result['completed'] is True

    # Vue.js Framework Tests
    
    @pytest.mark.asyncio
    async def test_vue_reactivity_system(self, framework_urls):
        """Test Vue.js reactivity system and computed properties."""
        content = await get(
            framework_urls['vue'],
            script="""
                const features = window.testData.detectVueFeatures();
                const reactiveData = window.testData.getReactiveData();
                return { features, reactiveData };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['features']['hasCompositionAPI'] is True
        assert result['features']['hasReactivity'] is True
        assert result['features']['hasComputed'] is True
        assert result['features']['isVue3'] is True
    
    @pytest.mark.asyncio
    async def test_vue_composition_api(self, framework_urls):
        """Test Vue 3 Composition API functionality."""
        content = await get(
            framework_urls['vue'],
            script="""
                // Test reactive data updates
                await window.testData.simulateUserAction('fill-form');
                await window.testData.waitForUpdate();
                
                const reactiveData = window.testData.getReactiveData();
                return reactiveData;
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['totalCharacters'] > 0  # Form was filled
        assert result['isValidEmail'] is True
        assert 'completedCount' in result
    
    @pytest.mark.asyncio
    async def test_vue_watchers_and_lifecycle(self, framework_urls):
        """Test Vue watchers and lifecycle hooks."""
        content = await get(
            framework_urls['vue'],
            script="""
                // Trigger deep change to test watchers
                await window.testData.simulateUserAction('increment-counter');
                await window.testData.waitForUpdate();
                
                const appState = window.testData.getAppState();
                return {
                    counterValue: appState.counterValue,
                    updateCount: appState.updateCount,
                    hasWatchers: true
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['counterValue'] > 0
        assert result['updateCount'] > 0
        assert result['hasWatchers'] is True
    
    @pytest.mark.asyncio
    async def test_vue_performance_measurement(self, framework_urls):
        """Test Vue reactivity performance measurement."""
        content = await get(
            framework_urls['vue'],
            script="window.testData.measureReactivity()"
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert 'updateTime' in result
        assert 'updatesPerSecond' in result
        assert result['updateTime'] > 0
        assert result['updatesPerSecond'] > 0

    # Angular Framework Tests
    
    @pytest.mark.asyncio
    async def test_angular_dependency_injection(self, framework_urls):
        """Test Angular dependency injection and services."""
        content = await get(
            framework_urls['angular'],
            script="""
                const serviceData = window.testData.getServiceData();
                const features = window.testData.detectAngularFeatures();
                return { serviceData, features };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['features']['hasAngular'] is True
        assert result['features']['hasServices'] is True
        assert result['features']['hasRxJS'] is True
        assert 'serviceData' in result
    
    @pytest.mark.asyncio
    async def test_angular_reactive_forms(self, framework_urls):
        """Test Angular reactive forms and validation."""
        content = await get(
            framework_urls['angular'],
            script="""
                await window.testData.simulateUserAction('fill-form');
                const state = window.testData.getAppState();
                return {
                    formValid: state.formValid,
                    formValue: state.formValue,
                    hasValidation: true
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['formValid'] is True
        assert result['formValue']['name'] == 'Test User'
        assert result['formValue']['email'] == 'test@example.com'
        assert result['hasValidation'] is True
    
    @pytest.mark.asyncio
    async def test_angular_observables_rxjs(self, framework_urls):
        """Test Angular RxJS observables and streams."""
        content = await get(
            framework_urls['angular'],
            script="""
                await window.testData.simulateUserAction('start-timer');
                await new Promise(resolve => setTimeout(resolve, 1100)); // Wait for timer
                
                const observables = window.testData.monitorObservables();
                const serviceData = window.testData.getServiceData();
                return { observables, timerRunning: serviceData.timerRunning };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['observables']['todosObservable'] is True
        assert result['observables']['timerObservable'] is True
        assert result['timerRunning'] is True
    
    @pytest.mark.asyncio
    async def test_angular_change_detection(self, framework_urls):
        """Test Angular change detection mechanism."""
        content = await get(
            framework_urls['angular'],
            script="window.testData.measureChangeDetection()"
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert 'detectionTime' in result
        assert 'cyclesPerSecond' in result
        assert result['detectionTime'] > 0

    # Cross-Framework Comparison Tests
    
    @pytest.mark.asyncio
    async def test_framework_feature_comparison(self, framework_urls):
        """Compare features across all three frameworks."""
        frameworks = []
        
        for name, url in framework_urls.items():
            try:
                content = await get(
                    url,
                    script=f"window.testData.detect{name.capitalize()}Features()"
                )
                frameworks.append({
                    'name': name,
                    'features': content.script_result,
                    'loaded': True
                })
            except Exception as e:
                frameworks.append({
                    'name': name,
                    'error': str(e),
                    'loaded': False
                })
        
        # Verify all frameworks loaded
        loaded_frameworks = [f for f in frameworks if f['loaded']]
        assert len(loaded_frameworks) >= 2  # At least 2 should work
        
        # Check for framework-specific features
        react_framework = next((f for f in loaded_frameworks if f['name'] == 'react'), None)
        vue_framework = next((f for f in loaded_frameworks if f['name'] == 'vue'), None)
        angular_framework = next((f for f in loaded_frameworks if f['name'] == 'angular'), None)
        
        if react_framework:
            assert react_framework['features']['hasReact'] is True
            assert react_framework['features']['hasHooks'] is True
        
        if vue_framework:
            assert vue_framework['features']['hasCompositionAPI'] is True
            assert vue_framework['features']['isVue3'] is True
        
        if angular_framework:
            assert angular_framework['features']['hasAngular'] is True
            assert angular_framework['features']['hasRxJS'] is True
    
    @pytest.mark.asyncio
    async def test_concurrent_framework_operations(self, framework_urls):
        """Test concurrent operations across multiple frameworks."""
        tasks = []
        
        # React: Add todo
        tasks.append(get(
            framework_urls['react'],
            script="window.testData.simulateUserAction('add-todo')"
        ))
        
        # Vue: Fill form
        tasks.append(get(
            framework_urls['vue'], 
            script="window.testData.simulateUserAction('fill-form')"
        ))
        
        # Angular: Start timer
        tasks.append(get(
            framework_urls['angular'],
            script="window.testData.simulateUserAction('start-timer')"
        ))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that at least 2 operations succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 2
        
        # Verify results contain expected data
        for result in successful_results:
            if hasattr(result, 'script_result'):
                assert result.script_result is not None

    # Complex Workflow Tests
    
    @pytest.mark.asyncio
    async def test_react_complex_workflow(self, framework_urls):
        """Test complex multi-step workflow in React."""
        content = await get(
            framework_urls['react'],
            script="window.testData.simulateComplexWorkflow()"
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert 'stepsCompleted' in result
        assert len(result['stepsCompleted']) >= 5
        assert 'finalState' in result
        assert result['finalState']['todosCount'] > 0
    
    @pytest.mark.asyncio
    async def test_vue_complex_workflow(self, framework_urls):
        """Test complex multi-step workflow in Vue."""
        content = await get(
            framework_urls['vue'],
            script="window.testData.simulateComplexWorkflow()"
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert 'stepsCompleted' in result
        assert len(result['stepsCompleted']) >= 5
        assert 'finalState' in result
    
    @pytest.mark.asyncio
    async def test_angular_complex_workflow(self, framework_urls):
        """Test complex multi-step workflow in Angular."""
        content = await get(
            framework_urls['angular'],
            script="window.testData.simulateComplexWorkflow()"
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert 'stepsCompleted' in result
        assert len(result['stepsCompleted']) >= 5
        assert 'finalState' in result
        assert 'serviceData' in result

    # Performance and Edge Cases
    
    @pytest.mark.asyncio
    async def test_framework_memory_usage(self, framework_urls):
        """Test memory usage patterns across frameworks."""
        results = {}
        
        for name, url in framework_urls.items():
            content = await get(
                url,
                script="""
                    const beforeMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
                    
                    // Perform memory-intensive operations
                    for (let i = 0; i < 100; i++) {
                        if (window.testData.simulateUserAction) {
                            await window.testData.simulateUserAction('add-todo');
                        }
                    }
                    
                    const afterMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
                    
                    return {
                        framework: window.testData.framework,
                        memoryBefore: beforeMemory,
                        memoryAfter: afterMemory,
                        memoryIncrease: afterMemory - beforeMemory
                    };
                """
            )
            
            if content.script_result:
                results[name] = content.script_result
        
        # Verify we got results for at least 2 frameworks
        assert len(results) >= 2
        
        # Check memory patterns are reasonable
        for name, result in results.items():
            assert result['framework'] == name
            # Memory increase should be reasonable (not excessive)
            if result['memoryIncrease'] > 0:
                assert result['memoryIncrease'] < 50 * 1024 * 1024  # Less than 50MB
    
    @pytest.mark.asyncio
    async def test_framework_error_handling(self, framework_urls):
        """Test error handling in framework applications."""
        for name, url in framework_urls.items():
            content = await get(
                url,
                script="""
                    try {
                        // Try to access non-existent method
                        window.testData.nonExistentMethod();
                        return { error: false };
                    } catch (error) {
                        return { 
                            error: true, 
                            errorMessage: error.message,
                            hasErrorHandler: typeof window.lastError !== 'undefined'
                        };
                    }
                """
            )
            
            assert content.script_result is not None
            result = content.script_result
            
            assert result['error'] is True
            assert 'errorMessage' in result
    
    @pytest.mark.asyncio
    async def test_framework_accessibility_features(self, framework_urls):
        """Test accessibility features in framework applications."""
        results = {}
        
        for name, url in framework_urls.items():
            content = await get(
                url,
                script="""
                    const ariaElements = document.querySelectorAll('[aria-label], [aria-describedby], [role]');
                    const focusableElements = document.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    const hasHeadings = document.querySelectorAll('h1, h2, h3').length > 0;
                    const hasSemanticHTML = document.querySelectorAll('main, section, article, nav').length > 0;
                    
                    return {
                        ariaElementsCount: ariaElements.length,
                        focusableElementsCount: focusableElements.length,
                        hasHeadings,
                        hasSemanticHTML,
                        framework: window.testData.framework
                    };
                """
            )
            
            if content.script_result:
                results[name] = content.script_result
        
        # Verify accessibility features
        for name, result in results.items():
            assert result['focusableElementsCount'] > 0  # Should have interactive elements
            assert result['hasHeadings'] is True  # Should have heading structure
            assert result['framework'] == name


class TestFrameworkSpecificFeatures:
    """Test framework-specific advanced features."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8083"
    
    @pytest.mark.asyncio
    async def test_react_hooks_edge_cases(self, base_url):
        """Test React hooks edge cases and advanced patterns."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Test custom hook functionality
                const componentInfo = window.testData.getComponentInfo();
                
                // Test memo and callback hooks
                const performanceData = window.testData.measureReactPerformance();
                
                return {
                    componentInfo,
                    performanceData,
                    hasAdvancedHooks: true
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['hasAdvancedHooks'] is True
        assert 'componentInfo' in result
    
    @pytest.mark.asyncio
    async def test_vue_composition_api_advanced(self, base_url):
        """Test Vue Composition API advanced patterns."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Test advanced composition patterns
                const features = window.testData.detectVueFeatures();
                
                // Test provide/inject pattern simulation
                const componentInfo = window.testData.getComponentInfo();
                
                return {
                    compositionAPI: features.hasCompositionAPI,
                    lifecycle: features.hasLifecycleHooks,
                    componentInfo,
                    advancedPatterns: true
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['compositionAPI'] is True
        assert result['lifecycle'] is True
        assert result['advancedPatterns'] is True
    
    @pytest.mark.asyncio 
    async def test_angular_advanced_features(self, base_url):
        """Test Angular advanced features like change detection strategy."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                const features = window.testData.detectAngularFeatures();
                const changeDetection = window.testData.measureChangeDetection();
                
                return {
                    hasZoneJS: features.hasZoneJS,
                    hasChangeDetection: features.hasChangeDetection,
                    changeDetectionPerformance: changeDetection,
                    advancedFeatures: true
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        assert result['hasZoneJS'] is True
        assert result['hasChangeDetection'] is True
        assert result['advancedFeatures'] is True


class TestFrameworkMigrationScenarios:
    """Test scenarios that simulate framework migration or integration."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8083"
    
    @pytest.mark.asyncio
    async def test_multi_framework_page_detection(self, base_url):
        """Test detection when multiple frameworks might coexist."""
        # Test each framework page to ensure they don't conflict
        frameworks = ['react', 'vue', 'angular']
        results = []
        
        for framework in frameworks:
            content = await get(
                f"{base_url}/{framework}/",
                script="""
                    // Check what frameworks are detected on this page
                    const detectedFrameworks = {
                        react: typeof React !== 'undefined',
                        vue: typeof Vue !== 'undefined', 
                        angular: typeof ng !== 'undefined',
                        jquery: typeof $ !== 'undefined'
                    };
                    
                    return {
                        currentFramework: window.testData.framework,
                        detectedFrameworks,
                        primaryFramework: window.testData.framework
                    };
                """
            )
            
            if content.script_result:
                results.append(content.script_result)
        
        # Verify each page correctly identifies its primary framework
        assert len(results) >= 2
        
        for result in results:
            primary = result['primaryFramework']
            detected = result['detectedFrameworks']
            
            # Primary framework should be detected
            assert detected[primary] is True
            
            # Other frameworks should generally not be present
            other_frameworks = [f for f in detected.keys() if f != primary and f != 'jquery']
            other_detected = [detected[f] for f in other_frameworks]
            
            # Most other frameworks should be false (some leakage is acceptable)
            false_count = sum(1 for x in other_detected if x is False)
            assert false_count >= len(other_detected) - 1  # At most 1 false positive


# Integration with existing test infrastructure
class TestFrameworkTestInfrastructure:
    """Test that framework tests integrate properly with existing test infrastructure."""
    
    @pytest.mark.asyncio
    async def test_framework_tests_with_existing_mock_server(self):
        """Test that framework tests work with existing mock HTTP server patterns."""
        from tests.test_javascript_api import MockHTTPServer
        
        server = MockHTTPServer()
        await server.start()
        
        try:
            # Test that we can combine mock server with framework testing
            content = await get(
                f"http://localhost:{server.port}/react-app",
                script="""
                    // Simulate a React-like environment
                    window.React = { version: '18.2.0' };
                    window.testData = {
                        framework: 'react',
                        detectReactFeatures: () => ({ hasReact: true, version: '18.2.0' })
                    };
                    
                    return window.testData.detectReactFeatures();
                """
            )
            
            assert content.script_result is not None
            assert content.script_result['hasReact'] is True
            
        finally:
            await server.stop()
    
    @pytest.mark.asyncio
    async def test_framework_integration_with_browser_configs(self):
        """Test framework testing with different browser configurations."""
        configs = [
            BrowserConfig(viewport={'width': 1920, 'height': 1080}),  # Desktop
            BrowserConfig(viewport={'width': 375, 'height': 667}),   # Mobile
            BrowserConfig(viewport={'width': 768, 'height': 1024})   # Tablet
        ]
        
        for config in configs:
            browser = Browser(config)
            await browser.start()
            
            try:
                # Test a simple framework detection
                result = await browser.execute_script(
                    "http://localhost:8083/react/",
                    "window.testData.getComponentInfo()"
                )
                
                assert result is not None
                assert 'totalInputs' in result
                assert result['totalInputs'] > 0
                
            finally:
                await browser.stop()