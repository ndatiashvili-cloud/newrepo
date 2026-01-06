# Alternative Download Methods for RND Monitoring

## Problem: ZIP Download Not Working

If the v0 ZIP download link is not working, here are several alternative methods:

## Method 1: Use GitHub Integration (Recommended)

The easiest and most reliable way:

1. In v0 chat, look for "Settings" in the sidebar
2. Connect your GitHub account
3. Click "Sync to GitHub" or "Publish"
4. Create a new repository named "rnd-monitoring"
5. Clone locally:
```bash
git clone https://github.com/YOUR-USERNAME/rnd-monitoring.git
cd rnd-monitoring
chmod +x setup-rnd-monitoring.sh
./setup-rnd-monitoring.sh
```

## Method 2: Copy Files Manually from v0

If GitHub is not available, copy files one by one:

### Core Files (Must Have):
1. `docker-compose.yml` - Service configuration
2. `Dockerfile` - Container build
3. `requirements.txt` - Python dependencies
4. `main.py` - Main application
5. `.env.example` - Configuration template
6. `setup-rnd-monitoring.sh` - Setup script

### How to Copy:
1. Click the "Copy" button next to each code block in v0 chat
2. Create the file locally: `nano filename.py`
3. Paste the content
4. Save and exit (Ctrl+X, Y, Enter)

## Method 3: Use Browser Download Manager

Sometimes browser settings block downloads:

1. Try a different browser (Chrome, Firefox, Edge)
2. Disable popup blocker temporarily
3. Clear browser cache
4. Try incognito/private mode

## Method 4: Use curl/wget

If you have access to terminal:

```bash
# Try direct download with curl
curl -o rnd-monitoring.zip "https://v0.app/chat/api/download-zip?id=b_oZzHDl6RIdS&name=rndmonitoringmain"

# Or with wget
wget -O rnd-monitoring.zip "https://v0.app/chat/api/download-zip?id=b_oZzHDl6RIdS&name=rndmonitoringmain"

# Extract
unzip rnd-monitoring.zip
```

## Method 5: Minimal Setup (Quick Start)

If nothing else works, here's a minimal setup:

```bash
# Create project directory
mkdir rnd-monitoring && cd rnd-monitoring

# Create minimal docker-compose.yml
cat > docker-compose.yml << 'EOF'
# (Copy docker-compose.yml content from v0 chat)
EOF

# Create .env
cat > .env << 'EOF'
POSTGRES_PASSWORD=rnd_password
REDIS_PASSWORD=redis_password
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
DEFAULT_ADMIN_PASSWORD=admin123
USE_POSTGRES=true
DATABASE_URL=postgresql+psycopg2://rnd_user:rnd_password@postgres:5432/rnd_monitoring
REDIS_URL=redis://:redis_password@redis:6379/0
EOF

# Create Dockerfile
# (Copy Dockerfile content from v0 chat)

# Create requirements.txt
# (Copy requirements.txt content from v0 chat)

# Create main.py
# (Copy main.py content from v0 chat)
```

## Troubleshooting Download Issues

### Check Browser Console:
1. Press F12 to open Developer Tools
2. Go to Console tab
3. Try download again
4. Look for error messages

### Common Issues:

**403 Forbidden:**
- Session expired in v0
- Refresh the page and try again

**Network Error:**
- Check internet connection
- Try different network (mobile hotspot)

**Timeout:**
- File is too large
- Use GitHub method instead

**CORS Error:**
- Browser security blocking
- Use incognito mode or different browser

## Getting Help

If all methods fail:

1. Screenshot any error messages
2. Check browser console (F12)
3. Note which method you tried
4. Describe what happens when you click download

## Verify Downloaded Files

After downloading by any method, verify:

```bash
# Check main files exist
ls -la docker-compose.yml Dockerfile requirements.txt main.py

# Check directory structure
tree -L 2

# Verify file sizes (main.py should be ~50-100KB)
du -h main.py requirements.txt
```

## Next Steps

Once you have the files:

```bash
# Make setup script executable
chmod +x setup-rnd-monitoring.sh

# Run setup
./setup-rnd-monitoring.sh

# Wait 30-40 seconds for services to start

# Access application
open http://localhost:5001
```

Default login:
- Username: `admin`
- Password: `admin123`

---

Need more help? The complete project is version-controlled and all changes are tracked in CHANGELOG.md
