#!/usr/bin/env python3
import sys
sys.path.append('.')

from backend.app.main_ml import load_ml_models, ml_state, predict_anomaly
from fastapi import Request
import json

class MockRequest:
    def __init__(self, data):
        self.data = data
        self.client = type('obj', (object,), {'host': '127.0.0.1'})
        self.headers = {}
    
    async def body(self):
        return json.dumps(self.data).encode()

async def test_final():
    print("Final ML Integration Test")
    print("=" * 30)
    
    # Load models
    load_ml_models()
    print(f"ML Available: {ml_state.available}")
    
    # Test cases
    tests = [
        {
            "name": "Normal Request",
            "data": {"method": "GET", "path": "/api/users", "user_agent": "Mozilla/5.0"}
        },
        {
            "name": "SQL Injection",
            "data": {"method": "POST", "path": "/login?id=1' UNION SELECT * FROM users--", "user_agent": "sqlmap/1.0"}
        }
    ]
    
    for test in tests:
        print(f"\nTesting: {test['name']}")
        mock_request = MockRequest(test['data'])
        result = await predict_anomaly(mock_request)
        
        print(f"  Anomaly: {result.get('is_anomaly')}")
        print(f"  Confidence: {result.get('confidence', 0):.3f}")
        print(f"  Attack Type: {result.get('attack_type')}")
        print(f"  Method: {result.get('method')}")
        
        if result.get('method') == 'advanced_ml':
            print("  Status: SUCCESS - Using ML!")
        else:
            print("  Status: Using fallback")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_final())