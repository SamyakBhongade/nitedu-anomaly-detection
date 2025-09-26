#!/usr/bin/env python3
"""
Test script to verify Render backend and Cloudflare Worker connection
"""

import requests
import json
import time

def test_render_backend():
    """Test the Render backend directly"""
    print("🧪 Testing Render Backend...")
    
    backend_url = "https://nitedu-anomaly-detection-6w4v.onrender.com"
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{backend_url}/health", timeout=10)
        print(f"✅ Health Check: {health_response.status_code}")
        print(f"   Response: {health_response.json()}")
        
        # Test prediction endpoint
        test_data = {
            "path": "/test",
            "user_agent": "Mozilla/5.0",
            "method": "GET",
            "client_ip": "192.168.1.1",
            "country": "US"
        }
        
        pred_response = requests.post(f"{backend_url}/api/v1/predict", 
                                    json=test_data, timeout=10)
        print(f"✅ Prediction API: {pred_response.status_code}")
        result = pred_response.json()
        print(f"   Anomaly: {result.get('is_anomaly')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Method: {result.get('method')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return False

def test_malicious_request():
    """Test with malicious request"""
    print("\n🦹 Testing Malicious Request...")
    
    backend_url = "https://nitedu-anomaly-detection-6w4v.onrender.com"
    
    malicious_data = {
        "path": "/login?id=1' UNION SELECT * FROM users--",
        "user_agent": "sqlmap/1.6.12",
        "method": "POST",
        "client_ip": "10.0.0.1",
        "country": "CN"
    }
    
    try:
        response = requests.post(f"{backend_url}/api/v1/predict", 
                               json=malicious_data, timeout=10)
        result = response.json()
        
        print(f"✅ Malicious Detection: {response.status_code}")
        print(f"   Anomaly: {result.get('is_anomaly')}")
        print(f"   Attack Type: {result.get('attack_type')}")
        print(f"   Confidence: {result.get('confidence')}")
        
        return result.get('is_anomaly', False)
        
    except Exception as e:
        print(f"❌ Malicious Test Error: {e}")
        return False

def main():
    print("🛡️ Cognitive Cyber Defense - Connection Test")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_render_backend()
    
    if backend_ok:
        # Test malicious detection
        detected = test_malicious_request()
        
        print(f"\n📊 Test Results:")
        print(f"   Backend Status: {'✅ Working' if backend_ok else '❌ Failed'}")
        print(f"   Threat Detection: {'✅ Working' if detected else '❌ Failed'}")
        
        if backend_ok and detected:
            print(f"\n🚀 Ready to connect to Cloudflare!")
            print(f"   Backend URL: https://nitedu-anomaly-detection-6w4v.onrender.com")
            print(f"   Next: Deploy Cloudflare Worker")
        else:
            print(f"\n⚠️  Fix backend issues before connecting to Cloudflare")
    
    else:
        print(f"\n❌ Backend not accessible. Deploy to Render first.")
        print(f"   1. Push code to GitHub")
        print(f"   2. Connect repo to Render")
        print(f"   3. Deploy as Web Service")

if __name__ == "__main__":
    main()