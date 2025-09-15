# ⚛️ Type checking  # noqa: D100
from __future__ import annotations

# ✅ Standard library imports
from enum import Enum


class HeaterChannel(Enum):  # noqa: D101
    PHASE_SECTION = 0
    RING_SMALL = 1
    RING_LARGE = 2
    TUNABLE_COUPLER = 3
