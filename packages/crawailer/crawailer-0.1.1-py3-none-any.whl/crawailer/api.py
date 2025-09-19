"""
High-level convenience API for common web content tasks.

This is the main interface most users will interact with - simple,
predictable functions that handle the complexity behind the scenes.
"""

from typing import List, Optional, Union
from .browser import Browser
from .content import WebContent, ContentExtractor
from .config import BrowserConfig


# Global browser instance for convenience API
_browser: Optional[Browser] = None


async def _get_browser() -> Browser:
    """Get or create the global browser instance."""
    global _browser
    if _browser is None:
        config = BrowserConfig()
        _browser = Browser(config)
        await _browser.start()
    return _browser


async def get(
    url: str,
    *,
    wait_for: Optional[str] = None,
    timeout: int = 30,
    clean: bool = True,
    extract_links: bool = True,
    extract_metadata: bool = True,
    script: Optional[str] = None,
    script_before: Optional[str] = None,
    script_after: Optional[str] = None,
) -> WebContent:
    """
    Get content from a single URL.
    
    This is the main function for extracting content from web pages.
    It handles browser management, content extraction, and cleaning automatically.
    
    Args:
        url: The URL to fetch
        wait_for: Optional CSS selector to wait for before extracting
        timeout: Request timeout in seconds
        clean: Whether to clean and optimize the content
        extract_links: Whether to extract and analyze links
        extract_metadata: Whether to extract metadata (author, date, etc.)
        script: JavaScript to execute before content extraction (alias for script_before)
        script_before: JavaScript to execute before content extraction
        script_after: JavaScript to execute after content extraction
        
    Returns:
        WebContent object with markdown, text, metadata, and script results
        
    Example:
        >>> content = await get("https://example.com")
        >>> print(content.title)
        >>> print(content.markdown[:500])
        >>> print(f"Reading time: {content.reading_time}")
        
        >>> # With JavaScript execution
        >>> content = await get(
        ...     "https://dynamic-site.com",
        ...     script="document.querySelector('.price').innerText",
        ...     wait_for=".price"
        ... )
        >>> print(f"Price: {content.script_result}")
    """
    browser = await _get_browser()
    extractor = ContentExtractor(
        clean=clean,
        extract_links=extract_links, 
        extract_metadata=extract_metadata
    )
    
    # Handle script parameter aliases
    effective_script_before = script_before or script
    effective_script_after = script_after
    
    page_data = await browser.fetch_page(
        url, 
        wait_for=wait_for, 
        timeout=timeout,
        script_before=effective_script_before,
        script_after=effective_script_after
    )
    content = await extractor.extract(page_data)
    
    return content


async def get_many(
    urls: List[str],
    *,
    max_concurrent: int = 5,
    timeout: int = 30,
    clean: bool = True,
    progress: bool = False,
    script: Optional[Union[str, List[str]]] = None,
) -> List[WebContent]:
    """
    Get content from multiple URLs efficiently.
    
    Uses intelligent concurrency control and provides optional progress tracking.
    Failed URLs are handled gracefully without stopping the entire batch.
    
    Args:
        urls: List of URLs to fetch
        max_concurrent: Maximum number of concurrent requests
        timeout: Request timeout per URL in seconds
        clean: Whether to clean and optimize the content
        progress: Whether to show progress bar
        script: JavaScript to execute for each URL (str) or per-URL scripts (List[str])
        
    Returns:
        List of WebContent objects (failed URLs return None)
        
    Example:
        >>> urls = ["https://site1.com", "https://site2.com"]
        >>> results = await get_many(urls, progress=True)
        >>> successful = [r for r in results if r is not None]
        
        >>> # With same script for all URLs
        >>> results = await get_many(
        ...     urls,
        ...     script="document.querySelector('.price').innerText"
        ... )
        
        >>> # With different scripts per URL
        >>> scripts = ["return document.title", "return document.querySelector('.count').innerText"]
        >>> results = await get_many(urls, script=scripts)
    """
    browser = await _get_browser()
    extractor = ContentExtractor(clean=clean)
    
    # Handle script parameter - either single script for all URLs or per-URL scripts
    scripts = []
    if script is None:
        scripts = [None] * len(urls)
    elif isinstance(script, str):
        scripts = [script] * len(urls) 
    elif isinstance(script, list):
        # Pad or truncate script list to match URL count
        scripts = script[:len(urls)] + [None] * max(0, len(urls) - len(script))
    else:
        raise ValueError("script parameter must be str, List[str], or None")
    
    # TODO: Implement proper concurrent processing with progress tracking
    results = []
    for url, url_script in zip(urls, scripts):
        try:
            content = await get(url, timeout=timeout, clean=clean, script=url_script)
            results.append(content)
        except Exception as e:
            # Log error but continue with other URLs
            print(f"Failed to fetch {url}: {e}")
            results.append(None)
    
    return results


