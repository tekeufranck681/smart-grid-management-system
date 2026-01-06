from app.models.enums import GridNodeType
from fastapi import HTTPException


def validate_node_attributes(node_data: dict):
    node_type = node_data.get("type")

    if node_type == GridNodeType.PLANT:
        if not node_data.get("plant_type"):
            raise HTTPException(
                status_code=400, detail="Plant node must have 'plant_type' set."
            )
        if node_data.get("load_type") or node_data.get("demand_mw"):
            raise HTTPException(
                status_code=400, detail="Plant node cannot have load attributes."
            )
        if node_data.get("priority") is None:
            node_data["priority"] = 0  # default priority if not set

    elif node_type == GridNodeType.LOAD:
        if not node_data.get("load_type"):
            raise HTTPException(
                status_code=400, detail="Load node must have 'load_type' set."
            )
        if not node_data.get("demand_mw"):
            raise HTTPException(
                status_code=400, detail="Load node must have 'demand_mw' set."
            )
        if node_data.get("plant_type") or node_data.get("capacity_mw"):
            raise HTTPException(
                status_code=400, detail="Load node cannot have plant attributes."
            )
        if node_data.get("priority") is None:
            node_data["priority"] = 0

    elif node_type == GridNodeType.SUBSTATION:
        if node_data.get("plant_type") or node_data.get("load_type"):
            raise HTTPException(
                status_code=400,
                detail="Substation node cannot have plant or load attributes.",
            )
        if node_data.get("demand_mw") is not None:
            raise HTTPException(
                status_code=400, detail="Substation node cannot have demand_mw."
            )
        if not node_data.get("capacity_mw"):
            raise HTTPException(
                status_code=400, detail="Substation node must have 'capacity_mw' set."
            )

    else:
        raise HTTPException(status_code=400, detail=f"Unknown node type: {node_type}")
