from time import sleep
import logging
from pychilaslasers import Laser
from pychilaslasers.modes import LaserMode


logging.basicConfig(level=logging.DEBUG)

laser = Laser(com_port="COM7", calibration_file="tests/calibrationFiles/comet1.csv")

laser.system_state = True  # Turn on the laser

laser.tec.target = 25.0  # Set target temperature to 25 degrees Celsius
print(f"Current TEC temperature: {laser.tec.target} {laser.tec.unit}")





laser.mode = LaserMode.SWEEP
laser.sweep.set_range(1560.0,1550.0)  # Set sweep bounds
laser.sweep.start_wavelength = 1555.0  # Set start wavelength for the sweep


laser.sweep.start()  # Start the sweep mode
print(f"Current wavelength: {laser.sweep.wavelength} nm")
print(f"Current wavelength: {laser.sweep.wavelength} nm")
print(f"Current wavelength: {laser.sweep.wavelength} nm")
sleep(4)  # Wait for 2 seconds to allow the sweep to start  

print(f"Current wavelength: {laser.sweep.wavelength} nm")
print(f"Current wavelength: {laser.sweep.wavelength} nm")
print(f"Current wavelength: {laser.sweep.wavelength} nm")



print("No errors!")


