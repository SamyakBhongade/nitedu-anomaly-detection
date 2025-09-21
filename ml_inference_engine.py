#!/usr/bin/env python3
"""
ML Inference Engine for Real-time Anomaly Detection
Loads trained models and provides fast inference for production use
"""

import torch
import torch.nn as nn
import joblib
import numpy as np
import logging
from pathlib import Path
import time
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMAutoencoder(nn.Module):
    """LSTM Autoencoder for anomaly detection"""
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(LSTMAutoencoder, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.encoder = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.decoder = nn.LSTM(hidden_size, input_size, num_layers, batch_first=True)
        
    def forward(self, x):
        encoded, (h_n, c_n) = self.encoder(x)
        decoded, _ = self.decoder(encoded, (h_n, c_n))
        return decoded
    
    def get_reconstruction_error(self, x):
        self.eval()
        with torch.no_grad():
            reconstructed = self.forward(x)
            mse = torch.mean((x - reconstructed) ** 2, dim=(1, 2))
            return mse

class MLInferenceEngine:
    """Production ML inference engine"""
    
    def __init__(self, models_dir: str = "data/models"):
        self.models_dir = Path(models_dir)
        self.lstm_model = None
        self.isolation_forest = None
        self.scaler = None
        self.label_encoders = None
        self.metadata = None
        self.is_loaded = False
        
    def load_models(self):
        """Load all trained models"""
        logger.info("Loading ML models...")
        
        try:
            # Load metadata
            metadata_path = self.models_dir / "model_metadata.joblib"
            if metadata_path.exists():
                self.metadata = joblib.load(metadata_path)
                logger.info(f"Loaded metadata: {self.metadata}")
            else:
                # Default metadata
                self.metadata = {
                    'feature_dim': 20,
                    'sequence_length': 10,
                    'lstm_threshold': 0.5
                }
            
            # Load LSTM model
            lstm_path = self.models_dir / "lstm_autoencoder.pth"
            if lstm_path.exists():
                checkpoint = torch.load(lstm_path, map_location='cpu')
                self.lstm_model = LSTMAutoencoder(
                    input_size=self.metadata['feature_dim'],
                    hidden_size=64,
                    num_layers=2
                )
                self.lstm_model.load_state_dict(checkpoint['model_state_dict'])
                self.lstm_model.eval()
                self.lstm_threshold = checkpoint.get('threshold', self.metadata['lstm_threshold'])
                logger.info("✅ LSTM Autoencoder loaded")
            else:
                logger.warning("❌ LSTM model not found")
            
            # Load Isolation Forest
            iso_path = self.models_dir / "isolation_forest.joblib"
            if iso_path.exists():
                self.isolation_forest = joblib.load(iso_path)
                logger.info("✅ Isolation Forest loaded")
            else:
                logger.warning("❌ Isolation Forest not found")
            
            # Load scaler
            scaler_path = self.models_dir / "feature_scaler.joblib"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("✅ Feature scaler loaded")
            else:
                logger.warning("❌ Feature scaler not found")
            
            # Load label encoders
            encoders_path = self.models_dir / "label_encoders.joblib"
            if encoders_path.exists():
                self.label_encoders = joblib.load(encoders_path)
                logger.info("✅ Label encoders loaded")
            
            self.is_loaded = True
            logger.info("🚀 All models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self.is_loaded = False
    
    def extract_features_from_request(self, request_data: Dict[str, Any]) -> np.ndarray:
        """Extract ML features from HTTP request data"""
        
        # Initialize feature vector
        features = np.zeros(self.metadata['feature_dim'])
        
        try:
            # Basic request features
            path = str(request_data.get('path', '')).lower()
            user_agent = str(request_data.get('user_agent', '')).lower()
            method = str(request_data.get('method', 'GET')).upper()
            
            # Feature 0: Path length
            features[0] = min(len(path) / 100.0, 1.0)
            
            # Feature 1: Query parameter count
            query_params = path.count('=') + path.count('&')
            features[1] = min(query_params / 10.0, 1.0)
            
            # Feature 2: SQL injection indicators
            sql_patterns = ['union', 'select', 'drop', 'insert', 'delete', "' or '", '--', ';']
            sql_score = sum(1 for pattern in sql_patterns if pattern in path)
            features[2] = min(sql_score / len(sql_patterns), 1.0)
            
            # Feature 3: XSS indicators
            xss_patterns = ['<script', 'javascript:', 'onerror=', 'alert(', '<iframe', 'document.cookie']
            xss_score = sum(1 for pattern in xss_patterns if pattern in path)
            features[3] = min(xss_score / len(xss_patterns), 1.0)
            
            # Feature 4: Bot indicators
            bot_patterns = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python', 'sqlmap']
            bot_score = sum(1 for pattern in bot_patterns if pattern in user_agent)
            features[4] = min(bot_score / len(bot_patterns), 1.0)
            
            # Feature 5: Method encoding (GET=0.1, POST=0.5, PUT=0.7, DELETE=0.9)
            method_scores = {'GET': 0.1, 'POST': 0.5, 'PUT': 0.7, 'DELETE': 0.9}
            features[5] = method_scores.get(method, 0.3)
            
            # Feature 6: Suspicious characters
            suspicious_chars = ['<', '>', '"', "'", '&', '%', ';', '(', ')', '{', '}']
            suspicious_count = sum(path.count(char) for char in suspicious_chars)
            features[6] = min(suspicious_count / 20.0, 1.0)
            
            # Feature 7: Entropy of path
            if len(path) > 0:
                entropy = self._calculate_entropy(path)
                features[7] = min(entropy / 5.0, 1.0)
            
            # Feature 8: Numeric values in path
            numeric_count = sum(1 for char in path if char.isdigit())
            features[8] = min(numeric_count / 50.0, 1.0)
            
            # Feature 9: Special encoding patterns
            encoding_patterns = ['%20', '%27', '%3c', '%3e', '%22', 'union+select']
            encoding_score = sum(1 for pattern in encoding_patterns if pattern in path)
            features[9] = min(encoding_score / len(encoding_patterns), 1.0)
            
            # Features 10-14: Network-like features (simulated)
            features[10] = request_data.get('packet_count', 10) / 100.0
            features[11] = min(request_data.get('byte_count', 1500) / 10000.0, 1.0)
            features[12] = min(request_data.get('duration', 0.1) / 10.0, 1.0)
            features[13] = 1.0 if request_data.get('country') in ['CN', 'RU', 'KP', 'IR'] else 0.0
            features[14] = request_data.get('src_port', 80) / 65535.0
            
            # Features 15-19: Additional behavioral features
            features[15] = 1.0 if 'admin' in path else 0.0
            features[16] = 1.0 if any(x in path for x in ['wp-', 'phpmyadmin', '.php']) else 0.0
            features[17] = len(user_agent) / 200.0 if user_agent else 0.0
            features[18] = 1.0 if method == 'POST' and any(x in path for x in ['login', 'auth']) else 0.0
            features[19] = path.count('/') / 10.0
            
        except Exception as e:
            logger.warning(f"Feature extraction error: {e}")
        
        return features.reshape(1, -1)
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_len = len(text)
        for count in char_counts.values():
            probability = count / text_len
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    def create_sequence(self, features: np.ndarray) -> np.ndarray:
        """Create sequence for LSTM input"""
        sequence_length = self.metadata['sequence_length']
        
        # Repeat features to create sequence
        sequence = np.tile(features, (sequence_length, 1))
        return sequence.reshape(1, sequence_length, -1)
    
    def predict_anomaly(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict if request is anomalous"""
        
        if not self.is_loaded:
            return {
                'error': 'Models not loaded',
                'is_anomaly': False,
                'confidence': 0.0
            }
        
        start_time = time.time()
        
        try:
            # Extract features
            features = self.extract_features_from_request(request_data)
            
            # Scale features
            if self.scaler:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features
            
            predictions = {}
            scores = {}
            
            # LSTM prediction
            if self.lstm_model:
                sequence = self.create_sequence(features_scaled)
                X_tensor = torch.FloatTensor(sequence)
                
                error = self.lstm_model.get_reconstruction_error(X_tensor)
                lstm_score = error.item()
                lstm_anomaly = lstm_score > self.lstm_threshold
                
                predictions['lstm'] = lstm_anomaly
                scores['lstm'] = lstm_score
            
            # Isolation Forest prediction
            if self.isolation_forest:
                iso_pred = self.isolation_forest.predict(features_scaled)[0]
                iso_score = self.isolation_forest.decision_function(features_scaled)[0]
                iso_anomaly = iso_pred == -1
                
                predictions['isolation'] = iso_anomaly
                scores['isolation'] = abs(iso_score)
            
            # Ensemble prediction (majority vote)
            anomaly_votes = sum(predictions.values())
            total_models = len(predictions)
            
            is_anomaly = anomaly_votes >= (total_models / 2)
            confidence = anomaly_votes / total_models if total_models > 0 else 0.0
            
            # Determine attack type
            attack_type = self._classify_attack_type(request_data, features_scaled)
            
            inference_time = time.time() - start_time
            
            return {
                'is_anomaly': is_anomaly,
                'confidence': confidence,
                'attack_type': attack_type,
                'model_predictions': predictions,
                'model_scores': scores,
                'inference_time_ms': inference_time * 1000,
                'feature_vector': features_scaled.tolist()[0]
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'error': str(e),
                'is_anomaly': False,
                'confidence': 0.0
            }
    
    def _classify_attack_type(self, request_data: Dict[str, Any], features: np.ndarray) -> str:
        """Classify the type of attack based on features"""
        
        path = str(request_data.get('path', '')).lower()
        user_agent = str(request_data.get('user_agent', '')).lower()
        
        # SQL Injection
        if features[0][2] > 0.3:  # SQL injection feature
            return 'SQL Injection'
        
        # XSS
        if features[0][3] > 0.3:  # XSS feature
            return 'XSS Attack'
        
        # Bot/Scraper
        if features[0][4] > 0.3:  # Bot feature
            return 'Bot Attack'
        
        # DDoS (high packet count)
        if features[0][10] > 0.5:  # Packet count feature
            return 'DDoS Attack'
        
        # Brute Force (login attempts)
        if features[0][18] > 0.5:  # Login POST feature
            return 'Brute Force'
        
        # Admin Access
        if features[0][15] > 0.5:  # Admin path feature
            return 'Unauthorized Access'
        
        return 'Unknown Attack'
    
    def batch_predict(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict anomalies for batch of requests"""
        
        results = []
        for request_data in requests:
            result = self.predict_anomaly(request_data)
            results.append(result)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        
        return {
            'models_loaded': self.is_loaded,
            'lstm_available': self.lstm_model is not None,
            'isolation_forest_available': self.isolation_forest is not None,
            'scaler_available': self.scaler is not None,
            'metadata': self.metadata,
            'models_directory': str(self.models_dir)
        }

def test_inference_engine():
    """Test the inference engine"""
    
    print("🧪 Testing ML Inference Engine")
    print("=" * 40)
    
    # Initialize engine
    engine = MLInferenceEngine()
    engine.load_models()
    
    # Test requests
    test_requests = [
        {
            'path': '/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'method': 'GET',
            'country': 'US'
        },
        {
            'path': "/?id=1' OR '1'='1",
            'user_agent': 'sqlmap/1.0',
            'method': 'POST',
            'country': 'CN'
        },
        {
            'path': '/search?q=<script>alert("xss")</script>',
            'user_agent': 'Mozilla/5.0',
            'method': 'GET',
            'country': 'RU'
        }
    ]
    
    for i, request in enumerate(test_requests):
        print(f"\n🔍 Test {i+1}: {request['path'][:50]}...")
        result = engine.predict_anomaly(request)
        
        print(f"   Anomaly: {result['is_anomaly']}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Attack Type: {result.get('attack_type', 'Unknown')}")
        print(f"   Inference Time: {result.get('inference_time_ms', 0):.2f}ms")
    
    # Model info
    print(f"\n📊 Model Info:")
    info = engine.get_model_info()
    for key, value in info.items():
        if key != 'metadata':
            print(f"   {key}: {value}")

if __name__ == "__main__":
    test_inference_engine()