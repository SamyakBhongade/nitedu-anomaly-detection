#!/usr/bin/env python3
"""
Critical Attack Testing for nitedu.in Cognitive Cyber Defense
Run this to test your anomaly detection against real attack patterns
"""

import sys
import os
sys.path.append('backend')

from backend.ml.testing.test_detection import DetectionTester
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    print("🛡️ COGNITIVE CYBER DEFENSE - ATTACK TESTING")
    print("=" * 50)
    
    tester = DetectionTester()
    
    # Individual attack tests
    attacks = {
        '1': ('sql_injection', 'SQL Injection'),
        '2': ('xss_attack', 'Cross-Site Scripting (XSS)'),
        '3': ('ddos_attack', 'DDoS Attack'),
        '4': ('bot_scraping', 'Bot Scraping'),
        '5': ('brute_force', 'Brute Force Login'),
        '6': ('all', 'All Attacks (Comprehensive)')
    }
    
    print("\nSelect attack to test:")
    for key, (_, name) in attacks.items():
        print(f"  {key}. {name}")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == '6':
        print("\n🚀 Running comprehensive attack testing...")
        results = tester.run_all_tests()
        
        print(f"\n🎯 PROTECTION STATUS FOR nitedu.in:")
        overall = sum(results.values()) / len(results)
        if overall > 80:
            print("🟢 EXCELLENT - Your site is well protected!")
        elif overall > 60:
            print("🟡 GOOD - Decent protection, some improvements possible")
        else:
            print("🔴 NEEDS WORK - Consider enhancing detection models")
            
    elif choice in attacks and choice != '6':
        attack_type, attack_name = attacks[choice]
        print(f"\n🚨 Testing {attack_name}...")
        detection_rate, _ = tester.test_attack(attack_type, 20)
        
        if detection_rate > 80:
            print(f"✅ EXCELLENT protection against {attack_name}")
        elif detection_rate > 60:
            print(f"⚠️ MODERATE protection against {attack_name}")
        else:
            print(f"❌ WEAK protection against {attack_name}")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()