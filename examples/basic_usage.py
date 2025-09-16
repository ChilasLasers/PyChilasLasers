#!/usr/bin/env python
"""
Demo script for pychilaslasers library.

This demo script follows a typical usage of the library. It initializes a laser, powers it on,
performs some common operations, before safely shutting it down.
"""

import logging
from pathlib import Path
from pychilaslasers.modes import LaserMode
from pychilaslasers import Laser
from basic_usage_sweeping import run_sweeping_example, select_com_port


# Change logging level to change the verbosity of the terminal output.
# Debug will print all the serial commands and responses sent to the laser.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

com_port: str = select_com_port()

# Path to *.csv file, which contains the calibration Look-Up Table (lut)
path_calibration_lut = Path("path/to/file")

# Initiate laser object
laser = Laser(com_port=com_port, calibration_file=path_calibration_lut)

# Check laser connection
print(f"Connection state {laser.system_state}")

# Turn on laser system
laser.system_state = True

# Laser switches to tuning mode for wavelength tuning (applies to both COMET and ATLAS lasers)
laser.mode = LaserMode.STEADY

# Set laser wavelength to any value within the tuning range given by the calibration look-up table
laser.steady.wavelength = 1550.000  # nm

# Get current laser wavelength
print(f"Current wavelength is {laser.steady.wavelength} nm")
input("Press enter to continue...")

# Set wavelength in relative manner to apply a single step or offset
print(f"New wavelength is {laser.steady.set_wl_relative(0.100)} nm")

# ... or decrease wavelength with a negative step
print(f"New wavelength is {laser.steady.set_wl_relative(-1.000)} nm")
input("Press Enter to continue...")

# Emit a trigger pulse for synchronization with other equipment, e.g. to indicate that the wavelength is set
laser.trigger_pulse()

# Laser continues with sweeping example (only applies to COMET lasers)
if laser.model == "COMET":
    run_sweeping_example(laser) 

# Finally, turn off the laser
laser.system_state = False
