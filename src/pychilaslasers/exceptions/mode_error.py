"""Exception class for laser mode-related errors.

This module defines the ModeError exception which is raised when operations
are attempted in or for incompatible laser modes. It provides detailed information
about the current mode and suggests the correct mode for the operation.

**Authors:** SDU
"""

# ⚛️ Type checking
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychilaslasers.modes.mode import Mode

# ✅ Local imports
from pychilaslasers.modes.mode import LaserMode


class ModeError(Exception):
    """Exception raised for errors related to the laser mode."""

    def __init__(
        self,
        message: str,
        current_mode: LaserMode | Mode,
        desired_mode: LaserMode | Mode | None = None,
    ) -> None:
        """Exception raised in case of an error related to the mode the laser is in.

        This exception is used to indicate that an operation cannot be performed
        in the current mode of the laser.
        It provides information about the current mode and the desired mode that would
        allow the operation to succeed

        Args:
            message (str): The error message.
            current_mode (LaserMode): The current mode of the laser.
            desired_mode (LaserMode | None, optional): The laser mode that would allow
                for the operation to succeed. Defaults to None.

        """
        super().__init__(message)
        self.message: str = message

        # Checking to allow for the use of both LaserMode and Mode types
        self.current_mode: LaserMode = (
            current_mode if isinstance(current_mode, LaserMode) else current_mode.mode
        )
        self.desired_mode: LaserMode | None = (
            desired_mode
            if isinstance(desired_mode, LaserMode)
            else (desired_mode.mode if desired_mode is not None else None)
        )
        # Constructing the error message
        if self.desired_mode:
            self.message += (
                f" (current mode: {self.current_mode.name}, mode this"
                + f" operation is possible in: {self.desired_mode.name})"
            )
        else:
            self.message += f" (current mode: {self.current_mode.name})"

    def __str__(self) -> str:  # noqa: D105
        return f"ModeError: {self.message}"
