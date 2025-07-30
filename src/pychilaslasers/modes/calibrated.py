"""
Abstract base class for laser modes that require calibration data.
<p>
This module defines the base class for modes that use calibration data to control 
laser wavelengths and other calibrated parameters. It provides common functionality 
shared between steady and sweep mode operations.
<p>
Authors: SDU
Last Revision: July 30, 2025 - Enhanced documentation and improved code formatting
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from pychilaslasers.modes.mode import Mode

if TYPE_CHECKING:
    from pychilaslasers import Laser


class __Calibrated(Mode):
    """Abstract base class for laser modes that work with calibration data.
    <p>
    This class provides the basic structure and properties that are common to all 
    "calibrated" modes such as steady and sweep mode. It handles auto-triggering 
    functionality and wavelength range validation.
    <p>
    The class is marked as private (double underscore prefix) as it should only be 
    used as a base class for other mode implementations within this package.
    """

    def __init__(self, laser: Laser) -> None:
        """Initialize the calibrated mode base class.
        
        Args:
            laser (Laser): The parent laser instance that owns this mode.
        """
        super().__init__(laser)

        # Initialize the mode-specific attributes
        self._autoTrig: bool = False


    @property
    def autoTrig(self) -> bool:
        """Get the auto-trigger setting of the laser.
        <p>
        This property indicates whether the laser is set to automatically send 
        a trigger signal when the wavelength is changed. This is useful for
        synchronizing the laser with other equipment or processes that depend on it.
        
        Returns:
            bool: True if auto-trigger is enabled, False otherwise.
        """
        return self._autoTrig
    
    @autoTrig.setter
    def autoTrig(self, value: bool) -> None:
        """Set the auto-trigger setting of the laser.
        
        Args:
            value (bool): Whether to enable (True) or disable (False) auto-trigger.
        """
        self._autoTrig = value


    ########## Main Methods ##########

    def toggle_autoTrig(self, value: bool | None = None) -> None:
        """Toggle the auto-trigger setting.
        <p>
        If `value` is provided, it sets the auto-trigger to that value.
        If `value` is None, it toggles the current state of auto-trigger.
        <p>
        This is useful for quickly enabling or disabling the auto-trigger without
        having to explicitly set it to True or False.
        <p>
        This method is an alternative to the setter for `autoTrig`.
        
        Args:
            value (bool | None): The value to set the auto-trigger to. If None,
                it toggles the current state.
        """
        self._autoTrig = value if value is not None else not self._autoTrig

    ########## Properties (Getters/Setters) ##########

    @property
    def min_wavelength(self) -> float:
        """Get the minimum wavelength that the laser can be tuned to.
        <p>
        Trying to set a wavelength below this value will raise an error.
        
        Returns:
            float: The minimum calibrated wavelength in nanometers.
        """
        return self._min_wl
    
    @property
    def max_wavelength(self) -> float:
        """Get the maximum wavelength that the laser can be tuned to.
        <p>
        Trying to set a wavelength above this value will raise an error.
        
        Returns:
            float: The maximum calibrated wavelength in nanometers.
        """
        return self._max_wl



   