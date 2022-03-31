"""Custom Exception Types"""


class Error(Exception):
    """Base class for exceptions in this module.

    Attributes:
    - `message`: Explanation of the error
    """

    def __init__(self, message: str):
        """`__init__` constructor

        Args:
        - `message` (`str`): Explanation of the error
        """
        Exception.__init__(self)
        self.message: str = message


class NoValidFilesFound(Error):
    """Exception raised when no files are found. Based on `Error` class

    Attributes:
    - `message`: Explanation of the error
    """


class FileFormatError(Error):
    """Exception raised for errors in the input. Based on `Error` class

    Attributes:
    - `expression`: Input expression in which the error occurred
    - `message`: Explanation of the error
    """

    def __init__(self, expression: str, message: str):
        """`__init__` constructor

        _extended_summary_

        Args:
        - `expression` (`str`): Input expression in which the error occurred
        - `message` (`str`): Explanation of the error
        """
        self.expression: str = expression
        Error.__init__(self, message)


class PNGHeaderError(FileFormatError):
    """Exception raised for PNG images that when the IHDR section doesn't
    checksum correctly.

    Attributes:
    - `expression` -- Input expression in which the error occurred
    - `message` -- Explanation of the error
    """


class RPGMakerHeaderError(FileFormatError):
    """Exception raised for files missing the RPGMaker MV header.

    Attributes:
    - `expression` -- Input expression in which the error occurred
    - `message` -- Explanation of the error
    """
