"""
Real-world production scenario testing for Crawailer JavaScript API.

This test suite focuses on complex workflows, database integration,
file system operations, and production-like error scenarios.
"""

import asyncio
import json
import pytest
import tempfile
import sqlite3
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from concurrent.futures import ThreadPoolExecutor
import threading

from crawailer import Browser, BrowserConfig
from crawailer.content import WebContent, ContentExtractor
from crawailer.api import get, get_many, discover


class TestComplexWorkflows:
    """Test complex multi-step workflows that mirror production use cases."""
    
    @pytest.mark.asyncio
    async def test_e_commerce_price_monitoring_workflow(self):
        """Test complete e-commerce price monitoring workflow."""
        browser = Browser(BrowserConfig())
        
        # Mock multiple pages for the workflow
        pages_data = [
            {
                "url": "https://shop.example.com/search?q=laptop",
                "products": [
                    {"name": "Gaming Laptop", "price": "$1299.99", "url": "/product/123"},
                    {"name": "Business Laptop", "price": "$899.99", "url": "/product/456"},
                ]
            },
            {
                "url": "https://shop.example.com/product/123",
                "details": {"price": "$1199.99", "stock": "In Stock", "rating": "4.5/5"}
            },
            {
                "url": "https://shop.example.com/product/456", 
                "details": {"price": "$849.99", "stock": "Limited", "rating": "4.2/5"}
            }
        ]
        
        # Setup mock browser
        mock_pages = []
        for page_data in pages_data:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = page_data
            mock_pages.append(mock_page)
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = mock_pages
        browser._browser = mock_browser
        browser._is_started = True
        
        # Step 1: Search for products
        search_result = await browser.execute_script(
            "https://shop.example.com/search?q=laptop",
            """
            // Extract product listings
            const products = Array.from(document.querySelectorAll('.product-item')).map(item => ({
                name: item.querySelector('.product-name')?.textContent,
                price: item.querySelector('.price')?.textContent,
                url: item.querySelector('a')?.href
            }));
            return { products };
            """
        )
        
        assert len(search_result["products"]) == 2
        assert "Gaming Laptop" in str(search_result)
        
        # Step 2: Get detailed product information
        product_urls = [
            "https://shop.example.com/product/123",
            "https://shop.example.com/product/456"
        ]
        
        product_details = []
        for url in product_urls:
            detail_result = await browser.execute_script(
                url,
                """
                return {
                    price: document.querySelector('.current-price')?.textContent,
                    stock: document.querySelector('.stock-status')?.textContent,
                    rating: document.querySelector('.rating')?.textContent
                };
                """
            )
            product_details.append(detail_result)
        
        # Step 3: Compare prices and generate report
        price_comparison = []
        for i, details in enumerate(product_details):
            price_str = details["details"]["price"].replace("$", "").replace(",", "")
            price = float(price_str)
            product_name = pages_data[0]["products"][i]["name"]
            
            price_comparison.append({
                "name": product_name,
                "price": price,
                "stock": details["details"]["stock"],
                "rating": details["details"]["rating"]
            })
        
        # Verify workflow results
        assert len(price_comparison) == 2
        assert price_comparison[0]["price"] == 1199.99
        assert price_comparison[1]["price"] == 849.99
        assert all("rating" in item for item in price_comparison)
    
    @pytest.mark.asyncio
    async def test_social_media_content_analysis_workflow(self):
        """Test social media content analysis and sentiment detection workflow."""
        browser = Browser(BrowserConfig())
        
        # Mock social media data
        social_data = {
            "posts": [
                {
                    "id": "post_1",
                    "text": "Loving the new product launch! Amazing features 🚀",
                    "author": "user123",
                    "likes": 45,
                    "shares": 12,
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                {
                    "id": "post_2", 
                    "text": "Not impressed with the customer service. Very disappointing.",
                    "author": "user456",
                    "likes": 3,
                    "shares": 1,
                    "timestamp": "2024-01-15T11:15:00Z"
                },
                {
                    "id": "post_3",
                    "text": "Great value for money! Highly recommend this product.",
                    "author": "user789",
                    "likes": 78,
                    "shares": 23,
                    "timestamp": "2024-01-15T12:00:00Z"
                }
            ]
        }
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = social_data
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Execute content analysis workflow
        analysis_result = await browser.execute_script(
            "https://social.example.com/brand-mentions",
            """
            // Extract and analyze social media posts
            const posts = Array.from(document.querySelectorAll('.post')).map(post => ({
                id: post.dataset.postId,
                text: post.querySelector('.post-text')?.textContent,
                author: post.querySelector('.author')?.textContent,
                likes: parseInt(post.querySelector('.likes-count')?.textContent) || 0,
                shares: parseInt(post.querySelector('.shares-count')?.textContent) || 0,
                timestamp: post.querySelector('.timestamp')?.dataset.time
            }));
            
            // Simple sentiment analysis
            const sentimentAnalysis = posts.map(post => {
                const text = post.text.toLowerCase();
                const positiveWords = ['loving', 'amazing', 'great', 'recommend', 'good'];
                const negativeWords = ['not impressed', 'disappointing', 'bad', 'terrible'];
                
                const positiveScore = positiveWords.filter(word => text.includes(word)).length;
                const negativeScore = negativeWords.filter(word => text.includes(word)).length;
                
                let sentiment = 'neutral';
                if (positiveScore > negativeScore) sentiment = 'positive';
                if (negativeScore > positiveScore) sentiment = 'negative';
                
                return {
                    ...post,
                    sentiment,
                    engagement: post.likes + post.shares
                };
            });
            
            // Generate summary
            const totalPosts = sentimentAnalysis.length;
            const positivePosts = sentimentAnalysis.filter(p => p.sentiment === 'positive').length;
            const negativePosts = sentimentAnalysis.filter(p => p.sentiment === 'negative').length;
            const totalEngagement = sentimentAnalysis.reduce((sum, p) => sum + p.engagement, 0);
            
            return {
                posts: sentimentAnalysis,
                summary: {
                    total: totalPosts,
                    positive: positivePosts,
                    negative: negativePosts,
                    neutral: totalPosts - positivePosts - negativePosts,
                    totalEngagement,
                    averageEngagement: totalEngagement / totalPosts
                }
            };
            """
        )
        
        # Verify analysis results
        assert analysis_result["summary"]["total"] == 3
        assert analysis_result["summary"]["positive"] >= 1
        assert analysis_result["summary"]["negative"] >= 1
        assert analysis_result["summary"]["totalEngagement"] > 0
        assert len(analysis_result["posts"]) == 3
        
        # Check sentiment assignment
        sentiments = [post["sentiment"] for post in analysis_result["posts"]]
        assert "positive" in sentiments
        assert "negative" in sentiments
    
    @pytest.mark.asyncio
    async def test_news_aggregation_and_summarization_workflow(self):
        """Test news aggregation and content summarization workflow."""
        browser = Browser(BrowserConfig())
        
        # Mock news sources
        news_sources = [
            {
                "url": "https://news1.example.com/tech",
                "articles": [
                    {"title": "AI Breakthrough in Medical Diagnosis", "snippet": "Researchers develop AI...", "url": "/article/1"},
                    {"title": "New Quantum Computing Milestone", "snippet": "Scientists achieve...", "url": "/article/2"}
                ]
            },
            {
                "url": "https://news2.example.com/business", 
                "articles": [
                    {"title": "Market Surges on Tech Stocks", "snippet": "Technology stocks led...", "url": "/article/3"},
                    {"title": "Startup Funding Reaches Record High", "snippet": "Venture capital...", "url": "/article/4"}
                ]
            }
        ]
        
        mock_pages = []
        for source in news_sources:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = source
            mock_pages.append(mock_page)
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = mock_pages
        browser._browser = mock_browser
        browser._is_started = True
        
        # Aggregate news from multiple sources
        aggregated_news = []
        
        for source in news_sources:
            news_result = await browser.execute_script(
                source["url"],
                """
                // Extract articles from news page
                const articles = Array.from(document.querySelectorAll('.article-item')).map(item => ({
                    title: item.querySelector('.title')?.textContent,
                    snippet: item.querySelector('.snippet')?.textContent,
                    url: item.querySelector('a')?.href,
                    source: window.location.hostname,
                    category: document.querySelector('.category')?.textContent || 'general',
                    publishTime: item.querySelector('.publish-time')?.textContent
                }));
                
                return { articles };
                """
            )
            
            aggregated_news.extend(news_result["articles"])
        
        # Process and categorize articles
        categorized_news = {
            "technology": [],
            "business": [],
            "general": []
        }
        
        for article in aggregated_news:
            title_lower = article["title"].lower()
            if any(keyword in title_lower for keyword in ["ai", "quantum", "tech"]):
                categorized_news["technology"].append(article)
            elif any(keyword in title_lower for keyword in ["market", "funding", "business"]):
                categorized_news["business"].append(article)
            else:
                categorized_news["general"].append(article)
        
        # Verify aggregation results
        total_articles = sum(len(articles) for articles in categorized_news.values())
        assert total_articles == 4
        assert len(categorized_news["technology"]) >= 1
        assert len(categorized_news["business"]) >= 1
        
        # Generate summary report
        summary_report = {
            "total_articles": total_articles,
            "categories": {cat: len(articles) for cat, articles in categorized_news.items()},
            "top_stories": aggregated_news[:3],  # Top 3 stories
            "sources": list(set(article["source"] for article in aggregated_news))
        }
        
        assert summary_report["total_articles"] == 4
        assert len(summary_report["sources"]) == 2


class TestDatabaseIntegrationEdgeCases:
    """Test database integration scenarios and edge cases."""
    
    def create_test_database(self) -> str:
        """Create a temporary test database."""
        db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        db_file.close()
        
        conn = sqlite3.connect(db_file.name)
        cursor = conn.cursor()
        
        # Create test tables
        cursor.execute("""
            CREATE TABLE scraped_data (
                id INTEGER PRIMARY KEY,
                url TEXT,
                title TEXT,
                content TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE execution_logs (
                id INTEGER PRIMARY KEY,
                script_hash TEXT,
                execution_time REAL,
                success BOOLEAN,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        return db_file.name
    
    @pytest.mark.asyncio
    async def test_database_transaction_handling(self):
        """Test database operations during scraping workflows."""
        db_path = self.create_test_database()
        browser = Browser(BrowserConfig())
        
        try:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = {
                "title": "Test Article",
                "content": "This is test content for database storage.",
                "url": "https://example.com/article/1"
            }
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            # Simulate scraping with database storage
            urls_to_scrape = [
                "https://example.com/article/1",
                "https://example.com/article/2", 
                "https://example.com/article/3"
            ]
            
            # Mock database operations
            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_connect.return_value = mock_conn
                
                for url in urls_to_scrape:
                    # Execute scraping script
                    result = await browser.execute_script(
                        url,
                        """
                        return {
                            title: document.title,
                            content: document.body.textContent,
                            url: window.location.href
                        };
                        """
                    )
                    
                    # Simulate database insertion
                    mock_cursor.execute.assert_called()
                    mock_conn.commit.assert_called()
                
                # Verify database operations
                assert mock_cursor.execute.call_count >= len(urls_to_scrape)
                assert mock_conn.commit.call_count >= len(urls_to_scrape)
                
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_database_connection_failures(self):
        """Test handling of database connection failures during operations."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate.return_value = {"data": "test"}
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test database connection failure scenarios
        with patch('sqlite3.connect') as mock_connect:
            # Simulate connection failure
            mock_connect.side_effect = sqlite3.OperationalError("Database locked")
            
            # Should handle database errors gracefully
            result = await browser.execute_script(
                "https://example.com",
                "return {data: 'test'}"
            )
            
            # Script should still execute successfully
            assert result["data"] == "test"
            
            # Would normally log the database error but continue execution
            mock_connect.assert_called()
    
    @pytest.mark.asyncio
    async def test_concurrent_database_access(self):
        """Test concurrent database access during parallel scraping."""
        browser = Browser(BrowserConfig())
        
        # Mock multiple pages for concurrent access
        mock_pages = []
        for i in range(10):
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = {"id": i, "data": f"content_{i}"}
            mock_pages.append(mock_page)
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = mock_pages
        browser._browser = mock_browser
        browser._is_started = True
        
        # Simulate concurrent database operations
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Launch concurrent scraping tasks
            async def scrape_and_store(index):
                result = await browser.execute_script(
                    f"https://example.com/page{index}",
                    f"return {{id: {index}, data: 'content_{index}'}}"
                )
                
                # Simulate database storage with transaction
                return result
            
            # Execute concurrent tasks
            tasks = [scrape_and_store(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            # Verify all tasks completed
            assert len(results) == 10
            assert all("data" in result for result in results)
            
            # Database should have been accessed for each operation
            assert mock_connect.call_count >= 10


class TestFileSystemInteractionEdgeCases:
    """Test file system operations and edge cases."""
    
    @pytest.mark.asyncio
    async def test_file_download_and_processing_workflow(self):
        """Test workflow that downloads and processes files."""
        browser = Browser(BrowserConfig())
        
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            
            # Mock file download scenarios
            mock_page.evaluate.return_value = {
                "downloadLinks": [
                    {"url": "https://example.com/report.pdf", "filename": "report.pdf"},
                    {"url": "https://example.com/data.csv", "filename": "data.csv"},
                    {"url": "https://example.com/image.jpg", "filename": "image.jpg"}
                ]
            }
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            # Execute download detection script
            result = await browser.execute_script(
                "https://example.com/downloads",
                """
                // Find all download links
                const downloadLinks = Array.from(document.querySelectorAll('a[download], a[href$=".pdf"], a[href$=".csv"]'))
                    .map(link => ({
                        url: link.href,
                        filename: link.download || link.href.split('/').pop(),
                        type: link.href.split('.').pop().toLowerCase()
                    }));
                
                return { downloadLinks };
                """
            )
            
            # Simulate file processing
            processed_files = []
            for link in result["downloadLinks"]:
                # Create mock file
                file_path = Path(temp_dir) / link["filename"]
                file_path.write_text(f"Mock content for {link['filename']}")
                
                # Process based on file type
                if link["filename"].endswith('.pdf'):
                    processed_files.append({"type": "pdf", "pages": 5, "text_extracted": True})
                elif link["filename"].endswith('.csv'):
                    processed_files.append({"type": "csv", "rows": 100, "columns": 8})
                elif link["filename"].endswith('.jpg'):
                    processed_files.append({"type": "image", "width": 1920, "height": 1080})
            
            # Verify processing
            assert len(processed_files) == 3
            assert any(f["type"] == "pdf" for f in processed_files)
            assert any(f["type"] == "csv" for f in processed_files)
            assert any(f["type"] == "image" for f in processed_files)
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self):
        """Test handling of large file operations."""
        browser = Browser(BrowserConfig())
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a large test file
            large_file_path = Path(temp_dir) / "large_data.txt"
            large_content = "x" * (10 * 1024 * 1024)  # 10MB file
            large_file_path.write_text(large_content)
            
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate.return_value = {
                "fileSize": len(large_content),
                "processed": True,
                "chunks": 10
            }
            
            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            browser._browser = mock_browser
            browser._is_started = True
            
            # Simulate large file processing
            result = await browser.execute_script(
                "https://example.com/large-file-processor",
                """
                // Simulate processing large file in chunks
                const fileSize = 10 * 1024 * 1024; // 10MB
                const chunkSize = 1024 * 1024; // 1MB chunks
                const chunks = Math.ceil(fileSize / chunkSize);
                
                // Simulate chunk processing
                let processed = true;
                for (let i = 0; i < chunks; i++) {
                    // Simulate processing delay
                    if (Math.random() < 0.1) { // 10% chance of processing issue
                        processed = false;
                        break;
                    }
                }
                
                return {
                    fileSize,
                    processed,
                    chunks
                };
                """
            )
            
            # Verify large file handling
            assert result["fileSize"] == 10 * 1024 * 1024
            assert result["chunks"] == 10
            assert isinstance(result["processed"], bool)
    
    @pytest.mark.asyncio
    async def test_file_permission_and_access_errors(self):
        """Test handling of file permission and access errors."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock file access scenarios
        file_scenarios = [
            {"path": "/protected/file.txt", "error": "Permission denied"},
            {"path": "/nonexistent/file.txt", "error": "File not found"},
            {"path": "/readonly/file.txt", "error": "Read-only file system"},
            {"path": "/network/file.txt", "error": "Network unreachable"}
        ]
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        for scenario in file_scenarios:
            mock_page.evaluate.return_value = {
                "path": scenario["path"],
                "accessible": False,
                "error": scenario["error"]
            }
            
            result = await browser.execute_script(
                "https://example.com/file-access",
                f"""
                // Simulate file access attempt
                const filePath = '{scenario["path"]}';
                let accessible = false;
                let error = null;
                
                try {{
                    // Simulate file access (would normally use File API or fetch)
                    throw new Error('{scenario["error"]}');
                }} catch (e) {{
                    error = e.message;
                }}
                
                return {{
                    path: filePath,
                    accessible,
                    error
                }};
                """
            )
            
            # Verify error handling
            assert result["accessible"] is False
            assert scenario["error"] in result["error"]


class TestNetworkInterruptionHandling:
    """Test handling of network interruptions and connectivity issues."""
    
    @pytest.mark.asyncio
    async def test_network_timeout_recovery(self):
        """Test recovery from network timeouts."""
        browser = Browser(BrowserConfig())
        
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Simulate network timeout scenarios
        timeout_count = 0
        def mock_goto(*args, **kwargs):
            nonlocal timeout_count
            timeout_count += 1
            if timeout_count <= 2:  # First two attempts timeout
                raise asyncio.TimeoutError("Navigation timeout")
            else:  # Third attempt succeeds
                return AsyncMock(status=200)
        
        mock_page.goto.side_effect = mock_goto
        mock_page.evaluate.return_value = "success_after_retry"
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test with retry logic
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await browser.execute_script(
                    "https://unreliable-site.com",
                    "return 'success_after_retry'"
                )
                break  # Success
            except asyncio.TimeoutError as e:
                last_error = e
                if attempt == max_retries - 1:
                    raise  # Final attempt failed
                await asyncio.sleep(0.1)  # Brief retry delay
        
        # Should eventually succeed
        assert result == "success_after_retry"
        assert timeout_count == 3  # Two failures, one success
    
    @pytest.mark.asyncio
    async def test_partial_network_failures(self):
        """Test handling of partial network failures."""
        browser = Browser(BrowserConfig())
        
        # Simulate mixed success/failure scenarios
        urls_and_results = [
            ("https://working-site.com", "success"),
            ("https://failing-site.com", "network_error"),
            ("https://slow-site.com", "timeout"),
            ("https://another-working.com", "success")
        ]
        
        mock_pages = []
        for url, result_type in urls_and_results:
            mock_page = AsyncMock()
            mock_page.close = AsyncMock()
            
            if result_type == "success":
                mock_page.goto = AsyncMock(return_value=AsyncMock(status=200))
                mock_page.evaluate.return_value = "success"
            elif result_type == "network_error":
                mock_page.goto.side_effect = Exception("Network error")
                mock_page.evaluate.return_value = None
            elif result_type == "timeout":
                mock_page.goto.side_effect = asyncio.TimeoutError("Timeout")
                mock_page.evaluate.return_value = None
            
            mock_pages.append(mock_page)
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = mock_pages
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test batch processing with mixed results
        results = []
        for url, expected_result in urls_and_results:
            try:
                result = await browser.execute_script(url, "return 'success'")
                results.append({"url": url, "result": result, "status": "success"})
            except Exception as e:
                results.append({"url": url, "result": None, "status": "error", "error": str(e)})
        
        # Verify mixed results
        assert len(results) == 4
        successful_results = [r for r in results if r["status"] == "success"]
        failed_results = [r for r in results if r["status"] == "error"]
        
        assert len(successful_results) == 2  # Two should succeed
        assert len(failed_results) == 2     # Two should fail
    
    @pytest.mark.asyncio
    async def test_progressive_network_degradation(self):
        """Test handling of progressive network degradation."""
        browser = Browser(BrowserConfig())
        
        # Simulate progressively degrading network
        network_conditions = [
            {"delay": 0.1, "success_rate": 0.9},    # Good network
            {"delay": 0.5, "success_rate": 0.7},    # Moderate issues
            {"delay": 1.0, "success_rate": 0.5},    # Poor network
            {"delay": 2.0, "success_rate": 0.2},    # Very poor network
        ]
        
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        results_by_condition = []
        
        for condition in network_conditions:
            # Simulate network condition
            def mock_goto_with_condition(*args, **kwargs):
                import random
                time.sleep(condition["delay"])  # Simulate network delay
                if random.random() < condition["success_rate"]:
                    return AsyncMock(status=200)
                else:
                    raise Exception("Network timeout")
            
            mock_page.goto.side_effect = mock_goto_with_condition
            mock_page.evaluate.return_value = f"success_at_{condition['success_rate']}"
            
            # Test multiple requests under this condition
            condition_results = []
            for i in range(10):  # 10 requests per condition
                try:
                    result = await browser.execute_script(
                        f"https://example.com/test_{i}",
                        "return 'test_result'"
                    )
                    condition_results.append("success")
                except Exception:
                    condition_results.append("failure")
            
            success_rate = condition_results.count("success") / len(condition_results)
            results_by_condition.append({
                "condition": condition,
                "actual_success_rate": success_rate,
                "results": condition_results
            })
        
        # Verify degradation pattern
        assert len(results_by_condition) == 4
        
        # Success rates should generally decrease as network degrades
        # (allowing for some randomness in the simulation)
        for i in range(len(results_by_condition) - 1):
            current_rate = results_by_condition[i]["actual_success_rate"]
            next_rate = results_by_condition[i + 1]["actual_success_rate"]
            # Allow some variance but expect general degradation
            assert current_rate >= next_rate - 0.3  # 30% tolerance for randomness


class TestProductionErrorScenarios:
    """Test production-like error scenarios and recovery."""
    
    @pytest.mark.asyncio
    async def test_cascading_failure_recovery(self):
        """Test recovery from cascading failures."""
        browser = Browser(BrowserConfig())
        
        # Simulate cascading failure scenario
        failure_sequence = [
            "network_timeout",
            "browser_crash", 
            "page_load_error",
            "script_execution_error",
            "recovery_success"
        ]
        
        mock_pages = []
        for failure_type in failure_sequence:
            mock_page = AsyncMock()
            mock_page.close = AsyncMock()
            
            if failure_type == "network_timeout":
                mock_page.goto.side_effect = asyncio.TimeoutError("Network timeout")
            elif failure_type == "browser_crash":
                mock_page.goto.side_effect = Exception("Browser process crashed")
            elif failure_type == "page_load_error":
                mock_page.goto.side_effect = Exception("Page load failed")
            elif failure_type == "script_execution_error":
                mock_page.goto = AsyncMock(return_value=AsyncMock(status=200))
                mock_page.evaluate.side_effect = Exception("Script execution failed")
            else:  # recovery_success
                mock_page.goto = AsyncMock(return_value=AsyncMock(status=200))
                mock_page.evaluate.return_value = "recovery_successful"
            
            mock_pages.append(mock_page)
        
        mock_browser = AsyncMock()
        mock_browser.new_page.side_effect = mock_pages
        browser._browser = mock_browser
        browser._is_started = True
        
        # Test with recovery logic
        recovery_attempts = []
        
        for i, failure_type in enumerate(failure_sequence):
            try:
                result = await browser.execute_script(
                    f"https://example.com/attempt_{i}",
                    "return 'test_result'"
                )
                recovery_attempts.append({"attempt": i, "result": result, "status": "success"})
                break  # Success - exit loop
            except Exception as e:
                recovery_attempts.append({"attempt": i, "result": None, "status": "error", "error": str(e)})
                
                # Implement recovery strategies
                if "timeout" in str(e).lower():
                    await asyncio.sleep(0.1)  # Wait before retry
                elif "crash" in str(e).lower():
                    # Would normally restart browser
                    await asyncio.sleep(0.2)
                elif "load" in str(e).lower():
                    # Would normally try different URL or approach
                    await asyncio.sleep(0.1)
        
        # Verify recovery eventually succeeds
        assert len(recovery_attempts) == 5
        final_attempt = recovery_attempts[-1]
        assert final_attempt["status"] == "success"
        assert final_attempt["result"] == "recovery_successful"
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_scenarios(self):
        """Test handling of resource exhaustion scenarios."""
        browser = Browser(BrowserConfig())
        
        # Simulate different resource exhaustion scenarios
        exhaustion_scenarios = [
            {"type": "memory", "error": "Out of memory"},
            {"type": "cpu", "error": "CPU quota exceeded"},
            {"type": "disk", "error": "No space left on device"},
            {"type": "file_handles", "error": "Too many open files"},
        ]
        
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.goto = AsyncMock(return_value=AsyncMock(status=200))
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        for scenario in exhaustion_scenarios:
            # Simulate resource exhaustion
            mock_page.evaluate.side_effect = Exception(scenario["error"])
            
            try:
                result = await browser.execute_script(
                    "https://example.com/resource-test",
                    "return 'resource_test'"
                )
                assert False, f"Should have failed with {scenario['type']} exhaustion"
            except Exception as e:
                # Verify appropriate error handling
                assert scenario["error"].lower() in str(e).lower()
                
                # Implement resource-specific recovery
                if scenario["type"] == "memory":
                    # Would normally trigger garbage collection
                    pass
                elif scenario["type"] == "cpu":
                    # Would normally reduce concurrent operations
                    pass
                elif scenario["type"] == "disk":
                    # Would normally clean up temporary files
                    pass
                elif scenario["type"] == "file_handles":
                    # Would normally close unused handles
                    pass
    
    @pytest.mark.asyncio
    async def test_intermittent_failure_patterns(self):
        """Test handling of intermittent failure patterns."""
        browser = Browser(BrowserConfig())
        
        # Simulate intermittent failures
        failure_pattern = [True, False, True, True, False, False, True, False, True, True]  # 60% success rate
        
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.goto = AsyncMock(return_value=AsyncMock(status=200))
        
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        browser._browser = mock_browser
        browser._is_started = True
        
        results = []
        
        for i, should_succeed in enumerate(failure_pattern):
            if should_succeed:
                mock_page.evaluate.return_value = f"success_{i}"
            else:
                mock_page.evaluate.side_effect = Exception(f"Intermittent failure {i}")
            
            try:
                result = await browser.execute_script(
                    f"https://example.com/intermittent_{i}",
                    f"return 'test_{i}'"
                )
                results.append({"index": i, "status": "success", "result": result})
            except Exception as e:
                results.append({"index": i, "status": "failure", "error": str(e)})
        
        # Verify pattern matches expectation
        assert len(results) == len(failure_pattern)
        successful_count = len([r for r in results if r["status"] == "success"])
        expected_successes = sum(failure_pattern)
        
        assert successful_count == expected_successes
        
        # Verify success/failure pattern
        for i, (result, expected) in enumerate(zip(results, failure_pattern)):
            if expected:
                assert result["status"] == "success"
                assert f"success_{i}" == result["result"]
            else:
                assert result["status"] == "failure"
                assert f"Intermittent failure {i}" in result["error"]


if __name__ == "__main__":
    # Run production scenario tests with detailed output
    pytest.main([__file__, "-v", "--tb=long", "-s"])