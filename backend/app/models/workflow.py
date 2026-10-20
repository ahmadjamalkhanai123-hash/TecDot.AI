"""Workflow definition and execution models."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class WorkflowDefinition(Base):
    """Workflow definition stores the visual graph configuration.

    Each workflow is a directed acyclic graph (DAG) of components.
    The graph_json field contains the React Flow node/edge structure.
    """

    __tablename__ = "workflow_definitions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    graph_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="React Flow nodes and edges JSON",
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<WorkflowDefinition(id={self.id}, name={self.name}, version={self.version})>"


class RunStatus(str, enum.Enum):
    """Workflow run execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowRun(Base):
    """Workflow run tracks execution of a workflow definition.

    Each run creates isolated execution of all tasks in the workflow graph.
    """

    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    workflow_definition_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[RunStatus] = mapped_column(
        SQLEnum(RunStatus),
        nullable=False,
        default=RunStatus.PENDING,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    result_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Final execution results",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    def __repr__(self) -> str:
        return f"<WorkflowRun(id={self.id}, status={self.status.value})>"


class TaskRun(Base):
    """Task run tracks execution of individual nodes in the workflow.

    Each node in the workflow graph creates a task run during execution.
    """

    __tablename__ = "task_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Node ID from the workflow graph",
    )
    node_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    status: Mapped[RunStatus] = mapped_column(
        SQLEnum(RunStatus),
        nullable=False,
        default=RunStatus.PENDING,
        index=True,
    )
    input_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Input parameters and data references",
    )
    output_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Output data and artifact references",
    )
    logs: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<TaskRun(id={self.id}, node_id={self.node_id}, status={self.status.value})>"


class ComponentDefinition(Base):
    """Component definition registry for available workflow node types.

    This stores the component configurations (inputs, outputs, parameters)
    that define what nodes users can add to their workflows.
    """

    __tablename__ = "component_definitions"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        comment="Component type ID (e.g., 'csv-source', 'train-model')",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="data-source, transform, ml-model, output",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    config_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Component configuration (inputs, outputs, parameters)",
    )
    icon: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<ComponentDefinition(id={self.id}, name={self.name}, category={self.category})>"
