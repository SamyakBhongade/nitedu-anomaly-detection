#!/usr/bin/env python3
"""
Test ML Integration with Backend
"""
import requests
import json

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
            "path": "/login",
            "user_agent": "Mozilla/5.0",
            "client_ip": "10.0.0.50",
            "payload": "username=admin' OR '1'='1' --&password=test"
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
    },
    {
        "name": "Bot Attack",
        "data": {
            "method": "GET",
            "path": "/admin",
            "user_agent": "sqlmap/1.0",
            "client_ip": "198.51.100.1"
        }
    }
]

def test_local_backend():
    """Test local backend ML integration"""
    print("🧪 Testing Local ML Backend Integration")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    
    for test in test_requests:
        print(f"\n📋 Test: {test['name']}")
        try:
            response = requests.post(
                f"{backend_url}/api/v1/predict",
                json=test['data'],
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"🎯 Anomaly: {result.get('is_anomaly', 'N/A')}")
                print(f"📊 Confidence: {result.get('confidence', 0):.1%}")
                print(f"🔍 Attack Type: {result.get('attack_type', 'N/A')}")
                print(f"⚙️  Method: {result.get('method', 'N/A')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - Backend not running")
            print("💡 Start backend: cd backend && python -m uvicorn app.main_ml:app --reload")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_render_backend():
    """Test deployed Render backend"""
    print("\n🌐 Testing Render ML Backend")
    print("=" * 50)
    
    render_url = "https://cognitive-cyber-defense.onrender.com"
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{render_url}/health", timeout=10)
        print(f"🏥 Health Check: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"📊 ML Status: {health_data.get('ml_status', 'unknown')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test prediction endpoint
    test_data = test_requests[1]  # SQL injection test
    print(f"\n📋 Testing: {test_data['name']}")
    
    try:
        response = requests.post(
            f"{render_url}/api/v1/predict",
            json=test_data['data'],
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"🎯 Anomaly: {result.get('is_anomaly', 'N/A')}")
            print(f"📊 Confidence: {result.get('confidence', 0):.1%}")
            print(f"🔍 Attack Type: {result.get('attack_type', 'N/A')}")
            print(f"⚙️  Method: {result.get('method', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🛡️ Cognitive Cyber Defense - ML Integration Test")
    print("=" * 60)
    
    # Test local backend
    test_local_backend()
    
    # Test deployed backend
    test_render_backend()
    
    print("\n" + "=" * 60)
    print("🎯 Integration Test Complete!")