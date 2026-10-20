"""Health check and status endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "TecDot.AI - Unified AI Platform",
        "version": "0.1.0",
        "milestone": "M1 - Platform Foundation",
    }


@router.get("/db")
async def database_health(db: AsyncSession = Depends(get_db)):
    """Check database connectivity."""
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return {
            "status": "healthy",
            "database": "PostgreSQL connected",
            "database_name": "TecDot.ai",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "PostgreSQL connection failed",
            "error": str(e),
        }
