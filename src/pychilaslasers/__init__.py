# SPDX-License-Identifier: Apache-2.0
"""Package for controlling laser products from Chilas Lasers.

Modules:
    laser: Contains the main [Laser][pychilaslasers.Laser] class for laser control.
    modes: Contains laser modes, enums, and specific laser behaviors.
    laser_components: Contains classes for TEC, diode, drivers, and other components.
    comm: Handles communication over the serial connection.
    calibration: Calibration data management and loading functionality.
    constants: System constants and configuration values.

These classes encapsulate the behavior, properties, and state of laser components.
Interaction with the laser should be done through the [Laser][pychilaslasers.Laser]
class.
"""

from .laser import Laser

__all__: list[str] = [
    # Main laser class
    "Laser",
    "__version__",
]


from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pychilaslasers")
except PackageNotFoundError:
    __version__ = "0.0.0"  # fallback for local dev
