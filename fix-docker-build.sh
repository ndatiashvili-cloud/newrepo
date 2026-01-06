#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# RND Monitoring Platform - Docker Build Fix Script
# ═══════════════════════════════════════════════════════════════════

echo "🔧 Fixing Docker build issues..."

# Stop any running containers
echo "📦 Stopping existing containers..."
docker-compose down

# Remove old images to force rebuild
echo "🗑️  Removing old images..."
docker-compose rm -f
docker rmi $(docker images -q newrepo-*) 2>/dev/null || true

# Generate package-lock.json if it doesn't exist
if [ ! -f frontend/package-lock.json ]; then
    echo "📝 Generating package-lock.json..."
    cd frontend
    npm install --package-lock-only
    cd ..
fi

# Rebuild and start
echo "🔨 Building containers..."
docker-compose build --no-cache

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check status
echo "✅ Checking service status..."
docker-compose ps

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Docker build fixed and services started!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📊 Access the application:"
echo "   - Web UI: http://localhost:8000"
echo "   - API: http://localhost:5001"
echo ""
echo "🔍 Check logs:"
echo "   docker-compose logs -f"
echo ""
