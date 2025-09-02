"""
PyChilasLasers Module
<p>
This module provides functionality for controlling and interfacing with laser systems.

The package has the following structure:
    - ``laser.py`` : Contains the main `Laser` class for laser control.
    - `utils.py`: Contains utility functions and data structures for calibration and other operations.
    - `modes/`: Contains laser modes which encompass specific laser behaviors as well as enums used interacting with these modes.
    - `laser_components/`: Contains classes for various laser components such as TEC, diode, and drivers.

These classes are used to encapsulate the behavior, properties and state of these components. Interaction with the laser should be done through the `Laser` class.
"""

from .laser import Laser

__all__: list[str] = [
    # Main laser class
    "Laser",
    "__version__"
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Chilas B.V."
__email__ = "info@chilasbv.com"