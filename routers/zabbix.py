"""
WARD Tech Solutions - Zabbix Integration Router
Handles Zabbix host management, alerts, groups, templates, and search
"""
import logging
import asyncio
from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from auth import get_current_active_user
from database import User, UserRole
from routers.utils import get_monitored_groupids, run_in_executor

# Thread pool executor
import concurrent.futures

logger = logging.getLogger(__name__)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# Create router
router = APIRouter(prefix="/api/v1/zabbix", tags=["zabbix"])


# Pydantic models for request validation
class CreateHostRequest(BaseModel):
    hostname: str
    visible_name: str
    ip_address: str
    group_ids: List[str]
    template_ids: List[str]


class UpdateHostRequest(BaseModel):
    hostname: Optional[str] = None
    visible_name: Optional[str] = None
    ip_address: Optional[str] = None
    branch: Optional[str] = None


@router.get("/alerts")
async def get_alerts(request: Request):
    """Get all active alerts"""
    zabbix = request.app.state.zabbix
    alerts = await run_in_executor(zabbix.get_active_alerts)
    return alerts


@router.get("/mttr/stats")
async def get_mttr_stats(request: Request):
    """Get MTTR statistics"""
    zabbix = request.app.state.zabbix
    stats = await run_in_executor(zabbix.get_mttr_stats)
    return stats


@router.get("/groups")
async def get_groups(request: Request):
    """Get all host groups"""
    zabbix = request.app.state.zabbix
    groups = await run_in_executor(zabbix.get_all_groups)
    return groups


@router.get("/templates")
async def get_templates(request: Request):
    """Get all templates"""
    zabbix = request.app.state.zabbix
    templates = await run_in_executor(zabbix.get_all_templates)
    return templates


@router.post("/hosts")
async def create_host(request: Request, host_data: CreateHostRequest):
    """Create a new host in Zabbix"""
    zabbix = request.app.state.zabbix

    result = await run_in_executor(
        lambda: zabbix.create_host(
            hostname=host_data.hostname,
            visible_name=host_data.visible_name,
            ip_address=host_data.ip_address,
            group_ids=host_data.group_ids,
            template_ids=host_data.template_ids,
        )
    )

    if result.get("success"):
        return result
    return JSONResponse(status_code=500, content=result)


@router.put("/hosts/{hostid}")
async def update_host(request: Request, hostid: str, host_data: UpdateHostRequest):
    """Update host properties"""
    zabbix = request.app.state.zabbix

    update_data = host_data.dict(exclude_unset=True)
    if not update_data:
        return JSONResponse(status_code=400, content={"error": "No fields to update"})

    result = await run_in_executor(lambda: zabbix.update_host(hostid, **update_data))

    if result.get("success"):
        return result
    return JSONResponse(status_code=500, content=result)


@router.delete("/hosts/{hostid}")
async def delete_host(request: Request, hostid: str):
    """Delete a host"""
    zabbix = request.app.state.zabbix
    result = await run_in_executor(zabbix.delete_host, hostid)

    if result.get("success"):
        return result
    return JSONResponse(status_code=500, content=result)


