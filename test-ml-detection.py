#!/usr/bin/env python3
"""
Test ML Model Detection - Verify advanced ML is working
"""

import requests
import json

def test_ml_detection():
    backend_url = "https://nitedu-anomaly-detection-6w4v.onrender.com"
    
    test_cases = [
        # Normal requests (should be safe)
        {
            "name": "Normal Homepage",
            "data": {
                "path": "/",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "method": "GET",
                "client_ip": "192.168.1.100",
                "country": "US"
            },
            "expected_anomaly": False
        },
        
        # SQL Injection attacks
        {
            "name": "SQL Injection - UNION",
            "data": {
                "path": "/login?id=1' UNION SELECT * FROM users--",
                "user_agent": "Mozilla/5.0",
                "method": "POST",
                "client_ip": "10.0.0.1",
                "country": "CN"
            },
            "expected_anomaly": True
        },
        
        {
            "name": "SQL Injection - OR bypass",
            "data": {
                "path": "/admin?user=admin&pass=1' OR '1'='1",
                "user_agent": "Mozilla/5.0",
                "method": "POST",
                "client_ip": "172.16.1.1",
                "country": "RU"
            },
            "expected_anomaly": True
        },
        
        # XSS attacks
        {
            "name": "XSS Attack",
            "data": {
                "path": "/search?q=<script>alert('XSS')</script>",
                "user_agent": "Mozilla/5.0",
                "method": "GET",
                "client_ip": "203.0.113.1",
                "country": "CN"
            },
            "expected_anomaly": True
        },
        
        # Bot/Scanner attacks
        {
            "name": "SQLMap Scanner",
            "data": {
                "path": "/vulnerable.php?id=1",
                "user_agent": "sqlmap/1.6.12#stable (http://sqlmap.org)",
                "method": "GET",
                "client_ip": "198.51.100.1",
                "country": "RU"
            },
            "expected_anomaly": True
        },
        
        # Command Injection
        {
            "name": "Command Injection",
            "data": {
                "path": "/exec?cmd=ls; cat /etc/passwd",
                "user_agent": "curl/7.68.0",
                "method": "POST",
                "client_ip": "203.0.113.50",
                "country": "KP"
            },
            "expected_anomaly": True
        }
    ]
    
    print("🧪 Testing ML Model Detection")
    print("=" * 50)
    
    ml_working = False
    correct_detections = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_tests}] {test_case['name']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{backend_url}/api/v1/predict",
                json=test_case['data'],
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if ML is working
                if result.get('method') == 'advanced_ml':
                    ml_working = True
                    print("✅ ML Detection: ACTIVE")
                else:
                    print("⚠️  Fallback Detection: ACTIVE")
                
                # Display results
                is_anomaly = result.get('is_anomaly', False)
                confidence = result.get('confidence', 0)
                attack_type = result.get('attack_type', 'Unknown')
                
                print(f"   Anomaly: {is_anomaly}")
                print(f"   Confidence: {confidence:.3f}")
                print(f"   Attack Type: {attack_type}")
                print(f"   Method: {result.get('method', 'unknown')}")
                
                # Check if detection is correct
                if is_anomaly == test_case['expected_anomaly']:
                    print("✅ Detection: CORRECT")
                    correct_detections += 1
                else:
                    print("❌ Detection: INCORRECT")
                
                # Show model scores if available
                if 'model_scores' in result:
                    print("   Model Scores:")
                    for model, score in result['model_scores'].items():
                        print(f"     {model}: {score:.3f}")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request Error: {e}")
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    print(f"ML Detection Active: {'✅ YES' if ml_working else '❌ NO (Fallback)'}")
    print(f"Correct Detections: {correct_detections}/{total_tests}")
    print(f"Accuracy: {(correct_detections/total_tests)*100:.1f}%")
    
    if ml_working and correct_detections >= total_tests * 0.8:
        print(f"\n🚀 ML Detection Working Perfectly!")
        print(f"   Advanced models are active and detecting threats")
    elif ml_working:
        print(f"\n⚠️  ML Active but some detection issues")
        print(f"   Check model thresholds or feature extraction")
    else:
        print(f"\n❌ ML Models Not Loading - Using Fallback")
        print(f"   Check model files and dependencies")

def test_cloudflare_integration():
    """Test the full Cloudflare + Render integration"""
    print(f"\n🌐 Testing Cloudflare Integration")
    print("=" * 40)
    
    test_urls = [
        ("https://nitedu.in/", "Normal traffic"),
        ("https://nitedu.in/?id=1' OR '1'='1", "SQL Injection")
    ]
    
    for url, description in test_urls:
        print(f"\n🔗 Testing: {description}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if "Access Blocked" in response.text:
                print("   Result: ✅ BLOCKED (Threat detected)")
            elif "Access Granted" in response.text:
                print("   Result: ✅ ALLOWED (Safe traffic)")
            else:
                print("   Result: ⚠️  Unknown response")
                
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_ml_detection()
    test_cloudflare_integration()