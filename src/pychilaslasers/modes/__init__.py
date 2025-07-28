"""
PyChilasLasers Modes Module

This module provides various laser operation modes and related classes for controlling
Chilas laser systems. It includes manual mode for direct control, calibrated modes
for wavelength-based operations, and wavelength change methods.

Classes:
    - LaserMode: Enum defining available laser modes
    - Mode: Abstract base class for all modes
    - ManualMode: Direct manual control of laser parameters
    - SteadyMode: Calibrated steady-state wavelength operation
    - SweepMode: Calibrated wavelength sweeping operation
    - WLChangeMethod: Abstract base for wavelength change methods
    - PreLoad: Preload-based wavelength change method
    - CyclerIndex: Cycler index-based wavelength change method
"""

# Core mode classes
from .mode import LaserMode, Mode

# Concrete mode implementations
from .manual_mode import ManualMode
from .steady_mode import SteadyMode
from .sweep_mode import SweepMode

# Note: _Calibrated is kept internal as it's a base class for other modes
# from .calibrated import _Calibrated  # Internal use only

__all__ = [
    # Enums and base classes
    "LaserMode",
    "Mode",
    
    # Mode implementations
    "ManualMode",
    "SteadyMode", 
    "SweepMode",
    
    # Wavelength change methods
    "WLChangeMethod",
    "PreLoad",
    "CyclerIndex",
]