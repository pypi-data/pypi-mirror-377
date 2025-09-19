#!/usr/bin/env python3
"""
Test script to verify the local server is actually serving content.
This verifies that the Docker container is working and serving our test sites.
"""

import requests
import time
from urllib.parse import urljoin

def test_server_endpoints():
    """Test various server endpoints to verify they're working."""
    
    base_url = "http://localhost:8083"
    
    endpoints = [
        "/health",
        "/api/users", 
        "/api/products",
        "/",
        "/spa/",
        "/shop/",
        "/docs/",
        "/news/",
        "/static/"
    ]
    
    print("🧪 Testing Local Server Endpoints")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print()
    
    results = []
    
    for endpoint in endpoints:
        url = urljoin(base_url, endpoint)
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            status = "✅" if response.status_code == 200 else "❌"
            content_length = len(response.content)
            
            print(f"{status} {endpoint:15} - Status: {response.status_code}, Size: {content_length:>6} bytes, Time: {response_time:.3f}s")
            
            results.append({
                'endpoint': endpoint,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'content_length': content_length,
                'response_time': response_time
            })
            
            # Check for specific content indicators
            if endpoint == "/health" and response.status_code == 200:
                print(f"   🏥 Health response: {response.text[:50]}")
            
            elif endpoint.startswith("/api/") and response.status_code == 200:
                if response.headers.get('content-type', '').startswith('application/json'):
                    print(f"   📊 JSON response detected")
                else:
                    print(f"   📄 Non-JSON response: {response.headers.get('content-type', 'unknown')}")
            
            elif endpoint in ["/", "/spa/", "/shop/", "/docs/", "/news/"] and response.status_code == 200:
                if "html" in response.headers.get('content-type', '').lower():
                    # Look for title tag
                    if '<title>' in response.text:
                        title_start = response.text.find('<title>') + 7
                        title_end = response.text.find('</title>', title_start)
                        title = response.text[title_start:title_end] if title_end > title_start else "Unknown"
                        print(f"   📰 Page title: {title}")
                    
                    # Look for window.testData
                    if 'window.testData' in response.text:
                        print(f"   🔬 JavaScript test data available")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint:15} - Error: {str(e)[:60]}")
            results.append({
                'endpoint': endpoint,
                'status_code': 0,
                'success': False,
                'error': str(e)
            })
    
    print()
    print("📊 Summary")
    print("=" * 50)
    
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total} ({successful/total*100:.1f}%)")
    
    if successful == total:
        print("🎉 All endpoints are working perfectly!")
        print()
        print("🌐 You can now visit these URLs in your browser:")
        for endpoint in ["/", "/spa/", "/shop/", "/docs/", "/news/"]:
            print(f"   • {urljoin(base_url, endpoint)}")
    else:
        print("⚠️  Some endpoints had issues. Check the Docker container status:")
        print("   docker compose ps")
        print("   docker compose logs")
    
    return results

if __name__ == "__main__":
    test_server_endpoints()