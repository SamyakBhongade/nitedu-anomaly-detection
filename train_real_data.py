#!/usr/bin/env python3
"""
Train ML models using real network attack datasets:
- NSL-KDD: Network intrusion detection
- UNSW-NB15: Modern network attacks  
- CIC-IDS2017: Web attacks and DDoS
"""

import sys
sys.path.append('backend')

from backend.ml.training.real_data_trainer import main

if __name__ == "__main__":
    print("🚀 Training with Real Attack Datasets")
    print("=" * 40)
    print("📊 Datasets: NSL-KDD, UNSW-NB15, CIC-IDS2017")
    print("🎯 Target: nitedu.in protection")
    print()
    
    main()