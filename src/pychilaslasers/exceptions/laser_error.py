"""Class representing errors received from the laser.

**Authors**: SDU
"""


class LaserError(Exception):  # noqa: D101
    def __init__(self, code: str, message: str) -> None:
        """Class representing errors received from the laser.

        Args:
            code (str): The error code sent by the laser. Typically a 1 but kept
                abstract to allow for future expansion.
            message (str): The error message.

        """
        self.code: str = code
        self.message: str = message

    def __str__(self) -> str:  # noqa: D105
        return f"LaserError {self.code}: {self.message}"
