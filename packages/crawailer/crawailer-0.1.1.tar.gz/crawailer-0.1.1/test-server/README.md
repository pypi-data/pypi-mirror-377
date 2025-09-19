# Crawailer Test Server

A comprehensive local test server providing controlled content for JavaScript API testing. This server eliminates external dependencies and provides reproducible test scenarios.

## 🏗️ Architecture

The test server is built using **Caddy** for HTTP serving and **DNSMasq** for local DNS resolution, all orchestrated with Docker Compose.

### Server Components

- **Caddy HTTP Server**: Serves multiple test sites with different scenarios
- **DNSMasq DNS Server**: Provides local domain resolution for test domains
- **Static Content**: Realistic test sites based on popular project patterns

## 🌐 Available Test Sites

| Site Type | Primary URL | Subdomain URL | Description |
|-----------|-------------|---------------|-------------|
| **Hub** | `localhost:8080` | `test.crawailer.local:8080` | Main navigation hub |
| **SPA** | `localhost:8080/spa/` | `spa.test.crawailer.local:8080` | React-style single page app |
| **E-commerce** | `localhost:8080/shop/` | `ecommerce.test.crawailer.local:8080` | Online store with cart |
| **Documentation** | `localhost:8080/docs/` | `docs.test.crawailer.local:8080` | API documentation site |
| **News/Blog** | `localhost:8080/news/` | - | Content-heavy news site |
| **Static Files** | `localhost:8080/static/` | - | File downloads and assets |

## 🔌 API Endpoints

### Main Server (`localhost:8080`)
- `/health` - Health check endpoint
- `/api/users` - User data (JSON)
- `/api/products` - Product catalog (JSON)
- `/api/slow` - Slow response (2s delay)
- `/api/error` - Error simulation (500 status)

### API Subdomain (`api.test.crawailer.local:8080`)
- `/v1/users` - Enhanced user API
- `/v1/products` - Enhanced product API
- `/v1/analytics` - Analytics data
- `/v1/fast` - Fast response endpoint
- `/v1/slow` - Slow response (3s delay)
- `/v1/error` - Server error simulation
- `/v1/timeout` - Timeout simulation (10s)

## 🚀 Quick Start

### 1. Start the Test Server

```bash
cd test-server
docker compose up -d
```

### 2. Verify Services

```bash
# Check server status
curl http://localhost:8080/health

# Test API endpoints
curl http://localhost:8080/api/users
curl http://localhost:8080/api/products
```

### 3. Access Test Sites

