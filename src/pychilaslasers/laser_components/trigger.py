"""Container for trigger related functions of the laser."""

# ⚛️ Type checking
from __future__ import annotations
from typing import TYPE_CHECKING

# ✅ Local imports
from pychilaslasers.laser_components import LaserComponent

if TYPE_CHECKING:
    from pychilaslasers import Laser


class Trigger(LaserComponent):
    """Container for trigger related functions of the laser."""

    def __init__(self, laser: Laser):
        """Container for trigger related functions of the laser.

        Args:
            laser (Laser): The parent Laser instance.
        """
        super().__init__(laser)

        _x, _y, _z = [int(n) for n in laser.system.fw_version.split(".")]

        self.new: bool = tuple(int(n) for n in laser.system.fw_version.split(".")) > (
            1,
            3,
            15,
        )

    def UnsupportedOperationError(self, *args, **kwargs):  # noqa: D102, N802
        raise NotImplementedError("Operation not supported on current firmware version")

    def pulse(self) -> None:
        """Instructs the laser to send a trigger pulse."""
        self._comm.query(f"DRV:CYC:TRIG {int(True):d}")
        self._comm.query(f"DRV:CYC:TRIG {int(False):d}")

    @property
    def inverted(self) -> bool:
        """Returns if the trigger is inverted.

        The trigger can be inverted between active low and active high.
        """
        return bool(self._comm.query("DRV:CYC:INVT?"))

    @inverted.setter
    def inverted(self, value: bool | None) -> None:
        """Invert trigger between active low and active high.

        Args:
            value(bool|None):
                If none it will be set to the opposite of the current value.
        """
        if not self.new:
            self.UnsupportedOperationError()

        if value is None:
            self.inverted = False if self.inverted else True
        else:
            self._comm.query(f"DRV:CYC:INVT {int(value)}")

    @property
    def mode(self) -> int:
        """Return the current trigger mode.

        Returns:
             trigger mode(int):
                0 = START_STOP
                1 = ONLY_START
                2 = ONLY_STOP
        """
        if not self.new:
            self.UnsupportedOperationError()
        return int(self._comm.query("DRV:CYC:TM?"))

    @mode.setter
    def mode(self, mode: int) -> None:
        """Sets the trigger mode.

        Arguments:
            mode(int):
                0 = START_STOP
                1 = ONLY_START
                2 = ONLY_STOP
        """
        if not self.new:
            self.UnsupportedOperationError()
        self._comm.query(f"DRV:CYC:TM {mode}")

    @property
    def value(self) -> float:
        """N/A."""
        return 0.0
