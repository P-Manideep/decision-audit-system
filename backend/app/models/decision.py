"""
Pydantic models for decision traces
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuleTriggered(BaseModel):
    """Individual rule that was triggered"""
    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    condition: str = Field(..., description="Condition that was evaluated")
    result: bool = Field(..., description="Result of the rule evaluation")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional rule metadata")


class ReviewNote(BaseModel):
    """Review note/annotation"""
    reviewer: str = Field(..., description="Email or ID of reviewer")
    note: str = Field(..., description="Review note content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class DecisionTraceCreate(BaseModel):
    """Model for creating a new decision trace"""
    source_system: str = Field(..., description="System that made the decision")
    input_payload: Dict[str, Any] = Field(..., description="Input data used for decision")
    rules_triggered: List[RuleTriggered] = Field(..., description="Rules that were triggered")
    output: Dict[str, Any] = Field(..., description="Decision output")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    risk_level: RiskLevel = Field(..., description="Risk level of the decision")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_system": "fraud_detection",
                "input_payload": {
                    "transaction_id": "TXN123",
                    "amount": 5000,
                    "merchant": "TechStore"
                },
                "rules_triggered": [
                    {
                        "rule_id": "R001",
                        "rule_name": "high_value_check",
                        "condition": "amount > 1000",
                        "result": True
                    }
                ],
                "output": {
                    "decision": "APPROVED",
                    "flags": ["high_value"]
                },
                "confidence": 0.95,
                "risk_level": "medium"
            }
        }


class DecisionTrace(BaseModel):
    """Complete decision trace model"""
    decision_id: str = Field(..., description="Unique decision identifier")
    source_system: str
    input_payload: Dict[str, Any]
    rules_triggered: List[RuleTriggered]
    output: Dict[str, Any]
    confidence: float
    risk_level: RiskLevel
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    hash: str = Field(..., description="SHA-256 hash for immutability verification")
    review_notes: List[ReviewNote] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class AnnotationCreate(BaseModel):
    """Model for adding an annotation"""
    reviewer: str = Field(..., description="Email or ID of reviewer")
    note: str = Field(..., min_length=1, max_length=2000, description="Review note")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class SearchQuery(BaseModel):
    """Search query parameters"""
    source_system: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchResponse(BaseModel):
    """Search results response"""
    total: int = Field(..., description="Total number of results")
    results: List[DecisionTrace] = Field(..., description="List of decision traces")
    limit: int
    offset: int
    has_more: bool = Field(..., description="Whether more results are available")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    services: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)