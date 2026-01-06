"""
RND FLUX - Metrics Router
Handles metrics retrieval from PostgreSQL and Zabbix
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from database import get_db, User
from auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


class MetricQuery(BaseModel):
    metric_name: str
    device_id: Optional[str] = None
    device_ip: Optional[str] = None
    time_from: Optional[int] = None
    time_to: Optional[int] = None
    labels: Optional[Dict[str, str]] = None


@router.get("/postgres/{device_id}")
async def get_postgres_metrics(
    device_id: str,
    metric_name: Optional[str] = None,
    time_from: Optional[int] = Query(None, description="Unix timestamp"),
    time_to: Optional[int] = Query(None, description="Unix timestamp"),
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get metrics from PostgreSQL database
    Supports querying from monitoring tables
    """
    try:
        # Default to last 24 hours if not specified
        if not time_to:
            time_to = int(datetime.now().timestamp())
        if not time_from:
            time_from = int((datetime.now() - timedelta(hours=24)).timestamp())

        time_from_dt = datetime.fromtimestamp(time_from)
        time_to_dt = datetime.fromtimestamp(time_to)

        # Check if monitoring tables exist
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%metric%' OR table_name LIKE '%monitoring%'
        """))
        tables = [row[0] for row in result.fetchall()]

        if not tables:
            # Try to query from VictoriaMetrics-style tables or create a view
            # For now, return empty if no tables found
            return {
                "device_id": device_id,
                "metrics": [],
                "message": "No metrics tables found. Ensure monitoring is configured.",
            }

        # Query metrics from available tables
        # This is a generic query - adjust based on your actual schema
        query = text("""
            SELECT 
                metric_name,
                value,
                labels,
                timestamp
            FROM metrics
            WHERE device_id = :device_id
            AND timestamp BETWEEN :time_from AND :time_to
            ORDER BY timestamp ASC
            LIMIT :limit
        """)

        try:
            result = db.execute(
                query,
                {
                    "device_id": device_id,
                    "time_from": time_from_dt,
                    "time_to": time_to_dt,
                    "limit": limit,
                }
            )
            metrics = []
            for row in result.fetchall():
                metrics.append({
                    "metric_name": row[0],
                    "value": float(row[1]) if row[1] else 0,
                    "labels": row[2] if row[2] else {},
                    "timestamp": int(row[3].timestamp()) if isinstance(row[3], datetime) else row[3],
                })

            return {
                "device_id": device_id,
                "time_from": time_from,
                "time_to": time_to,
                "metrics": metrics,
                "count": len(metrics),
            }
        except Exception as e:
            logger.warning(f"Direct metrics table query failed: {e}")
            # Fallback: query from monitoring items if available
            return {
                "device_id": device_id,
                "metrics": [],
                "message": f"Metrics query failed: {str(e)}. Ensure metrics are being stored.",
            }

    except Exception as e:
        logger.error(f"Error fetching PostgreSQL metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/postgres/devices/{device_ip}")
async def get_metrics_by_ip(
    device_ip: str,
    metric_name: Optional[str] = None,
    time_from: Optional[int] = None,
    time_to: Optional[int] = None,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get metrics by device IP address
    """
    # Similar to above but query by IP
    if not time_to:
        time_to = int(datetime.now().timestamp())
    if not time_from:
        time_from = int((datetime.now() - timedelta(hours=24)).timestamp())

    return {
        "device_ip": device_ip,
        "time_from": time_from,
        "time_to": time_to,
        "metrics": [],
        "message": "Query by IP - implement based on your schema",
    }


@router.get("/postgres/list")
async def list_available_metrics(
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all available metric names in the database
    """
    try:
        # Query distinct metric names
        query = text("""
            SELECT DISTINCT metric_name 
            FROM metrics
            WHERE device_id = :device_id OR :device_id IS NULL
            ORDER BY metric_name
        """)
        
        result = db.execute(query, {"device_id": device_id})
        metric_names = [row[0] for row in result.fetchall()]
        
        return {
            "device_id": device_id,
            "metric_names": metric_names,
            "count": len(metric_names),
        }
    except Exception as e:
        logger.warning(f"Could not list metrics: {e}")
        return {
            "device_id": device_id,
            "metric_names": [],
            "message": f"Could not list metrics: {str(e)}",
        }
