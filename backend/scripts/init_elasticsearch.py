#!/usr/bin/env python3
"""
Initialize Elasticsearch index with proper mapping
"""

import asyncio
import sys
import os
from elasticsearch import AsyncElasticsearch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


async def init_elasticsearch():
    """Initialize Elasticsearch index"""
    print("🚀 Initializing Elasticsearch index...")
    
    # Connect to Elasticsearch
    es_client = AsyncElasticsearch(
        hosts=[settings.ELASTICSEARCH_URL],
        verify_certs=False,
        request_timeout=30
    )
    
    try:
        # Test connection
        info = await es_client.info()
        print(f"✅ Connected to Elasticsearch version {info['version']['number']}")
        
        index_name = settings.ELASTICSEARCH_INDEX
        
        # Check if index exists
        exists = await es_client.indices.exists(index=index_name)
        
        if exists:
            print(f"⚠️  Index '{index_name}' already exists")
            print("Keeping existing index")
        else:
            # Create index with mapping
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
                    "number_of_replicas": 1,
                    "refresh_interval": "5s"
                }
            }
            
            await es_client.indices.create(index=index_name, body=mapping)
            print(f"✅ Created index '{index_name}'")
        
        print("\n✨ Elasticsearch initialization complete!")
        
    except Exception as e:
        print(f"❌ Error initializing Elasticsearch: {e}")
        raise
    finally:
        await es_client.close()


if __name__ == "__main__":
    asyncio.run(init_elasticsearch())