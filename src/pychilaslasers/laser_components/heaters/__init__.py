"""
Heater components package for laser thermal control.

This package provides heater component classes for controlling thermal elements
of the laser. Includes channel definitions and individual heater types.

Classes:
    HeaterChannel: Enum representing the different heater channels
    TunableCoupler: Tunable coupler section heater for wavelength fine-tuning
    LargeRing: Large ring section heater for coarse wavelength adjustment  
    SmallRing: Small ring section heater for fine wavelength adjustment
    PhaseSection: Phase section heater for phase adjustment and mode control

**Authors**: SDU
"""

from .heater_channels import HeaterChannel
from .heaters import Heater, TunableCoupler, LargeRing, SmallRing, PhaseSection

__all__: list[str] = [
    "HeaterChannel",
    "Heater",
    "TunableCoupler",
    "LargeRing",
    "SmallRing",
    "PhaseSection"
]