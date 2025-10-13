"""Default configuration values for laser calibration."""

# ⚛️ Type checking
from __future__ import annotations

from pychilaslasers.calibration.structs import TuneMethod


class Defaults:
    """Hard-coded default values for laser calibration parameters.

    Used when calibration files don't contain explicit settings.
    """

    LASER_MODEL: str = "ATLAS"

    # Tune mode defaults
    TUNE_CURRENT: float = 280.0
    TUNE_TEC_TEMP: float = 25.0
    TUNE_ANTI_HYST: tuple = ([35.0, 0.0], [10.0])
    TUNE_METHOD: TuneMethod = TuneMethod.FILE

    # Sweep mode defaults (COMET only)
    SWEEP_CURRENT: float = 280.0
    SWEEP_TEC_TEMP: float = 25.0
    INTERVAL: int = 100
