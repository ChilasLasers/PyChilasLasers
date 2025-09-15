"""Laser hardware components package.

This package provides classes for controlling and interfacing with various
laser hardware components including diode, TEC and heating elements. It offers
both low-level component access and high-level abstractions
for laser control operations.

Modules:
    LaserComponent: Base class for all laser hardware components
    Diode: Laser diode control and monitoring
    TEC: Temperature control functionality
    heaters: Phase section, ring heaters, and tunable coupler

**Authors**: SDU
"""

from .diode import Diode
from .heaters.heater_channels import HeaterChannel
from .heaters.heaters import Heater, LargeRing, PhaseSection, SmallRing, TunableCoupler
from .laser_component import LaserComponent
from .tec import TEC

__all__: list[str] = [
    "TEC",
    "Diode",
    "Heater",
    "HeaterChannel",
    "LargeRing",
    "LaserComponent",
    "PhaseSection",
    "SmallRing",
    "TunableCoupler",
]
