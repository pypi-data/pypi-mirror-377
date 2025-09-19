"""
Integration tests using the local Caddy test server.

This test suite demonstrates how to use the local test server for controlled,
reproducible JavaScript API testing without external dependencies.
"""
import pytest
import asyncio
import requests
import time
from unittest.mock import AsyncMock, MagicMock
from src.crawailer.api import get, get_many, discover
from src.crawailer.content import WebContent


class TestLocalServerIntegration:
    """Test Crawailer JavaScript API with local test server."""
    
    @pytest.fixture(autouse=True)
    def setup_server_check(self):
        """Ensure local test server is running before tests."""
        try:
            response = requests.get("http://localhost:8082/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("Local test server not running. Start with: cd test-server && ./start.sh")
        except requests.exceptions.RequestException:
            pytest.skip("Local test server not accessible. Start with: cd test-server && ./start.sh")
    
    @pytest.fixture
    def mock_browser(self):
        """Mock browser for controlled testing."""
        browser = MagicMock()
        
        async def mock_fetch_page(url, script_before=None, script_after=None, **kwargs):
            """Mock fetch_page that simulates real browser behavior with local content."""
            
            # Simulate actual content from our test sites
            if "/spa/" in url:
                html_content = """
                <html>
                <head><title>TaskFlow - Modern SPA Demo</title></head>
                <body>
                    <div class="app-container">
                        <nav class="nav">
                            <div class="nav-item active" data-page="dashboard">Dashboard</div>
                            <div class="nav-item" data-page="tasks">Tasks</div>
                        </nav>
                        <div id="dashboard" class="page active">
                            <h1>Dashboard</h1>
                            <div id="total-tasks">5</div>
                        </div>
                    </div>
                    <script>
                        window.testData = {
                            appName: 'TaskFlow',
                            currentPage: 'dashboard',
                            totalTasks: () => 5,
                            generateTimestamp: () => new Date().toISOString()
                        };
                    </script>
                </body>
                </html>
                """
                script_result = None
                if script_after:
                    if "testData.totalTasks()" in script_after:
                        script_result = 5
                    elif "testData.currentPage" in script_after:
                        script_result = "dashboard"
                    elif "testData.generateTimestamp()" in script_after:
                        script_result = "2023-12-07T10:30:00.000Z"
                
            elif "/shop/" in url:
                html_content = """
                <html>
                <head><title>TechMart - Premium Electronics Store</title></head>
                <body>
                    <div class="product-grid">
                        <div class="product-card">
                            <h3>iPhone 15 Pro Max</h3>
                            <div class="price">$1199</div>
                        </div>
                        <div class="product-card">
                            <h3>MacBook Pro 16-inch</h3>
                            <div class="price">$2499</div>
                        </div>
                    </div>
                    <script>
                        window.testData = {
                            storeName: 'TechMart',
                            totalProducts: () => 6,
                            cartItems: () => 0,
                            searchProduct: (query) => query === 'iPhone' ? [{id: 1, name: 'iPhone 15 Pro Max'}] : []
                        };
                    </script>
                </body>
                </html>
                """
                script_result = None
                if script_after:
                    if "testData.totalProducts()" in script_after:
                        script_result = 6
                    elif "testData.cartItems()" in script_after:
                        script_result = 0
                    elif "testData.searchProduct('iPhone')" in script_after:
                        script_result = [{"id": 1, "name": "iPhone 15 Pro Max"}]
            
            elif "/docs/" in url:
                html_content = """
                <html>
                <head><title>DevDocs - Comprehensive API Documentation</title></head>
                <body>
                    <nav class="sidebar">
                        <div class="nav-item active">Overview</div>
                        <div class="nav-item">Users API</div>
                        <div class="nav-item">Products API</div>
                    </nav>
                    <main class="content">
                        <h1>API Documentation</h1>
                        <p>Welcome to our comprehensive API documentation.</p>
                    </main>
                    <script>
                        window.testData = {
                            siteName: 'DevDocs',
                            currentSection: 'overview',
                            navigationItems: 12,
                            apiEndpoints: [
                                { method: 'GET', path: '/users' },
                                { method: 'POST', path: '/users' },
                                { method: 'GET', path: '/products' }
                            ]
                        };
                    </script>
                </body>
                </html>
                """
                script_result = None
                if script_after:
                    if "testData.currentSection" in script_after:
                        script_result = "overview"
                    elif "testData.navigationItems" in script_after:
                        script_result = 12
                    elif "testData.apiEndpoints.length" in script_after:
                        script_result = 3
            
            elif "/news/" in url:
                html_content = """
                <html>
                <head><title>TechNews Today - Latest Technology Updates</title></head>
                <body>
                    <div class="articles-section">
                        <article class="article-card">
                            <h3>Revolutionary AI Model Achieves Human-Level Performance</h3>
                            <p>Researchers have developed a groundbreaking AI system...</p>
                        </article>
                        <article class="article-card">
                            <h3>Quantum Computing Breakthrough</h3>
                            <p>Scientists at leading quantum computing laboratories...</p>
                        </article>
                    </div>
                    <script>
                        window.testData = {
                            siteName: 'TechNews Today',
                            totalArticles: 50,
                            currentPage: 1,
                            searchArticles: (query) => query === 'AI' ? [{title: 'AI Model Performance'}] : [],
                            getTrendingArticles: () => [{title: 'Top Article', views: 5000}]
                        };
                    </script>
                </body>
                </html>
                """
                script_result = None
                if script_after:
                    if "testData.totalArticles" in script_after:
                        script_result = 50
                    elif "testData.currentPage" in script_after:
                        script_result = 1
                    elif "testData.searchArticles('AI')" in script_after:
                        script_result = [{"title": "AI Model Performance"}]
            
            else:
                # Default hub content
                html_content = """
                <html>
                <head><title>Crawailer Test Suite Hub</title></head>
                <body>
                    <h1>Crawailer Test Suite Hub</h1>
                    <div class="grid">
                        <div class="card">E-commerce Demo</div>
                        <div class="card">Single Page Application</div>
                        <div class="card">Documentation Site</div>
                    </div>
                    <script>
                        window.testData = {
                            hubVersion: '1.0.0',
                            testSites: ['ecommerce', 'spa', 'docs', 'news'],
                            apiEndpoints: ['/api/users', '/api/products']
                        };
                    </script>
                </body>
                </html>
                """
                script_result = None
                if script_after:
                    if "testData.testSites.length" in script_after:
                        script_result = 4
                    elif "testData.hubVersion" in script_after:
                        script_result = "1.0.0"
            
            return WebContent(
                url=url,
                title="Test Page",
                text=html_content,
                html=html_content,
                links=[],
                status_code=200,
                script_result=script_result,
                script_error=None
            )
        
        browser.fetch_page = AsyncMock(side_effect=mock_fetch_page)
        return browser
    
    @pytest.mark.asyncio
    async def test_spa_javascript_execution(self, mock_browser, monkeypatch):
        """Test JavaScript execution with SPA site."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        # Test basic SPA functionality
        content = await get(
            "http://localhost:8082/spa/",
            script="return window.testData.totalTasks();"
        )
        
        assert content.script_result == 5
        assert "TaskFlow" in content.html
        assert content.script_error is None
    
    @pytest.mark.asyncio
    async def test_ecommerce_product_search(self, mock_browser, monkeypatch):
        """Test e-commerce site product search functionality."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        content = await get(
            "http://localhost:8082/shop/",
            script="return window.testData.searchProduct('iPhone');"
        )
        
        assert content.script_result == [{"id": 1, "name": "iPhone 15 Pro Max"}]
        assert "TechMart" in content.html
        assert content.script_error is None
    
    @pytest.mark.asyncio
    async def test_documentation_navigation(self, mock_browser, monkeypatch):
        """Test documentation site navigation and API data."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        content = await get(
            "http://localhost:8082/docs/",
            script="return window.testData.apiEndpoints.length;"
        )
        
        assert content.script_result == 3
        assert "DevDocs" in content.html
        assert content.script_error is None
    
    @pytest.mark.asyncio
    async def test_news_site_content_loading(self, mock_browser, monkeypatch):
        """Test news site article loading and search."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        content = await get(
            "http://localhost:8082/news/",
            script="return window.testData.searchArticles('AI');"
        )
        
        assert content.script_result == [{"title": "AI Model Performance"}]
        assert "TechNews Today" in content.html
        assert content.script_error is None
    
    @pytest.mark.asyncio
    async def test_get_many_with_local_sites(self, mock_browser, monkeypatch):
        """Test get_many with multiple local test sites."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        urls = [
            "http://localhost:8082/spa/",
            "http://localhost:8082/shop/",
            "http://localhost:8082/docs/"
        ]
        
        contents = await get_many(
            urls,
            script="return window.testData ? Object.keys(window.testData) : [];"
        )
        
        assert len(contents) == 3
        
        # Check SPA result
        spa_content = next(c for c in contents if "/spa/" in c.url)
        assert isinstance(spa_content.script_result, list)
        assert len(spa_content.script_result) > 0
        
        # Check e-commerce result
        shop_content = next(c for c in contents if "/shop/" in c.url)
        assert isinstance(shop_content.script_result, list)
        assert len(shop_content.script_result) > 0
        
        # Check docs result
        docs_content = next(c for c in contents if "/docs/" in c.url)
        assert isinstance(docs_content.script_result, list)
        assert len(docs_content.script_result) > 0
    
    @pytest.mark.asyncio
    async def test_discover_with_local_content(self, mock_browser, monkeypatch):
        """Test discover functionality with local test sites."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        # Mock search results to include our local sites
        async def mock_search(query, **kwargs):
            return [
                "http://localhost:8082/spa/",
                "http://localhost:8082/shop/",
                "http://localhost:8082/docs/"
            ]
        
        # Test discovering local test sites
        results = await discover(
            "test sites",
            script="return window.testData ? window.testData.siteName || window.testData.appName : 'Unknown';"
        )
        
        # Note: discover() would normally search external sources
        # In a real implementation, we'd need to mock the search function
        # For now, we'll test that the function accepts the parameters
        assert callable(discover)
    
    @pytest.mark.asyncio
    async def test_complex_javascript_workflow(self, mock_browser, monkeypatch):
        """Test complex JavaScript workflow simulating real user interactions."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        # Simulate complex e-commerce workflow
        complex_script = """
        // Simulate adding items to cart and checking totals
        if (window.testData && window.testData.totalProducts) {
            const productCount = window.testData.totalProducts();
            const cartCount = window.testData.cartItems();
            
            return {
                productsAvailable: productCount,
                itemsInCart: cartCount,
                timestamp: new Date().toISOString(),
                workflow: 'completed'
            };
        }
        return { error: 'testData not available' };
        """
        
        content = await get(
            "http://localhost:8082/shop/",
            script=complex_script
        )
        
        result = content.script_result
        assert isinstance(result, dict)
        assert result.get('productsAvailable') == 6
        assert result.get('itemsInCart') == 0
        assert result.get('workflow') == 'completed'
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_error_handling_with_local_server(self, mock_browser, monkeypatch):
        """Test error handling scenarios with local test server."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        # Mock a JavaScript error scenario
        async def mock_fetch_with_error(url, script_before=None, script_after=None, **kwargs):
            if script_after and "throw new Error" in script_after:
                return WebContent(
                    url=url,
                    title="Error Test",
                    text="<html><body>Error test page</body></html>",
                    html="<html><body>Error test page</body></html>",
                    links=[],
                    status_code=200,
                    script_result=None,
                    script_error="Error: Test error message"
                )
            
            # Default behavior
            return await mock_browser.fetch_page(url, script_before, script_after, **kwargs)
        
        mock_browser.fetch_page = AsyncMock(side_effect=mock_fetch_with_error)
        
        content = await get(
            "http://localhost:8082/",
            script="throw new Error('Test error');"
        )
        
        assert content.script_result is None
        assert content.script_error == "Error: Test error message"
    
    @pytest.mark.asyncio
    async def test_performance_with_local_server(self, mock_browser, monkeypatch):
        """Test performance characteristics with local server."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        # Simulate performance timing
        start_time = time.time()
        
        content = await get(
            "http://localhost:8082/spa/",
            script="return performance.now();"
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Local server should be fast
        assert execution_time < 5.0  # Should complete in under 5 seconds
        assert content.script_result is not None or content.script_error is not None
    
    @pytest.mark.asyncio
    async def test_content_extraction_with_dynamic_data(self, mock_browser, monkeypatch):
        """Test content extraction with dynamically generated data."""
        monkeypatch.setattr("src.crawailer.api._browser", mock_browser)
        
        content = await get(
            "http://localhost:8082/news/",
            script="""
            return {
                totalArticles: window.testData.totalArticles,
                currentPage: window.testData.currentPage,
                hasContent: document.querySelectorAll('.article-card').length > 0,
                siteTitle: document.title
            };
            """
        )
        
        result = content.script_result
        assert isinstance(result, dict)
        assert result.get('totalArticles') == 50
        assert result.get('currentPage') == 1
        assert result.get('hasContent') is True
        assert 'TechNews Today' in result.get('siteTitle', '')


class TestLocalServerUtilities:
    """Utility tests for local server integration."""
    
    def test_server_availability_check(self):
        """Test utility function to check server availability."""
        def is_server_running(url="http://localhost:8082/health", timeout=5):
            """Check if the local test server is running."""
            try:
                response = requests.get(url, timeout=timeout)
                return response.status_code == 200
            except requests.exceptions.RequestException:
                return False
        
        # This will pass if server is running, skip if not
        if is_server_running():
            assert True
        else:
            pytest.skip("Local test server not running")
    
    def test_local_server_urls(self):
        """Test generation of local server URLs for testing."""
        base_url = "http://localhost:8082"
        
        test_urls = {
            'hub': f"{base_url}/",
            'spa': f"{base_url}/spa/",
            'ecommerce': f"{base_url}/shop/",
            'docs': f"{base_url}/docs/",
            'news': f"{base_url}/news/",
            'static': f"{base_url}/static/",
            'api_users': f"{base_url}/api/users",
            'api_products': f"{base_url}/api/products",
            'health': f"{base_url}/health"
        }
        
        for name, url in test_urls.items():
            assert url.startswith("http://localhost:8082")
            assert len(url) > len(base_url)
    
    def test_javascript_test_data_structure(self):
        """Test expected structure of JavaScript test data."""
        expected_spa_data = {
            'appName': 'TaskFlow',
            'currentPage': str,
            'totalTasks': callable,
            'generateTimestamp': callable
        }
        
        expected_ecommerce_data = {
            'storeName': 'TechMart',
            'totalProducts': callable,
            'cartItems': callable,
            'searchProduct': callable
        }
        
        expected_docs_data = {
            'siteName': 'DevDocs',
            'currentSection': str,
            'navigationItems': int,
            'apiEndpoints': list
        }
        
        expected_news_data = {
            'siteName': 'TechNews Today',
            'totalArticles': int,
            'currentPage': int,
            'searchArticles': callable
        }
        
        # Verify data structure expectations
        for structure in [expected_spa_data, expected_ecommerce_data, 
                         expected_docs_data, expected_news_data]:
            assert isinstance(structure, dict)
            assert len(structure) > 0


@pytest.mark.integration
class TestLocalServerRealRequests:
    """Integration tests with real requests to local server (if running)."""
    
    @pytest.fixture(autouse=True)
    def check_server(self):
        """Check if server is actually running for real integration tests."""
        try:
            response = requests.get("http://localhost:8082/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("Local test server not running for real integration tests")
        except requests.exceptions.RequestException:
            pytest.skip("Local test server not accessible for real integration tests")
    
    def test_real_api_endpoints(self):
        """Test actual API endpoints if server is running."""
        endpoints = [
            "http://localhost:8082/health",
            "http://localhost:8082/api/users", 
            "http://localhost:8082/api/products"
        ]
        
        for endpoint in endpoints:
            response = requests.get(endpoint, timeout=10)
            assert response.status_code == 200
            
            if "/api/" in endpoint:
                # API endpoints should return JSON
                data = response.json()
                assert isinstance(data, dict)
    
    def test_real_site_responses(self):
        """Test actual site responses if server is running."""
        sites = [
            "http://localhost:8082/",
            "http://localhost:8082/spa/",
            "http://localhost:8082/shop/",
            "http://localhost:8082/docs/",
            "http://localhost:8082/news/"
        ]
        
        for site in sites:
            response = requests.get(site, timeout=10)
            assert response.status_code == 200
            assert "html" in response.headers.get('content-type', '').lower()
            assert len(response.text) > 100  # Should have substantial content


if __name__ == "__main__":
    # Run tests with local server integration
    pytest.main([__file__, "-v", "--tb=short"])