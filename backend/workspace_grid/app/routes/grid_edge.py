from uuid import UUID

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.schemas.grid_edge import (
    GridEdgeCreate,
    GridEdgeOut,
    GridEdgeStateUpdate,
    GridEdgeUpdate,
)
from app.services.grid_edge import GridEdgeService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/grids/{grid_id}/edges",
    tags=["Grid Edges"],
)

grid_edge_service = GridEdgeService()


@router.post(
    "/",
    response_model=GridEdgeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_grid_edge(
    grid_id: UUID,
    edge_data: GridEdgeCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_edge_service.create_edge(
        grid_id=grid_id,
        user_id=user_id,
        data=edge_data,
        db=db,
    )

    if code != 201:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.get(
    "/{edge_id}",
    response_model=GridEdgeOut,
)
async def get_grid_edge(
    grid_id: UUID,
    edge_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_edge_service.get_edge(
        edge_id=edge_id,
        user_id=user_id,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.put(
    "/{edge_id}",
    response_model=GridEdgeOut,
)
async def update_grid_edge(
    grid_id: UUID,
    edge_id: UUID,
    edge_data: GridEdgeUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_edge_service.update_edge(
        edge_id=edge_id,
        user_id=user_id,
        data=edge_data,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.patch(
    "/{edge_id}/state",
    response_model=GridEdgeOut,
    status_code=status.HTTP_200_OK,
)
async def update_grid_edge_state(
    grid_id: UUID,
    edge_id: UUID,
    state_data: GridEdgeStateUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_edge_service.update_edge_state(
        edge_id=edge_id,
        user_id=user_id,
        data=state_data,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result


@router.delete(
    "/{edge_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_grid_edge(
    grid_id: UUID,
    edge_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])

    result, code = await grid_edge_service.delete_edge(
        edge_id=edge_id,
        user_id=user_id,
        db=db,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=result.get("error"))

    return result
