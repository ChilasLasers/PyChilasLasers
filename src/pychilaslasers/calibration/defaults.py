"""Default configuration values for laser calibration."""

# ⚛️ Type checking
from __future__ import annotations


class Defaults:
    """Hard-coded default values for laser calibration parameters.

    Used when calibration files don't contain explicit settings.
    """

    HARD_CODED_LASER_MODEL: str = "ATLAS"

    # Tune mode defaults
    HARD_CODED_TUNE_CURRENT: float = 280.0
    HARD_CODED_TUNE_TEC_TEMP: float = 25.0
    HARD_CODED_TUNE_ANTI_HYST: tuple = ([35.0, 0.0], [10.0])

    # Sweep mode defaults (COMET only)
    HARD_CODED_SWEEP_CURRENT: float = 280.0
    HARD_CODED_SWEEP_TEC_TEMP: float = 25.0
    HARD_CODED_INTERVAL: int = 100
