"""
Laser hardware components package.

This package provides classes for controlling and interfacing with various
laser hardware components including diode, TEC and heating elements. It offers
both low-level component access and high-level abstractions for laser control operations.

Modules:
    LaserComponent: Base class for all laser hardware components
    Diode: Laser diode control and monitoring
    TEC: Temperature control functionality
    heaters: Phase section, ring heaters, and tunable coupler
   
**Authors**: SDU
"""

from .laser_component import LaserComponent
from .diode import Diode
from .tec import TEC
from .heaters.heater_channels import HeaterChannel
from .heaters.heaters import Heater, TunableCoupler, LargeRing, SmallRing, PhaseSection

__all__: list[str] = [
    "LaserComponent",
    "Diode", 
    "TEC",
    "HeaterChannel",
    "Heater",
    "TunableCoupler",
    "LargeRing", 
    "SmallRing",
    "PhaseSection"
]