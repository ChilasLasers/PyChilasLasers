#!/usr/bin/env python
"""
Laser base object to communicate with Chilas Lasers.
Authors: RLK, AVR, SDU
"""

import logging
import time
from enum import IntEnum

import numpy as np
import serial
import serial.tools
from serial.tools.list_ports import comports

# Constants
DEFAULT_BAUDRATE = 57600
SUPPORTED_BAUDRATES = {9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400, 460800, 912600}

# Setup logging
logger = logging.getLogger(__name__)

# ERROR CODES THAT SHOULD TRIGGER A ERROR DIALOG (errors 14 to 23)
CRITICAL_ERRORS: list[str] = ["E0" + str(x) for x in range(14,24)] + ["E0" + str(x) for x in range(30,51)]
SEMICOLON_COMMANDS: list[str] = [
    "DRV:CYC:GW?",
    "DRV:CYC:GET?",
    "DRV:CYC:PUT",
    "DRV:CYC:SETT",
    "DRV:CYC:STRW"]


# Constants
class CyclerColumn(IntEnum):
    PHASE_SECTION = 0
    RING_LARGE = 1
    RING_SMALL = 2
    TUNABLE_COUPLER = 3
    WAVELENGTH = 4
    MODE_HOPS = 5
    CAL_RESULT = 6
    ENTRY_INDEX = 6
    MODE_INDEX = 7


