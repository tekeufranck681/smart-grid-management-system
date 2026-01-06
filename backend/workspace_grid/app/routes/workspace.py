from uuid import UUID

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceListOut,
    WorkspaceOut,
    WorkspaceUpdate,
    WorkspaceWithGridsOut,
)
from app.services.workspace import WorkspaceService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])
workspace_service = WorkspaceService()


@router.post("/", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])
    result, code = await workspace_service.create_workspace(user_id, workspace_data, db)
    if code != 201:
        raise HTTPException(status_code=code, detail=result.get("error"))
    return result


@router.get("/", response_model=WorkspaceListOut)
async def list_workspaces(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])
    result = await workspace_service.list_workspaces(user_id, db)
    return result


@router.get("/{workspace_id}", response_model=WorkspaceWithGridsOut)
async def get_workspace(
    workspace_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])
    result, code = await workspace_service.get_workspace(workspace_id, user_id, db)
    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))
    return result


@router.put("/{workspace_id}", response_model=WorkspaceOut)
async def update_workspace(
    workspace_id: UUID,
    workspace_data: WorkspaceUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])
    result, code = await workspace_service.update_workspace(
        workspace_id, user_id, workspace_data, db
    )
    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))
    return result


@router.delete("/{workspace_id}", status_code=status.HTTP_200_OK)
async def delete_workspace(
    workspace_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])
    result, code = await workspace_service.delete_workspace(workspace_id, user_id, db)
    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))
    return result
