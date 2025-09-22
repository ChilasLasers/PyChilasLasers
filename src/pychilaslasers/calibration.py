"""Calibration data management for Chilas laser systems.

This module provides comprehensive functionality for loading, parsing, and managing
calibration data for Chilas laser systems. It supports both ATLAS and COMET laser
models with their respective calibration file formats.

The module provides:
    - A method for loading the provided calibration files
    - Data structures for containing the information in the calibration files
    - Functions for ease of use of the datastructures



File Format:
    ```
    [default_settings]
    laser_model = COMET
    tune_diode_current = 280.0
    tune_tec_target = 25.0
    ...
    [look_up_table]
    10.0;20.0;30.0;40.0;1555.0;0
    11.0;21.0;31.0;41.0;1554.0;1
    ...
    ```
Authors: SDU
"""

from csv import reader
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import TextIO, overload
from collections.abc import Iterator

from pychilaslasers.exceptions.calibration_error import CalibrationError


class Defaults:
    """Default configuration values for laser calibration.

    This class contains hard-coded default values for various laser
    parameters used in calibration modes.

    Attributes:
        HARD_CODED_LASER_MODEL : str
            Default laser model name.
        HARD_CODED_STEADY_CURRENT : float
            Default current value for steady mode.
        HARD_CODED_STEADY_TEC_TEMP : float
            Default TEC temperature for steady mode.
        HARD_CODED_STEADY_ANTI_HYST : tuple
            Default anti-hysteresis values for steady mode.
        HARD_CODED_SWEEP_CURRENT : float
            Default current value for sweep mode.
        HARD_CODED_SWEEP_TEC_TEMP : float
            Default TEC temperature for sweep mode.
        HARD_CODED_INTERVAL : int
            Default interval value for sweep mode.
    """

    HARD_CODED_LASER_MODEL: str = "ATLAS"

    # Steady mode default values
    HARD_CODED_STEADY_CURRENT: float = 280.0
    HARD_CODED_STEADY_TEC_TEMP: float = 25.0
    HARD_CODED_STEADY_ANTI_HYST: tuple = ([35.0, 0.0], [10.0])

    # Sweep mode default values (for COMET model)
    HARD_CODED_SWEEP_CURRENT: float = 280.0
    HARD_CODED_SWEEP_TEC_TEMP: float = 25.0
    HARD_CODED_INTERVAL: int = 100


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
    """Configuration settings for a specific laser operation mode.

    This dataclass stores the calibrated parameters needed to operate a laser
    in either tune mode or sweep mode.

    Attributes:
        current: Diode current setting in milliamps.
        tec_temp: TEC (Thermoelectric Cooler) temperature target in Celsius.
        anti_hyst_voltages: Anti-hysteresis voltage values for tune mode
            (None for sweep).
        anti_hyst_times: Anti-hysteresis timing values for tune mode
            (None for sweep).
        sweep_interval: Sweep interval for sweep mode in milliseconds
            (None for tune).

    Example:
        ```
        tune_setting = ModeSetting(
            current=280.0,
            tec_temp=25.0,
            anti_hyst_voltages=[35.0, 0.0],
            anti_hyst_times=[10.0],
            sweep_interval=None
        )
        ```
    """

    current: float
    tec_temp: float
    anti_hyst_voltages: list[float] | None
    anti_hyst_times: list[float] | None
    sweep_interval: int | None


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
        step_size: Wavelength step size between entries.
        tune_settings: Configuration for tune mode operation.
        sweep_settings: Configuration for sweep mode (None for ATLAS).
    """

    model: str
    _direct_access: dict[float, CalibrationEntry]
    entries: list[CalibrationEntry]
    min_wl: float
    max_wl: float
    step_size: float
    tune_settings: ModeSetting
    sweep_settings: ModeSetting | None

    def __init__(
        self,
        model: str,
        entries: list[CalibrationEntry],  # should be in original order
        tune_settings: ModeSetting,
        sweep_settings: ModeSetting | None,
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
        self.max_wl = _wavelengths[0]
        self.min_wl = _wavelengths[-1]
        try:
            self.step_size = abs(
                _wavelengths[0] - _wavelengths[_wavelengths.count(_wavelengths[0])]
            )
        except IndexError:
            logging.getLogger(__name__).warning(
                "Calibration loaded with less than 2 entries")

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
            return self.min_wl <= wl and self.max_wl >= wl


def _sanitize(s: str) -> str:
    """Clean and standardize parameter strings from calibration files.

    Removes whitespace, line endings, and converts to uppercase for
    consistent parameter name matching.

    Args:
        s: Raw string from calibration file.

    Returns:
        Cleaned and uppercase string.
    """
    return s.strip().replace("\r", "").replace("\n", "").upper()


def _parse_defaults_block(f: TextIO) -> tuple[str, ModeSetting, ModeSetting | None]:
    """Parse the [default_settings] block from a calibration file.

    Reads parameter lines until encountering the [look_up_table] marker.
    Handles both ATLAS and COMET laser configurations, with COMET
    requiring additional sweep mode parameters.

    Args:
        f: Text file stream positioned after the [default_settings] line.

    Returns:
        Tuple containing:
        - model: Laser model identifier ("ATLAS" or "COMET")
        - tune_settings: ModeSetting for tune mode operation
        - sweep_settings: ModeSetting for sweep mode (None for ATLAS)

    Raises:
        CalibrationError: If file ends unexpectedly or required parameters
            are missing.

    Example File Format:
        [default_settings]
        laser_model = COMET
        tune_diode_current = 280.0
        tune_tec_target = 25.0
        anti_hyst_phase_v_squared = [35.0, 0.0]
        anti_hyst_interval = [10.0]
        sweep_diode_current = 300.0
        sweep_tec_target = 30.0
        sweep_interval = 100
        [look_up_table]
    """
    settings = {}
    while True:
        line = f.readline()
        if not line:  # EOF
            raise CalibrationError("Unexpected end of file. No calibration data found")

        if "[look_up_table]" in line:
            break

        line = line.strip()
        if not line or "=" not in line:
            continue

        param, value = [_sanitize(x) for x in line.split(sep="=", maxsplit=1)]

        # Handle value being a list
        if "[" in value:
            value = [float(x) for x in value[1:-1].split(",")]
            settings[param] = value
        else:
            settings[param] = value

    try:
        model = settings.pop("LASER_MODEL").upper()
        tune = ModeSetting(
            current=float(settings.pop("TUNE_DIODE_CURRENT")),
            tec_temp=float(settings.pop("TUNE_TEC_TARGET")),
            anti_hyst_voltages=settings.pop("ANTI_HYST_PHASE_V_SQUARED"),
            anti_hyst_times=settings.pop("ANTI_HYST_INTERVAL"),
            sweep_interval=None,
        )
        if model == "ATLAS":
            sweep = None
        else:
            sweep = ModeSetting(
                current=float(settings.pop("SWEEP_DIODE_CURRENT")),
                tec_temp=float(settings.pop("SWEEP_TEC_TARGET")),
                sweep_interval=int(settings.pop("SWEEP_INTERVAL")),
                anti_hyst_voltages=None,
                anti_hyst_times=None,
            )
    except KeyError as e:  # Handle parameters missing
        raise CalibrationError(
            f"Calibration data incomplete. Missing parameter {e}!"
        ) from e

    if not settings == {}:  # Warn about extra parameters
        for param in settings.keys():
            logging.getLogger(__name__).warning(
                f"Invalid param {param} found in calibration data"
            )

    return model, tune, sweep


def _parse_rows(f: TextIO, model: str) -> list[CalibrationEntry]:
    """Parse the semicolon-delimited calibration table from a file.

    Reads CSV-formatted calibration data with semicolon delimiters and
    creates CalibrationEntry objects. Handles mode hop tracking for
    COMET lasers and assigns appropriate mode indices.

    Args:
        f: Text file stream positioned at the start of the data table.
        model: Laser model identifier ("ATLAS" or "COMET") to determine
            parsing behavior.

    Returns:
        List of CalibrationEntry objects in file order.

    Column Format:
        0: phase_section - Phase section heater voltage
        1: large_ring - Large ring heater voltage
        2: small_ring - Small ring heater voltage
        3: coupler - Coupler heater voltage
        4: wavelength - Target wavelength in nanometers
        5: mode_hop_flag - "0" for normal, "1" for mode hop (COMET only)

    Note:
        For COMET lasers, mode_index is tracked through mode hop sequences.
        ATLAS lasers ignore the mode_hop_flag and have mode_index set to None.

    Example Data:
        10.5;20.3;15.1;25.7;1550.0;0
        11.2;21.0;15.8;26.1;1549.5;1
    """
    csv_reader = reader(f, delimiter=";")
    entries: list[CalibrationEntry] = []

    cycler_index = 0
    mode_index = 1
    in_hop = False

    for row in csv_reader:
        hop_flag: bool = False
        if not row or all(not c for c in row):
            continue
        # normalize row length if trailing semicolons are missing
        if len(row) < 6:
            # You could raise here if the file is malformed
            raise CalibrationError("Incorrect file format, missing columns!")

        if model == "COMET":
            # hop flag as bool
            hop_flag = str(row[5]).strip() == "1"

            if in_hop and not hop_flag:
                in_hop = False
            elif not in_hop and hop_flag:
                in_hop = True
                mode_index += 1

        wl = float(row[4])
        ps, lr, sr, cp = (float(row[0]), float(row[1]), float(row[2]), float(row[3]))

        entries.append(
            CalibrationEntry(
                wavelength=wl,
                phase_section=ps,
                large_ring=lr,
                small_ring=sr,
                coupler=cp,
                mode_index=mode_index if model == "COMET" else None,
                mode_hop_flag=hop_flag,
                cycler_index=cycler_index,
            )
        )
        cycler_index += 1

    return entries


def load_calibration(file_path: str | Path) -> Calibration:
    """Load and parse a laser calibration file into a Calibration object.

    This function is the main entry point for loading calibration data.

    Args:
        file_path: Path to the calibration file (CSV format with semicolon
            delimiters).

    Returns:
        A fully initialized Calibration object containing all calibration
        data, settings, and metadata.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        CalibrationError: If the file format is invalid or contains
            incomplete data.
    """
    file_path = Path(file_path)
    entries: list[CalibrationEntry] = []

    with open(file_path, newline="") as f:
        first_line = f.readline()
        if "[default_settings]" in first_line:
            model, tune, sweep = _parse_defaults_block(f)
        else:
            # No defaults block: rewind so the first line belongs to the data table
            f.seek(0)
            model = Defaults.HARD_CODED_LASER_MODEL
            tune = ModeSetting(
                current=Defaults.HARD_CODED_STEADY_CURRENT,
                tec_temp=Defaults.HARD_CODED_STEADY_TEC_TEMP,
                anti_hyst_voltages=list(Defaults.HARD_CODED_STEADY_ANTI_HYST[0]),
                anti_hyst_times=list(Defaults.HARD_CODED_STEADY_ANTI_HYST[1]),
                sweep_interval=None,
            )
            sweep: ModeSetting | None = None
        # Now parse the lookup table rows
        entries = _parse_rows(f, model=model)

    return Calibration(
        model=model,
        entries=entries,  # original order retained
        tune_settings=tune,
        sweep_settings=sweep,  # None for non-COMET
    )
