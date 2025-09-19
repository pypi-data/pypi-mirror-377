# Crawailer API Reference

## Core Functions

### `get(url, **options) -> WebContent`

Extract content from a single URL with optional JavaScript execution.

**Parameters:**
- `url` (str): The URL to fetch
- `wait_for` (str, optional): CSS selector to wait for before extraction
- `timeout` (int, default=30): Request timeout in seconds
- `clean` (bool, default=True): Whether to clean and optimize content
- `extract_links` (bool, default=True): Whether to extract links
- `extract_metadata` (bool, default=True): Whether to extract metadata
- `script` (str, optional): JavaScript to execute (alias for `script_before`)
- `script_before` (str, optional): JavaScript to execute before content extraction
- `script_after` (str, optional): JavaScript to execute after content extraction

**Returns:** `WebContent` object with extracted content and metadata

**Example:**
```python
# Basic usage
content = await get("https://example.com")

# With JavaScript execution
content = await get(
    "https://dynamic-site.com",
    script="document.querySelector('.price').textContent",
    wait_for=".price-loaded"
)

# Before/after pattern
content = await get(
    "https://spa.com",
    script_before="document.querySelector('.load-more')?.click()",
    script_after="document.querySelectorAll('.item').length"
)
```

### `get_many(urls, **options) -> List[WebContent]`

Extract content from multiple URLs efficiently with concurrent processing.

**Parameters:**
- `urls` (List[str]): List of URLs to fetch
- `max_concurrent` (int, default=5): Maximum concurrent requests
- `timeout` (int, default=30): Request timeout per URL
- `clean` (bool, default=True): Whether to clean content
- `progress` (bool, default=False): Whether to show progress bar
- `script` (str | List[str], optional): JavaScript for all URLs or per-URL scripts

**Returns:** `List[WebContent]` (failed URLs return None)

**Example:**
```python
# Batch processing
urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
results = await get_many(urls, max_concurrent=3)

# Same script for all URLs
results = await get_many(
    urls,
    script="document.querySelector('.title').textContent"
)

# Different scripts per URL
scripts = [
    "document.title",
    "document.querySelector('.price').textContent", 
    "document.querySelectorAll('.item').length"
]
results = await get_many(urls, script=scripts)
```

### `discover(query, **options) -> List[WebContent]`

Intelligently discover and rank content related to a query.

**Parameters:**
- `query` (str): Search query or topic description
- `max_pages` (int, default=10): Maximum results to return
- `quality_threshold` (float, default=0.7): Minimum quality score
- `recency_bias` (bool, default=True): Prefer recent content
- `source_types` (List[str], optional): Filter by source types
- `script` (str, optional): JavaScript for search results pages
- `content_script` (str, optional): JavaScript for discovered content pages

**Returns:** `List[WebContent]` ranked by relevance and quality

**Example:**
```python
# Basic discovery
results = await discover("machine learning tutorials")

# With JavaScript interaction
results = await discover(
    "AI research papers",
    script="document.querySelector('.show-more')?.click()",
    content_script="document.querySelector('.abstract').textContent",
    max_pages=5
)
```

### `cleanup()`

Clean up global browser resources.

**Example:**
```python
# Clean up at end of script
await cleanup()
```

## Data Classes

### `WebContent`

Structured representation of extracted web content.

**Core Properties:**
- `url` (str): Source URL
- `title` (str): Extracted page title
- `markdown` (str): LLM-optimized markdown content
- `text` (str): Clean human-readable text
- `html` (str): Original HTML content

**Metadata Properties:**
- `author` (str | None): Content author
- `published` (datetime | None): Publication date
- `reading_time` (str): Estimated reading time
- `word_count` (int): Word count
- `language` (str): Content language
- `quality_score` (float): Content quality (0-10)

**Semantic Properties:**
- `content_type` (str): Detected content type (article, product, etc.)
- `topics` (List[str]): Extracted topics
- `entities` (Dict[str, List[str]]): Named entities

**Relationship Properties:**
- `links` (List[Dict]): Extracted links with metadata
- `images` (List[Dict]): Image information

**Technical Properties:**
- `status_code` (int): HTTP status code
- `load_time` (float): Page load time
- `content_hash` (str): Content hash for deduplication
- `extracted_at` (datetime): Extraction timestamp

**JavaScript Properties:**
- `script_result` (Any | None): JavaScript execution result
- `script_error` (str | None): JavaScript execution error

**Computed Properties:**
- `summary` (str): Brief content summary
- `readable_summary` (str): Human-friendly summary with metadata
- `has_script_result` (bool): Whether JavaScript result is available
- `has_script_error` (bool): Whether JavaScript error occurred

**Methods:**
- `save(path, format="auto")`: Save content to file

