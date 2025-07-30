"""
Manual mode implementation for direct laser heater control.
<p>
This module implements manual mode operation for laser control, allowing direct
manipulation of individual heater channels without calibration constraints.
Manual mode provides low-level access to all laser heater components for
advanced users and debugging purposes.
<p>
Authors: RLK, AVR, SDU
Last Revision: July 30, 2025 - Enhanced documentation and improved code formatting
"""

from __future__ import annotations
from typing import TYPE_CHECKING


from pychilaslasers.laser_components.heaters import HeaterChannel, LargeRing, PhaseSection, SmallRing, TunableCoupler, Heater
from pychilaslasers.modes import LaserMode, Mode


if TYPE_CHECKING:
    from pychilaslasers import Laser

class ManualMode(Mode):
    """Manual laser control mode for direct heater manipulation.
    <p>
    ManualMode provides unrestricted access to all laser heater channels,
    allowing users to manually set voltages without calibration constraints.
    This mode is primarily intended for advanced users, testing, and debugging
    purposes where precise control over individual components is required at the
    expense of calibration.
    <p>
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
        <p>
        Creates all heater component instances and establishes direct control
        over the laser hardware. The laser is temporarily turned on during
        initialization to gather component characteristics.
        
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
            self._tunable_coupler
        ]

    ########## Main Methods ##########

    def apply_defaults(self) -> None:
        """Apply default settings for manual mode operation.
        <p>
        Resets all heater values to zero, providing a safe starting state
        for manual operation. This ensures no residual voltages remain
        from previous operations.
        """
        for heater in self._heaters:
            heater.value = 0

    def set_driver_value(self, heater_ch: int | HeaterChannel, heater_value: float) -> None:
        """Manually set the voltage value of a specific driver channel.
        <p>
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
            Setting inappropriate voltages may damage the laser hardware.
        """
        self._laser.query(f"DRV:D {heater_ch:d} {heater_value:.4f}")

    ########## Properties (Getters/Setters) ##########

    @property
    def mode(self) -> LaserMode:
        """Get the laser operation mode.
        
        Returns:
            LaserMode: LaserMode.MANUAL indicating manual mode operation.
        """
        return LaserMode.MANUAL

    @property
    def phase_section(self) -> PhaseSection:
        """Get the phase section heater component.
        
        Returns:
            PhaseSection: The phase section heater for wavelength fine-tuning.
        """
        return self._phase_section

    @property
    def large_ring(self) -> LargeRing:
        """Get the large ring heater component.
        
        Returns:
            LargeRing: The large ring heater for coarse wavelength control.
        """
        return self._large_ring

    @property
    def small_ring(self) -> SmallRing:
        """Get the small ring heater component.
        
        Returns:
            SmallRing: The small ring heater for medium wavelength control.
        """
        return self._small_ring

    @property
    def tunable_coupler(self) -> TunableCoupler:
        """Get the tunable coupler heater component.
        
        Returns:
            TunableCoupler: The tunable coupler heater for output coupling control.
        """
        return self._tunable_coupler

    ########## Method Overloads/Aliases ##########

    @property
    def heaters(self) -> list[Heater]:
        """Get all heater components as a convenient list.
        <p>
        Alias that provides all individual heater components in a single list.
        
        Returns:
            list[Heater]: List containing phase_section, large_ring, small_ring,
                and tunable_coupler heater instances.
        """
        return self._heaters
    