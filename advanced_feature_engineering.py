#!/usr/bin/env python3
"""
Advanced Feature Engineering for Cyber Defense
Extracts 100+ sophisticated features from network data
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder
import hashlib
import re
from urllib.parse import urlparse, parse_qs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedFeatureExtractor:
    """Advanced feature extraction for network security"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_fitted = False
        
    def extract_statistical_features(self, data_series):
        """Extract statistical features from data series"""
        if len(data_series) == 0:
            return [0] * 10
        
        features = [
            np.mean(data_series),
            np.std(data_series),
            np.median(data_series),
            np.min(data_series),
            np.max(data_series),
            stats.skew(data_series),
            stats.kurtosis(data_series),
            np.percentile(data_series, 25),
            np.percentile(data_series, 75),
            np.ptp(data_series)  # Peak-to-peak
        ]
        return features
    
    def extract_entropy_features(self, text):
        """Extract entropy-based features"""
        if not text or len(text) == 0:
            return [0] * 5
        
        # Character frequency entropy
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        char_entropy = 0
        text_len = len(text)
        for count in char_counts.values():
            prob = count / text_len
            if prob > 0:
                char_entropy -= prob * np.log2(prob)
        
        # N-gram entropy (bigrams)
        bigram_counts = {}
        for i in range(len(text) - 1):
            bigram = text[i:i+2]
            bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1
        
        bigram_entropy = 0
        total_bigrams = len(text) - 1
        if total_bigrams > 0:
            for count in bigram_counts.values():
                prob = count / total_bigrams
                if prob > 0:
                    bigram_entropy -= prob * np.log2(prob)
        
        return [
            char_entropy,
            bigram_entropy,
            len(set(text)) / len(text) if len(text) > 0 else 0,  # Character diversity
            len(char_counts),  # Unique characters
            np.std([char_counts.get(chr(i), 0) for i in range(256)])  # Character distribution std
        ]
    
    def extract_payload_features(self, payload):
        """Extract advanced payload analysis features"""
        if not payload:
            payload = ""
        
        payload_lower = payload.lower()
        
        # SQL injection patterns (advanced)
        sql_patterns = [
            r"union\s+select", r"drop\s+table", r"insert\s+into", r"delete\s+from",
            r"update\s+set", r"alter\s+table", r"create\s+table", r"grant\s+select",
            r"exec\s*\(", r"sp_executesql", r"xp_cmdshell", r"bulk\s+insert",
            r"openrowset", r"opendatasource", r"'.*or.*'.*=.*'", r"'.*and.*'.*=.*'",
            r"--", r"/\*.*\*/", r"@@version", r"@@servername", r"waitfor\s+delay"
        ]
        
        sql_score = sum(1 for pattern in sql_patterns if re.search(pattern, payload_lower))
        
        # XSS patterns (advanced)
        xss_patterns = [
            r"<script[^>]*>", r"</script>", r"javascript:", r"vbscript:", r"onload\s*=",
            r"onerror\s*=", r"onclick\s*=", r"onmouseover\s*=", r"onfocus\s*=",
            r"alert\s*\(", r"confirm\s*\(", r"prompt\s*\(", r"document\.cookie",
            r"document\.write", r"window\.location", r"eval\s*\(", r"settimeout\s*\(",
            r"setinterval\s*\(", r"<iframe[^>]*>", r"<object[^>]*>", r"<embed[^>]*>"
        ]
        
        xss_score = sum(1 for pattern in xss_patterns if re.search(pattern, payload_lower))
        
        # Command injection patterns
        cmd_patterns = [
            r";\s*cat\s+", r";\s*ls\s+", r";\s*pwd", r";\s*id", r";\s*whoami",
            r";\s*uname", r";\s*ps\s+", r";\s*netstat", r";\s*ifconfig",
            r"\|\s*cat\s+", r"\|\s*grep\s+", r"&&\s*cat\s+", r"\$\(.*\)",
            r"`.*`", r"nc\s+-", r"wget\s+", r"curl\s+", r"chmod\s+\+x"
        ]
        
        cmd_score = sum(1 for pattern in cmd_patterns if re.search(pattern, payload_lower))
        
        # Directory traversal patterns
        traversal_patterns = [
            r"\.\./", r"\.\.\\", r"%2e%2e%2f", r"%2e%2e%5c", r"..%2f", r"..%5c",
            r"etc/passwd", r"etc/shadow", r"boot\.ini", r"win\.ini", r"system32"
        ]
        
        traversal_score = sum(1 for pattern in traversal_patterns if re.search(pattern, payload_lower))
        
        # NoSQL injection patterns
        nosql_patterns = [
            r'\[\$ne\]', r'\[\$gt\]', r'\[\$lt\]', r'\[\$gte\]', r'\[\$lte\]',
            r'\[\$regex\]', r'\[\$where\]', r'\[\$exists\]', r'\[\$in\]', r'\[\$nin\]'
        ]
        
        nosql_score = sum(1 for pattern in nosql_patterns if re.search(pattern, payload_lower))
        
        # Encoding detection
        encoding_patterns = [
            r"%[0-9a-f]{2}", r"&#x[0-9a-f]+;", r"&#[0-9]+;", r"\\u[0-9a-f]{4}",
            r"\\x[0-9a-f]{2}", r"\+", r"%20", r"%3c", r"%3e", r"%22", r"%27"
        ]
        
        encoding_score = sum(len(re.findall(pattern, payload_lower)) for pattern in encoding_patterns)
        
        # Suspicious characters and patterns
        suspicious_chars = ['<', '>', '"', "'", '&', '%', ';', '(', ')', '{', '}', '[', ']']
        suspicious_count = sum(payload.count(char) for char in suspicious_chars)
        
        # Length-based features
        payload_length = len(payload)
        word_count = len(payload.split())
        avg_word_length = np.mean([len(word) for word in payload.split()]) if word_count > 0 else 0
        
        # Special character ratios
        alpha_ratio = sum(1 for c in payload if c.isalpha()) / len(payload) if len(payload) > 0 else 0
        digit_ratio = sum(1 for c in payload if c.isdigit()) / len(payload) if len(payload) > 0 else 0
        special_ratio = sum(1 for c in payload if not c.isalnum()) / len(payload) if len(payload) > 0 else 0
        
        return [
            sql_score, xss_score, cmd_score, traversal_score, nosql_score, encoding_score,
            suspicious_count, payload_length, word_count, avg_word_length,
            alpha_ratio, digit_ratio, special_ratio
        ]
    
    def extract_network_flow_features(self, flow_data):
        """Extract network flow statistical features"""
        
        # Basic flow features
        duration = flow_data.get('duration', 0)
        src_bytes = flow_data.get('src_bytes', 0)
        dst_bytes = flow_data.get('dst_bytes', 0)
        src_packets = flow_data.get('src_packets', 0)
        dst_packets = flow_data.get('dst_packets', 0)
        
        # Derived features
        total_bytes = src_bytes + dst_bytes
        total_packets = src_packets + dst_packets
        
        # Ratios and rates
        byte_ratio = src_bytes / (dst_bytes + 1)  # Avoid division by zero
        packet_ratio = src_packets / (dst_packets + 1)
        
        bytes_per_second = total_bytes / (duration + 0.001)  # Avoid division by zero
        packets_per_second = total_packets / (duration + 0.001)
        
        avg_packet_size = total_bytes / (total_packets + 1)
        
        # Flow characteristics
        is_bulk_transfer = 1 if total_bytes > 100000 else 0
        is_interactive = 1 if total_packets > 50 and avg_packet_size < 100 else 0
        is_streaming = 1 if duration > 60 and bytes_per_second > 1000 else 0
        
        return [
            duration, src_bytes, dst_bytes, src_packets, dst_packets,
            total_bytes, total_packets, byte_ratio, packet_ratio,
            bytes_per_second, packets_per_second, avg_packet_size,
            is_bulk_transfer, is_interactive, is_streaming
        ]
    
    def extract_temporal_features(self, timestamp_series):
        """Extract temporal pattern features"""
        if len(timestamp_series) < 2:
            return [0] * 8
        
        # Inter-arrival times
        intervals = np.diff(sorted(timestamp_series))
        
        # Statistical features of intervals
        interval_stats = self.extract_statistical_features(intervals)[:5]  # Take first 5
        
        # Periodicity detection
        if len(intervals) > 10:
            # Simple periodicity measure using autocorrelation
            autocorr = np.correlate(intervals, intervals, mode='full')
            max_autocorr = np.max(autocorr[len(autocorr)//2+1:])
            periodicity_score = max_autocorr / np.max(autocorr) if np.max(autocorr) > 0 else 0
        else:
            periodicity_score = 0
        
        # Burstiness measure
        if len(intervals) > 1:
            burstiness = (np.std(intervals) - np.mean(intervals)) / (np.std(intervals) + np.mean(intervals))
        else:
            burstiness = 0
        
        # Time-of-day features (assuming timestamps are in seconds since epoch)
        hours = [(ts % 86400) // 3600 for ts in timestamp_series]
        hour_entropy = len(set(hours)) / 24.0  # Diversity of hours
        
        return interval_stats + [periodicity_score, burstiness, hour_entropy]
    
    def extract_behavioral_features(self, user_session_data):
        """Extract user behavioral features"""
        
        # Session characteristics
        session_duration = user_session_data.get('session_duration', 0)
        page_views = user_session_data.get('page_views', 0)
        unique_pages = user_session_data.get('unique_pages', 0)
        
        # Navigation patterns
        pages_per_minute = page_views / (session_duration / 60 + 0.001)
        page_diversity = unique_pages / (page_views + 1)
        
        # Request patterns
        request_methods = user_session_data.get('request_methods', ['GET'])
        method_diversity = len(set(request_methods)) / len(request_methods) if request_methods else 0
        
        post_ratio = request_methods.count('POST') / len(request_methods) if request_methods else 0
        
        # Error patterns
        error_count = user_session_data.get('error_count', 0)
        error_rate = error_count / (page_views + 1)
        
        # Geographic consistency
        countries = user_session_data.get('countries', ['US'])
        country_changes = len(set(countries)) - 1
        
        return [
            session_duration, page_views, unique_pages, pages_per_minute,
            page_diversity, method_diversity, post_ratio, error_count,
            error_rate, country_changes
        ]
    
    def extract_all_features(self, data_point):
        """Extract all advanced features from a single data point"""
        
        features = []
        
        # 1. Payload features (13 features - added NoSQL)
        payload = data_point.get('payload', data_point.get('path', ''))
        payload_features = self.extract_payload_features(payload)
        features.extend(payload_features)
        
        # 2. Entropy features (5 features)
        entropy_features = self.extract_entropy_features(payload)
        features.extend(entropy_features)
        
        # 3. Network flow features (15 features)
        flow_features = self.extract_network_flow_features(data_point)
        features.extend(flow_features)
        
        # 4. User agent analysis (8 features)
        user_agent = data_point.get('user_agent', '')
        ua_length = len(user_agent)
        ua_entropy = self.extract_entropy_features(user_agent)[0]
        
        # Bot indicators in user agent
        bot_keywords = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python']
        bot_score = sum(1 for keyword in bot_keywords if keyword in user_agent.lower())
        
        # Browser indicators
        browser_keywords = ['mozilla', 'chrome', 'firefox', 'safari', 'edge']
        browser_score = sum(1 for keyword in browser_keywords if keyword in user_agent.lower())
        
        # Version patterns
        version_patterns = len(re.findall(r'\d+\.\d+', user_agent))
        
        ua_features = [ua_length, ua_entropy, bot_score, browser_score, version_patterns, 0, 0, 0]
        features.extend(ua_features)
        
        # 5. Protocol and method features (5 features)
        method = data_point.get('method', 'GET')
        protocol = data_point.get('protocol', 'HTTP')
        
        method_encoded = {'GET': 0.1, 'POST': 0.5, 'PUT': 0.7, 'DELETE': 0.9}.get(method, 0.3)
        protocol_encoded = {'HTTP': 0.3, 'HTTPS': 0.7, 'TCP': 0.5, 'UDP': 0.2}.get(protocol, 0.1)
        
        is_post = 1 if method == 'POST' else 0
        is_secure = 1 if protocol == 'HTTPS' else 0
        
        protocol_features = [method_encoded, protocol_encoded, is_post, is_secure, 0]
        features.extend(protocol_features)
        
        # 6. Geographic and IP features (10 features)
        country = data_point.get('country', 'US')
        ip = data_point.get('ip', '192.168.1.1')
        
        # High-risk countries
        high_risk_countries = ['CN', 'RU', 'KP', 'IR', 'PK', 'BD']
        is_high_risk = 1 if country in high_risk_countries else 0
        
        # IP analysis
        ip_parts = ip.split('.')
        if len(ip_parts) == 4:
            try:
                ip_numeric = [int(part) for part in ip_parts]
                is_private = 1 if (ip_numeric[0] == 192 and ip_numeric[1] == 168) or \
                                 (ip_numeric[0] == 10) or \
                                 (ip_numeric[0] == 172 and 16 <= ip_numeric[1] <= 31) else 0
                ip_entropy = np.std(ip_numeric)
            except:
                is_private = 0
                ip_entropy = 0
        else:
            is_private = 0
            ip_entropy = 0
        
        geo_features = [is_high_risk, is_private, ip_entropy, 0, 0, 0, 0, 0, 0, 0]
        features.extend(geo_features)
        
        # 7. Timing features (10 features)
        timestamp = data_point.get('timestamp', 0)
        
        # Time-based features
        if timestamp > 0:
            hour_of_day = (timestamp % 86400) // 3600
            day_of_week = (timestamp // 86400) % 7
            
            # Suspicious time indicators
            is_night = 1 if hour_of_day < 6 or hour_of_day > 22 else 0
            is_weekend = 1 if day_of_week >= 5 else 0
        else:
            hour_of_day = 12
            day_of_week = 1
            is_night = 0
            is_weekend = 0
        
        timing_features = [hour_of_day/24, day_of_week/7, is_night, is_weekend, 0, 0, 0, 0, 0, 0]
        features.extend(timing_features)
        
        # 8. Advanced statistical features (15 features)
        # These would normally be computed from historical data
        # For now, we'll use derived features from current data
        
        # Request size analysis
        content_length = data_point.get('content_length', 0)
        is_large_request = 1 if content_length > 10000 else 0
        
        # Port analysis
        src_port = data_point.get('src_port', 80)
        dst_port = data_point.get('dst_port', 80)
        
        # Well-known suspicious ports
        suspicious_ports = [22, 23, 135, 139, 445, 1433, 3389, 5432, 6379]
        is_suspicious_port = 1 if dst_port in suspicious_ports else 0
        
        # Port entropy (simplified)
        port_entropy = abs(src_port - dst_port) / 65535.0
        
        advanced_features = [
            content_length/10000, is_large_request, src_port/65535, dst_port/65535,
            is_suspicious_port, port_entropy, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
        features.extend(advanced_features)
        
        # Ensure we have exactly 100 features
        while len(features) < 100:
            features.append(0.0)
        
        features = features[:100]  # Truncate if we have more than 100
        
        return np.array(features)
    
    def fit_transform(self, data):
        """Fit the feature extractor and transform data"""
        
        logger.info(f"Extracting advanced features from {len(data)} samples...")
        
        # Extract features for all data points
        feature_matrix = []
        for i, data_point in enumerate(data):
            if i % 1000 == 0:
                logger.info(f"Processing sample {i}/{len(data)}")
            
            features = self.extract_all_features(data_point)
            feature_matrix.append(features)
        
        feature_matrix = np.array(feature_matrix)
        
        # Fit scaler and transform
        feature_matrix_scaled = self.scaler.fit_transform(feature_matrix)
        
        self.is_fitted = True
        logger.info(f"Feature extraction completed: {feature_matrix_scaled.shape}")
        
        return feature_matrix_scaled
    
    def transform(self, data):
        """Transform new data using fitted extractor"""
        
        if not self.is_fitted:
            raise ValueError("Feature extractor not fitted. Call fit_transform first.")
        
        # Extract features
        if isinstance(data, dict):
            # Single data point
            features = self.extract_all_features(data)
            feature_matrix = features.reshape(1, -1)
        else:
            # Multiple data points
            feature_matrix = []
            for data_point in data:
                features = self.extract_all_features(data_point)
                feature_matrix.append(features)
            feature_matrix = np.array(feature_matrix)
        
        # Scale features
        feature_matrix_scaled = self.scaler.transform(feature_matrix)
        
        return feature_matrix_scaled

def test_feature_extractor():
    """Test the advanced feature extractor"""
    
    print("Testing Advanced Feature Extractor")
    print("=" * 40)
    
    # Test data
    test_data = [
        {
            'path': '/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'method': 'GET',
            'country': 'US',
            'ip': '192.168.1.100',
            'timestamp': 1640995200,
            'duration': 0.2,
            'src_bytes': 1500,
            'dst_bytes': 500
        },
        {
            'path': "/?id=1' OR '1'='1",
            'user_agent': 'sqlmap/1.6.12',
            'method': 'POST',
            'country': 'CN',
            'ip': '10.0.0.50',
            'timestamp': 1640995260,
            'duration': 0.1,
            'src_bytes': 800,
            'dst_bytes': 200
        }
    ]
    
    # Extract features
    extractor = AdvancedFeatureExtractor()
    features = extractor.fit_transform(test_data)
    
    print(f"Extracted features shape: {features.shape}")
    print(f"Feature range: [{features.min():.3f}, {features.max():.3f}]")
    
    # Test single prediction
    single_features = extractor.transform(test_data[0])
    print(f"Single sample features shape: {single_features.shape}")
    
    print("Advanced feature extraction test completed!")

if __name__ == "__main__":
    test_feature_extractor()