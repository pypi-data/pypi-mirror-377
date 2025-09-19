"""
Browser control and page fetching.

This module handles all browser automation using Playwright,
with intelligent defaults and error handling.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from playwright.async_api import async_playwright, Browser as PlaywrightBrowser, Page


@dataclass
class BrowserConfig:
    """Configuration for browser behavior."""
    headless: bool = True
    timeout: int = 30000  # 30 seconds in milliseconds
    user_agent: Optional[str] = None
    viewport: Dict[str, int] = None
    extra_args: List[str] = None
    
    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}
        if self.extra_args is None:
            self.extra_args = []


class Browser:
    """
    High-level browser control for content extraction.
    
    Manages Playwright browser instances with intelligent defaults,
    error handling, and resource cleanup.
    """
    
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self._playwright = None
        self._browser: Optional[PlaywrightBrowser] = None
        self._pages: List[Page] = []
        self._is_started = False
    
    async def start(self):
        """Initialize the browser."""
        if self._is_started:
            return
        
        self._playwright = await async_playwright().start()
        
        # Launch browser with configuration
        launch_args = {
            "headless": self.config.headless,
            "args": self.config.extra_args,
        }
        
        self._browser = await self._playwright.chromium.launch(**launch_args)
        self._is_started = True
    
    async def close(self):
        """Clean up browser resources."""
        if not self._is_started:
            return
        
        # Close all pages
        for page in self._pages:
            await page.close()
        self._pages.clear()
        
        # Close browser
        if self._browser:
            await self._browser.close()
            self._browser = None
        
        # Stop playwright
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        
        self._is_started = False
    
    async def fetch_page(
        self,
        url: str,
        *,
        wait_for: Optional[str] = None,
        timeout: int = 30,
        stealth: bool = False,
        script_before: Optional[str] = None,
        script_after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch a single page and return structured data.
        
        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for before returning
            timeout: Timeout in seconds
            stealth: Whether to use stealth mode (anti-detection)
            script_before: JavaScript to execute after page load, before content extraction
            script_after: JavaScript to execute after content extraction (if needed)
            
        Returns:
            Dict with url, html, status, load_time, title, script_result, script_error
        """
        if not self._is_started:
            await self.start()
        
        start_time = time.time()
        
        # Create new page
        page = await self._browser.new_page()
        self._pages.append(page)
        
        try:
            # Configure page
            await page.set_viewport_size(self.config.viewport)
            
            if self.config.user_agent:
                await page.set_extra_http_headers({
                    "User-Agent": self.config.user_agent
                })
            
            if stealth:
                # Basic stealth mode - can be enhanced
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)
            
            # Navigate to page
            response = await page.goto(
                url,
                timeout=timeout * 1000,
                wait_until="domcontentloaded"
            )
            
            # Wait for specific element if requested
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=timeout * 1000)
            
            # Execute script_before if provided
            script_result = None
            script_error = None
            if script_before:
                try:
                    script_result = await page.evaluate(script_before)
                except Exception as e:
                    script_error = f"Script execution error: {str(e)}"
            
            # Extract page data
            html = await page.content()
            title = await page.title()
            
            # Execute script_after if provided (can access extracted content)
            if script_after and script_error is None:
                try:
                    script_after_result = await page.evaluate(script_after)
                    # If we had a previous result, combine them
                    if script_result is not None:
                        script_result = {
                            "script_before": script_result,
                            "script_after": script_after_result
                        }
                    else:
                        script_result = script_after_result
                except Exception as e:
                    script_error = f"Script after execution error: {str(e)}"
            
            load_time = time.time() - start_time
            
            # Build result dictionary
            result = {
                "url": url,
                "html": html,
                "title": title,
                "status": response.status if response else 0,
                "load_time": load_time,
            }
            
            # Add script results if any scripts were executed
            if script_before or script_after:
                result["script_result"] = script_result
                result["script_error"] = script_error
            
            return result
        
        except Exception as e:
            load_time = time.time() - start_time
            
            # Return error information
            result = {
                "url": url,
                "html": "",
                "title": "",
                "status": 0,
                "load_time": load_time,
                "error": str(e),
            }
            
            # Add script fields if scripts were requested
            if script_before or script_after:
                result["script_result"] = None
                result["script_error"] = f"Page load failed, scripts not executed: {str(e)}"
            
            return result
        
        finally:
            # Clean up page
            await page.close()
            if page in self._pages:
                self._pages.remove(page)
    
    async def fetch_many(
        self,
        urls: List[str],
        *,
        max_concurrent: int = 5,
        timeout: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple pages concurrently.
        
        Args:
            urls: List of URLs to fetch
            max_concurrent: Maximum concurrent requests
            timeout: Timeout per request in seconds
            
        Returns:
            List of page data dictionaries
        """
        if not self._is_started:
            await self.start()
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.fetch_page(url, timeout=timeout)
        
        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error dictionaries
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "url": urls[i],
                    "html": "",
                    "title": "",
                    "status": 0,
                    "load_time": 0.0,
                    "error": str(result),
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def take_screenshot(
        self,
        url: str,
        *,
        selector: Optional[str] = None,
        full_page: bool = False,
        timeout: int = 30,
    ) -> bytes:
        """
        Take a screenshot of a page or element.
        
        Args:
            url: URL to screenshot
            selector: CSS selector to screenshot (or full page if None)
            full_page: Whether to capture the full scrollable page
            timeout: Timeout in seconds
            
        Returns:
            Screenshot as bytes (PNG format)
        """
        if not self._is_started:
            await self.start()
        
        page = await self._browser.new_page()
        self._pages.append(page)
        
        try:
            await page.set_viewport_size(self.config.viewport)
            await page.goto(url, timeout=timeout * 1000)
            
            if selector:
                # Screenshot specific element
                element = await page.wait_for_selector(selector, timeout=timeout * 1000)
                screenshot = await element.screenshot()
            else:
                # Screenshot full page or viewport
                screenshot = await page.screenshot(full_page=full_page)
            
            return screenshot
        
        finally:
            await page.close()
            if page in self._pages:
                self._pages.remove(page)
    
    async def execute_script(
        self,
        url: str,
        script: str,
        *,
        timeout: int = 30,
    ) -> Any:
        """
        Execute JavaScript on a page and return the result.
        
        Args:
            url: URL to load
            script: JavaScript code to execute
            timeout: Timeout in seconds
            
        Returns:
            Script execution result
        """
        if not self._is_started:
            await self.start()
        
        page = await self._browser.new_page()
        self._pages.append(page)
        
        try:
            await page.goto(url, timeout=timeout * 1000)
            result = await page.evaluate(script)
            return result
        
        finally:
            await page.close()
            if page in self._pages:
                self._pages.remove(page)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()