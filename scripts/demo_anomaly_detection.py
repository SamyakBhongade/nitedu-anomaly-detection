#!/usr/bin/env python3
"""
Demo script showing the anomaly detection system in action
"""
import sys
import os
from pathlib import Path
import time
import json

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from ml.training.train_hybrid_model import HybridModelTrainer
from ml.inference.real_time_detector import RealTimeAnomalyDetector
from ml.training.synthetic_data_generator import SyntheticNetworkDataGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_models():
    """Setup and train models if they don't exist"""
    models_dir = Path("data/models")
    lstm_path = models_dir / "lstm_autoencoder.pth"
    isolation_path = models_dir / "isolation_forest.joblib"
    
    if not (lstm_path.exists() and isolation_path.exists()):
        logger.info("🔧 Models not found. Training new models...")
        trainer = HybridModelTrainer()
        trainer.train_model(normal_samples=1000, anomaly_samples=50)
        logger.info("✅ Model training completed")
    else:
        logger.info("✅ Using existing trained models")
    
    return str(lstm_path), str(isolation_path)

def simulate_real_time_detection():
    """Simulate real-time anomaly detection"""
    logger.info("🚀 Starting real-time anomaly detection simulation...")
    
    # Setup models
    lstm_path, isolation_path = setup_models()
    
    # Initialize detector
    detector = RealTimeAnomalyDetector(lstm_path, isolation_path, sequence_length=5)
    
    # Generate streaming events
    data_gen = SyntheticNetworkDataGenerator()
    
    logger.info("📡 Simulating network traffic stream...")
    logger.info("=" * 80)
    
    # Mix of normal and anomalous events
    normal_events = data_gen.generate_normal_traffic(30)
    anomaly_events = data_gen.generate_anomalous_traffic(8)
    
    # Interleave events to simulate real stream
    all_events = []
    for i in range(max(len(normal_events), len(anomaly_events))):
        if i < len(normal_events):
            all_events.append(normal_events[i])
        if i < len(anomaly_events) and i % 4 == 0:  # Insert anomalies occasionally
            all_events.append(anomaly_events[i // 4])
    
    # Process events in real-time simulation
    anomaly_count = 0
    total_events = 0
    
    for i, event in enumerate(all_events):
        event['id'] = f"event_{i:04d}"
        
        # Process event
        result = detector.process_event(event)
        total_events += 1
        
        # Display result
        if result['is_anomaly']:
            anomaly_count += 1
            logger.warning(f"🚨 ANOMALY DETECTED - Event {result['event_id']}")
            logger.warning(f"   Score: {result['anomaly_score']:.3f} | Confidence: {result['confidence']:.3f}")
            logger.warning(f"   Reason: {result['reason']}")
            logger.warning(f"   Details: {result['event_details']['src_ip']} -> "
                          f"{result['event_details']['dst_ip']}:{result['event_details']['dst_port']} "
                          f"({result['event_details']['protocol']})")
            print()
        else:
            logger.info(f"✅ Normal - Event {result['event_id']} | Score: {result['anomaly_score']:.3f}")
        
        # Simulate real-time delay
        time.sleep(0.1)
    
    logger.info("=" * 80)
    logger.info(f"📊 DETECTION SUMMARY:")
    logger.info(f"   Total Events Processed: {total_events}")
    logger.info(f"   Anomalies Detected: {anomaly_count}")
    logger.info(f"   Detection Rate: {anomaly_count/total_events:.1%}")
    
    # Buffer stats
    stats = detector.get_buffer_stats()
    logger.info(f"   Buffer Status: {stats['buffer_size']}/{stats['max_buffer_size']} events")

def demonstrate_model_components():
    """Demonstrate individual model components"""
    logger.info("🔬 Demonstrating model components...")
    
    # Generate test data
    data_gen = SyntheticNetworkDataGenerator()
    events, labels = data_gen.generate_mixed_dataset(100, 10)
    
    logger.info(f"📊 Test Dataset: {len(events)} events ({sum(labels)} anomalies)")
    
    # Show sample events
    logger.info("\n📋 Sample Events:")
    for i, (event, label) in enumerate(zip(events[:5], labels[:5])):
        status = "ANOMALY" if label else "NORMAL"
        logger.info(f"   Event {i+1} [{status}]: {event['src_ip']} -> "
                   f"{event['dst_ip']}:{event['dst_port']} "
                   f"({event['packet_count']} packets, {event['byte_count']} bytes)")

def main():
    """Main demo function"""
    logger.info("🎯 Cognitive Cyber Defense - Anomaly Detection Demo")
    logger.info("=" * 60)
    
    # Create directories
    Path("data/models").mkdir(parents=True, exist_ok=True)
    
    try:
        # Demonstrate components
        demonstrate_model_components()
        
        print("\n" + "=" * 60)
        input("Press Enter to start real-time detection simulation...")
        print()
        
        # Run real-time simulation
        simulate_real_time_detection()
        
        logger.info("\n🎉 Demo completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"\n💥 Demo failed: {e}")
        raise

if __name__ == "__main__":
    main()