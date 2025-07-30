"""
Laser diode component 
<p>
This module implements the laser diode component that controls the laser's
emission by managing the drive current and on/off state. Handles
laser enable/disable operations as well as current adjustments.
<p>
Authors: SDU
Last Revision: July 30, 2025 - Enhanced documentation and improved code formatting
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from pychilaslasers.laser_components.laser_component import LaserComponent

if TYPE_CHECKING:
    from pychilaslasers import Laser


class Diode(LaserComponent):
    """Laser diode component for current control.
    <p>
    The Diode class encapsulates the control of the laser's diode.
    <p>
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
        <p>
        Sets up the laser diode component by querying the hardware for its
        maximum current and configuring the component with
        appropriate current range and units.
        
        Args:
            laser: The laser instance to control.
        """
        super().__init__(laser=laser)
        self._min: float = 0.0
        self._max: float = float(laser.query("LSR:IMAX?"))
        self._unit: str = "mA"

    ########## Properties (Getters/Setters) ##########

    @property
    def state(self) -> bool:
        """Get the current on/off state of the laser diode.

        Returns:
            bool: True if the laser diode is ON, False if OFF.
        """
        return bool(int(self._laser.query("LSR:STAT?")))

    @state.setter
    def state(self, value: bool) -> None:
        """Set the on/off state of the laser diode.
        <p>
        Controls laser emission by enabling or disabling the diode.

        Args:
            value: True to turn the laser ON, False to turn it OFF.
        """
        self._laser.query(f"LSR:STAT {value:d}")

    @property
    def current(self) -> float:
        """Get the current drive current of the laser diode.
        
        Returns:
            float: The current drive current in milliamps.
        """
        return float(self._laser.query("LSR:ILEV?"))

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
            raise ValueError(f"Current must be between {self._min} and {self._max} mA.")
        
        self._laser.query(f"LSR:ILEV {current_ma:.3f}")

    ########## Method Overloads/Aliases ##########

    def turn_ON(self) -> None:
        """Turn the laser diode ON.
        <p>
        Alias for setting :attr:`state` to True.
        """
        self.state = True

    def turn_OFF(self) -> None:
        """Turn the laser diode OFF.
        <p>
        Alias for setting :attr:`state` to False.
        """
        self.state = False

    @property
    def value(self) -> float:
        """Get the current drive current value.
        <p>
        Alias for the :attr:`current` property to implement the LaserComponent interface.

        Returns:
            float: The current drive current in milliamps.
        """
        return self.current

    @value.setter
    def value(self, val: float) -> None:
        """Set the drive current value.
        <p>
        Alias for the :attr:`current` property setter to implement the LaserComponent interface.
        
        Args:
            val: The desired drive current in milliamps.
        """
        self.current = val
