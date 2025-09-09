"""
Steady mode operation for laser wavelength control.

This module implements steady mode operation of the laser which allows for tuning to
wavelengths from the calibration table.

**Authors**: RLK, AVR, SDU
"""

# ⚛️ Type checking
from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pychilaslasers.laser import Laser
    from pychilaslasers.comm import Communication
    from pychilaslasers.utils import CalibrationEntry

# ✅ Standard library imports
import logging
from math import sqrt
from abc import ABC, abstractmethod
from time import sleep

# ✅ Local imports
from pychilaslasers.laser_components.heaters.heater_channels import HeaterChannel
from pychilaslasers.modes.calibrated import __Calibrated
from pychilaslasers.modes.mode import LaserMode


class SteadyMode(__Calibrated):
    """Steady operation mode of the laser.

    SteadyMode allows for tuning to specific wavelengths

    The mode supports anti-hysteresis correction to improve wavelength stability
    and provides convenient methods for wavelength setting and control.

    Args:
        laser: The laser instance to control.
        calibration: Calibration data dictionary containing steady mode parameters.
                as returned by the `utils.read_calibration_file` method

    Attributes:
        wavelength: Current wavelength setting in nanometers.
        antihyst: Anti-hysteresis correction enable/disable state.
        mode: Returns LaserMode.STEADY.
    """

    def __init__(self, laser: Laser, calibration: dict) -> None:
        """Initialize steady mode with laser and calibration data.

        Args:
            laser: The laser instance to control.
            calibration: Calibration data dictionary containing steady mode parameters.
        """
        super().__init__(laser)

        self._calibration = calibration["steady"]["calibration"]
        self._default_TEC = calibration["steady"]["tec_temp"]
        self._default_current = calibration["steady"]["current"]

        self._min_wl: float = min(self._calibration.keys())
        self._max_wl: float = max(self._calibration.keys())
        _wavelengths: list[float] = sorted(list(self._calibration.keys()))
        self._step_size: float = abs(
            _wavelengths[0] - _wavelengths[_wavelengths.count(_wavelengths[0])]
        )

        self._wl: float = self._min_wl  # Default to minimum wavelength

        # Initialize wavelength change method based on laser model
        antihyst_parameters = calibration["steady"]["anti-hyst"]
        if calibration["model"] == "COMET":
            self._change_method: _WLChangeMethod = _PreLoad(
                steady_mode=self,
                laser=laser,
                calibration_table=self._calibration,
                anti_hyst_parameters=antihyst_parameters,
            )
        else:
            # Default to cycler index method for ATLAS
            self._change_method: _WLChangeMethod = _CyclerIndex(
                steady_mode=self,
                laser=laser,
                calibration_table=self._calibration,
                anti_hyst_parameters=antihyst_parameters,
            )

    ########## Main Methods ##########

    def apply_defaults(self) -> None:
        """Apply default settings for steady mode operation.

        Sets the TEC temperature and diode current to their default values
        as specified in the calibration data.
        """
        self._laser.tec.target = self._default_TEC
        self._laser.diode.current = self._default_current

    ########## Properties (Getters/Setters) ##########

    @property
    def wavelength(self) -> float:
        """Get the current wavelength setting.

        Returns:
            Current wavelength in nanometers.
        """
        return self._wl

    @wavelength.setter
    def wavelength(self, wavelength: float) -> float:
        """Set the laser wavelength.

        Args:
            wavelength: Target wavelength in nanometers.
                If the wavelength is not in the calibration table, it will find the
                closest available wavelength and use that instead.

        Returns:
            The actual wavelength that was set.

        Raises:
            ValueError: If wavelength is outside the valid calibration range.
        """
        if wavelength < self._min_wl or wavelength > self._max_wl:
            raise ValueError(
                f"Wavelength value {wavelength} not valid: must be between {self._min_wl} and {self._max_wl}."
            )
        if wavelength not in self._calibration.keys():
            # Find the closest available wavelength to the requested wavelength
            wavelength = min(
                self._calibration.keys(), key=lambda x: abs(x - wavelength)
            )

        self._change_method.set_wl(wavelength)
        self._wl = wavelength

        # Trigger pulse if auto-trigger is enabled (inherited from parent)
        if self._autoTrig:
            self._laser.trigger_pulse()

        return self._wl

    @property
    def antihyst(self) -> bool:
        """Get the anti-hysteresis correction state.

        Returns:
            True if anti-hysteresis correction is enabled, False otherwise.
        """
        return self._change_method.anti_hyst_enabled

    @antihyst.setter
    def antihyst(self, state: bool) -> None:
        """Set the anti-hysteresis correction state.

        Args:
            state: Enable (True) or disable (False) anti-hysteresis correction.
        """
        self._change_method.anti_hyst_enabled = state

    @property
    def mode(self) -> LaserMode:
        """Get the laser operation mode.

        Returns:
            LaserMode.STEADY indicating steady mode operation.
        """
        return LaserMode.STEADY

    @property
    def step_size(self) -> float:
        """Get the step size between consecutive wavelengths.

        Returns:
            The step size in nanometers between consecutive wavelengths.
        """
        return self._step_size

    ########## Method Overloads/Aliases ##########

    def get_wl(self) -> float:
        """Get the current wavelength setting.

        Alias for the wavelength property getter.

        Returns:
            Current wavelength in nanometers.
        """
        return self.wavelength

    def set_wl_relative(self, delta: float) -> float:
        """Set wavelength relative to current position.

        Args:
            delta: Wavelength change in nanometers, relative to current wavelength.
                Positive deltas increase wavelength, negative deltas decrease it.

        Returns:
            The new absolute wavelength that was set.

        Raises:
            ValueError: If the resulting wavelength is outside the valid range.
        """
        self.wavelength = self.get_wl() + delta

        return self.wavelength

    def toggle_antihyst(self, state: bool | None = None) -> None:
        """Toggle the anti-hysteresis correction state.

        Args:
            state: Optional explicit state to set. If None, toggles current state.
                True enables anti-hysteresis, False disables it.
        """
        if state is None:
            # Toggle the current state
            self._change_method.anti_hyst_enabled = (
                not self._change_method.anti_hyst_enabled
            )
        else:
            self._change_method.anti_hyst_enabled = state


