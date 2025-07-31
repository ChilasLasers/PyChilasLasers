from csv import reader
from pathlib import Path


class Constants:
    """Constants used throughout the PyChilasLasers library."""

    DEFAULT_BAUDRATE = 57600
    SUPPORTED_BAUDRATES = {9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400, 460800, 912600}
    # ERROR CODES THAT SHOULD TRIGGER A ERROR DIALOG (errors 14 to 23)
    CRITICAL_ERRORS: list[str] = ["E0" + str(x) for x in range(14,24)] + ["E0" + str(x) for x in range(30,51)]

    # Commands that can be replaced with a semicolon to speed up communication in firmware TODO
    SEMICOLON_COMMANDS: list[str] = [
        "DRV:CYC:GW?",
        "DRV:CYC:GET?",
        "DRV:CYC:PUT",
        "DRV:CYC:SETT",
        "DRV:CYC:STRW"]

    HARD_CODED_LASER_MODEL: str = "COMET"
    
    # Steady mode default values
    HARD_CODED_STEADY_CURRENT: float = 295.0
    HARD_CODED_STEADY_TEC_TEMP: float = 25.0
    HARD_CODED_STEADY_ANTI_HYST: tuple = ([1.0, 2.0, 3.0], [0.1, 0.2, 0.3])
    
    # Sweep mode default values (for COMET model)
    HARD_CODED_SWEEP_CURRENT: float = 280.0
    HARD_CODED_SWEEP_TEC_TEMP: float = 25.0
    HARD_CODED_INTERVAL: int = 100


from dataclasses import dataclass
from typing import Tuple

@dataclass
class CalibrationEntry:
    """Represents a single entry in the calibration data.
    """
    wavelength: float 
    phase_section: float
    large_ring: float
    small_ring: float
    coupler: float
    heater_values: Tuple[float, float, float, float]  # The prev values for but in a list
    mode_index: int | None
    cycler_index: int 


def read_calibration_file(file_path: str | Path) -> dict:
    """ Utility function to read a calibration file of a laser.

    Returns a calibration object which is a dictionary with the following structure:
    {
        "model": str,  # The model of the laser
        "steady": {
            "current": float,  # Default current for steady mode
            "tec_temp": float,  # Default TEC temperature for steady mode
            "anti-hyst": tuple(voltages^2(list(float)),time_steps(list(float))),  # anti-hyst values for steady mode
            "calibration": dict[wavelength(float) -> CalibrationEntry]
        
        Due to how the tables are initialized the steady calibration dictionary does not contain
        the entries with mode hop flags just the final entry for each wavelength.
        This is fine for steady mode as those entries are not used in steady mode for
        the COMET model. However, this means that the index of the wavelengths in list of keys of the
        dictionary is not the same as it's cycler index.
        
        
        },
        "sweep": {
            "current": float,  # Default current for sweep mode
            "tec_temp": float,  # Default TEC temperature for sweep mode
            "sweep_interval": int(micro-seconds),  # Default sweep interval for sweep mode
            "wavelengths": list(float),  # List of wavelengths for sweep mode

            This list contains duplicate entries for each wavelength that has a mode hop.
            This is because the sweep mode uses the cycler index to set the wavelength, 
            which is based on the order of wavelengths in the list.

        }

        

    }
    """
    model: str = Constants.HARD_CODED_LASER_MODEL

    calibration: dict = {
        "model": model,
        "steady": {
            "current": Constants.HARD_CODED_STEADY_CURRENT,  # Default current for steady mode
            "tec_temp": Constants.HARD_CODED_STEADY_TEC_TEMP,  # Default TEC temperature for steady mode
            "anti-hyst": Constants.HARD_CODED_STEADY_ANTI_HYST,  # anti-hyst values for steady mode
            "calibration": {}  # Calibration data for steady mode
        }
    }

    if model == "COMET":
        calibration["sweep"] = {
            "current": Constants.HARD_CODED_SWEEP_CURRENT,  # Default current for sweep mode
            "tec_temp": Constants.HARD_CODED_SWEEP_TEC_TEMP,  # Default TEC temperature for sweep mode
            "interval": Constants.HARD_CODED_INTERVAL,  # Default interval for sweep mode
            "wavelengths": []  # List of wavelengths for sweep mode
        }

    with open(file_path, newline='') as csvfile:
        # Read content first to detect dialect
        content = csvfile.read()
        csvfile.seek(0)  # Reset to beginning
        
        # Handle empty files
        if not content.strip():
            return calibration
            
        # Use semicolon delimiter explicitly for calibration files
        csv_reader = reader(csvfile, delimiter=';')
        cycler_index: int = 0  # Initialize cycler index for COMET model
        mode_index = 0  # Initialize mode index for COMET model
        hop: bool = False
        for row in csv_reader:

            # Logic for only incrementing the mode_index once per mode hop
            if model == "COMET":
                if hop and row[5] == "0":
                    hop = False
                if row[5] == "1":
                    hop = True
                    mode_index += 1  # Increment mode index
                else:
                    mode_index += 1  # Increment mode index 

            # Adding calibration entry to the dictionary
            calibration["steady"]["calibration"][float(row[4])] = CalibrationEntry(
                wavelength=float(row[4]),
                phase_section=float(row[0]),
                large_ring=float(row[1]),
                small_ring=float(row[2]),
                coupler=float(row[3]),
                heater_values=(float(row[0]), float(row[1]), float(row[2]), float(row[3])), 
                mode_index=mode_index if model == "COMET" else None,
                cycler_index=cycler_index
            )
            # Append wavelength to the sweep wavelengths list
            if model == "COMET":
                calibration["sweep"]["wavelengths"].append(float(row[4]))
            
            cycler_index += 1  # Increment cycler index 

    return calibration



from serial.tools.list_ports import comports


@staticmethod
def list_comports() -> list[str]:
    """Lists all available COM ports on the system.
    :py:func:`serial.tools.list_ports.comports` is used to list all available
    ports. In that regard this method is but a wrapper for it.

    Returns:
        List of available COM ports as strings sorted
        alphabetically in ascending order.
    """
    return sorted([port.device for port in comports()])
