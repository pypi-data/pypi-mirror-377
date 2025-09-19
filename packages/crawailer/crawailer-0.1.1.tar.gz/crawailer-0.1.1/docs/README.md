# Crawailer Documentation

## 🚀 Quick Navigation

| Document | Description |
|----------|-------------|
| **[JavaScript API](JAVASCRIPT_API.md)** | Complete guide to JavaScript execution capabilities |
| **[API Reference](API_REFERENCE.md)** | Comprehensive function and class documentation |
| **[Benchmarks](BENCHMARKS.md)** | Performance comparison with Katana crawler |
| **[Testing](TESTING.md)** | Testing infrastructure and comprehensive test suite |

## 📚 Documentation Overview

### Core Documentation

#### [JavaScript API Guide](JAVASCRIPT_API.md)
**Complete guide to Crawailer's JavaScript execution capabilities**
- Basic JavaScript execution patterns
- Modern framework integration (React, Vue, Angular)  
- Dynamic content extraction techniques
- Performance monitoring and optimization
- Error handling and troubleshooting
- Real-world use cases and examples

#### [API Reference](API_REFERENCE.md)
**Comprehensive documentation for all functions and classes**
- Core functions: `get()`, `get_many()`, `discover()`
- Data classes: `WebContent`, `BrowserConfig`
- Browser control: `Browser` class and methods
- Content extraction: `ContentExtractor` customization
- Error handling and custom exceptions
- MCP integration patterns

### Performance & Quality

#### [Benchmarks](BENCHMARKS.md)
**Detailed performance analysis and tool comparison**
- Katana vs Crawailer head-to-head benchmarking
- JavaScript handling capabilities comparison
- Use case optimization recommendations
- Resource usage analysis
- Hybrid workflow strategies

#### [Testing Infrastructure](TESTING.md)
**Comprehensive testing suite documentation**
- 18 test files with 16,554+ lines of test code
- Local Docker test server setup
- Modern framework testing scenarios
- Security and performance validation
- Memory management and leak detection

## 🎯 Getting Started Paths

