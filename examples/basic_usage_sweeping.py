#!/usr/bin/env python
"""
Demo script for pychilaslasers library.

This demo script follows a typical usage of the library that showcases the sweeping 
mode functions that can be used on COMET lasers. 
"""

import logging
from pathlib import Path
from pychilaslasers import Laser


# Path to *.csv file, which contains the calibration Look-Up Table (lut)
path_calibration_lut = Path("path/to/file")

# Change logging level to change the verbosity of the terminal output.
# Debug will print all the serial commands and responses sent to the laser.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def select_com_port() -> str:
    from pychilaslasers import utils
    if len(ports := utils.list_comports()) == 1:
        selected_com_port: str = ports[0]
    elif len(ports) < 0:
        print("No COM ports found. Please connect the laser and try again.")
        exit(1)
    else:
        while True:
            selected_com_port = input(f"Available COM ports: {ports}\nPlease enter the COM port address: ")
            if selected_com_port in ports:
                break
            print("Invalid COM port address. Please choose from.")
    return selected_com_port


def run_sweeping_example(laser:Laser | None = None) -> None:
    # Continue with the sweeping example using the laser object
    if laser is None:
        laser = Laser(calibration_file=path_calibration_lut, com_port=select_com_port())

    # Turn on laser system
    laser.system_state = True

    # Laser switches to sweep mode for wavelength sweeping (applies only to COMET lasers)
    laser.mode = "sweeping"

    # Automatically define the sweep range for a full sweep, based on the maximum tuning range of the calibration look-up table
    start_wavelength: float = laser.sweep.start_wavelength
    end_wavelength: float = laser.sweep.end_wavelength
    print(f"Starting sweep from {start_wavelength} nm to {end_wavelength} nm")

    # Start a full wavelength sweep for an infinite number of sweeps, until it is interrupted by stop()
    laser.sweep.start()

    # Stop wavelength sweep
    input("Press Enter to stop the sweep...")
    laser.sweep.stop()

    # Manually define the sweep range
    print(f"Now sweeping with user-defined bounds. Min is {start_wavelength}nm, Max is {end_wavelength}nm")
    low_bound = input("Enter the start wavelength (nm): ")
    high_bound = input("Enter the end wavelength (nm): ")

    try:
        laser.sweep.set_range(float(low_bound), float(high_bound))
        print(f"Bounds set to {low_bound}nm - {high_bound}nm")
    except ValueError as e:
        print(f"Error setting bounds: {e}")

    # Start a full wavelength sweep for an infinite number of sweeps, until it is interrupted by stop()
    laser.sweep.start()

    # Stop wavelength sweep
    input("Press Enter to stop the sweep...")
    laser.sweep.stop()    


if __name__ == "__main__":
    # Example usage
    run_sweeping_example()
