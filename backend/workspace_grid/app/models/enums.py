import enum


class WorkspaceVisibility(str, enum.Enum):
    PRIVATE = "private"
    SHARED = "shared"


class GridNodeType(str, enum.Enum):
    PLANT = "plant"
    LOAD = "load"
    SUBSTATION = "substation"


class PlantType(str, enum.Enum):
    HYDRO = "hydro"
    SOLAR = "solar"
    THERMAL = "thermal"


class LoadType(str, enum.Enum):
    HOSPITAL = "hospital"
    ENTERPRISE = "enterprise"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"


class GridEdgeStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    FAILED = "failed"
