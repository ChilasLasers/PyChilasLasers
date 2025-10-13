"""Calibration file parsing and loading functionality.

Functions:
    load_calibration: Main entry point to load calibration files.
"""

import logging
from csv import reader
from pathlib import Path
from typing import Any, TextIO

from pychilaslasers.calibration.structs import (
    TuneMethod,
    TuneSettings,
    SweepSettings,
    CalibrationEntry,
    Calibration,
)
from pychilaslasers.calibration.defaults import Defaults
from pychilaslasers.exceptions.calibration_error import CalibrationError


def _sanitize(s: str) -> str:
    """Clean and standardize parameter strings from calibration files.

    Removes whitespace, line endings, and converts to uppercase for
    consistent parameter name matching.

    Args:
        s: Raw string from calibration file.

    Returns:
        Cleaned and uppercase string.
    """
    return (
        s.strip()
        .replace("\r", "")
        .replace("\n", "")
        .replace('"', "")
        .replace("'", "")
        .upper()
    )


def _parse_defaults_block(f: TextIO) -> tuple[str, TuneSettings, SweepSettings | None]:
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
        tune_method = "file"
        anti_hyst_phase_v_squared = [35.0, 0.0]
        anti_hyst_interval = [10.0]
        sweep_diode_current = 300.0
        sweep_tec_target = 30.0
        sweep_interval = 100
        [look_up_table]
    """
    settings: dict[str, Any] = {}
    while True:
        line = f.readline()
        if not line:  # EOF
            raise CalibrationError("Unexpected end of file. No calibration data found")

        if "[look_up_table]" in line:
            break

        line = line.strip()
        if not line or "=" not in line:
            continue

        param, raw_value = [_sanitize(x) for x in line.split(sep="=", maxsplit=1)]

        # Handle value being a list
        if "[" in raw_value:
            value = [float(x.strip()) for x in raw_value[1:-1].split(",")]
            settings[param] = value
        else:
            settings[param] = [raw_value]

    try:
        model = settings.pop("LASER_MODEL")[0].upper()
        tune = TuneSettings(
            current=float(settings.pop("TUNE_DIODE_CURRENT")[0]),
            tec_temp=float(settings.pop("TUNE_TEC_TARGET")[0]),
            anti_hyst_voltages=settings.pop("ANTI_HYST_PHASE_V_SQUARED"),
            anti_hyst_times=settings.pop("ANTI_HYST_INTERVAL"),
            method=TuneMethod(settings.pop("TUNE_METHOD", [Defaults.TUNE_METHOD])[0]),
        )
        if model == "ATLAS":
            sweep = None
        else:
            sweep = SweepSettings(
                current=float(settings.pop("SWEEP_DIODE_CURRENT")[0]),
                tec_temp=float(settings.pop("SWEEP_TEC_TARGET")[0]),
                interval=int(settings.pop("SWEEP_INTERVAL")[0]),
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

    no_expected_columns = 5 if model == "ATLAS" else 6
    cycler_index = 0
    mode_index = 1
    in_hop = False

    for row in csv_reader:
        hop_flag: bool = False
        if not row or all(not c for c in row):
            continue
        # normalize row length if trailing semicolons are missing
        if len(row) < no_expected_columns:
            # You could raise here if the file is malformed
            raise CalibrationError("Incorrect file format, missing columns!")

        if model == "COMET":
            # hop flag as bool
            hop_flag = int(float(str(row[5]).strip())) == 1

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

    model: str
    tune: TuneSettings
    sweep: SweepSettings | None
    with open(file_path, newline="") as f:
        first_line = f.readline()
        if "[default_settings]" in first_line:
            model, tune, sweep = _parse_defaults_block(f)
        else:
            # No defaults block: rewind so the first line belongs to the data table
            f.seek(0)
            model = Defaults.LASER_MODEL
            tune = TuneSettings(
                current=Defaults.TUNE_CURRENT,
                tec_temp=Defaults.TUNE_TEC_TEMP,
                anti_hyst_voltages=list(Defaults.TUNE_ANTI_HYST[0]),
                anti_hyst_times=list(Defaults.TUNE_ANTI_HYST[1]),
                method=Defaults.TUNE_METHOD,
            )
            sweep = None
        # Now parse the lookup table rows
        entries = _parse_rows(f, model=model)

    return Calibration(
        model=model,
        entries=entries,  # original order retained
        tune_settings=tune,
        sweep_settings=sweep,  # None for non-COMET
    )
