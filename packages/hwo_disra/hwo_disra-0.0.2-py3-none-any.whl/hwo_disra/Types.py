from enum import Enum
from typing import NewType


Range = NewType('Range', tuple[float, float])
ScienceYield = NewType('ScienceYield', float)
Time = NewType('Time', float)

class ScienceValue(Enum):
    ENHANCING = 0, # Minimum threshold, if we can't achieve this, project isn't worth doing.
    ENABLING = 1,  # Baseline goal for the observatory.
    BREAKTHROUGH = 2,
    STATE_OF_THE_ART = 3
