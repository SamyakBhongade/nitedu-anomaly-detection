#!/usr/bin/env python3
import sys
sys.path.append('.')

# Test the new ML integration
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

async def test_ml_integration():
    print("Testing New ML Integration")
    print("=" * 30)
    
    # Load models
    success = load_ml_models()
    print(f"ML Loading Success: {success}")
    print(f"ML Available: {ml_state.available}")
    print(f"Engine Loaded: {ml_state.engine is not None}")
    
    if ml_state.engine:
        print(f"Engine is_loaded: {ml_state.engine.is_loaded}")
    
    # Test prediction
    test_data = {
        "method": "POST",
        "path": "/login?id=1' UNION SELECT * FROM users--",
        "user_agent": "sqlmap/1.0"
    }
    
    mock_request = MockRequest(test_data)
    result = await predict_anomaly(mock_request)
    
    print(f"\nPrediction Result:")
    print(f"  Anomaly: {result.get('is_anomaly')}")
    print(f"  Confidence: {result.get('confidence', 0):.3f}")
    print(f"  Attack Type: {result.get('attack_type')}")
    print(f"  Method: {result.get('method')}")
    
    if result.get('method') == 'advanced_ml':
        print("✅ SUCCESS: Using Advanced ML!")
    else:
        print("❌ ISSUE: Still using fallback")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ml_integration())