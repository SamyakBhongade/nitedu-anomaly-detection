#!/usr/bin/env python3
"""
Simple ML Training - No emojis, just training
"""

import numpy as np
import torch
import torch.nn as nn
import joblib
import logging
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleLSTM(nn.Module):
    def __init__(self, input_size=20):
        super(SimpleLSTM, self).__init__()
        self.encoder = nn.LSTM(input_size, 32, 1, batch_first=True)
        self.decoder = nn.LSTM(32, input_size, 1, batch_first=True)
        
    def forward(self, x):
        encoded, (h, c) = self.encoder(x)
        decoded, _ = self.decoder(encoded, (h, c))
        return decoded
    
    def get_reconstruction_error(self, x):
        self.eval()
        with torch.no_grad():
            reconstructed = self.forward(x)
            mse = torch.mean((x - reconstructed) ** 2, dim=(1, 2))
            return mse

def create_training_data(n_samples=1000):
    """Create synthetic network data"""
    
    # Normal traffic
    normal_data = []
    for _ in range(int(n_samples * 0.8)):
        features = np.random.normal(0.3, 0.1, 20)
        features = np.clip(features, 0, 1)
        normal_data.append(features)
    
    # Attack traffic
    attack_data = []
    for _ in range(int(n_samples * 0.2)):
        features = np.random.normal(0.7, 0.2, 20)
        features = np.clip(features, 0, 1)
        features[2] = np.random.uniform(0.8, 1.0)  # SQL injection
        features[3] = np.random.uniform(0.7, 1.0)  # XSS
        features[4] = np.random.uniform(0.6, 1.0)  # Bot
        attack_data.append(features)
    
    X = np.array(normal_data + attack_data)
    y = np.array([0] * len(normal_data) + [1] * len(attack_data))
    
    return X, y

def train_models():
    """Train ML models"""
    
    print("Starting ML Model Training...")
    print("=" * 40)
    
    # Create directories
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate data
    print("Generating training data...")
    X, y = create_training_data(2000)
    
    # Use only normal data
    normal_data = X[y == 0]
    
    # Scale data
    scaler = StandardScaler()
    normal_scaled = scaler.fit_transform(normal_data)
    
    print(f"Training data ready: {len(normal_scaled)} normal samples")
    
    # Train LSTM
    print("Training LSTM Autoencoder...")
    
    sequence_length = 10
    sequences = []
    for i in range(0, len(normal_scaled) - sequence_length + 1, sequence_length):
        sequences.append(normal_scaled[i:i + sequence_length])
    
    sequences = np.array(sequences)
    X_tensor = torch.FloatTensor(sequences)
    
    lstm_model = SimpleLSTM(input_size=20)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(lstm_model.parameters(), lr=0.01)
    
    lstm_model.train()
    for epoch in range(20):
        optimizer.zero_grad()
        reconstructed = lstm_model(X_tensor)
        loss = criterion(reconstructed, X_tensor)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 5 == 0:
            print(f"   Epoch {epoch+1}/20, Loss: {loss.item():.6f}")
    
    # Calculate threshold
    lstm_model.eval()
    with torch.no_grad():
        errors = lstm_model.get_reconstruction_error(X_tensor)
        lstm_threshold = torch.quantile(errors, 0.9).item()
    
    print(f"LSTM trained, threshold: {lstm_threshold:.6f}")
    
    # Train Isolation Forest
    print("Training Isolation Forest...")
    
    isolation_forest = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=50
    )
    isolation_forest.fit(normal_scaled)
    
    print("Isolation Forest trained")
    
    # Save models
    print("Saving models...")
    
    torch.save({
        'model_state_dict': lstm_model.state_dict(),
        'threshold': lstm_threshold,
        'feature_dim': 20,
        'sequence_length': sequence_length
    }, models_dir / "lstm_autoencoder.pth")
    
    joblib.dump(isolation_forest, models_dir / "isolation_forest.joblib")
    joblib.dump(scaler, models_dir / "feature_scaler.joblib")
    
    metadata = {
        'feature_dim': 20,
        'sequence_length': sequence_length,
        'lstm_threshold': lstm_threshold
    }
    joblib.dump(metadata, models_dir / "model_metadata.joblib")
    
    print(f"Models saved to {models_dir}")
    
    # Quick test
    print("\nQuick Model Test:")
    
    # Normal request test
    normal_features = np.array([[0.3] * 20])
    normal_scaled = scaler.transform(normal_features)
    
    normal_seq = np.tile(normal_scaled, (sequence_length, 1)).reshape(1, sequence_length, 20)
    normal_tensor = torch.FloatTensor(normal_seq)
    normal_error = lstm_model.get_reconstruction_error(normal_tensor).item()
    normal_iso = isolation_forest.predict(normal_scaled)[0]
    
    print(f"Normal request - LSTM error: {normal_error:.6f}, ISO pred: {normal_iso}")
    
    # Attack request test
    attack_features = np.array([[0.8] * 20])
    attack_features[0][2] = 0.95  # High SQL injection score
    attack_scaled = scaler.transform(attack_features)
    
    attack_seq = np.tile(attack_scaled, (sequence_length, 1)).reshape(1, sequence_length, 20)
    attack_tensor = torch.FloatTensor(attack_seq)
    attack_error = lstm_model.get_reconstruction_error(attack_tensor).item()
    attack_iso = isolation_forest.predict(attack_scaled)[0]
    
    print(f"Attack request - LSTM error: {attack_error:.6f}, ISO pred: {attack_iso}")
    
    print("\nML Model Training Completed Successfully!")
    print("Models are ready for testing and integration!")
    
    return True

if __name__ == "__main__":
    train_models()