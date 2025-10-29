"""Tune mode operation for laser wavelength control.

This module implements tune mode operation of the laser which allows for tuning to
wavelengths from the calibration table.

**Authors**: RLK, AVR, SDU
"""

# ⚛️ Type checking
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pychilaslasers.laser import Laser
    from pychilaslasers.calibration import Calibration, CalibrationEntry

# ✅ Standard library imports

# ✅ Local imports
from pychilaslasers.exceptions.calibration_error import CalibrationError
from pychilaslasers.calibration.structs import TuneMethod
from pychilaslasers.modes.calibrated import __Calibrated
from pychilaslasers.modes.mode import LaserMode


class TuneMode(__Calibrated):
    """Tune operation mode of the laser.

    TuneMode allows for tuning to specific wavelengths

    The mode supports anti-hysteresis correction to improve wavelength stability
    and provides convenient methods for wavelength setting and control.

    Args:
        laser: The laser instance to control.
        calibration: Calibration object

    Attributes:
        wavelength: Current wavelength setting in nanometers.
        antihyst: Anti-hysteresis correction enable/disable state.
        mode: Returns LaserMode.TUNE.

    """

    _antihyst: Callable[..., None]

    def __init__(self, laser: Laser, calibration: Calibration) -> None:
        """Initialize tune mode with laser and calibration data.

        Args:
            laser: The laser instance to control.
            calibration: Calibration data object containing tune mode parameters.

        """
        super().__init__(laser, calibration=calibration)

        self._calibration: Calibration = calibration
        self._default_TEC = calibration.tune_settings.tec_temp
        self._default_current = calibration.tune_settings.current

        self.anti_hyst_enabled: bool = True  # Default to enabled

        self._wl: float = self._min_wl  # Default to minimum wavelength

        self._antihyst = laser._manual_mode.phase_section._anti_hyst

        self._change_method: Callable[[float], float]

        # Initialize wavelength change method
        if (method := calibration.tune_settings.method) is TuneMethod.FILE:
            self._change_method = self._pre_load_from_file
        elif method is TuneMethod.CYCLER:
            # Default to cycler index method for ATLAS
            self._change_method = self._cycler_index
        else:
            raise CalibrationError("Invalid tune Method")

    ########## Main Methods ##########

    def apply_defaults(self) -> None:
        """Apply default settings for tune mode operation.

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
        if wavelength not in self._calibration:
            raise ValueError(
                f"Wavelength value {wavelength} not valid: must be between "
                f"{self._min_wl} and {self._max_wl}."
            )

        self._wl = self._change_method(wavelength)

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
        return self.anti_hyst_enabled

    @antihyst.setter
    def antihyst(self, state: bool) -> None:
        """Set the anti-hysteresis correction state.

        Args:
            state: Enable (True) or disable (False) anti-hysteresis correction.

        """
        self.anti_hyst_enabled = state

    @property
    def mode(self) -> LaserMode:
        """Get the laser operation mode.

        Returns:
            LaserMode.TUNE indicating tune mode operation.

        """
        return LaserMode.TUNE

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
            self.anti_hyst_enabled = not self.anti_hyst_enabled
        else:
            self.anti_hyst_enabled = state

    ########## Private Classes ##########

    def _pre_load_from_file(self, wavelength: float) -> float:
        """Set wavelength by preloading the values from the file then updating.

        Loads heater values from calibration table and applies them to the laser.
        On COMET lasers, anti-hysteresis correction is applied only when a mode hop
        is detected.

        Warning:
            This method assumes self._wavelength is NOT already set to the requested
            wavelength. This is important for mode checking and anti-hysteresis
            application.

        Args:
            wavelength: Target wavelength in nanometers.

        Returns:
            The actual wavelength that was set.
        """
        try:
            entry: CalibrationEntry = self._calibration[wavelength]
        except KeyError as e:
            raise ValueError(
                f"Wavelength {wavelength} not found in calibration table."
            ) from e

        # Preload the laser with the calibration entry values
        self._comm.query(f"DRV:DP 0 {entry.phase_section:.4f}")
        self._comm.query(f"DRV:DP 1 {entry.large_ring:.4f}")
        self._comm.query(f"DRV:DP 2 {entry.small_ring:.4f}")
        self._comm.query(f"DRV:DP 3 {entry.coupler:.4f}")

        # Apply the heater values
        self._comm.query("DRV:U")

        # Check for mode hop and apply anti-hysteresis if needed
        if (
            # this applies to the Comet
            self._calibration[self._wl].mode_index != entry.mode_index
            or self._calibration.model == "ATLAS"
        ):
            if self.anti_hyst_enabled:
                self._antihyst()

        return entry.wavelength

    def _cycler_index(self, wavelength: float) -> float:
        """Set wavelength using the laser's cycler index.

        Args:
            wavelength: Target wavelength in nanometers.

        Raises:
            ValueError: If wavelength is outside the calibration range

        Returns:
            The actual wavelength that was set.

        Warning:
            This method assumes self._wavelength is NOT already set to the current
            wavelength. This is important for mode checking and anti-hysteresis
            application.

        """
        try:
            entry: CalibrationEntry = self._calibration[wavelength]
        except KeyError as e:
            raise ValueError(
                f"Wavelength {wavelength} not found in calibration table."
            ) from e

        self._comm.query(f"DRV:CYC:LOAD {entry.cycler_index}")

        if self.anti_hyst_enabled:
            self._antihyst()

        return entry.wavelength
