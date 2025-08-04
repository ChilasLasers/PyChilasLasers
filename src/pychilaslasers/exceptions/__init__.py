"""PyChilasLasers exceptions module.

This module contains all custom exceptions for the PyChilasLasers library.
These exceptions provide specific error handling for laser operations and modes.
<p>
Authors: SDU
Last Revision: Aug 4, 2025 - Created
"""

# ✅ Local imports
from .laser_error import LaserError
from .mode_error import ModeError

__all__ = [
    "LaserError",
    "ModeError",
]