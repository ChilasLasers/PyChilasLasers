#!/usr/bin/env python
"""
Demo script for ATLAS lasers.
Date: 2025-07-09
"""

import logging
from pathlib import Path
from pychilaslasers.atlas_laser import OperatingMode
from pychilaslasers.atlas_laser import AtlasLaser



# Optionally, print COM ports
# print(laser.list_comports())

# Settings for ATLAS
address = "COM31"
# Path to calibration file/LookUpTable (lut)
fp_lut = Path(r"G:\9500-9999 Laboratory workspace (PUBLIC)\Calibration files\MAC078\MAC078_settings.csv")

# Change logging level to change the verbosity of the terminal output.
# Debug will print all the serial commands and responses sent to the laser.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Initiate object for ATLAS interaction
laser = AtlasLaser()

# Specify address to use
laser.port = address

# Open connection
laser.open_connection()

# Increase the baud rate from 57600 to 460800 for 8x faster communication.
# The connection will be closed and re-opened at the new baud rate.
laser.baudrate = 460800
try:
    # Check connection state
    print(f"Connection state {laser.is_connected=}")

    # Load calibration file
    laser.open_file_cycler_table(fp_lut)

    # Turn on ATLAS system
    laser.system_state = True

    # Steady tuning functionality
    laser.operation_mode = OperatingMode.STEADY

    # Set wavelength, e.g. 1550.000nm
    wavelength = laser.set_wavelength_abs(wl=1545.000)


    #input("Press enter to continue...")

    # Set wavelength, based on index from calibration file, e.g. 2123
    wavelength = laser.set_wavelength_abs_idx(2123)
    print(f"Corresponding {wavelength=:.3f}nm")

    # Get current wavelength
    print(f"Current wavelength is {laser.get_wavelength()=}")

    # Get wavelength corresponding to certain index
    print(f"Wavelength corresponding to index 2123 is {laser.get_wavelength_idx(2123)=}")

    # Set wavelength in relative manner (apply step/offset), e.g. increase wavelength by 0.004nm
    print(f"New wavelength is {laser.set_wavelength_rel(wl_delta=0.004)=}")

    # ... or decrease wavelength with negative step, e.g. -1.000nm
    print(f"New wavelength is {laser.set_wavelength_rel(wl_delta=-1.000)=}")

    input("Press Enter to continue...")
    # Turn off the laser
    laser.system_state = False

finally:
    # Close the connection, which also resets the baudrate to its default value (57600)
    laser.close_connection()
