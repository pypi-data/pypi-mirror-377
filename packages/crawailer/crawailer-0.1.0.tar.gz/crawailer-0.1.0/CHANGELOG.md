# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Crawailer
- Full JavaScript execution support with `page.evaluate()`
- Modern framework support (React, Vue, Angular)
- Comprehensive content extraction with rich metadata
- High-level API functions: `get()`, `get_many()`, `discover()`
- Browser automation with Playwright integration
- Fast HTML processing with selectolax (5-10x faster than BeautifulSoup)
- WebContent dataclass with computed properties
- Async-first design with concurrent processing
- Command-line interface
- MCP (Model Context Protocol) server integration
- Comprehensive test suite with 357+ scenarios
- Local Docker test server for development
- Security hardening with XSS prevention
- Memory management and leak detection
- Cross-browser engine compatibility
- Performance optimization strategies

### Features
- **JavaScript Execution**: Execute arbitrary JavaScript with `script`, `script_before`, `script_after` parameters
- **SPA Support**: Handle React, Vue, Angular, and other modern frameworks
- **Dynamic Content**: Extract content loaded via AJAX, user interactions, and lazy loading
- **Batch Processing**: Process multiple URLs concurrently with intelligent batching
- **Content Quality**: Rich metadata extraction including author, reading time, quality scores
- **Error Handling**: Comprehensive error capture with graceful degradation
- **Performance Monitoring**: Extract timing and memory metrics from pages
- **Framework Detection**: Automatic detection of JavaScript frameworks and versions
- **User Interaction**: Simulate clicks, form submissions, scrolling, and complex workflows

### Documentation
- Complete JavaScript API guide with examples
- Comprehensive API reference documentation
- Performance benchmarks vs Katana crawler
- Testing infrastructure documentation
- Strategic positioning and use case guidance

### Testing
- 18 test files with 16,554+ lines of test code
- Modern framework integration tests
- Mobile browser compatibility tests
- Security and penetration testing
- Memory management and leak detection
- Network resilience and error handling
- Performance under pressure validation
- Browser engine compatibility testing

### Performance
- Intelligent content extraction optimized for LLM consumption
- Concurrent processing with configurable limits
- Memory-efficient batch processing
- Resource cleanup and garbage collection
- Connection pooling and request optimization

### Security
- XSS prevention and input validation
- Script execution sandboxing
- Safe error handling without information leakage
- Comprehensive security test suite

## [0.1.0] - 2024-09-18

### Added
- Initial public release
- Core browser automation functionality
- JavaScript execution capabilities
- Content extraction and processing
- MCP server integration
- Comprehensive documentation
- Production-ready test suite

---

For more details about changes, see the [commit history](https://git.supported.systems/MCP/crawailer/commits/branch/main).