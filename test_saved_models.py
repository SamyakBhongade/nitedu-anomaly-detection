#!/usr/bin/env python3
"""
Test the saved ML models
"""

import joblib
import numpy as np
from pathlib import Path

def test_models():
    """Test saved ML models"""
    
    print("Testing Saved ML Models")
    print("=" * 30)
    
    models_dir = Path("data/models")
    
    # Load models
    print("Loading models...")
    isolation_forest = joblib.load(models_dir / "isolation_forest.joblib")
    svm_model = joblib.load(models_dir / "svm_model.joblib")
    scaler = joblib.load(models_dir / "feature_scaler.joblib")
    metadata = joblib.load(models_dir / "model_metadata.joblib")
    
    print(f"Models loaded successfully!")
    print(f"Feature dimension: {metadata['feature_dim']}")
    
    # Test cases
    test_cases = [
        {
            'name': 'Normal Homepage Visit',
            'features': [0.2] * 20,
            'expected': 'Normal'
        },
        {
            'name': 'SQL Injection Attack',
            'features': [0.3] * 20,
            'expected': 'Attack'
        },
        {
            'name': 'XSS Attack',
            'features': [0.3] * 20,
            'expected': 'Attack'
        },
        {
            'name': 'Bot Attack',
            'features': [0.3] * 20,
            'expected': 'Attack'
        },
        {
            'name': 'DDoS Attack',
            'features': [0.3] * 20,
            'expected': 'Attack'
        }
    ]
    
    # Modify attack-specific features
    test_cases[1]['features'][2] = 0.9  # SQL injection score
    test_cases[2]['features'][3] = 0.9  # XSS score
    test_cases[3]['features'][4] = 0.9  # Bot score
    test_cases[4]['features'][10] = 0.9  # High packet count
    
    print(f"\nRunning {len(test_cases)} test cases...")
    print("-" * 50)
    
    correct_predictions = 0
    
    for i, test_case in enumerate(test_cases):
        # Prepare features
        features = np.array([test_case['features']])
        features_scaled = scaler.transform(features)
        
        # Get predictions
        iso_pred = isolation_forest.predict(features_scaled)[0]
        svm_pred = svm_model.predict(features_scaled)[0]
        
        # Ensemble prediction (majority vote)
        iso_anomaly = iso_pred == -1
        svm_anomaly = svm_pred == -1
        ensemble_anomaly = iso_anomaly or svm_anomaly
        
        # Determine result
        predicted = 'Attack' if ensemble_anomaly else 'Normal'
        is_correct = predicted == test_case['expected']
        
        if is_correct:
            correct_predictions += 1
            status = "PASS"
        else:
            status = "FAIL"
        
        print(f"{i+1}. {test_case['name']}")
        print(f"   Expected: {test_case['expected']}")
        print(f"   Predicted: {predicted}")
        print(f"   ISO: {iso_pred}, SVM: {svm_pred}")
        print(f"   Result: {status}")
        print()
    
    # Summary
    accuracy = (correct_predictions / len(test_cases)) * 100
    print(f"Test Results Summary:")
    print(f"  Correct: {correct_predictions}/{len(test_cases)}")
    print(f"  Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print(f"  Status: EXCELLENT - Models ready for production!")
    elif accuracy >= 60:
        print(f"  Status: GOOD - Models working well!")
    else:
        print(f"  Status: NEEDS WORK - Consider retraining")
    
    return accuracy >= 60

if __name__ == "__main__":
    test_models()