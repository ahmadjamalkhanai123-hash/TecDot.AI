"""Organization management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Organization
from app.schemas import OrganizationCreate, OrganizationResponse

router = APIRouter(prefix="/api/v1/organizations", tags=["Organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new organization.

    This will be visible immediately in PGAdmin!
    """
    new_org = Organization(name=org_data.name)
    db.add(new_org)
    await db.commit()
    await db.refresh(new_org)
    return new_org


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(db: AsyncSession = Depends(get_db)):
    """List all organizations."""
    result = await db.execute(select(Organization))
    organizations = result.scalars().all()
    return organizations


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(org_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific organization by ID."""
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
