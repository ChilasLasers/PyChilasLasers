"""Manual mode implementation for direct laser heater control.

This module implements manual mode operation for laser control, allowing direct
manipulation of individual heater channels without calibration constraints.
Manual mode provides low-level access to all laser heater components for
advanced users and debugging purposes.

**The calibration is not valid during manual mode**

**Authors**: RLK, AVR, SDU
"""

# ⚛️ Type checking
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.laser import Laser
    from pychilaslasers.laser_components.heaters.heater_channels import HeaterChannel
    from pychilaslasers.laser_components.heaters.heaters import Heater

# ✅ Local imports
from pychilaslasers.laser_components.heaters.heaters import (
    LargeRing,
    PhaseSection,
    SmallRing,
    TunableCoupler,
)
from pychilaslasers.modes.mode import LaserMode, Mode


class ManualMode(Mode):
    """Manual laser control mode for direct heater manipulation.

    ManualMode provides unrestricted access to all laser heater channels,
    allowing users to manually set voltages without calibration constraints.
    This mode is primarily intended for advanced users, testing, and debugging
    purposes where precise control over individual components is required at the
    expense of calibration.

    The mode initializes all heater components and provides both individual
    heater access and a unified interface for driver value setting.

    Args:
        laser: The laser instance to control.

    Attributes:
        heaters: List of all available heater components.
        phase_section: Phase section heater component.
        large_ring: Large ring heater component.
        small_ring: Small ring heater component.
        tunable_coupler: Tunable coupler heater component.

    """

    def __init__(self, laser: Laser) -> None:
        """Initialize manual mode with laser instance and heater components.

        Creates all heater component instances. The laser is temporarily turned on
        during initialization to gather component characteristics.

        Args:
            laser: The laser instance to control.

        """
        super().__init__(laser)
        self._laser.turn_on()  # Ensure the laser is on after initializing heaters
        self._phase_section: PhaseSection = PhaseSection(laser)
        self._large_ring: LargeRing = LargeRing(laser)
        self._small_ring: SmallRing = SmallRing(laser)
        self._tunable_coupler: TunableCoupler = TunableCoupler(laser)
        self._laser.turn_off()  # Ensure the laser is off after initializing heaters

        self._heaters: list[Heater] = [
            self._phase_section,
            self._large_ring,
            self._small_ring,
            self._tunable_coupler,
        ]

    ########## Main Methods ##########

    def apply_defaults(self) -> None:
        """Apply default settings for manual mode operation."""
        pass

    def set_driver_value(
        self, heater_ch: int | HeaterChannel, heater_value: float
    ) -> None:
        """Manually set the voltage value of a specific driver channel.

        Provides direct low-level access to set heater voltages without
        any validation or safety checks. This method bypasses all calibration
        constraints and allows unrestricted heater control.

        Args:
            heater_ch: The heater channel number or HeaterChannel enum.
                Valid channels are typically 0-3 for the four main heaters.
            heater_value: The voltage value to set in volts.
                Range depends on laser specifications and hardware limits.

        Warning:
            This method performs no validation on the input values.
            Setting inappropriate voltages may result in errors or undefined behavior.

        """
        self._comm.query(f"DRV:D {heater_ch:d} {heater_value:.4f}")

    ########## Properties (Getters/Setters) ##########

    @property
    def mode(self) -> LaserMode:
        """Get the laser operation mode."""
        return LaserMode.MANUAL

    @property
    def phase_section(self) -> PhaseSection:
        """Get the phase section heater."""
        return self._phase_section

    @phase_section.setter
    def phase_section(self, value: float) -> None:
        """Set the phase section heater value.

        Args:
            value: The heater drive value to set.

        """
        self._phase_section.value = value

    @property
    def large_ring(self) -> LargeRing:
        """Get the large ring heater."""
        return self._large_ring

    @large_ring.setter
    def large_ring(self, value: float) -> None:
        """Set the large ring heater value.

        Args:
            value: The heater drive value to set.

        """
        self._large_ring.value = value

    @property
    def small_ring(self) -> SmallRing:
        """Get the small ring heater."""
        return self._small_ring

    @small_ring.setter
    def small_ring(self, value: float) -> None:
        """Set the small ring heater value.

        Args:
            value: The heater drive value to set.

        """
        self._small_ring.value = value

    @property
    def tunable_coupler(self) -> TunableCoupler:
        """Get the tunable coupler."""
        return self._tunable_coupler

    @tunable_coupler.setter
    def tunable_coupler(self, value: float) -> None:
        """Set the tunable coupler heater value.

        Args:
            value: The heater drive value to set.

        """
        self._tunable_coupler.value = value

    ########## Method Overloads/Aliases ##########

    @property
    def heaters(self) -> list[Heater]:
        """Get all heater components as a convenient list.

        Alias that provides all individual heater components in a single list.

        Returns:
            List containing:
                0. phase_section
                1. large_ring
                2. small_ring
                3. tunable_coupler
                In this order for easy iteration and access.

        """
        return self._heaters
