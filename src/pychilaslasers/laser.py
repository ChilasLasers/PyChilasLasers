"""
This module defines the Laser class for Chilas lasers.

This acts as the main interface for controlling the laser. Some properties and
methods of the laser are accessible at all times, while others are only available
in specific operation modes.

!!! tip "The modes of the laser are:"
    - [ManualMode][pychilaslasers.modes.ManualMode]: Allows manual control of the heater values.
    - [SteadyMode][pychilaslasers.modes.SteadyMode]: Can be used to tune the laser to specific wavelengths according
       to the calibration data.
    - [SweepMode][pychilaslasers.modes.SweepMode]: Sweep mode is used for COMET lasers to enable the sweep
       functionality.

Changing the diode current or TEC temperature of the laser is available in all modes
however this implies that the calibration of the laser is no longer valid and the
laser may not achieve the desired wavelength.

**Authors:** RLK, AVR, SDU
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
from pychilaslasers.exceptions.mode_error import ModeError
from pychilaslasers.utils import read_calibration_file
from pychilaslasers.comm import Communication

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

    def __init__(
        self, com_port: str, calibration_file: str | Path | None = None
    ) -> None:
        """Laser class constructor. Initializes the laser with the given COM port and
        calibration file.

        Opens the serial connection to the laser, initializes the laser components and
        variables, and sets the initial mode to manual.

        Warning:
            During the initialization, **the laser will turn on** and communicate over
            the serial connection to gather necessary information about the laser and
            its components such as maximum values for parameters.

        Args:
            com_port: The COM port to which the laser is connected. This should
                be a string such as "COM7". To see available COM you may use the
                `pychilaslasers.utils.list_comports` method from the `utils` module.
            calibration_file (str | Path): The path to the calibration file that was
                provided for the laser.
        """

        self._comm: Communication = Communication(com_port=com_port)

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

        if calibration_file is not None:
            calibration = read_calibration_file(file_path=calibration_file)
            self._model: str = calibration["model"]
            self._steady_mode: SteadyMode | None = SteadyMode(self, calibration)
            self._sweep_mode: SweepMode | None = (
                SweepMode(self, calibration)
                if calibration["model"] == "COMET"
                else None
            )
        else:
            self._model: str = "Unknown"
            self._steady_mode: SteadyMode | None = None
            self._sweep_mode: SweepMode | None = None
        self._mode: Mode = self._manual_mode

        logger.debug(
            f"Initialized laser {self._model} on {com_port} with calibration file {calibration_file}"
        )

    ########## Main Methods ##########

    def trigger_pulse(self) -> None:
        """Instructs the laser to send a trigger pulse."""
        self._comm.query(f"DRV:CYC:TRIG {int(True):d}")
        self._comm.query(f"DRV:CYC:TRIG {int(False):d}")

    def calibrate(self, calibration_file: str | Path) -> None:
        """Calibrates the laser with the given calibration file.

        Args:
            calibration_file (str | Path): The path to the calibration file to be used for
                calibrating the laser.
        """
        calibration = read_calibration_file(file_path=calibration_file)
        self._model = calibration["model"]
        self._steady_mode = SteadyMode(self, calibration)

        if self._model == "COMET":
            self._sweep_mode = SweepMode(self, calibration)
        params = calibration["steady"]["anti-hyst"]
        self._manual_mode.phase_section.set_hyst_params(params[0], params[1])

    ########## Properties (Getters/Setters) ##########

    @property
    def comm(self) -> Communication:
        """Communication object for the laser.

        This property provides access to the communication object used to interact with
        the laser. It can be used to send commands and queries to the laser.

        Returns:
            The communication object for the laser.
        """
        return self._comm

    @property
    def system_state(self) -> bool:
        """System state of the laser.

        The property of the laser that indicates whether the laser is on or off.
        This is a boolean property that can be set to True to turn on the laser
        or False to turn it off.

        Returns:
            The system state. Whether the laser is on (True) or off (False).
        """
        return bool(int(self._comm.query("SYST:STAT?")))

    @system_state.setter
    def system_state(self, state: bool | int) -> None:
        """Sets the system state.

        Args:
            state: The system state to be set. Can be either bool or 1 or 0 (int)
        """
        if state == 1 or state == 0:
            state = bool(state)
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
    def mode(self, mode: LaserMode | Mode | str) -> None:
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
            ValueError: If the mode is not recognized or is not available for the laser model.
            TypeError: If the mode is not a valid type (not a string, enum, or specific mode instance).
            ModeError: If the sweep mode is not available
        """

        # Check if the mode is an instance of specific mode classes
        previous_mode: LaserMode = self._mode.mode
        if isinstance(mode, Mode):
            mode = mode.mode  # Get the mode from the instance

        # Check if the mode is a string or enum
        if isinstance(mode, str) or isinstance(mode, LaserMode):
            if isinstance(mode, str):
                # Define mode mappings including exact matches and fuzzy matches
                mode_mappings = {
                    "manual": LaserMode.MANUAL,  # Exact match
                    "steady": LaserMode.STEADY,  # Exact match
                    "sweep": LaserMode.SWEEP,  # Exact match
                    "manuel": LaserMode.MANUAL,  # Common misspelling
                    "manua": LaserMode.MANUAL,  # Partial typing
                    "man": LaserMode.MANUAL,  # Short form
                    "steadi": LaserMode.STEADY,  # Partial typing
                    "stead": LaserMode.STEADY,  # Partial typing
                    "ste": LaserMode.STEADY,  # Partial typing
                    "swep": LaserMode.SWEEP,  # Common misspelling
                    "swp": LaserMode.SWEEP,  # Common misspelling
                    "sweap": LaserMode.SWEEP,  # Common misspelling
                    "sweepin": LaserMode.SWEEP,  # Partial typing
                    "sweeping": LaserMode.SWEEP,  # Exact match
                }

                if (mode := mode.lower()) in mode_mappings:
                    mode = mode_mappings[mode]
                else:
                    raise ValueError(
                        f"Unknown mode: {mode}. "
                        "Please use 'manual', 'steady', or 'sweep' "
                    )
            # Check if the mode is a valid mode to enter at this point
            if mode in (LaserMode.STEADY, LaserMode.SWEEP) and not self.calibrated:
                raise ValueError(
                    f"Calibration data not available, laser cannot enter {mode.name.lower()} mode."
                )
            if mode is LaserMode.SWEEP and self._sweep_mode is None:
                raise ModeError(
                    message="Sweep mode is not available for this laser model.",
                    current_mode=self.mode,
                )
            # Change mode to the corresponding mode instance
            self._mode = (
                self._sweep_mode
                if mode is LaserMode.SWEEP
                else self._steady_mode
                if mode is LaserMode.STEADY
                else self._manual_mode
            )  # type: ignore
        else:
            raise TypeError(
                f"Invalid mode type: {type(mode)}. "
                "Please use 'ManualMode', 'SteadyMode', 'SweepMode' instances, "
                "or a string representing the mode (e.g., 'manual', 'steady', 'sweep')."
            )

        # If we were in sweep mode and are switching to another mode, stop the sweep
        if previous_mode is LaserMode.SWEEP and self._mode.mode is not LaserMode.SWEEP:
            self._sweep_mode.stop()

        if previous_mode is not self._mode.mode:
            self._mode.apply_defaults()
        logging.info(f"Laser mode set to {self._mode.mode}")

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
            The steady mode instance with access to wavelength control methods.

        Raises:
            ModeError: If the laser is not in steady mode.

        Example:
            ``` python
            >>> laser.mode = LaserMode.STEADY
            >>> laser.steady.set_wavelength(1550.0)  # Set wavelength to 1550nm
            ```
        """
        if self.mode != LaserMode.STEADY:
            raise ModeError(
                "Laser not in steady mode.",
                current_mode=self.mode,
                desired_mode=LaserMode.STEADY,
            )
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
            The sweep mode instance with access to sweep control methods.

        Raises:
            ModeError: If the laser is not in sweep mode or sweep mode is not available.

        Example:
            ``` python
            >>> laser.mode = LaserMode.SWEEP  # Only works for COMET lasers
            >>> laser.sweep.start_wavelength_sweep(1550.0, 1560.0)  # Sweep from 1550nm to 1560nm
            ```
        """
        if self._sweep_mode is None:
            raise ModeError(
                "Sweep mode is not available for this laser model.",
                self.mode,
                desired_mode=LaserMode.SWEEP,
            )
        if self.mode != LaserMode.SWEEP:
            raise ModeError(
                "Laser not in sweep mode.", self.mode, desired_mode=LaserMode.SWEEP
            )
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
            The manual mode instance with access to manual control methods.

        Raises:
            ModeError: If the laser is not in manual mode.

        Example:
            ``` python
            >>> laser.mode = LaserMode.MANUAL
            >>> laser.manual.set_heater_value(50.0)  # Set heater to 50%
            ```
        """
        if self.mode != LaserMode.MANUAL:
            raise ModeError("Laser not in manual mode.", self.mode, LaserMode.MANUAL)
        return self._manual_mode

    @property
    def model(self) -> str:
        """Return the model of the laser.

        Returns:
            The model of the laser. May be "COMET" or "ATLAS"
        """
        return self._model

    @property
    def calibrated(self) -> bool:
        """Check if the laser is calibrated.

        Returns:
            True if the laser has calibration data, False otherwise.
        """
        return self._steady_mode is not None or self._sweep_mode is not None

    ########## Method Overloads/Aliases ##########

    def set_mode(self, mode: LaserMode | Mode | str) -> None:
        """Sets the mode of the laser.

        This is an alias for the `mode` property setter.
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
