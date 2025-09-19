"""
MCP (Model Context Protocol) integration for Crawailer.

This module provides MCP server tools that expose Crawailer's
functionality as composable tools for AI agents and clients.
"""

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Create dummy classes for type hints when MCP isn't installed
    class Server:
        pass
    class Tool:
        pass
    class TextContent:
        pass

import json
import asyncio
from typing import Dict, List, Any, Optional

from . import api as crawailer_api
from .content import WebContent


class CrawlMCPServer:
    """
    MCP server that exposes Crawailer functionality as tools.
    
    Provides clean, composable tools for web content extraction
    that work seamlessly with MCP clients and AI agents.
    """
    
    def __init__(self, name: str = "crawailer-mcp"):
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP is not installed. Install with: pip install crawailer[mcp]"
            )
        
        self.server = Server(name)
        self._setup_tools()
    
    def _setup_tools(self):
        """Register all MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="web_get",
                    description="Extract content from a single web page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch content from"
                            },
                            "wait_for": {
                                "type": "string", 
                                "description": "CSS selector to wait for before extracting"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            },
                            "clean": {
                                "type": "boolean",
                                "description": "Whether to clean and optimize content (default: true)",
                                "default": True
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="web_get_many",
                    description="Extract content from multiple web pages efficiently",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of URLs to fetch"
                            },
                            "max_concurrent": {
                                "type": "integer", 
                                "description": "Maximum concurrent requests (default: 5)",
                                "default": 5
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout per URL in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["urls"]
                    }
                ),
                Tool(
                    name="web_discover",
                    description="Intelligently discover and rank content related to a query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query or topic to discover content for"
                            },
                            "max_pages": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            },
                            "quality_threshold": {
                                "type": "number",
                                "description": "Minimum quality score 0-1 (default: 0.7)",
                                "default": 0.7
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="web_extract_links",
                    description="Extract and analyze links from a web page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to extract links from"
                            },
                            "filter_type": {
                                "type": "string",
                                "description": "Filter links by type: internal, external, document, image",
                                "enum": ["all", "internal", "external", "document", "image"]
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="web_take_screenshot",
                    description="Take a screenshot of a web page or element",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to screenshot"
                            },
                            "selector": {
                                "type": "string",
                                "description": "CSS selector to screenshot (optional)"
                            },
                            "full_page": {
                                "type": "boolean",
                                "description": "Whether to capture full scrollable page",
                                "default": False
                            }
                        },
                        "required": ["url"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "web_get":
                    result = await self._handle_web_get(**arguments)
                elif name == "web_get_many":
                    result = await self._handle_web_get_many(**arguments)
                elif name == "web_discover":
                    result = await self._handle_web_discover(**arguments)
                elif name == "web_extract_links":
                    result = await self._handle_web_extract_links(**arguments)
                elif name == "web_take_screenshot":
                    result = await self._handle_web_take_screenshot(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=json.dumps(result, default=str, indent=2))]
            
            except Exception as e:
                error_result = {
                    "error": str(e),
                    "tool": name,
                    "arguments": arguments
                }
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    async def _handle_web_get(
        self,
        url: str,
        wait_for: Optional[str] = None,
        timeout: int = 30,
        clean: bool = True,
    ) -> Dict[str, Any]:
        """Handle web_get tool call."""
        content = await crawailer_api.get(
            url,
            wait_for=wait_for,
            timeout=timeout,
            clean=clean
        )
        return self._serialize_content(content)
    
    async def _handle_web_get_many(
        self,
        urls: List[str],
        max_concurrent: int = 5,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Handle web_get_many tool call."""
        results = await crawailer_api.get_many(
            urls,
            max_concurrent=max_concurrent,
            timeout=timeout
        )
        
        return {
            "total_urls": len(urls),
            "successful": len([r for r in results if r is not None]),
            "failed": len([r for r in results if r is None]),
            "results": [
                self._serialize_content(content) if content else None
                for content in results
            ]
        }
    
    async def _handle_web_discover(
        self,
        query: str,
        max_pages: int = 10,
        quality_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """Handle web_discover tool call."""
        results = await crawailer_api.discover(
            query,
            max_pages=max_pages,
            quality_threshold=quality_threshold
        )
        
        return {
            "query": query,
            "total_found": len(results),
            "results": [self._serialize_content(content) for content in results]
        }
    
    async def _handle_web_extract_links(
        self,
        url: str,
        filter_type: str = "all",
    ) -> Dict[str, Any]:
        """Handle web_extract_links tool call."""
        content = await crawailer_api.get(url, extract_links=True)
        
        links = content.links
        if filter_type != "all":
            links = [link for link in links if link.get('type', '').startswith(filter_type)]
        
        return {
            "url": url,
            "total_links": len(content.links),
            "filtered_links": len(links),
            "filter_applied": filter_type,
            "links": links
        }
    
    async def _handle_web_take_screenshot(
        self,
        url: str,
        selector: Optional[str] = None,
        full_page: bool = False,
    ) -> Dict[str, Any]:
        """Handle web_take_screenshot tool call."""
        # Note: This would require access to the browser instance
        # For now, return a placeholder
        return {
            "url": url,
            "selector": selector,
            "full_page": full_page,
            "screenshot": "base64_encoded_image_data_would_go_here",
            "note": "Screenshot functionality requires browser access - coming soon!"
        }
    
    def _serialize_content(self, content: WebContent) -> Dict[str, Any]:
        """Convert WebContent to JSON-serializable dict."""
        return {
            "url": content.url,
            "title": content.title,
            "markdown": content.markdown,
            "text": content.text[:1000] + "..." if len(content.text) > 1000 else content.text,
            "summary": content.summary,
            "author": content.author,
            "published": content.published.isoformat() if content.published else None,
            "reading_time": content.reading_time,
            "word_count": content.word_count,
            "language": content.language,
            "quality_score": content.quality_score,
            "content_type": content.content_type,
            "topics": content.topics,
            "entities": content.entities,
            "links": content.links[:10],  # Limit for readability
            "images": content.images[:5],  # Limit for readability
            "extracted_at": content.extracted_at.isoformat(),
        }
    
    async def run(self, transport):
        """Run the MCP server with the given transport."""
        await self.server.run(transport)


def create_mcp_server(name: str = "crawailer-mcp") -> CrawlMCPServer:
    """
    Create a Crawailer MCP server instance.
    
    Args:
        name: Server name for MCP identification
        
    Returns:
        CrawlMCPServer instance ready to run
        
    Example:
        >>> server = create_mcp_server()
        >>> # Run with stdio transport
        >>> await server.run(stdio_transport)
    """
    return CrawlMCPServer(name)


# Convenience function for quick server setup
async def serve_mcp(name: str = "crawailer-mcp", stdio: bool = True):
    """
    Start serving Crawailer as an MCP server.
    
    Args:
        name: Server name
        stdio: Whether to use stdio transport (default for MCP)
        
    Example:
        >>> await serve_mcp()  # Starts stdio MCP server
    """
    if not MCP_AVAILABLE:
        raise ImportError(
            "MCP is not installed. Install with: pip install crawailer[mcp]"
        )
    
    server = create_mcp_server(name)
    
    if stdio:
        # Use stdio transport (standard for MCP)
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                server.create_initialization_options(),
                read_stream,
                write_stream
            )
    else:
        raise NotImplementedError("Only stdio transport currently supported")


if __name__ == "__main__":
    # Allow running as MCP server directly
    asyncio.run(serve_mcp())