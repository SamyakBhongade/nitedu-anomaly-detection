from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Only import if not in production
if os.getenv("RENDER"):
    # Skip database and complex imports for Render
    app = FastAPI(
        title="Cognitive Cyber Defense - Anomaly Detection",
        description="Real-time network anomaly detection",
        version="1.0.0"
    )
else:
    from app.core.database import create_tables
    from app.api.endpoints import events, alerts, websocket

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        try:
            create_tables()
        except:
            pass  # Skip if fails
        yield
        # Shutdown
        pass

    app = FastAPI(
        title="Cognitive Cyber Defense - Anomaly Detection",
        description="Real-time network anomaly detection",
        version="1.0.0",
        lifespan=lifespan
    )

    # Include routers
    app.include_router(events.router, prefix="/api/v1", tags=["events"])
    app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
    app.include_router(websocket.router, tags=["websocket"])

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