"""Abstract base classes and enumerations for laser operating modes.

This module defines the core interfaces and types for laser mode implementations.
It provides the base Mode class that all specific modes inherit from, as well as
the LaserMode enumeration for type-safe mode identification.

**Authors**: RLK, AVR, SDU
"""

# ⚛️ Type checking
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.comm import Communication
    from pychilaslasers.laser import Laser

# ✅ Standard library imports
from abc import ABC, abstractmethod
from enum import Enum


class LaserMode(Enum):
    """Enumeration of laser modes.

    Provides an alternative way of referencing modes without using string literals,
    classes, or instances. This enumeration ensures type safety and consistency
    throughout the library.

    Attributes:
        MANUAL: Manual mode for direct component control.
        SWEEP: Sweep mode for wavelength scanning (COMET lasers only).
        TUNE: Tune mode for precise wavelength control using calibration data.

    """

    MANUAL = "Manual"
    SWEEP = "Sweep"
    TUNE = "Tune"


class Mode(ABC):
    """Abstract base class for laser modes.

    This class defines the basic structure and properties that all laser modes
    should implement. It provides a common interface for interacting with different
    laser modes, such as manual, sweep, and tune modes.

    A laser mode is an abstract operational state of the laser that adds functionality
    and defines how it behaves, the operations available, and the settings required
    for its operation.
    """

    def __init__(self, laser: Laser) -> None:
        """Initialize the mode with a reference to the parent laser.

        Args:
            laser: The laser instance that owns this mode.

        """
        super().__init__()
        self._laser: Laser = laser
        self._comm: Communication = laser._comm

    ########## Abstract Methods ##########

    @abstractmethod
    def apply_defaults(self) -> None:
        """Apply default settings for the mode.

        This method is called when the laser switches to this mode and should
        configure all mode-specific parameters to their default values.
        """
        pass

    @property
    @abstractmethod
    def mode(self) -> LaserMode:
        """Return the enumeration value identifying this mode type.

        Returns:
            The enumeration value identifying this mode type.

        """
        pass
