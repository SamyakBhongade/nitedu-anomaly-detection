from fastapi import FastAPI

app = FastAPI(
    title="Cognitive Cyber Defense",
    description="Real-time anomaly detection for nitedu.in",
    version="1.0.0"
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