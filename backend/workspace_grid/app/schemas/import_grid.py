from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ImportGridNode(BaseModel):
    client_id: str
    name: str
    type: str
    plant_type: Optional[str] = None
    load_type: Optional[str] = None
    demand_mw: Optional[float] = None
    capacity_mw: Optional[float] = None
    priority: int = 0
    x: float
    y: float


class ImportGridEdge(BaseModel):
    from_node_id: str
    to_node_id: str
    capacity_mw: float
    resistance: float
    losses_percent: float
    priority: Optional[int] = 0


class ImportGridPayload(BaseModel):
    name: str
    description: Optional[str] = None
    base_power_mva: float = Field(gt=0)
    voltage_level: float = Field(gt=0)
    is_active: bool = True

    nodes: List[ImportGridNode]
    edges: List[ImportGridEdge]

    @field_validator("nodes")
    @classmethod
    def validate_nodes_not_empty(cls, v):
        if not v:
            raise ValueError("Grid must contain at least one node")
        return v
