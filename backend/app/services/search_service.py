"""
Search service using Elasticsearch
"""

from typing import List, Optional
from datetime import datetime

from app.core.elasticsearch_client import get_es_client
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
        es_client = get_es_client()
        
        # Build query
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
        
        # Execute search
        response = await es_client.search(
            index="decision_traces",
            query=query,
            from_=offset,
            size=limit,
            sort=[{"timestamp": {"order": "desc"}}]
        )
        
        # Parse results
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
        es_client = get_es_client()
        
        response = await es_client.search(
            index="decision_traces",
            size=0,
            aggs={
                "risk_levels": {
                    "terms": {
                        "field": "risk_level",
                        "size": 10
                    }
                }
            }
        )
        
        buckets = response["aggregations"]["risk_levels"]["buckets"]
        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}
    
    @staticmethod
    async def aggregate_by_source_system() -> dict:
        """Aggregate decisions by source system"""
        es_client = get_es_client()
        
        response = await es_client.search(
            index="decision_traces",
            size=0,
            aggs={
                "source_systems": {
                    "terms": {
                        "field": "source_system",
                        "size": 20
                    }
                }
            }
        )
        
        buckets = response["aggregations"]["source_systems"]["buckets"]
        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}
    
    @staticmethod
    async def get_recent_high_risk(limit: int = 10) -> List[DecisionTrace]:
        """Get recent high-risk decisions"""
        es_client = get_es_client()
        
        response = await es_client.search(
            index="decision_traces",
            query={
                "bool": {
                    "should": [
                        {"term": {"risk_level": "high"}},
                        {"term": {"risk_level": "critical"}}
                    ]
                }
            },
            size=limit,
            sort=[{"timestamp": {"order": "desc"}}]
        )
        
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append(DecisionTrace(**source))
        
        return results