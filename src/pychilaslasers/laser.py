"""
This module defines the Laser class for Chilas lasers. 
<p>
This acts as the main interface for controlling the laser. Some properties and 
methods of the laser are accessible at all times, while others are only available 
in specific operation modes.
<p>
The modes of the laser are:
    1. Manual Mode: Allows manual control of the heater values.
    2. Steady Mode: Can be used to tune the laser to specific wavelengths according 
       to the calibration data.
    3. Sweep Mode: Sweep mode is used for COMET lasers to enable the sweep 
       functionality.
<p>
Changing the diode current or TEC temperature of the laser is available in all modes 
however this implies that the calibration of the laser is no longer valid and the 
laser may not achieve the desired wavelength.
<p>

**Authors:** RLK, AVR, SDU
**Last Revision:** August 4, 2025 - Refactored communications to new Communication class
"""

# ⚛️ Type checking
from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pathlib import Path

# ✅ Standard library imports
import logging

# ✅ Local imports
from pychilaslasers.laser_components.diode import Diode
from pychilaslasers.laser_components.tec import TEC
from pychilaslasers.modes.manual_mode import ManualMode
from pychilaslasers.modes.mode import LaserMode, Mode
from pychilaslasers.modes.steady_mode import SteadyMode
from pychilaslasers.modes.sweep_mode import SweepMode
from pychilaslasers.utils import read_calibration_file
from pychilaslasers.comm import Communication

logger: logging.Logger = logging.getLogger(__name__)


class Laser:
    """Laser class for Chilas lasers. 
    <p> 
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
        <p> 
        The laser can be turned on and off using the `system_state` property. The laser 
        can also be triggered to pulse using the `trigger_pulse()` method. The laser 
        can be set to prefix mode using the `prefix_mode` property. The prefix mode can 
        be used to speed up communication with the laser by reducing the amount of data 
        sent over the serial connection however this reduces the amount of information 
        that is sent back from the laser.
        <p> 
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
        <p>
        Opens the serial connection to the laser, initializes the laser components and 
        variables, and sets the initial mode to manual.

        Warning: 
            During the initialization, **the laser will turn on** and communicate over 
            the serial connection to gather necessary information about the laser and 
            its components such as maximum values for parameters.

        Args:
            com_port: The COM port to which the laser is connected. This should 
                be a string such as "COM7". To see available COM you may use the 
                :meth:`pychilaslasers.utils.list_comports` method from the `utils` module.
            calibration_file (str | Path): The path to the calibration file that was 
                provided for the laser.
        """

        self._comm: Communication = Communication(
            com_port=com_port
        )        

        # Laser identification. Library will not work with non-Chilas lasers.
        if "Chilas" not in (idn := self._comm.query("*IDN?")) and "LioniX" not in idn:
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
        self._comm.query(f"DRV:CYC:TRIG {int(True):d}")
        self._comm.query(f"DRV:CYC:TRIG {int(False):d}")

    ########## Properties (Getters/Setters) ##########


    @property
    def system_state(self) -> bool:
        """System state of the laser.
        <p>
        The property of the laser that indicates whether the laser is on or off.
        This is a boolean property that can be set to True to turn on the laser 
        or False to turn it off.

        Returns:
            The system state. Whether the laser is on (True) or off (False).
        """
        return bool(int(self._comm.query("SYST:STAT?")))

    @system_state.setter
    def system_state(self, state: bool) -> None:
        """Sets the system state.

        Args:
            state: The system state to be set.
        """
        if type(state) is not bool:
            logger.error("ERROR: given state is not a boolean")
            return
        self._comm.query(f"SYST:STAT {state:d}")


    @property
    def mode(self) -> LaserMode:
        """Gets the current mode of the laser.
        
        Returns:
            The current mode of the laser. This can be one of the following:
                - LaserMode.MANUAL
                - LaserMode.STEADY
                - LaserMode.SWEEP
        """
        return self._mode.mode

    @mode.setter
    def mode(self, mode: LaserMode|Mode|str) -> None:
        """Main method for setting the mode of the laser.
        <p>
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
        <p>
        This property allows access to the steady mode instance of the laser in a convenient way
        such as `laser.steady.method()`. Steady mode uses calibration data to tune the laser
        to specific wavelengths with high precision. This mode is available for both COMET and
        ATLAS lasers and provides wavelength control based on the laser's calibration file.

        Warning:
            This method will not change the mode of the laser, it will only return
            the steady mode instance if the laser is in that mode. To switch to steady mode,
            use `laser.mode = LaserMode.STEADY` or `laser.set_mode("steady")` first.
        
        Returns:
            The steady mode instance with access to wavelength control methods.
            
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
        <p> 
        This property allows access to the sweep mode instance of the laser in a convenient way
        such as `laser.sweep.method()`. Sweep mode is only available for COMET lasers and 
        enables sweeping functionality for wavelength scanning applications. This mode uses
        calibration data to perform controlled wavelength sweeps across specified ranges.

        Warning:
            This method will not change the mode of the laser, it will only return
            the sweep mode instance if the laser is in that mode. To switch to sweep mode,
            use `laser.mode = LaserMode.SWEEP` or `laser.set_mode("sweep")` first.
        
        Returns:
            The sweep mode instance with access to sweep control methods.
            
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
        <p>        
        This property allows access to the manual mode instance of the laser in a convenient way
        such as `laser.manual.method()`. Manual mode is always available and is the default mode.
        In manual mode, you have direct control over individual laser components and can manually
        set heater values and other parameters.

        Warning:
            This method will not change the mode of the laser, it will only return
            the manual mode instance if the laser is in that mode. To switch to manual mode,
            use `laser.mode = LaserMode.MANUAL` or `laser.set_mode("manual")` first.
        
        Returns:
            The manual mode instance with access to manual control methods.
            
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
    def model(self) -> str:
        """Return the model of the laser.
        
        Returns:
            The model of the laser. May be "COMET" or "ATLAS"
        """
        return self._model

    ########## Method Overloads/Aliases ##########


    def set_mode(self, mode: LaserMode | Mode | str) -> None:
        """Sets the mode of the laser. 
        <p>
        This is an alias for the :meth:`mode` property setter.
        """
        self.mode = mode


    def turn_on(self) -> None:
        """Turn on the laser.
        <p>
        This is an alias for setting the system state to True.
        """
        self.system_state = True

    def turn_off(self) -> None:
        """Turn off the laser.
        <p>
        This is an alias for setting the system state to False.
        """
        self.system_state = False
