"""
Configuration management for Crawailer.

Centralizes all configuration with sensible defaults
and environment variable support.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BrowserConfig:
    """Browser automation configuration."""
    headless: bool = True
    timeout: int = 30000  # milliseconds
    user_agent: Optional[str] = None
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    extra_args: List[str] = field(default_factory=list)
    
    @classmethod
    def from_env(cls) -> "BrowserConfig":
        """Create config from environment variables."""
        return cls(
            headless=os.getenv("CRAWAILER_HEADLESS", "true").lower() == "true",
            timeout=int(os.getenv("CRAWAILER_TIMEOUT", "30000")),
            user_agent=os.getenv("CRAWAILER_USER_AGENT"),
        )


@dataclass 
class ExtractionConfig:
    """Content extraction configuration."""
    clean_text: bool = True
    extract_links: bool = True
    extract_metadata: bool = True
    extract_images: bool = False
    max_links: int = 50
    max_images: int = 20
    
    @classmethod
    def from_env(cls) -> "ExtractionConfig":
        """Create config from environment variables."""
        return cls(
            clean_text=os.getenv("CRAWAILER_CLEAN_TEXT", "true").lower() == "true",
            extract_links=os.getenv("CRAWAILER_EXTRACT_LINKS", "true").lower() == "true",
            extract_metadata=os.getenv("CRAWAILER_EXTRACT_METADATA", "true").lower() == "true",
            extract_images=os.getenv("CRAWAILER_EXTRACT_IMAGES", "false").lower() == "true",
            max_links=int(os.getenv("CRAWAILER_MAX_LINKS", "50")),
            max_images=int(os.getenv("CRAWAILER_MAX_IMAGES", "20")),
        )


@dataclass
class ConcurrencyConfig:
    """Concurrency and rate limiting configuration."""
    max_concurrent: int = 5
    request_delay: float = 0.1  # seconds between requests
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    
    @classmethod
    def from_env(cls) -> "ConcurrencyConfig":
        """Create config from environment variables."""
        return cls(
            max_concurrent=int(os.getenv("CRAWAILER_MAX_CONCURRENT", "5")),
            request_delay=float(os.getenv("CRAWAILER_REQUEST_DELAY", "0.1")),
            retry_attempts=int(os.getenv("CRAWAILER_RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("CRAWAILER_RETRY_DELAY", "1.0")),
        )


@dataclass
class CacheConfig:
    """Caching configuration."""
    enabled: bool = True
    ttl: int = 3600  # seconds (1 hour)
    max_size: int = 1000  # number of cached items
    cache_dir: Optional[str] = None
    
    def __post_init__(self):
        if self.cache_dir is None:
            self.cache_dir = os.path.expanduser("~/.crawailer/cache")
    
    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Create config from environment variables."""
        return cls(
            enabled=os.getenv("CRAWAILER_CACHE_ENABLED", "true").lower() == "true",
            ttl=int(os.getenv("CRAWAILER_CACHE_TTL", "3600")),
            max_size=int(os.getenv("CRAWAILER_CACHE_MAX_SIZE", "1000")),
            cache_dir=os.getenv("CRAWAILER_CACHE_DIR"),
        )


@dataclass
class CrawlConfig:
    """Complete configuration for Crawailer."""
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    concurrency: ConcurrencyConfig = field(default_factory=ConcurrencyConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    @classmethod
    def from_env(cls) -> "CrawlConfig":
        """Create complete config from environment variables."""
        return cls(
            browser=BrowserConfig.from_env(),
            extraction=ExtractionConfig.from_env(),
            concurrency=ConcurrencyConfig.from_env(),
            cache=CacheConfig.from_env(),
        )
    
    @classmethod
    def default(cls) -> "CrawlConfig":
        """Get default configuration."""
        return cls()


# Global default configuration
DEFAULT_CONFIG = CrawlConfig.default()