#!/usr/bin/env python
"""
Demo script for COMET lasers.
Date: 2025-03-26
"""

import time

from pathlib import Path
from pychilaslasers.lasers_swept import OperatingMode
from pychilaslasers.atlas_laser import AtlasLaser

# Settings for COMET
address = "COM7"
# Path to calibration file/LookUpTable (lut)
fp_lut = Path(r"C:\\Users\\Sebastian\\Documents\\calibrationATLAS.csv")

if __name__ == "__main__":
    # Initiate object for COMET interaction
    laser = AtlasLaser()

    # Optionally, print COM ports
    # print(laser.list_comports())

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

        # Turn on COMET system
        laser.system_state = True

        # Steady tuning functionality
        laser.operation_mode = OperatingMode.STEADY

        # Set wavelength, e.g. 1550.000nm
        wavelength = laser.set_wavelength_abs(wl=1550.000)
        # Set wavelength, based on index from calibration file, e.g. 2123
        wavelength = laser.set_wavelength_abs_idx(2123)
        print(f"Corresponding {wavelength=:.3f}nm")

        # Get current wavelength
        print(f"Current wavelength is {laser.get_wavelength()=}")
        # Get current index
        print(f"Current cycler index is {laser.get_cycler_index()=}")
        # Get wavelength corresponding to certain index
        print(f"Wavelength corresponding to index 2123 is {laser.get_wavelength_idx(2123)=}")

        # Set wavelength in relative manner (apply step/offset), e.g. increase wavelength by 0.004nm
        print(f"New wavelength is {laser.set_wavelength_rel(wl_delta=0.004)=}")
        # ... or decrease wavelength with negative step, e.g. -1.000nm
        print(f"New wavelength is {laser.set_wavelength_rel(wl_delta=-1.000)=}")
        # Set wavelength in relative manner, by applying step/offset in index units, e.g. one unit later
        print(f"New wavelength is {laser.set_wavelength_rel_idx(1)=}")

        # Manually give a trigger pulse
        laser.trigger_pulse()

        # Turn off the laser
        laser.system_state = False
    finally:
        # Close the connection, which also resets the baudrate to its default value (57600)
        laser.close_connection()
