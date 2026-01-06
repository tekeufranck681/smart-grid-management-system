from app.models.enums import GridEdgeStatus
from app.models.tables import Grid, GridEdge, GridNode, Workspace
from app.schemas.grid import GridCreate
from app.schemas.grid_edge import GridEdgeCreate
from app.schemas.grid_node import GridNodeCreate
from app.services.grid_edge import ALLOWED_FLOW
from app.utils.node_type_validator import validate_node_attributes
from sqlalchemy import and_, func, or_, select


class ImportService:

    async def create_grid(
        self,
        *,
        workspace: Workspace,
        data: GridCreate,
        db,
    ) -> Grid:
        # Case-insensitive uniqueness
        stmt = select(Grid).where(
            Grid.workspace_id == workspace.id,
            func.lower(Grid.name) == data.name.lower(),
        )
        result = await db.execute(stmt)

        if result.scalar_one_or_none():
            raise ValueError(f"Grid '{data.name}' already exists")

        grid = Grid(
            workspace_id=workspace.id,
            name=data.name,
            description=data.description,
            base_power_mva=data.base_power_mva,
            voltage_level=data.voltage_level,
            is_active=data.is_active,
        )

        db.add(grid)
        await db.flush()
        return grid

    async def create_node(
        self,
        *,
        grid: Grid,
        data: GridNodeCreate,
        db,
    ) -> GridNode:
        validate_node_attributes(data.model_dump())

        node = GridNode(
            grid_id=grid.id,
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
        await db.flush()
        return node

    async def create_edge(
        self,
        *,
        grid: Grid,
        data: GridEdgeCreate,
        db,
    ) -> GridEdge:
        if data.from_node_id == data.to_node_id:
            raise ValueError("Self-loop edges are not allowed")

        # Validate nodes belong to grid
        stmt = select(GridNode).where(
            GridNode.id.in_([data.from_node_id, data.to_node_id]),
            GridNode.grid_id == grid.id,
        )
        result = await db.execute(stmt)
        nodes = result.scalars().all()

        if len(nodes) != 2:
            raise ValueError("Invalid nodes for grid")

        from_node = next(n for n in nodes if n.id == data.from_node_id)
        to_node = next(n for n in nodes if n.id == data.to_node_id)

        allowed_targets = ALLOWED_FLOW.get(from_node.type)
        if not allowed_targets or to_node.type not in allowed_targets:
            raise ValueError(
                f"Invalid power flow: {from_node.type.value} → {to_node.type.value}"
            )

        # Prevent duplicates
        dup_stmt = select(GridEdge).where(
            and_(
                GridEdge.grid_id == grid.id,
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

        if (await db.execute(dup_stmt)).scalar_one_or_none():
            raise ValueError("Edge already exists between nodes")

        edge = GridEdge(
            grid_id=grid.id,
            from_node_id=data.from_node_id,
            to_node_id=data.to_node_id,
            capacity_mw=data.capacity_mw,
            resistance=data.resistance,
            losses_percent=data.losses_percent,
            priority=data.priority or 0,
            status=GridEdgeStatus.ACTIVE,
        )

        db.add(edge)
        await db.flush()
        return edge
