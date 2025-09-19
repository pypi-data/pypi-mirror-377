"""
Command-line interface for Crawailer.

Provides a simple CLI for common operations and testing.
"""

import asyncio
import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import List

from . import api as crawailer_api
from .content import WebContent


console = Console()


@click.group()
@click.version_option()
def main():
    """🕷️ Crawailer: Browser control for robots"""
    pass


@main.command()
@click.argument('url')
@click.option('--format', '-f', type=click.Choice(['markdown', 'text', 'json', 'summary']), 
              default='summary', help='Output format')
@click.option('--clean/--no-clean', default=True, help='Clean content')
@click.option('--timeout', default=30, help='Timeout in seconds')
def get(url: str, format: str, clean: bool, timeout: int):
    """Extract content from a single URL"""
    async def _get():
        try:
            console.print(f"🔍 Fetching: {url}")
            content = await crawailer_api.get(url, clean=clean, timeout=timeout)
            
            if format == 'markdown':
                console.print(content.markdown)
            elif format == 'text':
                console.print(content.text)
            elif format == 'json':
                data = {
                    'url': content.url,
                    'title': content.title,
                    'markdown': content.markdown,
                    'text': content.text,
                    'word_count': content.word_count,
                    'reading_time': content.reading_time,
                    'quality_score': content.quality_score,
                }
                console.print_json(json.dumps(data, indent=2))
            else:  # summary
                _print_content_summary(content)
                
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")
        finally:
            await crawailer_api.cleanup()
    
    asyncio.run(_get())


@main.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--max-concurrent', default=5, help='Max concurrent requests')
@click.option('--timeout', default=30, help='Timeout per URL in seconds')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'detailed']), 
              default='table', help='Output format')
def get_many(urls: List[str], max_concurrent: int, timeout: int, format: str):
    """Extract content from multiple URLs"""
    async def _get_many():
        try:
            console.print(f"🔍 Fetching {len(urls)} URLs...")
            results = await crawailer_api.get_many(
                list(urls), 
                max_concurrent=max_concurrent, 
                timeout=timeout
            )
            
            successful = [r for r in results if r is not None]
            failed_count = len(results) - len(successful)
            
            console.print(f"✅ Success: {len(successful)}, ❌ Failed: {failed_count}")
            
            if format == 'table':
                _print_results_table(successful)
            elif format == 'json':
                data = [{
                    'url': r.url,
                    'title': r.title,
                    'word_count': r.word_count,
                    'quality_score': r.quality_score,
                } for r in successful]
                console.print_json(json.dumps(data, indent=2))
            else:  # detailed
                for content in successful:
                    _print_content_summary(content)
                    console.print()
                    
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")
        finally:
            await crawailer_api.cleanup()
    
    asyncio.run(_get_many())


@main.command()
@click.argument('query')
@click.option('--max-pages', default=10, help='Maximum pages to discover')
@click.option('--quality-threshold', default=0.7, help='Minimum quality score')
def discover(query: str, max_pages: int, quality_threshold: float):
    """Discover content related to a query"""
    async def _discover():
        try:
            console.print(f"🔍 Discovering content for: {query}")
            results = await crawailer_api.discover(
                query,
                max_pages=max_pages,
                quality_threshold=quality_threshold
            )
            
            console.print(f"✨ Found {len(results)} results")
            _print_results_table(results)
                    
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")
        finally:
            await crawailer_api.cleanup()
    
    asyncio.run(_discover())


@main.command()
def setup():
    """Set up Crawailer (install browser dependencies)"""
    console.print("🔧 Setting up Crawailer...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            console.print("✅ Browser setup complete!", style="green")
        else:
            console.print(f"❌ Setup failed: {result.stderr}", style="red")
            
    except Exception as e:
        console.print(f"❌ Setup error: {e}", style="red")
        console.print("💡 Try running: python -m playwright install chromium")


@main.command()
def mcp():
    """Start Crawailer as an MCP server"""
    try:
        from .mcp import serve_mcp
        console.print("🚀 Starting Crawailer MCP server...")
        asyncio.run(serve_mcp())
    except ImportError:
        console.print("❌ MCP not installed. Install with: pip install crawailer[mcp]", style="red")
    except Exception as e:
        console.print(f"❌ MCP server error: {e}", style="red")


def _print_content_summary(content: WebContent):
    """Print a nice summary of extracted content"""
    panel_content = f"""
🌐 **URL:** {content.url}
📄 **Title:** {content.title}
👤 **Author:** {content.author or "Unknown"}
📅 **Published:** {content.published or "Unknown"}
⏱️  **Reading Time:** {content.reading_time}
📊 **Quality Score:** {content.quality_score:.1f}/10
🏷️  **Type:** {content.content_type}
📝 **Word Count:** {content.word_count:,}

**Summary:** {content.summary}
    """.strip()
    
    console.print(Panel(panel_content, title="📄 Content Summary", expand=False))


def _print_results_table(results: List[WebContent]):
    """Print results in a nice table format"""
    if not results:
        console.print("No results to display")
        return
    
    table = Table(title="🕷️ Crawl Results")
    table.add_column("Title", style="cyan", no_wrap=False, max_width=40)
    table.add_column("URL", style="blue", no_wrap=True, max_width=30)
    table.add_column("Words", justify="right", style="green")
    table.add_column("Quality", justify="right", style="yellow")
    table.add_column("Type", style="magenta")
    
    for content in results:
        table.add_row(
            content.title[:40] + "..." if len(content.title) > 40 else content.title,
            content.url[:30] + "..." if len(content.url) > 30 else content.url,
            f"{content.word_count:,}",
            f"{content.quality_score:.1f}",
            content.content_type
        )
    
    console.print(table)


if __name__ == '__main__':
    main()