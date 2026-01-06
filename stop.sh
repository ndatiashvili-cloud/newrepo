#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# RND Monitoring Platform - Stop Script
# ═══════════════════════════════════════════════════════════════════

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════════"
echo "  RND - Stopping Monitoring Platform"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Use 'docker compose' or 'docker-compose'
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${BLUE}Stopping all services...${NC}"
$DOCKER_COMPOSE down

echo ""
echo -e "${GREEN}✓ All services stopped${NC}"
echo ""
echo -e "${YELLOW}Note: Data is preserved in Docker volumes${NC}"
echo -e "To remove all data, run: ${RED}$DOCKER_COMPOSE down -v${NC}"
echo ""
