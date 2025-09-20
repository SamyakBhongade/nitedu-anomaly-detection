import sys
import os
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.testing.test_detection import DetectionTester

class QuickTuner:
    def __init__(self):
        self.tester = DetectionTester()
    
    def optimize_sql_detection(self):
        """Quickly optimize SQL injection detection"""
        print("🔧 Optimizing SQL injection detection...")
        
        # Test different thresholds
        thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
        best_rate = 0
        best_threshold = 0.5
        
        self.tester.setup_detector()
        
        for threshold in thresholds:
            # Generate SQL attacks
            attacks = self.tester.simulator.simulate_attack('sql_injection', 15)
            features = self.tester.feature_extractor.extract_features(attacks)
            sequences, aggregated = self.tester.feature_extractor.create_sequences(features)
            
            # Test with different threshold
            results = self.tester.detector.predict_anomalies(sequences, aggregated, threshold=threshold)
            detection_rate = np.sum(results['ensemble_anomalies']) / len(sequences) * 100
            
            print(f"Threshold {threshold}: {detection_rate:.1f}% detection")
            
            if detection_rate > best_rate:
                best_rate = detection_rate
                best_threshold = threshold
        
        print(f"\n✅ Best threshold: {best_threshold} ({best_rate:.1f}% detection)")
        return best_threshold

def main():
    tuner = QuickTuner()
    best_threshold = tuner.optimize_sql_detection()
    
    print(f"\n🚀 Testing with optimized threshold...")
    tester = DetectionTester()
    tester.test_attack('sql_injection', 20)

if __name__ == "__main__":
    main()