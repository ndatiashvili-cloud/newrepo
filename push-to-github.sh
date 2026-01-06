#!/bin/bash

# RND Monitoring Platform - GitHub Setup Script
# This script initializes git and pushes to GitHub

echo "🚀 RND Monitoring Platform - GitHub Setup"
echo "=========================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git repository
echo "📦 Initializing git repository..."
git init

# Add all files
echo "📝 Adding all files..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: RND Monitoring Platform v3.0.0

- Complete rebranding from WARD FLUX to RND
- Enhanced Zabbix integration with topology visualization
- PostgreSQL and Elasticsearch integrations
- Fixed diagnostics (ping/traceroute) bugs
- Comprehensive documentation and deployment scripts
- Docker Compose configuration
- Production-ready setup"

# Instructions for user
echo ""
echo "✅ Repository initialized successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub (https://github.com/new)"
echo "2. Copy the repository URL (e.g., https://github.com/username/rnd-monitoring.git)"
echo "3. Run these commands:"
echo ""
echo "   git remote add origin YOUR_GITHUB_REPO_URL"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Example:"
echo "   git remote add origin https://github.com/yourusername/rnd-monitoring.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
