"""
Business logic for decision traces
"""

import hashlib
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.core.database import get_database, get_next_sequence
from app.core.elasticsearch_client import get_es_client
from app.models.decision import (
    DecisionTrace,
    DecisionTraceCreate,
    ReviewNote,
    RiskLevel
)


class DecisionService:
    """Service for managing decision traces"""
    
    @staticmethod
    def generate_decision_id() -> str:
        """Generate unique decision ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        return f"DEC_{timestamp}_{int(datetime.utcnow().timestamp() * 1000000)}"
    
    @staticmethod
    def calculate_hash(trace_data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash for immutability"""
        # Create deterministic JSON string
        json_str = json.dumps(trace_data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    @staticmethod
    async def create_decision_trace(trace_create: DecisionTraceCreate) -> DecisionTrace:
        """Create a new decision trace"""
        db = get_database()
        es_client = get_es_client()
        
        # Generate decision ID
        decision_id = DecisionService.generate_decision_id()
        
        # Prepare trace data
        trace_data = {
            "decision_id": decision_id,
            "source_system": trace_create.source_system,
            "input_payload": trace_create.input_payload,
            "rules_triggered": [rule.model_dump() for rule in trace_create.rules_triggered],
            "output": trace_create.output,
            "confidence": trace_create.confidence,
            "risk_level": trace_create.risk_level.value,
            "timestamp": datetime.utcnow(),
            "review_notes": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": trace_create.metadata or {}
        }
        
        # Calculate hash for immutability
        trace_data["hash"] = DecisionService.calculate_hash(trace_data)
        
        # Store in MongoDB
        await db.decision_traces.insert_one(trace_data)
        
        # Prepare data for Elasticsearch (remove MongoDB _id and convert datetime)
        es_data = trace_data.copy()
        es_data.pop("_id", None)
        
        # Convert datetime objects to ISO format strings for Elasticsearch
        for key in ["timestamp", "created_at", "updated_at"]:
            if key in es_data and isinstance(es_data[key], datetime):
                es_data[key] = es_data[key].isoformat()
        
        # Index in Elasticsearch for search
        await es_client.index(
            index="decision_traces",
            id=decision_id,
            document=es_data
        )
        
        # Remove _id from trace_data before returning
        trace_data.pop("_id", None)
        
        return DecisionTrace(**trace_data)
    
    @staticmethod
    async def get_decision_trace(decision_id: str) -> Optional[DecisionTrace]:
        """Retrieve a decision trace by ID"""
        db = get_database()
        
        trace_data = await db.decision_traces.find_one({"decision_id": decision_id})
        
        if trace_data:
            trace_data.pop("_id", None)
            return DecisionTrace(**trace_data)
        
        return None
    
    @staticmethod
    async def add_annotation(
        decision_id: str,
        reviewer: str,
        note: str,
        tags: List[str]
    ) -> Optional[DecisionTrace]:
        """Add a review note to a decision trace"""
        db = get_database()
        es_client = get_es_client()
        
        # Create review note
        review_note = ReviewNote(
            reviewer=reviewer,
            note=note,
            tags=tags,
            timestamp=datetime.utcnow()
        )
        
        # Update in MongoDB
        result = await db.decision_traces.find_one_and_update(
            {"decision_id": decision_id},
            {
                "$push": {"review_notes": review_note.model_dump()},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        if result:
            result.pop("_id", None)
            
            # Update in Elasticsearch
            await es_client.update(
                index="decision_traces",
                id=decision_id,
                doc={"review_notes": result["review_notes"]}
            )
            
            return DecisionTrace(**result)
        
        return None
    
    @staticmethod
    async def verify_hash(decision_id: str) -> bool:
        """Verify decision trace integrity via hash"""
        trace = await DecisionService.get_decision_trace(decision_id)
        
        if not trace:
            return False
        
        # Recalculate hash
        trace_data = trace.model_dump()
        stored_hash = trace_data.pop("hash")
        trace_data.pop("review_notes", None)
        trace_data.pop("updated_at", None)
        
        calculated_hash = DecisionService.calculate_hash(trace_data)
        
        return stored_hash == calculated_hash
    
    @staticmethod
    async def get_statistics() -> Dict[str, Any]:
        """Get system statistics"""
        db = get_database()
        
        # Total decisions
        total = await db.decision_traces.count_documents({})
        
        # Decisions by risk level
        pipeline = [
            {"$group": {"_id": "$risk_level", "count": {"$sum": 1}}}
        ]
        risk_stats = await db.decision_traces.aggregate(pipeline).to_list(None)
        
        # Decisions by system
        pipeline = [
            {"$group": {"_id": "$source_system", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        system_stats = await db.decision_traces.aggregate(pipeline).to_list(None)
        
        return {
            "total_decisions": total,
            "by_risk_level": {item["_id"]: item["count"] for item in risk_stats},
            "by_source_system": {item["_id"]: item["count"] for item in system_stats}
        }