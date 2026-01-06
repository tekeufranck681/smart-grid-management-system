from uuid import UUID

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioDetailOut,
    ScenarioEventCreate,
    ScenarioEventOut,
    ScenarioListOut,
    ScenarioOut,
    ScenarioUpdateStatus,
)
from app.services.scenario import ScenarioService
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/scenarios",
    tags=["Scenarios"],
)

scenario_service = ScenarioService()


@router.post(
    "/{grid_id}",
    response_model=ScenarioOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_scenario(
    grid_id: UUID,
    scenario_data: ScenarioCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new scenario from a base grid.

    - Copies full grid data into an immutable snapshot
    - Does NOT create events
    - Scenario starts in DRAFT status
    """
    user_id = UUID(current_user["id"])

    result = await scenario_service.create_scenario(
        user_id=user_id,
        grid_id=grid_id,
        data=scenario_data,
        db=db,
        request=request,
    )

    return result


@router.post(
    "/{scenario_id}/events",
    response_model=ScenarioEventOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_scenario_event(
    scenario_id: UUID,
    event_data: ScenarioEventCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # scenario_service already validates scenario access via JWT if needed
    result = await scenario_service.add_scenario_event(scenario_id, event_data, db)
    return result


@router.get("/{grid_id}/list", response_model=ScenarioListOut)
async def list_scenarios_by_grid(
    grid_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await scenario_service.list_scenarios_by_grid(grid_id, db)
    return result


@router.get("/{scenario_id}", response_model=ScenarioDetailOut)
async def view_scenario(
    scenario_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch scenario with read-only grid snapshot and events.
    Frontend can render scenario topology.
    """
    scenario_detail = await scenario_service.get_scenario(scenario_id, db)
    return scenario_detail


@router.patch("/{scenario_id}/status", response_model=ScenarioDetailOut)
async def update_scenario_status(
    scenario_id: UUID,
    payload: ScenarioUpdateStatus,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])
    scenario = await scenario_service.change_status(
        scenario_id, payload.new_status, user_id, db
    )
    return scenario


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(current_user["id"])
    result = await scenario_service.delete_scenario(scenario_id, user_id, db)
    return result
