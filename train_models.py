#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "backend"))

from ml.training.train_hybrid_model import HybridModelTrainer
import logging

logging.basicConfig(level=logging.INFO)

def main():
    Path("data/models").mkdir(parents=True, exist_ok=True)
    trainer = HybridModelTrainer()
    trainer.train_model(normal_samples=2000, anomaly_samples=100)
    print("✅ Models saved to data/models/")

if __name__ == "__main__":
    main()