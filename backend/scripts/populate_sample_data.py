#!/usr/bin/env python3
"""
Populate database with realistic sample data
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.decision_service import DecisionService
from app.models.decision import DecisionTraceCreate, RuleTriggered, RiskLevel
from app.core.database import connect_db, close_db
from app.core.elasticsearch_client import connect_elasticsearch, close_elasticsearch


# Sample data templates
FRAUD_SCENARIOS = [
    {
        "source_system": "fraud_detection",
        "input": {"transaction_id": "TXN{}", "amount": 5000, "merchant": "TechStore", "location": "USA"},
        "rules": [{"rule_id": "R001", "rule_name": "high_value_check", "condition": "amount > 1000", "result": True}],
        "output": {"decision": "APPROVED", "flags": ["high_value"]},
        "confidence": 0.95,
        "risk": "medium"
    },
    {
        "source_system": "fraud_detection",
        "input": {"transaction_id": "TXN{}", "amount": 150, "merchant": "Coffee Shop", "location": "USA"},
        "rules": [{"rule_id": "R002", "rule_name": "low_value_check", "condition": "amount < 500", "result": True}],
        "output": {"decision": "APPROVED", "flags": []},
        "confidence": 0.99,
        "risk": "low"
    },
    {
        "source_system": "fraud_detection",
        "input": {"transaction_id": "TXN{}", "amount": 12000, "merchant": "Unknown Vendor", "location": "Nigeria"},
        "rules": [
            {"rule_id": "R003", "rule_name": "high_risk_country", "condition": "location in high_risk_list", "result": True},
            {"rule_id": "R004", "rule_name": "unusual_amount", "condition": "amount > 10000", "result": True}
        ],
        "output": {"decision": "BLOCKED", "flags": ["suspicious_location", "high_amount"]},
        "confidence": 0.87,
        "risk": "critical"
    }
]

LOAN_SCENARIOS = [
    {
        "source_system": "loan_approval",
        "input": {"application_id": "LOAN{}", "credit_score": 750, "income": 85000, "debt_ratio": 0.15},
        "rules": [
            {"rule_id": "L001", "rule_name": "credit_score_check", "condition": "credit_score > 700", "result": True},
            {"rule_id": "L002", "rule_name": "debt_ratio_check", "condition": "debt_ratio < 0.4", "result": True}
        ],
        "output": {"decision": "APPROVED", "rate": 4.5, "amount": 250000},
        "confidence": 0.96,
        "risk": "low"
    },
    {
        "source_system": "loan_approval",
        "input": {"application_id": "LOAN{}", "credit_score": 620, "income": 45000, "debt_ratio": 0.45},
        "rules": [
            {"rule_id": "L001", "rule_name": "credit_score_check", "condition": "credit_score > 600", "result": True},
            {"rule_id": "L002", "rule_name": "debt_ratio_check", "condition": "debt_ratio < 0.4", "result": False}
        ],
        "output": {"decision": "DENIED", "reason": "High debt-to-income ratio"},
        "confidence": 0.91,
        "risk": "high"
    }
]

HIRING_SCENARIOS = [
    {
        "source_system": "ai_hiring",
        "input": {"candidate_id": "CAND{}", "skills_match": 0.88, "experience_years": 5, "education": "Masters"},
        "rules": [
            {"rule_id": "H001", "rule_name": "skills_match_threshold", "condition": "skills_match > 0.75", "result": True},
            {"rule_id": "H002", "rule_name": "experience_check", "condition": "experience_years >= 3", "result": True}
        ],
        "output": {"decision": "INTERVIEW", "interview_type": "technical"},
        "confidence": 0.88,
        "risk": "low"
    }
]


async def populate_data():
    """Populate database with sample decisions"""
    print("🚀 Populating Decision Audit System with sample data...")
    
    # Connect to databases
    await connect_db()
    await connect_elasticsearch()
    
    try:
        decisions_created = 0
        
        # Create 50 decisions over the past 30 days
        for i in range(50):
            # Randomly pick a scenario
            all_scenarios = FRAUD_SCENARIOS + LOAN_SCENARIOS + HIRING_SCENARIOS
            scenario = random.choice(all_scenarios)
            
            # Create decision with varying timestamps
            days_ago = random.randint(0, 30)
            
            # Format input with unique ID
            input_data = scenario["input"].copy()
            for key, value in input_data.items():
                if isinstance(value, str) and "{}" in value:
                    input_data[key] = value.format(1000 + i)
            
            # Create rules
            rules = [
                RuleTriggered(
                    rule_id=r["rule_id"],
                    rule_name=r["rule_name"],
                    condition=r["condition"],
                    result=r["result"]
                ) for r in scenario["rules"]
            ]
            
            # Create decision trace
            trace = DecisionTraceCreate(
                source_system=scenario["source_system"],
                input_payload=input_data,
                rules_triggered=rules,
                output=scenario["output"],
                confidence=scenario["confidence"],
                risk_level=RiskLevel(scenario["risk"])
            )
            
            result = await DecisionService.create_decision_trace(trace)
            decisions_created += 1
            
            if decisions_created % 10 == 0:
                print(f"✅ Created {decisions_created} decisions...")
        
        print(f"\n✨ Successfully created {decisions_created} sample decisions!")
        print(f"📊 Distribution:")
        print(f"   - Fraud Detection: ~{decisions_created * 0.6:.0f}")
        print(f"   - Loan Approval: ~{decisions_created * 0.3:.0f}")
        print(f"   - AI Hiring: ~{decisions_created * 0.1:.0f}")
        
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        raise
    finally:
        await close_db()
        await close_elasticsearch()


if __name__ == "__main__":
    asyncio.run(populate_data())