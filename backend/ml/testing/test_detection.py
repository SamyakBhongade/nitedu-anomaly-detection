import sys
import os
import numpy as np
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.testing.attack_simulator import AttackSimulator
from ml.preprocessing.feature_extractor import NetworkFeatureExtractor
from ml.models.ensemble_detector import EnsembleAnomalyDetector
from ml.training.synthetic_data_generator import SyntheticNetworkDataGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetectionTester:
    def __init__(self):
        self.simulator = AttackSimulator()
        self.feature_extractor = NetworkFeatureExtractor()
        self.data_generator = SyntheticNetworkDataGenerator()
        self.detector = None
    
    def setup_detector(self):
        """Train a quick detector for testing"""
        logger.info("Setting up detector...")
        
        # Generate normal training data
        normal_events, _ = self.data_generator.generate_mixed_dataset(500, 0)
        features = self.feature_extractor.extract_features(normal_events)
        sequences, aggregated = self.feature_extractor.create_sequences(features)
        
        # Train ensemble
        self.detector = EnsembleAnomalyDetector(
            sequence_length=10, 
            feature_dim=features.shape[1]
        )
        self.detector.fit(sequences, aggregated)
        logger.info("Detector ready!")
    
    def test_attack(self, attack_type: str, intensity: int = 20):
        """Test specific attack type"""
        if not self.detector:
            self.setup_detector()
        
        logger.info(f"\n🚨 TESTING {attack_type.upper()} ATTACK")
        
        # Generate attack
        attack_events = self.simulator.simulate_attack(attack_type, intensity)
        
        # Extract features
        features = self.feature_extractor.extract_features(attack_events)
        sequences, aggregated = self.feature_extractor.create_sequences(features)
        
        # Detect anomalies
        results = self.detector.predict_anomalies(sequences, aggregated, threshold=0.4)
        
        # Analyze results
        anomaly_count = np.sum(results['ensemble_anomalies'])
        detection_rate = anomaly_count / len(sequences) * 100
        
        logger.info(f"📊 RESULTS:")
        logger.info(f"   Events tested: {len(sequences)}")
        logger.info(f"   Anomalies detected: {anomaly_count}")
        logger.info(f"   Detection rate: {detection_rate:.1f}%")
        
        # Show individual model scores
        avg_scores = {
            'Ensemble': np.mean(results['ensemble_scores']),
            'Hybrid': np.mean(results['hybrid_scores']),
            'Transformer': np.mean(results['transformer_scores']),
            'Isolation': np.mean(results['isolation_scores'])
        }
        
        logger.info(f"   Average scores:")
        for model, score in avg_scores.items():
            logger.info(f"     {model}: {score:.3f}")
        
        return detection_rate, results
    
    def run_all_tests(self):
        """Run comprehensive attack testing"""
        logger.info("🛡️ STARTING COMPREHENSIVE ATTACK TESTING")
        
        attack_types = ['sql_injection', 'xss_attack', 'ddos_attack', 'bot_scraping', 'brute_force']
        results = {}
        
        for attack_type in attack_types:
            detection_rate, _ = self.test_attack(attack_type, 15)
            results[attack_type] = detection_rate
        
        logger.info(f"\n📈 SUMMARY RESULTS:")
        for attack, rate in results.items():
            status = "✅ GOOD" if rate > 70 else "⚠️ NEEDS IMPROVEMENT" if rate > 40 else "❌ POOR"
            logger.info(f"   {attack}: {rate:.1f}% {status}")
        
        avg_detection = np.mean(list(results.values()))
        logger.info(f"\n🎯 OVERALL DETECTION RATE: {avg_detection:.1f}%")
        
        return results

def main():
    tester = DetectionTester()
    
    # Test individual attack
    print("Testing SQL Injection...")
    tester.test_attack('sql_injection', 10)
    
    # Run all tests
    print("\nRunning comprehensive tests...")
    tester.run_all_tests()

if __name__ == "__main__":
    main()