#!/usr/bin/env python
"""
SweptLaser class to communicate with COMET lasers.
Authors: RLK, AVR, SDU
"""

import time
from enum import IntEnum

import numpy as np

from lasers_tlm import TLMLaser

DEFAULT_TEC_TARGET_SWEEP = 25.0
DEFAULT_TEC_TARGET_STEADY = DEFAULT_TEC_TARGET_SWEEP
DEFAULT_DIODE_CURRENT_SWEEP = 280.0
DEFAULT_DIODE_CURRENT_STEADY = 280.0
DEFAULT_CYCLER_INTERVAL = 100
DEFAULT_ANTI_HYST_V_PHASE_SQUARED = 30.0
DEFAULT_ANTI_HYST_SLEEP = 0.02


class OperatingMode(IntEnum):
    """Different operating modes for the COMET

    Attributes:
        SWEEP: For sweeping operation
        STEADY: For steady tuning operation
    """

    SWEEP = 0
    STEADY = 1


class SweptLaser(TLMLaser):
    """Representation and control of COMET lasers

    Inherits from TLMLaser and adds COMET specific functionality, mainly
    focussed on swept laser source operation.
    """

    def __init__(self, address=None, timeout=10.0, path_lut_file=None):
        super().__init__(address, timeout)

        self._operation_mode = None
        self._mode_number = 0
        self._idx_active = None
        self._min_wavelength = None
        self._max_wavelength = None
        self._sweep_step_size = None

        # Settings for different operating modes
        self._tec_target_sweep_mode = DEFAULT_TEC_TARGET_SWEEP
        self._tec_target_steady_mode = DEFAULT_TEC_TARGET_STEADY
        self._diode_current_sweep_mode = DEFAULT_DIODE_CURRENT_SWEEP
        self._diode_current_steady_mode = DEFAULT_DIODE_CURRENT_STEADY

        # Cycler table
        self._cycler_fp = path_lut_file
        if self._cycler_fp is not None:
            self.open_file_cycler_table(self._cycler_fp)

    # Different operating modes
    @property
    def operation_mode(self):
        """Returns operation mode of the laser

        The operation mode can be one of the following:
            - OperatingMode.SWEEP, for sweeping operation, referenced by
              integer 0
            - OperatingMode.STEADY, for steady tuning operation, referenced by
              integer 1

        At the start of SweptLaser initialization, this property is set to None

         Returns:
             (OperatingMode): the operating mode of the laser
        """
        return self._operation_mode

    @operation_mode.setter
    def operation_mode(self, mode: OperatingMode):
        """Sets the operation mode of the laser

        The operation mode can be one of the following:
            - OperatingMode.SWEEP, for sweeping operation, referenced by
              integer 0
            - OperatingMode.STEADY, for steady tuning operation, referenced by
              integer 1

        When setting the operation mode, the laser will set the appropriate
        settings for the mode operation. See the respective methods
        prepare_sweep_mode() and prepare_steady_mode()

        Args:
            mode(OperatingMode): the operating mode
        """

        if mode is OperatingMode.SWEEP:
            self.prepare_sweep_mode()
        if mode is OperatingMode.STEADY:
            self.prepare_steady_mode()

    def reapply_mode_settings(self):
        """Reapplies settings for the current mode

        In the case when settings for a specific operation mode is changed,
        this method is called to ensure the new settings are applied for the
        current mode. Makes use of the prepare_sweep_mode() and
        prepare_steady_mode() methods
        """
        current_mode = self.operation_mode
        if current_mode is OperatingMode.SWEEP:
            self.prepare_sweep_mode()
        if current_mode is OperatingMode.STEADY:
            self.prepare_steady_mode()

    # Different operating mode settings
    @property
    def tec_target_sweep_mode(self) -> float:
        """Gives the TEC target temperature setting to use during sweeping
        operation

        Returns:
            (float): TEC target temperature in °C
        """
        return self._tec_target_sweep_mode

    @tec_target_sweep_mode.setter
    def tec_target_sweep_mode(self, tec_target: float) -> None:
        """Sets the TEC target temperature setting to use during sweeping
        operation

        Will also call the reapply_mode_settings() method to ensure new settings
        are directly applied for the current mode that is enabled.

        Args:
            tec_target: TEC target temperature in °C
        """
        self._tec_target_sweep_mode = tec_target
        self.reapply_mode_settings()

    @property
    def diode_current_sweep_mode(self) -> float:
        """Gives the diode current setting to use during sweeping operation

        Returns:
            (float): diode current in mA
        """
        return self._diode_current_sweep_mode

    @diode_current_sweep_mode.setter
    def diode_current_sweep_mode(self, diode_current: float) -> None:
        """Sets the diode current setting to use during sweeping operation

        Will also call the reapply_mode_settings() method to ensure new settings
        are directly applied for the current mode that is enabled.

        Args:
            diode_current: diode current in mA
        """
        self._diode_current_sweep_mode = diode_current
        self.reapply_mode_settings()

    @property
    def tec_target_steady_mode(self) -> float:
        """Gives the TEC target temperature setting to use during steady tune
        operation

        Returns:
            (float): TEC target temperature in °C
        """
        return self._tec_target_steady_mode

    @tec_target_steady_mode.setter
    def tec_target_steady_mode(self, tec_target: float) -> None:
        """Sets the TEC target temperature setting to use during steady tune
        operation

        Will also call the reapply_mode_settings() method to ensure new settings
        are directly applied for the current mode that is enabled.

        Args:
            tec_target: TEC target temperature in °C
        """
        self._tec_target_steady_mode = tec_target
        self.reapply_mode_settings()

    @property
    def diode_current_steady_mode(self) -> float:
        """Gives the diode current setting to use during steady tune operation

        Returns:
            (float): diode current in mA
        """
        return self._diode_current_steady_mode

    @diode_current_steady_mode.setter
    def diode_current_steady_mode(self, diode_current: float) -> None:
        """Sets the diode current setting to use during steady tune operation

        Will also call the reapply_mode_settings() method to ensure new settings
        are directly applied for the current mode that is enabled.

        Args:
            diode_current: diode current in mA
        """
        self._diode_current_steady_mode = diode_current
        self.reapply_mode_settings()

    @property
    def _is_lut_prepared(self):
        """Checks whether the LUT or cycler table is prepared

        The cycler table loaded in the Python code with open_file_cycler_table()
        does not contain all columns for operation of the swept source laser.

        This property returns a simple check if the internal cycler table is
        already parsed and adapted for new columns, by checking the number of
        columns of the cycler table and comparing it to the number of columns
        needed in the eventual cycler table.

        Returns:
            (bool): whether internal cycler table has correct number of columns
        """
        return (self._cycler_table is not None) and (
            self._cycler_table.shape[-1] == len(type(self).cycler_config)
        )

    def _prepare_lut(self, force=False):
        """Updates PC loaded cycler table to be functional for operation

        The original cycler table loaded from the PC with open_file_cycler_table()
        only has 6 columns, namely:
            0 heater voltage 1, phase section voltage
            1 heater voltage 2, ring large voltage
            2 heater voltage 3, ring small voltage
            3 heater voltage 4, tunable coupler voltage
            4 wavelength, the corresponding wavelength of cycler entry
            5 mode hop, where a 1 is to indicate presence and 0 absence of mode hop

        For correct sweeping operation, extra information is needed, which is added
        to the internal _cycler_table by addition of two new columns:
            6 index, the original 0-based index of the entries
            7 mode index, an index number representing the mode number

        The mode number in above context is a consecutive series of cycler table entries
        where all heater voltages change in a monotone, continuous fashion.

        Besides adding the necessary columns, also determines and sets the minimum and
        maximum wavelengths found and supported by the cycler table, and the step size
        or wavelength resolution of the cycler table.

        Args:
            force (bool, default False): whether to always perform these steps even
            when the internal cycler table already has the correct number of columns
        """
        # Exit out early if current cycler table already has all columns
        if self._is_lut_prepared:
            print("Cycler table already has added columns.")
            if not force:
                return

        # Copy of original cycler table
        org_cycler_table = self._cycler_table
        # Preallocate new cycler table with size corresponding to new columns
        new_cycler_table = np.zeros(
            (self._cycler_table_length, len(type(self).cycler_config))
        )

        # Add original index numbers
        idx_array = np.arange(self._cycler_table_length)

        # Determine mode numbers
        # Determine differences in tc voltages
        mh_array = org_cycler_table[:, type(self).cycler_config.MODE_HOPS]
        mh_diff = np.diff(mh_array, prepend=mh_array[0])
        # Boolean array of look-up table where mode hops occur
        mode_hops = mh_diff == 1.0

        mode_array = np.zeros((self._cycler_table_length, 1))
        # Calculate mode numbers based on points where mode hops occur
        for ii, is_mode_hop in enumerate(mode_hops):
            if is_mode_hop:
                mode_array[ii:] += 1

        # Compose new cycler table with added columns
        # First 5 columns are original cycler table
        new_cycler_table[:, : type(self).cycler_config.ENTRY_INDEX] = org_cycler_table[
            :, : type(self).cycler_config.ENTRY_INDEX
        ]
        # Add index for entry numbers
        new_cycler_table[:, type(self).cycler_config.ENTRY_INDEX] = idx_array
        # Add mode number index
        new_cycler_table[:, type(self).cycler_config.MODE_INDEX] = mode_array[:, 0]

        # Update min and max wavelengths
        self._min_wavelength = new_cycler_table[-1, type(self).cycler_config.WAVELENGTH]
        self._max_wavelength = new_cycler_table[0, type(self).cycler_config.WAVELENGTH]
        # Update step size/wavelength resolution number
        wvl_mask = new_cycler_table[:, type(self).cycler_config.MODE_HOPS] == 0
        wvl_array = new_cycler_table[wvl_mask, type(self).cycler_config.WAVELENGTH]
        wvl_diff = np.diff(wvl_array)
        self._sweep_step_size = np.around(np.abs(wvl_diff[0]), decimals=4)

        # Save new table to private attribute
        self._cycler_table = new_cycler_table

    @property
    def min_wavelength(self) -> float:
        """The minimum wavelength supported by the PC loaded cycler table

        Returns:
            (float): minimum wavelength to use in nm
        """
        return self._min_wavelength

    @property
    def max_wavelength(self) -> float:
        """The maximum wavelength supported by the PC loaded cycler table

        Returns:
            (float): maximum wavelength to use in nm
        """
        return self._max_wavelength

    def open_file_cycler_table(self, path_cycler_table):
        """Open and load/read csv cycler table file

        This method calls the parent class TLMLaser().open_file_cycler_table(), and
        applies the necessary additions as described in _prepare_lut().
        See these methods for further documentation.

        Args:
            path_cycler_table(str | Path): filepath of cycler table / LUT file to load
        """
        super().open_file_cycler_table(path_cycler_table)
        self._prepare_lut()

    @property
    def sweep_stepsize(self) -> float:
        """The step size or wavelength resolution of a sweep in nm

        This is calculated from the cycler table after preparation in
        _prepare_lut()

        Returns:
            (float): step size or wavelength resolution in nm
        """
        if not self._is_lut_prepared:
            return None
        return self._sweep_step_size

    def _is_span_correct(self, idx_start: int, idx_end: int) -> bool:
        """Checks if the indices for a span for a sweep are correct

        For a sweep a subset of the cycler table can be used to sweep through.
        This method is a simple check if the end index is greater than the start index.
        Args:
            idx_start(int): start index of entry to sweep through
            idx_end(int): end index of entry to sweep through

        Returns:
            (bool): whether end index is greater than start index
        """
        correct = idx_end > idx_start
        if not correct:
            print(f"Indices for span are not correct. Given start:{idx_start:d} end:{idx_end:d}.\nNeeded start < end.")
        return correct

    def _update_mode_number(self, idx: int | None = None):
        """Updates and returns mode number

        The mode number is required to determine if anti-hysteresis mitigation
        is necessary. When changing/tuning to a wavelength of a different mode,
        this is the case.

        This method returns the mode number of the current index loaded/applied by
        the laser if no index argument is given. Otherwise, when an index integer
        is given, it returns the mode number of this cycler entry.
        The mode number is saved to private attribute _mode_number for internal
        reference.

        Args:
            idx(int | None, default None): cycler entry index to give mode number for.
                If none, will be set to the currently loaded cycler entry index.

        Returns:
            (int): mode number of the corresponding cycler entry index
        """
        if idx is None:
            idx = self.get_cycler_index()
        self._mode_number = self.get_mode_number_idx(idx)
        return self._mode_number

    def get_mode_number_idx(self, idx: int) -> int:
        """Gets the mode number for a specific cycler table entry

        Args:
            idx(int): cycler entry index to get mode number for

        Returns:
            (int): the mode number of the entry
        """
        return int(self._cycler_table[idx, type(self).cycler_config.MODE_INDEX])

    def get_idx_mode_hop(self, mode_number: int) -> int:
        """Gets the index of cycler table entry of mode hop for a mode number

        This method returns the entry corresponding to the one where a mode
        hop happens for the given mode number.

        Args:
            mode_number(int): the mode number to get the starting mode hop entry for

        Returns:
            (int): the cycler entry index corresponding to where a mode hop happens,
                given the mode number
        """
        return np.argmax(self._cycler_table[:, type(self).cycler_config.MODE_INDEX] == mode_number)

    @property
    def system_state(self) -> bool:
        """Gets the system state.

        Override of Laser().system_state, please refer to its documentation

        Returns:
            bool: The system state.
        """
        return bool(int(self.query("SYST:STAT?")))

    @system_state.setter
    def system_state(self, value: bool) -> None:
        """Sets the system state.

        Override of Laser().system_state, please refer to its documentation.
        Additionally, resets the operation_mode to None.

        Args:
            value (bool): The system state to be set.
        """
        if type(value) is not bool:
            print("ERROR: given value is not a boolean")
            return
        if not value:
            self._operation_mode = None
            self._mode_number = 0
        self.write(f"SYST:STAT {value:d}")

    def get_wavelength_idx(self, idx: int) -> float:
        """Gets wavelength corresponding to cycler entry index

        Args:
            idx(int): index of cycler entry to get wavelength value for

        Returns:
            (float): wavelength in nm
        """
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
        # Only look for entries that have no mode hop, which is indicated by
        # cycler_config.MODE_HOPS column = 0.0
        no_hops_mask = np.isclose(
            self._cycler_table[:, type(self).cycler_config.MODE_HOPS], 0.0
        )
        cycler_table_no_hops = self._cycler_table[no_hops_mask, :]

        # Search for the best look-up table entry, which is closest to the requested wavelength
        wl_array = cycler_table_no_hops[:, type(self).cycler_config.WAVELENGTH]
        wl_min = np.min(wl_array)
        if wavelength < wl_min:
            print(f"Input wavelength {wavelength:.3f} smaller than minimum {wl_min:.3f}.")
            wavelength = wl_min
        wl_max = np.max(wl_array)
        if wavelength > wl_max:
            print(f"Input wavelength {wavelength:.3f} larger than maximum {wl_max:.3f}.")
            wavelength = wl_max
        _idx_no_hops = np.argmin(np.abs(wl_array - wavelength))
        best_entry = cycler_table_no_hops[_idx_no_hops, :]
        return int(best_entry[type(self).cycler_config.ENTRY_INDEX])

    def prepare_sweep_mode(self):
        """Prepares the laser for sweeping operation

        It does this by applying the following settings:
            - the TEC temperature target, saved in _tec_target_sweep_mode
            - the diode current, saved in _diode_current_sweep_mode
            - the cycler interval, saved in cycler_interval or otherwise,
              when not set before the DEFAULT_CYCLER_INTERVAL
            - finally it will set the laser to tune to a wavelength in the
              middle of the cycler table (to come to a thermal state more
              akin to when during sweeping operation).

        The SweptLaser object's internal operating mode will also be updated
        to be in OperatingMode.SWEEP.
        """
        self.tec_target = self._tec_target_sweep_mode
        self.diode_current = self._diode_current_sweep_mode
        # Cycler interval is changed with another property setter, however, if not set
        # use default cycler interval
        if not self.cycler_interval:
            self.cycler_interval = DEFAULT_CYCLER_INTERVAL
        # Update internal state
        self._operation_mode = OperatingMode.SWEEP

        # Pick an entry in the middle of the cycler table
        self.set_wavelength_abs((self.max_wavelength + self.min_wavelength) / 2)

    def prepare_steady_mode(self):
        """Prepares the laser for steady tuning operation

        Steady tuning operation in this case means non-sweeping: settings
        applied when tuning to a certain wavelength will be held.

        It prepares for steady mode by applying the following settings:
            - the TEC temperature target, saved in _tec_target_steady_mode
            - the diode current, saved in _diode_current_steady_mode

        The SweptLaser object's internal operating mode will also be updated
        to be in OperatingMode.STEADY.
        """
        self.tec_target = self._tec_target_steady_mode
        self.diode_current = self._diode_current_steady_mode
        # Update internal state
        self._operation_mode = OperatingMode.STEADY

    def trigger_pulse(self):
        """Initiate a trigger pulse

        The driver will be instructed to pull the output trigger connector
        high and low as fast as possible via serial communication.

        This method can be used to manually generate a trigger pulse.
        """
        self.set_cycler_trigger(True)
        self.set_cycler_trigger(False)

    def phase_anti_hyst(self):
        """Perform a phase anti-hysteresis function

        This method instructs the driver to shortly increase the voltage on the phase
        section heater and then decrease it to the original voltage started with.

        This functionality is used to mitigate hysteresis effects and to
        correctly tune the laser to a single mode state. To avoid multi-mode
        operation, this function should be called when switching from one laser
        mode to another.
        """
        if self._idx_active is None:
            v_phase = self.get_driver_value(type(self).channel_config.PHASE_SECTION)
        else:
            v_phase = self._cycler_table[self._idx_active, type(self).cycler_config.PHASE_SECTION]
        v_phase_anti_hyst = np.sqrt(np.square(v_phase) + DEFAULT_ANTI_HYST_V_PHASE_SQUARED)  # V^2, hysteresis function
        self.set_driver_value(type(self).channel_config.PHASE_SECTION, v_phase_anti_hyst)
        time.sleep(DEFAULT_ANTI_HYST_SLEEP)
        self.set_driver_value(type(self).channel_config.PHASE_SECTION, v_phase)

    def phase_correction_sweep_to_steady(self):
        if self._idx_active is None:
            v_phase = self.get_driver_value(type(self).channel_config.PHASE_SECTION)
            v_ring_large = self.get_driver_value(type(self).channel_config.RING_LARGE)
            v_ring_small = self.get_driver_value(type(self).channel_config.RING_SMALL)
        else:
            v_phase = self._cycler_table[self._idx_active, type(self).cycler_config.PHASE_SECTION]
            v_ring_large = self._cycler_table[self._idx_active, type(self).cycler_config.RING_LARGE]
            v_ring_small = self._cycler_table[self._idx_active, type(self).cycler_config.RING_SMALL]
        v_squared_rings = np.square(v_ring_large) + np.square(v_ring_small)
        v_squared_phase = np.square(v_phase)
        v_squared_phase_correction = - 23.40 + 3.0 + 0.227 * v_squared_rings  # for 100 ms cycler interval
        v_squared_phase_new = v_squared_phase + v_squared_phase_correction
        if v_squared_phase_new < 0.0:
            v_squared_phase_new = 0.0
        v_phase_new = np.sqrt(v_squared_phase_new)
        print(f"Phase correction sweep {v_phase:.4f} to steady {v_squared_phase_new:.4f}")

        self.set_driver_value(type(self).channel_config.PHASE_SECTION, v_phase_new)

    def _calc_runtime(self, idx_start: int, idx_end: int, num_sweeps: int) -> float:
        """Calculates and returns the estimated runtime of a sweep

        The runtime of a sweep operation is calculated based on the span of
        the sweep, i.e., the start and end indices, the cycler time interval, and
        the amount of full cycles to perform.

        Args:
            idx_start(int): start index for sweep
            idx_end(int): end index for sweep
            num_sweeps(int): number of full cycles/sweeps

        Returns:
            (float): runtime of sweeping operation in seconds
        """
        return (idx_end - idx_start) * self.cycler_interval * 1e-6 * num_sweeps

    def sweep_idx(
        self,
        idx_start: int,
        idx_end: int,
        num_sweeps: int = 0,
        align_start_with_hop: bool = False,
    ):
        """Performs sweep operation based on cycler table indices

        This method instructs the laser to perform a sweep operation, which is
        defined by cycler table entry indices and the amount of full
        sweeps/cycles to make.

        If num_sweeps == 0, the laser will be instructed to keep sweeping indefinitely,
        only to be stopped by manual sweep abortion (see turn_off_cycler() method).

        It will return the wavelengths that will be swept through in the form of a
        numpy array, and the runtime in seconds, if not indefinitely.

        Optionally, it can be requested that the sweep will always start at the
        beginning of a mode, using the align_start_with_hop flag.

        NOTE: Sweeps will always be performed in the direction from longer wavelengths
        to shorter wavelengths.

        Args:
            idx_start(int): start index for sweep operation
            idx_end(int): stop index for sweep operation
            num_sweeps(int): number of full sweeps/cycles to perform. If 0, will
                sweep indefinitely
            align_start_with_hop(bool, default False): whether to change the start
                index to align with a mode hop

        Returns:
            - If cycler is already running: None, None
            - If given indices are not a correct span: None, None
            - If sweep is indefinite (num_sweeps=0):
                array of wavelengths to sweep over in nm, runtime=None
            - If numbered sweeps is given (num_sweeps!=0):
                array of wavelengths to sweep over in nm, runtime in seconds
        """
        # Exit out early, if sweep is already running
        if self.cycler_running:
            return None, None
        # If span numbers are not correct.
        if not self._is_span_correct(idx_start, idx_end):
            return None, None

        # Optional to have start wavelength align with a mode hop
        if align_start_with_hop:
            mode_number_to_set = self.get_mode_number_idx(idx_start)
            new_idx_start = self.get_idx_mode_hop(mode_number_to_set)
            if new_idx_start != idx_start:
                print("Optimize sweep by selecting starting wavelength at mode hop.")
                print(f"Index start: {idx_start=:d}, {new_idx_start=:d}.")
                print(
                    f"Wavelength start: original {self.get_wavelength_idx(idx_start):.3f}, new {self.get_wavelength_idx(new_idx_start):.3f}."
                )
            idx_start = new_idx_start

        # Calculate runtime
        runtime = (
            None
            if (num_sweeps == 0)
            else self._calc_runtime(idx_start, idx_end, num_sweeps)
        )

        # Instruct laser
        self.set_cycler_span(idx_start, idx_end)
        self.turn_on_cycler(num_sweeps)
        self._update_mode_number(idx_end)

        # Return what is swept through, and runtime
        return self._cycler_table[idx_start: (idx_end + 1), type(self).cycler_config.WAVELENGTH], runtime

    def sweep(
        self,
        wl_start: float,
        wl_end: float,
        num_sweeps: int = 0,
        align_start_with_hop: bool = False,
    ):
        """Performs sweep operation based on start and stop wavelength

        This method instructs the laser to perform a sweep operation, which is
        defined by a start and stop wavelength in nm and the amount of full
        sweeps/cycles to make.

        Makes use of sweep_idx() method, reference it for more detailed
        documentation.

        Args:
            wl_start(float): starting wavelength for a cycle/sweep in nm, must
                be greater than stopping wavelength wl_end
            wl_end(float): stopping wavelength for a cycle/sweep in nm, must
                be smaller than starting wavelength wl_start
            num_sweeps(int): number of full sweeps/cycles to perform. If 0, will
                sweep indefinitely
            align_start_with_hop(bool, default False): whether to change the start
                index to align with a mode hop

        Returns:
            - If cycler is already running: None, None
            - If given indices are not a correct span: None, None
            - If sweep is indefinite (num_sweeps=0):
                array of wavelengths to sweep over in nm, runtime=None
            - If numbered sweeps is given (num_sweeps!=0):
                array of wavelengths to sweep over in nm, runtime in seconds
        """
        idx_start = self.get_idx_wavelength(wl_start)
        idx_end = self.get_idx_wavelength(wl_end)

        # Return what is swept through, and runtime
        wls, runtime = self.sweep_idx(
            idx_start, idx_end, num_sweeps, align_start_with_hop
        )
        return wls, runtime

    def sweep_full(self, num_sweeps: int = 0):
        """Performs sweep operation over the entire cycler table, i.e.,
        calibrated wavelengths

        This method makes use of the sweep_idx() method, see it for detailed
        documentation.

        Args:
            num_sweeps(int): number of sweeps/cycles to perform. If 0, will
                sweep indefinitely

        Returns:
            - If cycler is already running: None, None
            - If sweep is indefinite (num_sweeps=0):
                full array of wavelengths to sweep over in nm, runtime=None
            - If numbered sweeps is given (num_sweeps!=0):
                full array of wavelengths to sweep over in nm, runtime in seconds
        """
        wls, runtime = self.sweep_idx(0, self._cycler_table_length - 1, num_sweeps)
        return wls, runtime

    def sweep_abort(self) -> None:
        """Abort a running sweep

        Will update the internal mode number attribute after the sweep is stopped
        """
        self.turn_off_cycler()
        self._update_mode_number()

    def get_wavelength(self) -> float:
        """Gets and returns the current wavelength the laser is tuned to

        Since the driver keeps track of the index of the last applied cycler
        table entry, this can be used to determine the corresponding wavelength
        the laser is at, based from the calibrated values in the cycler table.

        Returns:
            (float): current wavelength in nm
        """
        idx = self.get_cycler_index()
        # Update the field to keep track of the active index
        self._idx_active = idx
        # Request the wavelength corresponding to the active index
        wavelength = self.get_wavelength_idx(idx)
        return wavelength

    def set_wavelength_abs_idx(self, idx: int, trigger_pulse: bool = True) -> float:
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
            (float): wavelength the laser will tune to in nm. If the cycler is
            already running, it will return 0.0 instead
        """
        # Exit out early, if sweep is already running
        if self.cycler_running:
            return 0.0

        # Apply the heater values from the requested cycler table index
        self.load_cycler_entry(idx)
        # Update the field to keep track of the active index
        self._idx_active = idx

        # Perform a phase correction for static mode, since the phase is calibrated for sweep mode.
        self.phase_correction_sweep_to_steady()

        # Perform a phase anti-hysteresis function when the set mode number is different from the previously set one.
        mode_number_new = self.get_mode_number_idx(idx)
        if mode_number_new != self._mode_number:
            print(f"Phase anti-hysteresis required due to switching to mode number {mode_number_new:d}")
            self.phase_anti_hyst()
        self._mode_number = mode_number_new
        # Provide a trigger signal to indicate that a new wavelength is set
        if trigger_pulse:
            self.trigger_pulse()
        return self.get_wavelength_idx(idx)

    def set_wavelength_abs(self, wl: float, trigger_pulse: bool = True) -> float:
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

    def set_wavelength_rel(self, wl_delta: float, trigger_pulse: bool = True) -> float:
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

    def set_wavelength_rel_idx(
        self, idx_delta: int, trigger_pulse: bool = True
    ) -> float:
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
        idx_actual = self.get_cycler_index()
        idx_new = idx_actual + idx_delta
        return self.set_wavelength_abs_idx(idx_new, trigger_pulse)
