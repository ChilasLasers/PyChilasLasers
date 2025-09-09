"""
Heater component classes.

This module implements heater components that control thermal elements in the laser.
Includes individual heater types. These are only available in manual mode.

**Authors**: SDU
"""

# ⚛️ Type checking
from __future__ import annotations
from math import sqrt
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.laser import Laser

# ✅ Standard library imports
from abc import abstractmethod
import logging

# ✅ Local imports
from pychilaslasers.laser_components.laser_component import LaserComponent
from pychilaslasers.laser_components.heaters.heater_channels import HeaterChannel
from pychilaslasers.utils import Constants


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
        if not isinstance(value, (int, float)):
            raise ValueError("Heater value must be a number.")
        if value < self._min or value > self._max:
            raise ValueError(
                f"Heater value {value} not valid: must be between {self._min} and {self._max} {self._unit}."
            )

        self._comm.query(f"DRV:D {self.channel.value:d} {value:.3f}")

    ########## Method Overloads/Aliases ##########

    def get_value(self) -> float:
        """
        Alias for the `value` property getter.

        Returns:
            The current heater drive value.
        """
        return self.value

    def set_value(self, value: float) -> None:
        """
        Alias for the `value` property setter.

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


class PhaseSection(Heater):
    """Phase section heater component."""

    def __init__(self, laser: Laser) -> None:
        """Initialize the phase section heater component."""
        super().__init__(laser)

        self._anti_hyst = True

        self._volts: None | list[float] = None
        self._time_steps: None | list[float] = None

    def set_value(self, value: float) -> None:
        super().set_value(value)
        # Apply additional function after setting value
        if self._anti_hyst:
            self._antihyst(value)

    def _antihyst(self, target: float) -> None:
        """Apply anti-hysteresis correction to the laser.

        Applies a voltage ramping procedure to the phase section heater to
        minimize hysteresis effects during wavelength changes. The specifics of
        this method are laser-dependent and are specified as part of the calibration data.
        When calibration data is unavailable, default parameters from the constants class are used
        """

        if not self._volts or not self._time_steps:
            voltage_squares: list[float] = Constants.HARD_CODED_STEADY_ANTI_HYST[0]
            time_steps: list[float] = Constants.HARD_CODED_STEADY_ANTI_HYST[0]
        else:
            voltage_squares = self._volts.copy()
            time_steps = self._time_steps.copy()

        time_steps: list[float] = (
            [time_steps[0]] * (len(voltage_squares) - 1) + [0]
            if len(time_steps) == 1
            else time_steps + [0]
        )

        for i, voltage in enumerate(voltage_squares):
            if target**2 + voltage < 0:
                value = 0
                logging.getLogger(__name__).warning(
                    "Anti-hysteresis"
                    f"value out of bounds: {value} (min: {self.min_value}, max: "
                    f"{self.max_value}). Approximating by 0"
                )
                value: float = 0
            else:
                value = sqrt(target**2 + voltage)
            if value < self.min_value or value > self.max_value:
                logging.getLogger(__name__).error(
                    "Anti-hysteresis"
                    f"value out of bounds: {value} (min: {self.min_value}, max: "
                    f"{self.max_value}). Approximating with the closest limit."
                )
                value = min(value, self.max_value)
                value = max(value, self.min_value)
            self._comm.query(f"DRV:D {HeaterChannel.PHASE_SECTION.value:d} {value:.4f}")
            sleep(time_steps[i] / 1000)

    @property
    def anti_hyst(self) -> bool:
        """Get the anti-hysteresis flag."""
        return self._anti_hyst

    @anti_hyst.setter
    def anti_hyst(self, value: bool) -> None:
        """Set the anti-hysteresis flag."""
        if not isinstance(value, bool):
            raise ValueError("anti_hyst must be a boolean.")
        self._anti_hyst = value

    def set_hyst_params(self, volts: list[float], times: list[float]):
        self._volts = volts
        self._time_steps = times

    @property
    def channel(self) -> HeaterChannel:
        """Get the phase section channel."""
        return HeaterChannel.PHASE_SECTION
