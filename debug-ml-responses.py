#!/usr/bin/env python3
"""
Debug ML Responses
"""

import requests

def debug_ml():
    backend_url = "https://nitedu-anomaly-detection-6w4v.onrender.com"
    
    # Test exactly what Cloudflare sends
    test_data = {
        "method": "GET",
        "path": "/",  # Normal path
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "client_ip": "192.168.1.100", 
        "country": "US",
        "timestamp": 1640995200
    }
    
    print("DEBUGGING ML RESPONSE FOR NORMAL TRAFFIC")
    print("=" * 45)
    
    response = requests.post(f"{backend_url}/api/v1/predict", json=test_data, timeout=10)
    result = response.json()
    
    print(f"Request: {test_data}")
    print(f"Response: {result}")
    print(f"Is Anomaly: {result.get('is_anomaly')}")
    print(f"Confidence: {result.get('confidence')}")
    print(f"Attack Type: {result.get('attack_type')}")

if __name__ == "__main__":
    debug_ml()