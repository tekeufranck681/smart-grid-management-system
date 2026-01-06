from typing import List
from uuid import UUID

from app.models.enums import EventType, TargetType
from fastapi import HTTPException


def validate_event_parameters(
    event_type: EventType,
    target_type: TargetType,
    parameters: dict,
    snapshot: List[dict],  # snapshot.nodes or snapshot.edges
    target_id: UUID | str,  # allow logical IDs
):
    """
    Validate parameters for a scenario event based on the event type.
    Supports logical targets (e.g., ZONE for ISLANDING).
    Raises HTTPException if invalid.
    """

    snapshot_dict = {UUID(item["id"]): item for item in snapshot}

    #  Validate physical target existence ONLY when required
    if target_type in {TargetType.NODE, TargetType.EDGE}:
        try:
            target_uuid = UUID(str(target_id))
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid UUID for physical target"
            )

        if target_uuid not in snapshot_dict:
            raise HTTPException(
                status_code=400, detail="Target does not exist in snapshot"
            )

        target = snapshot_dict[target_uuid]
    else:
        # Logical target (ZONE, SYSTEM, etc.)
        target = None

    # Event-specific validation rules
    if event_type == EventType.LOAD_CHANGE:
        if target_type != TargetType.NODE or target.get("type") != "load":
            raise HTTPException(
                status_code=400, detail="LOAD_CHANGE can only apply to LOAD nodes"
            )
        required = ["delta_mw", "mode", "reason"]

    elif event_type == EventType.GENERATION_CHANGE:
        if target_type != TargetType.NODE or target.get("type") != "plant":
            raise HTTPException(
                status_code=400,
                detail="GENERATION_CHANGE can only apply to PLANT nodes",
            )
        required = ["new_capacity_mw", "plant_type", "cause"]

    elif event_type == EventType.LINE_OUTAGE:
        if target_type != TargetType.EDGE:
            raise HTTPException(
                status_code=400, detail="LINE_OUTAGE can only apply to edges"
            )
        required = ["new_status", "reason"]

    elif event_type == EventType.LOAD_SHEDDING:
        if target_type != TargetType.NODE or target.get("type") != "load":
            raise HTTPException(
                status_code=400, detail="LOAD_SHEDDING can only apply to LOAD nodes"
            )
        required = ["shed_mw", "priority_threshold", "policy"]

    elif event_type == EventType.ISLANDING:
        if target_type != TargetType.ZONE:
            raise HTTPException(
                status_code=400, detail="ISLANDING must use ZONE as target_type"
            )

        required = ["node_ids", "mode", "reason"]

        node_ids = parameters.get("node_ids", [])
        if not node_ids:
            raise HTTPException(status_code=400, detail="node_ids cannot be empty")

        # Validate referenced nodes exist
        for nid in node_ids:
            try:
                if UUID(nid) not in snapshot_dict:
                    raise HTTPException(
                        status_code=400, detail=f"Node {nid} does not exist in snapshot"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid UUID in node_ids: {nid}"
                )

    else:
        raise HTTPException(
            status_code=400, detail=f"Unsupported event type {event_type}"
        )

    # Required parameter enforcement
    for key in required:
        if key not in parameters:
            raise HTTPException(
                status_code=400, detail=f"Missing required parameter: {key}"
            )

    return True