class Laser:
    """Generic Laser class for Chilas lasers."""

    model = "Chilas generic Laser"
    channel_config = None
    cycler_config = CyclerColumn

    @staticmethod
    def list_comports() -> list[str]:
        """Lists all available COM ports on the system.
        :py:func:`serial.tools.list_ports.comports` is used to list all available
        ports. In that regard this method is but a wrapper for it.

        Returns:
            list[str]: List of available COM ports as strings sorted
            alphabetically in ascending order.
        """
        return sorted([port.device for port in comports()])

    @staticmethod
    def _is_port_correct(port: str) -> bool:
        """
        Checks if the entered port is a valid/available COM port.
        Args:
            port (str): The port to be checked.
        Returns:
            bool: True if the port is available, False otherwise.
        """
        available_comports = Laser.list_comports()
        if port in available_comports:
            return True
        else:
            logger.error(f"Port not correct, options are:\n{available_comports}")
            return False

    def __init__(self, port=None, timeout: float = 10.0) -> None:
        """
        Initializes the laser instrument with the given serial port and timeout.
        Args:
            port (str, optional): The serial port to connect to. Defaults to None.
            timeout (float, optional): The timeout for the serial connection in seconds. Defaults to 10.0.
        Attributes:
            _ser (serial.Serial): The serial connection object.
            _idn (str): The device identification string.
            _srn (str): The system serial number.
            _hwv (str): The hardware version.
            _fwv (str): The firmware version.
            _admin (bool): Admin mode state
        """
        # Serial connection
        self._ser: serial.Serial = serial.Serial(
            baudrate=DEFAULT_BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )

        # Previous command is logged to aid in replacing consecutive commands with semicolon
        self.previous_command: str = "None"


        # Device attributes (static)
        self._idn = None
        # System
        self._srn = None
        self._hwv = None
        self._fwv = None
        self._admin = None
        self._prefix_mode = True

        # Device attributes, settable and managed, no internal state
        # Communication protocol
        # TEC driver
        # TODO: add further device attributes as managed properties ()

        # Config serial connection if port is given
        if port:
            self.port = port

    def __repr__(self) -> str:
        """Returns a string representation of the Laser object."""
        return f"<Laser {self.idn} at {self.port}>"

    @property
    def port(self) -> str | None:
        """Gets the current serial port."""
        if self._ser and self._ser.port:
            return self._ser.port

    @port.setter
    def port(self, port: str) -> None:
        """Sets the serial port for the connection.

        Args:
            port (str): The serial port to be set.
        """
        if self._ser.is_open:
            logger.error("Error: serial connection already open.")
            return
        if not isinstance(port, str) or not type(self)._is_port_correct(port):
            logger.error(f"Error: given port, {port} is not suitable.")
            return
        self._ser.port = port

    @property
    def is_connected(self) -> bool:
        """
        Check if the laser instrument is connected.
        Returns:
            bool: True if the serial connection is open, False otherwise.
        """
        return self._ser.is_open

    @property
    def prefix_mode(self) -> bool:
        """Gets prefix mode for the laser driver

        The laser driver can be operated in two different communication modes:
            1. Prefix mode on
            2. Prefix mode off

        When prefix mode is on, every message over the serial connection will be
        replied to by the driver with a response, and every response will be prefixed
        with a return code (rc), either `0` or `1` for an OK or ERROR respectively.

        With prefix mode is off, responses from the laser driver are not prefixed
        with a return code. This means that in the case for a serial write command
        without an expected return value, the driver will not send back a reply.

        Returns:
            (bool): whether prefix mode is enabled (True) or disabled (False)
        """
        self._prefix_mode = bool(int(self.query("SYST:COMM:PFX?")))
        return self._prefix_mode

    @prefix_mode.setter
    def prefix_mode(self, mode: bool) -> None:
        """Sets prefix mode for the laser driver

        The laser driver can be operated in two different communication modes:
            1. Prefix mode on
            2. Prefix mode off

        When prefix mode is on, every message over the serial connection will be
        replied to by the driver with a response, and every response will be prefixed
        with a return code (rc), either `0` or `1` for an OK or ERROR respectively.

        With prefix mode is off, responses from the laser driver are not prefixed
        with a return code. This means that in the case for a serial write command
        without an expected return value, the driver will not send back a reply.

        Args:
            mode (bool): whether to enable prefix mode (True) or disable it (False)
        """
        self._prefix_mode = mode
        self.write(f"SYST:COMM:PFX {mode:d}")
        logger.info(f"Changed prefix mode to {self._prefix_mode=}")

    @property
    def baudrate(self) -> int:
        """Gets the baudrate of the serial connection to the driver

        The baudrate can be changed, but does require a serial reconnect

        Returns:
            (int): baudrate currently in use
        """
        driver_baudrate = int(self.query("SYST:SER:BAUD?"))
        if driver_baudrate != self._ser.baudrate:
            logger.error("There seems to be a baudrate mismatch between driver and connection baudrate settings")
        return driver_baudrate

    @baudrate.setter
    def baudrate(self, new_baudrate: int) -> None:
        """Sets the baudrate of the serial connection to the driver

        The baudrate can be changed, but this requires a serial reconnect.

        Currently supported baudrates are:
            - 9600
            - 14400
            - 19200
            - 28800
            - 38400
            - 57600, default
            - 115200
            - 230400
            - 460800
            - 912600

        This method will first check if there is already a serial connection open.
        If not, it will do nothing and return immediately (None). If a serial connection
        is open, it will first check if new baudrate requested, is supported.
        If not, it will return None. Otherwise, continue to check if the new baudrate
        needs to be set, by comparing with the current baudrate in use. If the new requested
        baudrate is different then it will set the new baudrate as follows:
            1. Instruct the driver to use a new baudrate
            2. Close the serial connection
            3. Change the serial connection attribute to use the new baudrate as well
            4. Reopen the serial connection

        Args:
            new_baudrate (int): new baudrate to use
        """
        if not self.is_connected:
            return None

        if new_baudrate not in SUPPORTED_BAUDRATES:
            logger.error(f"The given baudrate {new_baudrate} is not supported.")
            return None

        current_baudrate = self.baudrate
        if new_baudrate == current_baudrate:
            return None

        # 1. Instruct driver to use new baudrate
        logger.info(f"Instruct driver to use new baudrate {new_baudrate:d}")
        self._write(f"SYST:SER:BAUD {new_baudrate:d}")
        # 2. Close serial connection
        logger.info("Closing serial connection")
        self._ser.close()
        # 3. Change serial connection baudrate attribute
        logger.info("Using new baudrate with pyserial")
        self._ser.baudrate = new_baudrate
        # 4. Reopen serial connection
        logger.info("Reopening serial connection with new baudrate")
        self._ser.open()

    def open_connection(
        self, port: str | None = None, get_attributes: bool = True
    ) -> None:
        """Method used for opening a new PySerial connection to the device.
        If the port is not given, the saved port is used.
        If there is no saved port and none is given, an error is raised.
        If the connection is already open, it will be closed before opening a new one.

        Args:
            port (str, optional): The new port to be used for the connection.
              Formatted as the OS-specific serial port e.g. COM port. If none is
              provided the saved port will be used.
            get_attributes (bool, optional): Specifies whether the laser attributes
              should be refreshed upon creating the new connection. Defaults to True.
        """
        # Check if there is a suitable port to use, given before or now
        if port is None and not self.port:
            logger.error("No port is given or saved to use to open connection.")
            return

        # Otherwise set given port as new port if it differs from earlier one
        elif (port is not None) and (port != self.port):
            if self._ser.is_open:
                self.close_connection()
            self.port = port

        # Open connection if not open already
        if not self._ser.is_open:
            try:
                self._ser.open()
            except serial.SerialException as e:
                logger.error(f"Failed to open serial connection: {e}")
                return

        # Update device attributes
        if get_attributes:
            self._update_attributes()

    def close_connection(self) -> None:
        """Close serial connection to device."""
        if self._ser.is_open:
            if self.baudrate != DEFAULT_BAUDRATE:
                self.baudrate = DEFAULT_BAUDRATE
            logger.info("Closing serial connection")
            self._ser.close()

    def _write(self, data: str) -> None:
        """Writes data to the serial connection.
        If the command is the same as the previous one, it replaces it with a semicolon.

        Args:
            data (str): The data to be written.
        """
        logger.debug(f"W {data}")
        self._ser.write(f"{data}\r\n".encode("ascii"))

    def _read(self) -> str:
        """Reads data from the serial connection

        Always returns complete message, including rc if self.prefix_mode
        is enabled.

        Returns:
            str: The data read from the serial connection.
        """
        raw_reply: str = self._ser.readline().decode("ascii").rstrip()
        logger.debug(f"R {raw_reply}")

        if not raw_reply:
            logger.error("Empty raw reply from device")
            return raw_reply

        if self._prefix_mode:
            if raw_reply[0] != "0":
                logger.error(f"Nonzero return code: {raw_reply[2:]}")
        return raw_reply

    def _query(self, cmd: str) -> str:
        """Sends a command to the device and reads the response.

        Args:
            cmd (str): The command to be sent.

        Returns:
            (str): The response from the device.
        """
        self._write(cmd)
        reply = self._read()
        return reply


    def _query_rc_check(self, cmd: str) -> str:
        """Sends a command to the device and checks the return code.

        Args:
            cmd (str): The command to be sent.

        Returns:
            str: The response from the device.
        """

        reply = self._query(cmd)

        if reply[0] != "0":  # Check if the first character is not "0" as this indicates an error
            if any(reply[2:].startswith(error) for error in CRITICAL_ERRORS):  # Check for critical errors
                if reply[2:].startswith("E0" + "23"):
                    reply += "  SHUTDOWN_REASON = " + self.shutdown_reason
                logger.critical(f"Critical error: {reply[2:]}", extra={"cmd": cmd, "reply": reply})
            else:  # Check for non-critical errors
                logger.error(f"Nonzero return code: {reply[2:]}", extra={"cmd": cmd, "reply": reply})

        return reply

    def _query_replace_semicolon(self, cmd: str) -> str:
        """To speed up communication, a repeating command can be replaced with a semicolon.
        Check if the command was previously sent to the device. In that case, replace it with a semicolon.

        Args:
            cmd (str): The command to be replaced with semicolon.

        Returns:
            str: The command with semicolon inserted
        """
        if cmd.split(" ")[0] == self.previous_command and self.previous_command in SEMICOLON_COMMANDS:
            cmd = cmd.replace(cmd.split(" ")[0], ";")
        else:
            self.previous_command = cmd.split(" ")[0]
        return cmd

    def query(self, cmd: str) -> str:
        """Sends a command to the device and returns the response without the return code.

        Args:
            cmd (str): The command to be sent.

        Returns:
            str: The response from the device without the return code.
        """
        cmd = self._query_replace_semicolon(cmd)
        return self._query_rc_check(cmd)[2:]

    def write(self, cmd: str) -> None:
        """Sends a command to the device.

        Args:
            cmd (str): The command to be sent.
        """
        cmd = self._query_replace_semicolon(cmd)
        if self._prefix_mode:
            self._query_rc_check(cmd)
        else:
            self._write(cmd)

    @property
    def idn(self) -> str | None:
        """Gets the device identification string.

        Returns:
            (str | None): The device identification string.
        """
        if self._idn is None and self._ser.is_open:
            self._idn = self.query("*IDN?")
        return self._idn

    @property
    def srn(self) -> str | None:
        """Gets the system serial number.

        Returns:
            str | None: The system serial number.
        """
        if self._srn is None and self._ser.is_open:
            self._srn = self.query("SYST:SRN?")
        return self._srn

    @property
    def hwv(self) -> str | None:
        """Gets the hardware version.

        Returns:
            str | None: The hardware version.
        """
        if self._hwv is None and self._ser.is_open:
            self._hwv = self.query("SYST:HWV?")
        return self._hwv

    @property
    def fwv(self) -> str | None:
        """Gets the firmware version.

        Returns:
            str | None: The firmware version.
        """
        if self._fwv is None and self._ser.is_open:
            self._fwv = self.query("SYST:FWV?")
        return self._fwv


    @property
    def shutdown_reason(self) -> str:
        return self.query("SYST:SDRN?")


    @property
    def cpu(self) -> str | None:
        """Gets the CPU information.

        Returns:
            str | None: The CPU information.
        """
        if self._cpu is None and self._ser.is_open:
            self._cpu = self.query("SYST:CHIP?")
        return self._cpu

    def _update_attributes(self) -> None:
        """Updates the device attributes by querying the device."""
        self._idn = self.query("*IDN?")
        self._srn = self.query("SYST:SRN?")
        self._hwv = self.query("SYST:HWV?")
        self._fwv = self.query("SYST:FWV?")

    def reset_device(self) -> None:
        """Resets the device."""
        self._write("*RST")

    @property
    def system_state(self) -> bool:
        """Gets the system state.

        Returns:
            bool: The system state.
        """
        return bool(int(self.query("SYST:STAT?")))

    @system_state.setter
    def system_state(self, value: bool) -> None:
        """Sets the system state.

        Args:
            value (bool): The system state to be set.
        """
        if type(value) is not bool:
            logger.error("ERROR: given value is not a boolean")
            return
        self.write(f"SYST:STAT {value:d}")

    def turn_on_system(self) -> None:
        """Turns on the laser system."""
        logger.info("Turning on Laser")
        self.system_state = True

    def turn_off_system(self) -> None:
        """Turns off the laser system."""
        logger.info("Turning off Laser")
        self.system_state = False

    @property
    def admin_mode(self) -> bool:
        """Gets the admin mode state.

        Returns:
            bool: The admin mode state.
        """
        if self._admin is None and self._ser.is_open:
            self._admin = bool(int(self.query("SYST:PWD?")))
        return self._admin

    def _enable_admin_mode(self, password: str) -> None:
        """Enables admin mode with the given password.

        Args:
            password (str): The password to enable admin mode.
        """
        self.write(f"SYST:PWD {password}")

    @property
    def uptime(self) -> int:
        """Gets the system uptime.

        Returns:
            int: The system uptime.
        """
        return int(self.query("SYST:UPT?"))

    @property
    def debug_info(self) -> str:
        """Gets the debug information.

        Returns:
            str: The debug information.
        """
        return self.query("SYST:TTM?")

    @property
    def statusCode_prefix(self) -> bool:
        """Gets the status code prefix state.

        Returns:
            bool: The status code prefix state.
        """
        return bool(int(self.query("SYST:COMM:PFX?")))

    @statusCode_prefix.setter
    def statusCode_prefix(self, value: bool) -> None:
        """Sets the status code prefix state.

        Args:
            value (bool): The status code prefix state to be set.
        """
        if type(value) is not bool:
            logger.error("ERROR: given value is not a boolean")
            return
        self.write(f"SYST:COMM:PFX {value:d}")

    @property
    def diode_state(self) -> bool:
        """Gets the laser diode state.

        Returns:
            bool: The laser diode state.
        """
        return bool(int(self.query("LSR:STAT?")))

    @diode_state.setter
    def diode_state(self, value: bool) -> None:
        """Sets the laser diode state.

        Args:
            value (bool): The laser diode state to be set.
        """
        if type(value) is not bool:
            logger.error("ERROR: given value is not a boolean")
            return
        self.write(f"LSR:STAT {value:d}")

    def turn_on_diode(self) -> None:
        """Turns on the laser diode."""
        self.diode_state = True

    def turn_off_diode(self) -> None:
        """Turns off the laser diode."""
        self.diode_state = False

    @property
    def diode_current(self) -> float:
        """Gets the laser diode current.

        Returns:
            float: The laser diode current.
        """
        return float(self.query("LSR:ILEV?"))

    @diode_current.setter
    def diode_current(self, current_ma: float) -> None:
        """Sets the laser diode current.

        Args:
            current_ma (float): The laser diode current to be set.
        """
        if type(current_ma) is not float:
            logger.error("ERROR: given value is not a float")
            return
        # TODO: add limits and additional checking
        self.write(f"LSR:ILEV {current_ma:.3f}")

    @property
    def tec_state(self) -> bool:
        """Gets the TEC state.

        Returns:
            bool: The TEC state.
        """
        return bool(int(self.query("TEC:STAT?")))

    @tec_state.setter
    def tec_state(self, value: bool) -> None:
        """Sets the TEC state.

        Args:
            value (bool): The TEC state to be set.
        """
        if type(value) is not bool:
            logger.error("ERROR: given value is not a boolean")
            return
        self.write(f"TEC:STAT {value:d}")

    def turn_on_tec(self) -> None:
        """Turns on the TEC."""
        self.tec_state = True

    def turn_off_tec(self) -> None:
        """Turns off the TEC."""
        self.tec_state = False

    @property
    def tec_target(self) -> float:
        """Gets the TEC target temperature.

        Returns:
            float: The TEC target temperature.
        """
        return float(self.query("TEC:TTGT?"))

    @tec_target.setter
    def tec_target(self, target_temp: float) -> None:
        """Sets the TEC target temperature.

        Args:
            target_temp (float): The TEC target temperature to be set.
        """
        if type(target_temp) is not float:
            logger.error("ERROR: given value is not a float")
            return
        # TODO: add limits and additional checking
        self.write(f"TEC:TTGT {target_temp:.3f}")

    @property
    def tec_temp(self) -> float:
        """Gets the TEC temperature.

        Returns:
            float: The TEC temperature.
        """
        return float(self.query("TEC:TEMP?"))

    @property
    def tec_current(self) -> float:
        """Gets the TEC current.

        Returns:
            float: The TEC current.
        """
        return float(self.query("TEC:ITEC?"))

    @property
    def tec_limit_min(self) -> float:
        """Gets the TEC minimum temperature limit.

        Returns:
            float: The TEC minimum temperature limit.
        """
        return float(self.query("TEC:CFG:TMIN?"))

    @tec_limit_min.setter
    def tec_limit_min(self, tec_lim_min: float) -> None:
        """Sets the TEC minimum temperature limit.

        Args:
            tec_lim_min (float): The TEC minimum temperature limit to be set.
        """
        if type(tec_lim_min) is not float:
            logger.error("ERROR: given value is not a float")
            return
        # TODO: add limits and additional checking
        self.write(f"TEC:CFG:TMIN {tec_lim_min:.3f}")

    @property
    def tec_limit_max(self) -> float:
        """Gets the TEC maximum temperature limit.

        Returns:
            float: The TEC maximum temperature limit.
        """
        return float(self.query("TEC:CFG:TMAX?"))

    @tec_limit_max.setter
    def tec_limit_max(self, tec_lim_max: float) -> None:
        """Sets the TEC maximum temperature limit.

        Args:
            tec_lim_max (float): The TEC maximum temperature limit to be set.
        """
        if type(tec_lim_max) is not float:
            logger.error("ERROR: given value is not a float")
            return
        # TODO: add limits and additional checking
        self.write(f"TEC:CFG:TMAX {tec_lim_max:.3f}")

    def get_driver_min(self, heater_ch: int) -> float:
        """Gets the minimum voltage of the driver channel.

        Args:
            heater_ch (int): The heater channel number.

        Returns:
            float: The minimum voltage of the driver channel.
        """
        return float(self.query(f"DRV:LIM:MIN? {heater_ch:d}"))

    def get_driver_max(self, heater_ch: int) -> float:
        """Gets the maximum voltage of the driver channel.

        Args:
            heater_ch (int): The heater channel number.

        Returns:
            float: The maximum voltage of the driver channel.
        """
        return float(self.query(f"DRV:LIM:MAX? {heater_ch:d}"))

    def get_driver_value(self, heater_ch: int) -> float:
        """Gets the current value of the driver channel.

        Args:
            heater_ch (int): The heater channel number.

        Returns:
            float: The current value of the driver channel.
        """
        return float(self.query(f"DRV:D? {heater_ch:d}"))

    def set_driver_value(self, heater_ch: int, heater_value: float) -> None:
        """Sets the value of the driver channel.

        Args:
            heater_ch (int): The heater channel number.
            heater_value (float): The value to be set.
        """
        self.write(f"DRV:D {heater_ch:d} {heater_value:.4f}")

    def preload_driver_value(self, heater_ch: int, heater_value: float) -> None:
        """Preload the value of the driver channel.
        Does not immediately change the physical output value.

        Args:
            heater_ch (int): The heater channel number.
            heater_value (float): The value to be preloaded.
        """
        self.write(f"DRV:DP {heater_ch:d} {heater_value:.4f}")

    def apply_preload_values(self) -> None:
        """Update all driver channels with the preload values.

        """
        self.write("DRV:U")

    def set_driver_value_with_antihyst(
        self,
        heater_ch: int,
        heater_value: float,
        interval=0.1,
        deltas_sq=None,
    ) -> None:
        """Sets the value of the driver channel with anti-hysteresis.

        Args:
            heater_ch (int): The heater channel number.
            heater_value (float): The value to be set.
            interval (float, optional): The interval between steps. Defaults to 0.1.
            deltas_sq (list[float], optional): The list of delta values. Defaults to [30, 20, 10, 0].
        """
        if deltas_sq is None:
            deltas_sq = [30, 20, 10, 0]
        for dv_sq in deltas_sq:
            self.set_driver_value(heater_ch, np.sqrt(heater_value**2 + dv_sq))
            time.sleep(interval)

    # TODO, add other heater driver commands
    # TODO, add heater driver configuration commands
    # TODO, add heater driver limit commands
    # TODO, add cycler commands (new since v1.1 firmware)
