from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from app.models.enums import EventType, ScenarioStatus, TargetType
from pydantic import BaseModel, Field

# ---------- Scenario Event Schemas ----------


class ScenarioEventCreate(BaseModel):
    event_type: EventType
    target_type: TargetType
    target_id: UUID
    parameters: Optional[dict] = None
    start_time: datetime
    duration: timedelta


class ScenarioEventOut(BaseModel):
    id: UUID
    scenario_id: UUID
    event_type: EventType
    target_type: TargetType
    target_id: UUID
    parameters: Optional[dict] = None
    start_time: datetime
    duration: timedelta
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Scenario Grid Snapshot ----------


class ScenarioGridSnapshotOut(BaseModel):
    id: UUID
    scenario_id: UUID
    nodes: List[dict]
    edges: List[dict]
    grid_metadata: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Scenario Schemas ----------


class ScenarioCreate(BaseModel):
    name: str


class ScenarioOut(BaseModel):
    id: UUID
    name: str
    workspace_id: UUID
    base_grid_id: UUID
    status: ScenarioStatus
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ScenarioDetailOut(ScenarioOut):
    grid_snapshot: ScenarioGridSnapshotOut
    events: List[ScenarioEventOut] = Field(default_factory=list)


class ScenarioListItem(BaseModel):
    id: UUID
    name: str
    status: ScenarioStatus
    created_at: datetime


class ScenarioListOut(BaseModel):
    scenarios: List[ScenarioListItem]


class ScenarioUpdateStatus(BaseModel):
    new_status: ScenarioStatus
