"""
Utility functions for content processing and analysis.

Common operations that are useful across the library
and for users who want to process content manually.
"""

import re
import hashlib
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from selectolax.parser import HTMLParser


def clean_text(text: str, aggressive: bool = False) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        aggressive: Whether to apply aggressive cleaning
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Basic cleaning
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    if aggressive:
        # Remove common boilerplate patterns
        boilerplate_patterns = [
            r'Cookie\s+Policy.*?(?=\.|$)',
            r'Privacy\s+Policy.*?(?=\.|$)', 
            r'Terms\s+of\s+Service.*?(?=\.|$)',
            r'Subscribe\s+to.*?(?=\.|$)',
            r'Follow\s+us.*?(?=\.|$)',
            r'Share\s+this.*?(?=\.|$)',
            r'Sign\s+up.*?(?=\.|$)',
        ]
        
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
    
    return text.strip()


def extract_links(html: str, base_url: str) -> List[Dict[str, str]]:
    """
    Extract links from HTML with context information.
    
    Args:
        html: HTML content
        base_url: Base URL for resolving relative links
        
    Returns:
        List of link dictionaries with url, text, type, context
    """
    parser = HTMLParser(html)
    links = []
    
    for link in parser.css('a[href]'):
        href = link.attributes.get('href', '').strip()
        text = link.text().strip()
        
        if not href or href in ['#', 'javascript:void(0)', 'javascript:;']:
            continue
        
        # Resolve relative URLs
        absolute_url = resolve_url(href, base_url)
        
        # Determine link type
        link_type = classify_link(absolute_url, base_url)
        
        # Get surrounding context
        context = get_link_context(link, parser)
        
        links.append({
            'url': absolute_url,
            'text': text,
            'type': link_type,
            'context': context,
        })
    
    return links


def resolve_url(url: str, base_url: str) -> str:
    """
    Resolve a URL against a base URL.
    
    Args:
        url: URL to resolve (may be relative)
        base_url: Base URL for resolution
        
    Returns:
        Absolute URL
    """
    try:
        return urljoin(base_url, url)
    except:
        return url


def classify_link(url: str, base_url: str) -> str:
    """
    Classify a link as internal, external, or specific type.
    
    Args:
        url: Link URL
        base_url: Base URL for comparison
        
    Returns:
        Link classification string
    """
    try:
        url_parsed = urlparse(url)
        base_parsed = urlparse(base_url)
        
        # Check if same domain
        if url_parsed.netloc == base_parsed.netloc:
            # Internal link - classify by file extension or path
            path = url_parsed.path.lower()
            
            if path.endswith(('.pdf', '.doc', '.docx', '.txt')):
                return 'internal_document'
            elif path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
                return 'internal_image'
            elif '/api/' in path or path.startswith('/api'):
                return 'internal_api'
            else:
                return 'internal'
        else:
            # External link - classify by domain patterns
            domain = url_parsed.netloc.lower()
            
            if any(x in domain for x in ['github.com', 'gitlab.com', 'bitbucket.org']):
                return 'external_code'
            elif any(x in domain for x in ['youtube.com', 'youtu.be', 'vimeo.com']):
                return 'external_video'
            elif any(x in domain for x in ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com']):
                return 'external_social'
            elif url_parsed.path.lower().endswith('.pdf'):
                return 'external_pdf'
            else:
                return 'external'
    
    except:
        return 'unknown'


def get_link_context(link_element, parser: HTMLParser, words: int = 10) -> str:
    """
    Get surrounding text context for a link.
    
    Args:
        link_element: The link element from selectolax
        parser: HTMLParser instance
        words: Number of words of context to extract
        
    Returns:
        Context string
    """
    try:
        # Get parent element text and find the link position
        parent = link_element.parent
        if parent:
            parent_text = parent.text()
            link_text = link_element.text()
            
            # Find link position in parent text
            if link_text in parent_text:
                pos = parent_text.find(link_text)
                before = ' '.join(parent_text[:pos].split()[-words:])
                after = ' '.join(parent_text[pos + len(link_text):].split()[:words])
                return f"{before} [{link_text}] {after}".strip()
        
        return ""
    except:
        return ""


def detect_content_type(html: str, url: str = "", title: str = "") -> str:
    """
    Detect the type of content based on HTML structure and patterns.
    
    Args:
        html: HTML content
        url: Page URL (optional)
        title: Page title (optional)
        
    Returns:
        Content type string
    """
    parser = HTMLParser(html)
    
    # E-commerce indicators
    ecommerce_selectors = [
        '.price', '.add-to-cart', '.buy-now', '.shopping-cart',
        '[data-price]', '.product-price', '.add-to-bag'
    ]
    if any(parser.css_first(sel) for sel in ecommerce_selectors):
        return 'product'
    
    # Article/blog indicators
    article_selectors = [
        'article', '.post', '.entry', '.blog-post',
        '[role="article"]', '.article-content'
    ]
    if any(parser.css_first(sel) for sel in article_selectors):
        return 'article'
    
    # Documentation indicators
    doc_keywords = ['api', 'documentation', 'docs', 'guide', 'tutorial', 'reference']
    text_content = (html + " " + url + " " + title).lower()
    if any(keyword in text_content for keyword in doc_keywords):
        return 'documentation'
    
    # News indicators  
    news_selectors = [
        '.news', '.headline', '.breaking', '.story',
        '[data-article]', '.news-article'
    ]
    if any(parser.css_first(sel) for sel in news_selectors):
        return 'news'
    
    # Forum/discussion indicators
    forum_selectors = [
        '.forum', '.discussion', '.thread', '.comment',
        '.reply', '.post-content'
    ]
    if any(parser.css_first(sel) for sel in forum_selectors):
        return 'forum'
    
    return 'webpage'


def calculate_reading_time(text: str, words_per_minute: int = 200) -> str:
    """
    Calculate estimated reading time for text.
    
    Args:
        text: Text content
        words_per_minute: Average reading speed
        
    Returns:
        Reading time string (e.g., "5 min read")
    """
    if not text:
        return "0 min read"
    
    word_count = len(text.split())
    minutes = max(1, round(word_count / words_per_minute))
    
    if minutes == 1:
        return "1 min read"
    else:
        return f"{minutes} min read"


def generate_content_hash(content: str) -> str:
    """
    Generate a hash for content deduplication.
    
    Args:
        content: Content to hash
        
    Returns:
        MD5 hash string
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain string
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ""


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: String to validate
        
    Returns:
        True if valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_sentences(text: str, count: int = 3) -> List[str]:
    """
    Extract the first N sentences from text.
    
    Args:
        text: Text content
        count: Number of sentences to extract
        
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    # Simple sentence splitting - could be enhanced with NLTK
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences[:count]