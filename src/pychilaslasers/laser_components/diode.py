from __future__ import annotations
from typing import TYPE_CHECKING

from pychilaslasers.laser_components.laser_component import LaserComponent

if TYPE_CHECKING:
    from pychilaslasers import Laser


class Diode(LaserComponent):

    def __init__(self, laser: Laser) -> None:
        super().__init__()
        self._laser: Laser = laser
        self._min: float = 0.0
        self._max: float = float(laser.query("LSR:IMAX?"))
        self._unit: str = "mA"

    def turn_ON(self) -> None:
        """Turns the laser diode ON."""
        self._laser.query("LSR:STAT 1")

    def turn_OFF(self) -> None:
        """Turns the laser diode OFF."""
        self.state = False

    @property
    def state(self) -> bool:
        """Gets the laser diode state.

        Returns:
            bool: The laser diode state.
        """
        return bool(int(self._laser.query("LSR:STAT?")))

    @state.setter
    def state(self, value: bool) -> None:
        """Sets the laser diode state.

        Args:
            value (bool): The laser diode state to be set.
        """
        self._laser.query(f"LSR:STAT {value:d}")

    @property
    def current(self) -> float:
        return float(self._laser.query("LSR:ILEV?"))

    @current.setter
    def current(self, current_ma: float) -> None:
        """Sets the laser diode current.

        Args:
            current_ma (float): The laser diode current to be set.
        """
        # Validate the value
        if not isinstance(current_ma, (int, float)):
            raise ValueError("Current must be a number.")
        if current_ma < self._min or current_ma > self._max:
            raise ValueError(f"Current must be between {self._min} and {self._max} mA.")
        
        self._laser.query(f"LSR:ILEV {current_ma:.3f}")

    @property
    def value(self) -> float:
        return self.current

    @value.setter
    def value(self, val: float) -> None:
        self.current = val
