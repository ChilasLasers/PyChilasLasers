import logging


class OperatingModeError(Exception):
    """
    Exception raised when an operation is attempted that is not allowed
    in the current operating mode.
    """
    def __init__(self, message="Operation not allowed in the current operating mode."):
        logging.getLogger(__name__).error(message)
        super().__init__(message)