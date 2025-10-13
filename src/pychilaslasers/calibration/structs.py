"""Data structures for laser calibration management.

This module defines the core data structures used for laser calibration:
- CalibrationEntry: Individual wavelength calibration data
- ModeSetting: Base class for laser operation settings
- TuneSettings: Settings for tune mode operation
- SweepSettings: Settings for sweep mode operation
- Calibration: Main container for calibration data with wavelength lookup

Authors: SDU
"""

# ⚛️ Type checking
from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

# ✅ Standard library imports
import logging
from dataclasses import dataclass, field
from typing import overload

# ✅ Local imports
from pychilaslasers.exceptions.calibration_error import CalibrationError


@dataclass
class CalibrationEntry:
    """Represents a single calibration data entry for a specific wavelength.

    This dataclass represents all the calibration parameters for a single
    wavelength setting, including heater values for the laser's optical components
    and metadata about mode hops.

    Attributes:
        wavelength: Target wavelength in nanometers.
        phase_section: Voltage setting for the phase section heater.
        large_ring: Voltage setting for the large ring heater.
        small_ring: Voltage setting for the small ring heater.
        coupler: Voltage setting for the coupler heater.
        mode_index: Mode index for COMET lasers (None for ATLAS).
        mode_hop_flag: True if this entry is part of a mode hop procedure.
        cycler_index: Sequential index in the original calibration file.
        heater_values: Tuple of all heater values (computed automatically).

    Example:
        ```
        entry = CalibrationEntry(
            wavelength=1550.0,
            phase_section=10.5,
            large_ring=20.3,
            small_ring=15.1,
            coupler=25.7,
            mode_index=1,
            mode_hop_flag=False,
            cycler_index=42
        )
        ```
    """

    wavelength: float
    phase_section: float
    large_ring: float
    small_ring: float
    coupler: float
    mode_index: int | None
    mode_hop_flag: bool
    cycler_index: int
    heater_values: tuple[float, float, float, float] = field(init=False)

    def __post_init__(self) -> None:
        """Compute heater_values tuple from individual heater settings.

        This method is automatically called after object initialization to
        create a convenient tuple containing all heater values in order:
        (phase_section, large_ring, small_ring, coupler).
        """
        self.heater_values = (
            self.phase_section,
            self.large_ring,
            self.small_ring,
            self.coupler,
        )

    # def __str__(self) -> str:
    #     return f"{self.cycler_index}: {self.phase_section} {self.large_ring}" +\
    #         f" {self.small_ring} {self.coupler} {self.wavelength}" +\
    #         f" {1 if self.mode_hop_flag else 0}"


@dataclass
class ModeSetting:
    """Base class for laser operation mode settings.

    Contains common parameters shared by all laser operation modes.

    Attributes:
        current: Diode current setting in milliamps.
        tec_temp: TEC temperature target in Celsius.
    """

    current: float
    tec_temp: float


class TuneMethod(Enum):
    """Enumeration for tune method types.

    Specifies the available methods for tuning: from file or cycler.
    """

    FILE = "FILE"
    CYCLER = "CYCLER"


@dataclass
class TuneSettings(ModeSetting):
    """Configuration settings for laser tune mode operation.

    This class extends ModeSetting to include tune-specific parameters
    for laser systems operating in tune mode with anti-hysteresis control.

    Attributes:
        current: Inherited from ModeSetting - Diode current setting in milliamps.
        tec_temp: Inherited from ModeSetting - TEC temperature target in Celsius.
        anti_hyst_voltages: Anti-hysteresis voltage values for tune mode.
        anti_hyst_times: Anti-hysteresis timing values for tune mode.
        method: The wavelength changing method to be used.
    """

    anti_hyst_voltages: list[float]
    anti_hyst_times: list[float]
    method: TuneMethod


@dataclass
class SweepSettings(ModeSetting):
    """Configuration settings for laser sweep mode operation.

    This class extends ModeSetting to include sweep-specific parameters
    for COMET laser systems operating in sweep mode.

    Attributes:
        current: Inherited from ModeSetting - Diode current setting in milliamps.
        tec_temp: Inherited from ModeSetting - TEC temperature target in Celsius.
        interval: Sweep interval for sweep mode in milliseconds.
    """

    interval: int


