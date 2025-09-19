"""
Crawailer: Browser control for robots

A delightful library for web automation and content extraction,
designed for AI agents, MCP servers, and automation scripts.
"""

__version__ = "0.1.1"

# Core browser control
from .browser import Browser
from .config import BrowserConfig
from .content import WebContent, ContentExtractor
from .utils import clean_text, extract_links, detect_content_type

# High-level convenience functions
from .api import get, get_many, discover

__all__ = [
    # Core classes
    "Browser",
    "BrowserConfig", 
    "WebContent",
    "ContentExtractor",
    
    # Utilities
    "clean_text",
    "extract_links", 
    "detect_content_type",
    
    # High-level API
    "get",
    "get_many",
    "discover",
]