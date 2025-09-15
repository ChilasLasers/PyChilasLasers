"""Laser diode component.

This module implements the laser diode component that controls the laser's
emission by managing the drive current and on/off state. Handles
laser enable/disable operations as well as current adjustments.

**Authors**: SDU
"""

# ⚛️ Type checking
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.laser import Laser

# ✅ Local imports
from pychilaslasers.laser_components.laser_component import LaserComponent


class Diode(LaserComponent):
    """Laser diode component for current control.

    Args:
        laser: The laser instance to control.

    Attributes:
        state: The current on/off state of the laser diode.
        current: The drive current level in milliamps.
        value: Alias for the drive current (inherited from LaserComponent).
        min_value: Minimum current (always 0.0 mA).
        max_value: Maximum current.
        unit: Current unit (mA).

    """

    def __init__(self, laser: Laser) -> None:
        """Initialize the diode component with laser instance.

        Sets up the laser diode component by querying the hardware for its
        maximum current and configuring the component with
        appropriate current range and units.

        Args:
            laser: The laser instance to control.

        """
        super().__init__(laser=laser)
        self._min: float = 0.0
        self._max: float = float(laser._comm.query("LSR:IMAX?"))
        self._unit: str = "mA"

    ########## Properties (Getters/Setters) ##########

    @property
    def state(self) -> bool:
        """Get the current on/off state of the laser diode.

        Returns:
            True if the laser diode is ON, False if OFF.

        """
        return bool(int(self._comm.query("LSR:STAT?")))

    @state.setter
    def state(self, state: bool) -> None:
        """Enable or disable laser emission by controlling the diode.

        Args:
            state: True to turn the laser ON, False to turn it OFF.

        """
        self._comm.query(f"LSR:STAT {state:d}")

    @property
    def current(self) -> float:
        """Returns the current drive current in milliamps.

        Returns:
            The current drive current in milliamps.

        """
        return float(self._comm.query("LSR:ILEV?"))

    @current.setter
    def current(self, current_ma: float) -> None:
        """Set the drive current of the laser diode.

        Args:
            current_ma: The desired drive current in milliamps.

        Raises:
            ValueError: If current is not a number or is outside the valid range.

        """
        # Validate the value
        if not isinstance(current_ma, (int, float)):
            raise ValueError("Current must be a number.")
        if current_ma < self._min or current_ma > self._max:
            raise ValueError(
                f"Current value {current_ma} not valid: must be between {self._min} "
                f"and {self._max} mA."
            )

        self._comm.query(f"LSR:ILEV {current_ma:.3f}")

    ########## Method Overloads/Aliases ##########

    def get_value(self) -> float:
        """Alias for the `value` property getter.

        Returns:
            The current drive current in milliamps.

        """
        return self.value

    def set_value(self, val: float) -> None:
        """Alias for the `value` property setter.

        Args:
            val: The desired drive current in milliamps.

        Raises:
            ValueError: If current is not a number or is outside the valid range.

        """
        self.value = val

    def get_current(self) -> float:
        """Alias for the `current` property getter.

        Returns:
            The current drive current in milliamps.

        """
        return self.current

    def set_current(self, current_ma: float) -> None:
        """Alias for the `current` property setter.

        Args:
            current_ma: The desired drive current in milliamps.

        Raises:
            ValueError: If current is not a number or is outside the valid range.

        """
        self.current = current_ma

    def turn_on(self) -> None:
        """Turn the laser diode ON.

        Alias for setting `state` to True.
        """
        self.state = True

    def turn_off(self) -> None:
        """Turn the laser diode OFF.

        Alias for setting `state` to False.
        """
        self.state = False

    @property
    def value(self) -> float:
        """Get the current drive current value.

        Alias for the `current` property to implement the LaserComponent interface.

        Returns:
            The current drive current in milliamps.

        """
        return self.current

    @value.setter
    def value(self, val: float) -> None:
        """Set the drive current value.

        Alias for the `current` property setter to implement the LaserComponent
        interface.

        Args:
            val: The desired drive current in milliamps.

        """
        self.current = val