########## Private Classes ##########


class _WLChangeMethod(ABC):
    """Abstract base class for wavelength change methods.

    Defines the interface for different wavelength change strategies used by
    different laser models. Each implementation handles the specific hardware
    commands and anti-hysteresis procedures for its respective laser type.

    Args:
        steady_mode: Reference to the parent SteadyMode instance.
        laser: The laser hardware interface.
        calibration_table: Wavelength to calibration entry mapping.
        anti_hyst_parameters: Tuple of (voltage_list, time_steps_list) for anti-hysteresis.

    Attributes:
        anti_hyst_enabled: Enable/disable anti-hysteresis correction.
    """

    def __init__(
        self,
        steady_mode: SteadyMode,
        laser: Laser,
        calibration_table: dict[float, CalibrationEntry],
        anti_hyst_parameters: tuple[list[float], list[float]],
    ) -> None:
        """Initialize wavelength change method.

        Args:
            steady_mode: Reference to the parent SteadyMode instance.
            laser: The laser hardware interface.
            calibration_table: Wavelength to calibration entry mapping.
                This is not the same as the calibration dictionary returned by
                `utils.read_calibration_file`, just the calibration data
            anti_hyst_parameters: Tuple containing voltage steps and timing
                for anti-hysteresis correction.
        """

        self._laser: Laser = laser
        self._comm: Communication = laser._comm
        self._steady_mode: SteadyMode = steady_mode
        self._calibration_table: dict[float, CalibrationEntry] = calibration_table
        antihyst_parameters: tuple[list[float], list[float]] = anti_hyst_parameters

        self._v_phases_squared_antihyst = antihyst_parameters[0]
        self._time_steps = antihyst_parameters[1]

        assert len(self._v_phases_squared_antihyst) != 0 and len(self._time_steps) != 0
        assert (
            len(self._v_phases_squared_antihyst) == len(self._time_steps) + 1
            or len(self._time_steps) == 1
        )
        self._time_steps: list[float] = (
            [self._time_steps[0]] * (len(self._v_phases_squared_antihyst) - 1) + [0]
            if len(self._time_steps) == 1
            else self._time_steps + [0]
        )

        self._phase_max: float = self._laser._manual_mode.phase_section.max_value
        self._phase_min: float = self._laser._manual_mode.phase_section.min_value

        self.anti_hyst_enabled: bool = True  # Default to enabled

    ########## Private Methods ##########

    def _antihyst(self, v_phase: float = None) -> None:
        """Apply anti-hysteresis correction to the laser.

        Applies a voltage ramping procedure to the phase section heater to
        minimize hysteresis effects during wavelength changes. The specifics of
        this method are laser-dependent and are specified as part of the calibration data.
        """

        if v_phase is None:
            v_phase = self._comm.query(f"DRV:D? {HeaterChannel.PHASE_SECTION.value:d}")
        v_phases_squared_antihyst = self._v_phases_squared_antihyst.copy()
        time_steps = self._time_steps.copy()

        for i, v_phase_squared_antihyst in enumerate(v_phases_squared_antihyst):
            if v_phase**2 + v_phase_squared_antihyst < 0:
                value = 0
                logging.getLogger(__name__).warning(
                    "Anti-hysteresis "
                    f"value out of bounds: {value} (min: {self._phase_min}, max: "
                    f"{self._phase_max}). Approximating by 0"
                )
                value: float = 0
            else:
                value = sqrt(v_phase**2 + v_phase_squared_antihyst)
            if value < self._phase_min or value > self._phase_max:
                logging.getLogger(__name__).error(
                    "Anti-hysteresis"
                    f"value out of bounds: {value} (min: {self._phase_min}, max: "
                    f"{self._phase_max}). Approximating with the closest limit."
                )
                value = min(value, self._phase_max)
                value = max(value, self._phase_min)
            self._comm.query(f"DRV:D {HeaterChannel.PHASE_SECTION.value:d} {value:.4f}")
            sleep(time_steps[i] / 1000)

    ########## Properties (Getters/Setters) ##########

    @property
    def _wavelength(self) -> float:
        """
        Returns:
            Current wavelength setting in nanometers.
        """
        return self._steady_mode.wavelength

    ########## Abstract Methods ##########

    @abstractmethod
    def set_wl(self, wavelength: float) -> None:
        """Set the laser wavelength using the specific method implementation.

        This method must be implemented by subclasses to handle the wavelength
        change procedure specific to each laser model.

        Args:
            wavelength: Target wavelength in nanometers.

        Raises:
            ValueError: If wavelength is not found in calibration table.

        Warning:
            This method assumes self._wavelength is NOT already set to the current wavelength.
            This is important for mode checking and anti-hysteresis application.
            This method assumes that the wavelength is in the calibration data provided
            and does not choose the closest wavelength.
        """
        pass


