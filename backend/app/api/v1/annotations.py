"""
API endpoints for annotations and reviews
"""

from fastapi import APIRouter, HTTPException, status

from app.models.decision import AnnotationCreate, DecisionTrace
from app.services.decision_service import DecisionService

router = APIRouter()


@router.put("/annotate/{decision_id}", response_model=DecisionTrace)
async def add_annotation(decision_id: str, annotation: AnnotationCreate):
    """
    Add a review note/annotation to a decision trace
    
    Allows reviewers to add notes, tags, and comments to decisions
    for audit and compliance purposes.
    """
    result = await DecisionService.add_annotation(
        decision_id=decision_id,
        reviewer=annotation.reviewer,
        note=annotation.note,
        tags=annotation.tags
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision trace {decision_id} not found"
        )
    
    return result


@router.get("/annotations/{decision_id}")
async def get_annotations(decision_id: str):
    """
    Retrieve all annotations for a decision trace
    """
    trace = await DecisionService.get_decision_trace(decision_id)
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision trace {decision_id} not found"
        )
    
    return {
        "decision_id": decision_id,
        "annotations": trace.review_notes,
        "count": len(trace.review_notes)
    }