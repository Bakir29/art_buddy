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
    # Seed initial lessons if table is empty
    try:
        from app.entities.models import Lesson
        db = SessionLocal()
        if db.query(Lesson).count() == 0:
            seed_lessons = [
                Lesson(title="Understanding Color Wheels", content="Explore the fundamentals of color theory: primary, secondary, and tertiary colors, and how they relate to each other on the color wheel.", difficulty="beginner", category="color_theory", order_in_category=1, lesson_type="tutorial", duration_minutes=20),
                Lesson(title="Warm and Cool Colors", content="Learn how warm colors (reds, oranges, yellows) and cool colors (blues, greens, purples) affect mood and perception in artwork.", difficulty="beginner", category="color_theory", order_in_category=2, lesson_type="tutorial", duration_minutes=25),
                Lesson(title="Basic Line Drawing", content="Master the fundamental skill of line drawing: contour lines, gesture lines, and how to control pressure and direction.", difficulty="beginner", category="drawing_fundamentals", order_in_category=1, lesson_type="tutorial", duration_minutes=30),
                Lesson(title="Shapes and Forms", content="Learn to break down complex subjects into simple geometric shapes, and how to add volume to turn flat shapes into 3D forms.", difficulty="beginner", category="drawing_fundamentals", order_in_category=2, lesson_type="tutorial", duration_minutes=35),
                Lesson(title="Shading and Value", content="Understand light sources, shadow placement, and the full value scale from pure white to pure black. Practice rendering form with hatching and blending.", difficulty="intermediate", category="drawing_fundamentals", order_in_category=3, lesson_type="tutorial", duration_minutes=45),
                Lesson(title="One-Point Perspective", content="Learn how to draw realistic environments using one-point perspective. Understand vanishing points and horizon lines.", difficulty="intermediate", category="perspective", order_in_category=1, lesson_type="tutorial", duration_minutes=40),
                Lesson(title="Two-Point Perspective", content="Extend your perspective skills with two vanishing points to draw corners, buildings, and complex architectural scenes.", difficulty="intermediate", category="perspective", order_in_category=2, lesson_type="tutorial", duration_minutes=45),
                Lesson(title="Introduction to Digital Art", content="Get started with digital painting: learn about layers, brushes, canvas size, and the differences between raster and vector art.", difficulty="beginner", category="digital_art", order_in_category=1, lesson_type="tutorial", duration_minutes=30),
                Lesson(title="Digital Brushwork", content="Explore different brush types for digital painting — hard round, soft, textured — and how to build up form and texture digitally.", difficulty="intermediate", category="digital_art", order_in_category=2, lesson_type="tutorial", duration_minutes=40),
                Lesson(title="Color Harmony and Palettes", content="Learn advanced color harmony techniques: complementary, analogous, triadic, and split-complementary palettes. Create cohesive color schemes.", difficulty="intermediate", category="color_theory", order_in_category=3, lesson_type="exercise", duration_minutes=35),
            ]
            db.add_all(seed_lessons)
            db.commit()
            logger.info(f"Seeded {len(seed_lessons)} lessons")
        db.close()
    except Exception as e:
        logger.error(f"Could not seed lessons: {e}")
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