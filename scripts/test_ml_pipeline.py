#!/usr/bin/env python3
"""
Test script for the ML anomaly detection pipeline
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from ml.training.train_hybrid_model import HybridModelTrainer
from ml.inference.real_time_detector import RealTimeAnomalyDetector
from ml.training.synthetic_data_generator import SyntheticNetworkDataGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_training_pipeline():
    """Test the training pipeline"""
    logger.info("Testing ML training pipeline...")
    
    try:
        trainer = HybridModelTrainer()
        detector = trainer.train_model(
            normal_samples=500,  # Smaller dataset for testing
            anomaly_samples=25,
            sequence_length=5
        )
        logger.info("✅ Training pipeline test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Training pipeline test failed: {e}")
        return False

def test_inference_pipeline():
    """Test the inference pipeline"""
    logger.info("Testing ML inference pipeline...")
    
    try:
        # First ensure models exist
        models_dir = Path("data/models")
        lstm_path = models_dir / "lstm_autoencoder.pth"
        isolation_path = models_dir / "isolation_forest.joblib"
        
        if not (lstm_path.exists() and isolation_path.exists()):
            logger.warning("Models not found, running training first...")
            if not test_training_pipeline():
                return False
        
        # Test real-time detector
        detector = RealTimeAnomalyDetector(
            str(lstm_path), 
            str(isolation_path),
            sequence_length=5
        )
        
        # Generate test events
        data_gen = SyntheticNetworkDataGenerator()
        test_events = data_gen.generate_normal_traffic(20)
        anomaly_events = data_gen.generate_anomalous_traffic(5)
        
        # Process events
        results = []
        for event in test_events + anomaly_events:
            result = detector.process_event(event)
            results.append(result)
        
        # Check results
        anomaly_count = sum(1 for r in results if r['is_anomaly'])
        logger.info(f"Processed {len(results)} events, detected {anomaly_count} anomalies")
        
        logger.info("✅ Inference pipeline test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Inference pipeline test failed: {e}")
        return False

def test_synthetic_data_generation():
    """Test synthetic data generation"""
    logger.info("Testing synthetic data generation...")
    
    try:
        generator = SyntheticNetworkDataGenerator()
        
        # Test normal traffic
        normal_events = generator.generate_normal_traffic(100)
        logger.info(f"Generated {len(normal_events)} normal events")
        
        # Test anomalous traffic
        anomaly_events = generator.generate_anomalous_traffic(10)
        logger.info(f"Generated {len(anomaly_events)} anomalous events")
        
        # Test mixed dataset
        mixed_events, labels = generator.generate_mixed_dataset(200, 20)
        anomaly_ratio = sum(labels) / len(labels)
        logger.info(f"Mixed dataset: {len(mixed_events)} events, {anomaly_ratio:.2%} anomalies")
        
        logger.info("✅ Synthetic data generation test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Synthetic data generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting ML pipeline tests...")
    
    # Create data directories
    Path("data/models").mkdir(parents=True, exist_ok=True)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    tests = [
        ("Synthetic Data Generation", test_synthetic_data_generation),
        ("Training Pipeline", test_training_pipeline),
        ("Inference Pipeline", test_inference_pipeline)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        logger.info("\n🎉 All tests passed! ML pipeline is ready.")
    else:
        logger.error("\n💥 Some tests failed. Check the logs above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)