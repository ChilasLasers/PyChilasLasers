"""Heater component classes.

This module implements heater components that control thermal elements in the laser.
Includes individual heater types. These are only available in manual mode.

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
from pychilaslasers.laser_components.heaters.heater_channels import HeaterChannel
from pychilaslasers.laser_components.laser_component import LaserComponent


class Heater(LaserComponent):
    """Base class for laser heater components.

    Provides common functionality for all heater types including
    value setting and channel management.

    Attributes:
        channel: The heater channel identifier.
        value: The current heater drive value.
        min_value: Minimum heater value.
        max_value: Maximum heater value.
        unit: Heater value unit.

    """

    def __init__(self, laser: Laser) -> None:
        """Initialize the heater component.

        Sets up the heater with its operating limits and units by
        querying the laser hardware.

        Args:
            laser: The laser instance to control.

        """
        super().__init__(laser)
        self._min: float = float(self._comm.query(f"DRV:LIM:MIN? {self.channel.value}"))
        self._max: float = float(self._comm.query(f"DRV:LIM:MAX? {self.channel.value}"))
        self._unit: str = self._comm.query(f"DRV:UNIT? {self.channel.value}").strip()

    ########## Properties (Getters/Setters) ##########

    @property
    @abstractmethod
    def channel(self) -> HeaterChannel:
        """Get the heater channel identifier.

        Must be implemented by subclasses to specify which
        heater channel this component controls.

        Returns:
            The channel identifier for this heater.

        """
        pass

    @property
    def value(self) -> float:
        """Get the current heater drive value.

        Returns:
            The current heater drive value.

        """
        return float(self._comm.query(f"DRV:D? {self.channel.value:d}"))

    @value.setter
    def value(self, value: float) -> None:
        """Set the heater drive value.

        Args:
            value: The heater drive value to set.

        Raises:
            ValueError: If value is not a number or outside valid range.

        """
        # Validate the value
        if not isinstance(value, int | float):
            raise ValueError("Heater value must be a number.")
        if value < self._min or value > self._max:
            raise ValueError(
                f"Heater value {value} not valid: must be between "
                f"{self._min} and {self._max} {self._unit}."
            )

        self._comm.query(f"DRV:D {self.channel.value:d} {value:.3f}")

    ########## Method Overloads/Aliases ##########

    def get_value(self) -> float:
        """Alias for the `value` property getter.

        Returns:
            The current heater drive value.

        """
        return self.value

    def set_value(self, value: float) -> None:
        """Alias for the `value` property setter.

        Args:
            value: The heater drive value to set.

        Raises:
            ValueError: If value is not a number or outside valid range.

        """
        self.value = value


class TunableCoupler(Heater):
    """Tunable coupler heater component."""

    @property
    def channel(self) -> HeaterChannel:
        """Get the tunable coupler channel."""
        return HeaterChannel.TUNABLE_COUPLER


class LargeRing(Heater):
    """Large ring heater component."""

    @property
    def channel(self) -> HeaterChannel:
        """Get the large ring channel."""
        return HeaterChannel.RING_LARGE


class SmallRing(Heater):
    """Small ring heater component."""

    @property
    def channel(self) -> HeaterChannel:
        """Get the small ring channel."""
        return HeaterChannel.RING_SMALL
