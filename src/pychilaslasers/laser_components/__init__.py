"""
Laser hardware components package.
<p>
This package provides classes for controlling and interfacing with various
laser hardware components including diodes, (TEC) and heating elements. It offers
both low-level component access and high-level abstractions for laser control operations.
<p>
The package includes:
- **LaserComponent**: Base class for all laser hardware components
- **Diode**: Laser diode control and monitoring
- **TEC**: Temperature control functionality
- **Heater components**: Phase section, ring heaters, and tunable coupler
<p>
Authors: SDU
Last Revision: July 30, 2025 - Enhanced documentation and improved code formatting
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