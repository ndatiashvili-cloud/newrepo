"""
RND - Database Integrations Router
Handles PostgreSQL and Elasticsearch monitoring and health checks
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

from database import User
from auth import get_current_active_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])


# ============================================
# Pydantic Models
# ============================================

class PostgresConfig(BaseModel):
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    ssl_mode: str = "prefer"


class ElasticsearchConfig(BaseModel):
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    verify_ssl: bool = True


# ============================================
# PostgreSQL Integration
# ============================================

@router.post("/postgres/test")
async def test_postgres_connection(
    config: PostgresConfig,
    current_user: User = Depends(require_admin)
):
    """Test PostgreSQL connection"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Create connection string
        conn_str = f"host={config.host} port={config.port} dbname={config.database} user={config.username} password={config.password} sslmode={config.ssl_mode}"
        
        # Test connection
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()['version']
        
        # Get database size
        cursor.execute(f"SELECT pg_database_size('{config.database}') as size")
        db_size = cursor.fetchone()['size']
        
        # Get active connections
        cursor.execute("SELECT count(*) as connections FROM pg_stat_activity WHERE state = 'active'")
        active_connections = cursor.fetchone()['connections']
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "version": version.split(',')[0],
            "database_size_mb": round(db_size / (1024 * 1024), 2),
            "active_connections": active_connections
        }
        
    except Exception as e:
        logger.error(f"PostgreSQL connection test failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")