@dataclass
class Calibration:
    """Comprehensive calibration data container for laser systems.

    This class provides a complete representation of laser calibration data,
    offering convenient access to calibration entries by wavelength with
    automatic closest-match functionality.

    Attributes:
        model: Laser model identifier ("ATLAS" or "COMET").
        entries: Complete list of calibration entries in file order.
        min_wl: Minimum wavelength in the calibration range.
        max_wl: Maximum wavelength in the calibration range.
        precision: The maximum number of decimals an entry can have after the "."
        step_size: Wavelength step size between entries.
        tune_settings: Configuration for tune mode operation.
        sweep_settings: Configuration for sweep mode (None for ATLAS).
    """

    model: str
    _direct_access: dict[float, CalibrationEntry]
    entries: list[CalibrationEntry]
    min_wl: float
    max_wl: float
    precision: int
    step_size: float
    tune_settings: TuneSettings
    sweep_settings: SweepSettings | None

    def __init__(
        self,
        model: str,
        entries: list[CalibrationEntry],  # should be in original order
        tune_settings: TuneSettings,
        sweep_settings: SweepSettings | None,
    ) -> None:
        """Initialize Calibration with laser model and calibration data.

        Args:
            model: Laser model identifier ("ATLAS" or "COMET").
            entries: List of calibration entries in original file order.
                Must not be empty.
            tune_settings: Settings for tune mode operation.
            sweep_settings: Settings for sweep mode operation. Should be
                None for ATLAS lasers, required for COMET lasers.
        """
        self.model = model
        self.entries = entries
        self.tune_settings = tune_settings
        self.sweep_settings = sweep_settings
        if entries == []:
            raise CalibrationError("Empty calibration received!")
        _wavelengths: list[float] = [entry.wavelength for entry in entries]
        self.max_wl = max(_wavelengths)
        self.min_wl = min(_wavelengths)
        self.precision = max(
            len(s.split(".")[1]) if "." in s else 0 for s in map(str, _wavelengths)
        )

        try:
            self.step_size = abs(
                _wavelengths[0] - _wavelengths[_wavelengths.count(_wavelengths[0])]
            )
        except IndexError:
            logging.getLogger(__name__).warning(
                "Calibration loaded with less than 2 entries"
            )

        self._direct_access = {
            entry.wavelength: entry for entry in entries if not entry.mode_hop_flag
        }

    def get_mode_hop_start(self, wavelength: float) -> CalibrationEntry:
        """Get the calibration entry at the start of a mode hop procedure.

        For COMET lasers, mode hops require special handling with multiple
        calibration entries per wavelength. This method returns the first
        entry in a mode hop sequence if one exists for the requested wavelength.

        Args:
            wavelength: Target wavelength in nanometers.

        Returns:
            The first CalibrationEntry in a mode hop procedure if the wavelength
                has mode hop entries, otherwise returns the standard entry via
                `__getitem__`.

        """
        wavelength = self[wavelength].wavelength
        mode_hops: list[CalibrationEntry] = [
            entry
            for entry in self.entries
            if entry.wavelength == wavelength and entry.mode_hop_flag
        ]
        if mode_hops:
            return mode_hops[0]
        else:
            return self[wavelength]

    def __getitem__(self, wavelength: float) -> CalibrationEntry:
        """Get calibration entry for a specific wavelength.

        Supports exact wavelength matches and closest approximation for
        wavelengths within the calibration range. Mode hop entries are
        excluded from closest-match searches.

        Args:
            wavelength: Target wavelength in nanometers.

        Returns:
            CalibrationEntry for the exact wavelength or closest available match.

        Raises:
            KeyError: If wavelength is outside the calibration range.
        """
        if wavelength in self._direct_access:
            return self._direct_access[wavelength]
        elif wavelength in self:
            return self._direct_access[
                min(self._direct_access.keys(), key=lambda x: abs(x - wavelength))
            ]
        else:
            raise KeyError(wavelength)

    def __iter__(self) -> Iterator[CalibrationEntry]:
        """Iterate over all calibration entries in original file order.

        Returns:
            Iterator yielding CalibrationEntry objects.
        """
        return iter(self.entries)

    def __len__(self) -> int:
        """Return the total number of calibration entries.

        Returns:
            Number of entries in the calibration.
        """
        return len(self.entries)

    @overload
    def __contains__(self, wl: CalibrationEntry) -> bool: ...
    @overload
    def __contains__(self, wl: float) -> bool: ...
    def __contains__(self, wl: float | CalibrationEntry) -> bool:
        """Check if a wavelength or entry is within this calibration.

        Supports checking both wavelength ranges and specific entry membership.
        For wavelengths, uses inclusive range checking between min_wl and max_wl.

        Args:
            wl: Either a wavelength in nanometers or a CalibrationEntry object.

        Returns:
            For wavelength: True if within the calibration range [min_wl, max_wl].
            For CalibrationEntry: True if the exact entry exists in this calibration.
        """
        if isinstance(wl, CalibrationEntry):
            return wl in self.entries
        else:
            return self.min_wl <= wl <= self.max_wl
