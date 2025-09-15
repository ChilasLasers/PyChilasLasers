"""Abstract base class for laser hardware components.

This module defines the common interface that all laser hardware components
must implement. This encapsulation allows for abstracticizing the internals of
the laser in such a way as to allow for better visualization of their state and
possible operations.

**Authors**: SDU
"""

# ⚛️ Type checking
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.comm import Communication
    from pychilaslasers.laser import Laser

# ✅ Standard library imports
from abc import ABC, abstractmethod


class LaserComponent(ABC):
    """Abstract base class for all laser hardware components.

    This class defines the common interface that all laser components must
    implement. It provides standardized access to component values, operating
    ranges, and units of measurement.

    Attributes:
        value: The current value of the component (implementation-dependent).
        min_value: The minimum allowable value for this component.
        max_value: The maximum allowable value for this component.
        unit: The unit of measurement for this component's values.

    Note:
        Subclasses should initialize self._min, self._max and self._unit
        during construction.

    """

    _min: float
    _max: float
    _unit: str

    def __init__(self, laser: Laser) -> None:  # noqa: D107
        super().__init__()
        self._comm: Communication = laser._comm

    ########## Properties (Getters/Setters) ##########

    @property
    @abstractmethod
    def value(self) -> float:
        """Returns the current value of the component in appropriate units."""
        pass

    @property
    def min_value(self) -> float:
        """Returns the minimum value that can be safely set for this component."""
        return self._min

    @property
    def max_value(self) -> float:
        """Returns the maximum value that can be safely set for this component."""
        return self._max

    @property
    def unit(self) -> str:
        """Returns the unit string (e.g., "mA", "°C", "V") for this component."""
        return self._unit
