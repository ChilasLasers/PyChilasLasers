"""PyChilasLasers Modes Module.

Laser modes provide an encapsulation for operations that require common settings
and/or cannot be performed together.It includes manual mode for direct control
and calibrated modes for tune-state and sweeping operations.

Classes:
    LaserMode: Enum defining available laser modes
    Mode: Abstract base class for all modes
    ManualMode: Direct manual control of laser parameters
    TuneMode: Calibrated tune-state wavelength operation
    SweepMode: Calibrated sweeping operations
"""

# Core mode classes
# Concrete mode implementations
from .manual_mode import ManualMode
from .mode import LaserMode, Mode
from .tune_mode import TuneMode
from .sweep_mode import SweepMode

__all__: list[str] = [  # noqa: RUF022
    # Enums and base classes
    "Mode",
    "LaserMode",
    # Mode implementations
    "ManualMode",
    "SweepMode",
    "TuneMode",
]
