from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import create_tables
from app.api.endpoints import events, alerts, websocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Cognitive Cyber Defense - Anomaly Detection",
    description="Real-time network anomaly detection using LSTM + Isolation Forest",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router, prefix="/api/v1", tags=["events"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(websocket.router, tags=["websocket"])

@app.get("/")
async def root():
    return {
        "message": "Cognitive Cyber Defense System - Anomaly Detection Module",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "ingest": "/api/v1/ingest",
            "alerts": "/api/v1/alerts",
            "websocket": "/ws/alerts",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "anomaly-detection"}