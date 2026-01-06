from uuid import UUID

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.schemas.grid import (
    GridCreate,
    GridListOut,
    GridOut,
    GridUpdate,
    GridWithRelationsOut,
)
from app.services.grid import GridService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/grids", tags=["Grids"])
grid_service = GridService()


@router.post(
    "/workspaces/{workspace_id}/grids",
    response_model=GridOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_grid(
    workspace_id: UUID,
    grid_data: GridCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_service.create_grid(
        workspace_id=workspace_id,
        user_id=user_id,
        data=grid_data,
        db=db,
    )

    if code != 201:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.get(
    "/workspaces/{workspace_id}/grids",
    response_model=GridListOut,
)
async def list_grids_for_workspace(
    workspace_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_service.list_grids_for_workspace(
        workspace_id=workspace_id,
        user_id=user_id,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.get(
    "/{grid_id}",
    response_model=GridWithRelationsOut,
)
async def get_grid(
    grid_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_service.get_grid(
        grid_id=grid_id,
        user_id=user_id,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.put(
    "/{grid_id}",
    response_model=GridOut,
)
async def update_grid(
    grid_id: UUID,
    grid_data: GridUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_service.update_grid(
        grid_id=grid_id,
        user_id=user_id,
        data=grid_data,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.delete(
    "/{grid_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_grid(
    grid_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_service.delete_grid(
        grid_id=grid_id,
        user_id=user_id,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result
