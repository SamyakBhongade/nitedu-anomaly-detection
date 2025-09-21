#!/usr/bin/env python3
"""
Complete ML Training Pipeline for Cognitive Cyber Defense
Trains models on real datasets and saves them for production use
"""

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import joblib
import os
import logging
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMAutoencoder(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(LSTMAutoencoder, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Encoder
        self.encoder = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        
        # Decoder
        self.decoder = nn.LSTM(hidden_size, input_size, num_layers, batch_first=True)
        
    def forward(self, x):
        # Encode
        encoded, (h_n, c_n) = self.encoder(x)
        
        # Decode
        decoded, _ = self.decoder(encoded, (h_n, c_n))
        
        return decoded
    
    def get_reconstruction_error(self, x):
        self.eval()
        with torch.no_grad():
            reconstructed = self.forward(x)
            mse = torch.mean((x - reconstructed) ** 2, dim=(1, 2))
            return mse

class CyberDefenseMLPipeline:
    def __init__(self):
        self.models_dir = Path("data/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.lstm_model = None
        self.isolation_forest = None
        
        # Model parameters
        self.sequence_length = 10
        self.feature_dim = 20  # Standardized feature count
        
    def load_nsl_kdd(self):
        """Load and preprocess NSL-KDD dataset"""
        logger.info("Loading NSL-KDD dataset...")
        
        columns = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
            'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
            'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
            'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
            'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'attack_type', 'difficulty'
        ]
        
        try:
            train_df = pd.read_csv("datasets/nsl_kdd_train.txt", names=columns)
            test_df = pd.read_csv("datasets/nsl_kdd_test.txt", names=columns)
            
            df = pd.concat([train_df, test_df], ignore_index=True)
            df['label'] = (df['attack_type'] != 'normal').astype(int)
            
            logger.info(f"NSL-KDD loaded: {len(df)} samples, {df['label'].sum()} attacks")
            return df
        except Exception as e:
            logger.error(f"Failed to load NSL-KDD: {e}")
            return None
    
    def load_unsw_nb15(self):
        """Load and preprocess UNSW-NB15 dataset"""
        logger.info("Loading UNSW-NB15 dataset...")
        
        try:
            train_df = pd.read_csv("datasets/unsw_train.csv")
            test_df = pd.read_csv("datasets/unsw_test.csv")
            
            df = pd.concat([train_df, test_df], ignore_index=True)
            
            # Clean label column
            if 'label' in df.columns:
                df['label'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)
            else:
                df['label'] = 0
            
            logger.info(f"UNSW-NB15 loaded: {len(df)} samples, {df['label'].sum()} attacks")
            return df
        except Exception as e:
            logger.error(f"Failed to load UNSW-NB15: {e}")
            return None
    
    def preprocess_data(self, df):
        """Preprocess dataset for ML training"""
        logger.info("Preprocessing data...")
        
        # Handle categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if 'label' in categorical_cols:
            categorical_cols.remove('label')
        if 'attack_type' in categorical_cols:
            categorical_cols.remove('attack_type')
        
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                try:
                    df[col] = self.label_encoders[col].transform(df[col].astype(str))
                except:
                    df[col] = 0
        
        # Select numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'label' in numeric_cols:
            numeric_cols.remove('label')
        if 'difficulty' in numeric_cols:
            numeric_cols.remove('difficulty')
        
        # Standardize to fixed feature count
        if len(numeric_cols) > self.feature_dim:
            numeric_cols = numeric_cols[:self.feature_dim]
        elif len(numeric_cols) < self.feature_dim:
            # Pad with zeros
            for i in range(len(numeric_cols), self.feature_dim):
                df[f'feature_{i}'] = 0
                numeric_cols.append(f'feature_{i}')
        
        X = df[numeric_cols].fillna(0)
        y = df['label'] if 'label' in df.columns else np.zeros(len(df))
        
        return X.values, y.values
    
    def create_sequences(self, X, sequence_length=None):
        """Create sequences for LSTM training"""
        if sequence_length is None:
            sequence_length = self.sequence_length
            
        if len(X) < sequence_length:
            # Pad with zeros
            padded = np.zeros((sequence_length, X.shape[1]))
            padded[:len(X)] = X
            return padded.reshape(1, sequence_length, X.shape[1])
        
        sequences = []
        for i in range(0, len(X) - sequence_length + 1, sequence_length):
            sequences.append(X[i:i + sequence_length])
        
        return np.array(sequences)
    
    def train_lstm_autoencoder(self, X_normal):
        """Train LSTM Autoencoder on normal data"""
        logger.info("Training LSTM Autoencoder...")
        
        # Create sequences
        sequences = self.create_sequences(X_normal)
        
        # Convert to PyTorch tensors
        X_tensor = torch.FloatTensor(sequences)
        
        # Initialize model
        self.lstm_model = LSTMAutoencoder(
            input_size=self.feature_dim,
            hidden_size=64,
            num_layers=2
        )
        
        # Training parameters
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.lstm_model.parameters(), lr=0.001)
        epochs = 50
        
        # Training loop
        self.lstm_model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            # Forward pass
            reconstructed = self.lstm_model(X_tensor)
            loss = criterion(reconstructed, X_tensor)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"LSTM Epoch {epoch+1}/{epochs}, Loss: {loss.item():.6f}")
        
        # Calculate threshold on normal data
        self.lstm_model.eval()
        with torch.no_grad():
            errors = self.lstm_model.get_reconstruction_error(X_tensor)
            self.lstm_threshold = torch.quantile(errors, 0.95).item()
        
        logger.info(f"LSTM training completed. Threshold: {self.lstm_threshold:.6f}")
    
    def train_isolation_forest(self, X_normal):
        """Train Isolation Forest on normal data"""
        logger.info("Training Isolation Forest...")
        
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        self.isolation_forest.fit(X_normal)
        logger.info("Isolation Forest training completed")
    
    def save_models(self):
        """Save trained models to disk"""
        logger.info("Saving models...")
        
        # Save LSTM model
        if self.lstm_model:
            torch.save({
                'model_state_dict': self.lstm_model.state_dict(),
                'threshold': self.lstm_threshold,
                'feature_dim': self.feature_dim,
                'sequence_length': self.sequence_length
            }, self.models_dir / "lstm_autoencoder.pth")
        
        # Save Isolation Forest
        if self.isolation_forest:
            joblib.dump(self.isolation_forest, self.models_dir / "isolation_forest.joblib")
        
        # Save scaler
        joblib.dump(self.scaler, self.models_dir / "feature_scaler.joblib")
        
        # Save label encoders
        joblib.dump(self.label_encoders, self.models_dir / "label_encoders.joblib")
        
        # Save model metadata
        metadata = {
            'feature_dim': self.feature_dim,
            'sequence_length': self.sequence_length,
            'lstm_threshold': getattr(self, 'lstm_threshold', 0.5)
        }
        joblib.dump(metadata, self.models_dir / "model_metadata.joblib")
        
        logger.info(f"Models saved to {self.models_dir}")
    
    def evaluate_models(self, X_test, y_test):
        """Evaluate trained models"""
        logger.info("Evaluating models...")
        
        # Scale test data
        X_test_scaled = self.scaler.transform(X_test)
        
        # LSTM predictions
        sequences = self.create_sequences(X_test_scaled)
        X_tensor = torch.FloatTensor(sequences)
        
        self.lstm_model.eval()
        with torch.no_grad():
            lstm_errors = self.lstm_model.get_reconstruction_error(X_tensor)
            lstm_predictions = (lstm_errors > self.lstm_threshold).numpy()
        
        # Isolation Forest predictions
        iso_predictions = self.isolation_forest.predict(X_test_scaled)
        iso_predictions = (iso_predictions == -1).astype(int)  # Convert to binary
        
        # Ensemble prediction (majority vote)
        if len(lstm_predictions) == len(iso_predictions):
            ensemble_predictions = ((lstm_predictions + iso_predictions) >= 1).astype(int)
        else:
            # Handle length mismatch
            min_len = min(len(lstm_predictions), len(iso_predictions))
            ensemble_predictions = ((lstm_predictions[:min_len] + iso_predictions[:min_len]) >= 1).astype(int)
        
        # Evaluate
        y_test_subset = y_test[:len(ensemble_predictions)]
        
        logger.info("LSTM Autoencoder Results:")
        logger.info(classification_report(y_test_subset, lstm_predictions[:len(y_test_subset)]))
        
        logger.info("Isolation Forest Results:")
        logger.info(classification_report(y_test_subset, iso_predictions[:len(y_test_subset)]))
        
        logger.info("Ensemble Results:")
        logger.info(classification_report(y_test_subset, ensemble_predictions))
        
        return {
            'lstm_accuracy': np.mean(lstm_predictions[:len(y_test_subset)] == y_test_subset),
            'isolation_accuracy': np.mean(iso_predictions[:len(y_test_subset)] == y_test_subset),
            'ensemble_accuracy': np.mean(ensemble_predictions == y_test_subset)
        }
    
    def train_complete_pipeline(self, sample_size=10000):
        """Train complete ML pipeline"""
        logger.info("🚀 Starting Complete ML Training Pipeline")
        
        # Load datasets
        datasets = []
        
        nsl_df = self.load_nsl_kdd()
        if nsl_df is not None:
            datasets.append(nsl_df.sample(min(sample_size, len(nsl_df))))
        
        unsw_df = self.load_unsw_nb15()
        if unsw_df is not None:
            datasets.append(unsw_df.sample(min(sample_size, len(unsw_df))))
        
        if not datasets:
            raise ValueError("No datasets loaded successfully")
        
        # Combine datasets
        combined_df = pd.concat(datasets, ignore_index=True)
        logger.info(f"Combined dataset: {len(combined_df)} samples")
        
        # Preprocess data
        X, y = self.preprocess_data(combined_df)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Use only normal data for training (unsupervised)
        normal_indices = y_train == 0
        X_normal = X_train[normal_indices]
        
        logger.info(f"Training on {len(X_normal)} normal samples")
        
        # Train models
        self.train_lstm_autoencoder(X_normal)
        self.train_isolation_forest(X_normal)
        
        # Evaluate models
        results = self.evaluate_models(X_test, y_test)
        
        # Save models
        self.save_models()
        
        logger.info("🎯 Training Pipeline Completed!")
        logger.info(f"Final Results: {results}")
        
        return results

def main():
    """Main training function"""
    pipeline = CyberDefenseMLPipeline()
    results = pipeline.train_complete_pipeline(sample_size=5000)
    
    print("\n🛡️ COGNITIVE CYBER DEFENSE - ML TRAINING COMPLETE")
    print("=" * 60)
    print(f"✅ LSTM Accuracy: {results['lstm_accuracy']:.3f}")
    print(f"✅ Isolation Forest Accuracy: {results['isolation_accuracy']:.3f}")
    print(f"✅ Ensemble Accuracy: {results['ensemble_accuracy']:.3f}")
    print(f"📁 Models saved to: data/models/")
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    main()