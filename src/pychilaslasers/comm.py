"""Serial communication interface for Chilas laser systems.

Provides low-level serial communication with laser drivers, including
command/response handling, connection management, and port discovery.

Classes:
    Communication: Main serial communication handler.

Functions:
    list_comports: Discover available COM ports.

Authors: RLK, AVR, SDU
"""

# ✅ Standard library imports
import atexit
import logging
import signal

# ✅ Third-party imports
import serial
import serial.tools
import serial.tools.list_ports

# ✅ Local imports
from pychilaslasers.exceptions.laser_error import LaserError
from pychilaslasers.constants import Constants

logger = logging.getLogger(__name__)


class Communication:
    """Communication class for handling communication with the laser driver over serial.

    This class provides methods for sending commands to the laser, receiving responses,
    and managing the serial connection. It also handles the prefix mode for the
    laser driver.
    """

    def __init__(self, com_port: str) -> None:
        """Initialize the Communication class with the specified serial port.

        This method sets up the serial connection to the laser driver and initializes
        the communication parameters. It also registers cleanup functions to ensure
        the serial connection is properly closed on exit or signal termination. And
        sets the initial baudrate to the default value. When a connection fails, it will
        attempt to reconnect using the next supported baudrate until a connection is
        established as this is one of the most common issues when connecting to the
        laser driver.

        Args:
            com_port: The serial port to connect to the laser driver.
                this can be found by using the `pychilaslasers.comm.list_comports()`
                function.

        """
        # Validate the com_port input
        if not isinstance(com_port, str):
            raise ValueError(
                "The com_port must be a string representing the serial port."
            )

        # Initialize serial connection to the laser
        self._serial: serial.Serial = serial.Serial(
            port=com_port,
            baudrate=Constants.TLM_INITIAL_BAUDRATE,  # Use the first supported baudrate
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0,
        )
        self._previous_command: str = "None"

        self._prefix_mode: bool = True
        # Attempt to open the serial connection by trying different baudrates
        baudrates: set[int] = set(
            Constants.SUPPORTED_BAUDRATES
        )  # Copy to avoid modifying the original set
        rate = Constants.TLM_INITIAL_BAUDRATE
        while True:
            try:
                self.prefix_mode = True
                break
            except Exception:
                try:
                    logger.error(
                        f"Serial connection failed at {rate} baud.Attempting new "
                        f"connection with baudrate {(rate := baudrates.pop())}."
                    )
                    self.baudrate = rate  # Try next baudrate if the current one fails
                except KeyError:
                    logger.critical(
                        "No more supported baudrates available. Cannot establish serial"
                        " connection."
                    )
                    raise RuntimeError(
                        "Failed to establish serial connection with the laser driver. "
                        + "Please check the connection and supported baudrates."
                    ) from None
        self.baudrate = Constants.DEFAULT_BAUDRATE

        # Ensure proper closing of the serial connection on exit or signal
        try:
            atexit.register(self.close_connection)
            signal.signal(signal.SIGINT, self.close_connection)
            signal.signal(signal.SIGTERM, self.close_connection)
        except Exception:
            # This may fail in threaded environments
            pass

    def __del__(self) -> None:
        """Destructor that ensures the serial connection is closed after deletion.

        This method is called when the object is garbage collected, providing an
        additional safety mechanism to ensure the serial connection is properly closed
        even if the user forgets to call close explicitly or if the program terminates
        unexpectedly.
        """
        self.close_connection()

    ########## Main Methods ##########

    def query(self, data: str) -> str:
        """Send a command to the laser and return its response.

        This method sends a command to the laser over the serial connection and returns
        the response. It also handles the logging of the command and response. The
        response code of the reply is checked and an error is raised if the response
        code is not 0. Commands that are sent multiple times may be replaced with a
        semicolon to speed up communication.

        Args:
            data: The serial command to be sent to the laser.

        Returns:
            The response from the laser. The response is stripped of any leading
                or trailing whitespace as well as the return code. Response may be
                empty if the command does not return a value.

        Raises:
            serial.SerialException: If there is an error in the serial communication,
                such as a decoding error or an empty reply.
            LaserError: If the response code from the laser is not 0,
                indicating an error.

        """
        # Write the command to the serial port
        logger.debug(msg=f"W {data}")  # Logs the command being sent
        self._serial.write(f"{self._semicolon_replace(data)}\r\n".encode("ascii"))
        self._serial.flush()

        if not self.prefix_mode:
            return ""  # If prefix mode is off, return empty string immediately

        # Read the response from the laser
        try:
            reply: str = self._serial.readline().decode("ascii").rstrip()
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode reply from device: {e}")
            raise serial.SerialException(
                f"Failed to decode reply from device: {e}. "
                + "Please check the connection and baudrate settings."
            ) from e

        # Error handling
        if not reply or reply == "":
            logger.error("Empty reply from device")
            raise serial.SerialException(
                "Empty reply from device. Please check the connection and prefix mode."
            )

        if reply[0] != "0":
            logger.error(f"Nonzero return code: {reply[2:]}")
            raise LaserError(
                code=reply[2:6], message=reply[8:]
            )  # Raise a custom error with the reply message
        else:
            logger.debug(f"R {reply}")

        return reply[2:]

    def close_connection(self, signum=None, fname=None) -> None:
        """Close the serial connection to the laser driver safely.

        Attempts to reset the prefix mode and baudrate to the initial value before
        closing the connection.

        This method is registered to be called on exit or when a signal is received.
        """
        if self._serial and self._serial.is_open:
            if signum is not None:
                logger.error(
                    f"Received signal {signal.Signals(signum).name} ({signum}):"
                    "closing connection"
                )
            else:
                logger.debug("Closing connection")
            self.prefix_mode = True
            self.query("DRV:CYC:ABRT")  # Aborts cycler
            self.query("SYST:STAT 0")  # Turns off system
            self._serial.write(
                f"SYST:SER:BAUD {Constants.TLM_INITIAL_BAUDRATE}\r\n".encode("ascii")
            )  # Resets baud rate to initial value
            logger.debug("Resetting serial baudrate to initial value")
            self._serial.close()

    ########## Private Methods ##########

    def _semicolon_replace(self, cmd: str) -> str:
        """To speed up communication, repeating commands can be replaced by a semicolon.

        Check if the command was previously sent to the device. In that case, replace
        it with a semicolon.

        Args:
            cmd: The command to be replaced with semicolon.

        Returns:
            The command with semicolon inserted

        """
        if (
            cmd.split(" ")[0] == self._previous_command
            and self._previous_command in Constants.SEMICOLON_COMMANDS
        ):
            cmd = cmd.replace(cmd.split(" ")[0], ";")
        else:
            self._previous_command = cmd.split(" ")[0]
        return cmd

    def _initialize_variables(self) -> None:
        """Initialize private variables."""
        self._previous_command = "None"

    ########## Properties (Getters/Setters) ##########

    @property
    def prefix_mode(self) -> bool:
        """Gets prefix mode for the laser driver.

        !!! info "The laser can be operated in two different communication modes:"
            1. Prefix mode on
            2. Prefix mode off

        When prefix mode is on, every message over the serial connection will be
        replied to by the driver with a response, and every response will be
        prefixed with a return code (rc), either `0` or `1` for an OK or ERROR
        respectively.

        With prefix mode is off, responses from the laser driver are not prefixed
        with a return code. This means that in the case for a serial write command
        without an expected return value, the driver will not send back a reply.

        Returns:
            whether prefix mode is enabled (True) or disabled (False)

        """
        return self._prefix_mode

    @prefix_mode.setter
    def prefix_mode(self, mode: bool) -> None:
        """Set prefix mode for the laser driver.

        !!! info "The laser can be operated in two different communication modes:"
            1. Prefix mode on
            2. Prefix mode off

        When prefix mode is on, every message over the serial connection will be
        replied to by the driver with a response, and every response will be
        prefixed with a return code (rc), either `0` or `1` for an OK or ERROR
        respectively.

        With prefix mode is off, responses from the laser driver are not prefixed
        with a return code. This means that in the case for a serial write command
        without an expected return value, the driver will not send back a reply.


        Args:
            mode: whether to enable prefix mode (True) or disable it (False)

        """
        self._prefix_mode = mode  # mode needs to be set first before next query
        self.query(f"SYST:COMM:PFX {mode:d}")
        logger.info(f"Changed prefix mode to {mode}")

    @property
    def baudrate(self) -> int:
        """Gets the baudrate of the serial connection to the driver.

        The baudrate can be changed, but does require a serial reconnect

        ??? info "Currently supported baudrates are:"
            - 9600
            - 14400
            - 19200
            - 28800
            - 38400
            - 57600  **_default_**
            - 115200
            - 230400
            - 460800
            - 912600

        Returns:
            (int): baudrate currently in use

        """
        driver_baudrate = int(self.query("SYST:SER:BAUD?"))
        if driver_baudrate != self._serial.baudrate:
            logger.error(
                "There seems to be a baudrate mismatch between driver and connection"
                " baudrate settings"
            )
        return driver_baudrate

    @baudrate.setter
    def baudrate(self, new_baudrate: int) -> None:
        """Set the baudrate of the serial connection to the driver.

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
        needs to be set, by comparing with the current baudrate in use.
        If the new requested baudrate is different then it will set the new baudrate
        as follows:
            1. Instruct the driver to use a new baudrate
            2. Close the serial connection
            3. Change the serial connection attribute to use the new baudrate as well
            4. Reopen the serial connection

        Args:
            new_baudrate (int): new baudrate to use

        """
        # Input validation
        if not self._serial.is_open:
            return
        if new_baudrate == self._serial.baudrate:
            return
        if new_baudrate not in Constants.SUPPORTED_BAUDRATES:
            raise ValueError(f"The given baudrate {new_baudrate} is not supported.")

        # 1. Instruct driver to use new baudrate
        logger.info(
            f"Switching baudrates from {self._serial.baudrate} to {new_baudrate}."
        )
        self._serial.write(f"SYST:SER:BAUD {new_baudrate:d}\r\n".encode("ascii"))
        logger.debug(
            f"[baudrate_switch] Writing to serial: SYST:SER:BAUD {new_baudrate:d}"
        )
        # 2. Close serial connection
        logger.debug("[baudrate_switch] Closing serial connection")
        self._serial.close()
        # 3. Change serial connection baudrate attribute
        self._serial.baudrate = new_baudrate
        # 4. Reopen serial connection
        logger.debug("[baudrate_switch] Reopening serial connection with new baudrate")
        self._serial.open()

    @property
    def port(self) -> str:
        """Get the serial port currently used for communication.

        Returns:
            str: The name of the serial port in use.
        """
        return self._serial.port  # type: ignore


def list_comports() -> list[str]:
    """List all available COM ports on the system.

    `serial.tools.list_ports.comports` is used to list all available
    ports. In that regard this method is but a wrapper for it.

    Returns:
        List of available COM ports as strings sorted
        alphabetically in ascending order.
    """
    return sorted([port.device for port in serial.tools.list_ports.comports()])