**Example:**
```python
content = await get("https://example.com", script="document.title")

# Access content
print(content.title)
print(content.markdown[:100])
print(content.text[:100])

# Access metadata
print(f"Author: {content.author}")
print(f"Reading time: {content.reading_time}")
print(f"Quality: {content.quality_score}/10")

# Access JavaScript results
if content.has_script_result:
    print(f"Script result: {content.script_result}")

if content.has_script_error:
    print(f"Script error: {content.script_error}")

# Save content
content.save("article.md")  # Saves as markdown
content.save("article.json")  # Saves as JSON with all metadata
```

### `BrowserConfig`

Configuration for browser behavior.

**Properties:**
- `headless` (bool, default=True): Run browser in headless mode
- `timeout` (int, default=30000): Request timeout in milliseconds
- `user_agent` (str | None): Custom user agent
- `viewport` (Dict[str, int], default={"width": 1920, "height": 1080}): Viewport size
- `extra_args` (List[str], default=[]): Additional browser arguments

**Example:**
```python
from crawailer import BrowserConfig, Browser

config = BrowserConfig(
    headless=False,  # Show browser window
    timeout=60000,   # 60 second timeout
    user_agent="Custom Bot 1.0",
    viewport={"width": 1280, "height": 720}
)

browser = Browser(config)
```

## Browser Class

Lower-level browser control for advanced use cases.

### `Browser(config=None)`

**Methods:**

#### `async start()`
Initialize the browser instance.

#### `async close()`
Clean up browser resources.

#### `async fetch_page(url, **options) -> Dict[str, Any]`
Fetch a single page with full control.

**Parameters:**
- `url` (str): URL to fetch
- `wait_for` (str, optional): CSS selector to wait for
- `timeout` (int, default=30): Timeout in seconds
- `stealth` (bool, default=False): Enable stealth mode
- `script_before` (str, optional): JavaScript before content extraction
- `script_after` (str, optional): JavaScript after content extraction

**Returns:** Dictionary with page data

#### `async fetch_many(urls, **options) -> List[Dict[str, Any]]`
Fetch multiple pages concurrently.

#### `async take_screenshot(url, **options) -> bytes`
Take a screenshot of a page.

**Parameters:**
- `url` (str): URL to screenshot
- `selector` (str, optional): CSS selector to screenshot
- `full_page` (bool, default=False): Capture full scrollable page
- `timeout` (int, default=30): Timeout in seconds

**Returns:** Screenshot as PNG bytes

#### `async execute_script(url, script, **options) -> Any`
Execute JavaScript on a page and return result.

**Example:**
```python
from crawailer import Browser, BrowserConfig

config = BrowserConfig(headless=False)
browser = Browser(config)

async with browser:
    # Fetch page data
    page_data = await browser.fetch_page(
        "https://example.com",
        script_before="window.scrollTo(0, document.body.scrollHeight)",
        script_after="document.querySelectorAll('.item').length"
    )
    
    # Take screenshot
    screenshot = await browser.take_screenshot("https://example.com")
    with open("screenshot.png", "wb") as f:
        f.write(screenshot)
    
    # Execute JavaScript
    result = await browser.execute_script(
        "https://example.com",
        "document.title + ' - ' + document.querySelectorAll('a').length + ' links'"
    )
    print(result)
```

## Content Extraction

### `ContentExtractor`

Transforms raw HTML into structured WebContent.

**Parameters:**
- `clean` (bool, default=True): Clean and normalize text
- `extract_links` (bool, default=True): Extract link information
- `extract_metadata` (bool, default=True): Extract metadata
- `extract_images` (bool, default=False): Extract image information

**Methods:**

#### `async extract(page_data) -> WebContent`
Extract structured content from page data.

**Example:**
```python
from crawailer.content import ContentExtractor
from crawailer.browser import Browser

browser = Browser()
extractor = ContentExtractor(
    clean=True,
    extract_links=True,
    extract_metadata=True,
    extract_images=True
)

async with browser:
    page_data = await browser.fetch_page("https://example.com")
    content = await extractor.extract(page_data)
    print(content.title)
```

## Error Handling

### Custom Exceptions

```python
from crawailer.exceptions import (
    CrawlerError,           # Base exception
    TimeoutError,           # Request timeout
    CloudflareProtected,    # Cloudflare protection detected
    PaywallDetected,        # Paywall detected
    RateLimitError,         # Rate limit exceeded
    ContentExtractionError  # Content extraction failed
)

try:
    content = await get("https://protected-site.com")
except CloudflareProtected:
    # Try with stealth mode
    content = await get("https://protected-site.com", stealth=True)
except PaywallDetected as e:
    print(f"Paywall detected. Archive URL: {e.archive_url}")
except TimeoutError:
    # Increase timeout
    content = await get("https://slow-site.com", timeout=60)
```

## JavaScript Execution

### Script Patterns

#### Simple Execution
```python
# Extract single value
content = await get(url, script="document.title")
print(content.script_result)  # Page title
```