@router.get("/search")
async def search_devices(
    request: Request,
    q: Optional[str] = None,
    region: Optional[str] = None,
    branch: Optional[str] = None,
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    """Advanced search endpoint with user permissions"""
    zabbix = request.app.state.zabbix
    groupids = get_monitored_groupids()
    loop = asyncio.get_event_loop()
    devices = await loop.run_in_executor(executor, lambda: zabbix.get_all_hosts(group_ids=groupids))

    # Apply user permission filtering first (non-admin users)
    if current_user.role != UserRole.ADMIN:
        # Filter by region if user has regional restriction
        if current_user.region:
            devices = [d for d in devices if d.get("region") == current_user.region]

        # Filter by branches if user has branch restrictions
        if current_user.branches:
            allowed_branches = [b.strip() for b in current_user.branches.split(",")]
            devices = [d for d in devices if d.get("branch") in allowed_branches]

    # Apply text search
    if q:
        query = q.lower()
        devices = [
            d
            for d in devices
            if (
                query in d["display_name"].lower()
                or query in d["branch"].lower()
                or query in d["ip"].lower()
                or query in d["region"].lower()
            )
        ]

    # Apply filters
    if region:
        devices = [d for d in devices if d["region"] == region]
    if branch:
        devices = [d for d in devices if branch.lower() in d["branch"].lower()]
    if device_type:
        devices = [d for d in devices if d["device_type"] == device_type]
    if status:
        devices = [d for d in devices if d["ping_status"] == status]

    return devices


@router.get("/metrics/{hostid}")
async def get_host_metrics(
    request: Request,
    hostid: str,
    time_from: Optional[int] = None,
    time_to: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all metrics for a Zabbix host (from Zabbix sender)
    Returns all items and their historical data
    """
    from datetime import datetime, timedelta
    
    zabbix = request.app.state.zabbix
    
    # Default to last 24 hours if not specified
    if not time_to:
        time_to = int(datetime.now().timestamp())
    if not time_from:
        time_from = int((datetime.now() - timedelta(hours=24)).timestamp())
    
    def fetch_metrics():
        try:
            # Get all items for this host
            items = zabbix.zapi.item.get(
                hostids=hostid,
                output=["itemid", "name", "key_", "units", "value_type", "status"],
                filter={"status": "0"},  # Only enabled items
            )
            
            metrics = []
            for item in items:
                itemid = item["itemid"]
                item_name = item["name"]
                item_key = item["key_"]
                units = item.get("units", "")
                value_type = int(item.get("value_type", 0))
                
                # Get historical data
                history_type = 0  # Numeric (float)
                if value_type == 1:  # Character
                    history_type = 1
                elif value_type == 2:  # Log
                    history_type = 2
                elif value_type == 3:  # Numeric (unsigned)
                    history_type = 0
                elif value_type == 4:  # Text
                    history_type = 1
                
                try:
                    history = zabbix.zapi.history.get(
                        itemids=[itemid],
                        time_from=time_from,
                        time_to=time_to,
                        history=history_type,
                        sortfield="clock",
                        sortorder="ASC",
                    )
                    
                    # Get last value
                    last_value = item.get("lastvalue", "0")
                    
                    metrics.append({
                        "itemid": itemid,
                        "name": item_name,
                        "key": item_key,
                        "units": units,
                        "value_type": value_type,
                        "last_value": last_value,
                        "history": [
                            {
                                "timestamp": int(h["clock"]),
                                "value": h["value"],
                            }
                            for h in history
                        ],
                    })
                except Exception as e:
                    logger.warning(f"Error fetching history for item {itemid}: {e}")
                    metrics.append({
                        "itemid": itemid,
                        "name": item_name,
                        "key": item_key,
                        "units": units,
                        "value_type": value_type,
                        "last_value": item.get("lastvalue", "0"),
                        "history": [],
                    })
            
            return {
                "hostid": hostid,
                "time_from": time_from,
                "time_to": time_to,
                "metrics": metrics,
                "total_items": len(metrics),
            }
        except Exception as e:
            logger.error(f"Error fetching metrics for host {hostid}: {e}")
            raise
    
    return await run_in_executor(fetch_metrics)


@router.get("/metrics/{hostid}/item/{itemid}")
async def get_item_history(
    request: Request,
    hostid: str,
    itemid: str,
    time_from: Optional[int] = None,
    time_to: Optional[int] = None,
    limit: int = 1000,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get historical data for a specific item
    """
    from datetime import datetime, timedelta
    
    zabbix = request.app.state.zabbix
    
    # Default to last 24 hours if not specified
    if not time_to:
        time_to = int(datetime.now().timestamp())
    if not time_from:
        time_from = int((datetime.now() - timedelta(hours=24)).timestamp())
    
    def fetch_history():
        try:
            # Get item info
            items = zabbix.zapi.item.get(
                itemids=[itemid],
                output=["itemid", "name", "key_", "units", "value_type"],
            )
            
            if not items:
                return {"error": "Item not found"}
            
            item = items[0]
            value_type = int(item.get("value_type", 0))
            
            # Determine history type
            history_type = 0  # Numeric (float)
            if value_type == 1:  # Character
                history_type = 1
            elif value_type == 2:  # Log
                history_type = 2
            elif value_type == 3:  # Numeric (unsigned)
                history_type = 0
            elif value_type == 4:  # Text
                history_type = 1
            
            history = zabbix.zapi.history.get(
                itemids=[itemid],
                time_from=time_from,
                time_to=time_to,
                history=history_type,
                sortfield="clock",
                sortorder="ASC",
                limit=limit,
            )
            
            return {
                "itemid": itemid,
                "item_name": item["name"],
                "item_key": item["key_"],
                "units": item.get("units", ""),
                "time_from": time_from,
                "time_to": time_to,
                "data": [
                    {
                        "timestamp": int(h["clock"]),
                        "value": h["value"],
                    }
                    for h in history
                ],
            }
        except Exception as e:
            logger.error(f"Error fetching history for item {itemid}: {e}")
            raise
    
    return await run_in_executor(fetch_history)
