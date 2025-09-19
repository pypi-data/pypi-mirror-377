# Crawailer JavaScript API Documentation

## Overview

Crawailer provides comprehensive JavaScript execution capabilities that enable dynamic content extraction from modern web applications. Unlike traditional HTTP scrapers, Crawailer uses a real browser (Playwright) to execute JavaScript and extract content from single-page applications (SPAs), dynamic sites, and JavaScript-heavy pages.

## Key Features

- **Full JavaScript Execution**: Execute arbitrary JavaScript code using `page.evaluate()`
- **Before/After Script Patterns**: Run scripts before and after content extraction
- **SPA Support**: Handle React, Vue, Angular, and other modern frameworks
- **Dynamic Content**: Extract content that's loaded via AJAX or user interactions
- **Error Handling**: Comprehensive error capture and graceful degradation
- **Performance Monitoring**: Extract timing and memory metrics
- **User Interaction**: Simulate clicks, form submissions, and complex workflows

## Basic Usage

### Simple JavaScript Execution

```python
from crawailer import get

# Extract dynamic content
content = await get(
    "https://example.com",
    script="document.querySelector('.dynamic-price').innerText"
)

print(f"Price: {content.script_result}")
print(f"Has script result: {content.has_script_result}")
```

### Waiting for Dynamic Content

```python
# Wait for element and extract data
content = await get(
    "https://spa-app.com",
    script="document.querySelector('.loaded-content').textContent",
    wait_for=".loaded-content"  # Wait for element to appear
)
```

### Complex JavaScript Operations

```python
# Execute complex JavaScript
complex_script = """
// Scroll to load more content
window.scrollTo(0, document.body.scrollHeight);

// Wait for new content to load
await new Promise(resolve => setTimeout(resolve, 2000));

// Extract all product data
const products = Array.from(document.querySelectorAll('.product')).map(p => ({
    name: p.querySelector('.name')?.textContent,
    price: p.querySelector('.price')?.textContent,
    rating: p.querySelector('.rating')?.textContent
}));

return products;
"""

content = await get("https://ecommerce-site.com", script=complex_script)
products = content.script_result
```

## Advanced Patterns

### Before/After Script Execution

```python
# Execute script before content extraction, then after
content = await get(
    "https://dynamic-site.com",
    script_before="document.querySelector('.load-more')?.click()",
    script_after="document.querySelectorAll('.item').length"
)

if isinstance(content.script_result, dict):
    print(f"Triggered loading: {content.script_result['script_before']}")
    print(f"Items loaded: {content.script_result['script_after']}")
```

### Form Interaction and Submission

```python
# Fill and submit forms
form_script = """
// Fill login form
document.querySelector('#username').value = 'testuser';
document.querySelector('#password').value = 'testpass';

// Submit form
document.querySelector('#login-form').submit();

// Wait for redirect
await new Promise(resolve => setTimeout(resolve, 3000));

return 'form submitted';
"""

content = await get("https://app.com/login", script=form_script)
```

### Performance Monitoring

```python
# Extract performance metrics
perf_script = """
({
    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
    domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
    resources: performance.getEntriesByType('resource').length,
    memory: performance.memory ? {
        used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
        total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024)
    } : null
})
"""

content = await get("https://example.com", script=perf_script)
metrics = content.script_result
print(f"Load time: {metrics['loadTime']}ms")
```

## Batch Processing

### Same Script for Multiple URLs

```python
from crawailer import get_many

urls = [
    "https://site1.com/product/1",
    "https://site1.com/product/2", 
    "https://site1.com/product/3"
]

# Extract price from all products
results = await get_many(
    urls,
    script="document.querySelector('.price')?.textContent"
)

for result in results:
    if result and result.script_result:
        print(f"{result.url}: {result.script_result}")
```

### Different Scripts per URL

```python
# Custom script for each URL
urls = ["https://react-app.com", "https://vue-app.com", "https://angular-app.com"]
scripts = [
    "window.React ? 'React ' + React.version : 'No React'",
    "window.Vue ? 'Vue ' + Vue.version : 'No Vue'", 
    "window.ng ? 'Angular detected' : 'No Angular'"
]

results = await get_many(urls, script=scripts)
```

## Intelligent Discovery

### Search Result Interaction

```python
from crawailer import discover

# Discover content with JavaScript interaction
results = await discover(
    "machine learning tutorials",
    script="document.querySelector('.show-more')?.click()",
    content_script="document.querySelector('.read-time')?.textContent",
    max_pages=5
)

for result in results:
    print(f"{result.title} - Reading time: {result.script_result}")
```

