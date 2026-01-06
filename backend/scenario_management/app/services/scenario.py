import logging
from uuid import UUID

from app.cache.cache_service import CacheService
from app.dependencies.grid import fetch_grid
from app.models.enums import ScenarioStatus, TargetType
from app.models.tables import Scenario, ScenarioEvent, ScenarioGridSnapshot
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioDetailOut,
    ScenarioEventCreate,
    ScenarioEventOut,
    ScenarioGridSnapshotOut,
    ScenarioListItem,
    ScenarioListOut,
    ScenarioOut,
)
from app.utils.scenario_validation import validate_event_parameters
from fastapi import HTTPException, Request
from sentry_sdk import metrics
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger("scenario_service")


class ScenarioService:
    def __init__(self):
        self.cache = CacheService(namespace="scenario")
        self.list_cache_ttl = 600  # 10 minutes
        self.detail_cache_ttl = 300  # 5 minutes

    async def create_scenario(
        self,
        user_id: UUID,
        grid_id: UUID,
        data: ScenarioCreate,
        db: AsyncSession,
        request: Request,
    ) -> ScenarioOut:
        """
        Create a new scenario with an immutable snapshot of the base grid.
        """

        # 1. Fetch full grid from Grid service (authorization handled there)
        grid_data = await fetch_grid(grid_id, request)
        # Case-insensitive uniqueness per workspace
        stmt = select(Scenario).where(
            Scenario.workspace_id == grid_data["workspace_id"],
            func.lower(Scenario.name) == data.name.lower(),
        )

        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Scenario '{data.name}' already exists in the workspace",
            )

        # 2. Create Scenario record
        scenario = Scenario(
            name=data.name,
            workspace_id=grid_data["workspace_id"],
            base_grid_id=grid_id,
            created_by=user_id,
        )

        db.add(scenario)
        try:
            await db.commit()
            await db.refresh(scenario)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            await db.rollback()
            metrics.count("scenario.create.failure", 1)
            logger.error(f"Failed to create scenario: {e}")
            raise HTTPException(status_code=500, detail="Failed to create scenario")

        # 3. Create immutable grid snapshot (LOSSLESS COPY)
        snapshot = ScenarioGridSnapshot(
            scenario_id=scenario.id,
            # Copy FULL arrays as-is
            nodes=grid_data["nodes"],
            edges=grid_data["edges"],
            # Copy ALL grid-level metadata
            grid_metadata={
                "id": grid_data.get("id"),
                "name": grid_data.get("name"),
                "description": grid_data.get("description"),
                "workspace_id": grid_data.get("workspace_id"),
                "base_power_mva": grid_data.get("base_power_mva"),
                "voltage_level": grid_data.get("voltage_level"),
                "is_active": grid_data.get("is_active"),
                "created_at": grid_data.get("created_at"),
                "updated_at": grid_data.get("updated_at"),
            },
        )

        db.add(snapshot)
        try:
            await db.commit()
            await db.refresh(snapshot)
        except Exception as e:
            await db.rollback()
            metrics.count("scenario.create.failure", 1)
            logger.error(f"Failed to create scenario snapshot: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to create scenario snapshot"
            )

        await self.cache.delete(f"grid:{grid_id}:scenarios")
        metrics.count("scenario.create.success", 1)

        return ScenarioOut.model_validate(scenario)

    async def add_scenario_event(
        self, scenario_id: UUID, data: ScenarioEventCreate, db: AsyncSession
    ) -> ScenarioEventOut:
        """
        Add an event to an existing scenario.
        Validates scenario status and event parameters.
        """

        # Fetch scenario with snapshot
        stmt = (
            select(Scenario)
            .options(selectinload(Scenario.grid_snapshot))
            .where(Scenario.id == scenario_id)
        )
        result = await db.execute(stmt)
        scenario = result.scalar_one_or_none()
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Refuse if scenario is locked or archived
        if scenario.status in ("LOCKED", "ARCHIVED"):
            raise HTTPException(
                status_code=409,
                detail="Cannot add events to a locked or archived scenario",
            )

        snapshot = scenario.grid_snapshot
        if not snapshot:
            raise HTTPException(status_code=500, detail="Scenario snapshot missing")

        # Validate parameters
        target_snapshot = None
        if data.target_type == TargetType.NODE or data.target_type == TargetType.ZONE:
            target_snapshot = snapshot.nodes
        elif data.target_type == TargetType.EDGE:
            target_snapshot = snapshot.edges

        validate_event_parameters(
            event_type=data.event_type,
            target_type=data.target_type,
            parameters=data.parameters,
            snapshot=target_snapshot,
            target_id=data.target_id,
        )

        # Persist event
        event = ScenarioEvent(
            scenario_id=scenario_id,
            event_type=data.event_type,
            target_type=data.target_type,
            target_id=data.target_id,
            parameters=data.parameters,
            start_time=data.start_time,
            duration=data.duration,
        )
        db.add(event)
        try:
            await db.commit()
            await db.refresh(event)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create scenario snapshot: {e}")
            raise HTTPException(status_code=500, detail="Failed to add scenario event")

        await self.cache.delete(f"scenario:{scenario.id}:details")
        await self.cache.delete(f"grid:{scenario.base_grid_id}:scenarios")
        return ScenarioEventOut.model_validate(event)

    async def list_scenarios_by_grid(self, grid_id: UUID, db):
        cache_key = f"grid:{grid_id}:scenarios"
        cached = await self.cache.get(cache_key)
        if cached:
            return ScenarioListOut(scenarios=cached)

        stmt = (
            select(Scenario)
            .where(Scenario.base_grid_id == grid_id)
            .order_by(Scenario.created_at.desc())
        )
        result = await db.execute(stmt)
        scenarios = result.scalars().all()

        scenario_list = [
            ScenarioListItem(
                id=s.id, name=s.name, status=s.status, created_at=s.created_at
            )
            for s in scenarios
        ]

        # Cache result
        await self.cache.set(
            cache_key,
            [s.model_dump(mode="json") for s in scenario_list],
            ttl=self.list_cache_ttl,
        )
        return ScenarioListOut(scenarios=scenario_list)

    async def get_scenario(self, scenario_id: UUID, db):
        cache_key = f"scenario:{scenario_id}:details"
        cached = await self.cache.get(cache_key)
        if cached:
            return ScenarioDetailOut(**cached)

        stmt = (
            select(Scenario)
            .options(
                selectinload(Scenario.grid_snapshot), selectinload(Scenario.events)
            )
            .where(Scenario.id == scenario_id)
        )
        result = await db.execute(stmt)
        scenario = result.scalar_one_or_none()
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        snapshot_pydantic = (
            ScenarioGridSnapshotOut.model_validate(scenario.grid_snapshot)
            if scenario.grid_snapshot
            else None
        )
        events_pydantic = [ScenarioEventOut.model_validate(e) for e in scenario.events]

        scenario_detail = ScenarioDetailOut.model_validate(
            {
                "id": scenario.id,
                "name": scenario.name,
                "workspace_id": scenario.workspace_id,
                "base_grid_id": scenario.base_grid_id,
                "status": scenario.status,
                "created_by": scenario.created_by,
                "created_at": scenario.created_at,
                "grid_snapshot": snapshot_pydantic,
                "events": events_pydantic,
            }
        )

        # Cache result
        await self.cache.set(
            cache_key,
            scenario_detail.model_dump(mode="json"),
            ttl=self.detail_cache_ttl,
        )
        return scenario_detail

    async def change_status(
        self, scenario_id: UUID, new_status: ScenarioStatus, user_id: UUID, db
    ):
        """
        Update the status of a scenario.
        """
        stmt = select(Scenario).where(Scenario.id == scenario_id)
        result = await db.execute(stmt)
        scenario = result.scalar_one_or_none()

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if scenario.created_by != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        scenario.status = new_status
        db.add(scenario)
        await db.commit()
        await db.refresh(scenario)

        await self.cache.delete(f"scenario:{scenario.id}:details")
        await self.cache.delete(f"grid:{scenario.base_grid_id}:scenarios")
        return ScenarioDetailOut.model_validate(scenario)

    async def delete_scenario(self, scenario_id: UUID, user_id: UUID, db):
        stmt = select(Scenario).where(Scenario.id == scenario_id)
        result = await db.execute(stmt)
        scenario = result.scalar_one_or_none()

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if scenario.created_by != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        try:
            await db.delete(scenario)
            await db.commit()
            metrics.count("scenario.delete.success", 1)

            await self.cache.delete(f"scenario:{scenario.id}:details")
            await self.cache.delete(f"grid:{scenario.base_grid_id}:scenarios")
            return {"message": "Scenario deleted successfully"}
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete scenario: {e}")
            metrics.count("scenario.delete.failure", 1)
            raise HTTPException(status_code=500, detail="Failed to delete scenario")
