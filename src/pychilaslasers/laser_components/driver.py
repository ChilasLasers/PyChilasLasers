"""Abstract base class for laser drivers.

This module defines the interface for laser drivers, components that drive actuators
such as heater drivers.

**Authors**: SDU
"""

# ⚛️ Type checking
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.laser import Laser

# ✅ Standard library imports
from abc import abstractmethod

# ✅ Local imports
from pychilaslasers.laser_components.laser_component import LaserComponent


class Driver(LaserComponent):
    """Abstract base class for all laser drivers.

    This class defines the common interface that all laser drivers should implement. It
    provides standardized access operating ranges of the drivers and setters.

    Attributes:
        value: Setter for the value of this driver
        min_value: The minimum allowable value for this component.
        max_value: The maximum allowable value for this component.

    Note:
        Subclasses should initialize self._min, self._max and self._unit
        during construction.
    """

    _min: float
    _max: float
    _unit: str

    def __init__(self, laser: Laser) -> None:  # noqa: D107
        super().__init__(laser)

    ########## Properties (Getters/Setters) ##########

    @property
    @abstractmethod
    def value(self) -> float:
        """Returns the current value of the driver in appropriate units."""

    @value.setter
    @abstractmethod
    def value(self, value) -> None:
        """Sets the current value of the actuator."""

    @property
    def min_value(self) -> float:
        """Returns the minimum value that can be safely set for this component."""
        return self._min

    @property
    def max_value(self) -> float:
        """Returns the maximum value that can be safely set for this component."""
        return self._max
