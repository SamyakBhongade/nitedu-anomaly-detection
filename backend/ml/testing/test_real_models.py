import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.testing.attack_simulator import AttackSimulator
from ml.training.real_data_trainer import RealDataTrainer
from ml.preprocessing.feature_extractor import NetworkFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_data_models():
    """Test models trained on real datasets"""
    print("🛡️ TESTING REAL DATA TRAINED MODELS")
    print("=" * 50)
    
    # Train model on real data
    trainer = RealDataTrainer()
    detector = trainer.train_on_real_data(sample_size=2000)
    
    # Test with simulated attacks
    simulator = AttackSimulator()
    extractor = NetworkFeatureExtractor()
    
    attack_types = ['sql_injection', 'xss_attack', 'ddos_attack', 'bot_scraping', 'brute_force']
    
    print("\n🚨 ATTACK DETECTION RESULTS:")
    
    for attack_type in attack_types:
        # Generate attacks
        attacks = simulator.simulate_attack(attack_type, 20)
        
        # Extract features and detect
        features = extractor.extract_features(attacks)
        sequences, aggregated = extractor.create_sequences(features)
        
        results = detector.predict_anomalies(sequences, aggregated, threshold=0.4)
        
        detection_rate = sum(results['ensemble_anomalies']) / len(results['ensemble_anomalies']) * 100
        avg_score = sum(results['ensemble_scores']) / len(results['ensemble_scores'])
        
        status = "✅ EXCELLENT" if detection_rate > 80 else "⚠️ GOOD" if detection_rate > 60 else "❌ POOR"
        
        print(f"  {attack_type.replace('_', ' ').title()}: {detection_rate:.1f}% (Score: {avg_score:.3f}) {status}")
    
    print("\n🎯 Real data models are now active!")

if __name__ == "__main__":
    test_real_data_models()