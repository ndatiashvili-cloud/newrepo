# RND Platform - Troubleshooting Guide

Comprehensive troubleshooting guide for common issues.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Docker Issues](#docker-issues)
3. [Database Issues](#database-issues)
4. [Zabbix Integration Issues](#zabbix-integration-issues)
5. [Diagnostics Issues](#diagnostics-issues)
6. [Authentication Issues](#authentication-issues)
7. [Performance Issues](#performance-issues)
8. [Network Issues](#network-issues)

---

## Installation Issues

### Docker Compose not found

**Symptoms**: `docker-compose: command not found`

**Solution**:
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Port already in use

**Symptoms**: `Error: port 5001 is already allocated`

**Solution**:
```bash
# Find process using the port
sudo lsof -i :5001
# or
sudo netstat -tlnp | grep 5001

# Kill the process or change port in docker-compose.yml
# Edit docker-compose.yml and change:
    ports:
      - "5002:5001"  # Changed from 5001:5001
```

### Permission denied errors

**Symptoms**: `Permission denied` when running Docker commands

**Solution**:
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, then verify
docker ps
```

---

## Docker Issues

### Containers keep restarting

**Symptoms**: Container status shows "Restarting"

**Diagnosis**:
```bash
# Check container logs
docker-compose logs [service-name]

# Check container status
docker-compose ps

# Inspect container
docker inspect rnd-api
```

**Common Causes**:
1. **Database not ready**: Wait for postgres health check
2. **Environment variables missing**: Check .env file
3. **Port conflicts**: Change ports in docker-compose.yml

### Out of disk space

**Symptoms**: `no space left on device`

**Solution**:
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a
docker volume prune

# Remove old images
docker rmi $(docker images -f "dangling=true" -q)
```

### Container cannot connect to network

**Symptoms**: Services can't reach each other

**Solution**:
```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up -d

# Check network
docker network ls
docker network inspect rnd-network
```

---

## Database Issues

### PostgreSQL won't start

**Symptoms**: `postgres exited with code 1`

**Diagnosis**:
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Check if data directory is corrupted
docker-compose down
docker volume rm rnd-monitoring_postgres_data
docker-compose up -d
```

### Connection refused to database

**Symptoms**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U rnd_user -d rnd_monitoring

# Check DATABASE_URL in .env
echo $DATABASE_URL

# Restart services
docker-compose restart postgres
docker-compose restart api
```

### Database migrations failed

**Symptoms**: `alembic.util.exc.CommandError: Can't locate revision`

**Solution**:
```bash
# Reset migrations
docker-compose exec api alembic stamp head
docker-compose exec api alembic upgrade head

# Or completely reset database (WARNING: loses all data)
docker-compose down -v
docker-compose up -d
```

### Database is slow

**Symptoms**: Queries taking too long

**Solution**:
```bash
# Check active connections
docker-compose exec postgres psql -U rnd_user -d rnd_monitoring -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
docker-compose exec postgres psql -U rnd_user -d rnd_monitoring -c "SELECT pid, query, state FROM pg_stat_activity WHERE state != 'idle';"

# Vacuum database
docker-compose exec postgres psql -U rnd_user -d rnd_monitoring -c "VACUUM ANALYZE;"
```

---

## Zabbix Integration Issues

### Cannot connect to Zabbix

**Symptoms**: "Connection refused" or "Timeout" in Zabbix test

**Diagnosis**:
```bash
# Test from Docker container
docker-compose exec api curl -v http://your-zabbix-server/api_jsonrpc.php

# Test DNS resolution
docker-compose exec api nslookup your-zabbix-server

# Test from host
curl -X POST http://your-zabbix-server/api_jsonrpc.php \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":[],"id":1}'
```

**Solutions**:
1. **Check Zabbix URL**: Ensure it ends with `/api_jsonrpc.php`
2. **Firewall**: Allow Docker network to access Zabbix
3. **DNS**: Use IP address instead of hostname
4. **SSL**: If using HTTPS, ensure certificates are valid

### Authentication failed

**Symptoms**: "Login name or password is incorrect"

**Solution**:
```bash
# Verify credentials manually
curl -X POST http://your-zabbix-server/api_jsonrpc.php \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"user.login",
    "params":{"user":"Admin","password":"zabbix"},
    "id":1
  }'

# Check if API access is enabled for user in Zabbix UI
# User Settings → Frontend access → Enable
```

### Import from Zabbix fails

**Symptoms**: Import hangs or returns empty results

**Solution**:
```bash
# Check Zabbix API permissions
# Ensure user has read access to:
# - Hosts
# - Host groups
# - Templates
# - Items

# Check API logs
docker-compose logs api | grep -i zabbix

# Try manual API call
docker-compose exec api python3 -c "
from zabbix_client import ZabbixClient
z = ZabbixClient()
print(z.get_all_hosts())
"
```

### No metrics data from Zabbix

**Symptoms**: Devices imported but no performance metrics

**Solution**:
1. Check that items are configured in Zabbix
2. Verify item keys match what RND expects
3. Check VictoriaMetrics is running: `docker-compose ps victoriametrics`
4. Check Celery workers are processing: `docker-compose logs celery-worker`

---

## Diagnostics Issues

### Ping not working

**Symptoms**: "Ping command not available" or always timeout

**Solution**:
```bash
# Check if ping is installed in container
docker-compose exec api which ping
docker-compose exec api ping -c 2 8.8.8.8

# If not working, ensure Dockerfile has:
RUN apt-get update && apt-get install -y iputils-ping

# And docker-compose.yml has under 'api' service:
    cap_add:
      - NET_RAW

# Rebuild and restart
docker-compose build api
docker-compose restart api
```

### Traceroute not working

**Symptoms**: "Traceroute command not available"

**Solution**:
```bash
# Check if traceroute is installed
docker-compose exec api which traceroute

# If not, ensure Dockerfile has:
RUN apt-get update && apt-get install -y traceroute

# Rebuild
docker-compose build api
docker-compose restart api
```

### Ping works but results not parsing

**Symptoms**: Ping executes but shows parsing errors

**Solution**:
```bash
# Check system locale
docker-compose exec api locale

# Run ping manually to see output format
docker-compose exec api ping -c 5 8.8.8.8

# Update regex patterns in network_diagnostics.py if needed
```

### DNS lookup fails

**Symptoms**: Cannot resolve hostnames

**Solution**:
```bash
# Check DNS configuration in container
docker-compose exec api cat /etc/resolv.conf

# Test DNS manually
docker-compose exec api nslookup google.com

# Add DNS servers to docker-compose.yml:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

---

## Authentication Issues

### Cannot log in

**Symptoms**: "Invalid credentials" with correct password

**Solution**:
```bash
# Reset admin password
docker-compose exec api python3 -c "
from database import SessionLocal, User
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')
db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
admin.hashed_password = pwd_context.hash('newpassword123')
db.commit()
print('Password reset to: newpassword123')
"
```

### JWT token expired

**Symptoms**: Logged out unexpectedly

**Solution**:
- JWT tokens expire after 24 hours (default)
- Just log in again
- To change expiration, edit `auth.py`:
  ```python
  expires_delta = timedelta(days=7)  # Changed from 1 day
  ```

### Session not persisting

**Symptoms**: Logged out after page refresh

**Solution**:
```bash
# Check Redis is running
docker-compose ps redis

# Check Redis connection
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping

# Clear Redis cache
docker-compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHDB
```

---

## Performance Issues

### Slow page loads

**Symptoms**: Pages take 5+ seconds to load

**Diagnosis**:
```bash
# Check API response time
curl -w "@-" -o /dev/null -s http://localhost:5001/api/v1/health <<'EOF'
    time_total:  %{time_total}s\n
EOF

# Check database performance
docker-compose exec postgres psql -U rnd_user -d rnd_monitoring -c "
SELECT pid, query_start, state, query 
FROM pg_stat_activity 
WHERE state != 'idle' 
ORDER BY query_start;
"

# Check container resources
docker stats
```

**Solutions**:
1. **Increase resources**:
```yaml
# In docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

2. **Enable Redis caching**: Check REDIS_URL is set

3. **Optimize database**: Run VACUUM and ANALYZE

### High memory usage

**Symptoms**: System running out of memory

**Solution**:
```bash
# Check memory usage by container
docker stats --no-stream

# Limit container memory in docker-compose.yml:
    mem_limit: 1g
    memswap_limit: 1g

# Restart containers
docker-compose restart
```

### Celery workers not processing tasks

**Symptoms**: Background tasks queue up

**Diagnosis**:
```bash
# Check Celery worker status
docker-compose logs celery-worker

# Check Redis queue
docker-compose exec redis redis-cli -a $REDIS_PASSWORD LLEN celery

# Inspect Celery tasks
docker-compose exec celery-worker celery -A celery_app inspect active
```

**Solution**:
```bash
# Restart workers
docker-compose restart celery-worker celery-beat

# Increase worker concurrency in docker-compose.yml:
command: ["celery", "-A", "celery_app", "worker", "--concurrency=8"]
```

---

## Network Issues

### Frontend cannot reach backend

**Symptoms**: API calls fail with CORS errors

**Solution**:
```bash
# Check CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:5001,http://yourdomain.com

# Or allow all (development only):
CORS_ORIGINS=*

# Restart API
docker-compose restart api
```

### WebSocket connection fails

**Symptoms**: Real-time updates not working

**Diagnosis**:
```bash
# Check WebSocket in browser console
# Should see: WebSocket connection to 'ws://localhost:5001/ws/notifications' succeeded

# Check nginx/proxy configuration if behind reverse proxy
```

**Solution**:
```nginx
# Add to nginx config
location /ws/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Cannot access from other machines

**Symptoms**: Works on localhost but not from network

**Solution**:
```bash
# Check if binding to 0.0.0.0
# In docker-compose.yml:
    ports:
      - "0.0.0.0:5001:5001"

# Check firewall
sudo ufw allow 5001/tcp

# Test from another machine
curl http://your-server-ip:5001/health
```

---

## Logs and Debugging

### Enable debug logging

```bash
# Set LOG_LEVEL in .env
LOG_LEVEL=DEBUG

# Restart services
docker-compose restart
```

### View all logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api

# Save logs to file
docker-compose logs --no-color > logs.txt
```

### Check application health

```bash
# Health endpoint
curl http://localhost:5001/health

# API info
curl http://localhost:5001/openapi.json

# Database check
docker-compose exec api python -c "from database import test_connection; test_connection()"
```

---

## Getting More Help

If issues persist:

1. **Check logs** for detailed error messages
2. **Review documentation** in docs/ folder
3. **Search issues** on GitHub
4. **Contact support**: info@rnd.dev

Include in your support request:
- Error messages from logs
- Steps to reproduce
- System information (OS, Docker version)
- Configuration (sanitized .env)

---

**RND Team - Research & Development**