### Pagination Handling

```python
# Handle infinite scroll
pagination_script = """
let results = [];
let page = 0;

while (page < 3) {  // Load 3 pages
    // Scroll to bottom
    window.scrollTo(0, document.body.scrollHeight);
    
    // Wait for new content
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Extract current page items
    const items = Array.from(document.querySelectorAll('.item')).map(item => 
        item.textContent.trim()
    );
    
    results.push(...items);
    page++;
}

return results;
"""

content = await get("https://infinite-scroll-site.com", script=pagination_script)
```

## Error Handling

### JavaScript Error Capture

```python
content = await get(
    "https://example.com",
    script="document.querySelector('.nonexistent').click()"
)

if content.has_script_error:
    print(f"JavaScript error: {content.script_error}")
else:
    print(f"Result: {content.script_result}")
```

### Graceful Degradation

```python
# Try JavaScript, fall back to static content
try:
    content = await get(
        "https://dynamic-site.com",
        script="window.dynamicData || 'fallback'"
    )
    
    if content.has_script_error:
        # JavaScript failed, but we still have static content
        print(f"Using static content: {content.text[:100]}")
    else:
        print(f"Dynamic data: {content.script_result}")
        
except Exception as e:
    print(f"Complete failure: {e}")
```

## Modern Framework Integration

### React Applications

```python
# Extract React component data
react_script = """
// Find React root
const reactRoot = document.querySelector('[data-reactroot]') || document.querySelector('#root');

if (window.React && reactRoot) {
    // Get React fiber data (React 16+)
    const fiberKey = Object.keys(reactRoot).find(key => key.startsWith('__reactInternalInstance'));
    
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

### Vue Applications

```python
# Extract Vue app data
vue_script = """
if (window.Vue) {
    const app = document.querySelector('#app');
    
    return {
        framework: 'Vue',
        version: Vue.version,
        hasRouter: !!window.VueRouter,
        hasVuex: !!window.Vuex,
        rootComponent: app?.__vue__?.$options.name || 'unknown'
    };
}

return null;
"""

content = await get("https://vue-app.com", script=vue_script)
```

### Angular Applications

```python
# Extract Angular app data
angular_script = """
if (window.ng) {
    const platform = window.ng.platform || {};
    
    return {
        framework: 'Angular',
        version: window.ng.version?.full || 'unknown',
        hasRouter: !!window.ng.router,
        modules: Object.keys(platform).length
    };
}

return null;
"""

content = await get("https://angular-app.com", script=angular_script)
```

## WebContent Integration

### Accessing JavaScript Results

```python
content = await get("https://example.com", script="document.title")

# JavaScript result is available in WebContent object
print(f"Script result: {content.script_result}")
print(f"Has result: {content.has_script_result}")
print(f"Has error: {content.has_script_error}")

# Also access traditional content
print(f"Title: {content.title}")
print(f"Text: {content.text[:100]}")
print(f"Markdown: {content.markdown[:100]}")
```

### Combining Static and Dynamic Data

```python
# Extract both static content and dynamic data
dynamic_script = """
({
    dynamicPrice: document.querySelector('.dynamic-price')?.textContent,
    userCount: document.querySelector('.user-count')?.textContent,
    lastUpdated: document.querySelector('.last-updated')?.textContent
})
"""

content = await get("https://dashboard.com", script=dynamic_script)

# Use both static and dynamic content
analysis = {
    'title': content.title,
    'word_count': content.word_count,
    'reading_time': content.reading_time,
    'dynamic_data': content.script_result
}
```

## Performance Considerations

### Optimize JavaScript Execution

```python
# Lightweight scripts for better performance
fast_script = "document.title"  # Simple, fast

# Avoid heavy DOM operations
slow_script = """
// This is expensive - avoid if possible
const allElements = document.querySelectorAll('*');
return Array.from(allElements).map(el => el.tagName);
"""
```

### Batch Processing Optimization

```python
# Process in smaller batches for better memory usage
urls = [f"https://site.com/page/{i}" for i in range(100)]

batch_size = 10
results = []

for i in range(0, len(urls), batch_size):
    batch = urls[i:i+batch_size]
    batch_results = await get_many(batch, script="document.title")
    results.extend(batch_results)
    
    # Optional: small delay between batches
    await asyncio.sleep(1)
