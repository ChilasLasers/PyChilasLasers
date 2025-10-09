"""Sweep mode implementation for laser wavelength sweeping operations.

This module implements sweep mode operation for COMET lasers. The sweep mode enables
continuous cycling through wavelengths with configurable range, intervals,
and repetition counts.

**Authors**: RLK, AVR, SDU
"""

# ⚛️ Type checking
from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pychilaslasers.laser import Laser
    from pychilaslasers.calibration import Calibration

# ✅ Standard library imports
import logging

# ✅ Local imports
from pychilaslasers.exceptions.laser_error import LaserError
from pychilaslasers.exceptions.mode_error import ModeError
from pychilaslasers.modes.calibrated import __Calibrated
from pychilaslasers.modes.mode import LaserMode


class SweepMode(__Calibrated):
    """Manages laser wavelength sweep operations.

    SweepMode allows the laser to continuously cycle through a range of wavelengths
    with custom range, intervals, and repetition settings.

    Warning:
        The sweep operates from high wavelengths to low wavelengths.
        This means the start wavelength should be the maximum (highest) wavelength
        and the end wavelength should be the minimum (lowest) wavelength in your
        desired range.

    Args:
        laser: The laser instance to control.
        calibration: Calibration object as returned by the
            [`load_calibration()`][pychilaslasers.calibration.load_calibration] method.

    Attributes:
        wavelength: Current wavelength setting.
        start_wavelength: of the sweep range in nanometers.
        end_wavelength: of the sweep range in nanometers.
        interval: Time interval between wavelength steps in microseconds.
        number_sweeps: Number of sweep cycles to perform (0 for infinite).
        mode: Returns LaserMode.SWEEP.

    Raises:
        ValueError: If laser model is not compatible with sweep mode.

    """

    def __init__(self, laser: Laser, calibration: Calibration) -> None:
        """Initialize sweep mode with laser instance and calibration data.

        Args:
            laser: The laser instance to control.
            calibration: Calibration object as returned by the
                [`load_calibration()`][pychilaslasers.calibration.load_calibration]
                method.

        Raises:
            ValueError: If laser model is not COMET or calibration is invalid.

        """
        super().__init__(laser=laser, calibration=calibration)
        if (
            laser.model != "COMET"
            or calibration.model != "COMET"
            or calibration.sweep_settings is None
        ):
            raise ModeError(
                "Sweep mode is only supported for COMET lasers.",
                current_mode=laser.mode,
            )

        # Gather calibration data
        self._calibration: Calibration = calibration
        self._default_TEC: float = calibration.sweep_settings.tec_temp
        self._default_current: float = calibration.sweep_settings.current
        self._default_interval: int = calibration.sweep_settings.interval  # type: ignore

        self._no_sweeps: int = 0  # Default to infinite sweeps

    ########## Main Methods ##########

    def apply_defaults(self) -> None:
        """Apply default settings for sweep mode operation.

        Sets the laser to the default TEC temperature, diode current,
        full wavelength range and interval.
        """
        self._laser.tec.target = self._default_TEC
        self._laser.diode.current = self._default_current
        try:
            self.set_range(start_wl=self._max_wl, end_wl=self._min_wl)
        except LaserError as e:
            if "cycler" not in e.message:
                logging.getLogger(__name__).error(f"Failed to set sweep range: {e}")
                raise e

        self.interval = self._default_interval

    def start(self, number_sweeps: int | None = None) -> None:
        """Start the wavelength sweep operation.

        Initiates the sweep operation with the configured number of cycles.
        The laser will begin cycling through the wavelength range according
        to the current range and interval settings.
        """
        if number_sweeps is not None:
            self.number_sweeps = number_sweeps

        self._comm.query(data=f"DRV:CYC:RUN {self.number_sweeps:d}")

    def stop(self) -> None:
        """Stop the current wavelength sweep operation.

        Immediately halts the sweep operation. The laser will remain at its
        current wavelength position. Use `resume` to continue the sweep
        from where it was stopped.
        """
        self._comm.query(data="DRV:CYC:ABRT")

    def resume(self) -> None:
        """Resume a paused wavelength sweep operation.

        Resumes a sweep operation that was previously stopped using the
        `stop` method. The sweep will continue from its current position
        with the same configuration settings.
        """
        self._comm.query(data="DRV:CYC:CONT")

    def get_total_time(self) -> float:
        """Calculate the total estimated time for the complete sweep operation.

        Returns:
            The estimated total time for the sweep in microseconds, based on the current
                interval, number of wavelength points, and number of sweep cycles.
                Returns 0.0 if number of sweeps is 0 (infinite sweeps).

        """
        return (
            self.interval * len(self.get_points()) * self.number_sweeps
            if self.number_sweeps > 0
            else 0.0
        )

    def get_points(self) -> list[float]:
        """Get all wavelength points within the current sweep range.

        Returns:
            List of wavelengths that will be swept through during operation,
                including both the lower and upper wavelengths.

        """
        start, end = self.range
        return [
            wl
            for wl in [e.wavelength for e in self._calibration]
            if wl <= start and wl >= end
        ]

    ########## Properties (Getters/Setters) ##########

    @property
    def mode(self) -> LaserMode:
        """Get the laser operation mode.

        Returns:
            LaserMode: LaserMode.SWEEP indicating this is a sweep mode instance.

        """
        return LaserMode.SWEEP

    @property
    def wavelength(self) -> float:
        """Get the current wavelength from the laser.

        Returns:
            The wavelength corresponding to the current wavelength
                in nanometers.

        Note:
            Queries the laser hardware for the current position
            and maps it to the corresponding wavelength in the calibration table.

        Warning:
            Depending on the interval, this value may have changed by the
            time it is retrieved due to the continuous sweeping operation.

        """
        current_index: int = int(self._comm.query("DRV:CYC:CPOS?"))
        return self._calibration.entries[current_index].wavelength

    @property
    def interval(self) -> int:
        """Get the current interval setting.

        Returns:
            The time interval between wavelength steps in milliseconds.

        """
        return int(self._comm.query("DRV:CYC:INT?"))

    @interval.setter
    def interval(self, interval: int) -> None:
        """Set the interval between wavelength steps.

        Args:
            interval: Time interval between wavelength steps in microseconds.
                Must be a positive integer between 20 and 50 000.

        Warning:
            The interval is part of the calibration data. Changing it
            may cause the laser to behave differently than expected.

        Raises:
            ValueError: If interval is not a positive integer within the valid range.

        """
        if 20 > interval or interval > 50000 or not isinstance(interval, int):
            raise ValueError(
                f"Interval value {interval} not valid: must be a positive integer"
                "between 20 and 50 000 microseconds."
            )
        self._comm.query(data=f"DRV:CYC:INT {interval}")

    @property
    def number_sweeps(self) -> int:
        """Get the configured number of sweep cycles.

        Returns:
            The number of sweep cycles configured. 0 indicates infinite sweeps.

        """
        return self._no_sweeps

    @number_sweeps.setter
    def number_sweeps(self, number: int) -> None:
        """Set the number of sweep cycles to perform.

        Args:
            number: Number of sweep cycles to perform. Set to 0 for infinite sweeps.

        Raises:
            ValueError: If number is negative or not an integer.

        """
        if number < 0 or not isinstance(number, int):
            raise ValueError("Number of sweeps must be a non-negative integer.")
        self._no_sweeps = number

    @property
    def range(self) -> tuple[float, float]:
        """Get the current wavelength sweep range.

        Returns:
            A tuple containing (start_wavelength, end_wavelength) where
                start_wavelength is the higher value and end_wavelength is the lower
                value, reflecting the high-to-low sweep direction.

        """
        [index_start, index_end] = self._comm.query("DRV:CYC:SPAN?").split(" ")
        return (
            self._calibration.entries[int(index_start)].wavelength,
            self._calibration.entries[int(index_end)].wavelength,
        )

    @range.setter
    def range(self, range: tuple[float, float] | list[float]) -> None:
        """Set the wavelength sweep range.

        Configures the start and end wavelength limits for the sweep operation.
        When setting the range the start wavelength is set to the first occurrence of
        that wavelength in the calibration table and the end wavelength is set to the
        last occurrence. This ensures proper indexing within the calibration table.

        **Important**: The sweep goes from high to low wavelengths. Therefore:
        - `start_wl` should be the highest wavelength (where sweep begins)
        - `end_wl` should be the lowest wavelength (where sweep ends)

        If the specified wavelengths are not exact matches in the calibration table,
        the closest available wavelengths will be used instead.

        Args:
            range: Tuple or list containing (start_wl, end_wl) where start_wl is the
                highest wavelength (where sweep begins) and end_wl is the lowest
                wavelength (where sweep ends), both in nanometers.

        Raises:
            ValueError: If wavelength are outside the calibrated range or if
                start <= end.

        """
        start_wl, end_wl = range
        if end_wl < self._min_wl or start_wl > self._max_wl:
            raise ValueError(f"Range must be in [{self._max_wl} -> {self._min_wl}].")
        if start_wl <= end_wl:
            raise ValueError(
                f"Start wavelength {start_wl} cannot be less than end wavelength "
                f"{end_wl}."
            )

        # Get the index of the first occurrence of the start wavelength
        index_start: int = self._calibration.get_mode_hop_start(start_wl).cycler_index
        # Get the index of the first occurrence of the end wavelength
        index_end: int = self._calibration[end_wl].cycler_index

        self._comm.query(data=f"DRV:CYC:SPAN {index_start} {index_end}")

    @property
    def cycler_running(self) -> bool:
        """Indicates if the cycler is currently running.

        Returns:
            (bool): if the cycler is running

        """
        return bool(int(self._comm.query("DRV:CYC:RUN?")))

    ########## Method Overloads/Aliases ##########

    def set_count(self, count: int) -> None:
        """Alias for the `number_sweeps` property setter.

        Args:
            count: Number of sweeps to perform. Set to 0 for infinite sweeps.

        Raises:
            ValueError: If count is negative or not an integer.

        """
        self.number_sweeps = count

    def get_wl(self) -> float:
        """Alias for the `wavelength` property getter for convenience.

        Returns:
            Current wavelength in nanometers.

        """
        return self.wavelength

    def set_interval(self, interval: int) -> None:
        """Alias for the `interval` property setter.

        Args:
            interval: Time interval between wavelength steps in microseconds.
                Must be a positive integer between 20 and 50 000.

        Warning:
            The interval is part of the calibration data. Changing it
            may cause the laser to behave differently than expected.

        Raises:
            ValueError: If interval is not a positive integer within the valid range.

        """
        self.interval = interval

    @property
    def start_wavelength(self) -> float:
        """Get the start wavelength of the current sweep range.

        Alias for `get_range` result extraction for convenience.

        Returns:
            The wavelength at the start of the current sweep range
                in nanometers.

        """
        return self.range[0]

    @start_wavelength.setter
    def start_wavelength(self, wavelength: float) -> None:
        """Set the lower wavelength of the sweep range.

        Alias for `set_range` with current end wavelength for convenience.

        Args:
            wavelength: New start wavelength in nanometers.

        Raises:
            ValueError: If wavelength is outside the calibrated wavelength range or
                if it is greater than or equal to the current end wavelength.

        """
        self.range = (wavelength, self.end_wavelength)

    @property
    def end_wavelength(self) -> float:
        """Get the end wavelength of the current sweep range.

        Alias for `get_range` result extraction for convenience.

        Returns:
            The wavelength at the end of the current sweep range
                in nanometers.

        """
        return self.range[1]

    @end_wavelength.setter
    def end_wavelength(self, wavelength: float) -> None:
        """Set the end wavelength of the sweep range.

        Alias for `set_range` with current start wavelength for convenience.

        Args:
            wavelength: New end wavelength in nanometers.

        Raises:
            ValueError: If wavelength is outside the calibrated wavelength range or
                if it is less than or equal to the current start wavelength.

        """
        self.range = (self.start_wavelength, wavelength)

    def get_range(self) -> tuple[float, float]:
        """Alias for `range`.

        Returns the current sweep range as configured for high-to-low wavelength
        sweeping.

        Returns:
            A tuple containing (start_wavelength, end_wavelength) where
                start_wavelength is the higher value and end_wavelength is the lower
                value, reflecting the high-to-low sweep direction.

        """
        return self.range

    def set_range(self, start_wl: float, end_wl: float) -> tuple[float, float]:
        """Alias for `range`.

        Returns the current sweep range as configured for high-to-low wavelength
          sweeping.

        Args:
            start_wl: Start wavelength in nanometers (should be the higher value).
            end_wl: End wavelength in nanometers (should be the lower value).

        Raises:
            ValueError: If wavelength are outside the calibrated range or
                if start <= end.

        Returns:
            A tuple with the actual wavelengths that were set
        """
        self.range = (start_wl, end_wl)
        return self.range
