import logging
from uuid import UUID

from app.cache.cache_service import CacheService
from app.models.tables import Grid, Workspace
from app.schemas.grid import GridCreate, GridWithRelationsOut
from app.schemas.grid_edge import GridEdgeCreate
from app.schemas.grid_node import GridNodeCreate
from app.schemas.import_grid import ImportGridPayload
from app.utils.import_util import ImportService
from fastapi import HTTPException
from sentry_sdk import metrics
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger("import_grid_service")


class GridImportService:
    def __init__(self):
        # ONLY workspace cache is relevant
        self.workspace_cache = CacheService(namespace="workspace")
        self.import_service = ImportService()

    async def import_grid(
        self,
        workspace_id: UUID,
        user_id: UUID,
        payload: ImportGridPayload,
        db: AsyncSession,
    ):
        try:
            # -------------------------
            # Validate workspace
            stmt = select(Workspace).where(Workspace.id == workspace_id)
            workspace = (await db.execute(stmt)).scalar_one_or_none()

            if not workspace:
                raise HTTPException(404, "Workspace not found")

            if workspace.owner_id != user_id:
                raise HTTPException(403, "Access denied")

            # Create grid (metadata only)
            grid = await self.import_service.create_grid(
                workspace=workspace,
                data=GridCreate(
                    name=payload.name,
                    description=payload.description,
                    base_power_mva=payload.base_power_mva,
                    voltage_level=payload.voltage_level,
                    is_active=payload.is_active,
                ),
                db=db,
            )

            # -------------------------
            # Create nodes and build JSON-ID → DB-ID map
            node_id_map: dict[str, UUID] = {}

            for node_payload in payload.nodes:
                node = await self.import_service.create_node(
                    grid=grid,
                    data=GridNodeCreate(
                        name=node_payload.name,
                        type=node_payload.type,
                        plant_type=node_payload.plant_type,
                        load_type=node_payload.load_type,
                        demand_mw=node_payload.demand_mw,
                        capacity_mw=node_payload.capacity_mw,
                        priority=node_payload.priority,
                        x=node_payload.x,
                        y=node_payload.y,
                    ),
                    db=db,
                )

                node_id_map[node_payload.client_id] = node.id

            # -------------------------
            # Create edges using mapped IDs
            for edge_payload in payload.edges:
                try:
                    from_node_id = node_id_map[edge_payload.from_node_id]
                    to_node_id = node_id_map[edge_payload.to_node_id]
                except KeyError:
                    raise HTTPException(
                        status_code=400, detail="Edge references unknown node id"
                    )

                await self.import_service.create_edge(
                    grid=grid,
                    data=GridEdgeCreate(
                        from_node_id=from_node_id,
                        to_node_id=to_node_id,
                        capacity_mw=edge_payload.capacity_mw,
                        resistance=edge_payload.resistance,
                        losses_percent=edge_payload.losses_percent,
                        priority=edge_payload.priority,
                    ),
                    db=db,
                )

            await db.commit()

            # -------------------------
            # Cache invalidation (workspace ONLY)
            await self.workspace_cache.delete(f"workspace:{workspace_id}")

            # -------------------------
            # Reload grid with relations for response
            stmt = (
                select(Grid)
                .options(
                    selectinload(Grid.nodes),
                    selectinload(Grid.edges),
                )
                .where(Grid.id == grid.id)
            )
            grid = (await db.execute(stmt)).scalar_one()

            metrics.count("import_grid.create.success", 1)
            return GridWithRelationsOut.model_validate(grid)

        except HTTPException:
            raise

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        except Exception:
            logger.exception("Grid import failed")
            metrics.count("import_grid.create.failure", 1)
            raise HTTPException(500, "Grid import failed")
