from abc import ABC, abstractmethod
from enum import Enum

from __future__ import annotations
from typing import TYPE_CHECKING

from laser import Laser

if TYPE_CHECKING:
    from pychilaslasers import Laser


class LaserMode(Enum):
    MANUAL = "Manual"
    SWEEP = "Sweep"
    STEADY = "Steady"


class Mode(ABC):

    def __init__(self, laser: Laser) -> None:
        super().__init__()
        self._laser: Laser = laser

    @abstractmethod
    def apply_defaults(self) -> None:
        """Apply default settings for the mode."""
        pass

    @property
    @abstractmethod
    def mode(self) -> LaserMode:
        """Get the mode type."""
        pass