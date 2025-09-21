#!/usr/bin/env python3
"""
Comprehensive ML Model Testing Suite
Tests trained models with various attack scenarios and validates performance
"""

import sys
import time
import numpy as np
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from ml_inference_engine import MLInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelTester:
    """Comprehensive ML model testing"""
    
    def __init__(self):
        self.engine = MLInferenceEngine()
        self.test_results = {}
    
    def setup_engine(self):
        """Setup ML inference engine"""
        print("🔧 Setting up ML inference engine...")
        self.engine.load_models()
        
        if not self.engine.is_loaded:
            print("❌ Models not loaded. Please train models first:")
            print("   python ml_training_pipeline.py")
            return False
        
        print("✅ ML inference engine ready!")
        return True
    
    def generate_test_cases(self):
        """Generate comprehensive test cases"""
        
        test_cases = {
            'normal_traffic': [
                {
                    'name': 'Homepage visit',
                    'data': {
                        'path': '/',
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'method': 'GET',
                        'country': 'US',
                        'packet_count': 10,
                        'byte_count': 1500,
                        'duration': 0.2
                    },
                    'expected_anomaly': False
                },
                {
                    'name': 'About page',
                    'data': {
                        'path': '/about',
                        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                        'method': 'GET',
                        'country': 'CA',
                        'packet_count': 8,
                        'byte_count': 1200,
                        'duration': 0.15
                    },
                    'expected_anomaly': False
                },
                {
                    'name': 'Contact form',
                    'data': {
                        'path': '/contact',
                        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64)',
                        'method': 'POST',
                        'country': 'GB',
                        'packet_count': 12,
                        'byte_count': 2000,
                        'duration': 0.3
                    },
                    'expected_anomaly': False
                }
            ],
            
            'sql_injection': [
                {
                    'name': 'Classic SQL injection',
                    'data': {
                        'path': "/?id=1' OR '1'='1",
                        'user_agent': 'sqlmap/1.6.12',
                        'method': 'GET',
                        'country': 'CN',
                        'packet_count': 5,
                        'byte_count': 800,
                        'duration': 0.1
                    },
                    'expected_anomaly': True
                },
                {
                    'name': 'UNION SELECT attack',
                    'data': {
                        'path': '/login?user=admin&pass=\' UNION SELECT * FROM users--',
                        'user_agent': 'python-requests/2.28.1',
                        'method': 'POST',
                        'country': 'RU',
                        'packet_count': 3,
                        'byte_count': 600,
                        'duration': 0.05
                    },
                    'expected_anomaly': True
                },
                {
                    'name': 'DROP TABLE attack',
                    'data': {
                        'path': '/search?q=test\'; DROP TABLE users; --',
                        'user_agent': 'curl/7.68.0',
                        'method': 'GET',
                        'country': 'KP',
                        'packet_count': 4,
                        'byte_count': 500,
                        'duration': 0.08
                    },
                    'expected_anomaly': True
                }
            ],
            
            'xss_attacks': [
                {
                    'name': 'Script injection',
                    'data': {
                        'path': '/search?q=<script>alert("XSS")</script>',
                        'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)',
                        'method': 'GET',
                        'country': 'IR',
                        'packet_count': 6,
                        'byte_count': 700,
                        'duration': 0.12
                    },
                    'expected_anomaly': True
                },
                {
                    'name': 'JavaScript protocol',
                    'data': {
                        'path': '/redirect?url=javascript:alert(document.cookie)',
                        'user_agent': 'Mozilla/5.0',
                        'method': 'GET',
                        'country': 'CN',
                        'packet_count': 4,
                        'byte_count': 450,
                        'duration': 0.06
                    },
                    'expected_anomaly': True
                },
                {
                    'name': 'Event handler injection',
                    'data': {
                        'path': '/profile?name=<img src=x onerror=alert(1)>',
                        'user_agent': 'Mozilla/5.0',
                        'method': 'POST',
                        'country': 'RU',
                        'packet_count': 7,
                        'byte_count': 650,
                        'duration': 0.15
                    },
                    'expected_anomaly': True
                }
            ],
            
            'bot_attacks': [
                {
                    'name': 'SQLMap scanner',
                    'data': {
                        'path': '/vulnerable.php?id=1',
                        'user_agent': 'sqlmap/1.6.12#stable (http://sqlmap.org)',
                        'method': 'GET',
                        'country': 'CN',
                        'packet_count': 3,
                        'byte_count': 400,
                        'duration': 0.03
                    },
                    'expected_anomaly': True
                },
                {
                    'name': 'Aggressive crawler',
                    'data': {
                        'path': '/admin/config.php',
                        'user_agent': 'Mozilla/5.0 (compatible; Baiduspider/2.0)',
                        'method': 'GET',
                        'country': 'CN',
                        'packet_count': 15,
                        'byte_count': 300,
                        'duration': 0.02
                    },
                    'expected_anomaly': True
                },
                {
                    'name': 'Scraper bot',
                    'data': {
                        'path': '/api/data',
                        'user_agent': 'python-requests/2.28.1',
                        'method': 'GET',
                        'country': 'RU',
                        'packet_count': 20,
                        'byte_count': 200,
                        'duration': 0.01
                    },
                    'expected_anomaly': True
                }
            ],
            
            'ddos_attacks': [
                {
                    'name': 'High volume request',
                    'data': {
                        'path': '/',
                        'user_agent': 'Mozilla/5.0',
                        'method': 'GET',
                        'country': 'CN',
                        'packet_count': 200,
                        'byte_count': 50000,
                        'duration': 0.001
                    },
                    'expected_anomaly': True
                },
                {
                    'name': 'Rapid fire requests',
                    'data': {
                        'path': '/api/endpoint',
                        'user_agent': 'curl/7.68.0',
                        'method': 'POST',
                        'country': 'RU',
                        'packet_count': 150,
                        'byte_count': 30000,
                        'duration': 0.005
                    },
                    'expected_anomaly': True
                }
            ],
            
            'brute_force': [
                {
                    'name': 'Login brute force',
                    'data': {
                        'path': '/login',
                        'user_agent': 'python-requests/2.28.1',
                        'method': 'POST',
                        'country': 'CN',
                        'packet_count': 8,
                        'byte_count': 1000,
                        'duration': 0.5
                    },
                    'expected_anomaly': True
                },
                {
                    'name': 'Admin panel attack',
                    'data': {
                        'path': '/admin/login',
                        'user_agent': 'curl/7.68.0',
                        'method': 'POST',
                        'country': 'KP',
                        'packet_count': 5,
                        'byte_count': 800,
                        'duration': 0.3
                    },
                    'expected_anomaly': True
                }
            ]
        }
        
        return test_cases
    
    def run_test_category(self, category_name, test_cases):
        """Run tests for a specific category"""
        
        print(f"\n🚨 Testing {category_name.replace('_', ' ').title()}")
        print("-" * 50)
        
        results = {
            'total': len(test_cases),
            'correct': 0,
            'incorrect': 0,
            'details': []
        }
        
        for test_case in test_cases:
            start_time = time.time()
            
            # Run prediction
            prediction = self.engine.predict_anomaly(test_case['data'])
            
            inference_time = time.time() - start_time
            
            # Check if prediction matches expected
            predicted_anomaly = prediction.get('is_anomaly', False)
            expected_anomaly = test_case['expected_anomaly']
            is_correct = predicted_anomaly == expected_anomaly
            
            if is_correct:
                results['correct'] += 1
                status = "✅ PASS"
            else:
                results['incorrect'] += 1
                status = "❌ FAIL"
            
            # Store details
            result_detail = {
                'name': test_case['name'],
                'expected': expected_anomaly,
                'predicted': predicted_anomaly,
                'confidence': prediction.get('confidence', 0.0),
                'attack_type': prediction.get('attack_type', 'Unknown'),
                'inference_time': inference_time * 1000,
                'correct': is_correct
            }
            results['details'].append(result_detail)
            
            # Print result
            print(f"  {test_case['name']}: {status}")
            print(f"    Expected: {expected_anomaly}, Got: {predicted_anomaly}")
            print(f"    Confidence: {prediction.get('confidence', 0.0):.3f}")
            print(f"    Attack Type: {prediction.get('attack_type', 'Unknown')}")
            print(f"    Time: {inference_time*1000:.2f}ms")
        
        # Calculate accuracy
        accuracy = (results['correct'] / results['total']) * 100 if results['total'] > 0 else 0
        results['accuracy'] = accuracy
        
        print(f"\n📊 {category_name.title()} Results:")
        print(f"   Accuracy: {accuracy:.1f}% ({results['correct']}/{results['total']})")
        
        return results
    
    def run_comprehensive_test(self):
        """Run comprehensive ML model testing"""
        
        print("🛡️ COGNITIVE CYBER DEFENSE - ML MODEL TESTING")
        print("=" * 60)
        
        if not self.setup_engine():
            return
        
        # Generate test cases
        test_cases = self.generate_test_cases()
        
        # Run tests for each category
        overall_results = {}
        total_correct = 0
        total_tests = 0
        
        for category, cases in test_cases.items():
            results = self.run_test_category(category, cases)
            overall_results[category] = results
            
            total_correct += results['correct']
            total_tests += results['total']
        
        # Overall summary
        overall_accuracy = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Correct Predictions: {total_correct}")
        print(f"Overall Accuracy: {overall_accuracy:.1f}%")
        
        print(f"\n📈 CATEGORY BREAKDOWN:")
        for category, results in overall_results.items():
            status = "✅ EXCELLENT" if results['accuracy'] > 90 else "⚠️ GOOD" if results['accuracy'] > 70 else "❌ NEEDS WORK"
            print(f"  {category.replace('_', ' ').title()}: {results['accuracy']:.1f}% {status}")
        
        # Performance analysis
        all_times = []
        for results in overall_results.values():
            for detail in results['details']:
                all_times.append(detail['inference_time'])
        
        if all_times:
            avg_time = np.mean(all_times)
            max_time = np.max(all_times)
            min_time = np.min(all_times)
            
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"  Average Inference Time: {avg_time:.2f}ms")
            print(f"  Max Inference Time: {max_time:.2f}ms")
            print(f"  Min Inference Time: {min_time:.2f}ms")
        
        # Model info
        model_info = self.engine.get_model_info()
        print(f"\n🔧 MODEL CONFIGURATION:")
        print(f"  LSTM Available: {model_info['lstm_available']}")
        print(f"  Isolation Forest Available: {model_info['isolation_forest_available']}")
        print(f"  Feature Scaler Available: {model_info['scaler_available']}")
        
        # Final assessment
        if overall_accuracy > 90:
            print(f"\n🎉 EXCELLENT! Your ML models are production-ready!")
        elif overall_accuracy > 75:
            print(f"\n👍 GOOD! Your ML models show strong performance!")
        else:
            print(f"\n⚠️ NEEDS IMPROVEMENT! Consider retraining with more data.")
        
        return overall_results
    
    def benchmark_performance(self, num_requests=1000):
        """Benchmark inference performance"""
        
        print(f"\n🏃 PERFORMANCE BENCHMARK ({num_requests} requests)")
        print("-" * 50)
        
        # Generate random test data
        test_request = {
            'path': '/test',
            'user_agent': 'Mozilla/5.0',
            'method': 'GET',
            'country': 'US'
        }
        
        times = []
        
        for i in range(num_requests):
            start_time = time.time()
            self.engine.predict_anomaly(test_request)
            inference_time = time.time() - start_time
            times.append(inference_time * 1000)  # Convert to ms
        
        # Calculate statistics
        avg_time = np.mean(times)
        median_time = np.median(times)
        p95_time = np.percentile(times, 95)
        p99_time = np.percentile(times, 99)
        throughput = 1000 / avg_time  # Requests per second
        
        print(f"  Average Time: {avg_time:.2f}ms")
        print(f"  Median Time: {median_time:.2f}ms")
        print(f"  95th Percentile: {p95_time:.2f}ms")
        print(f"  99th Percentile: {p99_time:.2f}ms")
        print(f"  Throughput: {throughput:.0f} requests/second")

def main():
    """Main testing function"""
    tester = MLModelTester()
    
    # Run comprehensive tests
    results = tester.run_comprehensive_test()
    
    # Run performance benchmark
    tester.benchmark_performance(100)
    
    print(f"\n🚀 ML model testing completed!")
    print(f"Ready for backend integration!")

if __name__ == "__main__":
    main()