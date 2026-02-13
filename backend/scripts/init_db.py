#!/usr/bin/env python3
"""
Initialize MongoDB database with indexes and sample data
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


async def init_database():
    """Initialize database"""
    print("🚀 Initializing Decision Audit System database...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Create collections
        collections = await db.list_collection_names()
        
        if 'decision_traces' not in collections:
            await db.create_collection('decision_traces')
            print("✅ Created 'decision_traces' collection")
        
        # Create indexes
        print("📊 Creating indexes...")
        
        traces = db.decision_traces
        
        await traces.create_index("decision_id", unique=True)
        await traces.create_index("source_system")
        await traces.create_index("risk_level")
        await traces.create_index("timestamp")
        await traces.create_index("hash")
        await traces.create_index([("source_system", 1), ("timestamp", -1)])
        await traces.create_index([("risk_level", 1), ("timestamp", -1)])
        
        print("✅ Indexes created successfully")
        
        # Create counters collection
        if 'counters' not in collections:
            await db.create_collection('counters')
            print("✅ Created 'counters' collection")
        
        # Initialize sequence counter
        await db.counters.update_one(
            {"_id": "decision_id"},
            {"$setOnInsert": {"sequence": 0}},
            upsert=True
        )
        
        print("\n✨ Database initialization complete!")
        print(f"📝 Database: {settings.DATABASE_NAME}")
        print(f"🔗 MongoDB URL: {settings.MONGODB_URL}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(init_database())