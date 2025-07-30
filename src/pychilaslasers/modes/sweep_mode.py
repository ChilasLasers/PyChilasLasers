"""
Sweep mode implementation for laser wavelength sweeping operations.
<p>
This module implements sweep mode operation for COMET lasers. The sweep mode enables
continuous cycling through wavelengths with configurable bounds, intervals,
and repetition counts.
<p>
Authors: RLK, AVR, SDU
Last Revision: July 30, 2025 - Enhanced documentation and improved code formatting
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from pychilaslasers.modes.calibrated import __Calibrated
from pychilaslasers.modes.mode import LaserMode

if TYPE_CHECKING:
    from pychilaslasers import Laser


class SweepMode(__Calibrated):
    """Manages laser wavelength sweep operations.
    <p>
    SweepMode allows the laser to continuously cycle through a range of wavelengths
    with custom bounds, intervals, and repetition settings.
    
    Args:
        laser: The laser instance to control.
        calibration: Calibration data dictionary containing sweep mode parameters
            as returned by the :meth:`utils.read_calibration_file` method.
    
    Attributes:
        wavelength: Current wavelength setting from the cycler position.
        lower_bound: Lower bound of the sweep range in nanometers.
        upper_bound: Upper bound of the sweep range in nanometers.
        cycler_interval: Time interval between wavelength steps in microseconds.
        number_sweeps: Number of sweep cycles to perform (0 for infinite).
        mode: Returns LaserMode.SWEEP.
        
    Raises:
        ValueError: If laser model is not compatible with sweep mode.
    """

    def __init__(self, laser: Laser, calibration: dict) -> None:
        """Initialize sweep mode with laser instance and calibration data.
        
        Args:
            laser: The laser instance to control.
            calibration: Calibration data dictionary containing sweep mode parameters.
                This should be the full calibration dictionary as returned by
                :meth:`utils.read_calibration_file`.
                
        Raises:
            ValueError: If laser model is not COMET or calibration is invalid.
        """
        super().__init__(laser)
        if (
            laser.model != "COMET"
            or calibration.get("model") != "COMET"
            or "sweep" not in calibration
        ):
            raise ValueError("Sweep mode is only supported for COMET lasers.")

        # Gather calibration data
        self._calibration = calibration["sweep"]
        self._default_TEC: float = calibration["sweep"]["tec_temp"]
        self._default_current: float = calibration["sweep"]["current"]
        self._default_cycler_interval: int = calibration["sweep"]["cycler_interval"]
        self._wavelengths: list[float] = calibration["sweep"]["wavelengths"]


        self._min_wl: float = min(self._wavelengths)
        self._max_wl: float = max(self._wavelengths)

        self._no_sweeps: int = 0  # Default to infinite sweeps

    ########## Main Methods ##########
    
    def apply_defaults(self) -> None:
        """Apply default settings for sweep mode operation.
        <p>
        Sets the laser to the default TEC temperature, diode current,
        full wavelength range bounds, and cycler interval.
        """
        self._laser.tec.target = self._default_TEC
        self._laser.diode.current = self._default_current
        self.set_bounds(start_wl=self._max_wl, end_wl=self._min_wl)
        self.cycler_interval = self._default_cycler_interval

    def start(self, number_sweeps: int | None = None) -> None:
        """Start the wavelength sweep operation.
        <p> 
        Initiates the sweep operation with the configured number of cycles.
        The laser will begin cycling through the wavelength range according
        to the current bounds and interval settings.
        """
        if number_sweeps is not None:
            self.number_sweeps = number_sweeps

        self._laser.query(data=f"DRV:CYC:RUN {self.number_sweeps:d}")

    def stop(self) -> None:
        """Stop the current wavelength sweep operation.
        <p>
        Immediately halts the sweep operation. The laser will remain at its
        current wavelength position. Use :meth:`resume` to continue the sweep
        from where it was stopped.
        """

        self._laser.query(data="DRV:CYC:ABRT")
        
    def resume(self) -> None:
        """Resume a paused wavelength sweep operation.
        <p>
        Resumes a sweep operation that was previously stopped using the 
        :meth:`stop` method. The sweep will continue from its current position
        with the same configuration settings.
        """
        self._laser.query(data="DRV:CYC:CONT")

    def set_bounds(self, start_wl: float, end_wl: float) -> None:
        """Set the wavelength sweep range bounds.
        <p>
        Configures the start and end wavelength limits for the sweep operation.
        When setting bounds, the start bound is set to the first occurrence of
        a wavelength in the cycler table and the end bound is set to the last
        occurrence. This ensures proper indexing within the calibration table.
        <p>
        If the specified wavelengths are not exact matches in the calibration table,
        the closest available wavelengths will be used instead.

        Args:
            start_wl: Start bound wavelength in nanometers.
            end_wl: End bound wavelength in nanometers.

        Raises:
            ValueError: If bounds are outside the calibrated range or if lower >= upper.
        """
        if end_wl < self._min_wl or start_wl > self._max_wl:
            raise ValueError(f"Bounds must be between {self._min_wl} and {self._max_wl}.")
        if start_wl <= end_wl:
            raise ValueError(f"Lower bound {start_wl} must be less than upper bound {end_wl}.")
        if start_wl not in self._wavelengths:
            start_wl = self._find_closest_wavelength(start_wl)
        if end_wl not in self._wavelengths:
            end_wl = self._find_closest_wavelength(end_wl)

        # Get the index of the first occurrence of the start bound wavelength
        index_start: int = self._wavelengths.index(start_wl) 
        # Get the index of the first occurrence of the end bound wavelength
        index_end: int = self._wavelengths.index(end_wl)
        # Get the index of the last occurrence of the end bound wavelength
        index_end += self._wavelengths.count(end_wl) - 1
        
        self._laser.query(data=f"DRV:CYC:SPAN {index_start} {index_end}")

    def get_bounds(self) -> tuple[float, float]:
        """Get the current wavelength sweep range bounds.
        
        Returns:
            tuple[float, float]: A tuple containing (lower_bound, upper_bound) wavelengths 
                in nanometers.
        """
        [index_start, index_end] = self._laser.query("DRV:CYC:SPAN?").split(' ')
        return (
            self._wavelengths[int(index_start)],
            self._wavelengths[int(index_end)]
        )

    def get_total_time(self) -> float:
        """Calculate the total estimated time for the complete sweep operation.
        
        Returns:
            float: The estimated total time for the sweep in microseconds, based on the current
                interval, number of wavelength points, and number of sweep cycles.
                Returns 0.0 if number of sweeps is 0 (infinite sweeps).
        """
        return self.cycler_interval * len(self.get_points()) * self.number_sweeps if self.number_sweeps > 0 else 0.0

    def get_points(self) -> list[float]:
        """Get all wavelength points within the current sweep bounds.
        
        Returns:
            list[float]: List of wavelengths that will be swept through during operation, 
                including both the lower and upper bounds.
        """
        lower_index: int = self._wavelengths.index(self.lower_bound)
        upper_index: int = self._wavelengths.index(self.upper_bound)
        upper_index += self._wavelengths.count(self.upper_bound) - 1
        return self._wavelengths[lower_index:upper_index + 1]

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
        """Get the current wavelength from the cycler position.
        
        Returns:
            float: The wavelength corresponding to the current cycler position
                in nanometers.
            
        Note:
            Queries the laser hardware for the current cycler position
            and maps it to the corresponding wavelength in the calibration table.
            
        Warning:
            Depending on the cycler interval, this value may have changed by the 
            time it is retrieved due to the continuous sweeping operation.
        """
        current_cycler_index: int = int(self._laser.query("DRV:CYC:CPOS?"))
        return self._wavelengths[current_cycler_index]

    @property
    def cycler_interval(self) -> float:
        """Get the current cycler interval setting.
        
        Returns:
            float: The time interval between wavelength steps in milliseconds.
        """
        return float(self._laser.query("DRV:CYC:INT?"))

    @cycler_interval.setter
    def cycler_interval(self, value: int) -> None:
        """Set the cycler interval between wavelength steps.
        
        Args:
            value: Time interval between wavelength steps in microseconds.
                Must be a positive integer between 20 and 50 000.
                
        Warning:
            The cycler interval is part of the calibration data. Changing it
            may cause the laser to behave differently than expected.
            
        Raises:
            ValueError: If value is not a positive integer within the valid range.
        """
        if 20 > value or value > 50000 or not isinstance(value, int):
            raise ValueError("Cycler interval must be a positive integer between 20 and 50 000 microseconds.")
        self._laser.query(data=f"DRV:CYC:INT {value}")

    @property
    def number_sweeps(self) -> int:
        """Get the configured number of sweep cycles.
        
        Returns:
            int: The number of sweep cycles configured. 0 indicates infinite sweeps.
        """
        return self._no_sweeps

    @number_sweeps.setter
    def number_sweeps(self, value: int) -> None:
        """Set the number of sweep cycles to perform.
        
        Args:
            value: Number of sweep cycles to perform. Set to 0 for infinite sweeps.
            
        Raises:
            ValueError: If value is negative or not an integer.
        """
        if value < 0 or not isinstance(value, int):
            raise ValueError("Number of sweeps must be a non-negative integer.")
        self._no_sweeps = value


    ########## Private Methods ##########

    def _find_closest_wavelength(self, wavelength: float) -> float:
        """Find the closest available wavelength in the calibration table.
        <p>
        This method is used internally to find a wavelength in the calibration table
        that is closest to the specified target wavelength. This is useful when
        the exact requested wavelength is not available in the calibration data.
        
        Args:
            wavelength: The target wavelength in nanometers.
        
        Returns:
            float: The closest valid wavelength from the calibration data in nanometers.
        """
        return min(self._wavelengths, key=lambda x: abs(x - wavelength))


    ########## Method Overloads/Aliases ##########
    
    def get_wl(self) -> float:
        """Get the current wavelength setting.
        <p>
        Alias for the :attr:`wavelength` property getter for convenience.
        
        Returns:
            float: Current wavelength in nanometers.
        """
        return self.wavelength

    def set_interval(self, interval: int) -> None:
        """Set the cycler interval between wavelength steps.
        <p> 
        Alias for the :attr:`cycler_interval` property setter.
        Controls the time delay between each wavelength step during the sweep.
        
        Args:
            interval: Time interval between wavelength steps in microseconds.
                Must be a positive integer between 20 and 50 000.
            
        Warning:
            The cycler interval is part of the calibration data. Changing it
            may cause the laser to behave differently than expected.

        Raises:
            ValueError: If value is not a positive integer within the valid range.
        """
        self.cycler_interval = interval

    @property
    def lower_bound(self) -> float:
        """Get the lower bound of the current sweep range.
        <p>
        Alias for :meth:`get_bounds` result extraction for convenience.
        
        Returns:
            float: The wavelength at the lower bound of the current sweep range
                in nanometers.
        """
        return self.get_bounds()[0]

    @lower_bound.setter
    def lower_bound(self, value: float) -> None:
        """Set the lower bound of the sweep range.
        <p>
        Alias for :meth:`set_bounds` with current upper bound for convenience.
        
        Args:
            value: New lower bound wavelength in nanometers.
            
        Raises:
            ValueError: If value is outside the calibrated wavelength range or
                if it is greater than or equal to the current upper bound.
        """
        self.set_bounds(value, self.upper_bound)

    @property
    def upper_bound(self) -> float:
        """Get the upper bound of the current sweep range.
        <p>
        Alias for :meth:`get_bounds` result extraction for convenience.
        
        Returns:
            float: The wavelength at the upper bound of the current sweep range
                in nanometers.
        """
        return self.get_bounds()[1]

    @upper_bound.setter
    def upper_bound(self, value: float) -> None:
        """Set the upper bound of the sweep range.
        <p>
        Alias for :meth:`set_bounds` with current lower bound for convenience.
        
        Args:
            value: New upper bound wavelength in nanometers.
            
        Raises:
            ValueError: If value is outside the calibrated wavelength range or
                if it is less than or equal to the current lower bound.
        """
        self.set_bounds(self.lower_bound, value)

    @property
    def start_wavelength(self) -> float:
        """Get the starting wavelength of the sweep operation.
        <p>
        Alias for the :attr:`lower_bound` property for convenience.
        
        Returns:
            float: The lower bound wavelength of the current sweep range in nanometers.
        """
        return self.lower_bound

    @start_wavelength.setter
    def start_wavelength(self, value: float) -> None:
        """Set the starting wavelength of the sweep operation.
        <p>
        Alias for the :attr:`lower_bound` property setter for convenience.
        
        Args:
            value: The lower bound wavelength of the sweep range in nanometers.
        """
        self.lower_bound = value

    @property
    def end_wavelength(self) -> float:
        """Get the ending wavelength of the sweep operation.
        <p>
        Alias for the :attr:`upper_bound` property for convenience.

        Returns:
            float: The upper bound wavelength of the current sweep range in nanometers.
        """
        return self.upper_bound

    @end_wavelength.setter
    def end_wavelength(self, value: float) -> None:
        """Set the ending wavelength of the sweep operation.
        <p>
        Alias for the :attr:`upper_bound` property setter for convenience.
        
        Args:
            value: The upper bound wavelength of the sweep range in nanometers.
        """
        self.upper_bound = value

