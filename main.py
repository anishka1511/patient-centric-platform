"""
Healthcare Symptom Assessment Agent - Main Application
FastAPI application for AI-powered symptom assessment and care navigation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from config.settings import settings
from config.logging_config import logger
from config.database import engine, Base
from routers import agent_routes
from routers.schemas import HealthCheckResponse
from api.routes import router as api_router  # Orchestrator routes

# Create FastAPI app
app = FastAPI(
    title="Medical Guidance Orchestrator API",
    version="0.1.0",
    description="AI-powered healthcare symptom assessment and care navigation system with hospital orchestration",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - Both input-agents and orchestrator
app.include_router(agent_routes.router)  # Symptom assessment routes
app.include_router(api_router)           # Hospital orchestration routes

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {'Development' if settings.is_development else 'Production'}")
    logger.info(f"Database: {settings.database_url}")
    
    # Create tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["system"])
async def health_check():
    """
    Health check endpoint
    
    Returns system status and connectivity information
    """
    # Test database connection
    db_connected = True
    try:
        from config.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_connected = False
    
    # Determine LLM service type
    from services.llm_service import llm_service
    llm_type = "Mock Service" if llm_service.use_mock else f"OpenAI ({settings.openai_model})"
    
    return HealthCheckResponse(
        status="healthy" if db_connected else "degraded",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        database_connected=db_connected,
        llm_service=llm_type
    )

# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "api_endpoints": {
            "symptom_assessment": "POST /api/assess",
            "conversation_history": "GET /api/conversation/{session_id}",
            "disclaimer": "GET /api/disclaimer",
            "hospital_orchestration": "POST /api/analyze"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
