#!/usr/bin/env python
"""
TLMLaser class to communicate with Tunable Laser Module (TLM).
Authors: RLK, AVR, SDU

Date: 2024-10-22
"""

from pathlib import Path
from packaging.version import Version
import csv
from enum import IntEnum
import numpy as np
from lasers import Laser
from lasers import logger

# Constants
TLM_FEEDBACK_SOURCES = {
    1: "PD 0 -- MEAS:M? 0",
    2: "PD 1 -- MEAS:M? 1",
    3: "Heater driver Temp -- SYST:TEMP:NSEL 0",
    4: "Enclosure Temp -- SYST:TEMP:NSEL 1",
    5: "TEC Temp -- TEC:TEMP?",
}
TLM_FEEDBACK_DESTINATIONS = {
    1: "TEC target -- TEC:TTGT",
    2: "Diode current -- LSR:ILEV",
    3: "Phase heater -- DRV:D 0",
    4: "Small ring -- DRV:D 1",
    5: "Large ring -- DRV:D 2",
    6: "Dummy heater -- DRV:D 3",
}


class HeaterChannelTLM(IntEnum):
    PHASE_SECTION = 0
    RING_LARGE = 2
    RING_SMALL = 1
    TUNABLE_COUPLER = 3


CYCLER_SIZELIMIT_TLM = 14336


