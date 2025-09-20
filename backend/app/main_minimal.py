from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Cognitive Cyber Defense", "status": "operational"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/v1/ingest")
def ingest(data: dict = None):
    if not data:
        data = {}
    
    path = str(data.get('path', '')).lower()
    user_agent = str(data.get('user_agent', '')).lower()
    
    score = 0.0
    if 'union' in path or 'select' in path or "' or '" in path:
        score += 0.8
    if 'script' in path or 'alert' in path:
        score += 0.7
    if 'sqlmap' in user_agent or 'bot' in user_agent:
        score += 0.6
    
    return {
        "is_anomaly": score > 0.5,
        "anomaly_score": min(score, 1.0),
        "reason": "Attack detected" if score > 0.5 else "Normal"
    }

@app.get("/api/v1/alerts")
def alerts():
    return [{"id": "test", "type": "SQL Injection", "score": 0.9}]