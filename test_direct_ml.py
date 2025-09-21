#!/usr/bin/env python3
"""
Direct ML Test - Test ML models directly
"""
import sys
import os

# Add current directory to path
sys.path.append('.')

def test_direct_ml():
    """Test ML models directly"""
    print("Direct ML Model Test")
    print("=" * 30)
    
    try:
        from advanced_inference_engine import AdvancedInferenceEngine
        
        # Initialize engine
        model_dir = "data/models"
        engine = AdvancedInferenceEngine(model_dir)
        
        print(f"Engine initialized: {engine}")
        
        # Load models
        success = engine.load_models()
        print(f"Models loaded: {success}")
        print(f"Is loaded: {engine.is_loaded}")
        
        if success and engine.is_loaded:
            print("[OK] ML models loaded successfully!")
            
            # Test prediction
            test_data = {
                'path': '/login?id=1\' OR \'1\'=\'1\'--',
                'user_agent': 'sqlmap/1.0',
                'method': 'POST',
                'client_ip': '10.0.0.50'
            }
            
            print(f"\nTesting prediction with: {test_data['path']}")
            result = engine.predict_anomaly(test_data)
            
            print(f"Result: {result}")
            
            if 'error' not in result:
                print(f"[OK] Prediction successful!")
                print(f"  Anomaly: {result.get('is_anomaly')}")
                print(f"  Confidence: {result.get('confidence', 0):.3f}")
                print(f"  Attack Type: {result.get('attack_type')}")
                print(f"  Risk Score: {result.get('risk_score', 0):.3f}")
            else:
                print(f"[ERROR] Prediction failed: {result['error']}")
        else:
            print("[ERROR] Failed to load ML models")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_ml()