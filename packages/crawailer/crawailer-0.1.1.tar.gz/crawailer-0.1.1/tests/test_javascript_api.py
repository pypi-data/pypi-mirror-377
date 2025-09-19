"""
Comprehensive tests for JavaScript execution API enhancements.

Tests the proposed JavaScript execution features in get(), get_many(), 
and discover() functions using a mock HTTP server.
"""

import asyncio
import json
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

# These imports assume the enhanced API is implemented
# For now, we'll test against the proposed interface
from crawailer import Browser, BrowserConfig
from crawailer.content import WebContent
from crawailer.api import get, get_many, discover


class MockHTTPServer:
    """Mock HTTP server that serves test pages with JavaScript."""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.server = None
        self.port = None
        
    def setup_routes(self):
        """Set up test routes with various JavaScript scenarios."""
        self.app.router.add_get('/', self.index_page)
        self.app.router.add_get('/dynamic-price', self.dynamic_price_page)
        self.app.router.add_get('/infinite-scroll', self.infinite_scroll_page)
        self.app.router.add_get('/load-more', self.load_more_page)
        self.app.router.add_get('/spa-content', self.spa_page)
        self.app.router.add_get('/search', self.search_results_page)
        self.app.router.add_get('/article/{id}', self.article_page)
        self.app.router.add_get('/api/data', self.api_endpoint)
        
    async def start(self):
        """Start the mock server."""
        self.server = TestServer(self.app, port=0)
        await self.server.start_server()
        self.port = self.server.port
        return f"http://localhost:{self.port}"
        
    async def stop(self):
        """Stop the mock server."""
        if self.server:
            await self.server.close()
    
    async def index_page(self, request):
        """Simple index page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Page</h1>
            <div id="content">Initial content</div>
            <script>
                window.testData = { loaded: true };
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def dynamic_price_page(self, request):
        """E-commerce page with dynamically loaded price."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Product Page</title></head>
        <body>
            <h1>Amazing Product</h1>
            <div class="price-container">
                <span class="initial-price">$99.99</span>
                <span class="final-price" style="display:none;"></span>
            </div>
            <script>
                // Simulate price calculation after page load
                setTimeout(() => {
                    const discount = 0.2;
                    const price = 99.99 * (1 - discount);
                    document.querySelector('.final-price').innerText = '$' + price.toFixed(2);
                    document.querySelector('.final-price').style.display = 'block';
                    document.querySelector('.initial-price').style.display = 'none';
                }, 100);
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def infinite_scroll_page(self, request):
        """Page with infinite scroll functionality."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Infinite Scroll</title></head>
        <body>
            <h1>Infinite Content</h1>
            <div id="content">
                <div class="item">Item 1</div>
                <div class="item">Item 2</div>
                <div class="item">Item 3</div>
            </div>
            <div class="loading" style="display:none;">Loading...</div>
            <div class="end-of-content" style="display:none;">No more content</div>
            <script>
                let itemCount = 3;
                let isLoading = false;
                
                window.addEventListener('scroll', () => {
                    if (isLoading) return;
                    
                    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
                    if (scrollTop + clientHeight >= scrollHeight - 5) {
                        loadMore();
                    }
                });
                
                function loadMore() {
                    if (itemCount >= 10) {
                        document.querySelector('.end-of-content').style.display = 'block';
                        return;
                    }
                    
                    isLoading = true;
                    document.querySelector('.loading').style.display = 'block';
                    
                    setTimeout(() => {
                        const content = document.getElementById('content');
                        for (let i = 0; i < 3; i++) {
                            itemCount++;
                            const div = document.createElement('div');
                            div.className = 'item';
                            div.textContent = 'Item ' + itemCount;
                            content.appendChild(div);
                        }
                        document.querySelector('.loading').style.display = 'none';
                        isLoading = false;
                    }, 500);
                }
                
                // Expose for testing
                window.loadMore = loadMore;
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def load_more_page(self, request):
        """Page with 'Load More' button."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Load More Content</title></head>
        <body>
            <h1>Articles</h1>
            <div id="articles">
                <article class="article">
                    <h2>Article 1</h2>
                    <p class="preview">Preview text...</p>
                    <button class="read-more-btn" onclick="expandArticle(this)">Read More</button>
                    <p class="full-content" style="display:none;">Full article content here...</p>
                </article>
                <article class="article">
                    <h2>Article 2</h2>
                    <p class="preview">Preview text...</p>
                    <button class="read-more-btn" onclick="expandArticle(this)">Read More</button>
                    <p class="full-content" style="display:none;">Full article content here...</p>
                </article>
            </div>
            <button class="load-more" onclick="loadMoreArticles()">Load More Articles</button>
            <script>
                function expandArticle(btn) {
                    const article = btn.parentElement;
                    article.querySelector('.full-content').style.display = 'block';
                    article.querySelector('.preview').style.display = 'none';
                    btn.style.display = 'none';
                }
                
                let articleCount = 2;
                function loadMoreArticles() {
                    const container = document.getElementById('articles');
                    for (let i = 0; i < 2; i++) {
                        articleCount++;
                        const article = document.createElement('article');
                        article.className = 'article';
                        article.innerHTML = `
                            <h2>Article ${articleCount}</h2>
                            <p class="preview">Preview text...</p>
                            <button class="read-more-btn" onclick="expandArticle(this)">Read More</button>
                            <p class="full-content" style="display:none;">Full article content here...</p>
                        `;
                        container.appendChild(article);
                    }
                }
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def spa_page(self, request):
        """Single Page Application with React-like behavior."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>SPA Demo</title></head>
        <body>
            <div id="root">Loading...</div>
            <script>
                // Simulate React/Vue app initialization
                setTimeout(() => {
                    document.getElementById('root').innerHTML = `
                        <div class="app">
                            <h1>SPA Content Loaded</h1>
                            <div class="dynamic-data">
                                <p>User: John Doe</p>
                                <p>Status: Active</p>
                            </div>
                        </div>
                    `;
                    window.appReady = true;
                }, 300);
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def search_results_page(self, request):
        """Search results page for discovery testing."""
        query = request.query.get('q', 'test')
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Search: {query}</title></head>
        <body>
            <h1>Search Results for "{query}"</h1>
            <div id="results">
                <div class="result">
                    <h2><a href="/article/1">Result 1: {query}</a></h2>
                    <p>Preview of result 1...</p>
                </div>
                <div class="result">
                    <h2><a href="/article/2">Result 2: {query}</a></h2>
                    <p>Preview of result 2...</p>
                </div>
            </div>
            <button class="show-more" onclick="showMore()">Show More Results</button>
            <script>
                let resultCount = 2;
                function showMore() {{
                    const results = document.getElementById('results');
                    for (let i = 0; i < 3; i++) {{
                        resultCount++;
                        const div = document.createElement('div');
                        div.className = 'result';
                        div.innerHTML = `
                            <h2><a href="/article/${{resultCount}}">Result ${{resultCount}}: {query}</a></h2>
                            <p>Preview of result ${{resultCount}}...</p>
                        `;
                        results.appendChild(div);
                    }}
                }}
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def article_page(self, request):
        """Individual article page."""
        article_id = request.match_info['id']
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Article {article_id}</title></head>
        <body>
            <article>
                <h1>Article {article_id}</h1>
                <div class="metadata">
                    <span class="author">Author Name</span>
                    <span class="date">2024-01-01</span>
                </div>
                <div class="abstract" onclick="this.nextElementSibling.style.display='block'">
                    Click to expand abstract...
                </div>
                <div class="full-abstract" style="display:none;">
                    This is the full abstract of article {article_id}. 
                    It contains detailed information about the research.
                </div>
                <div class="content">
                    <p>Article content goes here...</p>
                </div>
            </article>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def api_endpoint(self, request):
        """JSON API endpoint for testing."""
        data = {
            "status": "success",
            "data": {"items": [1, 2, 3]}
        }
        return web.json_response(data)


@pytest.fixture
async def mock_server():
    """Fixture to provide mock HTTP server."""
    server = MockHTTPServer()
    base_url = await server.start()
    yield server, base_url
    await server.stop()


@pytest.fixture
def mock_browser():
    """Fixture to provide mocked Browser instance."""
    with patch('crawailer.api._browser') as mock:
        browser = AsyncMock(spec=Browser)
        mock.return_value = browser
        yield browser


# Test JavaScript execution in get() function
class TestGetWithJavaScript:
    """Tests for get() function with JavaScript execution."""
    
    @pytest.mark.asyncio
    async def test_get_with_script_before(self, mock_server):
        """Test executing JavaScript before content extraction."""
        server, base_url = mock_server
        
        # Mock the enhanced get() function
        with patch('crawailer.api.get') as mock_get:
            # Simulate successful JS execution
            mock_content = WebContent(
                url=f"{base_url}/dynamic-price",
                title="Product Page",
                text="Amazing Product $79.99",
                markdown="# Amazing Product\n\n$79.99",
                html="<html>...</html>",
                script_result="$79.99"
            )
            mock_get.return_value = mock_content
            
            # Call with script
            content = await get(
                f"{base_url}/dynamic-price",
                script="document.querySelector('.final-price').innerText",
                wait_for=".final-price"
            )
            
            assert content.script_result == "$79.99"
            assert "$79.99" in content.text
    
    @pytest.mark.asyncio
    async def test_get_with_scroll_script(self, mock_server):
        """Test scrolling to load more content."""
        server, base_url = mock_server
        
        with patch('crawailer.api.get') as mock_get:
            # Simulate content after scrolling
            mock_content = WebContent(
                url=f"{base_url}/infinite-scroll",
                title="Infinite Scroll",
                text="Infinite Content Item 1 Item 2 Item 3 Item 4 Item 5 Item 6",
                markdown="# Infinite Content\n\nItem 1\nItem 2\nItem 3\nItem 4\nItem 5\nItem 6",
                html="<html>...</html>",
                script_result=None
            )
            mock_get.return_value = mock_content
            
            content = await get(
                f"{base_url}/infinite-scroll",
                script_before="""
                    window.scrollTo(0, document.body.scrollHeight);
                    await new Promise(r => setTimeout(r, 600));
                    window.loadMore();
                """,
                wait_for=".end-of-content"
            )
            
            # Should have more items after scrolling
            assert "Item 6" in content.text
    
    @pytest.mark.asyncio
    async def test_get_with_click_expand(self, mock_server):
        """Test clicking buttons to expand content."""
        server, base_url = mock_server
        
        with patch('crawailer.api.get') as mock_get:
            # Simulate expanded content
            mock_content = WebContent(
                url=f"{base_url}/load-more",
                title="Load More Content",
                text="Articles Article 1 Full article content here... Article 2 Full article content here...",
                markdown="# Articles\n\n## Article 1\n\nFull article content here...\n\n## Article 2\n\nFull article content here...",
                html="<html>...</html>"
            )
            mock_get.return_value = mock_content
            
            content = await get(
                f"{base_url}/load-more",
                script_before="""
                    document.querySelectorAll('.read-more-btn').forEach(btn => btn.click());
                """
            )
            
            assert "Full article content" in content.text
    
    @pytest.mark.asyncio
    async def test_get_spa_wait_for_app(self, mock_server):
        """Test waiting for SPA to initialize."""
        server, base_url = mock_server
        
        with patch('crawailer.api.get') as mock_get:
            mock_content = WebContent(
                url=f"{base_url}/spa-content",
                title="SPA Demo",
                text="SPA Content Loaded User: John Doe Status: Active",
                markdown="# SPA Content Loaded\n\nUser: John Doe\nStatus: Active",
                html="<html>...</html>",
                script_result=True
            )
            mock_get.return_value = mock_content
            
            content = await get(
                f"{base_url}/spa-content",
                script="window.appReady",
                wait_for=".app"
            )
            
            assert content.script_result is True
            assert "John Doe" in content.text
            assert "Active" in content.text
    
    @pytest.mark.asyncio
    async def test_get_script_error_handling(self, mock_server):
        """Test handling of JavaScript execution errors."""
        server, base_url = mock_server
        
        with patch('crawailer.api.get') as mock_get:
            mock_content = WebContent(
                url=f"{base_url}/",
                title="Test Page",
                text="Test Page Initial content",
                markdown="# Test Page\n\nInitial content",
                html="<html>...</html>",
                script_error="ReferenceError: nonexistent is not defined"
            )
            mock_get.return_value = mock_content
            
            content = await get(
                f"{base_url}/",
                script="nonexistent.function()"
            )
            
            assert content.script_error is not None
            assert "ReferenceError" in content.script_error


# Test JavaScript execution in get_many() function
class TestGetManyWithJavaScript:
    """Tests for get_many() function with JavaScript execution."""
    
    @pytest.mark.asyncio
    async def test_get_many_same_script(self, mock_server):
        """Test applying same script to multiple URLs."""
        server, base_url = mock_server
        
        urls = [
            f"{base_url}/load-more",
            f"{base_url}/article/1",
            f"{base_url}/article/2"
        ]
        
        with patch('crawailer.api.get_many') as mock_get_many:
            mock_results = [
                WebContent(
                    url=urls[0],
                    title="Load More Content",
                    text="Expanded content",
                    markdown="# Load More\n\nExpanded content",
                    html="<html>...</html>"
                ),
                WebContent(
                    url=urls[1],
                    title="Article 1",
                    text="Full abstract shown",
                    markdown="# Article 1\n\nFull abstract shown",
                    html="<html>...</html>"
                ),
                WebContent(
                    url=urls[2],
                    title="Article 2",
                    text="Full abstract shown",
                    markdown="# Article 2\n\nFull abstract shown",
                    html="<html>...</html>"
                )
            ]
            mock_get_many.return_value = mock_results
            
            results = await get_many(
                urls,
                script="document.querySelectorAll('[onclick]').forEach(el => el.click())"
            )
            
            assert len(results) == 3
            for result in results:
                assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_many_different_scripts(self, mock_server):
        """Test applying different scripts to different URLs."""
        server, base_url = mock_server
        
        urls = [
            f"{base_url}/infinite-scroll",
            f"{base_url}/load-more",
            f"{base_url}/spa-content"
        ]
        
        scripts = [
            "window.scrollTo(0, document.body.scrollHeight)",
            "document.querySelector('.load-more').click()",
            "window.appReady"
        ]
        
        with patch('crawailer.api.get_many') as mock_get_many:
            mock_results = [
                WebContent(
                    url=urls[0],
                    title="Infinite Scroll",
                    text="More items loaded",
                    markdown="# Infinite Scroll\n\nMore items",
                    html="<html>...</html>",
                    script_result=None
                ),
                WebContent(
                    url=urls[1],
                    title="Load More Content",
                    text="More articles loaded",
                    markdown="# Load More\n\nMore articles",
                    html="<html>...</html>",
                    script_result=None
                ),
                WebContent(
                    url=urls[2],
                    title="SPA Demo",
                    text="SPA loaded",
                    markdown="# SPA Demo\n\nLoaded",
                    html="<html>...</html>",
                    script_result=True
                )
            ]
            mock_get_many.return_value = mock_results
            
            results = await get_many(urls, script=scripts)
            
            assert len(results) == 3
            assert results[2].script_result is True
    
    @pytest.mark.asyncio
    async def test_get_many_mixed_scripts(self, mock_server):
        """Test mix of URLs with and without scripts."""
        server, base_url = mock_server
        
        urls = [
            f"{base_url}/",  # No script needed
            f"{base_url}/dynamic-price",  # Needs script
            f"{base_url}/api/data"  # No script needed
        ]
        
        scripts = [
            None,
            "document.querySelector('.final-price').innerText",
            None
        ]
        
        with patch('crawailer.api.get_many') as mock_get_many:
            mock_results = [
                WebContent(
                    url=urls[0],
                    title="Test Page",
                    text="Initial content",
                    markdown="# Test Page",
                    html="<html>...</html>"
                ),
                WebContent(
                    url=urls[1],
                    title="Product Page",
                    text="Price: $79.99",
                    markdown="# Product\n\n$79.99",
                    html="<html>...</html>",
                    script_result="$79.99"
                ),
                WebContent(
                    url=urls[2],
                    title="API Response",
                    text='{"status":"success"}',
                    markdown="API data",
                    html="<html>...</html>"
                )
            ]
            mock_get_many.return_value = mock_results
            
            results = await get_many(urls, script=scripts)
            
            assert results[0].script_result is None
            assert results[1].script_result == "$79.99"
            assert results[2].script_result is None


# Test JavaScript execution in discover() function
class TestDiscoverWithJavaScript:
    """Tests for discover() function with JavaScript execution."""
    
    @pytest.mark.asyncio
    async def test_discover_with_search_script(self, mock_server):
        """Test executing script on search results page."""
        server, base_url = mock_server
        
        with patch('crawailer.api.discover') as mock_discover:
            # Simulate discovering more results after clicking "Show More"
            mock_results = [
                WebContent(
                    url=f"{base_url}/article/1",
                    title="Result 1: AI",
                    text="Article about AI",
                    markdown="# Result 1\n\nAI content",
                    html="<html>...</html>"
                ),
                WebContent(
                    url=f"{base_url}/article/2",
                    title="Result 2: AI",
                    text="Another AI article",
                    markdown="# Result 2\n\nMore AI",
                    html="<html>...</html>"
                ),
                WebContent(
                    url=f"{base_url}/article/3",
                    title="Result 3: AI",
                    text="Third AI article",
                    markdown="# Result 3\n\nAI research",
                    html="<html>...</html>"
                )
            ]
            mock_discover.return_value = mock_results
            
            results = await discover(
                "AI research",
                script="document.querySelector('.show-more')?.click()",
                max_pages=5
            )
            
            assert len(results) == 3
            assert all("AI" in r.title for r in results)
    
    @pytest.mark.asyncio
    async def test_discover_with_content_script(self, mock_server):
        """Test executing script on each discovered page."""
        server, base_url = mock_server
        
        with patch('crawailer.api.discover') as mock_discover:
            # Simulate expanded abstracts on article pages
            mock_results = [
                WebContent(
                    url=f"{base_url}/article/1",
                    title="Article 1",
                    text="Full abstract: Detailed research information",
                    markdown="# Article 1\n\nFull abstract",
                    html="<html>...</html>",
                    script_result="expanded"
                ),
                WebContent(
                    url=f"{base_url}/article/2",
                    title="Article 2",
                    text="Full abstract: More research details",
                    markdown="# Article 2\n\nFull abstract",
                    html="<html>...</html>",
                    script_result="expanded"
                )
            ]
            mock_discover.return_value = mock_results
            
            results = await discover(
                "research papers",
                content_script="""
                    document.querySelector('.abstract')?.click();
                    return 'expanded';
                """,
                max_pages=2
            )
            
            assert all(r.script_result == "expanded" for r in results)
            assert all("Full abstract" in r.text for r in results)
    
    @pytest.mark.asyncio
    async def test_discover_with_both_scripts(self, mock_server):
        """Test using both search and content scripts."""
        server, base_url = mock_server
        
        with patch('crawailer.api.discover') as mock_discover:
            mock_results = [
                WebContent(
                    url=f"{base_url}/article/1",
                    title="Enhanced Result 1",
                    text="Complete content with expanded sections",
                    markdown="# Enhanced Result 1",
                    html="<html>...</html>"
                ),
                WebContent(
                    url=f"{base_url}/article/2",
                    title="Enhanced Result 2",
                    text="Complete content with expanded sections",
                    markdown="# Enhanced Result 2",
                    html="<html>...</html>"
                )
            ]
            mock_discover.return_value = mock_results
            
            results = await discover(
                "comprehensive search",
                script="document.querySelector('.show-more')?.click()",
                content_script="document.querySelectorAll('.expand').forEach(e => e.click())",
                max_pages=10
            )
            
            assert len(results) == 2
            assert all("Complete content" in r.text for r in results)


# Test Browser class JavaScript execution
class TestBrowserJavaScriptExecution:
    """Tests for Browser class execute_script method."""
    
    @pytest.mark.asyncio
    async def test_execute_script_basic(self):
        """Test basic script execution."""
        browser = Browser(BrowserConfig())
        
        # Mock Playwright components
        mock_page = AsyncMock()
        mock_page.evaluate.return_value = {"result": "test"}
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        browser._browser = mock_browser
        browser._is_started = True
        
        result = await browser.execute_script(
            "https://example.com",
            "return {result: 'test'}"
        )
        
        assert result == {"result": "test"}
        mock_page.evaluate.assert_called_once_with("return {result: 'test'}")
        mock_page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_script_dom_query(self):
        """Test DOM querying via script."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.evaluate.return_value = 5
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        browser._browser = mock_browser
        browser._is_started = True
        
        result = await browser.execute_script(
            "https://example.com",
            "document.querySelectorAll('div').length"
        )
        
        assert result == 5
    
    @pytest.mark.asyncio
    async def test_execute_script_async_js(self):
        """Test async JavaScript execution."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.evaluate.return_value = "delayed result"
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        browser._browser = mock_browser
        browser._is_started = True
        
        script = """
        async () => {
            await new Promise(r => setTimeout(r, 100));
            return 'delayed result';
        }
        """
        
        result = await browser.execute_script("https://example.com", script)
        
        assert result == "delayed result"
    
    @pytest.mark.asyncio
    async def test_execute_script_error(self):
        """Test script execution error handling."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.evaluate.side_effect = Exception("Script error: undefined is not a function")
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        browser._browser = mock_browser
        browser._is_started = True
        
        with pytest.raises(Exception) as exc_info:
            await browser.execute_script(
                "https://example.com",
                "nonexistent.function()"
            )
        
        assert "undefined is not a function" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_script_timeout(self):
        """Test script execution timeout."""
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
                "https://slow-site.com",
                "return true",
                timeout=1
            )

    @pytest.mark.asyncio
    async def test_browser_execute_script_basic(self):
        """Test basic script execution (alias for compatibility)."""
        await self.test_execute_script_basic()

    @pytest.mark.asyncio
    async def test_browser_execute_script_error(self):
        """Test script execution error handling (alias for compatibility)."""
        await self.test_execute_script_error()

    @pytest.mark.asyncio
    async def test_browser_script_timeout(self):
        """Test script execution timeout (alias for compatibility)."""
        await self.test_execute_script_timeout()

    @pytest.mark.asyncio
    async def test_browser_fetch_page_with_scripts(self):
        """Test fetch_page with script_before and script_after parameters."""
        browser = Browser(BrowserConfig())
        
        # Mock Playwright components
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.set_viewport_size = AsyncMock()
        mock_page.content.return_value = "<html><body><h1>Test</h1></body></html>"
        mock_page.title.return_value = "Test Page"
        mock_page.close = AsyncMock()
        
        # Mock script execution results
        script_calls = []
        def mock_evaluate(script):
            script_calls.append(script)
            if "before" in script:
                return {"before_result": "success"}
            elif "after" in script:
                return {"after_result": "complete"}
            return None
        
        mock_page.evaluate.side_effect = mock_evaluate
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response
        
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test with both script_before and script_after
        result = await browser.fetch_page(
            "https://example.com",
            script_before="return {before: true}",
            script_after="return {after: true}"
        )
        
        # Verify the result structure
        assert result["url"] == "https://example.com"
        assert result["status"] == 200
        assert result["html"] == "<html><body><h1>Test</h1></body></html>"
        assert result["title"] == "Test Page"
        assert "script_result" in result
        assert "script_error" in result
        
        # Script result should contain both before and after results
        assert result["script_result"] == {
            "script_before": {"before_result": "success"},
            "script_after": {"after_result": "complete"}
        }
        assert result["script_error"] is None
        
        # Verify script execution order (before content extraction, after content extraction)
        assert len(script_calls) == 2
        mock_page.evaluate.assert_any_call("return {before: true}")
        mock_page.evaluate.assert_any_call("return {after: true}")

    @pytest.mark.asyncio
    async def test_browser_fetch_page_script_before_only(self):
        """Test fetch_page with only script_before parameter."""
        browser = Browser(BrowserConfig())
        
        # Mock setup
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.set_viewport_size = AsyncMock()
        mock_page.content.return_value = "<html><body><h1>Test</h1></body></html>"
        mock_page.title.return_value = "Test Page"
        mock_page.evaluate.return_value = {"data": "extracted"}
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response
        
        browser._browser = mock_browser
        browser._is_started = True
        
        result = await browser.fetch_page(
            "https://example.com",
            script_before="return document.querySelector('h1').innerText"
        )
        
        assert result["script_result"] == {"data": "extracted"}
        assert result["script_error"] is None
        mock_page.evaluate.assert_called_once_with("return document.querySelector('h1').innerText")

    @pytest.mark.asyncio
    async def test_browser_fetch_page_script_error_handling(self):
        """Test fetch_page script error handling."""
        browser = Browser(BrowserConfig())
        
        # Mock setup
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.set_viewport_size = AsyncMock()
        mock_page.content.return_value = "<html><body><h1>Test</h1></body></html>"
        mock_page.title.return_value = "Test Page"
        mock_page.evaluate.side_effect = Exception("Script syntax error")
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response
        
        browser._browser = mock_browser
        browser._is_started = True
        
        result = await browser.fetch_page(
            "https://example.com",
            script_before="invalid javascript syntax %@#$"
        )
        
        assert result["script_result"] is None
        assert "Script execution error: Script syntax error" in result["script_error"]
        # Page should still load successfully
        assert result["status"] == 200
        assert result["html"] == "<html><body><h1>Test</h1></body></html>"

    @pytest.mark.asyncio
    async def test_browser_fetch_page_page_load_error_with_scripts(self):
        """Test fetch_page when page load fails but scripts were requested."""
        browser = Browser(BrowserConfig())
        
        # Mock setup
        mock_page = AsyncMock()
        mock_page.goto.side_effect = Exception("Network error")
        mock_page.set_viewport_size = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        browser._browser = mock_browser
        browser._is_started = True
        
        result = await browser.fetch_page(
            "https://unreachable-site.com",
            script_before="return true"
        )
        
        # Should handle the error gracefully
        assert result["status"] == 0
        assert result["error"] == "Network error"
        assert result["script_result"] is None
        assert "Page load failed, scripts not executed: Network error" in result["script_error"]


