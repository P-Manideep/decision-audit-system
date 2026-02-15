"""
Search service using Elasticsearch
"""

from typing import List, Optional
from datetime import datetime

from app.core.elasticsearch_client import get_es_client
from app.core.database import get_database
from app.models.decision import DecisionTrace, SearchResponse, RiskLevel


class SearchService:
    """Service for searching decision traces"""
    
    @staticmethod
    async def search_decisions(
        source_system: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_text: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> SearchResponse:
        """Search decision traces with filters"""
        
        # Try Elasticsearch first, fall back to MongoDB
        try:
            es_client = get_es_client()
            return await SearchService._search_with_elasticsearch(
                es_client, source_system, risk_level, start_date, end_date, search_text, limit, offset
            )
        except Exception as e:
            # Fall back to MongoDB search
            return await SearchService._search_with_mongodb(
                source_system, risk_level, start_date, end_date, search_text, limit, offset
            )
    
    @staticmethod
    async def _search_with_mongodb(
        source_system, risk_level, start_date, end_date, search_text, limit, offset
    ):
        """Fallback search using MongoDB"""
        from app.core.database import get_database
        db = get_database()
        
        query = {}
        if source_system:
            query["source_system"] = source_system
        if risk_level:
            query["risk_level"] = risk_level.value
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = db.decision_traces.find(query).sort("timestamp", -1).skip(offset).limit(limit)
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(DecisionTrace(**doc))
        
        total = await db.decision_traces.count_documents(query)
        
        return SearchResponse(
            total=total,
            results=results,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
    
    @staticmethod
    async def _search_with_elasticsearch(
        es_client, source_system, risk_level, start_date, end_date, search_text, limit, offset
    ):
        """Search using Elasticsearch"""
        must_conditions = []
        
        if source_system:
            must_conditions.append({"term": {"source_system": source_system}})
        if risk_level:
            must_conditions.append({"term": {"risk_level": risk_level.value}})
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["gte"] = start_date.isoformat()
            if end_date:
                date_range["lte"] = end_date.isoformat()
            must_conditions.append({"range": {"timestamp": date_range}})
        if search_text:
            must_conditions.append({
                "multi_match": {
                    "query": search_text,
                    "fields": ["output.*", "input_payload.*", "rules_triggered.rule_name"]
                }
            })
        
        query = {
            "bool": {
                "must": must_conditions if must_conditions else [{"match_all": {}}]
            }
        }
        
        response = await es_client.search(
            index="decision_traces",
            query=query,
            from_=offset,
            size=limit,
            sort=[{"timestamp": {"order": "desc"}}]
        )
        
        total = response["hits"]["total"]["value"]
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append(DecisionTrace(**source))
        
        return SearchResponse(
            total=total,
            results=results,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
    
    @staticmethod
    async def aggregate_by_risk_level() -> dict:
        """Aggregate decisions by risk level"""
        db = get_database()
        pipeline = [{"$group": {"_id": "$risk_level", "count": {"$sum": 1}}}]
        result = await db.decision_traces.aggregate(pipeline).to_list(None)
        return {item["_id"]: item["count"] for item in result}
    
    @staticmethod
    async def aggregate_by_source_system() -> dict:
        """Aggregate decisions by source system"""
        db = get_database()
        pipeline = [
            {"$group": {"_id": "$source_system", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        result = await db.decision_traces.aggregate(pipeline).to_list(None)
        return {item["_id"]: item["count"] for item in result}
    
    @staticmethod
    async def get_recent_high_risk(limit: int = 10) -> List[DecisionTrace]:
        """Get recent high-risk decisions"""
        db = get_database()
        cursor = db.decision_traces.find({
            "risk_level": {"$in": ["high", "critical"]}
        }).sort("timestamp", -1).limit(limit)
        
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(DecisionTrace(**doc))
        
        return results
    
