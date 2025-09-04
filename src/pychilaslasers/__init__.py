# SPDX-License-Identifier:  Apache-2.0
"""
Package for controlling laser products from Chilas Lasers. 

Modules:
    laser: Contains the main [Laser][pychilaslasers.Laser] class for laser control.
    modes: Contains laser modes which encompass specific laser behaviors as well as enums used interacting with these modes.
    laser_components: Contains classes for various laser components such as TEC, diode, and drivers.
    comm: Handles the communication over the serial connection
    utils: Contains utility functions and data structures for calibration and other operations.

These classes are used to encapsulate the behavior, properties and state of these components. Interaction with the laser should be done through the [Laser][pychilaslasers.Laser] class.
"""

from .laser import Laser

__all__: list[str] = [
    # Main laser class
    "Laser",
    "__version__"
]


from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pychilaslasers")
except PackageNotFoundError:
    __version__ = "0.0.0"  # fallback for local dev
