import asyncio
import logging
import sys
import os
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from worker.ml_processor import MLProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main worker process"""
    logger.info("🚀 Starting ML Worker for anomaly detection...")
    
    processor = MLProcessor()
    
    # Initialize ML models
    await processor.initialize()
    
    # Start processing events
    await processor.start_processing()

if __name__ == "__main__":
    asyncio.run(main())