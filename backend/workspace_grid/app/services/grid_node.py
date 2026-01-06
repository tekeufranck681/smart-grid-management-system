import logging
from uuid import UUID

from app.cache.cache_service import CacheService
from app.models.tables import Grid, GridNode
from app.schemas.grid_node import (
    GridNodeCreate,
    GridNodeOut,
    GridNodePositionUpdate,
    GridNodeUpdate,
    GridNodeWithEdgesOut,
)
from app.utils.node_type_validator import validate_node_attributes
from fastapi import HTTPException
from sentry_sdk import metrics
from sqlalchemy import select
from sqlalchemy.orm import selectinload

logger = logging.getLogger("grid_node_service")


class GridNodeService:
    def __init__(self):
        self.cache = CacheService(namespace="gridnode")
        self.grid_cache = CacheService(namespace="grid")
        self.detail_cache_ttl = 300  # 5 min

    # Add Node to Grid
    async def create_node(
        self,
        grid_id: UUID,
        user_id: UUID,
        data: GridNodeCreate,
        db,
    ):
        try:
            # Validate grid + ownership
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

            # validate nodes attributes
            validate_node_attributes(data.model_dump())

            node = GridNode(
                grid_id=grid_id,
                name=data.name,
                type=data.type,
                plant_type=data.plant_type,
                load_type=data.load_type,
                demand_mw=data.demand_mw,
                capacity_mw=data.capacity_mw,
                priority=data.priority,
                x=data.x,
                y=data.y,
            )

            db.add(node)
            await db.commit()
            await db.refresh(node)

            # Invalidate grid topology cache
            await self.grid_cache.delete(f"grid:{grid_id}:details")

            metrics.count("gridnode.create.success", 1)
            return GridNodeOut.model_validate(node), 201

        except HTTPException as he:
            raise he

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create grid node: {e}")
            metrics.count("gridnode.create.failure", 1)
            raise HTTPException(status_code=500, detail="Failed to create grid node")

    async def get_node(
        self,
        grid_id: UUID,
        node_id: UUID,
        user_id: UUID,
        db,
    ):
        try:
            cache_key = f"node:{node_id}:details"
            cached = await self.cache.get(cache_key)

            if cached:
                metrics.count("grid_node.get.cache_hit", 1)
                return GridNodeWithEdgesOut(**cached), 200

            stmt = (
                select(GridNode)
                .options(
                    selectinload(GridNode.outgoing_edges),
                    selectinload(GridNode.incoming_edges),
                    selectinload(GridNode.grid).selectinload(Grid.workspace),
                )
                .where(
                    GridNode.id == node_id,
                    GridNode.grid_id == grid_id,
                )
            )

            result = await db.execute(stmt)
            node = result.scalar_one_or_none()

            if not node:
                return {"error": "Grid node not found"}, 404

            if node.grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            node_data = GridNodeWithEdgesOut.model_validate(node)

            await self.cache.set(
                cache_key,
                node_data.model_dump(mode="json"),
                ttl=self.detail_cache_ttl,
            )

            metrics.count("grid_node.get.cache_miss", 1)
            return node_data, 200

        except Exception as e:
            logger.error(f"Failed to fetch grid node: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch grid node",
            )

    # Move Node (drag & drop)
    async def update_node_position(
        self,
        node_id: UUID,
        user_id: UUID,
        data: GridNodePositionUpdate,
        db,
    ):
        try:
            stmt = (
                select(GridNode)
                .options(selectinload(GridNode.grid).selectinload(Grid.workspace))
                .where(GridNode.id == node_id)
            )
            result = await db.execute(stmt)
            node = result.scalar_one_or_none()

            if not node:
                return {"error": "Node not found"}, 404
            if node.grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            node.x = data.x
            node.y = data.y

            db.add(node)
            await db.commit()

            # Invalidate grid cache
            await self.cache.delete(f"node:{node_id}:details")
            await self.grid_cache.delete(f"grid:{node.grid_id}:details")

            return {"message": "Node position updated"}, 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to move node: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update node position"
            )

    # Update Node Attributes
    async def update_node(
        self,
        node_id: UUID,
        user_id: UUID,
        data: GridNodeUpdate,
        db,
    ):
        try:
            stmt = (
                select(GridNode)
                .options(selectinload(GridNode.grid).selectinload(Grid.workspace))
                .where(GridNode.id == node_id)
            )
            result = await db.execute(stmt)
            node = result.scalar_one_or_none()

            if not node:
                return {"error": "Node not found"}, 404
            if node.grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            # Validate node attributes
            update_dict = data.model_dump(exclude_unset=True)
            # Merge with existing node values to validate full node
            full_node_data = {**node.__dict__, **update_dict}
            validate_node_attributes(full_node_data)

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(node, field, value)

            db.add(node)
            await db.commit()
            await db.refresh(node)

            # Invalidate grid cache
            await self.cache.delete(f"node:{node_id}:details")
            await self.grid_cache.delete(f"grid:{node.grid_id}:details")

            return GridNodeOut.model_validate(node), 200

        except HTTPException as he:
            raise he

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update node: {e}")
            raise HTTPException(status_code=500, detail="Failed to update node")

    # Delete Node
    async def delete_node(
        self,
        node_id: UUID,
        user_id: UUID,
        db,
    ):
        try:
            stmt = (
                select(GridNode)
                .options(selectinload(GridNode.grid).selectinload(Grid.workspace))
                .where(GridNode.id == node_id)
            )
            result = await db.execute(stmt)
            node = result.scalar_one_or_none()

            if not node:
                return {"error": "Node not found"}, 404
            if node.grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            grid_id = node.grid_id

            await db.delete(node)
            await db.commit()

            # Invalidate grid cache
            await self.cache.delete(f"node:{node_id}:details")
            await self.grid_cache.delete(f"grid:{grid_id}:details")

            metrics.count("gridnode.delete.success", 1)
            return {"message": "Node deleted successfully"}, 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete node: {e}")
            return {"error": "Failed to delete node"}, 500
