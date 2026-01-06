from datetime import datetime
from typing import Annotated, List, Optional
from uuid import UUID

from app.models.enums import WorkspaceVisibility
from app.schemas.grid import GridOut
from pydantic import BaseModel, constr

# Input Schemas


class WorkspaceCreate(BaseModel):
    name: Annotated[str, constr(strip_whitespace=True, min_length=1, max_length=100)]
    description: Optional[str] = None
    visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE


class WorkspaceUpdate(BaseModel):
    name: Optional[
        Annotated[str, constr(strip_whitespace=True, min_length=1, max_length=100)]
    ]
    description: Optional[str] = None
    visibility: Optional[WorkspaceVisibility] = None


# Output Schemas


class WorkspaceOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    owner_id: UUID
    visibility: WorkspaceVisibility
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}  # Enables ORM-style parsing


class WorkspaceWithGridsOut(WorkspaceOut):
    grids: List[GridOut] = []


class WorkspaceListOut(BaseModel):
    workspaces: List[WorkspaceOut]
