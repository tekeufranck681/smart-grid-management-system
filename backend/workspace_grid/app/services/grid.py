import logging
from uuid import UUID

from app.cache.cache_service import CacheService
from app.models.tables import Grid, GridNode, Workspace
from app.schemas.grid import (
    GridCreate,
    GridListOut,
    GridOut,
    GridUpdate,
    GridWithRelationsOut,
)
from fastapi import HTTPException
from sentry_sdk import metrics
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

logger = logging.getLogger("grid_service")


class GridService:
    def __init__(self):
        self.cache = CacheService(namespace="grid")
        self.workspace_cache = CacheService(namespace="workspace")
        self.list_cache_ttl = 600  # 10 min
        self.detail_cache_ttl = 300  # 5 min

    # Create Grid
    async def create_grid(
        self,
        workspace_id: UUID,
        user_id: UUID,
        data: GridCreate,
        db,
    ):
        try:
            # Verify workspace exists & ownership
            stmt = select(Workspace).where(Workspace.id == workspace_id)
            result = await db.execute(stmt)
            workspace = result.scalar_one_or_none()

            if not workspace:
                return {"error": "Workspace not found"}, 404
            if workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            # Case-insensitive grid name uniqueness per workspace
            stmt = select(Grid).where(
                Grid.workspace_id == workspace_id,
                func.lower(Grid.name) == data.name.lower(),
            )
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                return {"error": f"Grid '{data.name}' already exists"}, 400

            grid = Grid(
                workspace_id=workspace_id,
                name=data.name,
                description=data.description,
                base_power_mva=data.base_power_mva,
                voltage_level=data.voltage_level,
                is_active=data.is_active,
            )

            db.add(grid)
            await db.commit()
            await db.refresh(grid)

            # Invalidate grid list cache
            await self.workspace_cache.delete(f"workspace:{workspace_id}")

            metrics.count("grid.create.success", 1)
            return GridOut.model_validate(grid), 201

        except Exception as e:
            await db.rollback()
            logger.error(f"Grid creation failed: {e}")
            metrics.count("grid.create.failure", 1)
            raise HTTPException(status_code=500, detail="Failed to create grid")

    # List Grids for Workspace
    async def list_grids_for_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID,
        db,
    ):
        try:
            cache_key = f"workspace:{workspace_id}:grids"
            cached = await self.cache.get(cache_key)
            if cached:
                metrics.count("grid.list.cache_hit", 1)
                return GridListOut(grids=cached), 200

            # Validate workspace access
            stmt = select(Workspace).where(Workspace.id == workspace_id)
            result = await db.execute(stmt)
            workspace = result.scalar_one_or_none()

            if not workspace:
                return {"error": "Workspace not found"}, 404
            if workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            stmt = select(Grid).where(Grid.workspace_id == workspace_id)
            result = await db.execute(stmt)
            grids = result.scalars().all()

            grid_list = [GridOut.model_validate(g) for g in grids]

            await self.cache.set(
                cache_key,
                [g.model_dump(mode="json") for g in grid_list],
                ttl=self.list_cache_ttl,
            )

            metrics.count("grid.list.cache_miss", 1)
            return GridListOut(grids=grid_list), 200

        except Exception as e:
            logger.error(f"Failed to list grids: {e}")
            raise HTTPException(status_code=500, detail="Failed to list grids")

    # Get Grid (with topology)
    async def get_grid(
        self,
        grid_id: UUID,
        user_id: UUID,
        db,
    ):
        try:
            cache_key = f"grid:{grid_id}:details"
            cached = await self.cache.get(cache_key)
            if cached:
                metrics.count("grid.get.cache_hit", 1)
                return GridWithRelationsOut(**cached), 200

            # Eager-load nodes and edges
            stmt = (
                select(Grid)
                .options(
                    selectinload(Grid.nodes).selectinload(GridNode.outgoing_edges),
                    selectinload(Grid.nodes).selectinload(GridNode.incoming_edges),
                    selectinload(Grid.edges),
                    selectinload(Grid.workspace),
                )
                .where(Grid.id == grid_id)
            )
            result = await db.execute(stmt)
            grid = result.scalar_one_or_none()

            if not grid:
                return {"error": "Grid not found"}, 404
            if grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            grid_data = GridWithRelationsOut.model_validate(grid)

            await self.cache.set(
                cache_key,
                grid_data.model_dump(mode="json"),
                ttl=self.detail_cache_ttl,
            )

            return grid_data, 200

        except Exception as e:
            logger.error(f"Failed to fetch grid: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch grid")

    # Update Grid Metadata
    async def update_grid(
        self,
        grid_id: UUID,
        user_id: UUID,
        data: GridUpdate,
        db,
    ):
        try:
            stmt = (
                select(Grid)
                .options(selectinload(Grid.workspace))
                .where(Grid.id == grid_id)
            )
            result = await db.execute(stmt)
            grid = result.scalar_one_or_none()

            if not grid:
                return {"error": "Grid not found"}, 404
            if grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            # Name uniqueness check
            if data.name and data.name.lower() != grid.name.lower():
                stmt = select(Grid).where(
                    Grid.workspace_id == grid.workspace_id,
                    func.lower(Grid.name) == data.name.lower(),
                )
                result = await db.execute(stmt)
                if result.scalar_one_or_none():
                    return {"error": f"Grid '{data.name}' already exists"}, 400
                grid.name = data.name

            if data.description is not None:
                grid.description = data.description
            if data.base_power_mva is not None:
                grid.base_power_mva = data.base_power_mva
            if data.voltage_level is not None:
                grid.voltage_level = data.voltage_level
            if data.is_active is not None:
                grid.is_active = data.is_active

            db.add(grid)
            await db.commit()
            await db.refresh(grid)

            # Invalidate caches
            await self.workspace_cache.delete(f"workspace:{grid.workspace_id}")
            await self.cache.delete(f"grid:{grid_id}:details")

            return GridOut.model_validate(grid), 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update grid: {e}")
            raise HTTPException(status_code=500, detail="Failed to update grid")

    # Delete Grid
    async def delete_grid(
        self,
        grid_id: UUID,
        user_id: UUID,
        db,
    ):
        try:
            stmt = (
                select(Grid)
                .options(selectinload(Grid.workspace))
                .where(Grid.id == grid_id)
            )
            result = await db.execute(stmt)
            grid = result.scalar_one_or_none()

            if not grid:
                return {"error": "Grid not found"}, 404
            if grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            workspace_id = grid.workspace_id

            await db.delete(grid)
            await db.commit()

            # Invalidate caches
            await self.workspace_cache.delete(f"workspace:{workspace_id}")
            await self.cache.delete(f"grid:{grid_id}:details")

            metrics.count("grid.delete.success", 1)
            return {"message": "Grid deleted successfully"}, 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete grid: {e}")
            return {"error": "Failed to delete grid"}, 500
