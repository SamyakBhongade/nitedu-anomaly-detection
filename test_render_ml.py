#!/usr/bin/env python3
"""
Test Render ML Backend
"""
import requests
import json

def test_render_ml():
    """Test deployed Render backend with ML"""
    
    # Your Render URL
    render_url = "https://cognitive-cyber-defense.onrender.com"
    
    print("Testing Render ML Backend")
    print("=" * 30)
    
    # Test 1: Health Check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{render_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   ML Status: {data.get('ml_status')}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Failed: {e}")
    
    # Test 2: ML Status
    print("\n2. ML Status Check")
    try:
        response = requests.get(f"{render_url}/api/v1/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ML Models Loaded: {data.get('ml_models_loaded')}")
            print(f"   Detection Method: {data.get('detection_method')}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Failed: {e}")
    
    # Test 3: ML Predictions
    print("\n3. ML Prediction Tests")
    
    test_cases = [
        {
            "name": "Normal Request",
            "data": {
                "method": "GET",
                "path": "/api/users",
                "user_agent": "Mozilla/5.0"
            }
        },
        {
            "name": "SQL Injection",
            "data": {
                "method": "POST",
                "path": "/login?id=1' UNION SELECT * FROM users--",
                "user_agent": "sqlmap/1.0"
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n   Testing: {test['name']}")
        try:
            response = requests.post(
                f"{render_url}/api/v1/predict",
                json=test['data'],
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"     Anomaly: {result.get('is_anomaly')}")
                print(f"     Confidence: {result.get('confidence', 0):.3f}")
                print(f"     Attack Type: {result.get('attack_type')}")
                print(f"     Method: {result.get('method')}")
                
                if result.get('method') == 'advanced_ml':
                    print("     SUCCESS: Using ML!")
                else:
                    print("     Using fallback rules")
            else:
                print(f"     Error: {response.status_code}")
                
        except Exception as e:
            print(f"     Failed: {e}")

if __name__ == "__main__":
    test_render_ml()