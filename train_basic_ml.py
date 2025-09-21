#!/usr/bin/env python3
"""
Basic ML Training - Simple and working
"""

import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

def create_training_data(n_samples=2000):
    """Create synthetic network data"""
    
    # Normal traffic features (20 features)
    normal_data = []
    for _ in range(int(n_samples * 0.8)):
        features = np.random.normal(0.2, 0.1, 20)  # Low values for normal
        features = np.clip(features, 0, 1)
        normal_data.append(features)
    
    # Attack traffic features
    attack_data = []
    for _ in range(int(n_samples * 0.2)):
        features = np.random.normal(0.6, 0.2, 20)  # Higher values for attacks
        features = np.clip(features, 0, 1)
        
        # Inject specific attack patterns
        features[2] = np.random.uniform(0.7, 1.0)  # SQL injection score
        features[3] = np.random.uniform(0.6, 1.0)  # XSS score  
        features[4] = np.random.uniform(0.5, 1.0)  # Bot score
        features[10] = np.random.uniform(0.8, 1.0) # High packet count
        
        attack_data.append(features)
    
    X = np.array(normal_data + attack_data)
    y = np.array([0] * len(normal_data) + [1] * len(attack_data))
    
    return X, y

def train_models():
    """Train ML models"""
    
    print("Starting Basic ML Model Training...")
    print("=" * 40)
    
    # Create directories
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate training data
    print("Generating synthetic training data...")
    X, y = create_training_data(3000)
    
    # Use only normal data for unsupervised training
    normal_data = X[y == 0]
    print(f"Normal training samples: {len(normal_data)}")
    
    # Scale features
    print("Scaling features...")
    scaler = StandardScaler()
    normal_scaled = scaler.fit_transform(normal_data)
    
    # Train Isolation Forest
    print("Training Isolation Forest...")
    isolation_forest = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    isolation_forest.fit(normal_scaled)
    print("Isolation Forest training completed")
    
    # Train One-Class SVM as backup
    print("Training One-Class SVM...")
    svm_model = OneClassSVM(
        kernel='rbf',
        gamma='scale',
        nu=0.1
    )
    svm_model.fit(normal_scaled)
    print("One-Class SVM training completed")
    
    # Save models
    print("Saving models...")
    
    # Save Isolation Forest
    joblib.dump(isolation_forest, models_dir / "isolation_forest.joblib")
    
    # Save One-Class SVM
    joblib.dump(svm_model, models_dir / "svm_model.joblib")
    
    # Save scaler
    joblib.dump(scaler, models_dir / "feature_scaler.joblib")
    
    # Save metadata
    metadata = {
        'feature_dim': 20,
        'model_type': 'isolation_forest_svm',
        'contamination': 0.1,
        'training_samples': len(normal_data)
    }
    joblib.dump(metadata, models_dir / "model_metadata.joblib")
    
    print(f"Models saved to: {models_dir}")
    
    # Test models
    print("\nTesting trained models...")
    
    # Test data (normal and attack)
    test_X, test_y = create_training_data(200)
    test_X_scaled = scaler.transform(test_X)
    
    # Isolation Forest predictions
    iso_predictions = isolation_forest.predict(test_X_scaled)
    iso_anomalies = (iso_predictions == -1).astype(int)
    
    # SVM predictions  
    svm_predictions = svm_model.predict(test_X_scaled)
    svm_anomalies = (svm_predictions == -1).astype(int)
    
    # Ensemble prediction (majority vote)
    ensemble_anomalies = ((iso_anomalies + svm_anomalies) >= 1).astype(int)
    
    # Calculate accuracy
    iso_accuracy = np.mean(iso_anomalies == test_y) * 100
    svm_accuracy = np.mean(svm_anomalies == test_y) * 100
    ensemble_accuracy = np.mean(ensemble_anomalies == test_y) * 100
    
    print(f"Isolation Forest Accuracy: {iso_accuracy:.1f}%")
    print(f"One-Class SVM Accuracy: {svm_accuracy:.1f}%")
    print(f"Ensemble Accuracy: {ensemble_accuracy:.1f}%")
    
    # Test specific cases
    print("\nTesting specific attack patterns...")
    
    # Normal request
    normal_test = np.array([[0.2] * 20])
    normal_scaled = scaler.transform(normal_test)
    
    iso_normal = isolation_forest.predict(normal_scaled)[0]
    svm_normal = svm_model.predict(normal_scaled)[0]
    
    print(f"Normal request - ISO: {iso_normal}, SVM: {svm_normal}")
    
    # SQL injection attack
    sql_attack = np.array([[0.3] * 20])
    sql_attack[0][2] = 0.9  # High SQL injection score
    sql_attack[0][3] = 0.1  # Low XSS score
    sql_attack[0][4] = 0.1  # Low bot score
    sql_scaled = scaler.transform(sql_attack)
    
    iso_sql = isolation_forest.predict(sql_scaled)[0]
    svm_sql = svm_model.predict(sql_scaled)[0]
    
    print(f"SQL injection - ISO: {iso_sql}, SVM: {svm_sql}")
    
    # Bot attack
    bot_attack = np.array([[0.3] * 20])
    bot_attack[0][2] = 0.1  # Low SQL score
    bot_attack[0][3] = 0.1  # Low XSS score
    bot_attack[0][4] = 0.9  # High bot score
    bot_scaled = scaler.transform(bot_attack)
    
    iso_bot = isolation_forest.predict(bot_scaled)[0]
    svm_bot = svm_model.predict(bot_scaled)[0]
    
    print(f"Bot attack - ISO: {iso_bot}, SVM: {svm_bot}")
    
    print("\nML Model Training Completed Successfully!")
    print("Models saved and ready for integration!")
    
    # List saved files
    print(f"\nSaved model files:")
    for file in models_dir.glob("*.joblib"):
        size_kb = file.stat().st_size / 1024
        print(f"  {file.name} ({size_kb:.1f} KB)")
    
    return True

if __name__ == "__main__":
    train_models()