#!/usr/bin/env python3
"""
Test Cloudflare Worker ML Integration
"""
import requests

def test_cloudflare_ml():
    """Test Cloudflare Worker with ML backend"""
    
    # Your Cloudflare Worker URL
    worker_url = "https://nitedu-protection.your-subdomain.workers.dev"
    
    print("Testing Cloudflare Worker ML Integration")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Normal Request",
            "url": f"{worker_url}/",
            "headers": {"User-Agent": "Mozilla/5.0"}
        },
        {
            "name": "SQL Injection Attack",
            "url": f"{worker_url}/login?id=1' UNION SELECT * FROM users--",
            "headers": {"User-Agent": "sqlmap/1.0"}
        },
        {
            "name": "XSS Attack", 
            "url": f"{worker_url}/search?q=<script>alert('XSS')</script>",
            "headers": {"User-Agent": "Mozilla/5.0"}
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        try:
            response = requests.get(
                test['url'],
                headers=test['headers'],
                timeout=10
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 403:
                print("  Result: BLOCKED (Attack detected)")
                if "ML" in response.text or "advanced" in response.text.lower():
                    print("  Method: ML Detection")
                else:
                    print("  Method: Fallback Rules")
            elif response.status_code == 200:
                print("  Result: ALLOWED (Safe traffic)")
            else:
                print(f"  Result: Unexpected ({response.status_code})")
                
            # Check response headers for ML info
            if 'X-ML-Confidence' in response.headers:
                print(f"  ML Confidence: {response.headers['X-ML-Confidence']}")
            if 'X-Blocked-Reason' in response.headers:
                print(f"  Block Reason: {response.headers['X-Blocked-Reason']}")
                
        except Exception as e:
            print(f"  Failed: {e}")

if __name__ == "__main__":
    test_cloudflare_ml()