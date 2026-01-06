import json
from uuid import UUID

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.schemas.import_grid import ImportGridPayload
from app.services.grid_import import GridImportService
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/import", tags=["Grid Import"])


@router.post("/grids/{workspace_id}", status_code=status.HTTP_201_CREATED)
async def import_grid_from_file(
    workspace_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # -------------------------
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")

    try:
        # -------------------------
        raw_bytes = await file.read()
        raw_data = json.loads(raw_bytes)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    # -------------------------
    try:
        payload = ImportGridPayload.model_validate(raw_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # -------------------------
    service = GridImportService()
    result = await service.import_grid(
        workspace_id=workspace_id,
        user_id=UUID(current_user["id"]),
        payload=payload,
        db=db,
    )
    return result
