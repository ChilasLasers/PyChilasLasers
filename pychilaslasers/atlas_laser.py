import time
import numpy as np
import logging
from enum import IntEnum
from typing import Optional
from pychilaslasers.lasers_tlm import TLMLaser
from pychilaslasers.OperatingModeError import OperatingModeError

logger = logging.getLogger(__name__)

DEFAULT_ANTI_HYST_V_PHASE_SQUARED = 20.0
DEFAULT_ANTI_HYST_SLEEP = 0.01 # 1ms


DEFAULT_TEC_TARGET = 25.0
DEFAULT_DIODE_CURRENT = 280.0


class OperatingMode(IntEnum):
    """Different operating modes for the ATLAS laser.

    Attributes:
        Manual: For manual operation
        STEADY: For steady tuning operation
    """
    MANUAL = 0
    STEADY = 1



class AtlasLaser(TLMLaser):
    """
    Atlas laser class, inheriting from TLMLaser.
    
    This class is designed to handle the specific functionalities and configurations
    related to the Atlas laser system. It supports two main operating modes:
    
    1. **Manual Mode (OperatingMode.MANUAL)**: 
       - Allows direct manual control of heater voltages
       - Bypasses cycler table entries for fine-tuned control
       - Use set_heater_manual() and get_heater_manual() methods
       
    2. **Steady Mode (OperatingMode.STEADY)**: 
       - Uses cycler table entries for wavelength control
       - Supports automated wavelength tuning functions
       - Use set_wavelength_abs(), set_wavelength_rel(), etc.
    
    The class can be extended with additional methods for specific Atlas laser
    functionalities.
    """

    def __init__(self, address=None, timeout=10):
        super().__init__(address, timeout)
        self._operation_mode = None


    
    def get_wavelength_idx(self, idx: int) -> float:
        """Gets wavelength corresponding to cycler entry index

        Args:
            idx(int): index of cycler entry to get wavelength value for

        Returns:
            (float): wavelength in nm
        """
        if self._operation_mode != OperatingMode.STEADY:
            raise OperatingModeError("Cannot get wavelength in manual mode.")
        return float(self._cycler_table[idx, type(self).cycler_config.WAVELENGTH])

    def get_idx_wavelength(self, wavelength: float) -> int:
        """Gets cycler entry index closest to a wavelength

        This method returns the cycler entry index corresponding to certain
        wavelength. It will find the closest matching wavelength value, if the
        wavelength value does not exactly occur in the cycler table.

        The method ensures that no indices of entries corresponding to mode
        hops will be returned.

        Args:
            wavelength(float): wavelength in nm to search corresponding cycler
                entry index for

        Returns:
            (int): index of cycler entry with wavelength value closest to input
                wavelength
        """

        # Search for the best look-up table entry, which is closest to the requested wavelength
        # Extract all wavelength values from the cycler table for comparison
        wl_array = self._cycler_table[:, type(self).cycler_config.WAVELENGTH]
        
        # Perform boundary checking to ensure wavelength is within valid range
        # Find minimum supported wavelength and clamp input if below threshold
        wl_min = np.min(wl_array)
        if wavelength < wl_min:
            logger.warning(f"Input wavelength {wavelength:.3f} smaller than minimum {wl_min:.3f}.")
            wavelength = wl_min  # Clamp to minimum supported wavelength
        
        # Find maximum supported wavelength and clamp input if above threshold
        wl_max = np.max(wl_array)
        if wavelength > wl_max:
            logger.warning(f"Input wavelength {wavelength:.3f} larger than maximum {wl_max:.3f}.")
            wavelength = wl_max  # Clamp to maximum supported wavelength
        
        # Find the cycler table entry with wavelength closest to the target
        # Calculate absolute differences and find index of minimum difference
        _idx = np.argmin(np.abs(wl_array - wavelength))
        

        # Extract and return the entry index as an integer
        # This index can be used to configure the laser hardware
        return int(_idx)
    
    
    def get_wavelength(self) -> float:
        """Gets and returns the current wavelength the laser is tuned to

        Since the driver keeps track of the index of the last applied cycler
        table entry, this can be used to determine the corresponding wavelength
        the laser is at, based from the calibrated values in the cycler table.

        Returns:
            (float): current wavelength in nm
        """
        if self._idx_active is None:
            idx = self.get_cycler_index()
            # Update the field to keep track of the active index
            self._idx_active = idx
        else:
            idx = self._idx_active
        # Request the wavelength corresponding to the active index
        wavelength = self.get_wavelength_idx(idx)
        return wavelength
    

    
    def trigger_pulse(self):
        """Initiate a trigger pulse

        The driver will be instructed to pull the output trigger connector
        high and low as fast as possible via serial communication.

        This method can be used to manually generate a trigger pulse.
        """
        self.set_cycler_trigger(True)
        self.set_cycler_trigger(False)



    
    def set_wavelength_abs(self, wl: float, trigger_pulse: bool = False) -> float:
        """Instructs laser to tune to a given wavelength

        Given a wavelength in nm, instructs the laser to tune to this
        wavelength. This method makes use of the corresponding method
        set_wavelength_abs_idx() to tune to a certain cycler table index.
        See its documentation for detailed information.

        Args:
            wl(int): wavelength in nm to tune the laser to
            trigger_pulse(bool): whether to generate a trigger pulse after
                tuning to the new wavelength

        Returns:
            (float): wavelength the laser will tune to in nm. If the cycler is
            already running, it will return 0.0 instead
        """
        idx = self.get_idx_wavelength(wl)
        return self.set_wavelength_abs_idx(idx, trigger_pulse)

    def set_wavelength_rel(self, wl_delta: float, trigger_pulse: bool = False) -> float:
        """Instructs laser to tune to a new wavelength using a delta wavelength
        w.r.t current wavelength

        Given a delta wavelength in nm, instructs the laser to tune to a new
        wavelength offset from the current wavelength.

        This method makes use of the corresponding method set_wavelength_abs()
        to tune to a certain wavelength in an absolute manner.
        See its documentation for detailed information.

        Args:
            wl_delta(float): wavelength delta in nm to tune the laser to in an offset
                from the current wavelength
            trigger_pulse(bool): whether to generate a trigger pulse after
                tuning to the new wavelength

        Returns:
            (float): absolute wavelength the laser will tune to in nm. If the
            cycler is already running, it will return 0.0 instead
        """
        wl_actual = self.get_wavelength()
        wl_new = wl_actual + wl_delta
        return self.set_wavelength_abs(wl_new, trigger_pulse)

    def set_wavelength_rel_idx(self, idx_delta: int, trigger_pulse: bool = False) -> float:
        """Instructs laser to tune to a new wavelength using a delta cycler
        index w.r.t current cycler table index loaded

        Given a delta index, instructs the laser to load heater voltage values
        of an index with number (current_index + idx_delta) of the cycler table.

        This method makes use of the corresponding method
        set_wavelength_abs_idx() to tune to a certain wavelength in an absolute
        manner. See its documentation for detailed information.

        Args:
            idx_delta(int): cycler table index delta
            trigger_pulse(bool): whether to generate a trigger pulse after
                tuning to the new wavelength

        Returns:
            (float): absolute wavelength the laser will tune to in nm. If the
            cycler is already running, it will return 0.0 instead
        """
        if self._idx_active is None:
            idx_actual = self.get_cycler_index()
        else:
            idx_actual = self._idx_active
        idx_new = idx_actual + idx_delta
        return self.set_wavelength_abs_idx(idx_new, trigger_pulse)




    def set_wavelength_abs_idx(self, idx: int, trigger_pulse: bool = False) -> float:
        """Instructs laser to tune to a given cycler table entry

        Given a cycler table index, instructs the laser to tune the
        corresponding wavelength. This method keeps track of what the current
        mode number and will apply anti-hysteresis mitigations if the requested
        wavelength is at a different mode number.

        After the laser wavelength tunes to this new wavelength, optionally
        (default yes) a trigger pulse is generated.

        NOTE: This functionality requires the steady state operation mode

        Args:
            idx(int): cycler entry index to tune the laser to
            trigger_pulse(bool): whether to generate a trigger pulse after
                tuning to the wavelength

        Returns:
            (float): wavelength the laser will tune to in nm.
        """

        # Apply the heater values from the requested cycler table index
        # self.load_cycler_entry(idx)

        # Alternative approach 1: apply all heater values directly from cycler table
        v_phase = float(self._cycler_table[idx, type(self).cycler_config.PHASE_SECTION])
        self.preload_driver_value(type(self).cycler_config.PHASE_SECTION, v_phase)
        self.preload_driver_value(type(self).cycler_config.RING_LARGE, float(self._cycler_table[idx, type(self).cycler_config.RING_LARGE]))
        self.preload_driver_value(type(self).cycler_config.RING_SMALL, float(self._cycler_table[idx, type(self).cycler_config.RING_SMALL]))
        self.preload_driver_value(type(self).cycler_config.TUNABLE_COUPLER, float(self._cycler_table[idx, type(self).cycler_config.TUNABLE_COUPLER]))
        self.apply_preload_values()

        # Alternative approach 2: only update phase heater directly from cycler table
        # v_phase = float(self._cycler_table[idx, type(self).cycler_config.PHASE_SECTION])
        # self.set_driver_value(type(self).cycler_config.PHASE_SECTION, v_phase)

        self.phase_anti_hyst(v_phase=v_phase)

        # Update the field to keep track of the active index
        self._idx_active = idx


        # Provide a trigger signal to indicate that a new wavelength is set
        if trigger_pulse:
            self.trigger_pulse()
        return self.get_wavelength_idx(idx)





    def phase_anti_hyst(self, v_phase: Optional[float] = None):
        """Perform a phase anti-hysteresis function

        This method instructs the driver to shortly increase the voltage on the phase
        section heater and then decrease it to the original voltage started with.

        This functionality is used to mitigate hysteresis effects and to
        correctly tune the laser to a single mode state. To avoid multi-mode
        operation, this function should be called when switching from one laser
        mode to another.
        
        Args:
            v_phase (float, optional): Phase voltage to use. If None, will get current value.
        """
        if v_phase is None:
            if self._idx_active is None:
                v_phase = self.get_driver_value(type(self).channel_config.PHASE_SECTION)
            else:
                v_phase = float(self._cycler_table[self._idx_active, type(self).cycler_config.PHASE_SECTION])

        offset: float = DEFAULT_ANTI_HYST_V_PHASE_SQUARED
        while offset != 0:
            v_phase_anti_hyst = np.sqrt(np.square(float(v_phase)) + offset)  # V^2
            self.set_driver_value(type(self).channel_config.PHASE_SECTION, v_phase_anti_hyst)
            offset -= 2
            time.sleep(DEFAULT_ANTI_HYST_SLEEP)
        
        self.set_driver_value(type(self).channel_config.PHASE_SECTION, float(v_phase))



            # Different operating modes
    @property
    def operation_mode(self) -> None | OperatingMode:
        """Returns operation mode of the laser

        The operation mode can be one of the following:
            - OperatingMode.MANUAL, for manual operation, referenced by
              integer 0
            - OperatingMode.STEADY, for steady tuning operation, referenced by
              integer 1

        At the start of AtlasLaser initialization, this property is set to None

         Returns:
             (OperatingMode): the operating mode of the laser
        """
        if not self.system_state:
            logger.info("System is off")
        return self._operation_mode

    @operation_mode.setter
    def operation_mode(self, mode: OperatingMode):
        """Sets the operation mode of the laser

        The operation mode can be one of the following:
            - OperatingMode.MANUAL, for manual operation, referenced by
              integer 0
            - OperatingMode.STEADY, for steady tuning operation, referenced by
              integer 1

        When setting the operation mode, the laser will set the appropriate
        settings for the mode operation. See the respective methods
        prepare_manual_mode() and prepare_steady_mode()

        Args:
            mode(OperatingMode): the operating mode
        """

        if mode is OperatingMode.MANUAL:
            self.prepare_manual_mode()
        if mode is OperatingMode.STEADY:
            self.prepare_steady_mode()
        
        # Update the operation mode
        self._operation_mode = mode

    def prepare_manual_mode(self):
        """Prepare the laser for manual operation mode.
        
        In manual mode, the values of the heaters can be manually changed
        without using the cycler table entries.
        """
        logger.info("Manual mode enabled")
        # Any specific setup for manual mode can be added here
        pass

    def prepare_steady_mode(self):
        """Prepare the laser for steady operation mode.
        """
        logger.info("Steady mode enabled")
        self.diode_current = DEFAULT_DIODE_CURRENT  # Set default diode current
        self.tec_target = DEFAULT_TEC_TARGET  # Set default TEC target for steady mode

    def set_heater_manual(self, heater_channel, voltage: float):
        """Set heater voltage manually in manual operating mode.
        
        This method allows direct control of heater voltages when the laser
        is in manual operating mode. This bypasses the cycler table and
        allows for fine-tuned control of laser parameters.
        
        Args:
            heater_channel: The heater channel to control 
            voltage (float): The voltage to set on the heater
            
        Raises:
            OperatingModeError: If not in manual operating mode
        """
        if self._operation_mode != OperatingMode.MANUAL:
            raise OperatingModeError("Manual heater control is only available in manual operating mode.")
        
        self.set_driver_value(heater_channel, voltage)
        logger.info(f"Set heater {heater_channel} to {voltage:.3f}V in manual mode")