#### Complex Operations
```python
# Multi-step JavaScript
complex_script = """
// Scroll to load content
window.scrollTo(0, document.body.scrollHeight);
await new Promise(resolve => setTimeout(resolve, 2000));

// Extract data
const items = Array.from(document.querySelectorAll('.item')).map(item => ({
    title: item.querySelector('.title')?.textContent,
    price: item.querySelector('.price')?.textContent
}));

return items;
"""

content = await get(url, script=complex_script)
items = content.script_result  # List of extracted items
```

#### Before/After Pattern
```python
content = await get(
    url,
    script_before="document.querySelector('.load-more')?.click()",
    script_after="document.querySelectorAll('.item').length"
)

if isinstance(content.script_result, dict):
    print(f"Action result: {content.script_result['script_before']}")
    print(f"Items count: {content.script_result['script_after']}")
```

#### Error Handling
```python
content = await get(url, script="document.querySelector('.missing').click()")

if content.has_script_error:
    print(f"JavaScript error: {content.script_error}")
    # Use fallback content
    print(f"Fallback: {content.text[:100]}")
else:
    print(f"Result: {content.script_result}")
```

### Framework Detection

#### React Applications
```python
react_script = """
if (window.React) {
    return {
        framework: 'React',
        version: React.version,
        hasRouter: !!window.ReactRouter,
        componentCount: document.querySelectorAll('[data-reactroot] *').length
    };
}
return null;
"""

content = await get("https://react-app.com", script=react_script)
```

#### Vue Applications
```python
vue_script = """
if (window.Vue) {
    return {
        framework: 'Vue',
        version: Vue.version,
        hasRouter: !!window.VueRouter,
        hasVuex: !!window.Vuex
    };
}
return null;
"""

content = await get("https://vue-app.com", script=vue_script)
```

## Performance Optimization

### Batch Processing
```python
# Process large URL lists efficiently
urls = [f"https://site.com/page/{i}" for i in range(100)]

# Process in batches
batch_size = 10
all_results = []

for i in range(0, len(urls), batch_size):
    batch = urls[i:i+batch_size]
    results = await get_many(batch, max_concurrent=5)
    all_results.extend(results)
    
    # Rate limiting
    await asyncio.sleep(1)
```

### Memory Management
```python
# For long-running processes
import gc

for batch in url_batches:
    results = await get_many(batch)
    process_results(results)
    
    # Clear references and force garbage collection
    del results
    gc.collect()
```

### Timeout Configuration
```python
# Adjust timeouts based on site characteristics
fast_sites = await get_many(urls, timeout=10)
slow_sites = await get_many(urls, timeout=60)
```

## MCP Integration

### Server Setup
```python
from crawailer.mcp import create_mcp_server

# Create MCP server with default tools
server = create_mcp_server()

# Custom MCP tool
@server.tool("extract_product_data")
async def extract_product_data(url: str) -> dict:
    content = await get(
        url,
        script="""
        ({
            name: document.querySelector('.product-name')?.textContent,
            price: document.querySelector('.price')?.textContent,
            rating: document.querySelector('.rating')?.textContent
        })
        """
    )
    
    return {
        'title': content.title,
        'product_data': content.script_result,
        'metadata': {
            'word_count': content.word_count,
            'quality_score': content.quality_score
        }
    }
```

## CLI Interface

### Basic Commands
```bash
# Extract content from URL
crawailer get https://example.com

# Batch processing
crawailer get-many urls.txt --output results.json

# Discovery
crawailer discover "AI research" --max-pages 10

# Setup (install browsers)
crawailer setup
```

### JavaScript Execution
```bash
# Execute JavaScript
crawailer get https://spa.com --script "document.title" --wait-for ".loaded"

# Save with script results
crawailer get https://dynamic.com --script "window.data" --output content.json
```

## Advanced Usage

### Custom Content Extractors
```python
from crawailer.content import ContentExtractor

class CustomExtractor(ContentExtractor):
    async def extract(self, page_data):
        content = await super().extract(page_data)
        
        # Add custom processing
        if 'product' in content.content_type:
            content.custom_data = self.extract_product_details(content.html)
        
        return content
    
    def extract_product_details(self, html):
        # Custom extraction logic
        pass

# Use custom extractor
from crawailer.api import _get_browser

browser = await _get_browser()
extractor = CustomExtractor()

page_data = await browser.fetch_page(url)
content = await extractor.extract(page_data)
```

### Session Management
```python
from crawailer.browser import Browser

# Persistent browser session
browser = Browser()
await browser.start()

try:
    # Login
    await browser.fetch_page(
        "https://site.com/login",
        script_after="""
        document.querySelector('#username').value = 'user';
        document.querySelector('#password').value = 'pass';
        document.querySelector('#login').click();
        """
    )
    
    # Access protected content
    protected_content = await browser.fetch_page("https://site.com/dashboard")
    
finally:
    await browser.close()
```

This API reference provides comprehensive documentation for all Crawailer functionality, with particular emphasis on the JavaScript execution capabilities that set it apart from traditional web scrapers.