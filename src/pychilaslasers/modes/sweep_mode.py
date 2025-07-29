"""Sweep mode implementation for laser wavelength sweeping operations."""

from __future__ import annotations
from typing import TYPE_CHECKING

from pychilaslasers.modes.calibrated import __Calibrated
from pychilaslasers.modes.mode import LaserMode

if TYPE_CHECKING:
    from pychilaslasers import Laser


class SweepMode(__Calibrated):
    """Manages laser wavelength sweep operations using calibrated wavelength tables.
    
    SweepMode allows the laser to continuously cycle through a range of wavelengths
    based on a predefined calibration table. The sweep can be configured with custom
    bounds, intervals, and repetition counts.
    
    Attributes:
        wavelength: Current wavelength setting from the cycler position.
        lower_bound: Lower bound of the sweep range.
        upper_bound: Upper bound of the sweep range.
        cycler_interval: Time interval between wavelength steps in milliseconds.
        no_sweeps: Number of sweep cycles to perform (0 for infinite).
    """

    def __init__(self, laser: Laser, calibration: dict) -> None:
        """Initialize sweep mode with laser instance and calibration data.
        
        Args:
            laser: The laser instance to control.
            calibration: Calibration dictionary containing sweep configuration.
                Must include a "sweep" key with nested configuration data.
                
        Note:
            The wavelengths list is automatically sorted during initialization.
            Default values are extracted from the calibration data.
        """
        super().__init__(laser)
        self._calibration = calibration["sweep"]

        self._default_TEC: float = calibration["sweep"]["tec_temp"]
        self._default_current: float = calibration["sweep"]["current"]
        self._default_cycler_interval: int = calibration["sweep"]["cycler_interval"]
        self._wavelengths: list[float] = calibration["sweep"]["wavelengths"]
        self._wavelengths.sort()

        self._min_wl: float = min(self._wavelengths)
        self._max_wl: float = max(self._wavelengths)

        self._no_sweeps: int = 0  # Default to infinite sweeps

    ########## Main Methods ##########
    
    def apply_defaults(self) -> None:
        """Apply default settings for the mode.
        
        Sets the laser to the default TEC temperature, diode current,
        full wavelength range bounds, and cycler interval from calibration data.
        """
        self._laser.tec.target = self._default_TEC
        self._laser.diode.current = self._default_current
        self.set_bounds(lower_wl=self._min_wl, upper_wl=self._max_wl)
        self.cycler_interval = self._default_cycler_interval

    def start(self) -> None:
        """Start the wavelength sweep.
        
        Initiates the sweep operation with the configured number of cycles.
        """
        self._laser.query(data=f"DRV:CYC:RUN {self.no_sweeps}")

    def stop(self) -> None:
        """Stop the current wavelength sweep.
        
        Aborts the sweep operation immediately.
        """
        self._laser.query(data="DRV:CYC:ABRT")
        
    def resume(self) -> None:
        """Resume a paused wavelength sweep.
        
        Continues the sweep from where it was stopped.
        """
        self._laser.query(data="DRV:CYC:CONT")

    def set_bounds(self, lower_wl: float, upper_wl: float) -> None:
        """Set the wavelength sweep bounds.
        
        When setting bounds, the lower bound is set to the first occurrence of 
        a wavelength in the cycler table and the upper bound is set to the last occurrence.
        
        Args:
            lower_wl: Lower bound wavelength in nanometers.
            upper_wl: Upper bound wavelength in nanometers.
            
        Raises:
            ValueError: If bounds are outside the calibrated range, if lower >= upper,
                or if the wavelengths are not in the calibration table.
        """
        if lower_wl < self._min_wl or upper_wl > self._max_wl:
            raise ValueError(f"Bounds must be between {self._min_wl} and {self._max_wl}.")
        if lower_wl >= upper_wl:
            raise ValueError(f"Lower bound {lower_wl} must be less than upper bound {upper_wl}.")
        if lower_wl not in self._wavelengths or upper_wl not in self._wavelengths:
            raise ValueError(f"Both bounds must be in the cycler table: {self._wavelengths}.")

        index_lower: int = self._wavelengths.index(lower_wl) # Get the index of the first occurrence of the lower bound wavelength
        index_upper: int = self._wavelengths.index(upper_wl)
        index_upper += self._wavelengths.count(upper_wl) - 1
        
        self._laser.query(data=f"DRV:CYC:SPAN {index_lower} {index_upper}")

    def get_bounds(self) -> tuple[float, float]:
        """Get the current bounds of the sweep range.
        
        Returns:
            A tuple of (lower_bound, upper_bound) wavelengths in nanometers.
        """
        [index_lower, index_upper] = self._laser.query("DRV:CYC:SPAN?").split(' ')
        return (
            self._wavelengths[int(index_lower)],
            self._wavelengths[int(index_upper)]
        )

    def set_interval(self, interval: float) -> None:
        """Set the cycler interval.
        
        Args:
            interval: Time interval between wavelength steps.
            
        Note:
            This method updates the internal interval value but may need
            additional implementation to apply to the laser hardware.
            
        Todo:
            Apply the interval to the laser hardware, similar to cycler_interval setter.
        """
        self._cycler_interval: float = interval

    def get_total_time(self) -> float:
        """Calculate the total time for one complete sweep.
        
        Returns:
            The estimated total time for one sweep cycle based on
            the current interval and number of wavelength points.
        """
        return self.cycler_interval * len(self.get_points())

    def get_points(self) -> list[float]:
        """Get the wavelength points within the current sweep bounds.
        
        Returns:
            List of wavelengths that will be swept through, including
            both the lower and upper bounds.
        """
        lower_index: int = self._wavelengths.index(self.lower_bound)
        upper_index: int = self._wavelengths.index(self.upper_bound)
        upper_index += self._wavelengths.count(self.upper_bound) - 1
        return self._wavelengths[lower_index:upper_index + 1]

    ########## Properties (Getters/Setters) ##########
    
    @property
    def mode(self) -> LaserMode:
        """Get the mode type.
        
        Returns:
            LaserMode.SWEEP indicating this is a sweep mode instance.
        """
        return LaserMode.SWEEP

    @property
    def wavelength(self) -> float:
        """Get the current wavelength setting.
        
        Returns:
            The wavelength corresponding to the current cycler position.
            
        Note:
            Queries the laser hardware for the current cycler position
            and maps it to the corresponding wavelength in the calibration table.
        """
        current_cycler_index: int = int(self._laser.query("DRV:CYC:CPOS?"))
        return self._wavelengths[current_cycler_index]

    @property
    def lower_bound(self) -> float:
        """Get the lower bound of the sweep range.
        
        Returns:
            The wavelength at the lower bound of the current sweep range.
        """
        return self.get_bounds()[0]

    @lower_bound.setter
    def lower_bound(self, value: float) -> None:
        """Set the lower bound of the sweep range.
        
        Args:
            value: New lower bound wavelength in nanometers.
            
        Raises:
            ValueError: If value is outside the calibrated wavelength range.
        """
        if value < self._min_wl or value > self._max_wl:
            raise ValueError(f"Lower bound must be between {self._min_wl} and {self._max_wl}.")

    @property
    def upper_bound(self) -> float:
        """Get the upper bound of the sweep range.
        
        Returns:
            The wavelength at the upper bound of the current sweep range.
        """
        return self.get_bounds()[1]

    @upper_bound.setter
    def upper_bound(self, value: float) -> None:
        """Set the upper bound of the sweep range.
        
        Args:
            value: New upper bound wavelength in nanometers.
            
        Raises:
            ValueError: If value is outside the calibrated wavelength range.
        """
        if value < self._min_wl or value > self._max_wl:
            raise ValueError(f"Upper bound must be between {self._min_wl} and {self._max_wl}.")

    @property
    def cycler_interval(self) -> float:
        """Get the current cycler interval.
        
        Returns:
            The time interval between wavelength steps in milliseconds.
        """
        return float(self._laser.query("DRV:CYC:INT?"))

    @cycler_interval.setter
    def cycler_interval(self, value: int) -> None:
        """Set the cycler interval.
        
        Args:
            value: Time interval between wavelength steps in milliseconds.
                Must be a positive integer.
                
        Raises:
            ValueError: If value is not a positive integer.
        """
        if value <= 0 or not isinstance(value, int):
            raise ValueError("Cycler interval must be a positive integer.")
        self._laser.query(data=f"DRV:CYC:INT {value}")

    @property
    def no_sweeps(self) -> int:
        """Get the number of sweeps.
        
        Returns:
            The number of sweep cycles configured. 0 indicates infinite sweeps.
        """
        return self._no_sweeps
    
    @no_sweeps.setter
    def no_sweeps(self, value: int) -> None:
        """Set the number of sweeps.
        
        Args:
            value: Number of sweep cycles to perform. 0 for infinite sweeps.
            
        Raises:
            ValueError: If value is negative or not an integer.
        """
        if value < 0 or not isinstance(value, int):
            raise ValueError("Number of sweeps needs to be a positive integer.")
        self._no_sweeps = value

    ########## Method Overloads/Aliases ##########
    
    def get_wl(self) -> float:
        """Get the current wavelength setting.
        
        Returns:
            The current wavelength in nanometers.
            
        Note:
            Alias method for wavelength property for convenience.
        """
        return self.wavelength


    

