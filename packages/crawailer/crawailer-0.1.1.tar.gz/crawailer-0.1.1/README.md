# 🕷️ Crawailer

**The web scraper that doesn't suck at JavaScript** ✨

> **Stop fighting modern websites.** While `requests` gives you empty `<div id="root"></div>`, Crawailer actually executes JavaScript and extracts real content from React, Vue, and Angular apps. Finally, web scraping that works in 2025.

> ⚡ **Claude Code's new best friend** - Your AI assistant can now access ANY website

```python
pip install crawailer
```

[![PyPI version](https://badge.fury.io/py/crawailer.svg)](https://badge.fury.io/py/crawailer)
[![Python Support](https://img.shields.io/pypi/pyversions/crawailer.svg)](https://pypi.org/project/crawailer/)

## ✨ Why Developers Choose Crawailer

**🔥 JavaScript That Actually Works**  
While other tools timeout or crash, Crawailer executes real JavaScript like a human browser

**⚡ Stupidly Fast**  
5-10x faster than BeautifulSoup with C-based parsing that doesn't make you wait

**🤖 AI Assistant Ready**  
Perfect markdown output that your Claude/GPT/local model will love

**🎯 Zero Learning Curve**  
`pip install` → works immediately → no 47-page configuration guides

**🧪 Production Battle-Tested**  
18 comprehensive test suites covering every edge case we could think of

**🎨 Actually Enjoyable**  
Rich terminal output, helpful errors, progress bars that don't lie

## 🚀 Quick Start

> *(Honestly, you probably don't need to read these examples - just ask your AI assistant to figure it out. That's what models are for! But here they are anyway...)*

### 🎬 See It In Action

**Basic Usage Demo** - Crawailer vs requests:
```bash
# View the demo locally
asciinema play demos/basic-usage.cast
```

**Claude Code Integration** - Give your AI web superpowers:
```bash
# View the Claude integration demo  
asciinema play demos/claude-integration.cast
```

*Don't have asciinema? `pip install asciinema` or run the demos yourself:*
```bash
# Clone the repo and run demos interactively
git clone https://git.supported.systems/MCP/crawailer.git
cd crawailer
python demo_basic_usage.py
python demo_claude_integration.py
```

```python
import crawailer as web

# Simple content extraction
content = await web.get("https://example.com")
print(content.markdown)  # Clean, LLM-ready markdown
print(content.text)      # Human-readable text
print(content.title)     # Extracted title

# JavaScript execution for dynamic content
content = await web.get(
    "https://spa-app.com",
    script="document.querySelector('.dynamic-price').textContent"
)
print(f"Price: {content.script_result}")

# Batch processing with JavaScript
results = await web.get_many(
    ["url1", "url2", "url3"],
    script="document.title + ' | ' + document.querySelector('.description')?.textContent"
)
for result in results:
    print(f"{result.title}: {result.script_result}")

# Smart discovery with interaction
research = await web.discover(
    "AI safety papers", 
    script="document.querySelector('.show-more')?.click()",
    max_pages=10
)
# Returns the most relevant content with enhanced extraction

# Compare: Traditional scraping fails on modern sites
# requests.get("https://react-app.com") → Empty <div id="root"></div>
# Crawailer → Full content + dynamic data
```

### 🧠 Claude Code MCP Integration

> *"Hey Claude, go grab that data from the React app"* ← This actually works now

```python
# Add to your Claude Code MCP server
from crawailer.mcp import create_mcp_server

@mcp_tool("web_extract")
async def extract_content(url: str, script: str = ""):
    """Extract content from any website with optional JavaScript execution"""
    content = await web.get(url, script=script)
    return {
        "title": content.title,
        "markdown": content.markdown,
        "script_result": content.script_result,
        "word_count": content.word_count
    }

# 🎉 No more "I can't access that site" 
# 🎉 No more copy-pasting content manually
# 🎉 Your AI can now browse the web like a human
```

## 🎯 Design Philosophy

### For Robots, By Humans
- **Predictive**: Anticipates what you need and provides it
- **Forgiving**: Handles errors gracefully with helpful suggestions  
- **Efficient**: Fast by default, with smart caching and concurrency
- **Composable**: Small, focused functions that work well together

### Perfect for AI Workflows
- **LLM-Optimized**: Clean markdown, structured data, semantic chunking
- **Context-Aware**: Extracts relationships and metadata automatically
- **Quality-Focused**: Built-in content quality assessment
- **Archive-Ready**: Designed for long-term storage and retrieval

## 📖 Use Cases

### 🤖 AI Agents & LLM Applications
**Problem**: Training data scattered across JavaScript-heavy academic sites
```python
# Research assistant workflow with JavaScript interaction
research = await web.discover(
    "quantum computing breakthroughs",
    script="document.querySelector('.show-abstract')?.click(); return document.querySelector('.full-text')?.textContent"
)
for paper in research:
    # Rich content includes JavaScript-extracted data
    summary = await llm.summarize(paper.markdown)
    dynamic_content = paper.script_result  # JavaScript execution result
    insights = await llm.extract_insights(paper.content + dynamic_content)
```

### 🛒 E-commerce Price Monitoring
**Problem**: Product prices loaded via AJAX, `requests` sees loading spinners
```python
# Monitor competitor pricing with dynamic content
products = await web.get_many(
    competitor_urls,
    script="return {price: document.querySelector('.price')?.textContent, stock: document.querySelector('.inventory')?.textContent}"
)
for product in products:
    if product.script_result['price'] != cached_price:
        await alert_price_change(product.url, product.script_result)
```

### 🔗 MCP Servers
**Problem**: Claude needs reliable web content extraction tools
```python
# Easy MCP integration (with crawailer[mcp])
from crawailer.mcp import create_mcp_server

server = create_mcp_server()
# Automatically exposes web.get, web.discover, etc. as MCP tools
```

### 📊 Social Media & Content Analysis
**Problem**: Posts and comments load infinitely via JavaScript
```python
# Extract social media discussions with infinite scroll
content = await web.get(
    "https://social-platform.com/topic/ai-safety",
    script="window.scrollTo(0, document.body.scrollHeight); return document.querySelectorAll('.post').length"
)
# Gets full thread content, not just initial page load
```

## 🛠️ Installation

```bash
# Basic installation
pip install crawailer

# With AI features (semantic search, entity extraction)
pip install crawailer[ai]

# With MCP server capabilities  
pip install crawailer[mcp]

# Everything
pip install crawailer[all]

# Post-install setup (installs Playwright browsers)
crawailer setup
```

## 🏗️ Architecture

Crawailer is built on modern, focused libraries:

- **🎭 Playwright**: Reliable browser automation
- **⚡ selectolax**: 5-10x faster HTML parsing (C-based)
- **📝 markdownify**: Clean HTML→Markdown conversion
- **🧹 justext**: Intelligent content extraction and cleaning
- **🔄 httpx**: Modern async HTTP client

## 🧪 Battle-Tested Quality

Crawailer includes **18 comprehensive test suites** with real-world scenarios:

- **Modern Frameworks**: React, Vue, Angular demos with full JavaScript APIs
- **Mobile Compatibility**: Safari iOS, Chrome Android, responsive designs
- **Production Edge Cases**: Network failures, memory pressure, browser differences
- **Performance Testing**: Stress tests, concurrency, resource management

**Want to contribute?** We welcome PRs with new test scenarios! Our test sites library shows exactly how different frameworks should behave with JavaScript execution.

> 📝 **Future TODO**: Move examples to dedicated repository for community contributions

## 🤝 Perfect for MCP Projects

MCP servers love Crawailer because it provides:

- **Focused tools**: Each function does one thing well
- **Rich outputs**: Structured data ready for LLM consumption  
- **Smart defaults**: Works out of the box with minimal configuration
- **Extensible**: Easy to add domain-specific extraction logic

```python
# Example MCP server tool
@mcp_tool("web_research")
async def research_topic(topic: str, depth: str = "comprehensive"):
    results = await web.discover(topic, max_pages=20)
    return {
        "sources": len(results),
        "content": [r.summary for r in results],
        "insights": await analyze_patterns(results)
    }
```

## 🥊 Crawailer vs Traditional Tools

| Challenge | `requests` & HTTP libs | Selenium | **Crawailer** |
|-----------|------------------------|----------|---------------|
| **React/Vue/Angular** | ❌ Empty templates | 🟡 Slow, complex setup | ✅ **Just works** |
| **Dynamic Pricing** | ❌ Shows loading spinner | 🟡 Requires waits/timeouts | ✅ **Intelligent waiting** |
| **JavaScript APIs** | ❌ No access | 🟡 Clunky WebDriver calls | ✅ **Native page.evaluate()** |
| **Speed** | 🟢 100-500ms | ❌ 5-15 seconds | ✅ **2-5 seconds** |
| **Memory** | 🟢 1-5MB | ❌ 200-500MB | 🟡 **100-200MB** |
| **AI-Ready Output** | ❌ Raw HTML | ❌ Raw HTML | ✅ **Clean Markdown** |
| **Developer Experience** | 🟡 Manual parsing | ❌ Complex WebDriver | ✅ **Intuitive API** |

> **The bottom line**: When JavaScript matters, Crawailer delivers. When it doesn't, use `requests`.
> 
> 📖 **[See complete tool comparison →](docs/COMPARISON.md)** (includes Scrapy, Playwright, BeautifulSoup, and more)

## 🎉 What Makes It Delightful

### JavaScript-Powered Intelligence
```python
# Dynamic content extraction from SPAs
content = await web.get(
    "https://react-app.com",
    script="window.testData?.framework + ' v' + window.React?.version"
)
# Automatically detects: React application with version info
# Extracts: Dynamic content + framework details

# E-commerce with JavaScript-loaded prices
product = await web.get(
    "https://shop.com/product",
    script="document.querySelector('.dynamic-price')?.textContent",
    wait_for=".price-loaded"
) 
# Recognizes product page with dynamic pricing
# Extracts: Real-time price, reviews, availability, specs
```

### Beautiful Output
```
✨ Found 15 high-quality sources
📊 Sources: 4 arxiv, 3 journals, 2 conferences, 6 blogs  
📅 Date range: 2023-2024 (recent research)
⚡ Average quality score: 8.7/10
🔍 Key topics: transformers, safety, alignment
```

### Helpful Errors
```python
try:
    content = await web.get("problematic-site.com")
except web.CloudflareProtected:
    # "💡 Try: await web.get(url, stealth=True)"
except web.PaywallDetected as e:
    # "🔍 Found archived version: {e.archive_url}"
```

## 📚 Documentation

- **[Tool Comparison](docs/COMPARISON.md)**: How Crawailer compares to Scrapy, Selenium, BeautifulSoup, etc.
- **[Getting Started](docs/getting-started.md)**: Installation and first steps
- **[JavaScript API](docs/JAVASCRIPT_API.md)**: Complete JavaScript execution guide
- **[API Reference](docs/API_REFERENCE.md)**: Complete function documentation  
- **[Benchmarks](docs/BENCHMARKS.md)**: Performance comparison with other tools
- **[MCP Integration](docs/mcp.md)**: Building MCP servers with Crawailer
- **[Examples](examples/)**: Real-world usage patterns
- **[Architecture](docs/architecture.md)**: How Crawailer works internally

## 🤝 Contributing

We love contributions! Crawailer is designed to be:
- **Easy to extend**: Add new content extractors and browser capabilities
- **Well-tested**: Comprehensive test suite with real websites
- **Documented**: Every feature has examples and use cases

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🚀 Ready to Stop Losing Your Mind?

```bash
pip install crawailer
crawailer setup  # Install browser engines
```

**Life's too short** for empty `<div>` tags and "JavaScript required" messages.

Get content that actually exists. From websites that actually work.

⭐ **Star us if this saves your sanity** → [git.supported.systems/MCP/crawailer](https://git.supported.systems/MCP/crawailer)

---

**Built with ❤️ for the age of AI agents and automation**

*Crawailer: Because robots deserve delightful web experiences too* 🤖✨