### For AI/ML Developers
1. **[JavaScript API](JAVASCRIPT_API.md#modern-framework-integration)** - Framework-specific extraction
2. **[API Reference](API_REFERENCE.md#webcontent)** - WebContent data structure
3. **[Testing](TESTING.md#javascript-api-testing)** - Validation examples

### For Security Researchers  
1. **[Benchmarks](BENCHMARKS.md#katana-strengths)** - When to use Katana vs Crawailer
2. **[JavaScript API](JAVASCRIPT_API.md#error-handling)** - Robust error handling
3. **[Testing](TESTING.md#security-testing)** - Security validation

### For Performance Engineers
1. **[Benchmarks](BENCHMARKS.md#performance-characteristics)** - Performance analysis
2. **[API Reference](API_REFERENCE.md#performance-optimization)** - Optimization strategies  
3. **[Testing](TESTING.md#performance-testing)** - Performance validation

### For Content Analysts
1. **[JavaScript API](JAVASCRIPT_API.md#complex-javascript-operations)** - Advanced extraction
2. **[API Reference](API_REFERENCE.md#content-extraction)** - Content processing
3. **[Testing](TESTING.md#modern-framework-testing)** - Framework compatibility

## 📖 Key Capabilities

### ⚡ JavaScript Execution Excellence
Crawailer provides **full browser automation** with reliable JavaScript execution:

```python
# Extract dynamic content from SPAs
content = await get(
    "https://react-app.com",
    script="window.testData?.framework + ' v' + React.version"
)
print(f"Framework: {content.script_result}")
```

**Key advantages over traditional scrapers:**
- Real browser environment with full API access
- Support for modern frameworks (React, Vue, Angular)
- Reliable `page.evaluate()` execution vs unreliable headless modes
- Complex user interaction simulation

### 🎯 Content Quality Focus
Unlike URL discovery tools, Crawailer optimizes for **content quality**:

```python
content = await get("https://blog.com/article")

# Rich metadata extraction
print(f"Title: {content.title}")
print(f"Author: {content.author}")
print(f"Reading time: {content.reading_time}")
print(f"Quality score: {content.quality_score}/10")

# AI-ready formats
print(content.markdown)  # Clean markdown for LLMs
print(content.text)      # Human-readable text
```

### 🚀 Production-Ready Performance
Comprehensive testing ensures production reliability:

- **357+ test scenarios** covering edge cases
- **Memory leak detection** for long-running processes
- **Cross-browser engine compatibility**
- **Security hardening** with XSS prevention
- **Performance optimization** strategies

## 🔄 Workflow Integration

### AI Agent Workflows
```python
# Research assistant pattern
research = await discover(
    "quantum computing breakthroughs",
    content_script="document.querySelector('.abstract')?.textContent"
)

for paper in research:
    summary = await llm.summarize(paper.markdown)
    abstract = paper.script_result  # JavaScript-extracted abstract
    insights = await llm.extract_insights(paper.content + abstract)
```

### Content Monitoring
```python
# E-commerce price monitoring
product_data = await get(
    "https://shop.com/product/123",
    script="""
    ({
        price: document.querySelector('.price')?.textContent,
        availability: document.querySelector('.stock')?.textContent,
        rating: document.querySelector('.rating')?.textContent
    })
    """
)

price_info = product_data.script_result
await notify_price_change(price_info)
```

### Security Reconnaissance  
```python
# Endpoint discovery (consider using Katana for this)
endpoints = await get(
    "https://target.com",
    script="""
    Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
    .filter(url => url.startsWith('https://target.com/api/'))
    """
)

api_endpoints = endpoints.script_result
```

## 🏗️ Architecture Insights

### Browser Automation Stack
```
Python Application
       ↓
Crawailer API (get, get_many, discover)
       ↓  
Browser Class (Playwright integration)
       ↓
Chrome/Firefox Browser Engine
       ↓
JavaScript Execution (page.evaluate)
       ↓
Content Extraction (selectolax, markdownify)
       ↓
WebContent Object (structured output)
```

### Performance Characteristics
- **JavaScript Execution**: ~2-5 seconds per page with complex scripts
- **Memory Usage**: ~50-100MB baseline + ~2MB per page
- **Concurrency**: Optimal at 5-10 concurrent pages
- **Content Quality**: 8.7/10 average with rich metadata

## 🆚 Tool Comparison

| Use Case | Recommended Tool | Why |
|----------|------------------|-----|
| **URL Discovery** | Katana | 3x URL multiplication, security focus |
| **Content Analysis** | Crawailer | Rich extraction, JavaScript reliability |
| **SPA Crawling** | Crawailer | Full React/Vue/Angular support |
| **Security Testing** | Katana | Fast reconnaissance, endpoint enumeration |
| **AI Training Data** | Crawailer | Structured output, content quality |
| **E-commerce Monitoring** | Crawailer | Dynamic pricing, JavaScript-heavy sites |

## 🛠️ Development Workflow

### Local Development
```bash
# Start test infrastructure
cd test-server && docker compose up -d

# Run comprehensive tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_javascript_api.py -v
pytest tests/test_modern_frameworks.py -v
```

### Performance Testing
```bash
# Benchmark against other tools
python benchmark_katana_vs_crawailer.py

# Memory and performance validation
pytest tests/test_memory_management.py -v
pytest tests/test_performance_under_pressure.py -v
```

### Security Validation
```bash
# Security and penetration testing
pytest tests/test_security_penetration.py -v

# Input validation and XSS prevention
pytest tests/test_security_penetration.py::test_xss_prevention -v
```

## 📈 Future Roadmap

### Planned Enhancements
1. **Performance Optimization**: Connection pooling, intelligent caching
2. **AI Integration**: Semantic content analysis, automatic categorization  
3. **Security Features**: Advanced stealth modes, captcha solving
4. **Mobile Support**: Enhanced mobile browser simulation
5. **Cloud Deployment**: Scalable cloud infrastructure patterns

### Community Contributions
- **Framework Support**: Additional SPA framework integration
- **Content Extractors**: Domain-specific extraction logic
- **Performance**: Optimization strategies and benchmarks
- **Documentation**: Use case examples and tutorials

---

This documentation suite provides comprehensive guidance for leveraging Crawailer's JavaScript execution capabilities across various use cases, from AI agent workflows to security research and content analysis.