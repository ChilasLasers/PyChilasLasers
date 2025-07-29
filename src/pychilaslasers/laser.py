"""
Laser base object to communicate with Chilas Lasers.
Authors: RLK, AVR, SDU
"""


# Standard library imports
from pathlib import Path
import logging
import serial

# Local imports
from pychilaslasers.modes.manual_mode import ManualMode
from pychilaslasers.modes.steady_mode import SteadyMode
from pychilaslasers.modes.sweep_mode import SweepMode
from .laser_components import TEC, Diode
from .modes.mode import LaserMode, Mode
from .utils import Constants, read_calibration_file

logger: logging.Logger = logging.getLogger(__name__)


class Laser:
    """Generic Laser class for Chilas lasers."""


    def __init__(self, com_port: str, calibration_file: str | Path) -> None:
        self._initialize_variables()

        # Initialize serial connection to the laser
        self._serial: serial.Serial = serial.Serial(
            port=com_port,
            baudrate=Constants.DEFAULT_BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=10.0,
        )
        
        if "Chilas" not in self.query("*IDN?"):
            logger.critical("Laser is not a Chilas device")
            import sys
            sys.exit(1)

        # Initialize laser components

        self.tec: TEC = TEC(self)
        self.diode: Diode = Diode(self)

        
        self._manual_mode: ManualMode = ManualMode(self)

        calibration = read_calibration_file(file_path=calibration_file)
        self._model: str = calibration["model"]

        self._steady_mode: SteadyMode | None = SteadyMode(self, calibration) if calibration else None
        self._sweep_mode: SweepMode | None = SweepMode(self, calibration) if calibration["model"] == "COMET" else None
        self._mode: Mode = self._manual_mode


        logger.debug(f"Initialized laser {self._model} on {com_port} with calibration file {calibration_file}")

        self._prefix_mode: bool = True  # Default to prefix mode TODO may go in special calibration class

    ########## Main Methods ##########


    def trigger_pulse(self) -> None:
        """Trigger a laser pulse."""
        self.query(f"DRV:CYC:TRIG {int(True):d}")
        self.query(f"DRV:CYC:TRIG {int(False):d}")


    def query(self, data: str):
        """Send a command to the laser."""

        # Write the command to the serial port
        logger.debug(msg=f"W {data}")  # Logs the command being sent
        self._serial.write(
            f"{self._semicolon_replace(data)}\r\n"
            .encode("ascii")
            )

        # Read the response from the laser
        reply: str = self._serial.readline().decode("ascii").rstrip()

        # Error handling
        if not reply:
            logger.error("Empty reply from device")
            return reply

        if reply[0] != "0":
            logger.error(f"Nonzero return code: {reply[2:]}")
        else:
            logger.debug(f"R {reply}")

        return reply[2:]

    ########## Private Methods ##########

    def _semicolon_replace(self, cmd: str) -> str:
        """To speed up communication, a repeating command can be replaced with a semicolon.
        Check if the command was previously sent to the device. In that case, replace it with a semicolon.

        Args:
            cmd (str): The command to be replaced with semicolon.

        Returns:
            str: The command with semicolon inserted
        """
        if cmd.split(" ")[0] == self._previous_command and self._previous_command in Constants.SEMICOLON_COMMANDS:
            cmd = cmd.replace(cmd.split(" ")[0], ";")
        else:
            self._previous_command = cmd.split(" ")[0]
        return cmd

    def _initialize_variables(self) -> None:
        """Initialize private variables."""
        self._previous_command: str = "None"

    ########## Properties (Getters/Setters) ##########


    @property
    def system_state(self) -> bool:
        """Gets the system state.

        Returns:
            bool: The system state.
        """
        return bool(int(self.query("SYST:STAT?")))

    @system_state.setter
    def system_state(self, value: bool) -> None:
        """Sets the system state.

        Args:
            value (bool): The system state to be set.
        """
        if type(value) is not bool:
            logger.error("ERROR: given value is not a boolean")
            return
        self.query(f"SYST:STAT {value:d}")


    @property
    def mode(self) -> LaserMode:
        """Gets the current mode of the laser."""
        return self._mode.mode

    @mode.setter
    def mode(self, mode: LaserMode|Mode|str) -> None:
        """Sets the current mode of the laser."""

        # Check if the mode is an instance of specific mode classes
        if isinstance(mode, Mode):  
            if isinstance(mode, ManualMode):
                self._mode = self._manual_mode

            elif isinstance(mode, SteadyMode):
                self._mode = self._steady_mode

            elif isinstance(mode, SweepMode):
                self._mode = self._sweep_mode

        # Check if the mode is a string or enum
        elif isinstance(mode, str) or isinstance(mode, LaserMode):
            if isinstance(mode, LaserMode):
                mode = mode.value  # Convert enum to string if necessary

            # Define mode mappings including exact matches and fuzzy matches
            mode_mappings = {
                "manual": self._manual_mode,  # Exact match
                "steady": self._steady_mode,  # Exact match
                "sweep":  self._sweep_mode,   # Exact match
                "manuel": self._manual_mode,  # Common misspelling
                "manua":  self._manual_mode,   # Partial typing
                "man":    self._manual_mode,     # Short form
                "steadi": self._steady_mode,  # Partial typing
                "stead":  self._steady_mode,   # Partial typing
                "ste":    self._steady_mode,   # Partial typing
                "swep":   self._sweep_mode,     # Common misspelling
                "swp":    self._sweep_mode,     # Common misspelling
                "sweap":  self._sweep_mode,    # Common misspelling
                "sweepin": self._sweep_mode,  # Partial typing
                "sweeping":  self._sweep_mode,    # Exact match
            }

            if ( mode := mode.lower() ) in mode_mappings:
                self._mode = mode_mappings[mode]
            if self._mode is None:
                raise NotImplementedError("Proper exception to be raised here")
                raise ModeNotInitializedError(f"Mode {mode} is not initialized.")
                
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        self._mode.apply_defaults()
        logger.info(f"Laser mode set to {self._mode.mode}")
        return
        


    @property
    def steady(self) -> SteadyMode:
        """Gets the steady mode instance."""
        if self._steady_mode is None:
            raise NotImplementedError("Proper exception to be raised here")
            raise NotCalibratedError("Steady mode is not initialized.")
        if self.mode != LaserMode.STEADY:
            raise NotImplementedError("Proper exception to be raised here")
            raise IncorrectModeError("Laser not in steady mode.")
        return self._steady_mode
    
    @property
    def sweep(self) -> SweepMode:
        """Gets the sweep mode instance."""
        if self._sweep_mode is None:
            raise NotImplementedError("Proper exception to be raised here")
            raise NotCalibratedError("Sweep mode is not initialized.")
        if self.mode != LaserMode.SWEEP:
            raise NotImplementedError("Proper exception to be raised here")
            raise IncorrectModeError("Laser not in sweep mode.")
        return self._sweep_mode
    
    @property
    def manual(self) -> ManualMode:
        """Gets the manual mode instance."""
        if self.mode != LaserMode.MANUAL:
            raise NotImplementedError("Proper exception to be raised here")
            raise IncorrectModeError("Laser not in manual mode.")
        return self._manual_mode

    @property
    def prefix_mode(self) -> bool:
        """Gets prefix mode for the laser driver

        The laser driver can be operated in two different communication modes:
            1. Prefix mode on
            2. Prefix mode off

        When prefix mode is on, every message over the serial connection will be
        replied to by the driver with a response, and every response will be prefixed
        with a return code (rc), either `0` or `1` for an OK or ERROR respectively.

        With prefix mode is off, responses from the laser driver are not prefixed
        with a return code. This means that in the case for a serial write command
        without an expected return value, the driver will not send back a reply.

        Returns:
            (bool): whether prefix mode is enabled (True) or disabled (False)
        """
        self._prefix_mode = bool(int(self.query("SYST:COMM:PFX?")))
        return self._prefix_mode

    @prefix_mode.setter
    def prefix_mode(self, mode: bool) -> None:
        """Sets prefix mode for the laser driver

        The laser driver can be operated in two different communication modes:
            1. Prefix mode on
            2. Prefix mode off

        When prefix mode is on, every message over the serial connection will be
        replied to by the driver with a response, and every response will be prefixed
        with a return code (rc), either `0` or `1` for an OK or ERROR respectively.

        With prefix mode is off, responses from the laser driver are not prefixed
        with a return code. This means that in the case for a serial write command
        without an expected return value, the driver will not send back a reply.

        Args:
            mode (bool): whether to enable prefix mode (True) or disable it (False)
        """
        self._prefix_mode = mode
        self.write(f"SYST:COMM:PFX {mode:d}")
        logger.info(f"Changed prefix mode to {self._prefix_mode=}")


    @property
    def model(self) -> str:
        """Gets the model of the laser."""
        return self._model

    ########## Method Overloads/Aliases ##########


    def set_mode(self, mode):
        """Set the laser mode (e.g., continuous, pulsed)."""
        mode = mode


    def turn_on(self) -> None:
        """Turn on the laser."""
        self.system_state = True

    def turn_off(self) -> None:
        """Turn off the laser."""
        self.system_state = False



    ########## Special Methods ##########

    def __del__(self) -> None:
        self._serial.close()