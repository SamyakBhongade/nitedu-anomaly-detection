#!/usr/bin/env python3
"""
Monitor nitedu.in Traffic via Render Backend
"""
import requests
import time
import json
from datetime import datetime

def monitor_traffic():
    """Monitor traffic to nitedu.in via Render backend"""
    
    # Your deployed Render backend URL
    backend_url = "https://cognitive-cyber-defense.onrender.com"
    
    print("Monitoring nitedu.in Traffic")
    print("=" * 40)
    print(f"Backend: {backend_url}")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    request_count = 0
    
    try:
        while True:
            try:
                # Make test requests to see traffic
                test_requests = [
                    {
                        "name": "Normal Request",
                        "path": "/api/users",
                        "method": "GET",
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    },
                    {
                        "name": "Your Real Request", 
                        "path": "/",
                        "method": "GET",
                        "user_agent": "Your-Browser/1.0"
                    }
                ]
                
                for test in test_requests:
                    request_count += 1
                    
                    # Send request to backend
                    response = requests.post(
                        f"{backend_url}/api/v1/predict",
                        json={
                            "method": test["method"],
                            "path": test["path"], 
                            "user_agent": test["user_agent"],
                            "timestamp": int(time.time())
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Request #{request_count}")
                        print(f"  Path: {test['path']}")
                        print(f"  Method: {test['method']}")
                        print(f"  Anomaly: {result.get('is_anomaly', 'N/A')}")
                        print(f"  Confidence: {result.get('confidence', 0):.3f}")
                        print(f"  Attack Type: {result.get('attack_type', 'N/A')}")
                        print(f"  Detection: {result.get('method', 'N/A')}")
                        print(f"  Source IP: {result.get('source_ip', 'N/A')}")
                        
                        if result.get('is_anomaly'):
                            print("  ⚠️  THREAT DETECTED!")
                        else:
                            print("  ✅ Safe Traffic")
                    else:
                        print(f"  ❌ Backend Error: {response.status_code}")
                
                # Wait before next check
                time.sleep(5)
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Connection Error: {e}")
                time.sleep(10)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"  ❌ Error: {e}")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print(f"\n\nMonitoring stopped. Total requests: {request_count}")

def test_your_ip():
    """Test with your actual IP and browser"""
    
    backend_url = "https://cognitive-cyber-defense.onrender.com"
    
    print("\nTesting Your Real Traffic")
    print("=" * 30)
    
    # Simulate your real request
    your_request = {
        "method": "GET",
        "path": "/",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "client_ip": "YOUR_REAL_IP",  # This will be detected automatically
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/v1/predict",
            json=your_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"Your Request Analysis:")
            print(f"  Path: {your_request['path']}")
            print(f"  User Agent: {your_request['user_agent']}")
            print(f"  Detected IP: {result.get('source_ip', 'N/A')}")
            print(f"  Anomaly: {result.get('is_anomaly', 'N/A')}")
            print(f"  Confidence: {result.get('confidence', 0):.3f}")
            print(f"  Attack Type: {result.get('attack_type', 'N/A')}")
            
            if result.get('is_anomaly'):
                print("  ⚠️  Your traffic flagged as suspicious!")
            else:
                print("  ✅ Your traffic is safe")
        else:
            print(f"Backend Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

def check_backend_status():
    """Check if backend is running"""
    
    backend_url = "https://cognitive-cyber-defense.onrender.com"
    
    print("Checking Backend Status")
    print("=" * 25)
    
    try:
        # Check health
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data.get('status')}")
            print(f"✅ Service: {data.get('service')}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            
        # Check main endpoint
        response = requests.get(f"{backend_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Main Endpoint: {data.get('message')}")
            print(f"✅ Version: {data.get('version')}")
        else:
            print(f"❌ Main Endpoint Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Backend Connection Failed: {e}")
        print("Make sure your Render backend is deployed and running")

if __name__ == "__main__":
    print("nitedu.in Traffic Monitor")
    print("=" * 30)
    
    # Check backend first
    check_backend_status()
    
    print("\nOptions:")
    print("1. Monitor continuous traffic")
    print("2. Test your IP/browser")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        monitor_traffic()
    elif choice == "2":
        test_your_ip()
    else:
        print("Exiting...")