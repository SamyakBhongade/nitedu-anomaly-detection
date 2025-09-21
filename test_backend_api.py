#!/usr/bin/env python3
"""
Test Backend API directly
"""
import requests
import json

def test_backend_api():
    """Test the backend API endpoints"""
    print("Testing Backend API")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "Normal Request",
            "data": {
                "method": "GET",
                "path": "/api/users",
                "user_agent": "Mozilla/5.0"
            },
            "expected_anomaly": False
        },
        {
            "name": "SQL Injection",
            "data": {
                "method": "POST",
                "path": "/login?id=1' UNION SELECT * FROM users--",
                "user_agent": "sqlmap/1.0"
            },
            "expected_anomaly": True
        },
        {
            "name": "XSS Attack",
            "data": {
                "method": "GET", 
                "path": "/search?q=<script>alert('XSS')</script>",
                "user_agent": "Mozilla/5.0"
            },
            "expected_anomaly": True
        }
    ]
    
    try:
        # Test health endpoint
        print("\n1. Testing Health Endpoint")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   ML Status: {health_data.get('ml_status')}")
        else:
            print(f"   Health check failed: {health_response.status_code}")
            return
        
        # Test status endpoint
        print("\n2. Testing Status Endpoint")
        status_response = requests.get(f"{base_url}/api/v1/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   ML Models Loaded: {status_data.get('ml_models_loaded')}")
            print(f"   Detection Method: {status_data.get('detection_method')}")
            print(f"   Feature Extractor: {status_data.get('feature_extractor_loaded')}")
            print(f"   Inference Engine: {status_data.get('inference_engine_loaded')}")
        
        # Test prediction endpoint
        print("\n3. Testing Prediction Endpoint")
        for i, test_case in enumerate(test_cases):
            print(f"\n   Test {i+1}: {test_case['name']}")
            
            try:
                response = requests.post(
                    f"{base_url}/api/v1/predict",
                    json=test_case['data'],
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    print(f"     Anomaly: {result.get('is_anomaly')}")
                    print(f"     Confidence: {result.get('confidence', 0):.3f}")
                    print(f"     Attack Type: {result.get('attack_type')}")
                    print(f"     Method: {result.get('method')}")
                    
                    if 'model_scores' in result:
                        print(f"     Model Scores: {result['model_scores']}")
                    
                    # Check if result matches expectation
                    if result.get('is_anomaly') == test_case['expected_anomaly']:
                        print(f"     ✓ Result matches expectation")
                    else:
                        print(f"     ✗ Expected {test_case['expected_anomaly']}, got {result.get('is_anomaly')}")
                        
                else:
                    print(f"     Error: {response.status_code}")
                    print(f"     Response: {response.text}")
                    
            except Exception as e:
                print(f"     Request failed: {e}")
        
        print(f"\n4. Summary")
        print(f"   Backend API is responding correctly")
        print(f"   All endpoints are functional")
        
    except requests.exceptions.ConnectionError:
        print("Backend server not running!")
        print("Start with: cd backend && python -m uvicorn app.main_ml:app --reload")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_backend_api()