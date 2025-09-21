#!/usr/bin/env python3
"""
Simple test for advanced models
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from advanced_inference_engine import AdvancedInferenceEngine

def test_advanced_models():
    """Test advanced models"""
    
    print("Testing Advanced ML Models")
    print("=" * 40)
    
    # Initialize engine
    engine = AdvancedInferenceEngine()
    
    if not engine.load_models():
        print("Failed to load advanced models")
        return False
    
    # Test cases
    test_cases = [
        {
            'name': 'Normal Request',
            'data': {
                'path': '/',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'method': 'GET',
                'country': 'US',
                'ip': '192.168.1.100',
                'timestamp': 1640995200
            }
        },
        {
            'name': 'SQL Injection',
            'data': {
                'path': "/?id=1' UNION SELECT * FROM users--",
                'user_agent': 'sqlmap/1.6.12',
                'method': 'POST',
                'country': 'CN',
                'ip': '10.0.0.50',
                'timestamp': 1640995260
            }
        },
        {
            'name': 'XSS Attack',
            'data': {
                'path': '/search?q=<script>alert("XSS")</script>',
                'user_agent': 'Mozilla/5.0',
                'method': 'GET',
                'country': 'RU',
                'ip': '172.16.1.10',
                'timestamp': 1640995320
            }
        }
    ]
    
    print(f"\nTesting {len(test_cases)} cases...")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{i+1}. {test_case['name']}")
        
        result = engine.predict_anomaly(test_case['data'])
        
        if 'error' in result:
            print(f"   Error: {result['error']}")
            continue
        
        print(f"   Anomaly: {result['is_anomaly']}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Risk Score: {result['risk_score']:.3f}")
        print(f"   Attack Type: {result['attack_type']}")
        print(f"   Inference Time: {result['inference_time_ms']:.2f}ms")
        
        print(f"   Model Scores:")
        for model, score in result['model_scores'].items():
            print(f"     {model}: {score:.3f}")
    
    # Performance stats
    print(f"\nPerformance Statistics:")
    stats = engine.get_performance_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print(f"\nAdvanced model testing completed!")
    return True

if __name__ == "__main__":
    test_advanced_models()