#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# RND Monitoring - Complete Setup Script
# ═══════════════════════════════════════════════════════════════════

set -e

echo "════════════════════════════════════════════════"
echo "   RND MONITORING - AUTOMATED SETUP"
echo "   Research & Development Team"
echo "════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}[1/6] Checking prerequisites...${NC}"
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Error: Docker is not installed${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { echo -e "${RED}Error: Docker Compose is not installed${NC}" >&2; exit 1; }
echo -e "${GREEN}✓ Prerequisites OK${NC}"

# Generate .env file
echo -e "${BLUE}[2/6] Creating .env configuration...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# ═══════════════════════════════════════════════════════════════════
# RND Monitoring - Environment Configuration
# ═══════════════════════════════════════════════════════════════════

# Database Configuration
POSTGRES_PASSWORD=rnd_secure_password_2024
DATABASE_URL=postgresql+psycopg2://rnd_user:rnd_secure_password_2024@postgres:5432/rnd_monitoring
USE_POSTGRES=true

# Redis Configuration
REDIS_PASSWORD=rnd_redis_password_2024
REDIS_URL=redis://:rnd_redis_password_2024@redis:6379/0

# Security Keys (IMPORTANT: Change these in production!)
SECRET_KEY=rnd-secret-key-change-in-production-$(openssl rand -hex 16)
ENCRYPTION_KEY=rnd-encryption-key-change-in-production-$(openssl rand -hex 16)
DEFAULT_ADMIN_PASSWORD=admin123

# VictoriaMetrics
VICTORIA_URL=http://victoriametrics:8428

# Application Settings
CORS_ORIGINS=*
LOG_LEVEL=INFO

# Zabbix Integration (Optional - configure if using Zabbix)
ZABBIX_URL=http://your-zabbix-server/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix

# External Integrations (Optional)
# PostgreSQL Monitoring
EXTERNAL_POSTGRES_HOST=
EXTERNAL_POSTGRES_PORT=5432
EXTERNAL_POSTGRES_USER=
EXTERNAL_POSTGRES_PASSWORD=
EXTERNAL_POSTGRES_DB=

# Elasticsearch Monitoring
ELASTICSEARCH_HOST=
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USER=
ELASTICSEARCH_PASSWORD=
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${YELLOW}! .env file already exists, skipping${NC}"
fi

# Create required directories
echo -e "${BLUE}[3/6] Creating directories...${NC}"
mkdir -p data logs migrations frontend/dist
chmod -R 755 data logs
echo -e "${GREEN}✓ Directories created${NC}"

# Pull Docker images
echo -e "${BLUE}[4/6] Pulling Docker images...${NC}"
docker-compose pull
echo -e "${GREEN}✓ Images pulled${NC}"

# Build application
echo -e "${BLUE}[5/6] Building RND Monitoring application...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✓ Application built${NC}"

# Start services
echo -e "${BLUE}[6/6] Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"

# Wait for services to be healthy
echo ""
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 15

# Check health
echo ""
echo -e "${BLUE}Checking service health...${NC}"
if curl -f http://localhost:5001/api/v1/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${YELLOW}! API is starting up, may take a few more seconds${NC}"
fi

# Display status
echo ""
echo "════════════════════════════════════════════════"
echo -e "${GREEN}   RND MONITORING - DEPLOYMENT COMPLETE!${NC}"
echo "════════════════════════════════════════════════"
echo ""
echo "Services running:"
echo "  • API:               http://localhost:5001"
echo "  • Frontend:          http://localhost:5001"
echo "  • PostgreSQL:        localhost:5432"
echo "  • Redis:             localhost:6379"
echo "  • VictoriaMetrics:   http://localhost:8428"
echo ""
echo "Default Login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Useful commands:"
echo "  • View logs:         docker-compose logs -f"
echo "  • Stop services:     docker-compose down"
echo "  • Restart:           docker-compose restart"
echo ""
echo "Documentation:"
echo "  • README.md"
echo "  • DEPLOYMENT.md"
echo "  • TROUBLESHOOTING.md"
echo ""
echo -e "${GREEN}Happy monitoring! 🚀${NC}"
echo "════════════════════════════════════════════════"
