#!/usr/bin/env python
"""
Demo script for pychilaslasers library.

This demo script follows a typical usage of the library. It initializes a laser, powers it on
performs some common operations with it before safely shutting it down.
"""

import logging
from pathlib import Path
from pychilaslasers.modes import LaserMode
from pychilaslasers import Laser
from  basic_usage_sweeping import run_sweeping_example,select_com_port


# Change logging level to change the verbosity of the terminal output.
# Debug will print all the serial commands and responses sent to the laser.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


address: str = select_com_port()
# Path to calibration file/LookUpTable (lut)
fp_lut = Path("path/to/file")


# Initiate laser object
laser = Laser(com_port=address, calibration_file=fp_lut)

# Check connection state
print(f"Connection state {laser.system_state}")

# Turn on system
laser.system_state = True

# Steady tuning functionality
laser.mode = LaserMode.STEADY

# Set wavelength, e.g. 1550.000nm
laser.steady.wavelength = 1598.000

# Get current wavelength
print(f"Current wavelength is {laser.steady.wavelength}")
input("Press enter to continue...")

# Set wavelength in relative manner (apply step/offset), e.g. increase wavelength by 0.004nm
print(f"New wavelength is {laser.steady.set_wl_relative(0.004)}")

# ... or decrease wavelength with negative step, e.g. -1.000nm
print(f"New wavelength is {laser.steady.set_wl_relative(-1.000)}")

input("Press Enter to continue...")

# Emit a trigger pulse 
laser.trigger_pulse()


if laser.model == "COMET":
    run_sweeping_example(laser) 

# Turn off the laser
laser.system_state = False
