import sys
import os
import numpy as np
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.testing.attack_simulator import AttackSimulator
from ml.preprocessing.feature_extractor import NetworkFeatureExtractor
from ml.training.synthetic_data_generator import SyntheticNetworkDataGenerator

class EnhancedDetector:
    def __init__(self):
        self.simulator = AttackSimulator()
        self.feature_extractor = NetworkFeatureExtractor()
        self.data_generator = SyntheticNetworkDataGenerator()
        self.thresholds = {
            'sql_injection': 0.3,
            'xss_attack': 0.25,
            'ddos_attack': 0.2,
            'bot_scraping': 0.35,
            'brute_force': 0.3
        }
    
    def detect_attack(self, events, attack_type='unknown'):
        """Enhanced rule-based detection with ML backup"""
        features = self.feature_extractor.extract_features(events)
        
        detections = []
        for i, event in enumerate(events):
            score = 0.0
            
            # Rule-based detection
            if attack_type == 'sql_injection':
                score = self._detect_sql_injection(event)
            elif attack_type == 'xss_attack':
                score = self._detect_xss(event)
            elif attack_type == 'ddos_attack':
                score = self._detect_ddos(event)
            elif attack_type == 'bot_scraping':
                score = self._detect_bot(event)
            elif attack_type == 'brute_force':
                score = self._detect_brute_force(event)
            else:
                # General anomaly detection
                score = self._general_anomaly_score(event)
            
            # Add feature-based score
            if i < len(features):
                feature_score = self._calculate_feature_anomaly(features[i])
                score = max(score, feature_score)
            
            detections.append(score > self.thresholds.get(attack_type, 0.5))
        
        return detections, [self._calculate_feature_anomaly(f) for f in features]
    
    def _detect_sql_injection(self, event):
        path = event.get('path', '').lower()
        sql_keywords = ['union', 'select', 'drop', 'insert', 'delete', 'update', 'exec', 'or 1=1', "' or '", '--', ';']
        score = sum(1 for keyword in sql_keywords if keyword in path)
        return min(score / len(sql_keywords), 1.0)
    
    def _detect_xss(self, event):
        path = event.get('path', '').lower()
        xss_keywords = ['<script', 'javascript:', 'onerror=', 'onload=', 'alert(', 'document.cookie', '<iframe', '<object']
        score = sum(1 for keyword in xss_keywords if keyword in path)
        return min(score / len(xss_keywords), 1.0)
    
    def _detect_ddos(self, event):
        score = 0.0
        if event.get('packet_count', 0) > 100:
            score += 0.4
        if event.get('byte_count', 0) > 10000:
            score += 0.3
        if event.get('duration', 1) < 0.1:
            score += 0.3
        return min(score, 1.0)
    
    def _detect_bot(self, event):
        ua = event.get('user_agent', '').lower()
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python', 'java']
        score = sum(1 for indicator in bot_indicators if indicator in ua)
        return min(score / len(bot_indicators), 1.0)
    
    def _detect_brute_force(self, event):
        score = 0.0
        if event.get('method') == 'POST' and '/login' in event.get('path', ''):
            score += 0.5
        if event.get('country') in ['RU', 'CN', 'KP']:
            score += 0.3
        if event.get('duration', 0) < 1.0:
            score += 0.2
        return min(score, 1.0)
    
    def _general_anomaly_score(self, event):
        score = 0.0
        # High traffic
        if event.get('packet_count', 0) > 50:
            score += 0.2
        # Suspicious countries
        if event.get('country') in ['RU', 'CN', 'KP', 'IR']:
            score += 0.3
        # Suspicious paths
        path = event.get('path', '').lower()
        if any(x in path for x in ['admin', 'wp-', 'phpmyadmin', '..', '<', 'script']):
            score += 0.4
        return min(score, 1.0)
    
    def _calculate_feature_anomaly(self, features):
        # Simple threshold-based anomaly detection
        anomaly_score = 0.0
        
        # Check each feature for anomalies
        if len(features) >= 15:  # Ensure we have all features
            # High SQL injection score
            if features[10] > 0.1:
                anomaly_score += 0.4
            # High XSS score  
            if features[11] > 0.1:
                anomaly_score += 0.4
            # High DDoS score
            if features[12] > 0.3:
                anomaly_score += 0.5
            # High bot score
            if features[13] > 0.3:
                anomaly_score += 0.3
        
        return min(anomaly_score, 1.0)

def test_enhanced_detection():
    detector = EnhancedDetector()
    simulator = AttackSimulator()
    
    print("🛡️ ENHANCED DETECTION TESTING")
    print("=" * 40)
    
    attack_types = ['sql_injection', 'xss_attack', 'ddos_attack', 'bot_scraping', 'brute_force']
    
    for attack_type in attack_types:
        print(f"\n🚨 Testing {attack_type.replace('_', ' ').title()}")
        
        # Generate attacks
        attacks = simulator.simulate_attack(attack_type, 20)
        
        # Detect with enhanced method
        detections, scores = detector.detect_attack(attacks, attack_type)
        
        detection_rate = sum(detections) / len(detections) * 100
        avg_score = np.mean(scores)
        
        print(f"   Detection Rate: {detection_rate:.1f}%")
        print(f"   Average Score: {avg_score:.3f}")
        
        if detection_rate > 80:
            print("   Status: ✅ EXCELLENT")
        elif detection_rate > 60:
            print("   Status: ⚠️ GOOD")
        else:
            print("   Status: ❌ NEEDS WORK")

if __name__ == "__main__":
    test_enhanced_detection()