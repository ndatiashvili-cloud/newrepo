# RND Network Monitoring Platform

**Research & Development Team - Enterprise Network Monitoring System**

Modern, fast, and secure network monitoring platform powered by FastAPI, Zabbix, PostgreSQL, and React.

![RND Logo](frontend/public/logo-rnd.png)

---

## Features

- **Real-time Monitoring**: Live device status tracking via Zabbix integration
- **Network Topology**: Visual network mapping with traffic flow visualization
- **Diagnostics Tools**: Ping, Traceroute, DNS lookup, Port scanning
- **Multi-Database Support**: PostgreSQL and Elasticsearch integrations
- **User Management**: Role-based access control (Admin, Manager, Technician, Viewer)
- **Responsive UI**: Modern React interface with dark mode support
- **API First**: Comprehensive REST API with OpenAPI documentation

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd rnd-monitoring
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
nano .env
```

3. **Generate security keys**
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (must be 32 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

4. **Start the application**
```bash
docker-compose up -d
```

5. **Access the application**
- Web UI: http://localhost:5001
- API Docs: http://localhost:5001/docs
- Default credentials: admin / admin123

---

## Configuration

### Required Environment Variables

```env
# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql+psycopg2://rnd_user:password@postgres:5432/rnd_monitoring

# Redis
REDIS_PASSWORD=your_redis_password
REDIS_URL=redis://:password@redis:6379/0

# Security
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_32_char_encryption_key

# Zabbix Integration
ZABBIX_URL=http://your-zabbix-server/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix
```

### Optional Integrations

**Elasticsearch**
```env
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=changeme
```

**External PostgreSQL**
```env
EXTERNAL_POSTGRES_HOST=localhost
EXTERNAL_POSTGRES_PORT=5432
EXTERNAL_POSTGRES_DB=your_database
EXTERNAL_POSTGRES_USER=your_user
EXTERNAL_POSTGRES_PASSWORD=your_password
```

---

## Usage Guide

### 1. Login
Access http://localhost:5001 and login with default credentials (admin/admin123).

### 2. Configure Zabbix Integration
1. Navigate to Settings > Integrations
2. Enter your Zabbix server details
3. Click "Test Connection"
4. Click "Save" if connection is successful

### 3. Import Devices from Zabbix
1. Go to Devices page
2. Click "Import from Zabbix"
3. Select host groups to import
4. Devices will appear in the list

### 4. View Network Topology
1. Navigate to Topology page
2. View auto-discovered network connections
3. See real-time traffic flow on links
4. Filter by region or device type

### 5. Run Diagnostics
1. Go to Diagnostics page
2. Enter target IP address
3. Run Ping, Traceroute, or DNS lookup
4. View results and history

### 6. Connect External Databases
1. Go to Settings > Integrations
2. Configure PostgreSQL or Elasticsearch connection
3. View health metrics and statistics

### 7. Manage Users
1. Navigate to Settings > Users (Admin only)
2. Create new users with appropriate roles
3. Assign permissions based on role

---

## Architecture

```
┌─────────────────┐
│   React UI      │
│   (Frontend)    │
└────────┬────────┘
         │
         │ HTTPS/WSS
         │
┌────────▼────────┐      ┌──────────────┐
│   FastAPI       │─────▶│   Zabbix     │
│   (Backend)     │      │   Server     │
└────────┬────────┘      └──────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐  ┌────────────┐
│Postgres│  │Redis │  │VictoriaM│
└────────┘  └──────┘  └────────────┘
```

---

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:5001/docs
- ReDoc: http://localhost:5001/redoc

### Key Endpoints

**Authentication**
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

**Devices**
- `GET /api/v1/devices` - List all devices
- `GET /api/v1/devices/{id}` - Get device details

**Diagnostics**
- `POST /api/v1/diagnostics/ping` - Run ping test
- `POST /api/v1/diagnostics/traceroute` - Run traceroute

**Topology**
- `GET /api/v1/infrastructure/topology` - Get network topology

---

## Development

### Local Development Setup

1. **Install Python dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Install frontend dependencies**
```bash
cd frontend
npm install
```

3. **Run backend**
```bash
python main.py
```

4. **Run frontend**
```bash
cd frontend
npm run dev
```

### Running Tests
```bash
pytest
```

---

## Troubleshooting

### Ping/Traceroute not working in Docker

Add NET_RAW capability to the API container:
```yaml
api:
  cap_add:
    - NET_RAW
```

### Zabbix connection fails

- Verify Zabbix URL is correct and accessible
- Check firewall rules
- Ensure Zabbix user has API access permissions

### Database connection errors

- Check PostgreSQL is running: `docker-compose ps`
- Verify DATABASE_URL is correct
- Check PostgreSQL logs: `docker-compose logs postgres`

### WebSocket disconnections

- Check Redis is running
- Verify REDIS_URL configuration
- Review Celery worker logs

---

## Security

- All passwords are hashed with Argon2
- API tokens use JWT with expiration
- Sensitive data encrypted at rest
- Security headers enabled
- Rate limiting supported
- CORS configurable

---

## License

Proprietary - © 2025 RND Research & Development Team

---

## Support

For issues and questions:
- Email: info@rnd.dev
- Documentation: See docs/ directory

---

## Contributors

Developed by the RND Research & Development Team
