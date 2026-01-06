# RND Platform - Quick Start Guide

Get up and running with RND Network Monitoring Platform in 10 steps!

---

## Prerequisites

Before you begin, ensure you have:
- Docker & Docker Compose installed
- At least 4GB RAM available
- Zabbix server accessible (optional but recommended)
- 10GB free disk space

---

## Step 1: Download and Extract

1. Extract the RND archive to your desired location:
```bash
unzip rnd-monitoring.zip
cd rnd-monitoring
```

2. Verify all files are present:
```bash
ls -la
# You should see: docker-compose.yml, Dockerfile, requirements.txt, frontend/, etc.
```

---

## Step 2: Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Generate secure keys:
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (must be exactly 32 characters)
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(24))"
```

3. Edit `.env` file with your favorite editor:
```bash
nano .env
# or
vim .env
```

4. Update these critical settings:
```env
# Use the keys generated above
SECRET_KEY=<your-generated-secret-key>
ENCRYPTION_KEY=<your-generated-encryption-key>

# Set strong passwords
POSTGRES_PASSWORD=StrongPassword123!
REDIS_PASSWORD=AnotherStrongPass456!
DEFAULT_ADMIN_PASSWORD=ChangeMe789!

# Configure Zabbix (if available)
ZABBIX_URL=http://your-zabbix-server/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=your-zabbix-password
```

---

## Step 3: Start Docker Containers

1. Build and start all services:
```bash
docker-compose up -d
```

2. Wait for services to be healthy (2-3 minutes):
```bash
docker-compose ps
```

You should see all services as "healthy" or "running":
```
NAME                STATUS
rnd-postgres        Up (healthy)
rnd-redis           Up (healthy)
rnd-victoriametrics Up
rnd-api             Up
rnd-celery-worker   Up
rnd-celery-beat     Up
```

---

## Step 4: Verify Installation

1. Check application health:
```bash
curl http://localhost:5001/health
```

Expected response:
```json
{"status": "healthy", "version": "2.0.0"}
```

2. Check Docker logs for errors:
```bash
docker-compose logs api | grep -i error
docker-compose logs postgres | grep -i error
```

If no errors appear, you're good to go!

---

## Step 5: Access the Web Interface

1. Open your browser and navigate to:
```
http://localhost:5001
```

2. You should see the RND login page with the new logo

3. Log in with default credentials:
   - Username: `admin`
   - Password: (the value you set in DEFAULT_ADMIN_PASSWORD)

---

## Step 6: Change Admin Password

**Important**: Change the default password immediately!

1. After logging in, click on your profile icon (top right)
2. Select "Settings" or "Profile"
3. Navigate to "Change Password"
4. Enter a strong new password
5. Save changes

---

## Step 7: Configure Zabbix Integration

1. Navigate to **Settings** → **Integrations**

2. Find the **Zabbix** integration section

3. Enter your Zabbix details:
   - Zabbix URL: `http://your-zabbix-server/api_jsonrpc.php`
   - Username: Your Zabbix username
   - Password: Your Zabbix password

4. Click **Test Connection**
   - If successful, you'll see: "✓ Connected to Zabbix v6.x"
   - If failed, check Zabbix URL and credentials

5. Click **Save Configuration**

---

## Step 8: Import Devices from Zabbix

1. Go to **Devices** page

2. Click **Import from Zabbix** button (top right)

3. Select which host groups to import:
   - Check the groups you want to monitor
   - Or select "All" for complete import

4. Click **Import Devices**

5. Wait for import to complete (may take 1-2 minutes for large installations)

6. Refresh the page - you should now see your devices!

---

## Step 9: Verify Diagnostics

Test that ping and traceroute work correctly:

1. Navigate to **Diagnostics** page

2. **Test Ping**:
   - Enter a device IP (e.g., `8.8.8.8`)
   - Click "Run Ping"
   - You should see results with packet loss and latency

3. **Test Traceroute**:
   - Enter the same IP
   - Select "Traceroute" tool
   - Click "Run Traceroute"
   - You should see hop-by-hop path

If tests fail, check the troubleshooting section below.

---

## Step 10: Explore the Dashboard

1. Navigate to **Dashboard** (home page)

2. You should see:
   - Total devices count
   - Online/Offline status
   - Active alerts (if Zabbix is connected)
   - Device type breakdown
   - Regional statistics

3. Click on different sections to explore:
   - **Devices** - View all monitored devices
   - **Topology** - Visual network map
   - **Alerts** - Current network alerts
   - **Reports** - Historical data and trends

Congratulations! Your RND platform is now fully operational.

---

## Troubleshooting

### Issue: Containers won't start

**Solution**:
```bash
# Check for port conflicts
sudo netstat -tlnp | grep -E '5001|5432|6379'

# If ports are in use, stop conflicting services or change ports in docker-compose.yml
```

### Issue: Cannot access web interface

**Solution**:
```bash
# Check if API container is running
docker-compose ps api

# Check API logs
docker-compose logs api

# Restart API container
docker-compose restart api
```

### Issue: Ping/Traceroute not working

**Solution**:
```bash
# Verify NET_RAW capability in docker-compose.yml
docker-compose exec api ping -c 2 8.8.8.8

# If it fails, add this to docker-compose.yml under 'api' service:
    cap_add:
      - NET_RAW
      - NET_ADMIN

# Then restart:
docker-compose restart api
```

### Issue: Database connection failed

**Solution**:
```bash
# Check PostgreSQL health
docker-compose exec postgres pg_isready -U rnd_user

# Check DATABASE_URL in .env matches your postgres settings

# Restart database
docker-compose restart postgres
docker-compose restart api
```

### Issue: Zabbix connection failed

**Solution**:
- Verify Zabbix URL is accessible: `curl http://your-zabbix-server/api_jsonrpc.php`
- Check Zabbix username and password
- Ensure Zabbix API is enabled in Zabbix configuration
- Check network connectivity from Docker container to Zabbix server

---

## Next Steps

Now that RND is running:

1. **Add More Users**
   - Go to Settings → Users
   - Create accounts for your team
   - Assign appropriate roles (Admin/Manager/Tech/Viewer)

2. **Configure Database Monitoring** (Optional)
   - Go to Settings → Integrations
   - Add PostgreSQL or Elasticsearch connections
   - Monitor your databases alongside network devices

3. **Set Up Topology**
   - Go to Topology page
   - The system will auto-discover connections from interface descriptions
   - Manually add links between devices if needed

4. **Create Performance Baselines**
   - Go to Diagnostics
   - Run ping tests on critical devices
   - Use "Calculate Baseline" to establish normal performance
   - Enable anomaly detection

5. **Explore Reports**
   - Generate downtime reports
   - View MTTR (Mean Time To Repair) statistics
   - Export data for analysis

---

## Maintenance Commands

```bash
# View logs
docker-compose logs -f

# Restart all services
docker-compose restart

# Stop all services
docker-compose down

# Update to new version
git pull
docker-compose build
docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U rnd_user rnd_monitoring > backup_$(date +%Y%m%d).sql
```

---

## Getting Help

- **Documentation**: Check README.md and docs/ folder
- **Troubleshooting**: See TROUBLESHOOTING.md
- **API Docs**: http://localhost:5001/docs
- **Support**: info@rnd.dev

---

**Happy Monitoring! 🚀**

*RND Team - Research & Development*