@router.get("/postgres/health")
async def get_postgres_health(
    current_user: User = Depends(get_current_active_user)
):
    """Get PostgreSQL health metrics"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import os
        
        # Use external database URL from env or return empty if not configured
        external_db_url = os.getenv("EXTERNAL_POSTGRES_HOST")
        if not external_db_url:
            return {
                "configured": False,
                "message": "External PostgreSQL not configured"
            }
        
        conn_str = f"host={os.getenv('EXTERNAL_POSTGRES_HOST')} port={os.getenv('EXTERNAL_POSTGRES_PORT', 5432)} dbname={os.getenv('EXTERNAL_POSTGRES_DB')} user={os.getenv('EXTERNAL_POSTGRES_USER')} password={os.getenv('EXTERNAL_POSTGRES_PASSWORD')} sslmode=prefer"
        
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Database metrics
        metrics = {}
        
        # 1. Database size
        cursor.execute(f"SELECT pg_database_size('{os.getenv('EXTERNAL_POSTGRES_DB')}') as size")
        metrics['database_size_mb'] = round(cursor.fetchone()['size'] / (1024 * 1024), 2)
        
        # 2. Connection stats
        cursor.execute("""
            SELECT 
                count(*) as total,
                count(*) FILTER (WHERE state = 'active') as active,
                count(*) FILTER (WHERE state = 'idle') as idle
            FROM pg_stat_activity
            WHERE datname = %s
        """, (os.getenv('EXTERNAL_POSTGRES_DB'),))
        conn_stats = cursor.fetchone()
        metrics['connections'] = {
            'total': conn_stats['total'],
            'active': conn_stats['active'],
            'idle': conn_stats['idle']
        }
        
        # 3. Top tables by size
        cursor.execute("""
            SELECT 
                schemaname || '.' || tablename as table_name,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY size_bytes DESC
            LIMIT 10
        """)
        metrics['top_tables'] = cursor.fetchall()
        
        # 4. Slow queries (if pg_stat_statements is available)
        try:
            cursor.execute("""
                SELECT 
                    query,
                    calls,
                    total_exec_time,
                    mean_exec_time,
                    max_exec_time
                FROM pg_stat_statements
                ORDER BY mean_exec_time DESC
                LIMIT 10
            """)
            metrics['slow_queries'] = cursor.fetchall()
        except:
            metrics['slow_queries'] = []
        
        # 5. Cache hit ratio
        cursor.execute("""
            SELECT 
                sum(heap_blks_read) as heap_read,
                sum(heap_blks_hit) as heap_hit,
                sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100 as cache_hit_ratio
            FROM pg_statio_user_tables
        """)
        cache_stats = cursor.fetchone()
        metrics['cache_hit_ratio'] = round(cache_stats['cache_hit_ratio'] or 0, 2)
        
        cursor.close()
        conn.close()
        
        return {
            "configured": True,
            "status": "healthy",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get PostgreSQL health: {str(e)}")
        return {
            "configured": True,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================
# Elasticsearch Integration
# ============================================

@router.post("/elasticsearch/test")
async def test_elasticsearch_connection(
    config: ElasticsearchConfig,
    current_user: User = Depends(require_admin)
):
    """Test Elasticsearch connection"""
    try:
        from elasticsearch import Elasticsearch
        
        # Create client
        es = Elasticsearch(
            [config.url],
            basic_auth=(config.username, config.password) if config.username else None,
            verify_certs=config.verify_ssl
        )
        
        # Test connection
        info = es.info()
        cluster_health = es.cluster.health()
        
        return {
            "success": True,
            "version": info['version']['number'],
            "cluster_name": info['cluster_name'],
            "cluster_status": cluster_health['status'],
            "nodes": cluster_health['number_of_nodes'],
            "active_shards": cluster_health['active_shards']
        }
        
    except Exception as e:
        logger.error(f"Elasticsearch connection test failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")


@router.get("/elasticsearch/health")
async def get_elasticsearch_health(
    current_user: User = Depends(get_current_active_user)
):
    """Get Elasticsearch cluster health and metrics"""
    try:
        from elasticsearch import Elasticsearch
        import os
        
        # Use external Elasticsearch URL from env
        es_url = os.getenv("ELASTICSEARCH_URL")
        if not es_url:
            return {
                "configured": False,
                "message": "Elasticsearch not configured"
            }
        
        es_user = os.getenv("ELASTICSEARCH_USER")
        es_password = os.getenv("ELASTICSEARCH_PASSWORD")
        
        # Create client
        es = Elasticsearch(
            [es_url],
            basic_auth=(es_user, es_password) if es_user else None,
            verify_certs=False
        )
        
        # Cluster health
        cluster_health = es.cluster.health()
        
        # Node stats
        nodes_stats = es.nodes.stats()
        
        # Index stats
        indices_stats = es.indices.stats()
        
        # Get top indices by size
        cat_indices = es.cat.indices(format='json', bytes='b')
        top_indices = sorted(cat_indices, key=lambda x: int(x.get('store.size', 0)), reverse=True)[:10]
        
        metrics = {
            "cluster": {
                "name": cluster_health['cluster_name'],
                "status": cluster_health['status'],
                "nodes": cluster_health['number_of_nodes'],
                "data_nodes": cluster_health['number_of_data_nodes'],
                "active_shards": cluster_health['active_shards'],
                "relocating_shards": cluster_health['relocating_shards'],
                "initializing_shards": cluster_health['initializing_shards'],
                "unassigned_shards": cluster_health['unassigned_shards'],
            },
            "indices": {
                "count": indices_stats['_all']['primaries']['indexing']['index_total'],
                "total_size_gb": round(indices_stats['_all']['total']['store']['size_in_bytes'] / (1024**3), 2),
                "documents": indices_stats['_all']['primaries']['docs']['count'],
            },
            "top_indices": [
                {
                    "index": idx['index'],
                    "docs": idx.get('docs.count', '0'),
                    "size_mb": round(int(idx.get('store.size', 0)) / (1024**2), 2),
                    "health": idx.get('health', 'unknown')
                }
                for idx in top_indices
            ]
        }
        
        return {
            "configured": True,
            "status": cluster_health['status'],
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get Elasticsearch health: {str(e)}")
        return {
            "configured": True,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================
# Configuration Management
# ============================================

@router.post("/postgres/configure")
async def configure_postgres(
    config: PostgresConfig,
    current_user: User = Depends(require_admin)
):
    """Save PostgreSQL configuration"""
    try:
        from dotenv import set_key
        import os
        
        env_file = ".env"
        set_key(env_file, "EXTERNAL_POSTGRES_HOST", config.host)
        set_key(env_file, "EXTERNAL_POSTGRES_PORT", str(config.port))
        set_key(env_file, "EXTERNAL_POSTGRES_DB", config.database)
        set_key(env_file, "EXTERNAL_POSTGRES_USER", config.username)
        set_key(env_file, "EXTERNAL_POSTGRES_PASSWORD", config.password)
        
        # Update environment variables
        os.environ["EXTERNAL_POSTGRES_HOST"] = config.host
        os.environ["EXTERNAL_POSTGRES_PORT"] = str(config.port)
        os.environ["EXTERNAL_POSTGRES_DB"] = config.database
        os.environ["EXTERNAL_POSTGRES_USER"] = config.username
        os.environ["EXTERNAL_POSTGRES_PASSWORD"] = config.password
        
        return {
            "success": True,
            "message": "PostgreSQL configuration saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to save PostgreSQL configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/elasticsearch/configure")
async def configure_elasticsearch(
    config: ElasticsearchConfig,
    current_user: User = Depends(require_admin)
):
    """Save Elasticsearch configuration"""
    try:
        from dotenv import set_key
        import os
        
        env_file = ".env"
        set_key(env_file, "ELASTICSEARCH_URL", config.url)
        if config.username:
            set_key(env_file, "ELASTICSEARCH_USER", config.username)
        if config.password:
            set_key(env_file, "ELASTICSEARCH_PASSWORD", config.password)
        
        # Update environment variables
        os.environ["ELASTICSEARCH_URL"] = config.url
        if config.username:
            os.environ["ELASTICSEARCH_USER"] = config.username
        if config.password:
            os.environ["ELASTICSEARCH_PASSWORD"] = config.password
        
        return {
            "success": True,
            "message": "Elasticsearch configuration saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to save Elasticsearch configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_integrations_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get status of all integrations"""
    import os
    
    return {
        "postgres": {
            "configured": bool(os.getenv("EXTERNAL_POSTGRES_HOST")),
            "host": os.getenv("EXTERNAL_POSTGRES_HOST", "Not configured")
        },
        "elasticsearch": {
            "configured": bool(os.getenv("ELASTICSEARCH_URL")),
            "url": os.getenv("ELASTICSEARCH_URL", "Not configured")
        },
        "zabbix": {
            "configured": bool(os.getenv("ZABBIX_URL")),
            "url": os.getenv("ZABBIX_URL", "Not configured")
        }
    }
