"""
Elasticsearch client and utilities
"""

from elasticsearch import AsyncElasticsearch
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Elasticsearch client
es_client: Optional[AsyncElasticsearch] = None


async def connect_elasticsearch():
    """Connect to Elasticsearch"""
    global es_client
    
    try:
        es_client = AsyncElasticsearch(
            hosts=[settings.ELASTICSEARCH_URL],
            verify_certs=False,
            request_timeout=30
        )
        
        # Test connection
        info = await es_client.info()
        logger.info(f"Connected to Elasticsearch version {info['version']['number']}")
        
        # Create index if not exists
        await create_index()
        
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        raise


async def close_elasticsearch():
    """Close Elasticsearch connection"""
    global es_client
    
    if es_client:
        await es_client.close()
        logger.info("Closed Elasticsearch connection")


def get_es_client():
    """Get Elasticsearch client instance"""
    if es_client is None:
        raise Exception("Elasticsearch not connected")
    return es_client


async def create_index():
    """Create Elasticsearch index with mapping"""
    client = get_es_client()
    index_name = settings.ELASTICSEARCH_INDEX
    
    # Check if index exists
    exists = await client.indices.exists(index=index_name)
    
    if not exists:
        # Index mapping
        mapping = {
            "mappings": {
                "properties": {
                    "decision_id": {"type": "keyword"},
                    "source_system": {"type": "keyword"},
                    "input_payload": {"type": "object", "enabled": True},
                    "rules_triggered": {
                        "type": "nested",
                        "properties": {
                            "rule_id": {"type": "keyword"},
                            "rule_name": {"type": "text"},
                            "condition": {"type": "text"},
                            "result": {"type": "boolean"}
                        }
                    },
                    "output": {"type": "object", "enabled": True},
                    "confidence": {"type": "float"},
                    "risk_level": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "hash": {"type": "keyword"},
                    "review_notes": {
                        "type": "nested",
                        "properties": {
                            "reviewer": {"type": "keyword"},
                            "note": {"type": "text"},
                            "timestamp": {"type": "date"},
                            "tags": {"type": "keyword"}
                        }
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1
            }
        }
        
        await client.indices.create(index=index_name, body=mapping)
        logger.info(f"Created Elasticsearch index: {index_name}")
    else:
        logger.info(f"Elasticsearch index already exists: {index_name}")