class _PreLoad(_WLChangeMethod):
    """Preload-based wavelength change method for COMET model.

    Note:
        This method is specifically designed for COMET laser models.
    """

    def set_wl(self, wavelength: float) -> None:
        """Set wavelength using preloaded calibration wavelengths.

        Loads heater values from calibration table and applies them to the laser.
        Anti-hysteresis correction is applied only when a mode hop is detected.

        Warning:
            This method assumes self._wavelength is NOT already set to the requested
            wavelength. This is important for mode checking and anti-hysteresis application.

        Args:
            wavelength: Target wavelength in nanometers.

        Raises:
            ValueError: If wavelength is not found in calibration table.
        """
        if wavelength not in self._calibration_table.keys():
            raise ValueError(f"Wavelength {wavelength} not found in calibration table.")

        entry: CalibrationEntry = self._calibration_table[wavelength]

        # Preload the laser with the calibration entry values
        self._comm.query(f"DRV:DP 0 {entry.phase_section:.4f}")
        self._comm.query(f"DRV:DP 1 {entry.large_ring:.4f}")
        self._comm.query(f"DRV:DP 2 {entry.small_ring:.4f}")
        self._comm.query(f"DRV:DP 3 {entry.coupler:.4f}")

        # Apply the heater values
        self._comm.query("DRV:U")

        # Check for mode hop and apply anti-hysteresis if needed
        if self._calibration_table[self._wavelength].mode_index != entry.mode_index:
            if self.anti_hyst_enabled:
                self._antihyst(entry.phase_section)

    @property
    def step_size(self) -> float:
        """Get the step size between consecutive wavelengths in the sweep range.

        Returns:
            The step size in nanometers between consecutive wavelengths
                in the sweep range.

        """
        return self._step_size


class _CyclerIndex(_WLChangeMethod):
    """Cycler index-based wavelength change method for ATLAS model.

    Uses the laser's internal cycler functionality to change wavelengths.
    This method always applies anti-hysteresis correction when enabled.

    Note:
        This method is the default for ATLAS laser models.
    """

    def set_wl(self, wavelength: float) -> None:
        """Set wavelength using the laser's cycler index.

        Args:
            wavelength: Target wavelength in nanometers.

        Raises:
            ValueError: If wavelength is not found in calibration table.

        Warning:
            This method assumes self._wavelength is NOT already set to the current
            wavelength. This is important for mode checking and anti-hysteresis application.
        """
        if wavelength not in self._calibration_table.keys():
            raise ValueError(f"Wavelength {wavelength} not found in calibration table.")

        self._comm.query(
            f"DRV:CYC:LOAD {self._calibration_table[wavelength].cycler_index}"
        )

        if self.anti_hyst_enabled:
            self._antihyst()
