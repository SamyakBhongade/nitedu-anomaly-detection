import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NetworkFeatureExtractor:
    def __init__(self):
        self.feature_names = [
            'packet_count', 'byte_count', 'duration', 'packets_per_second',
            'bytes_per_second', 'avg_packet_size', 'port_entropy', 'ip_entropy',
            'protocol_diversity', 'time_interval'
        ]
    
    def extract_features(self, events: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features from network events"""
        if not events:
            return np.zeros((1, len(self.feature_names)))
        
        features = []
        for event in events:
            feature_vector = self._extract_single_event_features(event)
            features.append(feature_vector)
        
        return np.array(features)
    
    def _extract_single_event_features(self, event: Dict[str, Any]) -> List[float]:
        """Extract features from a single network event"""
        features = []
        
        # Basic traffic metrics
        features.append(float(event.get('packet_count', 0)))
        features.append(float(event.get('byte_count', 0)))
        features.append(float(event.get('duration', 0)))
        
        # Derived metrics
        packet_count = event.get('packet_count', 1)
        byte_count = event.get('byte_count', 0)
        duration = max(event.get('duration', 1), 0.001)  # Avoid division by zero
        
        features.append(packet_count / duration)  # packets_per_second
        features.append(byte_count / duration)    # bytes_per_second
        features.append(byte_count / max(packet_count, 1))  # avg_packet_size
        
        # Entropy features
        features.append(self._calculate_port_entropy(event))
        features.append(self._calculate_ip_entropy(event))
        features.append(self._calculate_protocol_diversity(event))
        
        # Temporal feature
        features.append(self._extract_time_feature(event.get('timestamp')))
        
        return features
    
    def _calculate_port_entropy(self, event: Dict[str, Any]) -> float:
        """Calculate entropy of port usage"""
        ports = []
        if 'src_port' in event:
            ports.append(event['src_port'])
        if 'dst_port' in event:
            ports.append(event['dst_port'])
        
        if not ports:
            return 0.0
        
        return self._entropy(ports)
    
    def _calculate_ip_entropy(self, event: Dict[str, Any]) -> float:
        """Calculate entropy of IP addresses"""
        ips = []
        if 'src_ip' in event:
            ips.append(event['src_ip'])
        if 'dst_ip' in event:
            ips.append(event['dst_ip'])
        
        if not ips:
            return 0.0
        
        return self._entropy(ips)
    
    def _calculate_protocol_diversity(self, event: Dict[str, Any]) -> float:
        """Calculate protocol diversity score"""
        protocol = event.get('protocol', 'unknown')
        # Simple protocol scoring (can be enhanced)
        protocol_scores = {
            'tcp': 0.3, 'udp': 0.2, 'icmp': 0.1, 
            'http': 0.4, 'https': 0.5, 'dns': 0.3,
            'unknown': 0.0
        }
        return protocol_scores.get(protocol.lower(), 0.0)
    
    def _extract_time_feature(self, timestamp: Any) -> float:
        """Extract time-based feature (hour of day normalized)"""
        if timestamp is None:
            return 0.0
        
        try:
            if isinstance(timestamp, str):
                dt = pd.to_datetime(timestamp)
            elif isinstance(timestamp, (int, float)):
                dt = pd.to_datetime(timestamp, unit='s')
            else:
                dt = timestamp
            
            # Normalize hour to [0, 1]
            return dt.hour / 24.0
        except:
            return 0.0
    
    def _entropy(self, values: List[Any]) -> float:
        """Calculate Shannon entropy"""
        if not values:
            return 0.0
        
        value_counts = pd.Series(values).value_counts()
        probabilities = value_counts / len(values)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy
    
    def create_sequences(self, features: np.ndarray, sequence_length: int = 10,
                        step_size: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM and aggregated features for Isolation Forest"""
        if len(features) < sequence_length:
            # Pad with zeros if not enough data
            padding = np.zeros((sequence_length - len(features), features.shape[1]))
            features = np.vstack([padding, features])
        
        sequences = []
        aggregated_features = []
        
        for i in range(0, len(features) - sequence_length + 1, step_size):
            sequence = features[i:i + sequence_length]
            sequences.append(sequence)
            
            # Aggregate features for Isolation Forest
            agg_features = np.concatenate([
                np.mean(sequence, axis=0),
                np.std(sequence, axis=0),
                np.max(sequence, axis=0) - np.min(sequence, axis=0)  # range
            ])
            aggregated_features.append(agg_features)
        
        return np.array(sequences), np.array(aggregated_features)