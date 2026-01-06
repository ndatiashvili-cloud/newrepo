# RND Platform - Verification Checklist

Use this checklist to verify that all features are working correctly after deployment.

---

## Pre-Deployment Checks

- [ ] All required files present in archive
- [ ] `.env` file created from `.env.example`
- [ ] All secrets and passwords configured
- [ ] SECRET_KEY and ENCRYPTION_KEY generated
- [ ] Strong passwords set (not defaults)

---

## Installation Verification

### Docker Services

- [ ] All containers started: `docker-compose ps`
- [ ] PostgreSQL healthy
- [ ] Redis healthy
- [ ] VictoriaMetrics running
- [ ] API container running
- [ ] Celery worker running
- [ ] Celery beat running

**Command to verify**:
```bash
docker-compose ps
# All services should show "Up" or "healthy"
```

---

## Application Checks

### 1. Web Interface Access

- [ ] Can access http://localhost:5001
- [ ] Login page displays correctly
- [ ] RND logo visible (not old WARD FLUX logo)
- [ ] Favicon shows correctly
- [ ] No console errors in browser (F12)

**How to verify**:
- Open http://localhost:5001 in browser
- Check browser console for errors
- Verify branding is "RND" not "WARD FLUX"

---

### 2. Authentication

- [ ] Can log in with admin credentials
- [ ] Dashboard loads after login
- [ ] Can access user profile
- [ ] Can change password
- [ ] Logout works correctly
- [ ] Cannot access protected routes without login

**How to verify**:
```bash
# Test login API
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YOUR_PASSWORD"

# Should return JWT token
```

---

### 3. Database Connectivity

- [ ] PostgreSQL connection works
- [ ] Can create/read/update/delete records
- [ ] Database migrations applied
- [ ] Tables created correctly

**How to verify**:
```bash
# Connect to database
docker-compose exec postgres psql -U rnd_user -d rnd_monitoring

# List tables
\dt

# Check users table
SELECT username, role FROM users;
```

---

### 4. Zabbix Integration

- [ ] Can configure Zabbix connection in Settings
- [ ] "Test Connection" succeeds
- [ ] Can import devices from Zabbix
- [ ] Devices appear in Devices list
- [ ] Device status updates from Zabbix
- [ ] Alerts display from Zabbix

**How to verify**:
1. Go to Settings → Integrations
2. Enter Zabbix credentials
3. Click "Test Connection"
4. Should show: "✓ Connected to Zabbix v6.x"
5. Go to Devices → Import from Zabbix
6. Devices should appear in list

---

### 5. Network Diagnostics

#### Ping Test

- [ ] Ping page accessible
- [ ] Can enter IP address
- [ ] Ping executes successfully
- [ ] Results show packet loss percentage
- [ ] Results show min/avg/max latency
- [ ] Results stored in database
- [ ] History displays correctly

**How to verify**:
```bash
# Test ping from container
docker-compose exec api ping -c 3 8.8.8.8

# Test ping via API
curl -X POST "http://localhost:5001/api/v1/diagnostics/ping?ip=8.8.8.8&count=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Traceroute Test

- [ ] Traceroute executes successfully
- [ ] Results show hop-by-hop path
- [ ] Latency displayed for each hop
- [ ] Results stored in database
- [ ] History displays correctly

**How to verify**:
```bash
# Test traceroute from container
docker-compose exec api traceroute -m 15 8.8.8.8

# Test traceroute via API
curl -X POST "http://localhost:5001/api/v1/diagnostics/traceroute?ip=8.8.8.8" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### DNS Lookup

- [ ] DNS lookup works for hostnames
- [ ] Reverse DNS works for IPs
- [ ] Results show all A records
- [ ] Error handling works for invalid inputs

**How to verify**:
```bash
# Test DNS via API
curl -X POST "http://localhost:5001/api/v1/diagnostics/dns/lookup?hostname=google.com" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Port Scan

- [ ] Port scan executes successfully
- [ ] Shows open/closed status
- [ ] Multiple ports can be scanned
- [ ] Results display correctly

**How to verify**:
```bash
# Test port scan via API
curl -X POST "http://localhost:5001/api/v1/diagnostics/portscan?ip=8.8.8.8&ports=80,443" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 6. Network Topology

- [ ] Topology page accessible
- [ ] Network map displays
- [ ] Devices shown as nodes
- [ ] Links between devices visible
- [ ] Traffic information on links
- [ ] Can zoom and pan map
- [ ] Can filter by region/type
- [ ] Legend shows device types

**How to verify**:
1. Navigate to Topology page
2. Verify nodes appear
3. Check that connections show bandwidth
4. Test zoom and pan functionality

---

### 7. Database Integrations

#### PostgreSQL Integration

- [ ] Can add PostgreSQL connection
- [ ] Test connection succeeds
- [ ] Health metrics display:
  - [ ] Active connections
  - [ ] Database size
  - [ ] Cache hit ratio
- [ ] Charts display correctly

#### Elasticsearch Integration

