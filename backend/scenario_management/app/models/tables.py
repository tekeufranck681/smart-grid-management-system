import uuid
from datetime import datetime, timedelta
from typing import List

from app.database.connection import Base
from app.models.enums import EventType, ScenarioStatus, TargetType
from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Interval,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    base_grid_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    status: Mapped[ScenarioStatus] = mapped_column(
        Enum(ScenarioStatus),
        default=ScenarioStatus.DRAFT,
        nullable=False,
    )

    created_by: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # one → one (immutable snapshot)
    grid_snapshot: Mapped["ScenarioGridSnapshot"] = relationship(
        back_populates="scenario",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # one → many (event definitions)
    events: Mapped[List["ScenarioEvent"]] = relationship(
        back_populates="scenario",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ScenarioGridSnapshot(Base):
    __tablename__ = "scenario_grid_snapshots"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    scenario_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # enforce 1–1 at DB level
    )

    nodes: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    edges: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    grid_metadata: Mapped[dict | None] = mapped_column(
        JSON,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    scenario: Mapped["Scenario"] = relationship(
        back_populates="grid_snapshot",
    )


class ScenarioEvent(Base):
    __tablename__ = "scenario_events"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    scenario_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType),
        nullable=False,
    )

    target_type: Mapped[TargetType] = mapped_column(
        Enum(TargetType),
        nullable=False,
    )

    target_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    parameters: Mapped[dict | None] = mapped_column(
        JSON,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    duration: Mapped[timedelta] = mapped_column(Interval, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    scenario: Mapped["Scenario"] = relationship(
        back_populates="events",
    )
