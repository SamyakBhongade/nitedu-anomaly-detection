from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        from app.core.database import create_tables
        create_tables()
    except Exception as e:
        print(f"Database setup failed: {e}")
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Cognitive Cyber Defense - Anomaly Detection",
    description="Real-time network anomaly detection",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers with error handling
try:
    from app.api.endpoints import events, alerts, websocket
    app.include_router(events.router, prefix="/api/v1", tags=["events"])
    app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
    app.include_router(websocket.router, tags=["websocket"])
except Exception as e:
    print(f"Router setup failed: {e}")
    # Add basic endpoints as fallback
    pass

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
        "message": "Cognitive Cyber Defense System - Anomaly Detection Module",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "anomaly-detection"}