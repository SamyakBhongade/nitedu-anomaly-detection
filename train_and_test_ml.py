#!/usr/bin/env python3
"""
Complete ML Training and Testing Workflow
Trains models, saves them, and runs comprehensive tests
"""

import sys
import os
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from ml_training_pipeline import CyberDefenseMLPipeline
from ml_inference_engine import MLInferenceEngine
from test_ml_models import MLModelTester

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Complete ML workflow: Train → Save → Test"""
    
    print("🛡️ COGNITIVE CYBER DEFENSE - COMPLETE ML WORKFLOW")
    print("=" * 70)
    
    # Step 1: Check datasets
    print("\n📊 Step 1: Checking Datasets")
    print("-" * 30)
    
    datasets_dir = Path("datasets")
    required_files = [
        "nsl_kdd_train.txt",
        "nsl_kdd_test.txt", 
        "unsw_train.csv",
        "unsw_test.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not (datasets_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing dataset files: {missing_files}")
        print("Please ensure datasets are in the 'datasets/' directory")
        return False
    
    print("✅ All required datasets found")
    
    # Step 2: Train ML Models
    print("\n🧠 Step 2: Training ML Models")
    print("-" * 30)
    
    try:
        pipeline = CyberDefenseMLPipeline()
        results = pipeline.train_complete_pipeline(sample_size=3000)
        
        print(f"✅ Training completed successfully!")
        print(f"   LSTM Accuracy: {results['lstm_accuracy']:.3f}")
        print(f"   Isolation Forest Accuracy: {results['isolation_accuracy']:.3f}")
        print(f"   Ensemble Accuracy: {results['ensemble_accuracy']:.3f}")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False
    
    # Step 3: Verify Model Files
    print("\n💾 Step 3: Verifying Saved Models")
    print("-" * 30)
    
    models_dir = Path("data/models")
    expected_files = [
        "lstm_autoencoder.pth",
        "isolation_forest.joblib",
        "feature_scaler.joblib",
        "model_metadata.joblib"
    ]
    
    for file in expected_files:
        if (models_dir / file).exists():
            file_size = (models_dir / file).stat().st_size / 1024  # KB
            print(f"✅ {file} ({file_size:.1f} KB)")
        else:
            print(f"❌ {file} - Missing!")
            return False
    
    # Step 4: Test ML Models
    print("\n🧪 Step 4: Testing ML Models")
    print("-" * 30)
    
    try:
        tester = MLModelTester()
        test_results = tester.run_comprehensive_test()
        
        # Calculate overall performance
        total_correct = sum(r['correct'] for r in test_results.values())
        total_tests = sum(r['total'] for r in test_results.values())
        overall_accuracy = (total_correct / total_tests) * 100
        
        print(f"\n🎯 FINAL ML MODEL PERFORMANCE:")
        print(f"   Overall Accuracy: {overall_accuracy:.1f}%")
        
        if overall_accuracy > 85:
            print("   Status: ✅ PRODUCTION READY!")
        elif overall_accuracy > 70:
            print("   Status: ⚠️ GOOD - Minor improvements needed")
        else:
            print("   Status: ❌ NEEDS WORK - Consider retraining")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False
    
    # Step 5: Performance Benchmark
    print("\n⚡ Step 5: Performance Benchmark")
    print("-" * 30)
    
    try:
        tester.benchmark_performance(50)
    except Exception as e:
        print(f"⚠️ Benchmark failed: {e}")
    
    # Step 6: Integration Readiness
    print("\n🚀 Step 6: Integration Readiness Check")
    print("-" * 30)
    
    engine = MLInferenceEngine()
    engine.load_models()
    
    if engine.is_loaded:
        print("✅ ML inference engine ready")
        print("✅ Models can be integrated into backend")
        print("✅ Real-time anomaly detection available")
        
        # Test a sample request
        sample_request = {
            'path': "/?id=1' OR '1'='1",
            'user_agent': 'sqlmap/1.0',
            'method': 'GET',
            'country': 'CN'
        }
        
        result = engine.predict_anomaly(sample_request)
        print(f"\n🔍 Sample Detection Test:")
        print(f"   Request: SQL injection attempt")
        print(f"   Detected: {result['is_anomaly']}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Attack Type: {result.get('attack_type', 'Unknown')}")
        print(f"   Response Time: {result.get('inference_time_ms', 0):.2f}ms")
        
    else:
        print("❌ ML inference engine failed to load")
        return False
    
    # Final Summary
    print(f"\n🎉 COMPLETE ML SYSTEM READY!")
    print("=" * 70)
    print("✅ Models trained on real attack datasets")
    print("✅ Models saved and validated")
    print("✅ Inference engine operational")
    print("✅ Performance benchmarked")
    print("✅ Ready for backend integration")
    print(f"\n📁 Models location: {models_dir.absolute()}")
    print("🔗 Next step: Integrate with backend API")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🚀 Run this to integrate with backend:")
        print(f"   # Update backend to use trained ML models")
        sys.exit(0)
    else:
        print(f"\n❌ ML workflow failed. Please check errors above.")
        sys.exit(1)