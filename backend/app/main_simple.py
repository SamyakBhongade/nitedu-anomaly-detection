from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cognitive Cyber Defense",
    description="Real-time anomaly detection for nitedu.in",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Cognitive Cyber Defense - nitedu.in Protection",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nitedu-protection"}

@app.post("/api/v1/ingest")
async def ingest_event(event: dict):
    # Simple rule-based detection
    score = 0.0
    path = event.get('path', '').lower()
    user_agent = event.get('user_agent', '').lower()
    
    # SQL injection detection
    if any(x in path for x in ['union', 'select', 'drop', "' or '", '--']):
        score += 0.8
    
    # XSS detection  
    if any(x in path for x in ['<script', 'javascript:', 'alert(']):
        score += 0.7
        
    # Bot detection
    if any(x in user_agent for x in ['bot', 'curl', 'python', 'sqlmap']):
        score += 0.6
    
    is_anomaly = score > 0.5
    
    return {
        "event_id": f"evt_{event.get('timestamp', 0)}",
        "is_anomaly": is_anomaly,
        "anomaly_score": min(score, 1.0),
        "confidence": min(score, 1.0),
        "reason": "Attack detected" if is_anomaly else "Normal traffic"
    }

@app.get("/api/v1/alerts")
async def get_alerts():
    return [
        {
            "id": "alert_001",
            "timestamp": "2025-01-20T13:00:00Z",
            "anomaly_score": 0.95,
            "event_type": "SQL Injection Attempt",
            "source_ip": "10.0.0.50"
        }
    ]