import uuid
from datetime import datetime
from typing import List

from app.database.connection import Base
from app.models.enums import (
    GridEdgeStatus,
    GridNodeType,
    LoadType,
    PlantType,
    WorkspaceVisibility,
)
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    owner_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    visibility: Mapped[WorkspaceVisibility] = mapped_column(
        Enum(WorkspaceVisibility),
        default=WorkspaceVisibility.PRIVATE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # one → many
    grids: Mapped[List["Grid"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Grid(Base):
    __tablename__ = "grids"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    workspace_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)

    base_power_mva: Mapped[float] = mapped_column(Float, nullable=False)
    voltage_level: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # many → one
    workspace: Mapped["Workspace"] = relationship(back_populates="grids")

    # one → many
    nodes: Mapped[List["GridNode"]] = relationship(
        back_populates="grid",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    edges: Mapped[List["GridEdge"]] = relationship(
        back_populates="grid",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class GridNode(Base):
    __tablename__ = "grid_nodes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    grid_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grids.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    type: Mapped[GridNodeType] = mapped_column(Enum(GridNodeType), nullable=False)

    plant_type: Mapped[PlantType | None] = mapped_column(Enum(PlantType))
    load_type: Mapped[LoadType | None] = mapped_column(Enum(LoadType))

    demand_mw: Mapped[float | None] = mapped_column(Float)
    capacity_mw: Mapped[float | None] = mapped_column(Float)

    priority: Mapped[int] = mapped_column(Integer, default=0)

    x: Mapped[float | None] = mapped_column(Float)
    y: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # many to one
    grid: Mapped["Grid"] = relationship(back_populates="nodes")

    # self-referencing via GridEdge
    outgoing_edges: Mapped[list["GridEdge"]] = relationship(
        foreign_keys="GridEdge.from_node_id",
        back_populates="from_node",
    )

    incoming_edges: Mapped[list["GridEdge"]] = relationship(
        foreign_keys="GridEdge.to_node_id",
        back_populates="to_node",
    )


class GridEdge(Base):
    __tablename__ = "grid_edges"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    grid_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grids.id", ondelete="CASCADE"),
        nullable=False,
    )

    from_node_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grid_nodes.id", ondelete="CASCADE"),
        nullable=False,
    )

    to_node_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grid_nodes.id", ondelete="CASCADE"),
        nullable=False,
    )

    capacity_mw: Mapped[float] = mapped_column(Float, nullable=False)
    resistance: Mapped[float | None] = mapped_column(Float)
    losses_percent: Mapped[float | None] = mapped_column(Float)

    priority: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[GridEdgeStatus] = mapped_column(
        Enum(GridEdgeStatus),
        default=GridEdgeStatus.ACTIVE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    grid: Mapped["Grid"] = relationship(back_populates="edges")

    from_node: Mapped["GridNode"] = relationship(
        foreign_keys=[from_node_id],
        back_populates="outgoing_edges",
    )

    to_node: Mapped["GridNode"] = relationship(
        foreign_keys=[to_node_id],
        back_populates="incoming_edges",
    )
