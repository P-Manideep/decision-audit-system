"""
API endpoints for search and analytics
"""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from app.models.decision import SearchResponse, RiskLevel
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_decisions(
    source_system: Optional[str] = Query(None, description="Filter by source system"),
    risk_level: Optional[RiskLevel] = Query(None, description="Filter by risk level"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    search_text: Optional[str] = Query(None, description="Full-text search query"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Search decision traces with filters
    
    Supports:
    - Source system filtering
    - Risk level filtering
    - Date range filtering
    - Full-text search
    - Pagination
    """
    results = await SearchService.search_decisions(
        source_system=source_system,
        risk_level=risk_level,
        start_date=start_date,
        end_date=end_date,
        search_text=search_text,
        limit=limit,
        offset=offset
    )
    
    return results


@router.get("/analytics/risk-distribution")
async def get_risk_distribution():
    """
    Get distribution of decisions by risk level
    
    Returns count of decisions for each risk level:
    - low
    - medium
    - high
    - critical
    """
    distribution = await SearchService.aggregate_by_risk_level()
    return {"risk_distribution": distribution}


@router.get("/analytics/system-distribution")
async def get_system_distribution():
    """
    Get distribution of decisions by source system
    
    Returns count of decisions for each source system
    """
    distribution = await SearchService.aggregate_by_source_system()
    return {"system_distribution": distribution}


@router.get("/analytics/high-risk-recent")
async def get_recent_high_risk(limit: int = Query(10, ge=1, le=50)):
    """
    Get recent high-risk decisions
    
    Returns most recent decisions with risk level 'high' or 'critical'
    """
    decisions = await SearchService.get_recent_high_risk(limit=limit)
    return {"high_risk_decisions": decisions, "count": len(decisions)}