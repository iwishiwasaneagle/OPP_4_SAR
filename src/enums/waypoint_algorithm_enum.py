from enum import Enum, auto

class WaypointAlgorithmEnum(Enum):
    LHC_GW_CONV = auto()
    PARALLEL_SWATHS = auto()
    MODIFIED_LAWNMOWER  = auto()
    PABO = auto()