```

## Best Practices

### 1. Script Design

```python
# ✅ Good: Simple, focused scripts
good_script = "document.querySelector('.price').textContent"

# ❌ Avoid: Complex scripts that could fail
bad_script = """
try {
    const price = document.querySelector('.price').textContent.split('$')[1];
    const discountedPrice = parseFloat(price) * 0.9;
    return `$${discountedPrice.toFixed(2)}`;
} catch (e) {
    return null;
}
"""
```

### 2. Error Handling

```python
# Always check for script errors
content = await get(url, script=script)

if content.has_script_error:
    # Handle the error appropriately
    logging.warning(f"JavaScript error on {url}: {content.script_error}")
    # Use fallback approach
else:
    # Process successful result
    process_result(content.script_result)
```

### 3. Performance Monitoring

```python
import time

start_time = time.time()
content = await get(url, script=script)
duration = time.time() - start_time

if duration > 10:  # If taking too long
    logging.warning(f"Slow JavaScript execution on {url}: {duration:.2f}s")
```

## Common Use Cases

### E-commerce Data Extraction

```python
# Extract product information
product_script = """
({
    name: document.querySelector('.product-name')?.textContent,
    price: document.querySelector('.price')?.textContent,
    rating: document.querySelector('.rating')?.textContent,
    availability: document.querySelector('.stock-status')?.textContent,
    images: Array.from(document.querySelectorAll('.product-image img')).map(img => img.src)
})
"""

content = await get("https://shop.com/product/123", script=product_script)
product_data = content.script_result
```

### Social Media Content

```python
# Extract social media posts (be respectful of terms of service)
social_script = """
Array.from(document.querySelectorAll('.post')).slice(0, 10).map(post => ({
    text: post.querySelector('.post-text')?.textContent,
    author: post.querySelector('.author')?.textContent,
    timestamp: post.querySelector('.timestamp')?.textContent,
    likes: post.querySelector('.likes-count')?.textContent
}))
"""

content = await get("https://social-site.com/feed", script=social_script)
posts = content.script_result
```

### News and Articles

```python
# Extract article metadata
article_script = """
({
    headline: document.querySelector('h1')?.textContent,
    author: document.querySelector('.author')?.textContent,
    publishDate: document.querySelector('.publish-date')?.textContent,
    readingTime: document.querySelector('.reading-time')?.textContent,
    tags: Array.from(document.querySelectorAll('.tag')).map(tag => tag.textContent),
    wordCount: document.querySelector('.article-body')?.textContent.split(' ').length
})
"""

content = await get("https://news-site.com/article/123", script=article_script)
```

## Integration with AI Workflows

### Content Preparation for LLMs

```python
# Extract structured content for AI processing
ai_script = """
({
    mainContent: document.querySelector('main')?.textContent,
    headings: Array.from(document.querySelectorAll('h1, h2, h3')).map(h => ({
        level: h.tagName,
        text: h.textContent
    })),
    keyPoints: Array.from(document.querySelectorAll('.highlight, .callout')).map(el => el.textContent),
    metadata: {
        wordCount: document.body.textContent.split(' ').length,
        readingLevel: 'advanced',  // Could be calculated
        topics: Array.from(document.querySelectorAll('.topic-tag')).map(tag => tag.textContent)
    }
})
"""

content = await get("https://technical-blog.com/post", script=ai_script)
structured_data = content.script_result

# Now ready for AI processing
ai_prompt = f"""
Analyze this content:

Title: {content.title}
Main Content: {structured_data['mainContent'][:1000]}...
Key Points: {structured_data['keyPoints']}
Topics: {structured_data['metadata']['topics']}

Provide a summary and key insights.
"""
```

## Troubleshooting

### Common Issues

1. **Script Timeout**
   ```python
   # Increase timeout for slow scripts
   content = await get(url, script=script, timeout=60)
   ```

2. **Element Not Found**
   ```python
   # Use optional chaining and fallbacks
   safe_script = """
   document.querySelector('.target')?.textContent || 'not found'
   """
   ```

3. **JavaScript Not Loaded**
   ```python
   # Wait for JavaScript frameworks to load
   content = await get(
       url,
       script="typeof React !== 'undefined' ? React.version : 'React not loaded'",
       wait_for="[data-reactroot]"
   )
   ```

### Debug Mode

```python
# Enable verbose logging for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

content = await get(url, script=script)
```

This comprehensive JavaScript API enables Crawailer to handle modern web applications with the same ease as static sites, making it ideal for AI workflows that require rich, accurate content extraction.