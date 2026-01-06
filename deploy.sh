#!/bin/bash

# RND Monitoring Platform - Complete Deployment Script
# Copyright (c) 2025 Research & Development Team

set -e

echo "=========================================="
echo "RND Monitoring Platform Deployment"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Warning: Running as root. This is not recommended for production."
fi

# Check prerequisites
echo "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo "Error: Docker is not installed. Please install Docker first."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Error: Docker Compose is not installed. Please install Docker Compose first."; exit 1; }

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ .env file created"
        echo ""
        echo "IMPORTANT: Please edit the .env file with your configuration before proceeding!"
        echo "Minimum required settings:"
        echo "  - SECRET_KEY (generate a secure random string)"
        echo "  - DATABASE_PASSWORD"
        echo "  - REDIS_PASSWORD"
        echo ""
        read -p "Have you configured the .env file? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Please configure .env file and run this script again."
            exit 1
        fi
    else
        echo "Error: .env.example file not found!"
        exit 1
    fi
else
    echo "✓ .env file exists"
fi

echo ""
echo "Starting deployment..."
echo ""

# Stop existing containers
echo "Stopping existing containers (if any)..."
docker-compose down 2>/dev/null || true

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/postgres data/redis data/victoriametrics logs

# Set permissions
echo "Setting permissions..."
chmod -R 755 data logs

# Pull latest images
echo "Pulling Docker images..."
docker-compose pull

# Build application
echo "Building RND Monitoring Platform..."
docker-compose build --no-cache

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

services=("postgres" "redis" "app" "celery_worker" "celery_beat" "flower")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
        all_healthy=false
    fi
done

echo ""
if [ "$all_healthy" = true ]; then
    echo "=========================================="
    echo "Deployment completed successfully!"
    echo "=========================================="
    echo ""
    echo "Access the platform at:"
    echo "  Web Interface: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Flower (Celery Monitor): http://localhost:5555"
    echo ""
    echo "Default credentials:"
    echo "  Username: admin"
    echo "  Password: (check your .env file for ADMIN_PASSWORD)"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo ""
    echo "For troubleshooting, see TROUBLESHOOTING.md"
    echo "=========================================="
else
    echo "=========================================="
    echo "Deployment completed with warnings!"
    echo "=========================================="
    echo ""
    echo "Some services are not running properly."
    echo "Check logs with: docker-compose logs"
    echo ""
    echo "For troubleshooting, see TROUBLESHOOTING.md"
    echo "=========================================="
    exit 1
fi
