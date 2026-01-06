# Changelog

## Version 2.0.0 - RND Rebranding (2025-01-05)

### Major Changes
- **Complete Rebranding**: Application rebranded from "WARD FLUX/WardOps" to "RND" (Research & Development)
- **New Logo**: Updated logo and visual identity throughout the application
- **UI Redesign**: Modern minimalist functional interface with improved UX

### New Features

#### Zabbix Integration Enhancements
- Full Zabbix API integration with connection testing
- Device import from Zabbix with hosts, groups, and templates
- Network topology visualization with traffic flow
- Real-time metrics display from Zabbix items
- Automated device discovery and monitoring

#### Database Integrations
- PostgreSQL connector with health monitoring
  - Connection status and active connections
  - Database size and table statistics
  - Query performance metrics
- Elasticsearch connector with cluster health
  - Index and shard monitoring
  - Search performance metrics
  - Cluster status visualization

#### Diagnostic Improvements
- Fixed ping functionality with proper permissions
- Fixed traceroute with hop-by-hop latency
- Enhanced DNS lookup and reverse DNS
- Port scanning capabilities
- Network baseline calculation
- Anomaly detection

### UI/UX Improvements
- Redesigned login page with new branding
- Modern sidebar navigation with improved icons
- Responsive dashboard with real-time updates
- Dark mode support throughout the application
- Enhanced device details modal
- Improved topology map with better visualization

### Backend Improvements
- Updated FastAPI to latest version
- Improved error handling and logging
- Enhanced security headers
- Better WebSocket connection management
- Optimized database queries
- Added rate limiting support

### Bug Fixes
- Fixed ping/traceroute execution in Docker containers
- Resolved authentication token issues
- Fixed WebSocket connection drops
- Corrected topology edge calculations
- Fixed device status updates
- Resolved CORS configuration issues

### Documentation
- Updated README with new setup instructions
- Added comprehensive API documentation
- Created troubleshooting guide
- Updated Docker deployment guide
- Added integration setup guides

### Technical Changes
- Updated all branding references from "WARD FLUX" to "RND"
- Changed database names and user accounts
- Updated Docker container names
- Renamed Celery application
- Updated API metadata and contact information

### Dependencies
- Added elasticsearch client for Elasticsearch integration
- Updated all dependencies to latest stable versions
- Added support for external database connections

---

## Version 1.0.0 - Initial Release
- Initial WARD FLUX release with basic monitoring features
