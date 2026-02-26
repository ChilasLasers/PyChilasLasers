"""Module defining multiple sensors on the laser."""

# ⚛️ Type checking
from __future__ import annotations
from typing import override, TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers import Laser

# ✅ Standard library imports
from enum import Enum
from functools import cached_property

# ✅ Local imports
from pychilaslasers.laser_components import LaserComponent


class EnclosureTemp(LaserComponent):
    """Component representing the temperature sensor on the laser module enclosure."""

    def __init__(self, laser: Laser):
        """Sensor on the enclosure of the laser.

        Args:
            laser(Laser): parent laser
        """
        super().__init__(laser)
        self._unit = "°C"

    @property
    @override
    def value(self) -> float:
        return self.temp

    @property
    def temp(self):
        """Returns the current temperature readout of the sensor on the enclosure."""
        self._comm.query("SYST:TEMP:NSEL 1")
        return float(self._comm.query("SYST:TEMP:TEMP?"))


class CPU(LaserComponent):
    """Component representing the temperature sensor in the CPU of the laser module."""

    def __init__(self, laser: Laser) -> None:
        """Temp sensor in the CPU of the laser module."""
        super().__init__(laser)
        self._unit = "°C"

    @property
    @override
    def value(self) -> float:
        return self.temp

    @property
    def temp(self):
        """Returns the current temperature readout of the sensor in the CPU."""
        self._comm.query("SYST:TEMP:NSEL 1")
        return float(self._comm.query("SYST:TEMP:TEMP?"))


class PhotoDiodeChannel(Enum):
    """Enum representing the available photodiode channels."""

    PD1 = 0
    PD2 = 1


class PhotoDiode(LaserComponent):
    """Component representing one of the photodiodes in the laser."""

    def __init__(self, laser: Laser, channel: int | PhotoDiodeChannel) -> None:
        """Photodiode of laser.

        Args:
            laser(Laser): Parent laser.
            channel(int | PhotodiodeChannel): channel of photodiode
        """
        super().__init__(laser)
        self._channel: PhotoDiodeChannel = (
            channel
            if isinstance(channel, PhotoDiodeChannel)
            else PhotoDiodeChannel(channel)
        )

    @property
    @override
    def value(self) -> float:
        return self.readout

    @property
    def readout(self) -> float:
        """Returns the photodiode readout as a float."""
        return float(self._comm.query(f"MEAS:M? {self.channel}"))

    @cached_property
    @override
    def unit(self) -> str:
        return self._comm.query(f"MEAS:UNIT? {self.channel}")

    @property
    def channel(self) -> PhotoDiodeChannel:
        """Measurement channel of the photodiode."""
        return self._channel