- [ ] Can add Elasticsearch connection
- [ ] Test connection succeeds
- [ ] Health metrics display:
  - [ ] Cluster health (green/yellow/red)
  - [ ] Node count
  - [ ] Index statistics
- [ ] Charts display correctly

**How to verify**:
1. Go to Settings → Integrations
2. Add database connection
3. Click "Test Connection"
4. Go to Dashboard
5. Verify database health widgets appear

---

### 8. Dashboard and Reports

- [ ] Dashboard shows correct device counts
- [ ] Online/offline status accurate
- [ ] Alert counters display
- [ ] Charts and graphs render
- [ ] Real-time updates work
- [ ] Region statistics correct
- [ ] Device type breakdown correct

**How to verify**:
```bash
# Test dashboard API
curl http://localhost:5001/api/v1/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 9. User Management

- [ ] Can create new users
- [ ] Can assign roles (Admin/Manager/Tech/Viewer)
- [ ] Can edit user details
- [ ] Can deactivate users
- [ ] Role permissions enforced:
  - [ ] Admin: Full access
  - [ ] Manager: Cannot access system settings
  - [ ] Tech: Cannot manage users
  - [ ] Viewer: Read-only access

**How to verify**:
1. Go to Settings → Users
2. Create test user with each role
3. Log in as each user
4. Verify permissions

---

### 10. Performance and Reliability

- [ ] Page load times < 3 seconds
- [ ] API response times < 500ms
- [ ] No memory leaks (check after 1 hour)
- [ ] Celery workers processing tasks
- [ ] Redis caching working
- [ ] Database queries optimized
- [ ] No 500 errors in logs

**How to verify**:
```bash
# Check performance
docker stats

# Check API response time
time curl http://localhost:5001/health

# Check for errors
docker-compose logs api | grep -i error
docker-compose logs celery-worker | grep -i error

# Check Celery tasks
docker-compose exec celery-worker celery -A celery_app inspect active
```

---

## Security Checks

- [ ] Default admin password changed
- [ ] Strong passwords enforced
- [ ] HTTPS enabled (production)
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Security headers present
- [ ] SQL injection protection tested
- [ ] XSS protection verified
- [ ] No secrets in logs
- [ ] Firewall configured

**How to verify**:
```bash
# Check security headers
curl -I http://localhost:5001/

# Should see:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
```

---

## Documentation Checks

- [ ] README.md complete and accurate
- [ ] CHANGELOG.md updated
- [ ] QUICKSTART.md clear and tested
- [ ] TROUBLESHOOTING.md helpful
- [ ] .env.example has all variables
- [ ] API documentation accessible at /docs
- [ ] Comments in code are helpful

**How to verify**:
- Open http://localhost:5001/docs
- Verify all endpoints documented
- Test example API calls

---

## Final Sign-Off

### Functionality

- [  ] All core features working
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] UI/UX polished

### Branding

- [ ] No "WARD FLUX" references remain
- [ ] All logos updated to RND
- [ ] Favicon correct
- [ ] Browser title correct

### Documentation

- [ ] All docs complete
- [ ] Instructions clear
- [ ] Examples work

### Security

- [ ] No default passwords in production
- [ ] Secrets secured
- [ ] HTTPS enabled (production)
- [ ] Backups configured

---

## Verification Report Template

```
RND Platform Verification Report
Date: [DATE]
Verified by: [NAME]
Version: 2.0.0

SUMMARY:
- Installation: [PASS/FAIL]
- Authentication: [PASS/FAIL]
- Database: [PASS/FAIL]
- Zabbix Integration: [PASS/FAIL]
- Diagnostics: [PASS/FAIL]
- Topology: [PASS/FAIL]
- Performance: [PASS/FAIL]
- Security: [PASS/FAIL]

ISSUES FOUND:
1. [Issue description]
   - Severity: [Critical/High/Medium/Low]
   - Status: [Open/Fixed]
   
NOTES:
[Any additional notes]

SIGN-OFF:
[x] Ready for production deployment
[ ] Requires fixes before deployment

Signature: _______________
Date: _______________
```

---

## Commands for Full Verification

```bash
#!/bin/bash
# Quick verification script

echo "=== RND Platform Verification ==="

echo "1. Checking Docker services..."
docker-compose ps

echo "2. Checking application health..."
curl -f http://localhost:5001/health || echo "FAIL: Health check"

echo "3. Checking database..."
docker-compose exec postgres pg_isready -U rnd_user || echo "FAIL: Database"

echo "4. Checking Redis..."
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping || echo "FAIL: Redis"

echo "5. Checking logs for errors..."
docker-compose logs api | grep -i "error" | tail -10

echo "6. Checking diagnostics..."
docker-compose exec api ping -c 2 8.8.8.8 || echo "FAIL: Ping"
docker-compose exec api traceroute -m 5 8.8.8.8 || echo "FAIL: Traceroute"

echo "=== Verification Complete ==="
```

Save as `verify.sh`, make executable (`chmod +x verify.sh`), and run (`./verify.sh`)

---

**Verification completed successfully? You're ready to go! 🚀**

*RND Team - Research & Development*
