#!/usr/bin/env python
"""
Demo script for COMET lasers.
Date: 2025-03-26
"""

import time

from pathlib import Path
from lasers_swept import SweptLaser, OperatingMode

# Settings for COMET
address = "COM5"
# Path to calibration file/LookUpTable (lut)
fp_lut = Path(r"./calibration.csv")

if __name__ == "__main__":
    # Initiate object for COMET interaction
    laser = SweptLaser()

    # Optionally, print COM ports
    # print(laser.list_comports())

    # Specify address to use
    laser.port = address

    # Open connection
    laser.open_connection()
    try:
        # Check connection state
        print(f"Connection state {laser.is_connected=}")

        # Load calibration file
        laser.open_file_cycler_table(fp_lut)

        # Turn on COMET system
        laser.system_state = True

        # Sweeping functionality
        laser.operation_mode = OperatingMode.SWEEP

        # Start a sweep, where the laser will cycle between 1560.0 and 1550.0nm, for 10x cycles
        wavelengths, runtime = laser.sweep(
            wl_start=1560.0, wl_end=1550.0, num_sweeps=10
        )
        # Wait for sweep to finish
        time.sleep(runtime + 1)

        # Start a sweep, where the laser will cycle through the full LookUpTable, indefinitely (0x)
        wavelengths, runtime = laser.sweep_full(num_sweeps=0)
        print(f"Runtime for infinite running sweeps is {runtime=}")
        time.sleep(5)
        # Abort a running sweep
        laser.sweep_abort()

        # Get wavelength after
        print(f"Wavelength after aborting sweep, {laser.get_wavelength()=}")

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
        print(
            f"Wavelength corresponding to index 2123 is {laser.get_wavelength_idx(2123)=}"
        )

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
        laser.close_connection()
