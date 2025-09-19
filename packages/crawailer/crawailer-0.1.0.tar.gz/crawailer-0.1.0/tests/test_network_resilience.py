"""
Network resilience and recovery test suite.

Tests JavaScript execution under various network conditions including
timeouts, retries, progressive failure recovery, offline scenarios,
and connection quality variations.
"""
import pytest
import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
import json

from crawailer import get, get_many
from crawailer.browser import Browser
from crawailer.config import BrowserConfig


class TestNetworkResilience:
    """Test JavaScript execution under various network conditions."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for local test server."""
        return "http://localhost:8083"
    
    @pytest.fixture
    def resilient_config(self):
        """Browser configuration with network resilience settings."""
        return BrowserConfig(
            headless=True,
            viewport={'width': 1280, 'height': 720},
            timeout=30000,  # 30 second timeout
            user_agent='Mozilla/5.0 (compatible; CrawailerTest/1.0)'
        )
    
    @pytest.fixture
    async def browser(self, resilient_config):
        """Browser instance for testing network resilience."""
        browser = Browser(resilient_config)
        await browser.start()
        yield browser
        await browser.stop()

    # Network Timeout and Retry Patterns
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, base_url):
        """Test handling of network timeouts and connection delays."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Simulate network operations with timeout handling
                const networkOperations = [];
                
                // Test 1: Basic timeout simulation
                const basicTimeoutTest = async () => {
                    const timeoutPromise = new Promise((resolve, reject) => {
                        setTimeout(() => reject(new Error('Network timeout')), 1000);
                    });
                    
                    const dataPromise = new Promise(resolve => {
                        setTimeout(() => resolve({ data: 'success' }), 2000);
                    });
                    
                    try {
                        const result = await Promise.race([timeoutPromise, dataPromise]);
                        return { success: true, result };
                    } catch (error) {
                        return { success: false, error: error.message };
                    }
                };
                
                // Test 2: Retry with exponential backoff
                const retryWithBackoff = async (maxRetries = 3) => {
                    const attempts = [];
                    
                    for (let attempt = 1; attempt <= maxRetries; attempt++) {
                        const delay = Math.pow(2, attempt - 1) * 100; // 100ms, 200ms, 400ms
                        
                        try {
                            await new Promise(resolve => setTimeout(resolve, delay));
                            
                            // Simulate random failure (70% success rate)
                            if (Math.random() > 0.3) {
                                attempts.push({ attempt, success: true, delay });
                                return { success: true, attempts };
                            } else {
                                attempts.push({ attempt, success: false, delay, error: 'Simulated failure' });
                            }
                        } catch (error) {
                            attempts.push({ attempt, success: false, delay, error: error.message });
                        }
                    }
                    
                    return { success: false, attempts };
                };
                
                // Test 3: Circuit breaker pattern
                class CircuitBreaker {
                    constructor(threshold = 3, timeout = 5000) {
                        this.threshold = threshold;
                        this.timeout = timeout;
                        this.failureCount = 0;
                        this.lastFailTime = null;
                        this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
                    }
                    
                    async call(fn) {
                        if (this.state === 'OPEN') {
                            if (Date.now() - this.lastFailTime < this.timeout) {
                                throw new Error('Circuit breaker is OPEN');
                            } else {
                                this.state = 'HALF_OPEN';
                            }
                        }
                        
                        try {
                            const result = await fn();
                            if (this.state === 'HALF_OPEN') {
                                this.state = 'CLOSED';
                                this.failureCount = 0;
                            }
                            return result;
                        } catch (error) {
                            this.failureCount++;
                            this.lastFailTime = Date.now();
                            
                            if (this.failureCount >= this.threshold) {
                                this.state = 'OPEN';
                            }
                            
                            throw error;
                        }
                    }
                }
                
                const circuitBreaker = new CircuitBreaker(2, 1000);
                const circuitBreakerTest = async () => {
                    const results = [];
                    
                    for (let i = 0; i < 5; i++) {
                        try {
                            const result = await circuitBreaker.call(async () => {
                                // Simulate failing service
                                if (i < 3) {
                                    throw new Error('Service unavailable');
                                }
                                return { data: `Success on attempt ${i + 1}` };
                            });
                            
                            results.push({ attempt: i + 1, success: true, result });
                        } catch (error) {
                            results.push({ 
                                attempt: i + 1, 
                                success: false, 
                                error: error.message,
                                circuitState: circuitBreaker.state
                            });
                        }
                        
                        // Small delay between attempts
                        await new Promise(resolve => setTimeout(resolve, 200));
                    }
                    
                    return results;
                };
                
                // Execute all tests
                const basicTimeout = await basicTimeoutTest();
                const retryResult = await retryWithBackoff();
                const circuitBreakerResult = await circuitBreakerTest();
                
                return {
                    basicTimeout,
                    retryResult,
                    circuitBreakerResult,
                    testsSummary: {
                        basicTimeoutHandled: !basicTimeout.success && basicTimeout.error.includes('timeout'),
                        retryAttempted: retryResult.attempts && retryResult.attempts.length > 1,
                        circuitBreakerActivated: circuitBreakerResult.some(r => r.error && r.error.includes('OPEN'))
                    }
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify timeout handling
        basic_timeout = result['basicTimeout']
        assert basic_timeout['success'] is False
        assert 'timeout' in basic_timeout['error'].lower()
        
        # Verify retry logic
        retry_result = result['retryResult']
        assert 'attempts' in retry_result
        assert len(retry_result['attempts']) >= 1
        
        # Verify circuit breaker
        circuit_breaker_result = result['circuitBreakerResult']
        assert len(circuit_breaker_result) == 5
        
        # Verify test summary
        tests_summary = result['testsSummary']
        assert tests_summary['basicTimeoutHandled'] is True
        assert tests_summary['retryAttempted'] is True
    
    @pytest.mark.asyncio
    async def test_progressive_failure_recovery(self, base_url):
        """Test progressive failure recovery patterns."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Simulate progressive failure recovery system
                class ProgressiveRecovery {
                    constructor() {
                        this.services = new Map();
                        this.healthChecks = new Map();
                        this.degradationLevels = ['full', 'partial', 'minimal', 'offline'];
                        this.currentLevel = 'full';
                    }
                    
                    registerService(name, config) {
                        this.services.set(name, {
                            ...config,
                            health: 'healthy',
                            lastCheck: Date.now(),
                            failures: 0
                        });
                    }
                    
                    async checkHealth(serviceName) {
                        const service = this.services.get(serviceName);
                        if (!service) return false;
                        
                        try {
                            // Simulate health check
                            const isHealthy = Math.random() > 0.2; // 80% success rate
                            
                            if (isHealthy) {
                                service.health = 'healthy';
                                service.failures = 0;
                            } else {
                                service.failures++;
                                if (service.failures >= 3) {
                                    service.health = 'unhealthy';
                                } else {
                                    service.health = 'degraded';
                                }
                            }
                            
                            service.lastCheck = Date.now();
                            return isHealthy;
                        } catch (error) {
                            service.health = 'unhealthy';
                            service.failures++;
                            return false;
                        }
                    }
                    
                    async adaptToFailures() {
                        const serviceStates = Array.from(this.services.values());
                        const unhealthyCount = serviceStates.filter(s => s.health === 'unhealthy').length;
                        const degradedCount = serviceStates.filter(s => s.health === 'degraded').length;
                        const totalServices = serviceStates.length;
                        
                        if (unhealthyCount >= totalServices * 0.8) {
                            this.currentLevel = 'offline';
                        } else if (unhealthyCount >= totalServices * 0.5) {
                            this.currentLevel = 'minimal';
                        } else if (degradedCount >= totalServices * 0.3) {
                            this.currentLevel = 'partial';
                        } else {
                            this.currentLevel = 'full';
                        }
                        
                        return this.currentLevel;
                    }
                    
                    async recoverServices() {
                        const recoveryAttempts = [];
                        
                        for (const [name, service] of this.services) {
                            if (service.health !== 'healthy') {
                                try {
                                    // Simulate recovery attempt
                                    await new Promise(resolve => setTimeout(resolve, 100));
                                    
                                    const recoverySuccess = Math.random() > 0.4; // 60% recovery rate
                                    
                                    if (recoverySuccess) {
                                        service.health = 'healthy';
                                        service.failures = Math.max(0, service.failures - 1);
                                    }
                                    
                                    recoveryAttempts.push({
                                        service: name,
                                        success: recoverySuccess,
                                        newHealth: service.health
                                    });
                                } catch (error) {
                                    recoveryAttempts.push({
                                        service: name,
                                        success: false,
                                        error: error.message
                                    });
                                }
                            }
                        }
                        
                        return recoveryAttempts;
                    }
                }
                
                // Test progressive recovery
                const recovery = new ProgressiveRecovery();
                
                // Register services
                recovery.registerService('api', { endpoint: '/api', timeout: 5000 });
                recovery.registerService('database', { endpoint: '/db', timeout: 10000 });
                recovery.registerService('cache', { endpoint: '/cache', timeout: 1000 });
                recovery.registerService('search', { endpoint: '/search', timeout: 3000 });
                
                const testResults = {
                    initialLevel: recovery.currentLevel,
                    healthChecks: [],
                    adaptations: [],
                    recoveryAttempts: []
                };
                
                // Simulate multiple failure and recovery cycles
                for (let cycle = 0; cycle < 3; cycle++) {
                    // Health check cycle
                    const healthResults = {};
                    for (const serviceName of recovery.services.keys()) {
                        const isHealthy = await recovery.checkHealth(serviceName);
                        healthResults[serviceName] = {
                            healthy: isHealthy,
                            service: recovery.services.get(serviceName)
                        };
                    }
                    
                    testResults.healthChecks.push({
                        cycle,
                        results: healthResults
                    });
                    
                    // Adaptation based on health
                    const newLevel = await recovery.adaptToFailures();
                    testResults.adaptations.push({
                        cycle,
                        level: newLevel,
                        timestamp: Date.now()
                    });
                    
                    // Recovery attempts
                    const recoveryResults = await recovery.recoverServices();
                    testResults.recoveryAttempts.push({
                        cycle,
                        attempts: recoveryResults
                    });
                    
                    // Wait between cycles
                    await new Promise(resolve => setTimeout(resolve, 200));
                }
                
                return {
                    testResults,
                    finalLevel: recovery.currentLevel,
                    totalCycles: 3,
                    servicesRegistered: recovery.services.size,
                    summary: {
                        levelChanges: testResults.adaptations.map(a => a.level),
                        totalRecoveryAttempts: testResults.recoveryAttempts
                            .reduce((total, cycle) => total + cycle.attempts.length, 0),
                        successfulRecoveries: testResults.recoveryAttempts
                            .reduce((total, cycle) => total + cycle.attempts.filter(a => a.success).length, 0)
                    }
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify progressive recovery system
        assert result['totalCycles'] == 3
        assert result['servicesRegistered'] == 4
        
        test_results = result['testResults']
        assert len(test_results['healthChecks']) == 3
        assert len(test_results['adaptations']) == 3
        assert len(test_results['recoveryAttempts']) == 3
        
        # Verify summary metrics
        summary = result['summary']
        assert 'levelChanges' in summary
        assert summary['totalRecoveryAttempts'] >= 0
        assert summary['successfulRecoveries'] >= 0
    
    @pytest.mark.asyncio
    async def test_offline_mode_handling(self, base_url):
        """Test offline mode detection and graceful degradation."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                // Simulate offline mode handling
                class OfflineManager {
                    constructor() {
                        this.isOnline = navigator.onLine;
                        this.offlineQueue = [];
                        this.lastOnlineTime = Date.now();
                        this.syncAttempts = 0;
                        this.setupEventListeners();
                    }
                    
                    setupEventListeners() {
                        // Simulate online/offline events
                        this.originalOnLine = navigator.onLine;
                    }
                    
                    simulateOffline() {
                        this.isOnline = false;
                        this.lastOfflineTime = Date.now();
                        this.onOffline();
                    }
                    
                    simulateOnline() {
                        this.isOnline = true;
                        this.lastOnlineTime = Date.now();
                        this.onOnline();
                    }
                    
                    onOffline() {
                        // Store current state for offline use
                        const currentState = {
                            timestamp: Date.now(),
                            url: window.location.href,
                            userData: this.getCurrentUserData(),
                            pendingActions: [...this.offlineQueue]
                        };
                        
                        localStorage.setItem('offlineState', JSON.stringify(currentState));
                    }
                    
                    onOnline() {
                        // Attempt to sync when back online
                        this.syncOfflineData();
                    }
                    
                    getCurrentUserData() {
                        // Simulate getting current user data
                        return {
                            formData: {
                                name: 'Test User',
                                email: 'test@example.com'
                            },
                            interactions: 5,
                            lastAction: 'form_fill'
                        };
                    }
                    
                    queueAction(action) {
                        this.offlineQueue.push({
                            ...action,
                            timestamp: Date.now(),
                            id: Math.random().toString(36).substr(2, 9)
                        });
                        
                        // Try immediate sync if online
                        if (this.isOnline) {
                            this.syncOfflineData();
                        }
                        
                        return this.offlineQueue.length;
                    }
                    
                    async syncOfflineData() {
                        if (!this.isOnline || this.offlineQueue.length === 0) {
                            return { synced: 0, failed: 0 };
                        }
                        
                        this.syncAttempts++;
                        const syncResults = {
                            attempted: this.offlineQueue.length,
                            synced: 0,
                            failed: 0,
                            errors: []
                        };
                        
                        // Process queue
                        const queue = [...this.offlineQueue];
                        this.offlineQueue = [];
                        
                        for (const action of queue) {
                            try {
                                // Simulate sync attempt
                                await new Promise(resolve => setTimeout(resolve, 50));
                                
                                const syncSuccess = Math.random() > 0.2; // 80% success rate
                                
                                if (syncSuccess) {
                                    syncResults.synced++;
                                } else {
                                    syncResults.failed++;
                                    syncResults.errors.push(`Failed to sync action ${action.id}`);
                                    // Re-queue failed actions
                                    this.offlineQueue.push(action);
                                }
                            } catch (error) {
                                syncResults.failed++;
                                syncResults.errors.push(error.message);
                                this.offlineQueue.push(action);
                            }
                        }
                        
                        return syncResults;
                    }
                    
                    getOfflineCapabilities() {
                        return {
                            hasLocalStorage: typeof localStorage !== 'undefined',
                            hasIndexedDB: typeof indexedDB !== 'undefined',
                            hasServiceWorker: typeof navigator.serviceWorker !== 'undefined',
                            hasAppCache: typeof window.applicationCache !== 'undefined',
                            canDetectOnlineStatus: typeof navigator.onLine !== 'undefined'
                        };
                    }
                }
                
                // Test offline scenarios
                const offlineManager = new OfflineManager();
                const testScenarios = [];
                
                // Scenario 1: Normal online operation
                testScenarios.push({
                    scenario: 'online_operation',
                    isOnline: offlineManager.isOnline,
                    queueLength: offlineManager.offlineQueue.length
                });
                
                // Scenario 2: Queue actions while online
                offlineManager.queueAction({ type: 'user_interaction', data: 'click_button' });
                offlineManager.queueAction({ type: 'form_submit', data: { name: 'Test', email: 'test@example.com' } });
                
                testScenarios.push({
                    scenario: 'queue_while_online',
                    queueLength: offlineManager.offlineQueue.length
                });
                
                // Scenario 3: Go offline and queue more actions
                offlineManager.simulateOffline();
                
                offlineManager.queueAction({ type: 'offline_interaction', data: 'tried_to_submit' });
                offlineManager.queueAction({ type: 'offline_edit', data: 'modified_form' });
                
                testScenarios.push({
                    scenario: 'offline_queueing',
                    isOnline: offlineManager.isOnline,
                    queueLength: offlineManager.offlineQueue.length
                });
                
                // Scenario 4: Come back online and sync
                offlineManager.simulateOnline();
                const syncResult = await offlineManager.syncOfflineData();
                
                testScenarios.push({
                    scenario: 'online_sync',
                    isOnline: offlineManager.isOnline,
                    syncResult: syncResult,
                    remainingQueue: offlineManager.offlineQueue.length
                });
                
                return {
                    testScenarios,
                    offlineCapabilities: offlineManager.getOfflineCapabilities(),
                    finalState: {
                        isOnline: offlineManager.isOnline,
                        queueLength: offlineManager.offlineQueue.length,
                        syncAttempts: offlineManager.syncAttempts
                    }
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify offline capabilities
        offline_capabilities = result['offlineCapabilities']
        assert offline_capabilities['hasLocalStorage'] is True
        assert offline_capabilities['canDetectOnlineStatus'] is True
        
        # Verify test scenarios
        test_scenarios = result['testScenarios']
        assert len(test_scenarios) == 4
        
        # Check specific scenarios
        scenario_types = [scenario['scenario'] for scenario in test_scenarios]
        assert 'online_operation' in scenario_types
        assert 'offline_queueing' in scenario_types
        assert 'online_sync' in scenario_types
        
        # Verify sync functionality
        sync_scenario = next(s for s in test_scenarios if s['scenario'] == 'online_sync')
        assert 'syncResult' in sync_scenario
        assert sync_scenario['syncResult']['attempted'] > 0

    # Connection Quality and Adaptive Loading
    
    @pytest.mark.asyncio
    async def test_connection_quality_adaptation(self, base_url):
        """Test adaptation to different connection qualities."""
        content = await get(
            f"{base_url}/react/",
            script="""
                // Simulate connection quality detection and adaptation
                class ConnectionQualityManager {
                    constructor() {
                        this.connectionInfo = this.getConnectionInfo();
                        this.qualityMetrics = {
                            ping: 0,
                            downloadSpeed: 0,
                            uploadSpeed: 0,
                            packetLoss: 0
                        };
                        this.adaptiveSettings = {
                            imageQuality: 'high',
                            videoQuality: 'hd',
                            prefetchEnabled: true,
                            backgroundSyncEnabled: true
                        };
                    }
                    
                    getConnectionInfo() {
                        if (navigator.connection) {
                            return {
                                effectiveType: navigator.connection.effectiveType,
                                downlink: navigator.connection.downlink,
                                rtt: navigator.connection.rtt,
                                saveData: navigator.connection.saveData
                            };
                        }
                        
                        // Fallback detection
                        return {
                            effectiveType: 'unknown',
                            downlink: null,
                            rtt: null,
                            saveData: false
                        };
                    }
                    
                    async measureConnectionSpeed() {
                        const startTime = Date.now();
                        
                        try {
                            // Simulate connection speed test
                            const testData = new Array(1000).fill('x').join(''); // Small test payload
                            
                            // Simulate round-trip time
                            await new Promise(resolve => {
                                const delay = Math.random() * 200 + 50; // 50-250ms
                                setTimeout(resolve, delay);
                            });
                            
                            const endTime = Date.now();
                            const rtt = endTime - startTime;
                            
                            // Estimate connection quality based on RTT
                            let quality = 'unknown';
                            if (rtt < 100) quality = 'excellent';
                            else if (rtt < 200) quality = 'good';
                            else if (rtt < 500) quality = 'fair';
                            else quality = 'poor';
                            
                            this.qualityMetrics = {
                                ping: rtt,
                                downloadSpeed: Math.max(1, 100 - rtt / 10), // Simulated Mbps
                                uploadSpeed: Math.max(0.5, 50 - rtt / 20), // Simulated Mbps
                                packetLoss: Math.min(0.1, rtt / 5000), // Simulated packet loss
                                quality
                            };
                            
                            return this.qualityMetrics;
                        } catch (error) {
                            this.qualityMetrics.quality = 'error';
                            throw error;
                        }
                    }
                    
                    adaptToConnection() {
                        const quality = this.qualityMetrics.quality;
                        const saveData = this.connectionInfo.saveData;
                        
                        switch (quality) {
                            case 'excellent':
                                this.adaptiveSettings = {
                                    imageQuality: 'high',
                                    videoQuality: 'hd',
                                    prefetchEnabled: true,
                                    backgroundSyncEnabled: true,
                                    maxConcurrentRequests: 6
                                };
                                break;
                                
                            case 'good':
                                this.adaptiveSettings = {
                                    imageQuality: 'medium',
                                    videoQuality: 'sd',
                                    prefetchEnabled: true,
                                    backgroundSyncEnabled: true,
                                    maxConcurrentRequests: 4
                                };
                                break;
                                
                            case 'fair':
                                this.adaptiveSettings = {
                                    imageQuality: 'low',
                                    videoQuality: 'low',
                                    prefetchEnabled: false,
                                    backgroundSyncEnabled: false,
                                    maxConcurrentRequests: 2
                                };
                                break;
                                
                            case 'poor':
                                this.adaptiveSettings = {
                                    imageQuality: 'minimal',
                                    videoQuality: 'audio-only',
                                    prefetchEnabled: false,
                                    backgroundSyncEnabled: false,
                                    maxConcurrentRequests: 1
                                };
                                break;
                        }
                        
                        // Override for data saver mode
                        if (saveData) {
                            this.adaptiveSettings.imageQuality = 'minimal';
                            this.adaptiveSettings.videoQuality = 'audio-only';
                            this.adaptiveSettings.prefetchEnabled = false;
                            this.adaptiveSettings.backgroundSyncEnabled = false;
                        }
                        
                        return this.adaptiveSettings;
                    }
                    
                    async optimizeResourceLoading() {
                        const optimizations = {
                            applied: [],
                            resourcesOptimized: 0,
                            estimatedSavings: 0
                        };
                        
                        // Simulate resource optimization based on connection
                        if (this.adaptiveSettings.imageQuality !== 'high') {
                            optimizations.applied.push('image_compression');
                            optimizations.resourcesOptimized += 10;
                            optimizations.estimatedSavings += 50; // KB saved
                        }
                        
                        if (!this.adaptiveSettings.prefetchEnabled) {
                            optimizations.applied.push('disabled_prefetch');
                            optimizations.estimatedSavings += 200; // KB saved
                        }
                        
                        if (this.adaptiveSettings.maxConcurrentRequests < 4) {
                            optimizations.applied.push('reduced_concurrency');
                            optimizations.estimatedSavings += 30; // KB saved
                        }
                        
                        // Simulate applying optimizations
                        await new Promise(resolve => setTimeout(resolve, 100));
                        
                        return optimizations;
                    }
                }
                
                // Test connection quality adaptation
                const qualityManager = new ConnectionQualityManager();
                
                const testResults = {
                    initialConnection: qualityManager.connectionInfo,
                    speedTests: [],
                    adaptations: [],
                    optimizations: []
                };
                
                // Perform multiple speed tests and adaptations
                for (let test = 0; test < 3; test++) {
                    const speedResult = await qualityManager.measureConnectionSpeed();
                    testResults.speedTests.push({
                        test: test + 1,
                        metrics: speedResult
                    });
                    
                    const adaptedSettings = qualityManager.adaptToConnection();
                    testResults.adaptations.push({
                        test: test + 1,
                        settings: adaptedSettings
                    });
                    
                    const optimizationResult = await qualityManager.optimizeResourceLoading();
                    testResults.optimizations.push({
                        test: test + 1,
                        optimizations: optimizationResult
                    });
                    
                    // Simulate some variation in connection quality
                    if (test < 2) {
                        await new Promise(resolve => setTimeout(resolve, 200));
                    }
                }
                
                return {
                    testResults,
                    hasConnectionAPI: navigator.connection !== undefined,
                    finalQuality: qualityManager.qualityMetrics.quality,
                    finalSettings: qualityManager.adaptiveSettings,
                    summary: {
                        totalSpeedTests: testResults.speedTests.length,
                        qualityLevels: testResults.speedTests.map(t => t.metrics.quality),
                        totalOptimizations: testResults.optimizations.reduce((total, opt) => 
                            total + opt.optimizations.applied.length, 0
                        ),
                        estimatedTotalSavings: testResults.optimizations.reduce((total, opt) => 
                            total + opt.optimizations.estimatedSavings, 0
                        )
                    }
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify connection quality testing
        test_results = result['testResults']
        assert len(test_results['speedTests']) == 3
        assert len(test_results['adaptations']) == 3
        assert len(test_results['optimizations']) == 3
        
        # Verify summary metrics
        summary = result['summary']
        assert summary['totalSpeedTests'] == 3
        assert len(summary['qualityLevels']) == 3
        assert summary['totalOptimizations'] >= 0
        assert summary['estimatedTotalSavings'] >= 0
        
        # Verify quality levels are valid
        valid_qualities = ['excellent', 'good', 'fair', 'poor', 'unknown', 'error']
        for quality in summary['qualityLevels']:
            assert quality in valid_qualities

    # Error Recovery and Graceful Degradation
    
    @pytest.mark.asyncio
    async def test_request_retry_strategies(self, base_url):
        """Test various request retry strategies and error recovery."""
        content = await get(
            f"{base_url}/vue/",
            script="""
                // Comprehensive retry strategy testing
                class RetryStrategy {
                    constructor(name, config) {
                        this.name = name;
                        this.config = config;
                        this.attempts = [];
                    }
                    
                    async execute(operation) {
                        const { maxRetries, baseDelay, maxDelay, backoffFactor } = this.config;
                        
                        for (let attempt = 0; attempt < maxRetries; attempt++) {
                            const attemptStart = Date.now();
                            
                            try {
                                const result = await operation(attempt);
                                const attemptEnd = Date.now();
                                
                                this.attempts.push({
                                    attempt: attempt + 1,
                                    success: true,
                                    duration: attemptEnd - attemptStart,
                                    result
                                });
                                
                                return { success: true, result, attempts: this.attempts };
                            } catch (error) {
                                const attemptEnd = Date.now();
                                
                                this.attempts.push({
                                    attempt: attempt + 1,
                                    success: false,
                                    duration: attemptEnd - attemptStart,
                                    error: error.message
                                });
                                
                                if (attempt < maxRetries - 1) {
                                    const delay = this.calculateDelay(attempt, baseDelay, maxDelay, backoffFactor);
                                    await new Promise(resolve => setTimeout(resolve, delay));
                                }
                            }
                        }
                        
                        return { success: false, attempts: this.attempts };
                    }
                    
                    calculateDelay(attempt, baseDelay, maxDelay, backoffFactor) {
                        let delay;
                        
                        switch (this.name) {
                            case 'exponential':
                                delay = baseDelay * Math.pow(backoffFactor, attempt);
                                break;
                            case 'linear':
                                delay = baseDelay + (attempt * baseDelay);
                                break;
                            case 'fixed':
                                delay = baseDelay;
                                break;
                            case 'jittered':
                                const baseExponential = baseDelay * Math.pow(backoffFactor, attempt);
                                delay = baseExponential + (Math.random() * baseExponential * 0.1);
                                break;
                            default:
                                delay = baseDelay;
                        }
                        
                        return Math.min(delay, maxDelay);
                    }
                }
                
                // Test different retry strategies
                const strategies = [
                    new RetryStrategy('exponential', {
                        maxRetries: 3,
                        baseDelay: 100,
                        maxDelay: 5000,
                        backoffFactor: 2
                    }),
                    new RetryStrategy('linear', {
                        maxRetries: 3,
                        baseDelay: 200,
                        maxDelay: 5000,
                        backoffFactor: 1
                    }),
                    new RetryStrategy('fixed', {
                        maxRetries: 4,
                        baseDelay: 150,
                        maxDelay: 1000,
                        backoffFactor: 1
                    }),
                    new RetryStrategy('jittered', {
                        maxRetries: 3,
                        baseDelay: 100,
                        maxDelay: 3000,
                        backoffFactor: 1.5
                    })
                ];
                
                const strategyResults = [];
                
                for (const strategy of strategies) {
                    // Test with different failure scenarios
                    
                    // Scenario 1: Eventually succeeds
                    const eventualSuccess = await strategy.execute(async (attempt) => {
                        if (attempt < 2) {
                            throw new Error('Simulated failure');
                        }
                        return { data: 'success', attempt: attempt + 1 };
                    });
                    
                    // Reset attempts for next test
                    strategy.attempts = [];
                    
                    // Scenario 2: Always fails
                    const alwaysFails = await strategy.execute(async (attempt) => {
                        throw new Error('Persistent failure');
                    });
                    
                    strategyResults.push({
                        strategy: strategy.name,
                        config: strategy.config,
                        eventualSuccess: {
                            success: eventualSuccess.success,
                            attempts: eventualSuccess.attempts.length,
                            totalTime: eventualSuccess.attempts.reduce((sum, a) => sum + a.duration, 0)
                        },
                        alwaysFails: {
                            success: alwaysFails.success,
                            attempts: alwaysFails.attempts.length,
                            totalTime: alwaysFails.attempts.reduce((sum, a) => sum + a.duration, 0)
                        }
                    });
                }
                
                // Test request timeout scenarios
                const timeoutTests = [];
                
                const timeoutScenarios = [
                    { name: 'fast_timeout', timeout: 100, expectedResult: 'timeout' },
                    { name: 'normal_timeout', timeout: 1000, expectedResult: 'success' },
                    { name: 'slow_timeout', timeout: 5000, expectedResult: 'success' }
                ];
                
                for (const scenario of timeoutScenarios) {
                    const timeoutStart = Date.now();
                    
                    try {
                        const timeoutPromise = new Promise((_, reject) => {
                            setTimeout(() => reject(new Error('Timeout')), scenario.timeout);
                        });
                        
                        const operationPromise = new Promise(resolve => {
                            setTimeout(() => resolve({ data: 'completed' }), 500);
                        });
                        
                        const result = await Promise.race([timeoutPromise, operationPromise]);
                        const timeoutEnd = Date.now();
                        
                        timeoutTests.push({
                            scenario: scenario.name,
                            expectedResult: scenario.expectedResult,
                            actualResult: 'success',
                            duration: timeoutEnd - timeoutStart,
                            success: true
                        });
                    } catch (error) {
                        const timeoutEnd = Date.now();
                        
                        timeoutTests.push({
                            scenario: scenario.name,
                            expectedResult: scenario.expectedResult,
                            actualResult: 'timeout',
                            duration: timeoutEnd - timeoutStart,
                            success: false,
                            error: error.message
                        });
                    }
                }
                
                return {
                    strategyResults,
                    timeoutTests,
                    summary: {
                        strategiesTested: strategyResults.length,
                        successfulStrategies: strategyResults.filter(s => s.eventualSuccess.success).length,
                        timeoutScenarios: timeoutTests.length,
                        timeoutBehaviorCorrect: timeoutTests.every(t => 
                            t.expectedResult === t.actualResult || 
                            (t.expectedResult === 'success' && t.actualResult === 'success')
                        )
                    }
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify retry strategies
        strategy_results = result['strategyResults']
        assert len(strategy_results) == 4
        
        strategy_names = [s['strategy'] for s in strategy_results]
        expected_strategies = ['exponential', 'linear', 'fixed', 'jittered']
        for expected in expected_strategies:
            assert expected in strategy_names
        
        # Verify timeout tests
        timeout_tests = result['timeoutTests']
        assert len(timeout_tests) == 3
        
        # Verify summary
        summary = result['summary']
        assert summary['strategiesTested'] == 4
        assert summary['successfulStrategies'] >= 0
        assert summary['timeoutScenarios'] == 3


class TestNetworkErrorHandling:
    """Test comprehensive network error handling scenarios."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8083"
    
    @pytest.mark.asyncio
    async def test_comprehensive_error_recovery(self, base_url):
        """Test comprehensive error handling and recovery mechanisms."""
        content = await get(
            f"{base_url}/angular/",
            script="""
                // Comprehensive error handling system
                class NetworkErrorHandler {
                    constructor() {
                        this.errorCounts = new Map();
                        this.recoveryStrategies = new Map();
                        this.errorLog = [];
                        this.setupRecoveryStrategies();
                    }
                    
                    setupRecoveryStrategies() {
                        this.recoveryStrategies.set('NETWORK_ERROR', {
                            strategy: 'retry_with_backoff',
                            maxRetries: 3,
                            baseDelay: 1000
                        });
                        
                        this.recoveryStrategies.set('TIMEOUT_ERROR', {
                            strategy: 'increase_timeout_and_retry',
                            maxRetries: 2,
                            timeoutMultiplier: 2
                        });
                        
                        this.recoveryStrategies.set('SERVER_ERROR', {
                            strategy: 'fallback_to_cache',
                            maxRetries: 1,
                            fallbackDelay: 500
                        });
                        
                        this.recoveryStrategies.set('CLIENT_ERROR', {
                            strategy: 'validate_and_retry',
                            maxRetries: 1,
                            validationRequired: true
                        });
                    }
                    
                    classifyError(error) {
                        const message = error.message.toLowerCase();
                        
                        if (message.includes('network') || message.includes('fetch')) {
                            return 'NETWORK_ERROR';
                        } else if (message.includes('timeout')) {
                            return 'TIMEOUT_ERROR';
                        } else if (message.includes('server') || message.includes('5')) {
                            return 'SERVER_ERROR';
                        } else if (message.includes('client') || message.includes('4')) {
                            return 'CLIENT_ERROR';
                        } else {
                            return 'UNKNOWN_ERROR';
                        }
                    }
                    
                    async handleError(error, context = {}) {
                        const errorType = this.classifyError(error);
                        const timestamp = Date.now();
                        
                        // Log error
                        this.errorLog.push({
                            timestamp,
                            type: errorType,
                            message: error.message,
                            context,
                            stack: error.stack
                        });
                        
                        // Update error counts
                        const currentCount = this.errorCounts.get(errorType) || 0;
                        this.errorCounts.set(errorType, currentCount + 1);
                        
                        // Get recovery strategy
                        const strategy = this.recoveryStrategies.get(errorType);
                        
                        if (!strategy) {
                            return { recovered: false, strategy: 'no_strategy' };
                        }
                        
                        // Attempt recovery
                        return await this.executeRecoveryStrategy(strategy, error, context);
                    }
                    
                    async executeRecoveryStrategy(strategy, error, context) {
                        const recoveryStart = Date.now();
                        
                        try {
                            switch (strategy.strategy) {
                                case 'retry_with_backoff':
                                    return await this.retryWithBackoff(strategy, context);
                                    
                                case 'increase_timeout_and_retry':
                                    return await this.increaseTimeoutAndRetry(strategy, context);
                                    
                                case 'fallback_to_cache':
                                    return await this.fallbackToCache(strategy, context);
                                    
                                case 'validate_and_retry':
                                    return await this.validateAndRetry(strategy, context);
                                    
                                default:
                                    return { recovered: false, strategy: 'unknown_strategy' };
                            }
                        } catch (recoveryError) {
                            const recoveryEnd = Date.now();
                            
                            return {
                                recovered: false,
                                strategy: strategy.strategy,
                                recoveryError: recoveryError.message,
                                recoveryTime: recoveryEnd - recoveryStart
                            };
                        }
                    }
                    
                    async retryWithBackoff(strategy, context) {
                        for (let attempt = 0; attempt < strategy.maxRetries; attempt++) {
                            const delay = strategy.baseDelay * Math.pow(2, attempt);
                            await new Promise(resolve => setTimeout(resolve, delay));
                            
                            try {
                                // Simulate retry operation
                                const success = Math.random() > 0.3; // 70% success rate
                                if (success) {
                                    return {
                                        recovered: true,
                                        strategy: 'retry_with_backoff',
                                        attempts: attempt + 1,
                                        totalDelay: strategy.baseDelay * (Math.pow(2, attempt + 1) - 1)
                                    };
                                }
                            } catch (retryError) {
                                // Continue to next attempt
                            }
                        }
                        
                        return { recovered: false, strategy: 'retry_with_backoff', maxAttemptsReached: true };
                    }
                    
                    async increaseTimeoutAndRetry(strategy, context) {
                        const originalTimeout = context.timeout || 5000;
                        const newTimeout = originalTimeout * strategy.timeoutMultiplier;
                        
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                        // Simulate retry with increased timeout
                        const success = newTimeout > 8000; // Succeed if timeout is generous enough
                        
                        return {
                            recovered: success,
                            strategy: 'increase_timeout_and_retry',
                            originalTimeout,
                            newTimeout,
                            timeoutIncreased: true
                        };
                    }
                    
                    async fallbackToCache(strategy, context) {
                        await new Promise(resolve => setTimeout(resolve, strategy.fallbackDelay));
                        
                        // Simulate cache lookup
                        const cacheData = {
                            data: 'cached_response',
                            timestamp: Date.now() - 300000, // 5 minutes old
                            source: 'cache'
                        };
                        
                        return {
                            recovered: true,
                            strategy: 'fallback_to_cache',
                            cacheData,
                            isStale: Date.now() - cacheData.timestamp > 60000
                        };
                    }
                    
                    async validateAndRetry(strategy, context) {
                        // Simulate validation
                        await new Promise(resolve => setTimeout(resolve, 200));
                        
                        const validationPassed = context.data ? Object.keys(context.data).length > 0 : false;
                        
                        if (validationPassed) {
                            return {
                                recovered: true,
                                strategy: 'validate_and_retry',
                                validationPassed: true,
                                retryAttempted: true
                            };
                        } else {
                            return {
                                recovered: false,
                                strategy: 'validate_and_retry',
                                validationPassed: false,
                                retryAttempted: false
                            };
                        }
                    }
                    
                    getErrorSummary() {
                        return {
                            totalErrors: this.errorLog.length,
                            errorsByType: Object.fromEntries(this.errorCounts),
                            recentErrors: this.errorLog.slice(-5),
                            errorRate: this.errorLog.length / Math.max(1, Date.now() / 1000 / 60) // errors per minute
                        };
                    }
                }
                
                // Test comprehensive error handling
                const errorHandler = new NetworkErrorHandler();
                const testResults = [];
                
                // Test different error types
                const errorScenarios = [
                    { type: 'network', error: new Error('Network request failed'), context: { url: '/api/data' } },
                    { type: 'timeout', error: new Error('Request timeout'), context: { timeout: 3000 } },
                    { type: 'server', error: new Error('Server error 500'), context: { status: 500 } },
                    { type: 'client', error: new Error('Client error 400'), context: { data: { valid: true } } },
                    { type: 'unknown', error: new Error('Unknown error occurred'), context: {} }
                ];
                
                for (const scenario of errorScenarios) {
                    const result = await errorHandler.handleError(scenario.error, scenario.context);
                    testResults.push({
                        scenarioType: scenario.type,
                        errorMessage: scenario.error.message,
                        recoveryResult: result
                    });
                }
                
                const errorSummary = errorHandler.getErrorSummary();
                
                return {
                    testResults,
                    errorSummary,
                    totalScenariosProcessed: testResults.length,
                    successfulRecoveries: testResults.filter(r => r.recoveryResult.recovered).length,
                    recoveryStrategiesUsed: [...new Set(testResults.map(r => r.recoveryResult.strategy))],
                    errorHandlerEffective: testResults.some(r => r.recoveryResult.recovered)
                };
            """
        )
        
        assert content.script_result is not None
        result = content.script_result
        
        # Verify comprehensive error handling
        assert result['totalScenariosProcessed'] == 5
        assert result['successfulRecoveries'] >= 0
        assert result['errorHandlerEffective'] is True
        
        # Verify error summary
        error_summary = result['errorSummary']
        assert error_summary['totalErrors'] == 5
        assert 'errorsByType' in error_summary
        assert len(error_summary['recentErrors']) <= 5
        
        # Verify test results
        test_results = result['testResults']
        assert len(test_results) == 5
        
        scenario_types = [r['scenarioType'] for r in test_results]
        expected_types = ['network', 'timeout', 'server', 'client', 'unknown']
        for expected in expected_types:
            assert expected in scenario_types
    
    @pytest.mark.asyncio
    async def test_network_resilience_integration(self, base_url):
        """Test integration of all network resilience features."""
        # Test multiple frameworks with network resilience
        framework_tests = []
        
        frameworks = ['react', 'vue', 'angular']
        
        for framework in frameworks:
            try:
                content = await get(
                    f"{base_url}/{framework}/",
                    script="""
                        // Test network resilience integration
                        const resilienceTest = {
                            framework: window.testData.framework,
                            networkFeatures: {
                                hasOnlineDetection: typeof navigator.onLine !== 'undefined',
                                hasConnectionAPI: typeof navigator.connection !== 'undefined',
                                hasServiceWorker: typeof navigator.serviceWorker !== 'undefined',
                                hasLocalStorage: typeof localStorage !== 'undefined',
                                hasFetch: typeof fetch !== 'undefined'
                            },
                            errorHandling: {
                                hasGlobalErrorHandler: typeof window.onerror !== 'undefined',
                                hasPromiseRejectionHandler: typeof window.addEventListener !== 'undefined',
                                canCatchErrors: true
                            },
                            performanceMetrics: {
                                hasPerformanceAPI: typeof performance !== 'undefined',
                                hasMemoryInfo: !!(performance.memory),
                                hasTiming: !!(performance.timing),
                                hasNavigation: !!(performance.navigation)
                            }
                        };
                        
                        // Test basic resilience functionality
                        try {
                            const basicTest = {
                                canHandlePromiseRejection: true,
                                canDetectOnlineStatus: navigator.onLine,
                                canStoreDataLocally: !!localStorage,
                                canMeasurePerformance: !!performance.now
                            };
                            
                            resilienceTest.basicTests = basicTest;
                            resilienceTest.testsPass = Object.values(basicTest).every(test => test === true);
                        } catch (error) {
                            resilienceTest.basicTestError = error.message;
                            resilienceTest.testsPass = false;
                        }
                        
                        return resilienceTest;
                    """,
                    config=BrowserConfig(timeout=10000)  # Extended timeout for resilience
                )
                
                if content.script_result:
                    framework_tests.append({
                        framework: framework,
                        result: content.script_result,
                        success: True
                    });
                    
            except Exception as e:
                framework_tests.append({
                    framework: framework,
                    error: str(e),
                    success: False
                })
        
        # Verify integration results
        assert len(framework_tests) >= 2  # At least 2 frameworks should work
        
        successful_tests = [t for t in framework_tests if t['success']]
        assert len(successful_tests) >= 2
        
        # Verify resilience features across frameworks
        for test in successful_tests:
            result = test['result']
            
            # Check network features
            assert result['networkFeatures']['hasOnlineDetection'] is True
            assert result['networkFeatures']['hasLocalStorage'] is True
            assert result['networkFeatures']['hasFetch'] is True
            
            # Check error handling
            assert result['errorHandling']['hasGlobalErrorHandler'] is True
            assert result['errorHandling']['canCatchErrors'] is True
            
            # Check performance monitoring
            assert result['performanceMetrics']['hasPerformanceAPI'] is True


<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Add modern framework integration tests (React/Vue/Angular)", "status": "completed", "activeForm": "Adding modern framework integration tests"}, {"content": "Create React demo page with component interactions", "status": "completed", "activeForm": "Creating React demo page with component interactions"}, {"content": "Create Vue demo page with reactive data", "status": "completed", "activeForm": "Creating Vue demo page with reactive data"}, {"content": "Create Angular demo page with TypeScript features", "status": "completed", "activeForm": "Creating Angular demo page with TypeScript features"}, {"content": "Build comprehensive framework integration test suite", "status": "completed", "activeForm": "Building comprehensive framework integration test suite"}, {"content": "Create mobile browser compatibility test suite", "status": "completed", "activeForm": "Creating mobile browser compatibility test suite"}, {"content": "Build advanced user interaction workflow tests", "status": "completed", "activeForm": "Building advanced user interaction workflow tests"}, {"content": "Implement network resilience and recovery tests", "status": "completed", "activeForm": "Implementing network resilience and recovery tests"}]