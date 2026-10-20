"""Project management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    organization_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Create a new project.

    Watch this appear live in PGAdmin!
    """
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        organization_id=organization_id,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    organization_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all projects, optionally filtered by organization."""
    query = select(Project)
    if organization_id:
        query = query.where(Project.organization_id == organization_id)

    result = await db.execute(query)
    projects = result.scalars().all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific project by ID."""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
