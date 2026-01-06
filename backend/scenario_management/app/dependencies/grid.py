from uuid import UUID

import httpx
from app.core.config import settings
from fastapi import HTTPException, Request

WORKSPACE_SERVICE_URL = settings.WORKSPACE_SERVICE_URL


async def fetch_grid(
    grid_id: UUID,
    request: Request,
) -> dict:
    """
    Fetch a full grid (with nodes and edges) from the Grid microservice.

    - Forwards access_token cookie
    - Relies on Grid service for authorization & workspace checks
    - Returns raw grid payload for snapshotting
    """

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{WORKSPACE_SERVICE_URL}/grids/{grid_id}",
                cookies={"access_token": token},
                timeout=30,
            )
            resp.raise_for_status()

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            # propagate meaningful errors
            if status_code == 404:
                raise HTTPException(status_code=404, detail="Grid not found")
            if status_code == 403:
                raise HTTPException(status_code=403, detail="Access to grid denied")
            if status_code == 401:
                raise HTTPException(status_code=401, detail="Unauthorized")

            raise HTTPException(
                status_code=status_code,
                detail="Failed to fetch grid from Grid service",
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Grid service unreachable",
            )

    grid_data = resp.json()

    if not grid_data or "id" not in grid_data:
        raise HTTPException(
            status_code=502,
            detail="Invalid grid payload received from Grid service",
        )

    return grid_data
