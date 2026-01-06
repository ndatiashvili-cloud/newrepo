# RND Monitoring Platform - Installation Guide

## Overview
This guide will help you install and deploy the RND Monitoring Platform on your server.

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, or any Linux with Docker support
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB free space
- **Network**: 1 Gbps recommended

### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 100+ GB SSD
- **Network**: 10 Gbps

### Software Prerequisites
- Docker 20.10+ or later
- Docker Compose 2.0+ or later
- Git (for version control)

## Installation Steps

### Step 1: Install Docker

#### Ubuntu/Debian
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# Install required packages
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 2: Install Docker Compose

```bash
# Docker Compose is included with Docker Desktop and docker-compose-plugin
# Verify installation
docker compose version

# If not available, install standalone version
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 3: Download RND Monitoring Platform

Extract the ZIP file you downloaded from v0:

```bash
# Create installation directory
mkdir -p /opt/rnd-monitoring
cd /opt/rnd-monitoring

# Extract ZIP file
unzip rndmonitoringmain.zip
cd rndmonitoringmain
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration (use nano, vim, or any text editor)
nano .env
```

**Required Configuration:**
```env
# Application Settings
SECRET_KEY=<generate-secure-random-string-here>
ADMIN_PASSWORD=<your-secure-admin-password>

# Database Settings
DATABASE_PASSWORD=<secure-postgres-password>

# Redis Settings
REDIS_PASSWORD=<secure-redis-password>

# Optional: Email Settings (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Zabbix Integration
ZABBIX_URL=http://your-zabbix-server/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix
```

**Generate Secure Keys:**
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Generate passwords
openssl rand -base64 32
```

### Step 5: Deploy Application

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The deployment script will:
1. Check prerequisites
2. Create necessary directories
3. Pull Docker images
4. Build the application
5. Start all services
6. Verify health of services

### Step 6: Verify Installation

```bash
# Check running containers
docker-compose ps

# Check logs
docker-compose logs -f app

# Test web interface
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"healthy","version":"2.0.0"}
```

### Step 7: Access the Platform

Open your web browser and navigate to:
- **Web Interface**: http://your-server-ip:8000
- **API Documentation**: http://your-server-ip:8000/docs
- **Flower (Celery Monitor)**: http://your-server-ip:8000/flower

**Default Login:**
- Username: `admin`
- Password: (the ADMIN_PASSWORD you set in .env)

## Post-Installation Steps

### 1. Change Default Password
Immediately change the admin password after first login.

### 2. Configure Firewall

```bash
# Allow HTTP/HTTPS
sudo ufw allow 8000/tcp
sudo ufw allow 443/tcp

# If using Flower on separate port
sudo ufw allow 5555/tcp

# Enable firewall
sudo ufw enable
```

### 3. Set Up SSL/TLS (Recommended)

For production, use a reverse proxy like Nginx with Let's Encrypt:

```bash
# Install Nginx
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Configure Nginx (example)
cat > /etc/nginx/sites-available/rnd-monitoring << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/rnd-monitoring /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Configure Monitoring Targets

After logging in:
1. Go to **Settings** → **Monitoring Configuration**
2. Add your network devices
3. Configure SNMP credentials
4. Set up monitoring thresholds
5. Configure alert notifications

### 5. Set Up Backups

```bash
# Create backup script
cat > /opt/rnd-monitoring/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/rnd-monitoring"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker exec rnd-postgres pg_dump -U rnduser rnd_monitoring > $BACKUP_DIR/db_$DATE.sql

# Backup configuration
cp /opt/rnd-monitoring/.env $BACKUP_DIR/env_$DATE.backup

# Compress
tar -czf $BACKUP_DIR/rnd_backup_$DATE.tar.gz $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/env_$DATE.backup

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "rnd_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/rnd_backup_$DATE.tar.gz"
EOF

chmod +x /opt/rnd-monitoring/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/rnd-monitoring/backup.sh") | crontab -
```

## Maintenance Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Start services
docker-compose up -d

# Update application
git pull
docker-compose build
docker-compose up -d

# Database backup
docker exec rnd-postgres pg_dump -U rnduser rnd_monitoring > backup.sql

# Database restore
docker exec -i rnd-postgres psql -U rnduser rnd_monitoring < backup.sql
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Support

For issues or questions:
- Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
- Review logs: `docker-compose logs`
- Contact: Research & Development Team

## License

Copyright (c) 2025 Research & Development Team. All rights reserved.
