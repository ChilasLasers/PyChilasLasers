"""
Temperature control (TEC) component

The TEC component allows for setting target temperatures as well as monitoring current temperatures.

**Authors**: SDU
"""

# ⚛️ Type checking
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.laser import Laser

# ✅ Local imports
from pychilaslasers.laser_components.laser_component import LaserComponent


class TEC(LaserComponent):
    """Temperature control component for laser thermal management.

    This component automatically retrieves its operating range limits from the
    laser hardware and provides input validation.

    Attributes:
        target: The target temperature in Celsius.
        temp: The current measured temperature in Celsius.
        value: Alias for the current temperature (inherited from LaserComponent).
        min_value: Minimum allowable temperature target.
        max_value: Maximum allowable temperature target.
        unit: Temperature unit (Celsius).
    """

    def __init__(self, laser: Laser) -> None:
        """
        Sets up the temperature control component by querying the laser hardware
        for its temperature operating limits and configuring the component
        with appropriate units and ranges.

        Args:
            laser: The laser instance to control.
        """
        super().__init__(laser=laser)
        self._min: float = float(self._comm.query("TEC:CFG:TMIN?"))
        self._max: float = float(self._comm.query("TEC:CFG:TMAX?"))
        self._unit: str = "Celsius"

    ########## Properties (Getters/Setters) ##########

    @property
    def target(self) -> float:
        """Get the current target temperature in Celsius."""
        return float(self._comm.query("TEC:TTGT?"))

    @target.setter
    def target(self, target: float) -> None:
        """Set the target temperature of the TEC.

        Args:
            target: The desired temperature in Celsius.

        Raises:
            ValueError: If target is not a number or is outside the valid range.
        """
        # Validate the target temperature
        if not isinstance(target, (int, float)):
            raise ValueError("Target temperature must be a number.")
        # Check if the target is within the valid range
        if target < self.min_value or target > self.max_value:
            raise ValueError(
                f"Target temperature value {target} not valid: must be between {self.min_value} and {self.max_value} °C."
            )

        self._comm.query(f"TEC:TTGT {target:.3f}")

    @property
    def temp(self) -> float:
        """Get the current **measured** temperature reading in Celsius."""
        return float(self._comm.query("TEC:TEMP?"))

    @property
    def value(self) -> float:
        """Get the current temperature value.

        Note:
            This is an alias for the `temp` property.
        """
        return self.temp

    ########## Method Overloads/Aliases ##########

    def get_value(self) -> float:
        """
        Alias for the `value` property getter.

        Returns:
            The current measured temperature in Celsius.
        """
        return self.value

    def set_value(self, val: float) -> None:
        """
        Alias for the `target` property setter.

        Args:
            val: The desired target temperature in Celsius.

        Raises:
            ValueError: If target is not a number or is outside the valid range.
        """
        self.target = val

    def get_temp(self) -> float:
        """
        Alias for the `temp` property getter.

        Returns:
            The current measured temperature in Celsius.
        """
        return self.temp

    def get_target_temp(self) -> float:
        """
        Alias for the `target` property getter.

        Returns:
            The current target temperature in Celsius.
        """
        return self.target

    def set_target(self, target: float) -> None:
        """
        Alias for the `target` property setter.

        Args:
            target: The desired target temperature in Celsius.

        Raises:
            ValueError: If target is not a number or is outside the valid range.
        """
        self.target = target
