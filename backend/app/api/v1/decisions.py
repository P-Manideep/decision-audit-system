"""
API endpoints for decision management
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.models.decision import DecisionTrace, DecisionTraceCreate
from app.services.decision_service import DecisionService

router = APIRouter()


@router.post("/ingest", response_model=DecisionTrace, status_code=status.HTTP_201_CREATED)
async def ingest_decision(trace: DecisionTraceCreate):
    """
    Ingest a new decision trace
    
    Creates a new decision trace with full lineage tracking including:
    - Input data
    - Rules triggered
    - Output decision
    - Risk level
    - Immutable hash for verification
    """
    try:
        result = await DecisionService.create_decision_trace(trace)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest decision: {str(e)}"
        )


@router.get("/trace/{decision_id}", response_model=DecisionTrace)
async def get_decision_trace(decision_id: str):
    """
    Retrieve full decision trace by ID
    
    Returns complete decision lineage including:
    - Original inputs
    - Rules executed
    - Decision output
    - All review notes
    - Hash verification data
    """
    trace = await DecisionService.get_decision_trace(decision_id)
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision trace {decision_id} not found"
        )
    
    return trace


@router.get("/verify/{decision_id}")
async def verify_decision_integrity(decision_id: str):
    """
    Verify decision trace integrity via hash
    
    Validates that the decision trace has not been tampered with
    by recalculating and comparing the hash.
    """
    is_valid = await DecisionService.verify_hash(decision_id)
    
    if is_valid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision trace {decision_id} not found"
        )
    
    return {
        "decision_id": decision_id,
        "is_valid": is_valid,
        "message": "Hash verification successful" if is_valid else "Hash mismatch - data may be corrupted"
    }


@router.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """
    Get system statistics
    
    Returns aggregated statistics including:
    - Total decisions
    - Breakdown by risk level
    - Breakdown by source system
    """
    try:
        stats = await DecisionService.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )