"""
Basic usage examples for Crawailer.

This demonstrates the main API functions and typical workflows.
"""

import asyncio
import crawailer as web


async def basic_example():
    """Basic content extraction from a single URL."""
    print("🕷️ Basic Crawailer Example")
    print("=" * 50)
    
    # Simple content extraction
    print("\n1. Single page extraction:")
    content = await web.get("https://example.com")
    
    print(f"   Title: {content.title}")
    print(f"   Word count: {content.word_count}")
    print(f"   Reading time: {content.reading_time}")
    print(f"   Quality score: {content.quality_score:.1f}/10")
    print(f"   Content type: {content.content_type}")
    
    # Show first 200 characters of markdown
    print(f"\n   Markdown preview:")
    print(f"   {content.markdown[:200]}...")


async def batch_example():
    """Batch processing multiple URLs."""
    print("\n2. Batch processing:")
    
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://httpbin.org/json"  # This will be different content
    ]
    
    results = await web.get_many(urls, max_concurrent=3)
    
    print(f"   Processed {len(results)} URLs")
    for i, result in enumerate(results):
        if result:
            print(f"   {i+1}. {result.title} ({result.word_count} words)")
        else:
            print(f"   {i+1}. Failed to fetch")


async def discovery_example():
    """Content discovery (placeholder implementation)."""
    print("\n3. Content discovery:")
    
    try:
        # Note: This is a placeholder implementation
        results = await web.discover("web crawling", max_pages=3)
        print(f"   Found {len(results)} relevant sources")
        
        for result in results:
            print(f"   - {result.title}")
            
    except NotImplementedError:
        print("   Discovery feature coming soon!")


async def context_manager_example():
    """Using browser as context manager for more control."""
    print("\n4. Advanced browser control:")
    
    from crawailer import Browser, BrowserConfig
    
    config = BrowserConfig(headless=True, timeout=15000)
    
    async with Browser(config) as browser:
        # Fetch with custom wait condition
        page_data = await browser.fetch_page(
            "https://httpbin.org/delay/1",
            timeout=10
        )
        
        print(f"   Fetched: {page_data['url']}")
        print(f"   Status: {page_data['status']}")
        print(f"   Load time: {page_data['load_time']:.2f}s")


async def content_analysis_example():
    """Analyzing extracted content."""
    print("\n5. Content analysis:")
    
    content = await web.get("https://httpbin.org/html")
    
    print(f"   Content hash: {content.content_hash[:16]}...")
    print(f"   Language: {content.language}")
    print(f"   Links found: {len(content.links)}")
    print(f"   Images found: {len(content.images)}")
    
    if content.links:
        print(f"   First link: {content.links[0]['text']} -> {content.links[0]['url']}")


async def main():
    """Run all examples."""
    try:
        await basic_example()
        await batch_example()
        await discovery_example()
        await context_manager_example()
        await content_analysis_example()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean up global resources
        await web.cleanup()


if __name__ == "__main__":
    asyncio.run(main())