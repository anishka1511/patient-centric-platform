"""
Healthcare Symptom Assessment Agent - Main Application
FastAPI application for AI-powered symptom assessment and care navigation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
from pathlib import Path

from backend.config.settings import settings
from backend.config.logging_config import logger
from backend.config.database import engine, Base
from backend.routers import agent_routes, review_routes
from backend.routers.schemas import HealthCheckResponse
from backend.api.routes import router as api_router  # Orchestrator routes
from backend.fix_database_schema import fix_schema

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

# Mount static files
static_path = Path(__file__).parent / "static"
frontend_dist_path = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"Static files mounted from {static_path}")

frontend_assets_path = frontend_dist_path / "assets"
if frontend_assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_assets_path)), name="frontend-assets")
    logger.info(f"Frontend assets mounted from {frontend_assets_path}")

# Include routers - Both input-agents and orchestrator
app.include_router(agent_routes.router)  # Symptom assessment routes
app.include_router(review_routes.router)  # Patient reviews routes
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
        
        # Auto-fix database schema (add missing columns)
        logger.info("Checking database schema...")
        if fix_schema(silent=True):
            logger.info("Database schema up to date")
        else:
            logger.warning("Database schema fix encountered issues")
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
        from backend.config.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_connected = False
    
    # Determine LLM service type
    from backend.services.llm_service import llm_service
    llm_type = "Mock Service" if llm_service.use_mock else f"OpenAI ({settings.openai_model})"
    
    return HealthCheckResponse(
        status="healthy" if db_connected else "degraded",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        database_connected=db_connected,
        llm_service=llm_type
    )

# Root endpoint - Serve web interface
@app.get("/", include_in_schema=False)
async def root():
    """
    Serve the web interface
    """
    frontend_index_path = frontend_dist_path / "index.html"
    if frontend_index_path.exists():
        return FileResponse(frontend_index_path)

    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "message": "Web interface not found. Visit /docs for API documentation.",
            "docs": "/docs",
            "health": "/health"
        }

# API Info endpoint
@app.get("/api-info", tags=["system"])
async def api_info():
    """
    API information and available endpoints
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
            "reviews_list": "GET /api/reviews",
            "reviews_create": "POST /api/reviews",
            "hospital_orchestration": "POST /api/analyze"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
