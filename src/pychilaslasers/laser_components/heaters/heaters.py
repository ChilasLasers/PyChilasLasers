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
    from pychilaslasers.calibration import Calibration
    from collections.abc import Callable

# ✅ Standard library imports
from abc import abstractmethod
import logging
from math import sqrt
from time import sleep


# ✅ Local imports
from pychilaslasers.laser_components.heaters.heater_channels import HeaterChannel
from pychilaslasers.laser_components.laser_component import LaserComponent
from pychilaslasers.calibration.defaults import Defaults
from pychilaslasers.exceptions import ModeError


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


class PhaseSection(Heater):
    """Phase section heater component."""

    _anti_hyst: Callable[
        [
            float | None,
        ],
        None,
    ]

    def __init__(self, laser: Laser) -> None:
        """Initialize the phase section heater component."""
        super().__init__(laser)

        self._anti_hyst_enabled = True

        self._volts: None | list[float] = None
        self._time_steps: None | list[float] = None

        self._anti_hyst = self.get_antihyst_method(laser=laser)

    def set_value(self, value: float) -> None:  # noqa: D102
        super().set_value(value)
        # Apply additional function after setting value
        if self._anti_hyst_enabled:
            self._anti_hyst(value)

    @property
    def anti_hyst(self) -> bool:
        """Get the anti-hysteresis flag."""
        return self._anti_hyst_enabled

    @anti_hyst.setter
    def anti_hyst(self, value: bool) -> None:
        """Set the anti-hysteresis flag."""
        if not isinstance(value, bool):
            raise ValueError("anti_hyst must be a boolean.")
        self._anti_hyst_enabled = value

    def calibrate(self, laser: Laser, calibration: Calibration) -> None:
        """Calibrate the phase section heater with the given laser and calibration.

        Args:
            laser: The laser instance to use for calibration.
            calibration: The calibration object containing calibration data.
        """
        self._anti_hyst = self.get_antihyst_method(
            laser=laser,
            voltage_steps=calibration.tune_settings.anti_hyst_voltages,
            time_steps=calibration.tune_settings.anti_hyst_times,
        )

    @property
    def channel(self) -> HeaterChannel:
        """Get the phase section channel."""
        return HeaterChannel.PHASE_SECTION

    @staticmethod
    def get_antihyst_method(
        laser: Laser,
        voltage_steps: list[float] | None = None,
        time_steps: list[float] | None = None,
    ) -> Callable[[float | None], None]:
        """Construct an anti-hysteresis correction function for the laser.

        This method takes a laser object and returns an appropriate anti-hyst func
        that can be used independently.

        Args:
            laser: The laser instance to apply anti-hysteresis correction to.
            voltage_steps: Optional list of voltage step values for the
                anti-hysteresis procedure. Defaults will be used if None provided.
            time_steps: Optional list of time step durations (in ms) for
                each voltage step. Defaults will be used if None provided.

        Returns:
            A callable that applies anti-hysteresis correction when invoked with
              an optional phase voltage.
        """
        query: Callable[[str], str] = laser.comm.query

        phase_min: float
        phase_max: float

        try:
            phase_max = laser._manual_mode.phase_section.max_value
            phase_min = laser._manual_mode.phase_section.min_value
        except AttributeError as e:
            if laser.system_state:
                phase_max = float(
                    laser.comm.query(f"DRV:LIM:MAX? {PhaseSection.channel}")
                )
                phase_min = float(
                    laser.comm.query(f"DRV:LIM:MIN? {PhaseSection.channel}")
                )
            else:
                raise ModeError(
                    "Phase section min-max values could not be obtained", laser.mode
                ) from e

        voltage_steps = (
            Defaults.TUNE_ANTI_HYST[0] if voltage_steps is None else voltage_steps
        )
        time_steps = Defaults.TUNE_ANTI_HYST[0] if time_steps is None else time_steps

        time_steps = (
            [time_steps[0]] * (len(voltage_steps) - 1) + [0]
            if len(time_steps) == 1
            else [*time_steps, 0]
        )

        def antihyst(v_phase: float | None = None) -> None:
            """Apply anti-hysteresis correction to the laser.

            Applies a voltage ramping procedure to the phase section heater to
            minimize hysteresis effects during wavelength changes. The specifics of
            this method are laser-dependent and are specified as part of the calibration
            data.
            """
            if v_phase is None:
                v_phase = float(query(f"DRV:D? {HeaterChannel.PHASE_SECTION.value:d}"))

            for i, voltage_step in enumerate(voltage_steps):
                if v_phase**2 + voltage_step < 0:
                    value: float = 0
                    logging.getLogger(__name__).warning(
                        "Anti-hysteresis "
                        f"value out of bounds: {value} (min: {phase_min}, max: "
                        f"{phase_max}). Approximating by 0"
                    )
                else:
                    value = sqrt(v_phase**2 + voltage_step)
                if value < phase_min or value > phase_max:
                    logging.getLogger(__name__).error(
                        "Anti-hysteresis"
                        f"value out of bounds: {value} (min: {phase_min}, max: "
                        f"{phase_max}). Approximating with the closest limit."
                    )
                    value = min(value, phase_max)
                    value = max(value, phase_min)
                query(f"DRV:D {HeaterChannel.PHASE_SECTION.value:d} {value:.4f}")
                sleep(time_steps[i] / 1000)

        return antihyst
