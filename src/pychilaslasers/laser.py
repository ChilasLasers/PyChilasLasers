"""
This module defines the Laser class for Chilas lasers. 

This acts as the main interface for controlling the laser. Some properties and 
methods of the laser are accessible at all times, while others are only available 
in specific operation modes.

The modes of the laser are:
    1. Manual Mode: Allows manual control of the heater values.
    2. Steady Mode: Can be used to tune the laser to specific wavelengths according 
       to the calibration data.
    3. Sweep Mode: Sweep mode is used for COMET lasers to enable the sweep 
       functionality.

Changing the diode current or TEC temperature of the laser is available in all modes 
however this implies that the calibration of the laser is no longer valid and the 
laser may not achieve the desired wavelength.

Authors: RLK, AVR, SDU
Last Revision: July 30, 2025 - Enhanced documentation and improved code formatting
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
    """Laser class for Chilas lasers. 
    
    Contains the main methods for communication with the laser, the logic for changing 
    and accessing the laser modes, and the properties of the laser. Multiple overloaded 
    methods are available to interact with the laser. Many of the methods are overloads 
    of other methods that either provide different ways do the same operation for 
    convenience.

    Usage:
        Accessing functionality of a specific mode is done through the `mode` property 
        such as `laser.steady.method_name()` or `laser.sweep.method_name()`. This will 
        however only work if the laser is in the correct mode. If the laser is not in 
        the correct mode, an exception will be raised. The current mode of the laser 
        can be set using the `mode` property as well.
        
        The laser can be turned on and off using the `system_state` property. The laser 
        can also be triggered to pulse using the `trigger_pulse()` method. The laser 
        can be set to prefix mode using the `prefix_mode` property. The prefix mode can 
        be used to speed up communication with the laser by reducing the amount of data 
        sent over the serial connection however this reduces the amount of information 
        that is sent back from the laser.
        
        Some laser components such as the TEC and Diode can be accessed in all modes 
        using the `tec` and `diode` properties respectively. Other components are only 
        available in manual mode.

    Attributes:
        tec (TEC): The TEC component of the laser.
        diode (Diode): The Diode component of the laser.
        mode (Mode): The current mode of the laser.
        system_state (bool): The system state of the laser (on/off).
        prefix_mode (bool): Whether the laser is in prefix mode or not.
    """


    def __init__(self, com_port: str, calibration_file: str | Path) -> None:
        """Laser class constructor. Initializes the laser with the given COM port and 
        calibration file.

        Opens the serial connection to the laser, initializes the laser components and 
        variables, and sets the initial mode to manual.

        Warning: 
            During the initialization, **the laser will turn on** and communicate over 
            the serial connection to gather necessary information about the laser and 
            its components such as maximum values for parameters.

        Args:
            com_port (str): The COM port to which the laser is connected. This should 
                be a string such as "COM7". To see available COM you may use the 
                :meth:`pychilaslasers.utils.list_comports` method from the `utils` module.
            calibration_file (str | Path): The path to the calibration file that was 
                provided for the laser.
        """

        # Variable initialization
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
        
        # Laser identification. Library will not work with non-Chilas lasers.
        if "Chilas" not in self.query("*IDN?"):
            logger.critical("Laser is not a Chilas device")
            import sys
            sys.exit(1)

        # Initialize laser components
        self.tec: TEC = TEC(self)
        self.diode: Diode = Diode(self)

        # Initialize modes 
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
        """Instructs the laser to send a trigger pulse."""
        self.query(f"DRV:CYC:TRIG {int(True):d}")
        self.query(f"DRV:CYC:TRIG {int(False):d}")


    def query(self, data: str) -> str:
        """Main method for communication with the laser.
        
        This method sends a command to the laser over the serial connection and returns 
        the response. It also handles the logging of the command and response. The 
        response code of the reply is checked and an error is raised if the response 
        code is not 0. Commands that are sent multiple times may be replaced with a 
        semicolon to speed up communication.
        
        Args:
            data (str): The serial command to be sent to the laser.
            
        Returns:
            str: The response from the laser. The response is stripped of any leading 
                or trailing whitespace as well as the return code. Response may be 
                empty if the command does not return a value.
                
        Raises:
            ValueError: If the command is not a string.
            serial.SerialException: If there is an error with the serial connection.
            NotImplementedError: For most errors TODO
        """

        # Write the command to the serial port
        logger.debug(msg=f"W {data}")  # Logs the command being sent
        self._serial.write(
            f"{self._semicolon_replace(data)}\r\n"
            .encode("ascii")
            )

        # Read the response from the laser
        reply: str = self._serial.readline().decode("ascii").rstrip()

        # Error handling
        if not reply and not self._prefix_mode:
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
        
        Check if the command was previously sent to the device. In that case, replace 
        it with a semicolon.

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
        """System state of the laser.

        The property of the laser that indicates whether the laser is on or off.
        This is a boolean property that can be set to True to turn on the laser 
        or False to turn it off.

        Returns:
            bool: The system state. Whether the laser is on (True) or off (False).
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
        """Gets the current mode of the laser.
        
        Returns:
            LaserMode: The current mode of the laser. This can be one of the following:
                - LaserMode.MANUAL
                - LaserMode.STEADY
                - LaserMode.SWEEP
        """
        return self._mode.mode

    @mode.setter
    def mode(self, mode: LaserMode|Mode|str) -> None:
        """Main method for setting the mode of the laser.
        
        This method is used for changing the current mode of the laser. The mode 
        can be set to one of the following:
            - ManualMode
            - SteadyMode
            - SweepMode (only available for COMET lasers)
        When changing the mode the default values for the mode are applied.

        Args:
            mode (LaserMode | Mode | str): The mode to set the laser to. This can be:
                - An instance of a specific mode class (ManualMode, SteadyMode, 
                  SweepMode). The mode will NOT be changed to that specific mode 
                  class, but rather the mode will be set to the mode of that class.
                - A string representing the mode (e.g., "manual", "steady", "sweep")
                  Case-insensitive and allows for common misspellings or partial typing.
                - An enum value from LaserMode (e.g., LaserMode.MANUAL, 
                  LaserMode.STEADY, LaserMode.SWEEP)
                  
        Raises:
            NotImplementedError: If the mode is not initialized or not available.TODO
            ValueError: If the mode is not recognized or not a valid type.
        """

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
        


    @property
    def steady(self) -> SteadyMode:
        """Getter function for the steady mode instance.
        
        This property allows access to the steady mode instance of the laser in a convenient way
        such as `laser.steady.method()`. Steady mode uses calibration data to tune the laser
        to specific wavelengths with high precision. This mode is available for both COMET and
        ATLAS lasers and provides wavelength control based on the laser's calibration file.

        Warning:
            This method will not change the mode of the laser, it will only return
            the steady mode instance if the laser is in that mode. To switch to steady mode,
            use `laser.mode = LaserMode.STEADY` or `laser.set_mode("steady")` first.
        
        Returns:
            SteadyMode: The steady mode instance with access to wavelength control methods.
            
        Raises:
            NotImplementedError: If the laser is not in steady mode. TODO
            
        Example:
            >>> laser.mode = LaserMode.STEADY
            >>> laser.steady.set_wavelength(1550.0)  # Set wavelength to 1550nm
        """
        if self._steady_mode is None:
            raise NotImplementedError("Proper exception to be raised here")
            raise NotCalibratedError("Steady mode is not initialized.")
        if self.mode != LaserMode.STEADY:
            raise NotImplementedError("Proper exception to be raised here")
            raise IncorrectModeError("Laser not in steady mode.")
        return self._steady_mode
    
    @property
    def sweep(self) -> SweepMode:
        """Getter function for the sweep mode instance.
        
        This property allows access to the sweep mode instance of the laser in a convenient way
        such as `laser.sweep.method()`. Sweep mode is only available for COMET lasers and 
        enables sweeping functionality for wavelength scanning applications. This mode uses
        calibration data to perform controlled wavelength sweeps across specified ranges.

        Warning:
            This method will not change the mode of the laser, it will only return
            the sweep mode instance if the laser is in that mode. To switch to sweep mode,
            use `laser.mode = LaserMode.SWEEP` or `laser.set_mode("sweep")` first.
        
        Returns:
            SweepMode: The sweep mode instance with access to sweep control methods.
            
        Raises:
            NotImplementedError: If the laser is not in sweep mode or sweep mode is not available. TODO
            
        Example:
            >>> laser.mode = LaserMode.SWEEP  # Only works for COMET lasers
            >>> laser.sweep.start_wavelength_sweep(1550.0, 1560.0)  # Sweep from 1550nm to 1560nm
        """
        if self._sweep_mode is None:
            raise NotImplementedError("Proper exception to be raised here")
            raise NotCalibratedError("Sweep mode is not initialized.")
        if self.mode != LaserMode.SWEEP:
            raise NotImplementedError("Proper exception to be raised here")
            raise IncorrectModeError("Laser not in sweep mode.")
        return self._sweep_mode
    
    @property
    def manual(self) -> ManualMode:
        """Getter function for the manual mode instance.
        
        This property allows access to the manual mode instance of the laser in a convenient way
        such as `laser.manual.method()`. Manual mode is always available and is the default mode.
        In manual mode, you have direct control over individual laser components and can manually
        set heater values and other parameters.

        Warning:
            This method will not change the mode of the laser, it will only return
            the manual mode instance if the laser is in that mode. To switch to manual mode,
            use `laser.mode = LaserMode.MANUAL` or `laser.set_mode("manual")` first.
        
        Returns:
            ManualMode: The manual mode instance with access to manual control methods.
            
        Raises:
            NotImplementedError: If the laser is not in manual mode. TODO
            
        Example:
            >>> laser.mode = LaserMode.MANUAL
            >>> laser.manual.set_heater_value(50.0)  # Set heater to 50%
        """
        if self.mode != LaserMode.MANUAL:
            raise NotImplementedError("Proper exception to be raised here")
            raise IncorrectModeError("Laser not in manual mode.")
        return self._manual_mode

    @property
    def prefix_mode(self) -> bool:
        """Gets prefix mode for the laser driver.

        The laser driver can be operated in two different communication modes:
            1. Prefix mode on
            2. Prefix mode off

        When prefix mode is on, every message over the serial connection will be
        replied to by the driver with a response, and every response will be 
        prefixed with a return code (rc), either `0` or `1` for an OK or ERROR 
        respectively.

        With prefix mode is off, responses from the laser driver are not prefixed
        with a return code. This means that in the case for a serial write command
        without an expected return value, the driver will not send back a reply.

        Returns:
            bool: whether prefix mode is enabled (True) or disabled (False)
        """
        return bool(int(self.query("SYST:COMM:PFX?")))

    @prefix_mode.setter
    def prefix_mode(self, mode: bool) -> None:
        """Sets prefix mode for the laser driver.

        The laser driver can be operated in two different communication modes:
            1. Prefix mode on
            2. Prefix mode off

        When prefix mode is on, every message over the serial connection will be
        replied to by the driver with a response, and every response will be 
        prefixed with a return code (rc), either `0` or `1` for an OK or ERROR 
        respectively.

        With prefix mode is off, responses from the laser driver are not prefixed
        with a return code. This means that in the case for a serial write command
        without an expected return value, the driver will not send back a reply.

        Args:
            mode (bool): whether to enable prefix mode (True) or disable it (False)
        """
        self.query(f"SYST:COMM:PFX {mode:d}")
        logger.info(f"Changed prefix mode to {mode}")

    @property
    def model(self) -> str:
        """Return the model of the laser.
        
        Returns:
            str: The model of the laser. May be "COMET" or "ATLAS"
        """
        return self._model

    ########## Method Overloads/Aliases ##########


    def set_mode(self, mode: LaserMode | Mode | str) -> None:
        """Sets the mode of the laser. 
        
        This is an alias for the :meth:`mode` property setter.
        """
        self.mode = mode


    def turn_on(self) -> None:
        """Turn on the laser.
        
        This is an alias for setting the system state to True.
        """
        self.system_state = True

    def turn_off(self) -> None:
        """Turn off the laser.
        
        This is an alias for setting the system state to False.
        """
        self.system_state = False



    ########## Special Methods ##########

    def __del__(self) -> None:
        self._serial.close()