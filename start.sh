#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# RND Monitoring Platform - Startup Script
# ═══════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════════"
echo "  RND - Research & Development Network Monitoring Platform"
echo "  Version 2.0.0 | Deployment Startup"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Use 'docker compose' or 'docker-compose'
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${BLUE}[1/6]${NC} Checking prerequisites..."

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file"
    echo -e "${YELLOW}⚠ Please edit .env and update passwords and keys!${NC}"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Check if critical env vars are set
if grep -q "your_secure_postgres_password_here" .env || grep -q "your_secret_key_here" .env; then
    echo -e "${YELLOW}⚠ Warning: Default values detected in .env${NC}"
    echo -e "${YELLOW}  For security, please update:${NC}"
    echo "  - POSTGRES_PASSWORD"
    echo "  - REDIS_PASSWORD"
    echo "  - SECRET_KEY"
    echo "  - ENCRYPTION_KEY"
    echo "  - DEFAULT_ADMIN_PASSWORD"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} Prerequisites checked"

echo -e "${BLUE}[2/6]${NC} Stopping existing containers..."
$DOCKER_COMPOSE down 2>/dev/null || true
echo -e "${GREEN}✓${NC} Stopped existing containers"

echo -e "${BLUE}[3/6]${NC} Building Docker images..."
$DOCKER_COMPOSE build --no-cache
echo -e "${GREEN}✓${NC} Images built successfully"

echo -e "${BLUE}[4/6]${NC} Starting services..."
$DOCKER_COMPOSE up -d
echo -e "${GREEN}✓${NC} Services started"

echo -e "${BLUE}[5/6]${NC} Waiting for services to be ready..."
echo -n "  Waiting for database"
for i in {1..30}; do
    if $DOCKER_COMPOSE exec -T postgres pg_isready -U rnd_user &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo -n "  Waiting for Redis"
for i in {1..30}; do
    if $DOCKER_COMPOSE exec -T redis redis-cli ping &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo -n "  Waiting for application"
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo -e "${BLUE}[6/6]${NC} Running database migrations..."
$DOCKER_COMPOSE exec rnd-app python -m alembic upgrade head 2>/dev/null || echo -e "${YELLOW}⚠ Migrations skipped or already applied${NC}"
echo -e "${GREEN}✓${NC} Migrations completed"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🚀 RND Monitoring Platform is now running!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${BLUE}Web Interface:${NC}      http://localhost:8000"
echo -e "  ${BLUE}API Documentation:${NC}  http://localhost:8000/docs"
echo -e "  ${BLUE}Flower (Celery):${NC}    http://localhost:5555"
echo -e "  ${BLUE}VictoriaMetrics:${NC}    http://localhost:8428"
echo ""
echo -e "  ${BLUE}Default Login:${NC}"
echo -e "    Username: ${GREEN}admin${NC}"
echo -e "    Password: ${GREEN}(check .env: DEFAULT_ADMIN_PASSWORD)${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Log in to the web interface"
echo "  2. Configure Zabbix integration (Settings → Integrations)"
echo "  3. Add devices to monitor"
echo "  4. Review DEPLOYMENT.md for advanced configuration"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs:       ${GREEN}$DOCKER_COMPOSE logs -f${NC}"
echo "  Stop services:   ${GREEN}$DOCKER_COMPOSE down${NC}"
echo "  Restart:         ${GREEN}$DOCKER_COMPOSE restart${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
