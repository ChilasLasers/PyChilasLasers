"""Defines the system class, a container for some attributes of the laser."""

# ⚛️ Type checking
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers import Laser
    from pychilaslasers.comm import Communication

# ✅ Standard library imports
from functools import cached_property


class System:
    """Container for key laser attributes.

    Provides access to hardware and firmware metadata,
    serial number, and uptime. Attributes are read-only
    and may be lazily computed.

    Args:
        laser (Laser): The parent Laser instance.

    Attributes:
        hw_version (str): Hardware version of the laser.
        fw_version (str): Firmware version.
        serial_no (str): Laser serial number.
        uptime (float): Time elapsed since laser startup (seconds).
    """

    def __init__(self, laser: Laser) -> None:
        """System class acts as a container for some of the laser attributes.

        Attributes:
            hw_version: hardware version of the laser
            fw_version: version of the firmware running on the laser
            serial_no: serial number of the laser
            uptime:    the amount of time that has passed since the laser was turned on.

        Args:
            laser: laser of which system this is a component of
        """
        self._comm: Communication = laser.comm

    @cached_property
    def hw_version(self) -> str:
        """Hardware version of the laser as a string.

        Hardware version of the laser in x.y.z format, possibly with a single character
        variant suffix.
        """
        return self._comm.query("SYST:HWV?")

    @cached_property
    def fw_version(self) -> str:
        """Firmware version running on the laser.

        Firmware version of the laser in x.y.z format, possibly with a single character
        variant suffix.
        """
        return self._comm.query("SYST:FWV?")

    @cached_property
    def serial_no(self) -> str:
        """Serial number of the laser."""
        return self._comm.query("SYST:SRN?")

    @property
    def uptime(self) -> int:
        """System uptime in seconds."""
        return int(self._comm.query("SYST:UPT?"))
