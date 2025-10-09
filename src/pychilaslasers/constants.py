"""Constants used throughout the PyChilasLasers library.

This module defines baud rates, error codes, and command lists used by the library.
"""


class Constants:
    """Constants used throughout the PyChilasLasers library."""

    DEFAULT_BAUDRATE = 460800
    TLM_INITIAL_BAUDRATE = (
        57600  # Initial baudrate the laser is set to when it is powered on.
    )
    SUPPORTED_BAUDRATES: tuple[int, ...] = (
        460800,
        57600,
        9600,
        14400,
        19200,
        28800,
        38400,
        115200,
        230400,
        912600,
    )

    # ERROR CODES THAT SHOULD TRIGGER A ERROR DIALOG (errors 14 to 23)
    CRITICAL_ERRORS: tuple[str, ...] = tuple(
        ["E0" + str(x) for x in range(14, 24)] + ["E0" + str(x) for x in range(30, 51)]
    )

    # Commands that can be replaced with a semicolon to speed up communication in
    # firmware
    SEMICOLON_COMMANDS: tuple[str, ...] = (
        "DRV:CYC:GW?",
        "DRV:CYC:GET?",
        "DRV:CYC:PUT",
        "DRV:CYC:SETT",
        "DRV:CYC:STRW",
    )
