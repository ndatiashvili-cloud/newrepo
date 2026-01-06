# RND Monitoring Platform - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the RND (Research & Development) Network Monitoring Platform using Docker Compose.

## Prerequisites

- Docker Engine 24.0 or higher
- Docker Compose V2 (2.20.0+)
- Minimum 4GB RAM available
- Minimum 20GB disk space
- Linux host with kernel 3.10+ (for network diagnostics)

## Quick Start (5 Minutes)

### 1. Initial Setup

```bash
# Clone or extract the project
cd rnd-monitoring

# Copy environment template
cp .env.example .env

# Generate secure keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32)[:32])" >> .env
```

### 2. Configure Environment

Edit `.env` file and update these critical values:

```env
# Required: Change default passwords
DEFAULT_ADMIN_PASSWORD=YourSecurePassword123!
POSTGRES_PASSWORD=YourPostgresPassword123!
REDIS_PASSWORD=YourRedisPassword123!

# Required: Update database URL with your postgres password
DATABASE_URL=postgresql+psycopg2://rnd_user:YourPostgresPassword123!@postgres:5432/rnd_monitoring

# Required: Update Redis URL with your redis password
REDIS_URL=redis://:YourRedisPassword123!@redis:6379/0

# Optional: Add Zabbix if available
ZABBIX_URL=http://your-zabbix-server/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix
```

### 3. Launch Platform

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f rnd-app

# Wait for "Application startup complete" message
```

### 4. Access Platform

- **Web Interface**: http://localhost:8000
- **Default Login**: `admin` / password from `.env`
- **Flower UI** (Celery): http://localhost:5555
- **VictoriaMetrics**: http://localhost:8428

## Advanced Configuration

### Custom Ports

Edit `docker-compose.yml` to change default ports:

```yaml
services:
  rnd-app:
    ports:
      - "8080:8000"  # Change 8080 to your desired port
```

### SSL/TLS Setup

For production, use a reverse proxy (nginx/traefik):

```bash
# Example nginx configuration
server {
    listen 443 ssl;
    server_name monitoring.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Resource Limits

Adjust resources in `docker-compose.yml`:

```yaml
services:
  rnd-app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Integration Setup

### Zabbix Integration

1. Ensure Zabbix is accessible from Docker network
2. Configure in `.env`:
```env
ZABBIX_URL=http://zabbix.local/api_jsonrpc.php
ZABBIX_USER=monitoring_user
ZABBIX_PASSWORD=secure_password
```

3. Test connection: Settings → Integrations → Zabbix

### External PostgreSQL Monitoring

Configure external database in Settings → Integrations → PostgreSQL:
- Host: external-db.local
- Port: 5432
- Database: production_db
- User: readonly_user
- Password: secure_password

### Elasticsearch Integration

Configure in Settings → Integrations → Elasticsearch:
- URL: http://elasticsearch:9200
- Username: elastic
- Password: changeme

## Maintenance

### Backup Database

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U rnd_user rnd_monitoring > backup_$(date +%Y%m%d).sql

# Backup with compression
docker-compose exec postgres pg_dump -U rnd_user rnd_monitoring | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database

```bash
# Restore from backup
cat backup_20250106.sql | docker-compose exec -T postgres psql -U rnd_user rnd_monitoring
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run migrations if needed
docker-compose exec rnd-app python -m alembic upgrade head
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rnd-app

# Last 100 lines
docker-compose logs --tail=100 rnd-app
```

### Service Management

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ DATA LOSS)
docker-compose down -v

# Restart specific service
docker-compose restart rnd-app

# Scale celery workers
docker-compose up -d --scale rnd-celery=3
```

## Monitoring & Health Checks

### Health Check Endpoints

- **API Health**: http://localhost:8000/health
- **Database**: http://localhost:8000/health/db
- **Redis**: http://localhost:8000/health/redis

### Performance Monitoring

1. Access Flower: http://localhost:5555
2. Monitor task queue, worker status, and performance
3. Check VictoriaMetrics: http://localhost:8428

### Logs Location

```bash
# Container logs
docker-compose logs rnd-app

# Application logs (inside container)
docker-compose exec rnd-app cat /app/logs/rnd.log
```

## Troubleshooting

### Application won't start

```bash
# Check logs
docker-compose logs rnd-app

# Common fixes:
# 1. Verify .env configuration
# 2. Check port conflicts: netstat -tuln | grep 8000
# 3. Ensure Docker has enough resources
# 4. Rebuild: docker-compose build --no-cache
```

### Database connection errors

```bash
# Check PostgreSQL
docker-compose logs postgres

# Test connection
docker-compose exec rnd-app python -c "from database import get_db; print('OK')"

# Verify credentials in .env
```

### Celery tasks not running

```bash
# Check Celery worker
docker-compose logs rnd-celery

# Check Redis
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart rnd-celery
```

### Network diagnostics not working

Ensure Docker has NET_ADMIN capability:

```yaml
cap_add:
  - NET_ADMIN
  - NET_RAW
```

## Security Best Practices

1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY** (32+ characters)
3. **Enable HTTPS** with reverse proxy
4. **Restrict CORS** origins in production
5. **Regular backups** (daily recommended)
6. **Monitor logs** for suspicious activity
7. **Update dependencies** regularly
8. **Use firewall** to restrict access

## Production Checklist

- [ ] Changed all default passwords
- [ ] Generated secure SECRET_KEY and ENCRYPTION_KEY
- [ ] Configured SSL/TLS
- [ ] Set up regular backups
- [ ] Configured log rotation
- [ ] Set resource limits
- [ ] Tested disaster recovery
- [ ] Documented custom configurations
- [ ] Set up monitoring alerts
- [ ] Reviewed security settings

## Support

For issues and questions:
- Check TROUBLESHOOTING.md
- Review logs: `docker-compose logs`
- Verify configuration: `docker-compose config`
- Contact: RND Team

---

**RND Monitoring Platform** - Research & Development Team
Version 2.0.0 | January 2026
