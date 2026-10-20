"""Pydantic schemas for Organization API."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    """Schema for creating a new organization."""

    name: str = Field(..., min_length=1, max_length=255, description="Organization name")


class OrganizationResponse(BaseModel):
    """Schema for organization API responses."""

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
