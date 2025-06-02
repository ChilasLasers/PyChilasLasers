
class InvalidFileFormatError(Exception):
    """
    Exception raised for errors related to invalid file formats.
    Attributes:
        message (str): A description of the error.
        file_path (str | None): The path to the file that caused the error, if available.
        upstream_error (Exception | None): The original exception that caused this error, if available.
    """
    def __init__(self, message: str, file_path: str | None = None, upstream_error: Exception | None = None):
        """
        Initialize an InvalidFileFormatError instance.
        Args:
            message (str): A description of the error.
            file_path (str | None, optional): The path to the file that caused the error. Defaults to None.
            upstream_error (Exception | None, optional): The original exception that caused this error. Defaults to None.
        """

        super().__init__(message)
        self.file_path = file_path
        self.message = message
        self.upstream_error = upstream_error