class TLMLaser(Laser):
    """TLM Laser class for Chilas lasers."""

    model = "Chilas TLM Laser"
    channel_config = HeaterChannelTLM

    def __init__(self, address=None, timeout=10.0):
        super().__init__(address, timeout)

        # Cycler private attributes
        self._eeprom_size = None
        self._cycler_fp = None
        self._cycler_table = None
        self._cycler_table_length = None
        self._cycler_interval = None

    @property
    def shutdown_reason(self) -> str:
        """Latest reason for shutdown of the laser

        Can be either ones off:
            - User initiated
            - Laser interlock is open
            - Incorrect input voltage
            - Analog voltage failure
            - Heater voltage failure
            - Reference voltage failure
            - TEC reference voltage failure
            - TEC temperature control failure
            - Unknown violation
            - Heater drivers overheated

        Returns:
            (str): shutdown reason
        """
        return self.query("SYST:SDRN?")

    # Non TEC temperatures
    @property
    def temp_enclosure(self) -> float:
        """Temperature of the enclosure in °C

        Returns the enclosure temperature in °C. The driver has multiple
        sensors that can be read, the enclosure temperature being referenced by
        number 1. If the enclosure temperature is not the current sensor
        selected, then this method will instruct the driver first to use the
        correct sensor number.

        Returns:
            (float): enclosure temperature in °C
        """
        now_selected = int(self.query("SYST:TEMP:NSEL?"))
        if now_selected != 1:
            self.write("SYST:TEMP:NSEL 1")
        return float(self.query("SYST:TEMP:TEMP?"))

    @property
    def temp_electronics(self) -> float:
        """Temperature of the electronics in °C

        Returns the electronics temperature in °C. The driver has multiple
        sensors that can be read, the electronics temperature being referenced
        by number 0. If the electronics temperature is not the current sensor
        selected, then this method will instruct the driver first to use the
        correct sensor number.

        Returns:
            (float): electronics temperature in °C
        """
        now_selected = int(self.query("SYST:TEMP:NSEL?"))
        if now_selected != 0:
            self.write("SYST:TEMP:NSEL 0")
        return float(self.query("SYST:TEMP:TEMP?"))

    # PD readout
    def get_amount_meas_channels(self) -> int:
        """Amount of measurement channels

        Returns the amount of measurement channels of the driver.
        Currently, the measurement channels are used for reading out the onboard photodiode (PD) sensors.

        Returns:
            (int): the number of measurement channels
        """
        return int(self.query("MEAS:COUN?"))

    def get_meas_unit(self, channel: int) -> str:
        """Gives unit for specific measurement channel

        Can be either one of:
            - uA

        Args:
            channel(int): measurement channel number

        Returns:
            (str): unit of measurement channel
        """
        return self.query(f"MEAS:UNIT? {channel}")

    def get_meas_value(self, channel: int) -> float:
        """Gives measured value for specific measurement channel

        Args:
            channel(int): measurement channel number

        Returns:
            (float): value (readout) of measurement channel
        """
        return float(self.query(f"MEAS:M? {channel}"))

    # Helper functions
    def write_laser_settings(self, fp: Path):
        """Writes out the current laser settings to an external file

        Given a filepath, the laser settings including the diode current, TEC temperature target,
        phase section, first ring, second ring and tunable coupler heater voltages are written out as a text file.

        The file is created if it does not exist yet, otherwise it is overwritten.

        The formatting is csv with ',' as delimiter, specifically:
            - Diode current (mA),<diode current>
            - TEC target (degC),<TEC target temperature>
            - Phase section (V),<phase section heater voltage>
            - Ring large (V),<first ring heater voltage>
            - Ring small (V),<second ring heater voltage>
            - Tunable coupler (V),<tunable coupler heater voltage>

        Args:
            fp(pathlib.Path): external file to write to
        """
        current = self.diode_current
        tec_tgt = self.tec_target
        ps = self.get_driver_value(type(self).channel_config.PHASE_SECTION)
        rl = self.get_driver_value(type(self).channel_config.RING_LARGE)
        rs = self.get_driver_value(type(self).channel_config.RING_SMALL)
        tc = self.get_driver_value(type(self).channel_config.TUNABLE_COUPLER)

        settings_dict = {
            "Diode current (mA)": current,
            "TEC target (degC)": tec_tgt,
            "Phase section (V)": ps,
            "Ring large (V)": rl,
            "Ring small (V)": rs,
            "Tunable coupler (V)": tc,
        }
        with fp.open(mode="w", encoding="utf-8") as fout:
            for key, value in settings_dict.items():
                _ = fout.write(f"{key},{value}\n")

    # Cycler commands
    def turn_on_cycler(self, num_sweeps: int = 0):
        """Turns on the cycler of the laser driver

        Calling this method the driver is instructed to perform cycling operation, either continuously
        or for a fixed number of times, where it cycles through a series of settings for heater values.
        Effectively this will tune the operating wavelength of the laser.

        A number of sweeps of '0' corresponds to turning on the cycler for indefinite amount of time, otherwise
        it corresponds to the number of complete cycles to perform.

        This method only starts the cycler. For other cycler related settings, such as
        the time interval to cycle between entries or the span of entries to cover, see other methods.

        Args:
            num_sweeps (int): the number
        """
        if num_sweeps < 0:
            logger.error("Error, number of sweeps needs to be 0 or positive integer.")
            raise ValueError
        if num_sweeps == 0:
            logger.info("Turning on cycler, running infinite times")
        if num_sweeps > 0:
            logger.info(f"Turning on cycler, running {num_sweeps:d} times")
        self.write(f"DRV:CYC:RUN {num_sweeps:d}")

    def turn_off_cycler(self):
        """Turns off the cycler of the laser driver

        Calling this method the driver is instructed to stop cycling operation if this were the case.
        If the driver is not cycling, this method does nothing.
        """
        logger.info("Turning off cycler")
        self.write("DRV:CYC:ABRT")

    @property
    def cycler_running(self) -> bool:
        """Indicates if the cycler is currently running

        Returns:
            (bool): if the cycler is running
        """
        return bool(int(self.query("DRV:CYC:RUN?")))

    def get_cycler_index(self) -> int:
        """Returns the current or latest index from the cycler table

        When the cycler is running it continuously runs through (a subset of) entries
        of the cycler table. This index method returns the latest known index/position
        of the cycler table being used.

        Returns:
            (int): index of currently or latest known cycler table entry applied
        """
        return int(self.query("DRV:CYC:CPOS?"))

    # Cycler <-> Heaters
    def load_cycler_entry(self, entry: int):
        """Applies heater values from a specific cycler table entry

        When executing this method the voltages in a cycler entry or row,
        indicated by the required entry argument, will be applied to the
        heaters. These are the four voltages corresponding in a cycler entry or
        row which correspond to the channel configuration of the driver and
        stored in the enum HeaterChannelTLM.

        Args:
            entry(int): index number of the cycler entry/row to apply to heater actuators
        """
        self.write(f"DRV:CYC:LOAD {entry:d}")

    def save_cycler_entry(self, entry: int):
        """Saves currently active heater values to specific cycler table entry

        When executing this method the voltages currently active for the
        various heater actuators are saved to an entry of the cycler table. The
        row written to is referenced by the entry argument.

        Args:
            entry(int): index number of the cycler entry/row to write heater voltages to
        """
        self.write(f"DRV:CYC:SAVE {entry:d}")

    # TLC: Must be at least 200 us (5 kHz)
    # TLM: Must be between 20 us (50 kHz) and 50 ms (20 Hz)
    @property
    def cycler_interval(self) -> int:
        """Gives the time interval set for the cycler in microseconds

        This property returns the time interval used when cycling over subsequent
        cycler entries. The response is an integer for the amount of microseconds.

        Returns:
            (int): amount of microseconds between successive entries when in cycling operation
        """
        if self._cycler_interval is None:
            self._cycler_interval = int(self.query("DRV:CYC:INT?"))
        return self._cycler_interval

    @cycler_interval.setter
    def cycler_interval(self, interval: int):
        """Sets the time interval for the cycler in microseconds

        Using this setter the time interval used when cycling over subsequent
        cycler entries can be changed.

        The default cycler interval is set to 100 microseconds, or a rate of 10kHz.
        Respective minimum and maximum values for the TLM driver are 20 us and 50000 us,
        corresponding to rates of maximum 50 kHz and minimum of 20 Hz.

        Args:
            interval(int): amount of microseconds between successive entries when in cycling operation
        """
        self.write(f"DRV:CYC:INT {interval:d}")
        self._cycler_interval = interval

    # Cycler I/O
    def open_file_cycler_table(self, path_cycler_table: str | Path):
        """Open and load/read csv cycler table file

        This method opens a file given a path to a cycler table file, otherwise known as
        a LookUpTable (LUT). It is read and saved to a private attribute _cycler_table.

        The format of the csv file is four entries per row, with ';' delimiter.
        If the filepath has more rows than the TLM driver can store in EEPROM, the
        numpy array is clipped to this maximum number of entries (CYCLER_SIZELIMIT_TLM).
        Also saves the length of the cycler table or the number of attributes to the
        private attribute _cycler_table_length

        Args:
            path_cycler_table(str | Path): filepath of cycler table / LUT file to load
        """
        logger.info("Loading cycler table from file")
        try:
            with open(path_cycler_table, "r") as file:
                dialect = csv.Sniffer().sniff(file.read())
                file.seek(0)
                reader = csv.reader(file, dialect)
                cycler_table = np.array(list(reader)).astype(float)
        except Exception as e:
            logger.error("Non-standard lookup table - ", e)

        # Clip length of table if larger than EEPROM
        table_length = len(cycler_table)
        if table_length > CYCLER_SIZELIMIT_TLM:
            logger.warning("Warning: loaded cycler table is longer than what is max holdable!")
            logger.warning(f"\tOpened table length {table_length:d}, clipping up to {CYCLER_SIZELIMIT_TLM:d}")
            cycler_table = cycler_table[:CYCLER_SIZELIMIT_TLM, :]
            table_length = len(cycler_table)

        self._cycler_table = cycler_table
        self._cycler_table_length = table_length

    def save_file_cycler_table(self, path_cycler_table: Path):
        """Saves currently loaded cycler table to an external csv file.

        Format is ';' delimiter.
        Args:
            path_cycler_table(Path): path to file to write out to
        """
        logger.info("Saving cycler table to file")
        try:
            np.savetxt(
                fname=path_cycler_table,
                X=self._cycler_table[:, :],
                fmt="%.4f",
                delimiter=";",
            )
        except Exception as e:
            logger.error("Error ", e)

    def put_cycler_entry(self, entry: int, value1: float, value2: float, value3: float, value4: float, repetition: bool = False):
        """Sets all heater voltages of a cycler entry

        The cycler table entry referenced by the entry index integer will be
        set with the four given input voltages.
        
        NOTE: This is done in volatile memory of the driver, it will not
        survive a power cycle unless written to persistent storage.
        See method store_cycler       
        
        Args:
            entry(int): integer index of the entry to set heater voltages for
            value1(float): first heater voltage
            value2(float): second heater voltage
            value3(float): third heater voltage
            value4(float): fourth heater voltage
            repetition: command text can be shortened when repeated
        """
        if repetition:
            self.write(f"; {entry:d} {value1:.4f} {value2:.4f} {value3:.4f} {value4:.4f}")
        else:
            self.write(f"DRV:CYC:PUT {entry:d} {value1:.4f} {value2:.4f} {value3:.4f} {value4:.4f}")

    def get_cycler_entry(self, entry: int) -> tuple[float, float, float, float]:
        """Gets all heater voltages of a cycler entry in driver memory

        Returns all heater voltages of a specific cycler entry as currently
        in use, i.e., as loaded in the driver memory.

        Args:
            entry(int): integer index of entry to get heater voltages from

        Returns:
            (tuple[float,float,float,float]): a tuple of size four with
            the heater voltages for respective heater channels 1 to 4
        """
        resp = self.query(f"DRV:CYC:GET? {entry:d}")
        values_list = [float(value) for value in resp.split(" ")]
        return tuple(values_list)

    def get_all_cycler_entries(self):
        """Gets complete cycler table currently loaded in driver memory

        Returns entire cycler table as currently loaded in memory. Makes
        use of method get_cycler_entry to iterate over entire size of ???
        Return type is a numpy array of size (EEPROM_SIZE, 4)

        Returns:
            (np.array[size(EEPROM_SIZE, 4), dtype=float]):
        """
        cycler_table = np.zeros((self._eeprom_size, 4))
        for ii in range(self._eeprom_size):
            cycler_table[ii, :] = self.get_cycler_entry(ii)
        return cycler_table

    def set_cycler_entry(self, entry: int, heater_number: int, heater_value: float):
        """Sets single specific heater voltage of a cycler entry in driver memory

        Similar to method put cycler entry, however, only stores a single heater voltage
        into the cycler row, instead of an entire row.

        Args:
            entry(int): integer index of the cycler entry to set heater voltage for
            heater_number(int): integer heater channel number (or column in cycler table)
                to set heater voltage for
            heater_value(float): heater voltage to set
        """
        self.write(f"DRV:CYC:SET {entry:d} {heater_number:d} {heater_value:.4f}")

    def set_cycler_entry_mode_hop(self, entry: int, mode_hop: bool, repetition: bool = False) -> None:
        """Write one trigger setting for mode hop into RAM."""
        if Version(self.fwv) >= Version("1.3.7"):
            if repetition:
                self.write(f"; {entry:d} {mode_hop:d}")
            else:
                self.write(f"DRV:CYC:SETT {entry:d} {mode_hop:d}")

    def get_cycler_entry_mode_hop(self, entry: int) -> bool:
        """Get one trigger setting for mode hop"""
        if Version(self.fwv) >= Version("1.3.7"):
            mode_hop = bool(int(self.query(f"DRV:CYC:GETT? {entry:d}")))
        else:
            mode_hop = None
        return mode_hop

    def set_cycler_wavelength_count(self, wavelength_count: int) -> None:
        """Set number of wavelengths to be queried and stored"""
        if Version(self.fwv) >= Version("1.3.8"):
            self.write(f"DRV:CYC:WC {wavelength_count:d}")

    def get_cycler_wavelength_count(self, entry: int) -> int:
        """Get number of wavelengths to be queried and stored"""
        if Version(self.fwv) >= Version("1.3.8"):
            wavelength_count = int(self.query(f"DRV:CYC:WC? {entry:d}"))
        else:
            wavelength_count = None
        return wavelength_count

    def set_cycler_entry_wavelengths(self, entry: int, wavelengths, repetition: bool = False):
        """Write wavelength values of multiply entries (up to 10) into EEPROM."""
        if Version(self.fwv) >= Version("1.3.8"):
            if repetition:
                write_string = f"; {entry:d}"
            else:
                write_string = f"DRV:CYC:STRW {entry:d}"
            for wavelength in wavelengths:
                write_string = write_string + f" {wavelength:.4f}"
            self.write(write_string)

    def get_cycler_entry_wavelength(self, entry: int) -> float:
        """Get a single wavelength value from EEPROM."""
        if Version(self.fwv) >= Version("1.3.8"):
            wavelength = float(self.query(f"DRV:CYC:GW? {entry:d}"))
        else:
            wavelength = None
        return wavelength

    def store_cycler(self) -> None:
        """Stores modified entries to the cycler table in memory to persistent storage

        This command is the only way to save cycler table entries to persistent storage,
        which will survive a power cycle of the driver.

        NOTE: The cycler cannot be running when calling this method.
        """
        logger.info("Storing cycler entries to persistent storage")
        self.write("DRV:CYC:STOR")

    # Run settings
    def set_cycler_span(self, start_index: int, stop_index: int):
        """Sets the span, indices of boundaries, to cycle in between

        The cycler can cycle between a subrange of the entire cycler table.
        This method is used to set the boundaries where the cycler will cycle
        in between, given by a start and stop index.

        Args:
            start_index(int): start index of entry to use for cycler operation (included)
            stop_index(int): stop index of entry to use for cycler operation (included)
        """
        self.write(f"DRV:CYC:SPAN {start_index:d} {stop_index:d}")

    def get_cycler_span(self):
        """Gets the span, indices of boundaries, to cycle in between

        The cycler can cycle between a subrange of the entire cycler table.
        This method is used to get the boundaries that are set.

        Returns:
            (tuple[int, int]): tuple with the start and end index
        """
        resp = self.query("DRV:CYC:SPAN?")
        return tuple(int(val) for val in resp.split())

    def get_cycler_entries_max(self):
        """Returns the maximum size of persistent storage."""
        if self._eeprom_size is None:
            self._eeprom_size = int(self.query("DRV:CYC:LSZE?"))
        return self._eeprom_size

    def set_cycler_trigger(self, state: bool):
        """Manually sets the output trigger level

        The output trigger can be set high (True) or low (False),
        corresponding to x and x V.

        Args:
            state(bool): trigger state to set, can be True/high or False/low
        """
        self.write(f"DRV:CYC:TRIG {int(state):d}")
    
    def set_cycler_mode_hop(self, state: bool) -> None:
        if Version(self.fwv) >= Version("1.3.7"):
            self.write(f"DRV:CYC:MHP {int(state):d}")

    def clear_cycler_table(self) -> None:
        """Clear cycler table, set all entries to 0.0."""
        if Version(self.fwv) >= Version("1.3.7"):
            self.write(f"DRV:CYC:CLR")
    
    def initialize_cycler_table(self, add_mode_hops: bool = False, add_wavelengths: bool = False):
        """Loads all cycler entries from PC into volatile driver memory

        This method will set the entire opened cycler table into driver memory
        to use. It will first turn of the cycler, if running.
        All entries of the loaded cycler table, (with method open_file_cycler_table),
        will be set to driver memory for direct use. It has an option to
        fill all subsequent entries not in the opened cycler table to 0V.

        Args:
        """
        logger.info("Initializing cycler table")
        # Ensure cycler is not running
        if self.cycler_running:
            self.turn_off_cycler()
        # Clear cycler, all values are set to 0
        self.clear_cycler_table()
        # Turn off status codes to speed up communication
        self.prefix_mode = False
        # Update per entry/row heater values into RAM
        repetition = False
        for cycler_entry in range(self._cycler_table_length):
            self.put_cycler_entry(
                entry=cycler_entry,
                value1=float(self._cycler_table[cycler_entry, self.cycler_config.PHASE_SECTION]),
                value2=float(self._cycler_table[cycler_entry, self.cycler_config.RING_LARGE]),
                value3=float(self._cycler_table[cycler_entry, self.cycler_config.RING_SMALL]),
                value4=float(self._cycler_table[cycler_entry, self.cycler_config.TUNABLE_COUPLER]),
                repetition=repetition,
            )
            # Update user with print statement every 100 entries
            if (cycler_entry + 1) % 1000 == 0:
                logger.info(f"{(cycler_entry + 1):d}/{self._cycler_table_length:d}")
            repetition = True

        # Adding mode hops is only supported from firmware version 1.3.7 and higher.
        if add_mode_hops and Version(self.fwv) >= Version("1.3.7"):
            logger.info("Adding mode hops")
            repetition = False
            for cycler_entry in range(self._cycler_table_length):
                self.set_cycler_entry_mode_hop(
                    entry=cycler_entry,
                    mode_hop=bool(self._cycler_table[cycler_entry, self.cycler_config.MODE_HOPS]),
                    repetition=repetition,
                )
                # Update user with print statement every 100 entries
                if (cycler_entry + 1) % 1000 == 0:
                    logger.info(f"{(cycler_entry + 1):d}/{self._cycler_table_length:d}")
                repetition = True

        # Turn status codes on as default communication mode
        self.prefix_mode = True

        # Adding wavelengths is only supported from firmware version 1.3.8 and higher.
        if add_wavelengths and Version(self.fwv) >= Version("1.3.8"):
            logger.info("Adding wavelengths")
            # Set number of wavelengths to be queried and stored back to 4, to increase spead
            self.set_cycler_wavelength_count(4)
            repetition = False
            for cycler_entry in range(self._cycler_table_length):
                if cycler_entry % 4 == 0:
                    wavelengths = np.zeros(shape=4, dtype=float)
                    for cycler_entry_forward in range(4):
                        if cycler_entry + cycler_entry_forward < self._cycler_table_length:
                            wavelengths[cycler_entry_forward] = float(self._cycler_table[cycler_entry+cycler_entry_forward, self.cycler_config.WAVELENGTH])
                    self.set_cycler_entry_wavelengths(
                        entry=cycler_entry,
                        wavelengths=wavelengths,
                        repetition=repetition,
                    )
                if (cycler_entry + 1) % 1000 == 0:
                    logger.info(f"{(cycler_entry + 1):d}/{self._cycler_table_length:d}")
            # Set number of wavelengths to be queried and stored back to 1
            self.set_cycler_wavelength_count(1)
        logger.info("Initializing cycler table Done!")

    def turn_off_system(self) -> None:
        if self.cycler_running:
            self.turn_off_cycler()
        super().turn_off_system()

    # Storage of user and calibration data to the EEPROM
    # TODO: Warning: these user data function are not fully supported yet in firmware 1.3.8, due to a memory overflow issue.
    def set_user_data_bool(self, address: int, data: bool) -> None:
        """Set user calibration data to RAM"""
        if Version(self.fwv) >= Version("1.3.8"):
            # Storing Python bool type to byte
            self.write(f"SYST:UDTA:B {address:d} {data:d}")

    def get_user_data_bool(self, address: int) -> bool:
        """Set user calibration data to RAM"""
        if Version(self.fwv) >= Version("1.3.8"):
            # Query Python bool type from byte
            data = bool(int(self.query(f"SYST:UDTA:B? {address:d}")))
        else:
            data = None
        return data

    def set_user_data_int(self, address: int, data: int) -> None:
        """Set user calibration data to RAM"""
        if Version(self.fwv) >= Version("1.3.8"):
            # Storing Python int type to double word (4 bytes)
            self.write(f"SYST:UDTA:DW {address:d} {data:d}")

    def get_user_data_int(self, address: int) -> int:
        """Set user calibration data to RAM"""
        if Version(self.fwv) >= Version("1.3.8"):
            # Query Python int type from double word (4 bytes)
            data = int(self.query(f"SYST:UDTA:DW? {address:d}"))
        else:
            data = None
        return data

    def set_user_data_float(self, address: int, data: float) -> None:
        """Set user calibration data to RAM"""
        if Version(self.fwv) >= Version("1.3.8"):
            # Storing Python int type to double word (4 bytes)
            self.write(f"SYST:UDTA:F {address:d} {data:.4f}")

    def get_user_data_float(self, address: int) -> float:
        """Set user calibration data to RAM"""
        if Version(self.fwv) >= Version("1.3.8"):
            # Query Python int type from double word (4 bytes)
            data = float(self.query(f"SYST:UDTA:F? {address:d}"))
        else:
            data = None
        return data

    def store_user_data(self) -> None:
        """Store all user calibration data from RAM to persistent (non-volatile EEPROM) storage."""
        if Version(self.fwv) >= Version("1.3.8"):
            logger.info("Storing user calibration data to persistent storage")
            self.write("SYST:UDTA:STOR")

    # Feedback loops
    # General state
    def get_fb_state(self) -> bool:
        return bool(int(self.query("FB:STAT?")))

    def set_fb_state(self, true_or_false: bool) -> None:
        self.write(f"FB:STAT {true_or_false:d}")

    def get_amount_fb(self) -> int:
        return int(self.query("FB:COUN?"))

    def get_fb_loop(self) -> int:
        return int(self.query("FB:NSEL?"))

    def set_fb_loop(self, loop_number: int) -> None:
        self.write(f"FB:NSEL {loop_number:d}")

    # Source/destination
    def get_fb_source(self) -> int:
        return int(self.query("FB:SRC?"))

    def set_fb_source(self, source: int) -> None:
        self.write(f"FB:SRC {source:d}")

    def get_fb_destination(self) -> int:
        return int(self.query("FB:DST?"))

    def set_fb_destination(self, destination: int) -> None:
        self.write(f"FB:DST {destination:d}")

    # Loop setpoint, coefficients, timing
    def get_fb_setpoint(self) -> float:
        return float(self.query("FB:SETP?"))

    def set_fb_setpoint(self, setpoint: float) -> None:
        self.write(f"FB:SETP {setpoint:.6f}")

    def get_fb_tick_interval(self) -> int:
        """In milliseconds"""
        return int(self.query("FB:INT?"))

    def set_fb_tick_interval(self, tick_interval_ms: int) -> None:
        self.write(f"FB:INT {tick_interval_ms:d}")

    # Gains
    def get_fb_gain(self, gain_type: str) -> float:
        gain_type = gain_type.upper()
        gains = ("P", "I", "D")
        if gain_type not in gains:
            logger.error("Error: gain_type can only be P, I, or D")
            return 0.0
        return float(self.query(f"FB:K{gain_type}?"))

    def set_fb_gain(self, gain_type: str, proportional_gain: float) -> None:
        gain_type = gain_type.upper()
        gains = ("P", "I", "D")
        if gain_type not in gains:
            logger.error("Error: gain_type can only be P, I, or D")
            return
        self.write(f"FB:K{gain_type} {proportional_gain:.6f}")

    # Abstractions for setting up feedback loop
    def set_up_temp_enclosure_fb(
        self, comp_coefficient: float, enclosure_ref=23.0, tick_interval=500
    ):
        # Make use of first available feedback loop
        if not (self.get_fb_loop == 0):
            self.set_fb_loop(0)
        # We want to make use of Temp enclosure temp as feedback source/input, that has index 4
        if not (self.get_fb_source == 4):
            self.set_fb_source(4)
        # Output/compensation for the feedback loop should be TEC internal, index 1
        if not (self.get_fb_destination == 1):
            self.set_fb_destination(1)
        # Configure feedback loop reference point (to check source value against), gain, tick interval (ms)
        self.set_fb_tick_interval(tick_interval)
        self.set_fb_setpoint(enclosure_ref)
        self.set_fb_gain("P", comp_coefficient)
        self.set_fb_gain("I", 0.0)
        self.set_fb_gain("D", 0.0)

    def get_fb_settings(self) -> None:
        ii_fb = self.get_fb_loop()
        src_fb = self.get_fb_source()
        dest_fb = self.get_fb_destination()
        tick_interval = self.get_fb_tick_interval()
        setpoint_fb = self.get_fb_setpoint()
        p_gain = self.get_fb_gain("P")
        i_gain = self.get_fb_gain("I")
        d_gain = self.get_fb_gain("D")
        enabled = self.get_fb_state()
        logger.info(f"FB settings, #{ii_fb}\nSource: {src_fb}\nDestination: {dest_fb}")
        logger.info(f"Setpoint: {setpoint_fb}\nInterval: {tick_interval} ms")
        logger.info(f"Gains:\nP: {p_gain}, I: {i_gain}, D: {d_gain}")
        logger.info(f"FB enabled? {enabled}")
