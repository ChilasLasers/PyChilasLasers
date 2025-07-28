from abc import ABC, abstractmethod
from enum import Enum


class LaserMode(Enum):
    MANUAL = "Manual"
    SWEEP = "Sweep"
    STEADY = "Steady"


class Mode(ABC):

    @abstractmethod
    def apply_defaults(self) -> None:
        """Apply default settings for the mode."""
        pass

    @property
    @abstractmethod
    def mode(self) -> LaserMode:
        """Get the mode type."""
        pass