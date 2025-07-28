from __future__ import annotations
from abc import ABC, abstractmethod
from time import sleep
from typing import TYPE_CHECKING

from pychilaslasers.laser_components.heaters import HeaterChannel
from pychilaslasers.modes.calibrated import __Calibrated
from pychilaslasers.modes.mode import LaserMode

if TYPE_CHECKING:
    from pychilaslasers import Laser
    from utils import CalibrationEntry


class SteadyMode(__Calibrated):

    def __init__(self, laser: Laser, calibration: dict) -> None:
        super().__init__(laser)
        
        self._laser = laser
        self._calibration = calibration["steady"]["calibration"]
        self._default_TEC = calibration["steady"]["tec_temp"]
        self._default_current = calibration["steady"]["current"]

        self._min_wl: float = min(self._calibration.keys())
        self._max_wl: float = max(self._calibration.keys())

        
        self._wl: float = self._min_wl  # Default to minimum wavelength

        antihyst_parameters = calibration["steady"]["anti-hyst"]
        if calibration["model"] == "COMET":
            self._change_method: _WLChangeMethod = _PreLoad(
                steady_mode=self,
                laser=laser,
                calibration_table=self._calibration,
                anti_hyst_parameters=antihyst_parameters
            )
        else:
            # Default to cycler index method for ATLAS
            self._change_method: _WLChangeMethod = _CyclerIndex(
                steady_mode=self,
                laser=laser,
                calibration_table=self._calibration,
                anti_hyst_parameters=antihyst_parameters
            )


    def apply_defaults(self) -> None:
        """Apply default settings for the mode."""
        self._laser.tec.target = self._default_TEC
        self._laser.diode.current = self._default_current



    @property
    def wavelength(self) -> float:
        """Get the current wavelength setting."""
        return self._wl
    def get_wl(self) -> float:
        """Get the current wavelength setting."""
        return self.wavelength
    @wavelength.setter
    def wavelength(self, value: float) -> None:
        """Set the current wavelength setting."""
        if value < self._min_wl or value > self._max_wl:
            raise ValueError(f"Wavelength must be between {self._min_wl} and {self._max_wl}.")

        self._change_method.set_wl(value)

        self._wl = value

        self._laser.trigger_pulse() if self._autoTrig else None


       

    def set_wl_relative(self, value: float) -> None:
        """in nm, relative to the current wavelength

        Args:
            value (float): _description_
        """
        self.wavelength = self.get_wl() + value

    @property
    def antihyst(self) -> bool:
        """Get the antihysteresis setting."""
        return self._change_method.anti_hyst_enabled
    @antihyst.setter
    def antihyst(self, value: bool) -> None:
            self._change_method.anti_hyst_enabled = value
    def toggle_antihyst(self, value: bool | None = None) -> None:
        """Toggle the antihysteresis setting."""
        if value is not None:
            self._change_method.anti_hyst_enabled = value
        else:
            # Toggle the current state
            self._change_method.anti_hyst_enabled = not self._change_method.anti_hyst_enabled


    @property
    def mode(self) -> LaserMode:
        """Get the mode type."""
        return LaserMode.STEADY






class _WLChangeMethod(ABC):
    """Abstract base class for wavelength change methods."""

    def __init__(self,
                steady_mode: SteadyMode,
                laser: Laser,
                calibration_table: dict[float, CalibrationEntry],
                anti_hyst_parameters: tuple[list[float], list[float]]) -> None:

        self._laser: Laser = laser
        self._steady_mode: SteadyMode = steady_mode
        self._calibration_table: dict[float, CalibrationEntry] = calibration_table
        self._antihyst_parameters: tuple[list[float], list[float]] = anti_hyst_parameters
        

        self.anti_hyst_enabled: bool = True  # Default to enabled


    def _antihyst(self) -> None:
        """Apply antihysteresis correction."""
        initial_phase = float(self._calibration_table[self._wavelength].phase_section)

        offset: float = self._antihyst_parameters[0][0]
        v_phase_anti_hyst = initial_phase  # Initialize with the base value
        
        while offset >= 0:
            v_phase_anti_hyst = ((initial_phase ** 2) + offset) ** 0.5  # V^2
            self._laser.query(f"DRV:D {HeaterChannel.PHASE_SECTION.value:d} {v_phase_anti_hyst:.4f}")
            offset -= 2
            sleep(self._antihyst_parameters[1][0])

        self._laser.query(f"DRV:D {HeaterChannel.PHASE_SECTION.value:d} {v_phase_anti_hyst:.4f}")

    @property
    def _wavelength(self) -> float:
        """Get the current wavelength."""
        return self._steady_mode.wavelength

    @abstractmethod
    def set_wl(self, value: float) -> None:
        """
            Assumes that the wavelength getter of steady mode is set to the current wavelength not value.
            throws error if value is not in the calibration table.
            This method should set the wavelength of the laser to the specified value.
        """

        pass


class _PreLoad(_WLChangeMethod):
    """Preload-based wavelength change method.
       Only for COMET model, uses preloaded values for wavelength change.
    """

    def set_wl(self, value: float) -> None:
        """Set the wavelength using a preloaded calibration entry.
       """
       
        if value not in self._calibration_table.keys():
            raise ValueError(f"Wavelength {value} not found in calibration table.")

        entry: CalibrationEntry = self._calibration_table[value]
        # Preload the laser with the calibration entry values
        self._laser.query(f"DRV:DP 0 {entry.phase_section:.4f}")
        self._laser.query(f"DRV:DP 1 {entry.large_ring:.4f}")
        self._laser.query(f"DRV:DP 2 {entry.small_ring:.4f}")
        self._laser.query(f"DRV:DP 3 {entry.coupler:.4f}")

        # apply the heater values
        self._laser.query("DRV:U")

        # Check for mode hop
        if self._calibration_table[self._wavelength].mode_index is not entry.mode_index:
            # apply antihysteresis if enabled
            self._antihyst() if self.anti_hyst_enabled else None



class _CyclerIndex(_WLChangeMethod):
    """Cycler index-based wavelength change method."""

    def set_wl(self, value: float) -> None:
        """Set the wavelength using a cycler index."""
        if value not in self._calibration_table.keys():
            raise ValueError(f"Wavelength {value} not found in calibration table.")

        self._laser.query(f"DRV:CYC:LOAD {self._calibration_table[value].cycler_index}")

        self._antihyst() if self.anti_hyst_enabled else None
