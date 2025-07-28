
from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

from pychilaslasers.modes.mode import Mode

if TYPE_CHECKING:
    from pychilaslasers import Laser


class __Calibrated(Mode):

    def __init__(self, laser: Laser) -> None:
        super().__init__()
        self._laser: Laser = laser

        # Initialize the mode-specific attributes
        self._autoTrig: bool = False


    @property
    def autoTrig(self) -> bool:
        """Get the auto-trigger setting."""
        return self._autoTrig
    @autoTrig.setter
    def autoTrig(self, value: bool) -> None:
        self._autoTrig = value
    def toggle_autoTrig(self, value: bool | None = None) -> None:
        """Toggle the auto-trigger setting."""
        self._autoTrig = value if value is not None else not self._autoTrig

    
    @property
    def min_wavelength(self) -> float:
        """Get the minimum wavelength."""
        return self._min_wl
    
    @property
    def max_wavelength(self) -> float:
        """Get the maximum wavelength."""
        return self._max_wl
    @property
    def min_wavelength(self) -> float:
        """Get the minimum wavelength."""
        return self._min_wl
    
    @property
    def max_wavelength(self) -> float:
        """Get the maximum wavelength."""
        return self._max_wl
