import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import random

class SyntheticNetworkDataGenerator:
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
        self.normal_patterns = {
            'web_traffic': {'ports': [80, 443], 'packet_size_range': (64, 1500), 'frequency': 0.4},
            'email_traffic': {'ports': [25, 587, 993], 'packet_size_range': (100, 2000), 'frequency': 0.2},
            'dns_traffic': {'ports': [53], 'packet_size_range': (32, 512), 'frequency': 0.3},
            'file_transfer': {'ports': [21, 22], 'packet_size_range': (500, 8000), 'frequency': 0.1}
        }
        
        self.anomaly_patterns = {
            'port_scan': {'port_range': (1, 65535), 'packet_size': 64, 'frequency_multiplier': 10},
            'ddos': {'packet_size_range': (32, 128), 'frequency_multiplier': 50},
            'data_exfiltration': {'packet_size_range': (1000, 9000), 'frequency_multiplier': 5},
            'unusual_protocol': {'ports': [1337, 31337, 4444], 'packet_size_range': (100, 500)}
        }
    
    def generate_normal_traffic(self, num_events: int = 1000, 
                               duration_hours: int = 24) -> List[Dict[str, Any]]:
        """Generate normal network traffic patterns"""
        events = []
        start_time = datetime.now() - timedelta(hours=duration_hours)
        
        for i in range(num_events):
            # Choose traffic pattern
            pattern_name = np.random.choice(list(self.normal_patterns.keys()), 
                                          p=[p['frequency'] for p in self.normal_patterns.values()])
            pattern = self.normal_patterns[pattern_name]
            
            # Generate timestamp with business hours bias
            time_offset = np.random.exponential(duration_hours * 3600 / num_events)
            timestamp = start_time + timedelta(seconds=time_offset * i)
            
            # Add business hours bias (more traffic during 9-17)
            hour_bias = max(0.1, np.sin((timestamp.hour - 6) * np.pi / 12))
            if np.random.random() > hour_bias:
                continue
            
            event = self._generate_normal_event(pattern, timestamp)
            events.append(event)
        
        return sorted(events, key=lambda x: x['timestamp'])
    
    def generate_anomalous_traffic(self, num_events: int = 50) -> List[Dict[str, Any]]:
        """Generate anomalous network traffic"""
        events = []
        
        for i in range(num_events):
            anomaly_type = np.random.choice(list(self.anomaly_patterns.keys()))
            pattern = self.anomaly_patterns[anomaly_type]
            
            timestamp = datetime.now() - timedelta(seconds=np.random.randint(0, 86400))
            event = self._generate_anomalous_event(pattern, anomaly_type, timestamp)
            events.append(event)
        
        return events
    
    def _generate_normal_event(self, pattern: Dict, timestamp: datetime) -> Dict[str, Any]:
        """Generate a single normal network event"""
        src_ip = self._generate_internal_ip()
        dst_ip = self._generate_external_ip() if np.random.random() > 0.3 else self._generate_internal_ip()
        
        port = np.random.choice(pattern['ports'])
        packet_count = np.random.poisson(10) + 1
        
        min_size, max_size = pattern['packet_size_range']
        avg_packet_size = np.random.uniform(min_size, max_size)
        byte_count = int(packet_count * avg_packet_size)
        
        duration = np.random.exponential(2.0) + 0.1
        
        return {
            'timestamp': timestamp,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': np.random.randint(1024, 65535),
            'dst_port': port,
            'protocol': self._get_protocol_for_port(port),
            'packet_count': packet_count,
            'byte_count': byte_count,
            'duration': duration,
            'is_anomaly': False
        }
    
    def _generate_anomalous_event(self, pattern: Dict, anomaly_type: str, 
                                 timestamp: datetime) -> Dict[str, Any]:
        """Generate a single anomalous network event"""
        src_ip = self._generate_internal_ip()
        
        if anomaly_type == 'port_scan':
            dst_ip = self._generate_external_ip()
            dst_port = np.random.randint(1, 65535)
            packet_count = 1
            byte_count = pattern['packet_size']
            duration = 0.01
        
        elif anomaly_type == 'ddos':
            dst_ip = self._generate_external_ip()
            dst_port = 80
            packet_count = np.random.poisson(100) + 50
            min_size, max_size = pattern['packet_size_range']
            byte_count = packet_count * np.random.uniform(min_size, max_size)
            duration = np.random.uniform(0.1, 1.0)
        
        elif anomaly_type == 'data_exfiltration':
            dst_ip = self._generate_external_ip()
            dst_port = 443
            packet_count = np.random.poisson(50) + 20
            min_size, max_size = pattern['packet_size_range']
            byte_count = packet_count * np.random.uniform(min_size, max_size)
            duration = np.random.uniform(5.0, 30.0)
        
        else:  # unusual_protocol
            dst_ip = self._generate_external_ip()
            dst_port = np.random.choice(pattern['ports'])
            packet_count = np.random.poisson(20) + 5
            min_size, max_size = pattern['packet_size_range']
            byte_count = packet_count * np.random.uniform(min_size, max_size)
            duration = np.random.uniform(1.0, 10.0)
        
        return {
            'timestamp': timestamp,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': np.random.randint(1024, 65535),
            'dst_port': dst_port,
            'protocol': self._get_protocol_for_port(dst_port),
            'packet_count': packet_count,
            'byte_count': int(byte_count),
            'duration': duration,
            'is_anomaly': True,
            'anomaly_type': anomaly_type
        }
    
    def _generate_internal_ip(self) -> str:
        """Generate internal IP address"""
        return f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}"
    
    def _generate_external_ip(self) -> str:
        """Generate external IP address"""
        octets = [np.random.randint(1, 255) for _ in range(4)]
        # Avoid private ranges
        if octets[0] == 192 and octets[1] == 168:
            octets[0] = np.random.randint(1, 191)
        return '.'.join(map(str, octets))
    
    def _get_protocol_for_port(self, port: int) -> str:
        """Get protocol based on port number"""
        protocol_map = {
            80: 'http', 443: 'https', 53: 'dns', 25: 'smtp',
            587: 'smtp', 993: 'imap', 21: 'ftp', 22: 'ssh'
        }
        return protocol_map.get(port, 'tcp')
    
    def generate_mixed_dataset(self, normal_count: int = 5000, 
                              anomaly_count: int = 250) -> Tuple[List[Dict[str, Any]], np.ndarray]:
        """Generate mixed dataset with labels"""
        normal_events = self.generate_normal_traffic(normal_count)
        anomaly_events = self.generate_anomalous_traffic(anomaly_count)
        
        all_events = normal_events + anomaly_events
        labels = np.array([event['is_anomaly'] for event in all_events])
        
        # Shuffle while maintaining label correspondence
        indices = np.random.permutation(len(all_events))
        shuffled_events = [all_events[i] for i in indices]
        shuffled_labels = labels[indices]
        
        return shuffled_events, shuffled_labels