Open your browser to:
- [localhost:8080](http://localhost:8080) - Main hub
- [localhost:8080/spa/](http://localhost:8080/spa/) - Single Page App
- [localhost:8080/shop/](http://localhost:8080/shop/) - E-commerce demo
- [localhost:8080/docs/](http://localhost:8080/docs/) - Documentation
- [localhost:8080/news/](http://localhost:8080/news/) - News site

## 🧪 JavaScript Testing Scenarios

Each test site includes comprehensive JavaScript for testing various scenarios:

### SPA (Single Page Application)
- **Client-side routing** with history API
- **State management** with local storage
- **Dynamic content loading** and updates
- **Modal dialogs** and form handling
- **Real-time data** simulation

**Test Capabilities:**
```javascript
// Navigate programmatically
window.testData.getCurrentPage()

// Interact with state
window.testData.totalTasks()
window.testData.cartItems()

// Generate dynamic content
window.testData.generateTimestamp()
```

### E-commerce Platform
- **Dynamic pricing** and inventory updates
- **Shopping cart** functionality
- **Product filtering** and search
- **Real-time notifications**
- **Simulated payment** flow

**Test Capabilities:**
```javascript
// Product operations
window.testData.totalProducts()
window.testData.searchProduct("iPhone")
window.testData.getProductById(1)

// Cart operations
window.testData.cartTotal()
window.testData.getCartContents()
```

### Documentation Site
- **Dynamic navigation** and content switching
- **Search functionality** with live results
- **API status** simulation
- **Code examples** with syntax highlighting
- **Interactive examples**

**Test Capabilities:**
```javascript
// Navigation and search
window.testData.currentSection()
window.testData.navigationItems()

// API simulation
window.testData.getApiStatus()
window.testData.getLiveMetrics()
```

### News/Blog Platform
- **Infinite scroll** and pagination
- **Real-time content** updates
- **Comment systems** simulation
- **Newsletter signup** handling
- **Article search** and filtering

**Test Capabilities:**
```javascript
// Content operations
window.testData.totalArticles()
window.testData.searchArticles("AI")
window.testData.getTrendingArticles()

// Dynamic updates
window.testData.currentPage()
window.testData.articlesLoaded()
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `test-server` directory:

```env
# Project identification
COMPOSE_PROJECT_NAME=crawailer-test

# Server configuration
HTTP_PORT=8080
HTTPS_PORT=8443
DNS_PORT=53

# Feature flags
ENABLE_DNS=false
ENABLE_LOGGING=true
ENABLE_CORS=true
```

### DNS Setup (Optional)

To use subdomain URLs, enable the DNS service:

```bash
# Enable DNS profile
docker compose --profile dns up -d

# Configure system DNS (Linux/macOS)
echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf
```

### Custom Domains

Add custom test domains to `dnsmasq.conf`:

```conf
address=/custom.test.crawailer.local/127.0.0.1
```

## 📊 Monitoring and Debugging

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f caddy
docker compose logs -f dnsmasq
```

### Health Checks

```bash
# Server health
curl http://localhost:8080/health

# API endpoints
curl http://localhost:8080/api/users | jq
curl http://api.test.crawailer.local:8080/v1/analytics | jq
```

### Performance Testing

```bash
# Load testing with curl
for i in {1..100}; do
  curl -s http://localhost:8080/api/users > /dev/null &
done
wait

# Response time testing
curl -w "@curl-format.txt" -s http://localhost:8080/api/slow
```

## 🧩 Integration with Test Suite

### Python Test Integration

```python
import pytest
from crawailer import get

class TestLocalServer:
    @pytest.fixture(autouse=True)
    def setup_server(self):
        # Ensure test server is running
        response = requests.get("http://localhost:8080/health")
        assert response.status_code == 200
    
    async def test_spa_navigation(self):
        # Test SPA routing
        content = await get(
            "http://localhost:8080/spa/",
            script="app.navigateToPage('tasks'); return app.currentPage;"
        )
        assert content.script_result == "tasks"
    
    async def test_ecommerce_cart(self):
        # Test shopping cart functionality
        content = await get(
            "http://localhost:8080/shop/",
            script="store.addToCart(1); return store.cart.length;"
        )
        assert content.script_result > 0
    
    async def test_dynamic_content(self):
        # Test dynamic content loading
        content = await get(
            "http://localhost:8080/news/",
            script="return newsApp.articles.length;"
        )
        assert content.script_result > 0
```

### JavaScript Execution Examples

```python
# Test complex workflows
result = await get(
    "http://localhost:8080/shop/",
    script="""
    // Add items to cart
    store.addToCart(1);
    store.addToCart(2);
    
    // Apply filters
    store.currentSort = 'price-low';
    store.renderProducts();
    
    // Return cart summary
    return {
        itemCount: store.cart.length,
        total: store.cart.reduce((sum, item) => sum + item.price, 0),
        currentSort: store.currentSort
    };
    """
)

print(f"Cart has {result.script_result['itemCount']} items")
print(f"Total: ${result.script_result['total']}")
```

## 🎯 Test Scenarios Covered

### ✅ Content Extraction
- **Static HTML** content parsing
- **Dynamic JavaScript** content rendering
- **SPA routing** and state changes
- **Infinite scroll** and pagination
- **Modal dialogs** and overlays

### ✅ User Interactions
- **Form submissions** and validation
- **Button clicks** and navigation
- **Search and filtering**
- **Shopping cart** operations
- **Authentication** flows (simulated)

### ✅ Performance Testing
- **Slow loading** scenarios
- **Large content** handling
- **Concurrent requests**
- **Error recovery**
- **Timeout handling**

### ✅ Browser Compatibility
- **Different viewport** sizes
- **Mobile responsive** design
- **Cross-browser** JavaScript features
- **Modern web APIs**

## 🔒 Security Features

- **CORS headers** configured for testing
- **No real authentication** (test data only)
- **Isolated environment** (localhost only)
- **No external dependencies**
- **Safe test data** (no PII)

## 📁 Directory Structure

```
test-server/
├── docker-compose.yml      # Service orchestration
├── Caddyfile              # HTTP server configuration
├── dnsmasq.conf           # DNS server configuration
├── .env                   # Environment variables
├── README.md              # This documentation
└── sites/                 # Test site content
    ├── hub/               # Main navigation hub
    ├── spa/               # Single page application
    ├── ecommerce/         # E-commerce demo
    ├── docs/              # Documentation site
    ├── news/              # News/blog platform
    └── static/            # Static files and downloads
        ├── index.html
        └── files/
            ├── data-export.csv
            ├── sample-document.pdf
            ├── test-image.jpg
            └── archive.zip
```

## 🛠️ Maintenance

### Adding New Test Sites

1. Create site directory: `mkdir sites/newsite`
2. Add HTML content with JavaScript test data
3. Update `Caddyfile` with new route
4. Restart services: `docker compose restart`

### Updating Content

Sites use vanilla HTML/CSS/JavaScript for maximum compatibility. Update files directly and refresh browser.

### Performance Optimization

- Enable gzip compression in Caddyfile
- Implement caching headers for static assets
- Monitor resource usage with `docker stats`

## 🎉 Benefits

✅ **Reproducible Testing** - Consistent content across test runs
✅ **No External Dependencies** - Works offline, no rate limits
✅ **Realistic Scenarios** - Based on real-world website patterns
✅ **Comprehensive Coverage** - Multiple site types and use cases
✅ **Easy Integration** - Drop-in replacement for external URLs
✅ **Fast Execution** - Local network speeds, immediate response
✅ **Safe Testing** - No impact on external services

This test server provides a comprehensive, controlled environment for validating the Crawailer JavaScript API enhancement with realistic, reproducible test scenarios.