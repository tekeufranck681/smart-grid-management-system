from uuid import UUID

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.schemas.grid_node import (
    GridNodeCreate,
    GridNodeOut,
    GridNodePositionUpdate,
    GridNodeUpdate,
    GridNodeWithEdgesOut,
)
from app.services.grid_node import GridNodeService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/grids/{grid_id}/nodes",
    tags=["Grid Nodes"],
)

grid_node_service = GridNodeService()


@router.post(
    "/",
    response_model=GridNodeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_grid_node(
    grid_id: UUID,
    node_data: GridNodeCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_node_service.create_node(
        grid_id=grid_id,
        user_id=user_id,
        data=node_data,
        db=db,
    )

    if code != 201:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.get(
    "/{node_id}",
    response_model=GridNodeWithEdgesOut,
)
async def get_grid_node(
    grid_id: UUID,
    node_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_node_service.get_node(
        grid_id=grid_id,
        node_id=node_id,
        user_id=user_id,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.patch(
    "/{node_id}/position",
    status_code=status.HTTP_200_OK,
)
async def update_grid_node_position(
    grid_id: UUID,
    node_id: UUID,
    position_data: GridNodePositionUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_node_service.update_node_position(
        node_id=node_id,
        user_id=user_id,
        data=position_data,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.put(
    "/{node_id}",
    response_model=GridNodeOut,
)
async def update_grid_node(
    grid_id: UUID,
    node_id: UUID,
    node_data: GridNodeUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_node_service.update_node(
        node_id=node_id,
        user_id=user_id,
        data=node_data,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.delete(
    "/{node_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_grid_node(
    grid_id: UUID,
    node_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_node_service.delete_node(
        node_id=node_id,
        user_id=user_id,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result
