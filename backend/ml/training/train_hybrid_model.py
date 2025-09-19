import numpy as np
import torch
import logging
from pathlib import Path
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.models.hybrid_detector import HybridAnomalyDetector
from ml.preprocessing.feature_extractor import NetworkFeatureExtractor
from ml.preprocessing.windowing import TimeWindowProcessor
from ml.training.synthetic_data_generator import SyntheticNetworkDataGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridModelTrainer:
    def __init__(self, data_dir: str = "data", models_dir: str = "data/models"):
        self.data_dir = Path(data_dir)
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.data_generator = SyntheticNetworkDataGenerator()
        self.feature_extractor = NetworkFeatureExtractor()
        self.window_processor = TimeWindowProcessor(window_size_seconds=60)
        
    def train_model(self, normal_samples: int = 5000, anomaly_samples: int = 250,
                   sequence_length: int = 10) -> HybridAnomalyDetector:
        """Train the hybrid anomaly detection model"""
        
        logger.info("Generating synthetic training data...")
        events, labels = self.data_generator.generate_mixed_dataset(
            normal_count=normal_samples, 
            anomaly_count=anomaly_samples
        )
        
        logger.info(f"Generated {len(events)} events ({np.sum(labels)} anomalies)")
        
        # Extract features
        logger.info("Extracting features...")
        features = self.feature_extractor.extract_features(events)
        
        # Create sequences for LSTM and aggregated features for Isolation Forest
        logger.info("Creating sequences...")
        sequences, aggregated_features = self.feature_extractor.create_sequences(
            features, sequence_length=sequence_length
        )
        
        logger.info(f"Created {len(sequences)} sequences, {len(aggregated_features)} aggregated features")
        
        # Filter to use only normal data for training (unsupervised)
        normal_indices = np.where(labels[:len(sequences)] == False)[0]
        normal_sequences = sequences[normal_indices]
        normal_aggregated = aggregated_features[normal_indices]
        
        logger.info(f"Training on {len(normal_sequences)} normal sequences")
        
        # Initialize and train hybrid detector
        detector = HybridAnomalyDetector(
            sequence_length=sequence_length,
            feature_dim=features.shape[1]
        )
        
        detector.fit(normal_sequences, normal_aggregated)
        
        # Evaluate on full dataset
        logger.info("Evaluating model...")
        results = detector.predict_anomalies(sequences, aggregated_features)
        
        # Calculate metrics
        true_labels = labels[:len(sequences)]
        self._evaluate_performance(results, true_labels)
        
        # Save models
        lstm_path = self.models_dir / "lstm_autoencoder.pth"
        isolation_path = self.models_dir / "isolation_forest.joblib"
        
        detector.save_models(str(lstm_path), str(isolation_path))
        logger.info(f"Models saved to {self.models_dir}")
        
        return detector
    
    def _evaluate_performance(self, results: dict, true_labels: np.ndarray):
        """Evaluate model performance"""
        for model_name in ['lstm', 'isolation', 'hybrid']:
            predictions = results[f'{model_name}_anomalies']
            
            tp = np.sum((predictions == 1) & (true_labels == 1))
            fp = np.sum((predictions == 1) & (true_labels == 0))
            tn = np.sum((predictions == 0) & (true_labels == 0))
            fn = np.sum((predictions == 0) & (true_labels == 1))
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            accuracy = (tp + tn) / len(predictions)
            
            logger.info(f"{model_name.upper()} - Precision: {precision:.3f}, "
                       f"Recall: {recall:.3f}, F1: {f1:.3f}, Accuracy: {accuracy:.3f}")

def main():
    """Main training function"""
    trainer = HybridModelTrainer()
    
    # Train the model
    detector = trainer.train_model(
        normal_samples=3000,
        anomaly_samples=150,
        sequence_length=10
    )
    
    logger.info("Training completed successfully!")
    
    return detector

if __name__ == "__main__":
    main()