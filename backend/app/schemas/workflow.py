"""Pydantic schemas for Workflow API."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Any


class WorkflowDefinitionCreate(BaseModel):
    """Schema for creating a new workflow."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    graph_json: dict[str, Any] = Field(..., description="React Flow graph JSON")


class WorkflowDefinitionUpdate(BaseModel):
    """Schema for updating a workflow."""

    name: str | None = None
    description: str | None = None
    graph_json: dict[str, Any] | None = None


class WorkflowDefinitionResponse(BaseModel):
    """Schema for workflow API responses."""

    id: UUID
    project_id: UUID
    name: str
    description: str | None
    graph_json: dict[str, Any]
    version: int
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowRunCreate(BaseModel):
    """Schema for creating a workflow run."""

    pass  # No additional fields needed, workflow_id comes from URL


class WorkflowRunResponse(BaseModel):
    """Schema for workflow run API responses."""

    id: UUID
    workflow_definition_id: UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    result_json: dict[str, Any] | None
    error_message: str | None
    created_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskRunResponse(BaseModel):
    """Schema for task run API responses."""

    id: UUID
    workflow_run_id: UUID
    node_id: str
    node_type: str
    status: str
    input_data: dict[str, Any] | None
    output_data: dict[str, Any] | None
    logs: str | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GraphValidationRequest(BaseModel):
    """Schema for graph validation requests."""

    graph_json: dict[str, Any]


class GraphValidationResponse(BaseModel):
    """Schema for graph validation responses."""

    valid: bool
    errors: list[str] = []
    warnings: list[str] = []


class ComponentDefinitionResponse(BaseModel):
    """Schema for component definition API responses."""

    id: str
    name: str
    category: str
    description: str | None
    config_json: dict[str, Any]
    icon: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
