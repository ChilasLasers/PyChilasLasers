from time import sleep
import logging
from pychilaslasers import Laser
from pychilaslasers.modes import LaserMode


logging.basicConfig(level=logging.INFO)

laser = Laser(com_port="COM7", calibration_file="tests/calibrationFiles/comet1_with_settings.csv")

laser.system_state = True  # Turn on the laser

laser.tec.target = 25.0  # Set target temperature to 25 degrees Celsius
print(f"Current TEC temperature: {laser.tec.target} {laser.tec.unit}")





laser.mode = LaserMode.SWEEP
laser.sweep.stop()
laser.sweep.set_range(1560.0,1550.0)  # Set sweep bounds
laser.sweep.start_wavelength = 1555.0  # Set start wavelength for the sweep


laser.sweep.start()  # Start the sweep mode
print(f"Current wavelength: {laser.sweep.wavelength} nm")
print(f"Current wavelength: {laser.sweep.wavelength} nm")
print(f"Current wavelength: {laser.sweep.wavelength} nm")
sleep(1)  # Wait for 1 second to allow the sweep to start

print(f"Current wavelength: {laser.sweep.wavelength} nm")
print(f"Current wavelength: {laser.sweep.wavelength} nm")
print(f"Current wavelength: {laser.sweep.wavelength} nm")


# TODO go trough all files and check for comments about imports like in laser.py
# TODO go trough all files and check for type checking init like laser.py


#  TODO move step size to calibrated class
print("No errors!")

print("\nLaser Default Settings:")
print(f"  laser_model: {laser.model}")
laser.mode = "sweep"
print(f"  sweep_tec_target: {laser.sweep._default_TEC}")
print(f"  sweep_diode_current: {laser.sweep._default_current}")
print(f"  sweep_interval: {laser.sweep._default_interval}")
laser.mode = "steady"
print(f"  tune_tec_target: {laser.steady._default_TEC}")
print(f"  tune_diode_current: {laser.steady._default_current}")



