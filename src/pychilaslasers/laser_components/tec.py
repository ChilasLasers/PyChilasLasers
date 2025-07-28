from __future__ import annotations
from typing import TYPE_CHECKING

from pychilaslasers.laser_components.laser_component import LaserComponent

if TYPE_CHECKING:
    from pychilaslasers import Laser


class TEC(LaserComponent):

    def __init__(self, laser: Laser) -> None:
        super().__init__()
        self._laser: Laser = laser
        self._min: float = float(self._laser.query("TEC:CFG:TMIN?"))
        self._max: float = float(self._laser.query("TEC:CFG:TMAX?"))
        self._unit: str = "Celsius" 

        
    
    @property
    def target(self) -> float:
        return float(self._laser.query("TEC:TTGT?"))


    @target.setter
    def target(self, target: float):
        """Set the target temperature."""
        # Validate the target temperature
        if not isinstance(target, (int, float)):
            raise ValueError("Target temperature must be a number.") ##TODO maybe implement diff error
        # Check if the target is within the valid range
        if target < self.min_value or target > self.max_value:
            raise ValueError(f"Target temperature must be between {self.min_value} and {self.max_value}.")
        
        self._laser.query(f"TEC:TTGT {target:.3f}")

    @property
    def temp(self) -> float:
        """Get the current temperature."""
        return float(self._laser.query("TEC:TEMP?"))

    @property
    def value(self) -> float:
        """Gets the TEC temperature.

        Returns:
            float: The TEC temperature.
        """
        return self.temp

