"""Pydantic schemas for Project API."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")


class ProjectResponse(BaseModel):
    """Schema for project API responses."""

    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
