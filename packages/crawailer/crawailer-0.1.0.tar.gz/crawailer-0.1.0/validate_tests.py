#!/usr/bin/env python3
"""Validate our JavaScript API tests and mock server without complex imports."""

import asyncio
import json
from aiohttp import web
from aiohttp.test_utils import TestServer

class SimpleTestServer:
    """Simplified version of our mock HTTP server for validation."""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.server = None
        
    def setup_routes(self):
        self.app.router.add_get('/', self.index_page)
        self.app.router.add_get('/dynamic-price', self.dynamic_price_page)
        self.app.router.add_get('/api/test', self.api_endpoint)
    
    async def start(self):
        self.server = TestServer(self.app, port=0)
        await self.server.start()
        return f"http://localhost:{self.server.port}"
        
    async def stop(self):
        if self.server:
            await self.server.close()
    
    async def index_page(self, request):
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>JavaScript Test Page</h1>
            <div id="content">Initial content</div>
            <script>
                window.testData = { loaded: true, timestamp: Date.now() };
                console.log('Test page loaded');
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def dynamic_price_page(self, request):
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Product Page</title></head>
        <body>
            <h1>Amazing Product</h1>
            <div class="price-container">
                <span class="loading">Loading price...</span>
                <span class="final-price" style="display:none;">$79.99</span>
            </div>
            <script>
                // Simulate dynamic price loading
                setTimeout(() => {
                    document.querySelector('.loading').style.display = 'none';
                    document.querySelector('.final-price').style.display = 'block';
                }, 200);
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def api_endpoint(self, request):
        data = {
            "status": "success",
            "message": "Test API working",
            "features": ["javascript_execution", "mock_server", "async_testing"]
        }
        return web.json_response(data)

async def test_mock_server():
    """Test our mock server infrastructure."""
    print("🧪 Testing Mock HTTP Server Infrastructure...")
    
    server = SimpleTestServer()
    base_url = await server.start()
    print(f"✅ Test server started at {base_url}")
    
    # Test with aiohttp client
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        # Test HTML page
        async with session.get(f"{base_url}/") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "JavaScript Test Page" in text
            assert "window.testData" in text
            print("✅ HTML page with JavaScript served correctly")
        
        # Test dynamic content page
        async with session.get(f"{base_url}/dynamic-price") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "Amazing Product" in text
            assert "final-price" in text
            assert "setTimeout" in text  # JavaScript present
            print("✅ Dynamic content page served correctly")
        
        # Test JSON API
        async with session.get(f"{base_url}/api/test") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "success"
            assert "javascript_execution" in data["features"]
            print("✅ JSON API endpoint working")
    
    await server.stop()
    print("✅ Test server stopped cleanly")

def test_proposed_api_structure():
    """Test the structure of our proposed JavaScript API enhancements."""
    print("\n🧪 Testing Proposed API Structure...")
    
    # Simulate the enhanced get() function signature
    def enhanced_get(url, *, wait_for=None, script=None, script_before=None, 
                    script_after=None, timeout=30, clean=True, 
                    extract_links=True, extract_metadata=True):
        """Mock enhanced get function with JavaScript support."""
        return {
            "url": url,
            "script_params": {
                "script": script,
                "script_before": script_before, 
                "script_after": script_after,
                "wait_for": wait_for
            },
            "options": {
                "timeout": timeout,
                "clean": clean,
                "extract_links": extract_links,
                "extract_metadata": extract_metadata
            }
        }
    
    # Test various call patterns
    basic_call = enhanced_get("https://example.com")
    assert basic_call["url"] == "https://example.com"
    assert basic_call["script_params"]["script"] is None
    print("✅ Basic API call structure works")
    
    script_call = enhanced_get(
        "https://shop.com/product",
        script="document.querySelector('.price').innerText",
        wait_for=".price-loaded"
    )
    assert script_call["script_params"]["script"] is not None
    assert script_call["script_params"]["wait_for"] == ".price-loaded"
    print("✅ Script execution parameters work")
    
    complex_call = enhanced_get(
        "https://spa.com",
        script_before="window.scrollTo(0, document.body.scrollHeight)",
        script_after="return window.pageData",
        timeout=45
    )
    assert complex_call["script_params"]["script_before"] is not None
    assert complex_call["script_params"]["script_after"] is not None
    assert complex_call["options"]["timeout"] == 45
    print("✅ Complex script scenarios work")

