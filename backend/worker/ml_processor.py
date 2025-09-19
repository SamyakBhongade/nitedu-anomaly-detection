import asyncio
import logging
from pathlib import Path
from sqlalchemy.orm import Session
import sys
import os

# Add paths
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.models.database import AnomalyAlert
from app.api.endpoints.websocket import broadcast_alert
from ml.inference.real_time_detector import RealTimeAnomalyDetector

logger = logging.getLogger(__name__)

class MLProcessor:
    def __init__(self):
        self.detector = None
        self.db = None
        
    async def initialize(self):
        """Initialize ML models and database"""
        try:
            # Check if models exist
            models_dir = Path("data/models")
            lstm_path = models_dir / "lstm_autoencoder.pth"
            isolation_path = models_dir / "isolation_forest.joblib"
            
            if not (lstm_path.exists() and isolation_path.exists()):
                logger.error("❌ ML models not found. Please run training first.")
                logger.info("Run: python train_models.py")
                return False
            
            # Initialize detector
            self.detector = RealTimeAnomalyDetector(
                str(lstm_path),
                str(isolation_path),
                sequence_length=10
            )
            
            logger.info("✅ ML models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML processor: {e}")
            return False
    
    async def start_processing(self):
        """Start processing events from Redis queue"""
        if not self.detector:
            logger.error("ML detector not initialized")
            return
        
        logger.info("🔄 Starting event processing loop...")
        
        while True:
            try:
                # Get event from Redis queue
                event = redis_client.get_event()
                
                if event:
                    await self.process_event(event)
                else:
                    # No events, sleep briefly
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(1)
    
    async def process_event(self, event: dict):
        """Process single event through ML pipeline"""
        try:
            # Run ML inference
            result = self.detector.process_event(event)
            
            # Store alert in database
            await self.store_alert(result)
            
            # Broadcast if anomaly detected
            if result['is_anomaly']:
                await self.broadcast_anomaly_alert(result)
                logger.warning(f"🚨 Anomaly detected: {result['event_id']} (score: {result['anomaly_score']:.3f})")
            else:
                logger.info(f"✅ Normal event: {result['event_id']} (score: {result['anomaly_score']:.3f})")
                
        except Exception as e:
            logger.error(f"Failed to process event {event.get('id', 'unknown')}: {e}")
    
    async def store_alert(self, result: dict):
        """Store alert result in database"""
        try:
            db = SessionLocal()
            
            alert = AnomalyAlert(
                event_id=result['event_id'],
                timestamp=result['timestamp'],
                anomaly_score=result['anomaly_score'],
                confidence=result['confidence'],
                is_anomaly=result['is_anomaly'],
                reason=result['reason'],
                lstm_score=result['model_scores'].get('lstm_score', 0.0),
                isolation_score=result['model_scores'].get('isolation_score', 0.0),
                hybrid_score=result['model_scores'].get('hybrid_score', 0.0),
                event_details=result.get('event_details', {}),
                model_scores=result['model_scores'],
                status="new"
            )
            
            db.add(alert)
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    async def broadcast_anomaly_alert(self, result: dict):
        """Broadcast anomaly alert via WebSocket"""
        try:
            if result['is_anomaly']:
                await broadcast_alert(result)
        except Exception as e:
            logger.error(f"Failed to broadcast alert: {e}")