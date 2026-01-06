from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.schemas.grid_edge import GridEdgeOut
from app.schemas.grid_node import GridNodeOut
from pydantic import BaseModel, Field


# Base
class GridBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_power_mva: float
    voltage_level: float
    is_active: bool = True


# Create / Update
class GridCreate(GridBase):
    pass


class GridUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_power_mva: Optional[float] = None
    voltage_level: Optional[float] = None
    is_active: Optional[bool] = None


# Output – Grid metadata only
class GridOut(GridBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}  # Enables ORM-style parsing


class GridWithRelationsOut(GridOut):
    nodes: List[GridNodeOut] = Field(default_factory=list)
    edges: List[GridEdgeOut] = Field(default_factory=list)


# List wrapper


class GridListOut(BaseModel):
    grids: List[GridOut]
