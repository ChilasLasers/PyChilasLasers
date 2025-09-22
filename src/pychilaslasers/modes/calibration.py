"""Contains all the necessary objects and logic to use calibration data."""

from cmath import phase
from csv import reader
from dataclasses import dataclass, field
from io import TextIOWrapper
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
    """Represents a single entry in the calibration data."""

    wavelength: float
    phase_section: float
    large_ring: float
    small_ring: float
    coupler: float
    mode_index: int | None
    mode_hop_flag: bool
    cycler_index: int
    heater_values: tuple[float, float, float, float] = field(init=False)

    def __post_init__(self):
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
    """Structure for holding the calibrated settings of a laser mode."""
    current: float
    tec_temp: float
    anti_hyst_voltages: list[float] | None
    anti_hyst_times: list[float] | None
    sweep_interval: int | None

@dataclass
class Calibration:
    """Object representing the calibration settings of a laser.

    This is a object representation of a calibration file in a easy to use way. It
    allows for the access of calibration entries based on the wavelength. As well as
    handling their organization and finding the closest entry available.
    """

    model : str
    _direct_access: dict[float,CalibrationEntry]
    entries: list[CalibrationEntry]
    min_wl: float
    max_wl: float
    step_size: float
    tune_settings: ModeSetting
    sweep_settings: ModeSetting | None

    def __init__(self,
                model: str,
                entries: list[CalibrationEntry], # should be in original order
                tune_settings: ModeSetting,
                sweep_settings: ModeSetting | None) -> None:
        """Data class holding calibration of a Laser.

        Args:
            model (str): model of the laser the calibration is for
            entries (list[CalibrationEntry]): list of all entries in the calibration
                sorted in the order they are found in the file
            tune_settings (ModeSetting): settings for the tune mode of the laser
            sweep_settings (ModeSetting | None): settings for the sweep mode of the
                laser. May be None in case of an atlas laser.
        """
        self.model = model
        self.entries = entries
        self.tune_settings = tune_settings
        self.sweep_settings = sweep_settings
        _wavelengths: list[float] = [entry.wavelength for entry in entries]
        self.max_wl = _wavelengths[0]
        self.min_wl = _wavelengths[-1]
        self.step_size =  abs(
             _wavelengths[0] - _wavelengths[_wavelengths.count(_wavelengths[0])]
                            )

        self._direct_access = {
            entry.wavelength : entry for entry in entries if not entry.mode_hop_flag 
                                }

    def get_mode_hop_start(self, wavelength: float) -> CalibrationEntry:
        """Returns the calibration entry at the start of a mode hop procedure.

        Args:
            wavelength (float): requested

        Returns:
            CalibrationEntry: of the first entry in a mode hop procedure if the
                wavelength is part of one. Otherwise returns `self[wavelength]`
        """
        mode_hops: list[CalibrationEntry] = [
            entry for entry in self.entries
            if entry.wavelength == wavelength and entry.mode_hop_flag]
        if mode_hops:
            return mode_hops[0]
        else:
            return self[wavelength]

    def __getitem__(self, wavelength: float) -> CalibrationEntry:
        if wavelength in self._direct_access:
            return self._direct_access[wavelength]
        elif wavelength in self:
            return self._direct_access[
                min(self._direct_access.keys(), key=lambda x: abs(x - wavelength))
                                        ]
        else:
            raise KeyError(wavelength)

    def __iter__(self) -> Iterator[CalibrationEntry]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    @overload
    def __contains__(self, wl: CalibrationEntry) -> bool: ...
    @overload
    def __contains__(self, wl: float) -> bool: ...
    def __contains__(self, wl: float | CalibrationEntry) -> bool:
        """Enables the use of the in operator.

        Args:
            wl (float | CalibrationEntry): Either a float representing a wavelength
                or a CalibrationEntry

        Returns:
            bool: For wavelength returns `self.min_wl < wl and self.max_wl > wl`
                for a `CalibrationEntry` returns weather the specific entry is in
                the calibration provided
        """
        if isinstance(wl,CalibrationEntry):
            return wl in self.entries
        else:
            return self.min_wl < wl and self.max_wl > wl

