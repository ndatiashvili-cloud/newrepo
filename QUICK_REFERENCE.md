# RND Monitoring Platform - Quick Reference

## Quick Start Commands

```bash
# Deploy application
./deploy.sh

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Start services
docker-compose up -d

# Restart specific service
docker-compose restart app
```

## Access URLs

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| Web Interface | http://localhost:8000 | admin / (from .env) |
| API Docs | http://localhost:8000/docs | - |
| Flower | http://localhost:5555 | - |
| PostgreSQL | localhost:5432 | rnduser / (from .env) |
| Redis | localhost:6379 | - / (from .env) |

## Important Files

| File | Purpose |
|------|---------|
| `.env` | Configuration settings |
| `docker-compose.yml` | Service orchestration |
| `requirements.txt` | Python dependencies |
| `main.py` | Application entry point |

## Common Tasks

### Add New Device
1. Login to web interface
2. Navigate to Devices → Add Device
3. Enter device details (IP, SNMP credentials)
4. Save and start monitoring

### View Device Status
1. Go to Dashboard
2. Select device from list
3. View real-time metrics and graphs

### Configure Alerts
1. Settings → Alerts
2. Add Alert Rule
3. Set thresholds and notification channels

### Run Diagnostics
1. Tools → Diagnostics
2. Enter target IP
3. Select tool (Ping, Traceroute, etc.)
4. Run test

## Service Management

```bash
# Check service status
docker-compose ps

# View resource usage
docker stats

# Enter app container
docker-compose exec app bash

# View database
docker-compose exec postgres psql -U rnduser -d rnd_monitoring

# Clear Redis cache
docker-compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHALL
```

## Backup & Restore

```bash
# Backup database
docker exec rnd-postgres pg_dump -U rnduser rnd_monitoring > backup_$(date +%Y%m%d).sql

# Restore database
docker exec -i rnd-postgres psql -U rnduser rnd_monitoring < backup.sql

# Backup config
cp .env .env.backup
```

## Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f celery_worker

# Last 100 lines
docker-compose logs --tail=100 app

# Save logs to file
docker-compose logs > logs_$(date +%Y%m%d).txt
```

## Performance Tuning

### Database Optimization
```sql
-- Connect to database
docker-compose exec postgres psql -U rnduser -d rnd_monitoring

-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Vacuum and analyze
VACUUM ANALYZE;
```

### Clear Old Metrics
```sql
-- Delete metrics older than 90 days
DELETE FROM device_metrics WHERE timestamp < NOW() - INTERVAL '90 days';
```

## Security Checklist

- [ ] Changed default admin password
- [ ] Updated SECRET_KEY in .env
- [ ] Set strong database passwords
- [ ] Configured firewall rules
- [ ] Enabled SSL/TLS
- [ ] Set up regular backups
- [ ] Reviewed user permissions
- [ ] Enabled audit logging

## Environment Variables Reference

### Core Settings
```env
SECRET_KEY=<random-string>          # Application secret key
DEBUG=false                         # Debug mode (false for production)
ADMIN_PASSWORD=<password>           # Default admin password
```

### Database
```env
DATABASE_URL=postgresql://...       # PostgreSQL connection
DATABASE_PASSWORD=<password>        # Database password
```

### Redis
```env
REDIS_URL=redis://...              # Redis connection
REDIS_PASSWORD=<password>          # Redis password
```

### Monitoring
```env
SNMP_COMMUNITY=public              # Default SNMP community
POLL_INTERVAL=300                  # Polling interval (seconds)
```

### Integrations
```env
ZABBIX_URL=http://...              # Zabbix API URL
ZABBIX_USER=Admin                  # Zabbix username
ZABBIX_PASSWORD=<password>         # Zabbix password
```

## API Quick Reference

### Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# Response: {"access_token":"...","token_type":"bearer"}
```

### Devices
```bash
# List devices
curl -X GET http://localhost:8000/api/devices \
  -H "Authorization: Bearer <token>"

# Add device
curl -X POST http://localhost:8000/api/devices \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Router1","ip_address":"192.168.1.1","snmp_community":"public"}'
```

### Metrics
```bash
# Get device metrics
curl -X GET http://localhost:8000/api/devices/1/metrics \
  -H "Authorization: Bearer <token>"
```

## Troubleshooting Quick Fixes

### Services won't start
```bash
docker-compose down
docker-compose up -d --force-recreate
```

### Database connection error
```bash
docker-compose restart postgres
docker-compose logs postgres
```

### Out of disk space
```bash
# Clean Docker images
docker system prune -a

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

### High memory usage
```bash
# Restart memory-intensive services
docker-compose restart celery_worker
docker-compose restart redis
```

## Support

- Documentation: See README.md, DEPLOYMENT.md, TROUBLESHOOTING.md
- Logs: `docker-compose logs`
- Health check: http://localhost:8000/health
