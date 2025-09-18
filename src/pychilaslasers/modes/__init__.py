"""PyChilasLasers Modes Module.

Laser modes provide an encapsulation for operations that require common settings
and/or cannot be performed together.It includes manual mode for direct control
and calibrated modes for tune-state and sweeping operations. The module also
defines wavelength change methods and manages the calibration data for different
laser models.

Classes:
    LaserMode: Enum defining available laser modes
    Mode: Abstract base class for all modes
    ManualMode: Direct manual control of laser parameters
    TuneMode: Calibrated tune-state wavelength operation
    SweepMode: Calibrated sweeping operations
    _WLChangeMethod: Abstract base for wavelength change methods
    _PreLoad: Preload-based wavelength change method
    _CyclerIndex: Cycler index-based wavelength change method
"""

# Core mode classes
# Concrete mode implementations
from .manual_mode import ManualMode
from .mode import LaserMode, Mode
from .tune_mode import TuneMode
from .sweep_mode import SweepMode

__all__: list[str] = [
    # Enums and base classes
    "LaserMode",
    # Mode implementations
    "ManualMode",
    "Mode",
    "SweepMode",
    "TuneMode",
]