def _sanitize(s: str) -> str:
    return s.strip().replace("\r", "").replace("\n", "").upper()


def _parse_defaults_block(f: TextIO) -> tuple[str, ModeSetting, ModeSetting | None]:
    """Reads after the initial line that contained '[default_settings]'.

    Stops when '[look_up_table]' line is encountered.
    Returns (model, tune_settings, sweep_settings)
    """
    settings = {}
    while True:
        line = f.readline()
        if not line: # EOF
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
        model = settings["laser_model"].upper()
        tune  = ModeSetting(
            current=float(settings.pop("tune_diode_current")),
            tec_temp=float(settings.pop("tune_tec_target")),
            anti_hyst_voltages=settings.pop("anti_hyst_phase_v_squared"),
            anti_hyst_times=settings.pop("anti_hyst_interval"),
            sweep_interval=None
            )
        if model == "ATLAS":
            sweep = None
        else:
            sweep = ModeSetting(
            current=float(settings.pop("sweep_diode_current")),
            tec_temp=float(settings.pop("sweep_tec_target")),
            sweep_interval=int(settings.pop("sweep_interval")),
            anti_hyst_voltages=None,
            anti_hyst_times=None
            )

    except KeyError as e: # Handle parameters missing
        raise CalibrationError(
            f"Calibration data incomplete. Missing parameter {e}!") from e

    if not settings == {}: # Warn about extra parameters
        for param in settings.keys():
            logging.getLogger(__name__).warning(
                f"Invalid param {param} found in calibration data")

    return model, tune, sweep

def _parse_rows(
    f: TextIO, model: str
) -> list[CalibrationEntry]:
    """Assumes the next lines are the semicolon-delimited calibration table.

    Column indices are preserved from your previous implementation:
      0: phase_section
      1: large_ring
      2: small_ring
      3: coupler
      4: wavelength
      5: mode_hop_flag ("0" or "1")
    """
    csv_reader = reader(f, delimiter=";")
    entries: list[CalibrationEntry] = []

    cycler_index = 0
    mode_index = 0
    in_hop = False

    for row in csv_reader:
        hop_flag: bool = False
        if not row or all(not c for c in row):
            continue
        # normalize row length if trailing semicolons are missing
        if len(row) < 6:
            # You could raise here if the file is malformed
            continue


        if model == "COMET":
            # hop flag as bool
            hop_flag = str(row[5]).strip() == "1"

            # with a sticky notion of being "in a hop").
            if in_hop and not hop_flag:
                in_hop = False
                mode_index += 1
            if hop_flag:
                in_hop = True

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
    """Refactored loader that returns a `Calibration` object.

    Keeps backward compatibility with your CSV structure and header keys.
    """
    file_path = Path(file_path)
    model = Defaults.HARD_CODED_LASER_MODEL
    tune = ModeSetting(
        current=Defaults.HARD_CODED_STEADY_CURRENT,
        tec_temp=Defaults.HARD_CODED_STEADY_TEC_TEMP,
        anti_hyst_voltages=list(Defaults.HARD_CODED_STEADY_ANTI_HYST[0]),
        anti_hyst_times=list(Defaults.HARD_CODED_STEADY_ANTI_HYST[1]),
        sweep_interval=None
    )
    sweep: ModeSetting | None = None
    entries: list[CalibrationEntry] = []

    with open(file_path, newline="") as f:


        first_line = f.readline()
        if "[default_settings]" in first_line:
            model, tune, sweep = _parse_defaults_block(f)
        else:
            # No defaults block: rewind so the first line belongs to the data table
            f.seek(0)
            model = Defaults.HARD_CODED_LASER_MODEL
        # Now parse the lookup table rows
        entries = _parse_rows(f, model=model)

    return Calibration(
        model=model,
        entries=entries,            # original order retained
        tune_settings=tune,
        sweep_settings=sweep,       # None for non-COMET
    )