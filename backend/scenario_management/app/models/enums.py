from enum import Enum


class ScenarioStatus(str, Enum):
    DRAFT = "DRAFT"  # Editable
    LOCKED = "LOCKED"  # Immutable, ready for simulation
    ARCHIVED = "ARCHIVED"  # Read-only, historical


class EventType(str, Enum):
    LOAD_CHANGE = "LOAD_CHANGE"  # Demand fluctuation at a node
    LINE_OUTAGE = "LINE_OUTAGE"  # Transmission line failure
    GENERATION_CHANGE = "GENERATION_CHANGE"  # Generator / renewable variation
    LOAD_SHEDDING = "LOAD_SHEDDING"  # Controlled power cut
    ISLANDING = "ISLANDING"  # Micro-grid separation


class TargetType(str, Enum):
    NODE = "NODE"  # GridNode snapshot ID
    EDGE = "EDGE"  # GridEdge snapshot ID
    ZONE = "ZONE"  # Group of nodes (for islanding)
