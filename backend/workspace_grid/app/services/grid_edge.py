import logging
from uuid import UUID

from app.cache.cache_service import CacheService
from app.models.tables import Grid, GridEdge, GridEdgeStatus, GridNode
from app.schemas.grid_edge import (
    GridEdgeCreate,
    GridEdgeOut,
    GridEdgeStateUpdate,
    GridEdgeUpdate,
)
from fastapi import HTTPException
from sentry_sdk import metrics
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload

logger = logging.getLogger("grid_edge_service")


ALLOWED_FLOW = {
    "plant": {"substation", "load"},
    "substation": {"substation", "load"},
    "load": set(),
}


class GridEdgeService:
    def __init__(self):
        self.cache = CacheService(namespace="gridedge")
        self.grid_node_cache = CacheService(namespace="gridnode")
        self.grid_cache = CacheService(namespace="grid")
        self.detail_cache_ttl = 300  # 5 min

    # Add Edge (Connect Two Nodes)
    async def create_edge(
        self,
        grid_id: UUID,
        user_id: UUID,
        data: GridEdgeCreate,
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

            # Validate nodes belong to same grid
            nodes_stmt = select(GridNode).where(
                GridNode.id.in_([data.from_node_id, data.to_node_id]),
                GridNode.grid_id == grid_id,
            )
            nodes_result = await db.execute(nodes_stmt)
            nodes = nodes_result.scalars().all()

            if len(nodes) != 2:
                return {"error": "Invalid nodes for grid"}, 400

            from_node = next(n for n in nodes if n.id == data.from_node_id)
            to_node = next(n for n in nodes if n.id == data.to_node_id)

            allowed_targets = ALLOWED_FLOW.get(from_node.type)

            if allowed_targets is None:
                return {"error": f"Unsupported node type: {from_node.type.value}"}, 400

            if to_node.type not in allowed_targets:
                return {
                    "error": f"Invalid power flow: {from_node.type.value} → {to_node.type.value}"
                }, 400

            if data.from_node_id == data.to_node_id:
                return {"error": "Self-loop edges are not allowed"}, 400

            # Prevent duplicate edges (bidirectional check)
            dup_stmt = select(GridEdge).where(
                and_(
                    GridEdge.grid_id == grid_id,
                    or_(
                        and_(
                            GridEdge.from_node_id == data.from_node_id,
                            GridEdge.to_node_id == data.to_node_id,
                        ),
                        and_(
                            GridEdge.from_node_id == data.to_node_id,
                            GridEdge.to_node_id == data.from_node_id,
                        ),
                    ),
                )
            )
            dup_result = await db.execute(dup_stmt)
            if dup_result.scalar_one_or_none():
                return {"error": "Edge already exists between nodes"}, 409

            edge = GridEdge(
                grid_id=grid_id,
                from_node_id=data.from_node_id,
                to_node_id=data.to_node_id,
                capacity_mw=data.capacity_mw,
                resistance=data.resistance,
                losses_percent=data.losses_percent,
                priority=data.priority or 0,
                status=GridEdgeStatus.ACTIVE,
            )

            db.add(edge)
            await db.commit()
            await db.refresh(edge)

            # Invalidate grid topology cache
            await self.grid_node_cache.delete(f"node:{edge.from_node_id}:details")
            await self.grid_node_cache.delete(f"node:{edge.to_node_id}:details")
            await self.grid_cache.delete(f"grid:{grid_id}:details")

            metrics.count("gridedge.create.success", 1)
            return GridEdgeOut.model_validate(edge), 201

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create grid edge: {e}")
            metrics.count("gridedge.create.failure", 1)
            raise HTTPException(status_code=500, detail="Failed to create grid edge")

    # Get Edge
    async def get_edge(
        self,
        edge_id: UUID,
        user_id: UUID,
        db,
    ):
        try:
            cache_key = f"edge:{edge_id}:details"
            cached = await self.cache.get(cache_key)

            if cached:
                metrics.count("gridedge.get.cache_hit", 1)
                return GridEdgeOut(**cached), 200

            stmt = (
                select(GridEdge)
                .options(selectinload(GridEdge.grid).selectinload(Grid.workspace))
                .where(GridEdge.id == edge_id)
            )
            result = await db.execute(stmt)
            edge = result.scalar_one_or_none()

            if not edge:
                return {"error": "Grid edge not found"}, 404
            if edge.grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            edge_data = GridEdgeOut.model_validate(edge)

            await self.cache.set(
                cache_key,
                edge_data.model_dump(mode="json"),
                ttl=self.detail_cache_ttl,
            )

            metrics.count("gridedge.get.cache_miss", 1)
            return edge_data, 200

        except Exception as e:
            logger.error(f"Failed to fetch grid edge: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch grid edge")

    # Update Edge Attributes
    async def update_edge(
        self,
        edge_id: UUID,
        user_id: UUID,
        data: GridEdgeUpdate,
        db,
    ):
        try:
            stmt = (
                select(GridEdge)
                .options(selectinload(GridEdge.grid).selectinload(Grid.workspace))
                .where(GridEdge.id == edge_id)
            )
            result = await db.execute(stmt)
            edge = result.scalar_one_or_none()

            if not edge:
                return {"error": "Grid edge not found"}, 404
            if edge.grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(edge, field, value)

            db.add(edge)
            await db.commit()
            await db.refresh(edge)

            # Invalidate caches
            await self.cache.delete(f"edge:{edge_id}:details")
            await self.grid_node_cache.delete(f"node:{edge.from_node_id}:details")
            await self.grid_node_cache.delete(f"node:{edge.to_node_id}:details")
            await self.grid_cache.delete(f"grid:{edge.grid_id}:details")

            return GridEdgeOut.model_validate(edge), 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update grid edge: {e}")
            raise HTTPException(status_code=500, detail="Failed to update grid edge")

    # Update Persistent Edge State
    async def update_edge_state(
        self,
        edge_id: UUID,
        user_id: UUID,
        data: GridEdgeStateUpdate,
        db,
    ):
        try:
            stmt = (
                select(GridEdge)
                .options(selectinload(GridEdge.grid).selectinload(Grid.workspace))
                .where(GridEdge.id == edge_id)
            )
            result = await db.execute(stmt)
            edge = result.scalar_one_or_none()

            if not edge:
                return {"error": "Grid edge not found"}, 404
            if edge.grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            if data.status not in GridEdgeStatus:
                return {"error": "Invalid edge state"}, 400

            edge.status = data.status

            db.add(edge)
            await db.commit()
            await db.refresh(edge)

            # Invalidate caches
            await self.cache.delete(f"edge:{edge_id}:details")
            await self.grid_node_cache.delete(f"node:{edge.from_node_id}:details")
            await self.grid_node_cache.delete(f"node:{edge.to_node_id}:details")
            await self.grid_cache.delete(f"grid:{edge.grid_id}:details")

            return GridEdgeOut.model_validate(edge), 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update edge state: {e}")
            raise HTTPException(status_code=500, detail="Failed to update edge state")

    # Delete Edge
    async def delete_edge(
        self,
        edge_id: UUID,
        user_id: UUID,
        db,
    ):
        try:
            stmt = (
                select(GridEdge)
                .options(selectinload(GridEdge.grid).selectinload(Grid.workspace))
                .where(GridEdge.id == edge_id)
            )
            result = await db.execute(stmt)
            edge = result.scalar_one_or_none()

            if not edge:
                return {"error": "Grid edge not found"}, 404
            if edge.grid.workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            grid_id = edge.grid_id

            await db.delete(edge)
            await db.commit()

            # Invalidate caches
            await self.cache.delete(f"edge:{edge_id}:details")
            await self.grid_node_cache.delete(f"node:{edge.from_node_id}:details")
            await self.grid_node_cache.delete(f"node:{edge.to_node_id}:details")
            await self.grid_cache.delete(f"grid:{grid_id}:details")

            metrics.count("gridedge.delete.success", 1)
            return {"message": "Grid edge deleted successfully"}, 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete grid edge: {e}")
            return {"error": "Failed to delete grid edge"}, 500