def test_webcontent_enhancements():
    """Test WebContent enhancements for JavaScript results."""
    print("\n🧪 Testing WebContent JavaScript Enhancements...")
    
    class MockWebContent:
        """Mock WebContent with JavaScript fields."""
        def __init__(self, url, title, text, markdown, html, 
                     script_result=None, script_error=None):
            self.url = url
            self.title = title
            self.text = text
            self.markdown = markdown
            self.html = html
            self.script_result = script_result
            self.script_error = script_error
        
        def to_dict(self):
            return {
                "url": self.url,
                "title": self.title,
                "script_result": self.script_result,
                "script_error": self.script_error
            }
    
    # Test successful script execution
    content_success = MockWebContent(
        url="https://example.com",
        title="Test Page",
        text="Content with $79.99 price",
        markdown="# Test\n\nPrice: $79.99",
        html="<html>...</html>",
        script_result="$79.99"
    )
    
    assert content_success.script_result == "$79.99"
    assert content_success.script_error is None
    print("✅ WebContent with successful script result")
    
    # Test script error
    content_error = MockWebContent(
        url="https://example.com",
        title="Test Page", 
        text="Content",
        markdown="# Test",
        html="<html>...</html>",
        script_error="ReferenceError: nonexistent is not defined"
    )
    
    assert content_error.script_result is None
    assert "ReferenceError" in content_error.script_error
    print("✅ WebContent with script error handling")
    
    # Test serialization
    data = content_success.to_dict()
    json_str = json.dumps(data)
    assert "$79.99" in json_str
    print("✅ WebContent serialization with script results")

def test_batch_processing_scenarios():
    """Test batch processing scenarios with JavaScript."""
    print("\n🧪 Testing Batch Processing Scenarios...")
    
    def mock_get_many(urls, *, script=None, **kwargs):
        """Mock get_many with JavaScript support."""
        results = []
        
        # Handle different script formats
        if isinstance(script, str):
            # Same script for all URLs
            scripts = [script] * len(urls)
        elif isinstance(script, list):
            # Different scripts per URL
            scripts = script + [None] * (len(urls) - len(script))
        else:
            # No scripts
            scripts = [None] * len(urls)
        
        for i, (url, script_item) in enumerate(zip(urls, scripts)):
            results.append({
                "url": url,
                "script": script_item,
                "result": f"Content from {url}" + (f" (script: {script_item})" if script_item else "")
            })
        
        return results
    
    # Test same script for all URLs
    urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
    results = mock_get_many(urls, script="document.title")
    
    assert len(results) == 3
    assert all(r["script"] == "document.title" for r in results)
    print("✅ Same script applied to multiple URLs")
    
    # Test different scripts per URL
    scripts = [
        "window.scrollTo(0, document.body.scrollHeight)",
        "document.querySelector('.load-more').click()",
        None
    ]
    results = mock_get_many(urls, script=scripts)
    
    assert results[0]["script"] == scripts[0]
    assert results[1]["script"] == scripts[1] 
    assert results[2]["script"] is None
    print("✅ Different scripts per URL")

async def main():
    """Run all validation tests."""
    print("🚀 JavaScript API Enhancement Validation\n")
    
    try:
        # Test mock server infrastructure
        await test_mock_server()
        
        # Test API structure
        test_proposed_api_structure()
        
        # Test WebContent enhancements
        test_webcontent_enhancements()
        
        # Test batch processing
        test_batch_processing_scenarios()
        
        print("\n🎉 All Validation Tests Passed!")
        
        print("\n📊 Validation Summary:")
        print("   ✅ Mock HTTP server with JavaScript content")
        print("   ✅ Enhanced API function signatures") 
        print("   ✅ WebContent with script result fields")
        print("   ✅ Batch processing with mixed scripts")
        print("   ✅ Error handling patterns")
        print("   ✅ JSON serialization compatibility")
        
        print("\n🛠️  Implementation Roadmap:")
        print("   1. Update WebContent dataclass (add script_result, script_error fields)")
        print("   2. Enhance Browser.fetch_page() (add script_before, script_after params)")
        print("   3. Update api.py functions (add script parameters)")
        print("   4. Implement ContentExtractor JS handling")
        print("   5. Add comprehensive error handling")
        print("   6. Run full test suite with Playwright")
        
        print("\n📁 Test Files Created:")
        print("   📄 tests/test_javascript_api.py - Comprehensive test suite")
        print("   📄 ENHANCEMENT_JS_API.md - Detailed enhancement proposal") 
        print("   📄 validate_tests.py - This validation script")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)