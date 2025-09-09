#!/usr/bin/env python
"""
Demo script for ATLAS lasers.
Date: 2025-07-09
"""

from encodings.punycode import T
import logging
from pathlib import Path

from pychilaslasers import Laser,utils



# Optionally, print COM ports
# print(laser.list_comports())

# Settings for ATLAS


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





# Path to calibration file/LookUpTable (lut)
fp_lut = Path(r"G:\9500-9999 Laboratory workspace (PUBLIC)\Calibration files\MAC077\20250121_MAC077_TLM10_15nm_8pm_280mA_PhaseFit.csv")

# Change logging level to change the verbosity of the terminal output.
# Debug will print all the serial commands and responses sent to the laser.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Initiate object for ATLAS interaction
laser = Laser(com_port=address, calibration_file=fp_lut)


# Increase the baud rate from 57600 to 460800 for 8x faster communication.
# The connection will be closed and re-opened at the new baud rate.
# laser.baudrate = 460800
try:
    # Check connection state
    print(f"Connection state {laser.system_state}")


    # Turn on ATLAS system
    laser.system_state = True

    # Steady tuning functionality
    laser.mode = "steady"

    # Set wavelength, e.g. 1550.000nm
    wavelength = laser.steady.wavelength = 1598.000


    # input("Press enter to continue...")

    # Get current wavelength
    print(f"Current wavelength is {laser.steady.wavelength}")

    # Set wavelength in relative manner (apply step/offset), e.g. increase wavelength by 0.004nm
    print(f"New wavelength is {laser.steady.set_wl_relative(0.004)}")

    # ... or decrease wavelength with negative step, e.g. -1.000nm
    print(f"New wavelength is {laser.steady.set_wl_relative(-1.000)}")

    # input("Press Enter to continue...")
    # Turn off the laser
    laser.system_state = False

    if laser.model == "COMET":
        from  basic_usage_sweeping import run_sweeping_example
        run_sweeping_example(laser) 


finally:
    # Close the connection, which also resets the baudrate to its default value (57600)
    laser.system_state = False
