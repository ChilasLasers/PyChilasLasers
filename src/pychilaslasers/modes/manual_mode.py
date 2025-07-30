from __future__ import annotations
from typing import TYPE_CHECKING


from pychilaslasers.laser_components.heaters import HeaterChannel, LargeRing, PhaseSection, SmallRing, TunableCoupler, Heater
from pychilaslasers.modes import LaserMode, Mode


if TYPE_CHECKING:
    from pychilaslasers import Laser

class ManualMode(Mode):

    def __init__(self, laser:Laser) -> None:
        """
        docstring
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

    @property
    def mode(self) -> LaserMode:
        # Return the mode identifier for manual mode
        return LaserMode.MANUAL

    def set_driver_value(self, heater_ch: int | HeaterChannel, heater_value: float) -> None:
        """Manually sets the value of the driver channel.

        Args:
            heater_ch (int): The heater channel number.
            heater_value (float): The value to be set.
        """
        self._laser.query(f"DRV:D {heater_ch:d} {heater_value:.4f}")


    def apply_defaults(self) -> None:
        """Apply default settings for the mode."""
        for heater in self._heaters:
            heater.value = 0

    @property
    def heaters(self) -> list[Heater]:
        """Gets the list of heaters."""
        return self._heaters

    @property
    def phase_section(self) -> PhaseSection:
        return self._phase_section

    @property
    def large_ring(self) -> LargeRing:
        return self._large_ring

    @property
    def small_ring(self) -> SmallRing:
        return self._small_ring

    @property
    def tunable_coupler(self) -> TunableCoupler:
        return self._tunable_coupler
    