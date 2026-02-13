"""
MongoDB database connection and utilities
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global database client
mongodb_client: Optional[AsyncIOMotorClient] = None


async def connect_db():
    """Connect to MongoDB"""
    global mongodb_client
    
    try:
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
        )
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_db():
    """Close MongoDB connection"""
    global mongodb_client
    
    if mongodb_client:
        mongodb_client.close()
        logger.info("Closed MongoDB connection")


def get_database():
    """Get database instance"""
    if mongodb_client is None:
        raise Exception("Database not connected")
    return mongodb_client[settings.DATABASE_NAME]


async def create_indexes():
    """Create database indexes"""
    db = get_database()
    
    # Decision traces collection indexes
    traces = db.decision_traces
    
    await traces.create_index("decision_id", unique=True)
    await traces.create_index("source_system")
    await traces.create_index("risk_level")
    await traces.create_index("timestamp")
    await traces.create_index("hash")
    await traces.create_index([("source_system", 1), ("timestamp", -1)])
    await traces.create_index([("risk_level", 1), ("timestamp", -1)])
    
    logger.info("Database indexes created successfully")


async def get_next_sequence(name: str) -> int:
    """Get next sequence number for ID generation"""
    db = get_database()
    counters = db.counters
    
    result = await counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"sequence": 1}},
        upsert=True,
        return_document=True
    )
    
    return result["sequence"] if result else 1