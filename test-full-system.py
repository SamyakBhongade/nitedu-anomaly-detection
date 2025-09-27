#!/usr/bin/env python3
"""
Test Full System - Backend + Cloudflare Integration
"""

import requests
import json

def test_backend_direct():
    """Test Render backend directly"""
    print("🔧 Testing Backend (Direct)")
    print("-" * 30)
    
    backend_url = "https://nitedu-anomaly-detection-6w4v.onrender.com"
    
    tests = [
        {
            "name": "Normal Request",
            "data": {"path": "/", "user_agent": "Mozilla/5.0", "method": "GET"},
            "expect_anomaly": False
        },
        {
            "name": "SQL Injection",
            "data": {"path": "/login?id=1' OR '1'='1", "user_agent": "Mozilla/5.0", "method": "POST"},
            "expect_anomaly": True
        }
    ]
    
    backend_working = True
    
    for test in tests:
        try:
            response = requests.post(f"{backend_url}/api/v1/predict", json=test["data"], timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {test['name']}: {result.get('method', 'unknown')}")
                print(f"   Anomaly: {result.get('is_anomaly')} | Confidence: {result.get('confidence', 0):.3f}")
            else:
                print(f"❌ {test['name']}: HTTP {response.status_code}")
                backend_working = False
                
        except Exception as e:
            print(f"❌ {test['name']}: {e}")
            backend_working = False
    
    return backend_working

def test_cloudflare_protection():
    """Test Cloudflare Worker protection"""
    print(f"\n🌐 Testing Cloudflare Protection")
    print("-" * 30)
    
    tests = [
        {
            "url": "https://nitedu.in/",
            "name": "Normal Traffic",
            "expect_blocked": False
        },
        {
            "url": "https://nitedu.in/?id=1' OR '1'='1",
            "name": "SQL Injection",
            "expect_blocked": True
        },
        {
            "url": "https://nitedu.in/search?q=<script>alert('xss')</script>",
            "name": "XSS Attack",
            "expect_blocked": True
        }
    ]
    
    cloudflare_working = True
    
    for test in tests:
        try:
            response = requests.get(test["url"], timeout=10)
            
            if "Access Blocked" in response.text:
                result = "BLOCKED"
                working = test["expect_blocked"]
            elif "Access Granted" in response.text:
                result = "ALLOWED"
                working = not test["expect_blocked"]
            else:
                result = f"HTTP {response.status_code}"
                working = False
            
            status = "✅" if working else "❌"
            print(f"{status} {test['name']}: {result}")
            
            if not working:
                cloudflare_working = False
                
        except Exception as e:
            print(f"❌ {test['name']}: {e}")
            cloudflare_working = False
    
    return cloudflare_working

def main():
    print("🛡️ Full System Test - nitedu.in Protection")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend_direct()
    
    # Test Cloudflare
    cloudflare_ok = test_cloudflare_protection()
    
    # Summary
    print(f"\n📊 System Status")
    print("=" * 20)
    print(f"Backend (Render): {'✅ Working' if backend_ok else '❌ Failed'}")
    print(f"Protection (Cloudflare): {'✅ Working' if cloudflare_ok else '❌ Failed'}")
    
    if backend_ok and cloudflare_ok:
        print(f"\n🚀 System Fully Operational!")
        print(f"   nitedu.in is protected by advanced ML detection")
    elif backend_ok:
        print(f"\n⚠️  Backend working, but Cloudflare needs fixing")
    elif cloudflare_ok:
        print(f"\n⚠️  Cloudflare working, but backend needs fixing")
    else:
        print(f"\n❌ Both systems need attention")

if __name__ == "__main__":
    main()