


import logging
from pathlib import Path
from pychilaslasers import Laser

fp_lut = Path(r"C:\Users\labuser\20250124_MAP2059_TLM4_50nm_5pm_Full_280mA_PhaseFit_Headers.csv")

# Change logging level to change the verbosity of the terminal output.
# Debug will print all the serial commands and responses sent to the laser.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_sweeping_example(laser:Laser | None = None) -> None:
    if laser is None:
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

        laser = Laser(calibration_file=fp_lut, com_port=address)


    # Continue with the sweeping example using the laser object
    laser.system_state = True
    laser.mode = "sweeping"
    min_wavelength: float = laser.sweep.min_wavelength
    max_wavelength: float = laser.sweep.max_wavelength


    laser.sweep.interval = int(input("Enter the sweep interval (in us): "))
    print(f"Starting sweep from {min_wavelength}nm to {max_wavelength}nm")
    laser.sweep.start()

    input("Press Enter to stop the sweep...")
    laser.sweep.stop()

    print(f"Now sweeping with user-defined bounds. Min is {min_wavelength}nm, Max is {max_wavelength}nm")
    low_bound = input("Enter the lower bound wavelength (nm): ")
    high_bound = input("Enter the upper bound wavelength (nm): ")

    try:
        laser.sweep.set_bounds(float(low_bound), float(high_bound))
        print(f"Bounds set to {low_bound}nm - {high_bound}nm")
    except ValueError as e:
        print(f"Error setting bounds: {e}")

    laser.sweep.start()
    input("Press Enter to stop the sweep...")
    laser.sweep.stop()

    


if __name__ == "__main__":
    # Example usage
    run_sweeping_example()