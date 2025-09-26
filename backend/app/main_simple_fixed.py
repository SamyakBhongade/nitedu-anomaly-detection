from fastapi import FastAPI, Request
import json
from datetime import datetime

app = FastAPI(
    title="nitedu.in Protection",
    description="Cybersecurity API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def root():
    return {
        "message": "nitedu.in Protection Active", 
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "predict": "/api/v1/predict"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "nitedu-protection",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/predict")
async def predict(request: Request):
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
        
        path = str(data.get('path', '')).lower()
        user_agent = str(data.get('user_agent', '')).lower()
        
        # Simple detection
        is_attack = False
        attack_type = "Normal"
        confidence = 0.0
        
        if any(x in path for x in ['union', 'select', "' or '"]):
            is_attack = True
            attack_type = "SQL Injection"
            confidence = 0.8
        elif any(x in path for x in ['<script', 'alert(']):
            is_attack = True
            attack_type = "XSS"
            confidence = 0.7
        elif any(x in user_agent for x in ['sqlmap', 'bot']):
            is_attack = True
            attack_type = "Bot"
            confidence = 0.6
        
        return {
            "event_id": f"evt_{int(datetime.now().timestamp())}",
            "is_anomaly": is_attack,
            "confidence": confidence,
            "attack_type": attack_type,
            "method": "simple_rules",
            "source_ip": request.client.host,
            "timestamp": datetime.now().isoformat()
        }
    except:
        return {"is_anomaly": False, "confidence": 0.0, "attack_type": "Normal"}

@app.get("/api/v1/status")
def get_status():
    return {
        "system_status": "operational",
        "detection_method": "simple_rules",
        "version": "1.0.0",
        "uptime": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/alerts")
def get_alerts():
    # Return sample alert for testing
    return [
        {
            "id": f"alert_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat(),
            "event_type": "System Monitoring",
            "source_ip": "system",
            "confidence": 0.1,
            "attack_type": "Normal"
        }
    ]