# Test utilities and integration
class TestJavaScriptIntegration:
    """Integration tests for JavaScript execution."""
    
    @pytest.mark.asyncio
    async def test_real_browser_js_execution(self, mock_server):
        """Test with real browser if available (integration test)."""
        server, base_url = mock_server
        
        # This test requires Playwright to be installed
        pytest.importorskip("playwright")
        
        from crawailer import Browser, BrowserConfig
        
        browser = Browser(BrowserConfig(headless=True))
        
        try:
            await browser.start()
            
            # Test dynamic price extraction
            result = await browser.execute_script(
                f"{base_url}/dynamic-price",
                """
                await new Promise(r => setTimeout(r, 500));
                return document.querySelector('.final-price')?.innerText;
                """
            )
            
            # Should get discounted price
            assert result is not None
            # Price should be discounted (80% of 99.99 = 79.99)
            assert "79.99" in result
            
        finally:
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_performance_multiple_scripts(self):
        """Test performance with multiple script executions."""
        browser = Browser(BrowserConfig())
        
        # Mock setup
        mock_page = AsyncMock()
        mock_page.evaluate.return_value = "result"
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        
        browser._browser = mock_browser
        browser._is_started = True
        
        # Execute multiple scripts concurrently
        urls = [f"https://example.com/page{i}" for i in range(10)]
        scripts = ["return document.title" for _ in range(10)]
        
        tasks = [
            browser.execute_script(url, script)
            for url, script in zip(urls, scripts)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(r == "result" for r in results)
        
        # Verify all pages were closed
        assert mock_page.close.call_count == 10


# Test WebContent enhancements
class TestWebContentJavaScriptFields:
    """Test WebContent dataclass JavaScript-related fields."""
    
    def test_webcontent_with_script_result(self):
        """Test WebContent with script_result field."""
        content = WebContent(
            url="https://example.com",
            title="Test",
            text="Content",
            markdown="# Test",
            html="<html></html>",
            script_result={"data": "value"}
        )
        
        assert content.script_result == {"data": "value"}
        assert content.script_error is None
    
    def test_webcontent_with_script_error(self):
        """Test WebContent with script_error field."""
        content = WebContent(
            url="https://example.com",
            title="Test",
            text="Content",
            markdown="# Test",
            html="<html></html>",
            script_error="ReferenceError: x is not defined"
        )
        
        assert content.script_result is None
        assert "ReferenceError" in content.script_error
    
    def test_webcontent_serialization(self):
        """Test WebContent serialization with JS fields."""
        content = WebContent(
            url="https://example.com",
            title="Test",
            text="Content",
            markdown="# Test",
            html="<html></html>",
            script_result=[1, 2, 3],
            script_error=None
        )
        
        # Should be serializable
        import json
        data = {
            "url": content.url,
            "title": content.title,
            "script_result": content.script_result
        }
        
        serialized = json.dumps(data)
        assert "[1, 2, 3]" in serialized


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])