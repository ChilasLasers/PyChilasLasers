from operator import index
from pychilaslasers.modes.calibrated import __Calibrated
from pychilaslasers.modes.mode import LaserMode


class SweepMode(__Calibrated):

    def __init__(self, laser, calibration: dict) -> None:
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

    @property
    def mode(self) -> LaserMode:
        """Get the mode type."""
        return LaserMode.SWEEP

    def apply_defaults(self) -> None:
        """Apply default settings for the mode."""
        self._laser.tec.target = self._default_TEC
        self._laser.diode.current = self._default_current
        self.set_bounds(lower_wl=self._min_wl, upper_wl=self._max_wl)
        self.cycler_interval = self._default_cycler_interval

    @property
    def wavelength(self) -> float:
        """Get the current wavelength setting."""
        current_cycler_index: int = int(self._laser.query("DRV:CYC:CPOS?"))
        return self._wavelengths[current_cycler_index]
    def get_wl(self) -> float:
        """Get the current wavelength setting."""
        return self.wavelength

    @property
    def lower_bound(self) -> float:
        """Get the lower bound of the sweep range."""
        return self.get_bounds()[0]

    @lower_bound.setter
    def lower_bound(self, value: float) -> None:
        """Set the lower bound of the sweep range."""
        if value < self._min_wl or value > self._max_wl:
            raise ValueError(f"Lower bound must be between {self._min_wl} and {self._max_wl}.")

    @property
    def upper_bound(self) -> float:
        """Get the upper bound of the sweep range."""
        return self.get_bounds()[1]

    @upper_bound.setter
    def upper_bound(self, value: float) -> None:
        """Set the upper bound of the sweep range."""
        if value < self._min_wl or value > self._max_wl:
            raise ValueError(f"Upper bound must be between {self._min_wl} and {self._max_wl}.")
    

    
    @property
    def cycler_interval(self) -> float:
        return float(self._laser.query("DRV:CYC:INT?"))

    @cycler_interval.setter
    def cycler_interval(self, value: int) -> None:
        self._laser.query(data=f"DRV:CYC:INT {value}")


    @property
    def no_sweeps(self) -> int:
        """Get the number of sweeps. 0 for infinite sweeps."""
        return self._no_sweeps
    
    
    @no_sweeps.setter
    def no_sweeps(self, value: int) -> None:
        """Set the number of sweeps. 0 for infinite sweeps."""
        if value < 0:
            raise ValueError("Number of sweeps cannot be negative.")
        self._no_sweeps = value

    def start(self) -> None:
        """Start the sweep."""
        self._laser.query(data=f"DRV:CYC:RUN {self.no_sweeps}")

    def stop(self) -> None:
        """Stop the sweep."""
        self._laser.query(data="DRV:CYC:ABRT")
    def resume(self) -> None:
        """Resume the sweep."""
        self._laser.query(data="DRV:CYC:CONT")



    def set_bounds(self, lower_wl: float, upper_wl: float) -> None:
        """ When setting bounds, the lower bound is set to the first occurrence of 
        a wavelength in the cycler table and the upper bound is set to the last occurrence.
        """
        if lower_wl < self._min_wl or upper_wl > self._max_wl:
            raise ValueError(f"Bounds must be between {self._min_wl} and {self._max_wl}.")
        if lower_wl >= upper_wl:
            raise ValueError(f"Lower bound {lower_wl} must be less than upper bound {upper_wl}.")


        index_lower: int = self._wavelengths.index(lower_wl) # Get the index of the first occurrence of the lower bound wavelength
        index_upper: int = self._wavelengths.index(upper_wl)
        index_upper += self._wavelengths.count(upper_wl) - 1
        
        self._laser.query(data=f"DRV:CYC:SPAN {index_lower} {index_upper}")

    def get_bounds(self) -> tuple[float, float]:
        """Get the current bounds of the sweep range.
        Returns a tuple of (lower_bound, upper_bound).
        """
        [index_lower, index_upper] = self._laser.query("DRV:CYC:SPAN?").split(' ')
        return (
            self._wavelengths[int(index_lower)],
            self._wavelengths[int(index_upper)]
        )

    def set_interval(self, interval: float) -> None:
        self._cycler_interval: float = interval

    def get_total_time(self) -> float:
        return self.cycler_interval * (self.upper_bound - self.lower_bound)

    def get_points(self) -> list[float]:
        lower_index: int = self._wavelengths.index(self.lower_bound)
        upper_index: int = self._wavelengths.index(self.upper_bound)
        return self._wavelengths[lower_index:upper_index + 1]


    

