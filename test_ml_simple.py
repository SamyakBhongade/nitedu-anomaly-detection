#!/usr/bin/env python3
"""
Simple ML Integration Test
"""
import requests
import json
import sys
import os

# Add current directory to path
sys.path.append('.')

def test_ml_backend():
    """Test ML backend functionality"""
    print("Testing ML Backend Integration")
    print("=" * 40)
    
    # Test data
    test_requests = [
        {
            "name": "Normal Request",
            "data": {
                "method": "GET",
                "path": "/api/users",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "client_ip": "192.168.1.100"
            }
        },
        {
            "name": "SQL Injection Attack",
            "data": {
                "method": "POST", 
                "path": "/login?id=1' UNION SELECT * FROM users--",
                "user_agent": "sqlmap/1.0",
                "client_ip": "10.0.0.50"
            }
        },
        {
            "name": "XSS Attack",
            "data": {
                "method": "GET",
                "path": "/search?q=<script>alert('XSS')</script>",
                "user_agent": "Mozilla/5.0",
                "client_ip": "203.0.113.1"
            }
        }
    ]
    
    # Test local import
    try:
        from backend.app.main_ml import load_ml_models, ml_engine, ml_available
        print("\n[OK] ML modules imported successfully")
        
        # Load models
        load_ml_models()
        print(f"[INFO] ML Available: {ml_available}")
        
        if ml_engine and ml_available:
            print("[OK] Advanced ML models loaded")
            
            # Test predictions
            for test in test_requests:
                print(f"\nTesting: {test['name']}")
                try:
                    result = ml_engine.predict_anomaly(test['data'])
                    
                    if 'error' not in result:
                        print(f"  Anomaly: {result.get('is_anomaly', 'N/A')}")
                        print(f"  Confidence: {result.get('confidence', 0):.3f}")
                        print(f"  Attack Type: {result.get('attack_type', 'N/A')}")
                        print(f"  Method: {result.get('model_type', 'N/A')}")
                    else:
                        print(f"  Error: {result['error']}")
                        
                except Exception as e:
                    print(f"  Prediction Error: {e}")
        else:
            print("[WARN] ML models not available, using fallback")
            
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

def test_backend_server():
    """Test backend server if running"""
    print("\nTesting Backend Server")
    print("=" * 40)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"[OK] Server running: {health_data}")
            
            # Test prediction endpoint
            test_data = {
                "method": "GET",
                "path": "/test' OR '1'='1",
                "user_agent": "sqlmap/1.0"
            }
            
            pred_response = requests.post(
                "http://localhost:8000/api/v1/predict",
                json=test_data,
                timeout=10
            )
            
            if pred_response.status_code == 200:
                result = pred_response.json()
                print(f"[OK] Prediction API working")
                print(f"  Anomaly: {result.get('is_anomaly')}")
                print(f"  Confidence: {result.get('confidence', 0):.3f}")
                print(f"  Method: {result.get('method', 'N/A')}")
            else:
                print(f"[ERROR] Prediction API failed: {pred_response.status_code}")
        else:
            print(f"[ERROR] Server not healthy: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("[INFO] Backend server not running")
        print("To start: cd backend && python -m uvicorn app.main_ml:app --reload")
    except Exception as e:
        print(f"[ERROR] Server test failed: {e}")

if __name__ == "__main__":
    print("Cognitive Cyber Defense - ML Integration Test")
    print("=" * 50)
    
    # Test ML functionality
    test_ml_backend()
    
    # Test server if running
    test_backend_server()
    
    print("\n" + "=" * 50)
    print("Integration test complete!")