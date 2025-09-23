"""Calibration data management for Chilas laser systems.

This module provides comprehensive functionality for loading, parsing, and managing
calibration data for Chilas laser systems. It supports both ATLAS and COMET laser
models with their respective calibration file formats.

Classes:
    Calibration: Main calibration data container with wavelength lookup.
    CalibrationEntry: Individual calibration data point for a wavelength.
    TuneSettings: Configuration for tune mode operation.
    SweepSettings: Configuration for sweep mode operation.

Functions:
    load_calibration: Load calibration data from file.
"""

from .structs import Calibration, CalibrationEntry, TuneSettings, SweepSettings
from .calibration_parsing import load_calibration
from .defaults import Defaults

__all__ = [
    "Calibration",
    "CalibrationEntry",
    "Defaults",
    "SweepSettings",
    "TuneSettings",
    "load_calibration",
]
