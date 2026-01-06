from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.enums import GridEdgeStatus
from pydantic import BaseModel


# Base
class GridEdgeBase(BaseModel):
    from_node_id: UUID
    to_node_id: UUID

    capacity_mw: float
    resistance: Optional[float] = None
    losses_percent: Optional[float] = None

    priority: int = 0
    status: GridEdgeStatus = GridEdgeStatus.ACTIVE


# Create / Update (for later use)
class GridEdgeCreate(GridEdgeBase):
    pass


class GridEdgeStateUpdate(BaseModel):
    status: GridEdgeStatus


class GridEdgeUpdate(BaseModel):
    capacity_mw: Optional[float] = None
    resistance: Optional[float] = None
    losses_percent: Optional[float] = None
    priority: Optional[int] = None
    status: Optional[GridEdgeStatus] = None


# Output
class GridEdgeOut(GridEdgeBase):
    id: UUID
    grid_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}  # Enables ORM-style parsing
