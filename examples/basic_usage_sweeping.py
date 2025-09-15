#!/usr/bin/env python
"""
Demo script for pychilaslasers library.

This demo script follows a typical usage of the library that showcases the sweeping 
mode functions that can be used on COMET lasers. 
"""

import logging
from pathlib import Path
from pychilaslasers import Laser


fp_lut = Path("path/to/file")

# Change logging level to change the verbosity of the terminal output.
# Debug will print all the serial commands and responses sent to the laser.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def select_com_port() -> str:  # noqa: D103
    from pychilaslasers import utils
    if len(ports:= utils.list_comports()) == 1:
        address: str = ports[0]
    elif len(ports) < 0:
        print("No COM ports found. Please connect the laser and try again.")
        exit(1)
    else:
        while True: 
            address = input(f"Available COM ports: {ports}\nPlease enter the COM port address: ")
            if address in ports:
                break
            print("Invalid COM port address. Please choose from.")

    return address


def run_sweeping_example(laser:Laser | None = None) -> None:  # noqa: D103
    if laser is None:
        laser = Laser(calibration_file=fp_lut, com_port=select_com_port())

    # Continue with the sweeping example using the laser object
    laser.system_state = True
    laser.mode = "sweeping"
    start_wavelength: float = laser.sweep.start_wavelength
    end_wavelength: float = laser.sweep.end_wavelength
    


    laser.sweep.interval = int(input("Enter the sweep interval (in us): "))
    print(f"Starting sweep from {start_wavelength}nm to {end_wavelength}nm")
    laser.sweep.start()

    input("Press Enter to stop the sweep...")
    laser.sweep.stop()

    print(f"Now sweeping with user-defined bounds. Min is {start_wavelength}nm, Max is {end_wavelength}nm")
    low_bound = input("Enter the start wavelength (nm): ")
    high_bound = input("Enter the end wavelength (nm): ")

    try:
        laser.sweep.set_range(float(low_bound), float(high_bound))
        print(f"Bounds set to {low_bound}nm - {high_bound}nm")
    except ValueError as e:
        print(f"Error setting bounds: {e}")

    laser.sweep.start()
    input("Press Enter to stop the sweep...")
    laser.sweep.stop()    


if __name__ == "__main__":
    # Example usage
    run_sweeping_example()




