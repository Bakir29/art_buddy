from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import os
from app.config import settings
from app.database import get_db, engine, SessionLocal
from app.entities.models import Base
from app.controllers import (
    auth_controller,
    user_controller,
    lesson_controller,
    progress_controller,
    recommendation_controller,
    ai_controller,
    mcp_controller,
    image_analysis_controller,
    analytics_controller,
    collaboration_controller,
    personalization_controller,
    offline_controller
)

# Import additional controllers
from app.workflows.workflow_controller import router as workflow_router
from app.controllers.dashboard_controller import router as dashboard_router
import logging

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        logger.info("pgvector extension ensured")
    except Exception as e:
        logger.warning(f"Could not create vector extension (may already exist): {e}")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Could not create database tables: {e}")
    # Seed full lesson catalogue (70 lessons, 350 quiz questions) if not already present
    try:
        from app.entities.models import Lesson
        from seed_data import create_sample_data
        db = SessionLocal()
        lesson_count = db.query(Lesson).count()
        db.close()
        if lesson_count < 70:
            logger.info(f"Found {lesson_count} lessons (expected 70) — running full seed…")
            create_sample_data(reset=True)
            logger.info("Full lesson + quiz seed complete")
        else:
            logger.info(f"Lesson catalogue already complete ({lesson_count} lessons)")
    except Exception as e:
        logger.error(f"Could not seed lessons: {e}")
    # Seed knowledge chunks if table is empty
    try:
        from app.entities.models import KnowledgeChunk
        db = SessionLocal()
        if db.query(KnowledgeChunk).count() == 0:
            seed_chunks = [
                KnowledgeChunk(content="Advanced shading requires understanding how light interacts with different surfaces. The core shadow is the darkest area on a curved form, located between the lit surface and the reflected light. Cast shadows are thrown by objects onto other surfaces, while form shadows exist on the object itself.", source="Advanced Light and Shadow Guide", chunk_index=1, chunk_metadata={"topic": "advanced_shading", "difficulty": "advanced"}),
                KnowledgeChunk(content="Composition is the arrangement of visual elements in artwork. The rule of thirds divides the canvas into nine sections, with important elements placed along the lines or intersections. Leading lines guide the viewer's eye through the composition, while visual weight creates balance.", source="Composition Fundamentals Manual", chunk_index=1, chunk_metadata={"topic": "composition", "difficulty": "intermediate"}),
                KnowledgeChunk(content="Figure drawing captures the human form through understanding anatomy and gesture. The line of action is the main flow that runs through a pose, expressing its energy and movement. Contrapposto creates natural-looking poses through weight shifts and opposing angles.", source="Figure Drawing Techniques", chunk_index=1, chunk_metadata={"topic": "figure_drawing", "difficulty": "advanced"}),
                KnowledgeChunk(content="Watercolor painting relies on water control and transparency. Wet-on-wet technique applies paint to damp paper for soft effects, while wet-on-dry creates sharp edges. Glazing involves applying transparent layers over dry paint to build rich, complex colors.", source="Watercolor Methods Handbook", chunk_index=1, chunk_metadata={"topic": "watercolor", "difficulty": "beginner"}),
                KnowledgeChunk(content="Character design uses shape language to convey personality. Circles suggest friendly, safe characters; squares indicate stable, trustworthy types; triangles imply dynamic or dangerous personalities. Strong silhouettes should be readable as solid black shapes.", source="Character Design Principles", chunk_index=1, chunk_metadata={"topic": "character_design", "difficulty": "intermediate"}),
                KnowledgeChunk(content="Oil painting techniques include fat-over-lean application, where thicker paint goes over thinner layers. Alla prima involves completing a painting in one session, while glazing builds transparent layers for luminous effects. Scumbling creates broken color through dry brush techniques.", source="Oil Painting Methods", chunk_index=1, chunk_metadata={"topic": "oil_painting", "difficulty": "advanced"}),
                KnowledgeChunk(content="Dynamic poses show energy through the line of action and asymmetrical positioning. Contrapposto creates natural weight shifts, while gesture drawing captures movement essence in quick sketches. Body language communicates emotion through posture and positioning.", source="Dynamic Figure Art Guide", chunk_index=1, chunk_metadata={"topic": "dynamic_poses", "difficulty": "intermediate"}),
                KnowledgeChunk(content="Landscape painting benefits from understanding atmospheric perspective, where distant objects appear lighter and cooler. Acrylic paints offer versatility for both transparent and opaque techniques. Sky should be painted first to establish lighting and mood for the entire composition.", source="Landscape Painting Techniques", chunk_index=1, chunk_metadata={"topic": "landscape_painting", "difficulty": "intermediate"}),
                KnowledgeChunk(content="Facial expressions communicate emotions through specific muscle movements. The six basic emotions are happiness, sadness, anger, fear, surprise, and disgust. Eyebrows are the primary emotion indicators, while eyes and mouth provide supporting expression cues.", source="Character Expression Reference", chunk_index=1, chunk_metadata={"topic": "facial_expressions", "difficulty": "intermediate"}),
            ]
            db.add_all(seed_chunks)
            db.commit()
            logger.info(f"Seeded {len(seed_chunks)} knowledge chunks")
        db.close()
    except Exception as e:
        logger.error(f"Could not seed knowledge chunks: {e}")
    yield

app = FastAPI(
    title="Art Buddy API",
    description="AI-powered art learning platform with RAG and MCP capabilities",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# CORS middleware
allow_origins = ["*"] if settings.environment == "development" else [
    settings.frontend_url,
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Art Buddy API",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "environment": settings.environment,
            "error": str(e)
        }


# Include API routers
app.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])
app.include_router(user_controller.router, prefix="/users", tags=["Users"])
app.include_router(lesson_controller.router, prefix="/lessons", tags=["Lessons"])
app.include_router(progress_controller.router, prefix="/progress", tags=["Progress"])
app.include_router(recommendation_controller.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(ai_controller.router, prefix="/ai", tags=["AI Tutor"])
app.include_router(mcp_controller.router, prefix="/mcp", tags=["MCP (Model Context Protocol)"])
app.include_router(image_analysis_controller.router, tags=["Image Analysis"])
app.include_router(analytics_controller.router, tags=["Advanced Analytics"])
app.include_router(collaboration_controller.router, tags=["Real-time Collaboration"])
app.include_router(personalization_controller.router, tags=["AI Personalization"])
app.include_router(offline_controller.router, tags=["Advanced Offline"])
app.include_router(workflow_router, tags=["Workflows"])
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )