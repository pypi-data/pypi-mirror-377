# Enhancement Proposal: JavaScript Execution in High-Level API

## Summary
Add optional JavaScript execution capabilities to the high-level API functions (`get`, `get_many`, `discover`) to enable DOM manipulation and dynamic content interaction without requiring direct Browser class usage.

## Motivation

Currently, users must drop down to the `Browser` class to execute JavaScript:

```python
# Current approach - requires Browser class
from crawailer import Browser, BrowserConfig

browser = Browser(BrowserConfig())
await browser.start()
result = await browser.execute_script(url, script)
await browser.stop()
```

Many common use cases would benefit from JavaScript execution in the convenience API:
- Clicking "Load More" buttons before extraction
- Scrolling to trigger lazy loading
- Extracting computed values from JavaScript
- Interacting with dynamic UI elements

## Proposed API Changes

### 1. Enhanced `get` Function

```python
async def get(
    url: str,
    *,
    wait_for: Optional[str] = None,
    script: Optional[str] = None,  # NEW
    script_before: Optional[str] = None,  # NEW - run before extraction
    script_after: Optional[str] = None,  # NEW - run after extraction
    timeout: int = 30,
    clean: bool = True,
    extract_links: bool = True,
    extract_metadata: bool = True,
) -> WebContent:
    """
    Get content from a single URL with optional JavaScript execution.
    
    Args:
        script: JavaScript to execute before content extraction (alias for script_before)
        script_before: JavaScript to execute after page load, before extraction
        script_after: JavaScript to execute after extraction (result available as content.script_result)
    """
```

### 2. Enhanced `get_many` Function

```python
async def get_many(
    urls: List[str],
    *,
    script: Optional[Union[str, List[str]]] = None,  # NEW
    max_concurrent: int = 5,
    timeout: int = 30,
    **kwargs
) -> List[WebContent]:
    """
    Args:
        script: JavaScript to execute on each page (string for all, list for per-URL)
    """
```

### 3. Enhanced `discover` Function

```python
async def discover(
    query: str,
    *,
    max_pages: int = 10,
    script: Optional[str] = None,  # NEW - for search results page
    content_script: Optional[str] = None,  # NEW - for each discovered page
    **kwargs
) -> List[WebContent]:
    """
    Args:
        script: JavaScript to execute on search results pages
        content_script: JavaScript to execute on each discovered content page
    """
```

## Usage Examples

### Example 1: E-commerce Price Extraction
```python
# Extract dynamic price that loads via JavaScript
content = await web.get(
    "https://shop.example.com/product",
    wait_for=".price-container",
    script="document.querySelector('.final-price').innerText"
)
print(f"Price: {content.script_result}")
```

### Example 2: Infinite Scroll Content
```python
# Scroll to bottom to load all content
content = await web.get(
    "https://infinite-scroll.example.com",
    script_before="""
        // Scroll to bottom multiple times
        for(let i = 0; i < 3; i++) {
            window.scrollTo(0, document.body.scrollHeight);
            await new Promise(r => setTimeout(r, 1000));
        }
    """,
    wait_for=".end-of-content"
)
```

### Example 3: Click to Expand Content
```python
# Click all "Read More" buttons before extraction
content = await web.get(
    "https://blog.example.com/article",
    script_before="""
        document.querySelectorAll('.read-more-btn').forEach(btn => btn.click());
    """
)
```

### Example 4: Batch Processing with Different Scripts
```python
# Different scripts for different URLs
urls = [
    "https://site1.com",  # Needs scrolling
    "https://site2.com",  # Needs button click
    "https://site3.com",  # No script needed
]

scripts = [
    "window.scrollTo(0, document.body.scrollHeight)",
    "document.querySelector('.load-all').click()",
    None
]

results = await web.get_many(urls, script=scripts)
```

### Example 5: Complex Discovery Flow
```python
# Advanced search with pagination
results = await web.discover(
    "machine learning papers",
    script="""
        // Click "Show More Results" on search page
        const moreBtn = document.querySelector('.show-more');
        if(moreBtn) moreBtn.click();
    """,
    content_script="""
        // Expand abstracts on each paper page
        document.querySelector('.expand-abstract')?.click();
    """
)
```

## Implementation Details

### WebContent Enhancement
```python
@dataclass
class WebContent:
    # ... existing fields ...
    script_result: Optional[Any] = None  # NEW - result from JavaScript execution
    script_error: Optional[str] = None  # NEW - any JS execution errors
```

### Browser Method Updates
```python
async def fetch_page(
    self,
    url: str,
    *,
    wait_for: Optional[str] = None,
    script_before: Optional[str] = None,  # NEW
    script_after: Optional[str] = None,  # NEW
    timeout: int = 30,
    stealth: bool = False,
) -> Dict[str, Any]:
    # ... existing code ...
    
    # After page load, before extraction
    if script_before:
        try:
            script_result = await page.evaluate(script_before)
            page_data["script_result"] = script_result
        except Exception as e:
            page_data["script_error"] = str(e)
    
    # ... extraction ...
    
    # After extraction if needed
    if script_after:
        after_result = await page.evaluate(script_after)
        page_data["script_after_result"] = after_result
```

## Benefits

1. **Simplified API**: No need to manage Browser instances for common JS tasks
2. **Backward Compatible**: All changes are optional parameters
3. **Flexible**: Supports before/after extraction scripts
4. **Batch Support**: Can apply different scripts to different URLs
5. **Error Handling**: Graceful degradation if scripts fail

## Considerations

1. **Security**: Scripts run in page context - users must trust their scripts
2. **Performance**: JavaScript execution adds latency
3. **Debugging**: Script errors should be clearly reported
4. **Documentation**: Need clear examples of common patterns

## Alternative Approaches Considered

1. **Predefined Actions**: Instead of raw JS, provide actions like `click`, `scroll`, `fill`
   - Pros: Safer, easier to use
   - Cons: Less flexible, can't cover all cases

2. **Separate Functions**: `get_with_script`, `get_many_with_script`
   - Pros: Cleaner separation
   - Cons: API proliferation

3. **Script Templates**: Provide common script templates
   - Pros: Easier for beginners
   - Cons: Maintenance burden

## Recommendation

Implement the proposed changes with optional script parameters. This provides maximum flexibility while maintaining backward compatibility. Start with `script` parameter only, then add `script_before`/`script_after` if needed based on user feedback.

## Next Steps

1. Update `api.py` to accept script parameters
2. Modify `Browser.fetch_page` to execute scripts
3. Update `WebContent` to include script results
4. Add comprehensive tests for JS execution
5. Update documentation with examples
6. Consider adding script templates as utilities