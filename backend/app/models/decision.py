from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enum"""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RuleTriggered(BaseModel):
    """Rule that was triggered in decision"""
    rule_id: str
    rule_name: str
    condition: str
    result: bool
    metadata: Optional[Dict[str, Any]] = None


class ReviewNote(BaseModel):
    """Review note for a decision"""
    reviewer: str
    note: str
    timestamp: datetime
    tags: List[str] = []


class DecisionTraceCreate(BaseModel):
    """Schema for creating a decision trace"""
    source_system: str
    input_payload: Dict[str, Any]
    rules_triggered: List[RuleTriggered] = []
    output: Dict[str, Any]
    confidence: float
    risk_level: RiskLevel
    metadata: Optional[Dict[str, Any]] = None


class DecisionTrace(BaseModel):
    """Complete decision trace"""
    decision_id: str
    source_system: str
    input_payload: Dict[str, Any]
    rules_triggered: List[RuleTriggered]
    output: Dict[str, Any]
    confidence: float
    risk_level: str
    timestamp: datetime
    hash: str
    review_notes: List[ReviewNote] = []
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}


class AnnotationCreate(BaseModel):
    """Schema for creating an annotation"""
    reviewer: str
    note: str
    tags: List[str] = []


class SearchQuery(BaseModel):
    """Search query parameters"""
    source_system: Optional[str] = None
    risk_level: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None
    limit: int = 20
    offset: int = 0


class SearchResponse(BaseModel):
    """Search response"""
    total: int
    results: List[DecisionTrace]
    limit: int
    offset: int
    has_more: bool


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    services: Dict[str, str]
    timestamp: datetime