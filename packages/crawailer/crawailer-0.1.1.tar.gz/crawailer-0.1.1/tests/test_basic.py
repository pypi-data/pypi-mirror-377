"""
Basic tests for Crawailer functionality.

Simple tests to verify the core components work together.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from crawailer.content import WebContent, ContentExtractor
from crawailer.utils import clean_text, detect_content_type, calculate_reading_time
from crawailer.config import BrowserConfig, CrawlConfig


def test_web_content_creation():
    """Test WebContent dataclass creation and properties."""
    content = WebContent(
        url="https://example.com",
        title="Test Article",
        markdown="# Test\n\nThis is a test article.",
        text="Test\n\nThis is a test article.",
        html="<h1>Test</h1><p>This is a test article.</p>"
    )
    
    assert content.url == "https://example.com"
    assert content.title == "Test Article"
    assert content.word_count == 6  # "This is a test article."
    assert content.reading_time == "1 min read"
    assert content.content_hash != ""


def test_clean_text():
    """Test text cleaning utility."""
    dirty_text = "  Hello    world  \n\n  with   spaces  "
    clean = clean_text(dirty_text)
    assert clean == "Hello world with spaces"
    
    # Test aggressive cleaning
    dirty_with_boilerplate = "Read our Cookie Policy and Privacy Policy. Hello world."
    clean_aggressive = clean_text(dirty_with_boilerplate, aggressive=True)
    assert "Cookie Policy" not in clean_aggressive
    assert "Hello world" in clean_aggressive


def test_detect_content_type():
    """Test content type detection."""
    # Product page
    product_html = '<div class="price">$99</div><button class="add-to-cart">Buy</button>'
    assert detect_content_type(product_html) == "product"
    
    # Article
    article_html = '<article><h1>Title</h1><p>Content</p></article>'
    assert detect_content_type(article_html) == "article"
    
    # Documentation
    doc_html = '<div>API documentation for developers</div>'
    assert detect_content_type(doc_html, title="API Guide") == "documentation"


def test_reading_time_calculation():
    """Test reading time calculation."""
    short_text = "Hello world"
    assert calculate_reading_time(short_text) == "1 min read"
    
    long_text = " ".join(["word"] * 400)  # 400 words
    assert calculate_reading_time(long_text) == "2 min read"


def test_browser_config():
    """Test browser configuration."""
    config = BrowserConfig()
    assert config.headless is True
    assert config.timeout == 30000
    assert config.viewport["width"] == 1920
    
    # Test custom config
    custom_config = BrowserConfig(headless=False, timeout=15000)
    assert custom_config.headless is False
    assert custom_config.timeout == 15000


def test_crawl_config():
    """Test complete crawl configuration."""
    config = CrawlConfig.default()
    assert config.browser.headless is True
    assert config.extraction.clean_text is True
    assert config.concurrency.max_concurrent == 5


@pytest.mark.asyncio
async def test_content_extractor():
    """Test content extraction from mock HTML."""
    html = """
    <html>
    <head>
        <title>Test Page</title>
        <meta name="author" content="Test Author">
    </head>
    <body>
        <h1>Main Title</h1>
        <p>This is the main content of the page.</p>
        <a href="https://example.com">External Link</a>
        <a href="/internal">Internal Link</a>
    </body>
    </html>
    """
    
    page_data = {
        "url": "https://test.com",
        "html": html,
        "status": 200,
        "load_time": 1.5
    }
    
    extractor = ContentExtractor(
        clean=True,
        extract_links=True,
        extract_metadata=True
    )
    
    content = await extractor.extract(page_data)
    
    assert content.url == "https://test.com"
    assert content.title == "Test Page"
    assert "Main Title" in content.text
    assert "main content" in content.text
    assert content.status_code == 200
    assert content.load_time == 1.5
    assert len(content.links) == 2  # Two links found


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])