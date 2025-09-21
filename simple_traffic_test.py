#!/usr/bin/env python3
"""
Simple Traffic Test for nitedu.in
"""
import requests
import time

def test_backend():
    """Test the deployed backend"""
    
    backend_url = "https://cognitive-cyber-defense.onrender.com"
    
    print("Testing nitedu.in Backend")
    print("=" * 30)
    
    # Test 1: Health Check
    try:
        print("1. Health Check...")
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
        else:
            print(f"   Failed: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Main Endpoint
    try:
        print("\n2. Main Endpoint...")
        response = requests.get(f"{backend_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"   Failed: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Prediction API
    try:
        print("\n3. Testing Your Traffic...")
        
        # Simulate your request
        test_data = {
            "method": "GET",
            "path": "/",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "timestamp": int(time.time())
        }
        
        response = requests.post(
            f"{backend_url}/api/v1/predict",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Your IP: {result.get('source_ip', 'Unknown')}")
            print(f"   Anomaly: {result.get('is_anomaly', False)}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
            print(f"   Attack Type: {result.get('attack_type', 'Normal')}")
            print(f"   Method: {result.get('method', 'Unknown')}")
            
            if result.get('is_anomaly'):
                print("   Status: SUSPICIOUS TRAFFIC")
            else:
                print("   Status: SAFE TRAFFIC")
        else:
            print(f"   Failed: {response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: SQL Injection Test
    try:
        print("\n4. Testing SQL Injection Detection...")
        
        attack_data = {
            "method": "POST",
            "path": "/login?id=1' UNION SELECT * FROM users--",
            "user_agent": "sqlmap/1.0",
            "timestamp": int(time.time())
        }
        
        response = requests.post(
            f"{backend_url}/api/v1/predict",
            json=attack_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Anomaly: {result.get('is_anomaly', False)}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
            print(f"   Attack Type: {result.get('attack_type', 'Normal')}")
            
            if result.get('is_anomaly'):
                print("   Status: ATTACK DETECTED!")
            else:
                print("   Status: Not detected")
        else:
            print(f"   Failed: {response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_backend()