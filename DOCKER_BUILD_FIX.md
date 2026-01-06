# Docker Build Fix Guide

## Problem
Docker build fails with error:
```
npm error The `npm ci` command can only install with an existing package-lock.json
```

## Solution

### Option 1: Automated Fix (Recommended)
Run the automated fix script:

```bash
chmod +x fix-docker-build.sh
./fix-docker-build.sh
```

This will:
1. Stop existing containers
2. Remove old images
3. Generate package-lock.json
4. Rebuild containers
5. Start services

### Option 2: Manual Fix

#### Step 1: Generate package-lock.json
```bash
cd frontend
npm install --package-lock-only
cd ..
```

#### Step 2: Rebuild Docker
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Option 3: Use npm install instead of npm ci

Edit `Dockerfile` line 14:
```dockerfile
# Change from:
RUN npm ci

# To:
RUN npm install
```

Then rebuild:
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Verification

Check if services are running:
```bash
docker-compose ps
```

All services should show "Up" status.

Check logs:
```bash
docker-compose logs api
docker-compose logs celery-worker
```

Access the application:
- Web UI: http://localhost:8000
- API: http://localhost:5001

## Troubleshooting

### Build still fails
```bash
# Clean everything
docker-compose down -v
docker system prune -a
docker volume prune

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Permission errors
```bash
sudo chmod -R 755 frontend/
sudo chown -R $USER:$USER .
```

### Network conflicts
```bash
# Check if ports are in use
netstat -tulpn | grep -E '5001|8000|6379|5432'

# Kill processes using these ports
sudo kill -9 $(sudo lsof -t -i:5001)
sudo kill -9 $(sudo lsof -t -i:8000)
```

## Quick Commands

```bash
# View all logs
docker-compose logs -f

# Restart specific service
docker-compose restart api

# Rebuild single service
docker-compose up -d --build api

# Check container health
docker-compose ps
docker inspect <container_name> | grep Health
```

## Success Indicators

When successfully running:
```
✓ Redis running on port 6379
✓ PostgreSQL running on port 5432
✓ API running on port 5001
✓ Celery worker processing tasks
✓ Celery beat scheduling tasks
✓ Web UI accessible at http://localhost:8000
