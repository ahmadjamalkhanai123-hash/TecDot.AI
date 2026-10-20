"""Workflow management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import WorkflowDefinition, WorkflowRun, TaskRun, ComponentDefinition
from app.schemas.workflow import (
    WorkflowDefinitionCreate,
    WorkflowDefinitionUpdate,
    WorkflowDefinitionResponse,
    WorkflowRunCreate,
    WorkflowRunResponse,
    TaskRunResponse,
    GraphValidationRequest,
    GraphValidationResponse,
    ComponentDefinitionResponse,
)
from app.services.graph_validator import validate_workflow_graph
from app.services.executor import execute_workflow
from typing import List

router = APIRouter(prefix="/api/v1", tags=["Workflows"])


# Workflow Definition Endpoints
@router.post("/workflows/", response_model=WorkflowDefinitionResponse, status_code=201)
async def create_workflow(
    workflow_data: WorkflowDefinitionCreate,
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Create a new workflow definition."""
    new_workflow = WorkflowDefinition(
        project_id=project_id,
        name=workflow_data.name,
        description=workflow_data.description,
        graph_json=workflow_data.graph_json,
    )
    db.add(new_workflow)
    await db.commit()
    await db.refresh(new_workflow)
    return new_workflow


@router.get("/workflows/", response_model=List[WorkflowDefinitionResponse])
async def list_workflows(
    project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all workflows, optionally filtered by project."""
    query = select(WorkflowDefinition)
    if project_id:
        query = query.where(WorkflowDefinition.project_id == project_id)

    result = await db.execute(query.order_by(WorkflowDefinition.updated_at.desc()))
    workflows = result.scalars().all()
    return workflows


@router.get("/workflows/{workflow_id}", response_model=WorkflowDefinitionResponse)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific workflow by ID."""
    result = await db.execute(
        select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.patch("/workflows/{workflow_id}", response_model=WorkflowDefinitionResponse)
async def update_workflow(
    workflow_id: str,
    updates: WorkflowDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a workflow definition."""
    result = await db.execute(
        select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if updates.name is not None:
        workflow.name = updates.name
    if updates.description is not None:
        workflow.description = updates.description
    if updates.graph_json is not None:
        workflow.graph_json = updates.graph_json
        workflow.version += 1

    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.delete("/workflows/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a workflow definition."""
    result = await db.execute(
        select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    await db.delete(workflow)
    await db.commit()


# Graph Validation Endpoint
@router.post("/workflows/validate", response_model=GraphValidationResponse)
async def validate_graph(validation_request: GraphValidationRequest):
    """Validate a workflow graph without saving it."""
    validation_result = validate_workflow_graph(validation_request.graph_json)
    return validation_result


# Workflow Run Endpoints
@router.post("/runs/", response_model=WorkflowRunResponse, status_code=201)
async def create_workflow_run(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Start a new workflow execution.

    This creates a workflow run and triggers asynchronous execution.
    """
    # Get workflow definition
    result = await db.execute(
        select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Create workflow run
    new_run = WorkflowRun(
        workflow_definition_id=workflow_id,
        status="pending",
    )
    db.add(new_run)
    await db.commit()
    await db.refresh(new_run)

    # Trigger async execution (fire-and-forget)
    import asyncio
    asyncio.create_task(execute_workflow(str(new_run.id), workflow.graph_json, db))

    return new_run


@router.get("/runs/", response_model=List[WorkflowRunResponse])
async def list_runs(
    workflow_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all workflow runs, optionally filtered by workflow."""
    query = select(WorkflowRun)
    if workflow_id:
        query = query.where(WorkflowRun.workflow_definition_id == workflow_id)

    result = await db.execute(query.order_by(WorkflowRun.created_at.desc()))
    runs = result.scalars().all()
    return runs


@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific workflow run by ID."""
    result = await db.execute(
        select(WorkflowRun).where(WorkflowRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return run


@router.get("/runs/{run_id}/tasks", response_model=List[TaskRunResponse])
async def get_run_tasks(run_id: str, db: AsyncSession = Depends(get_db)):
    """Get all task runs for a specific workflow run."""
    result = await db.execute(
        select(TaskRun).where(TaskRun.workflow_run_id == run_id)
        .order_by(TaskRun.created_at)
    )
    tasks = result.scalars().all()
    return tasks


@router.post("/runs/{run_id}/cancel", response_model=WorkflowRunResponse)
async def cancel_run(run_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel a running workflow."""
    result = await db.execute(
        select(WorkflowRun).where(WorkflowRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    if run.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed run")

    run.status = "cancelled"
    await db.commit()
    await db.refresh(run)
    return run


# Component Registry Endpoints
@router.get("/components/", response_model=List[ComponentDefinitionResponse])
async def list_components(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all available component definitions."""
    query = select(ComponentDefinition).where(ComponentDefinition.is_active == True)
    if category:
        query = query.where(ComponentDefinition.category == category)

    result = await db.execute(query)
    components = result.scalars().all()
    return components


@router.get("/components/{component_id}", response_model=ComponentDefinitionResponse)
async def get_component(component_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific component definition."""
    result = await db.execute(
        select(ComponentDefinition).where(ComponentDefinition.id == component_id)
    )
    component = result.scalar_one_or_none()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component
