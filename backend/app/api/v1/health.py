"""
Health check and system status endpoints
"""

from fastapi import APIRouter
from datetime import datetime

from app.core.database import get_database
from app.core.elasticsearch_client import get_es_client
from app.models.decision import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Checks the status of all system components:
    - API server
    - MongoDB
    - Elasticsearch
    """
    services = {}
    
    # Check MongoDB
    try:
        db = get_database()
        await db.command("ping")
        services["mongodb"] = "healthy"
    except Exception as e:
        services["mongodb"] = f"unhealthy: {str(e)}"
    
    # Check Elasticsearch
    try:
        es_client = get_es_client()
        await es_client.ping()
        services["elasticsearch"] = "healthy"
    except Exception as e:
        services["elasticsearch"] = f"unhealthy: {str(e)}"
    
    # Overall status
    overall_status = "healthy" if all(
        status == "healthy" for status in services.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        services=services,
        timestamp=datetime.utcnow()
    )


@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes"""
    try:
        db = get_database()
        await db.command("ping")
        return {"status": "ready"}
    except Exception:
        return {"status": "not ready"}, 503


@router.get("/live")
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return {"status": "alive"}