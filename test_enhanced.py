#!/usr/bin/env python3
"""
Enhanced Attack Testing with Rule-Based Detection
Much better accuracy than pure ML approach
"""

import sys
sys.path.append('backend')

from backend.ml.testing.enhanced_detector import test_enhanced_detection

if __name__ == "__main__":
    test_enhanced_detection()