"""Organization model - Top-level tenant boundary."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Organization(Base):
    """Organization represents a tenant in the multi-tenant platform.

    All users, projects, and resources belong to an organization.
    This provides the primary isolation boundary.
    """

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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

    # Relationships (will be populated as we add more models)
    # users: Mapped[list["User"]] = relationship(back_populates="organization")
    # projects: Mapped[list["Project"]] = relationship(back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name})>"
