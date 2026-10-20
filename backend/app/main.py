"""FastAPI main application for TecDot.AI - Unified AI Platform."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_tables
from app.api import health, organizations, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: startup and shutdown."""
    # Startup: Create database tables
    print("🚀 Starting TecDot.AI - Unified AI Platform...")
    print(f"📊 Database: {settings.database_url.split('@')[1]}")  # Hide password
    await create_tables()
    print("✅ Database tables created/verified")
    print(f"🌐 API running on http://{settings.api_host}:{settings.api_port}")
    print(f"📚 API docs: http://localhost:{settings.api_port}/docs")

    yield

    # Shutdown
    print("👋 Shutting down TecDot.AI...")


# Create FastAPI app
app = FastAPI(
    title="TecDot.AI - Unified AI Platform",
    description="A unified, web-first AI Engineering Platform for building, training, deploying, and operating AI systems",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(organizations.router)
app.include_router(projects.router)


@app.get("/")
async def root():
    """Root endpoint with platform information."""
    return {
        "message": "TecDot.AI - Unified AI Engineering Platform",
        "version": "0.1.0",
        "milestone": "M1 - Platform Foundation",
        "status": "development",
        "docs": "/docs",
        "health": "/health",
    }
