from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.models.enums import GridNodeType, LoadType, PlantType
from app.schemas.grid_edge import GridEdgeOut
from pydantic import BaseModel, Field


# Base schema (common fields)
class GridNodeBase(BaseModel):
    name: str
    type: GridNodeType

    # Plant attributes (only if type == PLANT)
    plant_type: Optional[PlantType] = None

    # Load attributes (only if type == LOAD)
    load_type: Optional[LoadType] = None
    demand_mw: Optional[float] = None
    capacity_mw: Optional[float] = None

    # Priority: for LOAD or PLANT
    priority: Optional[int] = None

    # Position
    x: Optional[float] = None
    y: Optional[float] = None


# Create schema
class GridNodeCreate(GridNodeBase):
    pass


# Update attributes (excluding position)
class GridNodeUpdate(BaseModel):
    name: Optional[str] = None
    plant_type: Optional[PlantType] = None
    load_type: Optional[LoadType] = None
    demand_mw: Optional[float] = None
    capacity_mw: Optional[float] = None
    priority: Optional[int] = None


# Position update (drag & drop)
class GridNodePositionUpdate(BaseModel):
    x: float
    y: float


# Output schema
class GridNodeOut(GridNodeBase):
    id: UUID
    grid_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Output with edges
class GridNodeWithEdgesOut(GridNodeOut):
    outgoing_edges: List[GridEdgeOut] = Field(default_factory=list)
    incoming_edges: List[GridEdgeOut] = Field(default_factory=list)
