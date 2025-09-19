"""
WebContent model and extraction logic.

This module defines the WebContent dataclass and ContentExtractor
that transforms raw HTML into structured, useful content.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib
import re

from selectolax.parser import HTMLParser
from markdownify import markdownify as md


@dataclass
class WebContent:
    """
    Structured representation of web content.
    
    Designed to be immediately useful for both humans and LLMs,
    with rich metadata and multiple content formats.
    """
    # Core content
    url: str
    title: str
    markdown: str          # LLM-optimized markdown
    text: str             # Clean human-readable text  
    html: str             # Original HTML (if needed)
    
    # Metadata
    author: Optional[str] = None
    published: Optional[datetime] = None
    reading_time: str = "Unknown"
    word_count: int = 0
    language: str = "en"
    quality_score: float = 0.0
    
    # Semantic understanding
    content_type: str = "unknown"  # article, product, documentation, etc.
    topics: List[str] = field(default_factory=list)
    entities: Dict[str, List[str]] = field(default_factory=dict)
    
    # Relationships
    links: List[Dict[str, str]] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    
    # Technical metadata
    status_code: int = 200
    load_time: float = 0.0
    content_hash: str = ""
    extracted_at: datetime = field(default_factory=datetime.now)
    
    # JavaScript execution results
    script_result: Optional[Any] = None
    script_error: Optional[str] = None
    
    def __post_init__(self):
        """Calculate derived fields."""
        if not self.content_hash:
            self.content_hash = hashlib.md5(self.text.encode()).hexdigest()
        
        if self.word_count == 0:
            self.word_count = len(self.text.split())
            
        if self.reading_time == "Unknown" and self.word_count > 0:
            # Average reading speed: 200 words per minute
            minutes = max(1, round(self.word_count / 200))
            self.reading_time = f"{minutes} min read"
    
    @property
    def summary(self) -> str:
        """Generate a brief summary of the content."""
        # Simple extractive summary - first paragraph or sentence
        sentences = self.text.split('. ')
        if sentences:
            return sentences[0] + ('.' if not sentences[0].endswith('.') else '')
        return self.title
    
    @property
    def readable_summary(self) -> str:
        """Human-friendly summary with metadata."""
        parts = [self.title]
        
        if self.author:
            parts.append(f"by {self.author}")
            
        if self.published:
            parts.append(f"• {self.published.strftime('%b %Y')}")
            
        parts.append(f"• {self.reading_time}")
        
        if self.quality_score > 0:
            parts.append(f"• Quality: {self.quality_score:.1f}/10")
            
        return " ".join(parts)
    
    @property
    def has_script_result(self) -> bool:
        """Check if JavaScript execution result is available."""
        return self.script_result is not None
    
    @property 
    def has_script_error(self) -> bool:
        """Check if JavaScript execution error occurred."""
        return self.script_error is not None
    
    def save(self, path: str, format: str = "auto") -> None:
        """Save content to file in specified format."""
        if format == "auto":
            format = path.split('.')[-1] if '.' in path else "md"
            
        content_map = {
            "md": self.markdown,
            "txt": self.text,
            "html": self.html,
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            if format in content_map:
                f.write(content_map[format])
            else:
                # JSON format with all metadata
                import json
                f.write(json.dumps(self.__dict__, default=str, indent=2))


class ContentExtractor:
    """
    Transforms raw HTML into structured WebContent.
    
    Uses modern, fast libraries and heuristics to extract
    clean, meaningful content from web pages.
    """
    
    def __init__(
        self,
        clean: bool = True,
        extract_links: bool = True,
        extract_metadata: bool = True,
        extract_images: bool = False,
    ):
        self.clean = clean
        self.extract_links = extract_links
        self.extract_metadata = extract_metadata
        self.extract_images = extract_images
    
    async def extract(self, page_data: Dict[str, Any]) -> WebContent:
        """
        Extract structured content from page data.
        
        Args:
            page_data: Dict with 'url', 'html', 'status', 'load_time'
            
        Returns:
            WebContent object with extracted information
        """
        html = page_data['html']
        parser = HTMLParser(html)
        
        # Extract basic content
        title = self._extract_title(parser)
        text = self._extract_text(parser)
        markdown = self._html_to_markdown(html)
        
        # Extract metadata if requested
        metadata = {}
        if self.extract_metadata:
            metadata = self._extract_metadata(parser)
        
        # Extract links if requested
        links = []
        if self.extract_links:
            links = self._extract_links(parser, page_data['url'])
        
        # Extract images if requested
        images = []
        if self.extract_images:
            images = self._extract_images(parser, page_data['url'])
        
        # Determine content type
        content_type = self._detect_content_type(parser, text)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(text, title, metadata)
        
        return WebContent(
            url=page_data['url'],
            title=title,
            markdown=markdown,
            text=text,
            html=html,
            author=metadata.get('author'),
            published=metadata.get('published'),
            content_type=content_type,
            links=links,
            images=images,
            quality_score=quality_score,
            status_code=page_data.get('status', 200),
            load_time=page_data.get('load_time', 0.0),
            script_result=page_data.get('script_result'),
            script_error=page_data.get('script_error'),
        )
    
    def _extract_title(self, parser: HTMLParser) -> str:
        """Extract the page title using multiple strategies."""
        # Try <title> tag first
        title_tag = parser.css_first('title')
        if title_tag and title_tag.text():
            return title_tag.text().strip()
        
        # Try h1 tags
        h1_tags = parser.css('h1')
        if h1_tags:
            return h1_tags[0].text().strip()
        
        # Try Open Graph title
        og_title = parser.css_first('meta[property="og:title"]')
        if og_title:
            return og_title.attributes.get('content', '').strip()
        
        return "Untitled"
    
    def _extract_text(self, parser: HTMLParser) -> str:
        """Extract clean text content from HTML."""
        # Remove script and style elements
        for tag in parser.css('script, style, nav, footer, header'):
            tag.decompose()
        
        # Get text from main content areas
        main_selectors = [
            'main', 'article', '[role="main"]', 
            '.content', '.post', '.entry'
        ]
        
        for selector in main_selectors:
            main_content = parser.css_first(selector)
            if main_content:
                text = main_content.text(separator=' ', strip=True)
                if len(text) > 100:  # Reasonable amount of content
                    return self._clean_text(text)
        
        # Fallback: get all text from body
        body = parser.css_first('body')
        if body:
            return self._clean_text(body.text(separator=' ', strip=True))
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not self.clean:
            return text
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common boilerplate patterns
        patterns_to_remove = [
            r'Cookie\s+Policy.*?(?=\.|$)',
            r'Privacy\s+Policy.*?(?=\.|$)',
            r'Terms\s+of\s+Service.*?(?=\.|$)',
            r'Subscribe\s+to.*?(?=\.|$)',
            r'Follow\s+us.*?(?=\.|$)',
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to clean markdown."""
        # Configure markdownify for clean output
        markdown = md(
            html,
            heading_style="ATX",
            bullets="-",
            strip=['script', 'style', 'nav', 'footer'],
        )
        
        if self.clean:
            # Clean up markdown formatting
            markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)  # Remove excessive newlines
            markdown = re.sub(r'\[\]\([^)]*\)', '', markdown)      # Remove empty links
            markdown = re.sub(r'\n\s*[-*]\s*\n', '\n', markdown)   # Remove empty list items
        
        return markdown.strip()
    
    def _extract_metadata(self, parser: HTMLParser) -> Dict[str, Any]:
        """Extract metadata like author, publish date, etc."""
        metadata = {}
        
        # Extract author
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author', '.byline',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            element = parser.css_first(selector)
            if element:
                if element.tag == 'meta':
                    metadata['author'] = element.attributes.get('content', '').strip()
                else:
                    metadata['author'] = element.text().strip()
                break
        
        # Extract publish date
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'time[datetime]',
            '.published', '.date'
        ]
        
        for selector in date_selectors:
            element = parser.css_first(selector)
            if element:
                date_str = ""
                if element.tag == 'meta':
                    date_str = element.attributes.get('content', '')
                elif element.tag == 'time':
                    date_str = element.attributes.get('datetime', '') or element.text()
                else:
                    date_str = element.text()
                
                if date_str:
                    # TODO: Parse date string to datetime
                    metadata['published_str'] = date_str.strip()
                    break
        
        return metadata
    
    def _extract_links(self, parser: HTMLParser, base_url: str) -> List[Dict[str, str]]:
        """Extract and categorize links from the page."""
        links = []
        
        for link in parser.css('a[href]'):
            href = link.attributes.get('href', '').strip()
            text = link.text().strip()
            
            if href and href not in ['#', 'javascript:void(0)']:
                # TODO: Resolve relative URLs using base_url
                # TODO: Categorize links (internal/external, type)
                links.append({
                    'url': href,
                    'text': text,
                    'type': 'unknown'
                })
        
        return links[:50]  # Limit to avoid too much data
    
    def _extract_images(self, parser: HTMLParser, base_url: str) -> List[Dict[str, str]]:
        """Extract image information from the page."""
        images = []
        
        for img in parser.css('img[src]'):
            src = img.attributes.get('src', '').strip()
            alt = img.attributes.get('alt', '').strip()
            
            if src:
                # TODO: Resolve relative URLs using base_url
                images.append({
                    'src': src,
                    'alt': alt,
                })
        
        return images[:20]  # Limit to avoid too much data
    
    def _detect_content_type(self, parser: HTMLParser, text: str) -> str:
        """Detect the type of content (article, product, etc.)."""
        # Simple heuristics - could be much more sophisticated
        
        # Check for e-commerce indicators
        if parser.css_first('.price, .add-to-cart, .buy-now'):
            return "product"
        
        # Check for article indicators  
        if parser.css_first('article, .post, .entry'):
            return "article"
        
        # Check for documentation indicators
        if any(word in text.lower() for word in ['api', 'documentation', 'getting started', 'tutorial']):
            return "documentation"
        
        return "webpage"
    
    def _calculate_quality_score(self, text: str, title: str, metadata: Dict) -> float:
        """Calculate a quality score for the content (0-10)."""
        score = 5.0  # Start with neutral score
        
        # Text length (reasonable content)
        if 100 <= len(text) <= 10000:
            score += 1.0
        elif len(text) < 100:
            score -= 2.0
        
        # Has meaningful title
        if title and title != "Untitled" and len(title) > 5:
            score += 1.0
        
        # Has author information
        if metadata.get('author'):
            score += 1.0
        
        # Has publish date
        if metadata.get('published_str'):
            score += 1.0
        
        # Text quality indicators
        sentences = text.count('.')
        if sentences > 5:  # Reasonably structured text
            score += 1.0
        
        return max(0.0, min(10.0, score))