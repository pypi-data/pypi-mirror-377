#!/usr/bin/env python3
"""
Real-world testing of Crawailer JavaScript API enhancements.
Tests various website types to validate production readiness.
"""

import asyncio
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

# Add src to path to use our enhanced implementation
sys.path.insert(0, 'src')

import crawailer as web


class RealWorldTester:
    """Test suite for real-world website crawling with JavaScript enhancement."""
    
    def __init__(self):
        self.results = []
        self.test_start_time = None
        
    async def test_static_content_baseline(self):
        """Test with static content to ensure basic functionality works."""
        print("🧪 Testing Static Content (Baseline)")
        print("-" * 50)
        
        test_cases = [
            {
                "name": "Wikipedia Article",
                "url": "https://en.wikipedia.org/wiki/Web_scraping",
                "expected_elements": ["Web scraping", "content", "extraction"],
                "use_js": False
            },
            {
                "name": "Example.com",
                "url": "https://example.com",
                "expected_elements": ["Example Domain", "information", "examples"],
                "use_js": False
            }
        ]
        
        for test in test_cases:
            await self._run_test_case(test)
    
    async def test_dynamic_content_scenarios(self):
        """Test JavaScript-enhanced content extraction."""
        print("\n🚀 Testing Dynamic Content with JavaScript")
        print("-" * 50)
        
        test_cases = [
            {
                "name": "GitHub Repository (Dynamic Loading)",
                "url": "https://github.com/microsoft/playwright",
                "script": """
                // Wait for dynamic content and return repository stats
                await new Promise(r => setTimeout(r, 2000));
                const stars = document.querySelector('[data-view-component="true"] strong')?.innerText || 'unknown';
                return {stars: stars, loaded: true};
                """,
                "expected_elements": ["Playwright", "browser", "automation"],
                "use_js": True
            },
            {
                "name": "JSONPlaceholder API Demo",
                "url": "https://jsonplaceholder.typicode.com/",
                "script": """
                // Look for API endpoints and examples
                const links = Array.from(document.querySelectorAll('a')).map(a => a.href);
                const codeBlocks = Array.from(document.querySelectorAll('code')).map(c => c.innerText);
                return {
                    links_found: links.length,
                    code_examples: codeBlocks.length,
                    has_api_info: document.body.innerText.includes('REST API')
                };
                """,
                "expected_elements": ["REST API", "JSON", "placeholder"],
                "use_js": True
            }
        ]
        
        for test in test_cases:
            await self._run_test_case(test)
    
    async def test_spa_and_modern_sites(self):
        """Test Single Page Applications and modern JavaScript-heavy sites."""
        print("\n⚡ Testing SPAs and Modern JavaScript Sites")
        print("-" * 50)
        
        test_cases = [
            {
                "name": "React Documentation",
                "url": "https://react.dev/",
                "script": """
                // Wait for React app to load
                await new Promise(r => setTimeout(r, 3000));
                const title = document.querySelector('h1')?.innerText || 'No title found';
                const navItems = document.querySelectorAll('nav a').length;
                return {
                    page_title: title,
                    navigation_items: navItems,
                    react_loaded: !!window.React || document.body.innerText.includes('React')
                };
                """,
                "expected_elements": ["React", "JavaScript", "library"],
                "use_js": True
            }
        ]
        
        for test in test_cases:
            await self._run_test_case(test)
    
    async def test_batch_processing(self):
        """Test get_many() with multiple sites and different JavaScript requirements."""
        print("\n📦 Testing Batch Processing with Mixed JavaScript")
        print("-" * 50)
        
        urls = [
            "https://httpbin.org/html",      # Static HTML
            "https://httpbin.org/json",      # JSON endpoint  
            "https://example.com"            # Simple static page
        ]
        
        scripts = [
            "document.querySelector('h1')?.innerText || 'No H1 found'",  # Extract title
            "JSON.stringify(Object.keys(window).slice(0, 5))",           # Get some window properties
            None  # No script for simple page
        ]
        
        start_time = time.time()
        
        try:
            print(f"Processing {len(urls)} URLs with mixed JavaScript requirements...")
            
            results = await web.get_many(urls, script=scripts, max_concurrent=3)
            
            processing_time = time.time() - start_time
            
            print(f"✅ Batch processing completed in {processing_time:.2f}s")
            print(f"✅ Successfully processed {len([r for r in results if r])} out of {len(urls)} URLs")
            
            for i, (url, result) in enumerate(zip(urls, results)):
                if result:
                    script_status = "✅ JS executed" if result.script_result else "➖ No JS"
                    word_count = result.word_count
                    print(f"   {i+1}. {url[:50]:<50} | {word_count:>4} words | {script_status}")
                    if result.script_result:
                        print(f"      Script result: {str(result.script_result)[:80]}")
                else:
                    print(f"   {i+1}. {url[:50]:<50} | FAILED")
            
            self.results.append({
                "test_name": "Batch Processing",
                "status": "success",
                "urls_processed": len([r for r in results if r]),
                "total_urls": len(urls),
                "processing_time": processing_time,
                "details": f"Mixed JS/no-JS processing successful"
            })
            
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
            self.results.append({
                "test_name": "Batch Processing", 
                "status": "failed",
                "error": str(e)
            })
    
    async def test_discovery_scenarios(self):
        """Test discover() function with JavaScript enhancement."""
        print("\n🔍 Testing Discovery with JavaScript Enhancement")
        print("-" * 50)
        
        try:
            print("Testing discover() function (Note: May be limited implementation)")
            
            # Test basic discovery
            start_time = time.time()
            results = await web.discover("Python web scraping", max_pages=3)
            discovery_time = time.time() - start_time
            
            print(f"✅ Discovery completed in {discovery_time:.2f}s")
            print(f"✅ Found {len(results)} results")
            
            for i, result in enumerate(results[:3]):
                print(f"   {i+1}. {result.title[:60]}")
                print(f"      URL: {result.url}")
                print(f"      Words: {result.word_count}")
            
            self.results.append({
                "test_name": "Discovery Function",
                "status": "success",
                "results_found": len(results),
                "discovery_time": discovery_time
            })
            
        except NotImplementedError:
            print("ℹ️  Discovery function not yet fully implemented (expected)")
            self.results.append({
                "test_name": "Discovery Function",
                "status": "not_implemented",
                "note": "Expected - discovery may need search engine integration"
            })
        except Exception as e:
            print(f"❌ Discovery test failed: {e}")
            self.results.append({
                "test_name": "Discovery Function",
                "status": "failed", 
                "error": str(e)
            })
    
    async def _run_test_case(self, test: Dict[str, Any]):
        """Run an individual test case."""
        print(f"\n🌐 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        start_time = time.time()
        
        try:
            if test['use_js'] and 'script' in test:
                print(f"   JavaScript: {test['script'][:60]}...")
                content = await web.get(
                    test['url'], 
                    script=test['script'],
                    timeout=45
                )
            else:
                print("   Mode: Static content extraction")
                content = await web.get(test['url'], timeout=30)
            
            load_time = time.time() - start_time
            
            # Analyze results
            found_elements = sum(1 for element in test['expected_elements'] 
                               if element.lower() in content.text.lower())
            
            print(f"   ✅ Loaded in {load_time:.2f}s")
            print(f"   ✅ Title: {content.title}")
            print(f"   ✅ Content: {content.word_count} words")
            print(f"   ✅ Expected elements found: {found_elements}/{len(test['expected_elements'])}")
            
            if content.script_result:
                print(f"   ✅ JavaScript result: {str(content.script_result)[:100]}")
            
            if content.script_error:
                print(f"   ⚠️  JavaScript error: {content.script_error}")
            
            self.results.append({
                "test_name": test['name'],
                "url": test['url'],
                "status": "success",
                "load_time": load_time,
                "word_count": content.word_count,
                "elements_found": found_elements,
                "expected_elements": len(test['expected_elements']),
                "has_js_result": content.script_result is not None,
                "has_js_error": content.script_error is not None
            })
            
        except Exception as e:
            load_time = time.time() - start_time
            print(f"   ❌ Failed after {load_time:.2f}s: {e}")
            
            self.results.append({
                "test_name": test['name'],
                "url": test['url'], 
                "status": "failed",
                "load_time": load_time,
                "error": str(e)
            })
    
    def print_summary(self):
        """Print comprehensive test results summary."""
        print("\n" + "="*80)
        print("🎯 REAL-WORLD TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r['status'] == 'success'])
        failed_tests = len([r for r in self.results if r['status'] == 'failed'])
        not_implemented = len([r for r in self.results if r['status'] == 'not_implemented'])
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total tests: {total_tests}")
        print(f"   ✅ Successful: {successful_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ℹ️  Not implemented: {not_implemented}")
        print(f"   📈 Success rate: {success_rate:.1f}%")
        
        if successful_tests > 0:
            successful_results = [r for r in self.results if r['status'] == 'success']
            avg_load_time = sum(r.get('load_time', 0) for r in successful_results) / len(successful_results)
            total_words = sum(r.get('word_count', 0) for r in successful_results)
            js_enabled_tests = len([r for r in successful_results if r.get('has_js_result', False)])
            
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average load time: {avg_load_time:.2f}s")
            print(f"   Total content extracted: {total_words:,} words")
            print(f"   JavaScript-enhanced extractions: {js_enabled_tests}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'failed' else "ℹ️"
            print(f"   {status_icon} {result['test_name']}")
            
            if result['status'] == 'success':
                load_time = result.get('load_time', 0)
                words = result.get('word_count', 0)
                js_indicator = " (JS)" if result.get('has_js_result', False) else ""
                print(f"      {load_time:.2f}s | {words} words{js_indicator}")
            elif result['status'] == 'failed':
                print(f"      Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n🎉 JavaScript API Enhancement: {'VALIDATED' if success_rate >= 70 else 'NEEDS IMPROVEMENT'}")
        
        if success_rate >= 70:
            print("   The JavaScript API enhancement is working well in real-world scenarios!")
        else:
            print("   Some issues detected that may need attention.")

async def main():
    """Run comprehensive real-world testing."""
    print("🚀 Crawailer JavaScript API Enhancement - Real-World Testing")
    print("="*80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing enhanced JavaScript capabilities with real websites...")
    
    tester = RealWorldTester()
    tester.test_start_time = time.time()
    
    try:
        # Run all test suites
        await tester.test_static_content_baseline()
        await tester.test_dynamic_content_scenarios()
        await tester.test_spa_and_modern_sites()
        await tester.test_batch_processing()
        await tester.test_discovery_scenarios()
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        total_time = time.time() - tester.test_start_time
        print(f"\nTotal testing time: {total_time:.2f}s")
        tester.print_summary()

if __name__ == "__main__":
    print("Note: This requires Playwright to be installed and browser setup complete.")
    print("Run 'playwright install chromium' if you haven't already.")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTesting cancelled by user.")
    except Exception as e:
        print(f"Failed to start testing: {e}")
        print("Make sure Playwright is properly installed and configured.")