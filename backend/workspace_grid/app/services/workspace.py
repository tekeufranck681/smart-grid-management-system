import logging
from uuid import UUID

from app.cache.cache_service import CacheService
from app.models.tables import Workspace
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceListOut,
    WorkspaceOut,
    WorkspaceUpdate,
    WorkspaceWithGridsOut,
)
from fastapi import HTTPException
from sentry_sdk import metrics
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

logger = logging.getLogger("workspace_service")


class WorkspaceService:
    def __init__(self):
        self.cache = CacheService(namespace="workspace")
        self.list_cache_ttl = 900  # 15 min
        self.detail_cache_ttl = 600  # 10 min

    async def create_workspace(self, user_id: UUID, data: WorkspaceCreate, db):
        try:
            # Case-insensitive uniqueness per user
            stmt = select(Workspace).where(
                Workspace.owner_id == user_id,
                func.lower(Workspace.name) == data.name.lower(),
            )
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                return {
                    "error": f"A workspace with name '{data.name}' already exists"
                }, 400

            workspace = Workspace(
                name=data.name,
                description=data.description,
                owner_id=user_id,
                visibility=data.visibility.value,
            )
            db.add(workspace)
            await db.commit()
            await db.refresh(workspace)

            # Invalidate workspace list cache
            await self.cache.delete(f"user:{user_id}:workspaces")

            # Metrics for successful creation
            metrics.count("workspace.create.success", 1)
            return WorkspaceOut.model_validate(workspace), 201

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create workspace: {e}")
            metrics.count("workspace.create.failure", 1)  # only unexpected
            raise HTTPException(status_code=500, detail="Failed to create workspace")

    async def list_workspaces(self, user_id: UUID, db) -> WorkspaceListOut:
        try:
            cached = await self.cache.get(f"user:{user_id}:workspaces")
            if cached:
                metrics.count("workspace.list.cache_hit", 1)
                return WorkspaceListOut(workspaces=cached)

            stmt = select(Workspace).where(Workspace.owner_id == user_id)
            result = await db.execute(stmt)
            workspaces = result.scalars().all()
            workspace_list = [WorkspaceOut.model_validate(w) for w in workspaces]

            await self.cache.set(
                f"user:{user_id}:workspaces",
                [w.model_dump(mode="json") for w in workspace_list],
                ttl=self.list_cache_ttl,
            )
            metrics.count("workspace.list.cache_miss", 1)
            return WorkspaceListOut(workspaces=workspace_list)

        except Exception as e:
            logger.error(f"Failed to list workspaces: {e}")
            raise HTTPException(status_code=500, detail="Failed to list workspaces")

    async def get_workspace(
        self, workspace_id: UUID, user_id: UUID, db
    ) -> WorkspaceWithGridsOut:
        try:
            cache_key = f"workspace:{workspace_id}"
            cached = await self.cache.get(cache_key)
            if cached:
                metrics.count("workspace.get.cache_hit", 1)
                return WorkspaceWithGridsOut(**cached), 200

            stmt = (
                select(Workspace)
                .options(selectinload(Workspace.grids))
                .execution_options(populate_existing=True)
                .where(Workspace.id == workspace_id)
            )
            result = await db.execute(stmt)
            workspace = result.scalar_one_or_none()
            if not workspace:
                return {"error": "Workspace not found"}, 404
            if workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            workspace_data = WorkspaceWithGridsOut.model_validate(workspace)
            await self.cache.set(
                cache_key,
                workspace_data.model_dump(mode="json"),
                ttl=self.detail_cache_ttl,
            )
            return workspace_data, 200

        except Exception as e:
            logger.error(f"Failed to fetch workspace: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch workspace")

    async def update_workspace(
        self, workspace_id: UUID, user_id: UUID, data: WorkspaceUpdate, db
    ):
        try:
            stmt = select(Workspace).where(Workspace.id == workspace_id)
            result = await db.execute(stmt)
            workspace = result.scalar_one_or_none()
            if not workspace:
                return {"error": "Workspace not found"}, 404
            if workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            # Case-insensitive name uniqueness check
            if data.name and data.name.lower() != workspace.name.lower():
                stmt = select(Workspace).where(
                    Workspace.owner_id == user_id,
                    func.lower(Workspace.name) == data.name.lower(),
                )
                result = await db.execute(stmt)
                if result.scalar_one_or_none():
                    return {
                        "error": f"A workspace with name '{data.name}' already exists"
                    }, 400
                workspace.name = data.name

            if data.description is not None:
                workspace.description = data.description
            if data.visibility is not None:
                workspace.visibility = data.visibility.value

            db.add(workspace)
            await db.commit()
            await db.refresh(workspace)

            # Invalidate caches
            await self.cache.delete(f"user:{user_id}:workspaces")
            await self.cache.delete(f"workspace:{workspace_id}")

            return WorkspaceOut.model_validate(workspace), 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update workspace: {e}")
            raise HTTPException(status_code=500, detail="Failed to update workspace")

    async def delete_workspace(self, workspace_id: UUID, user_id: UUID, db):
        try:
            stmt = select(Workspace).where(Workspace.id == workspace_id)
            result = await db.execute(stmt)
            workspace = result.scalar_one_or_none()
            if not workspace:
                return {"error": "Workspace not found"}, 404
            if workspace.owner_id != user_id:
                return {"error": "Access denied"}, 403

            await db.delete(workspace)
            await db.commit()

            # Invalidate caches
            await self.cache.delete(f"user:{user_id}:workspaces")
            await self.cache.delete(f"workspace:{workspace_id}")

            metrics.count("workspace.delete.success", 1)
            return {"message": "Workspace deleted successfully"}, 200

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete workspace: {e}")
            return {"error": "Failed to delete workspace"}, 500