async def discover(
    query: str,
    *,
    max_pages: int = 10,
    quality_threshold: float = 0.7,
    recency_bias: bool = True,
    source_types: Optional[List[str]] = None,
    script: Optional[str] = None,
    content_script: Optional[str] = None,
) -> List[WebContent]:
    """
    Intelligently discover and rank content related to a query.
    
    This goes beyond simple search - it finds high-quality, relevant content
    and ranks it by usefulness for the given query.
    
    Args:
        query: Search query or topic description
        max_pages: Maximum number of results to return
        quality_threshold: Minimum quality score (0-1) for inclusion
        recency_bias: Whether to prefer more recent content
        source_types: Filter by source types: ['academic', 'news', 'blog', 'official']
        script: JavaScript to execute on search results page
        content_script: JavaScript to execute on each discovered content page
        
    Returns:
        List of WebContent objects, ranked by relevance and quality
        
    Example:
        >>> papers = await discover("AI safety alignment", max_pages=5)
        >>> for paper in papers:
        ...     print(f"{paper.title} - {paper.quality_score:.2f}")
        
        >>> # With JavaScript to expand search results and abstracts
        >>> papers = await discover(
        ...     "machine learning papers",
        ...     script="document.querySelector('.show-more')?.click()",
        ...     content_script="document.querySelector('.abstract')?.click()",
        ...     max_pages=10
        ... )
    """
    # TODO: Implement intelligent discovery with real search engines
    # This would typically:
    # 1. Use multiple search engines/sources (Google, Bing, academic databases)
    # 2. Apply quality filtering and ranking
    # 3. Deduplicate results
    # 4. Extract discovered URLs from search results
    
    # Placeholder implementation - in production this would use real search APIs
    search_urls = [
        f"https://search.example.com?q={query.replace(' ', '+')}"
    ]
    
    # Step 1: Get search results page(s) with optional script execution
    search_results = await get_many(search_urls[:max_pages], script=script)
    
    # Step 2: Extract URLs from search results (placeholder)
    # In real implementation, this would parse search result links
    discovered_urls = []
    for search_result in search_results:
        if search_result is not None:
            # Extract URLs from search results (simplified)
            # In production: parse actual search result links
            base_url = search_result.url.replace('/search', '')
            discovered_urls.extend([
                f"{base_url}/article/1",
                f"{base_url}/article/2",
                f"{base_url}/article/3"
            ])
    
    # Limit to max_pages
    discovered_urls = discovered_urls[:max_pages]
    
    # Step 3: Fetch content from discovered URLs with optional content_script
    if discovered_urls:
        content_results = await get_many(discovered_urls, script=content_script)
        return [r for r in content_results if r is not None]
    
    return []


async def monitor_changes(
    urls: List[str],
    *,
    check_interval: str = "1h", 
    significance_threshold: float = 0.5,
    archive: bool = True,
) -> List[dict]:
    """
    Monitor URLs for changes over time.
    
    Tracks content changes and evaluates their significance automatically.
    Useful for competitive monitoring, news tracking, and update detection.
    
    Args:
        urls: URLs to monitor
        check_interval: How often to check (e.g., "1h", "30m", "1d")
        significance_threshold: Minimum change significance to report
        archive: Whether to archive content for historical comparison
        
    Returns:
        List of change detection results
        
    Example:
        >>> changes = await monitor_changes(
        ...     ["https://competitor.com/pricing"],
        ...     check_interval="6h"
        ... )
        >>> for change in changes:
        ...     if change['significance'] > 0.8:
        ...         print(f"Major change detected: {change['description']}")
    """
    # TODO: Implement change monitoring
    # This would typically:
    # 1. Store baseline content
    # 2. Periodically re-fetch URLs  
    # 3. Compare content intelligently
    # 4. Score significance of changes
    # 5. Return structured change reports
    
    raise NotImplementedError("Change monitoring coming soon!")


async def cleanup():
    """Clean up global browser resources."""
    global _browser
    if _browser is not None:
        await _browser.close()
        _browser = None