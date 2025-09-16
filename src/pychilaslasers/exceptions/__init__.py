"""PyChilasLasers exceptions module.

This module contains all custom exceptions for the PyChilasLasers library.
These exceptions provide specific error handling for laser operations and modes.

**Authors**: SDU
"""

# ✅ Local imports
from .laser_error import LaserError
from .mode_error import ModeError

__all__ = [
    "LaserError",
    "ModeError",
]
