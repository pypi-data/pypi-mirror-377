#!/bin/bash
# Crawailer Test Server Startup Script

set -e

echo "🕷️ Starting Crawailer Test Server..."

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Navigate to test server directory
cd "$(dirname "$0")"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating default .env file..."
    cat > .env << EOF
# Crawailer Test Server Configuration
COMPOSE_PROJECT_NAME=crawailer-test
HTTP_PORT=8083
HTTPS_PORT=8443
DNS_PORT=53
ENABLE_DNS=false
ENABLE_LOGGING=true
ENABLE_CORS=true
EOF
fi

# Start services
echo "🚀 Starting Docker services..."
if docker compose up -d; then
    echo "✅ Services started successfully!"
else
    echo "❌ Failed to start services"
    exit 1
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8083/health > /dev/null 2>&1; then
        echo "✅ Test server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout waiting for server to start"
        docker compose logs caddy
        exit 1
    fi
    sleep 1
done

# Display service information
echo ""
echo "🌐 Test Server URLs:"
echo "   Main Hub: http://localhost:8083"
echo "   SPA Demo: http://localhost:8083/spa/"
echo "   E-commerce: http://localhost:8083/shop/"
echo "   Documentation: http://localhost:8083/docs/"
echo "   News Site: http://localhost:8083/news/"
echo "   Static Files: http://localhost:8083/static/"
echo ""
echo "🔌 API Endpoints:"
echo "   Health Check: http://localhost:8083/health"
echo "   Users API: http://localhost:8083/api/users"
echo "   Products API: http://localhost:8083/api/products"
echo "   Slow Response: http://localhost:8083/api/slow"
echo "   Error Test: http://localhost:8083/api/error"
echo ""

# Test basic functionality
echo "🧪 Running basic health checks..."

# Test main endpoints
endpoints=(
    "http://localhost:8083/health"
    "http://localhost:8083/api/users"
    "http://localhost:8083/api/products"
    "http://localhost:8083/"
    "http://localhost:8083/spa/"
    "http://localhost:8083/shop/"
    "http://localhost:8083/docs/"
    "http://localhost:8083/news/"
)

failed_endpoints=()

for endpoint in "${endpoints[@]}"; do
    if curl -s -f "$endpoint" > /dev/null; then
        echo "   ✅ $endpoint"
    else
        echo "   ❌ $endpoint"
        failed_endpoints+=("$endpoint")
    fi
done

if [ ${#failed_endpoints[@]} -gt 0 ]; then
    echo ""
    echo "⚠️ Some endpoints failed health checks:"
    for endpoint in "${failed_endpoints[@]}"; do
        echo "   - $endpoint"
    done
    echo ""
    echo "📋 Troubleshooting:"
    echo "   - Check logs: docker compose logs"
    echo "   - Restart services: docker compose restart"
    echo "   - Check ports: netstat -tulpn | grep :8083"
fi

echo ""
echo "🎯 Test Server Ready!"
echo "   Use these URLs in your Crawailer tests for controlled, reproducible scenarios."
echo "   All traffic stays local - no external dependencies!"
echo ""
echo "📚 Documentation: test-server/README.md"
echo "🛑 Stop server: docker compose down"
echo "📊 View logs: docker compose logs -f"
echo ""