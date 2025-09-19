from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.redis_client import redis_client
from app.schemas.events import NetworkEventCreate, NetworkEventResponse, IngestionResponse
from app.models.database import NetworkEvent

router = APIRouter()

@router.post("/ingest", response_model=IngestionResponse)
async def ingest_event(event: NetworkEventCreate, db: Session = Depends(get_db)):
    """Ingest network event for anomaly detection"""
    
    # Generate event ID
    event_id = f"evt_{uuid.uuid4().hex[:8]}"
    
    # Create database record
    db_event = NetworkEvent(
        src_ip=event.src_ip,
        dst_ip=event.dst_ip,
        src_port=event.src_port,
        dst_port=event.dst_port,
        protocol=event.protocol,
        packet_count=event.packet_count,
        byte_count=event.byte_count,
        duration=event.duration,
        timestamp=event.timestamp or datetime.utcnow(),
        raw_data=event.raw_data
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Prepare event for ML processing
    ml_event = {
        "id": event_id,
        "db_id": db_event.id,
        "timestamp": db_event.timestamp.isoformat(),
        "src_ip": event.src_ip,
        "dst_ip": event.dst_ip,
        "src_port": event.src_port,
        "dst_port": event.dst_port,
        "protocol": event.protocol,
        "packet_count": event.packet_count,
        "byte_count": event.byte_count,
        "duration": event.duration
    }
    
    # Queue for ML processing
    success = redis_client.publish_event(ml_event)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to queue event for processing")
    
    return IngestionResponse(
        success=True,
        event_id=event_id,
        message="Event ingested successfully",
        anomaly_detected=False  # Will be updated by ML worker
    )

@router.get("/events", response_model=List[NetworkEventResponse])
async def get_events(limit: int = 100, db: Session = Depends(get_db)):
    """Get recent network events"""
    events = db.query(NetworkEvent).order_by(NetworkEvent.created_at.desc()).limit(limit).all()
    return events