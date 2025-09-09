"""
Abstract base class for laser modes that require calibration data.

This module defines the base class for modes that use calibration data to control
laser wavelengths and other calibrated parameters. It provides common functionality
shared between steady and sweep mode operations.

**Authors**: SDU
"""

# ⚛️ Type checking
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.laser import Laser

# ✅ Standard library imports
from abc import abstractmethod

# ✅ Local imports
from pychilaslasers.modes.mode import Mode


class __Calibrated(Mode):
    """Abstract base class for laser modes that work with calibration data.

    This class provides the basic structure and properties that are common to all
    "calibrated" modes such as steady and sweep mode. It handles auto-triggering
    functionality and wavelength range validation.

    The class is marked as private (double underscore prefix) as it should only be
    used as a base class for other mode implementations within this package.
    """

    def __init__(self, laser: Laser) -> None:
        """Initialize the calibrated mode base class.

        Args:
            laser: The parent laser instance that owns this mode.
        """
        super().__init__(laser)

        # Initialize the mode-specific attributes
        self._autoTrig: bool = False

    @property
    def autoTrig(self) -> bool:
        """Get the auto-trigger setting of the laser.

        This property indicates whether the laser is set to automatically send
        a trigger signal when the wavelength is changed. This is useful for
        synchronizing the laser with other equipment or processes that depend on it.

        Returns:
            True if auto-trigger is enabled, False otherwise.
        """
        return self._autoTrig

    @autoTrig.setter
    def autoTrig(self, state: bool) -> None:
        """Set the auto-trigger setting of the laser.

        Args:
            state: Whether to enable (True) or disable (False) auto-trigger.
        """
        self._autoTrig = state

    ########## Main Methods ##########

    def toggle_autoTrig(self, state: bool | None = None) -> None:
        """Toggle the auto-trigger setting.

        If `state` is provided, it sets the auto-trigger to that state.
        If `state` is None, it toggles the current state of auto-trigger.

        This is useful for quickly enabling or disabling the auto-trigger without
        having to explicitly set it to True or False.

        This method is an alternative to the setter for `autoTrig`.

        Args:
            state: The state to set the auto-trigger to. If None,
                it toggles the current state.
        """
        self._autoTrig = state if state is not None else not self._autoTrig

    ########## Properties (Getters/Setters) ##########

    @property
    def min_wavelength(self) -> float:
        """Get the minimum wavelength that the laser can be tuned to.

        Trying to set a wavelength below this value will raise an error.

        Returns:
            The minimum calibrated wavelength in nanometers.
        """
        return self._min_wl

    @property
    def max_wavelength(self) -> float:
        """Get the maximum wavelength that the laser can be tuned to.

        Trying to set a wavelength above this value will raise an error.

        Returns:
            The maximum calibrated wavelength in nanometers.
        """
        return self._max_wl

    @abstractmethod
    def get_wl(self) -> float:
        """Get the current wavelength of the laser.

        This method must be implemented by all subclasses to provide the
        current wavelength setting of the laser.

        Returns:
            The current wavelength in nanometers.
        """
        pass
