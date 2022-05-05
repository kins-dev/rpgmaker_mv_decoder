"""`callback` module

Used to handle callbacks in a single object rather than multiple parameters
"""
from enum import Enum, Flag, auto
from typing import Callable, List

import click
from click._termui_impl import ProgressBar


class MessageType(Enum):
    """`MessageType` Is a message debug, informational, warning or error"""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class MessageResponse(Flag):
    """`MessageResponse` types of responses the user can give

    Shows OK unless NO is also specified, which then changes OK to YES
    """

    NONE = 0
    OK = auto()
    YES = OK
    NO = auto()
    YES_NO = YES | NO
    CANCEL = auto()
    OK_CANCEL = OK | CANCEL
    YES_NO_CANCEL = YES | NO | CANCEL

    def get_responses(self) -> List[str]:
        """`get_responses` List of response that this enum represents

        Returns:
        - `List[str]`: Possible user response to this message
        """
        responses: List[str] = []
        if self:
            if self & MessageResponse.OK:
                if self & MessageResponse.NO:
                    responses.append("Yes")
                else:
                    responses.append("OK")
            if self & MessageResponse.NO:
                responses.append("No")
            if self & MessageResponse.CANCEL:
                responses.append("Cancel")
        return responses


def _default_progressbar_callback(_: ProgressBar) -> bool:
    return False


def default_overwrite_callback(filename: str) -> bool:
    """`default_overwrite_callback` When files are about to be overwritten

    This is the default action when no callback is given

    Args:
    - `filename` (`str`): File to be overwitten

    Returns:
    - `bool`: `True` allows the file to be overwritten, `None` cancels the operation
    """
    choice: str = click.prompt(
        f"Do you want to overwrite {filename}?",
        default="Cancel",
        type=click.Choice(["Yes", "No", "Cancel"], False),
    )
    if choice == "Cancel":
        return None
    if choice == "Yes":
        return True
    return False


def _default_error_callback(_: str) -> bool:
    return False


def _default_warning_callback(_: str) -> bool:
    return False


def _default_info_callback(_: str) -> bool:
    return False


class Callbacks:
    """`Callbacks` encapsulates all the callbacks that might be used during execution"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        progressbar_callback: Callable[[ProgressBar], bool] = _default_progressbar_callback,
        overwrite_callback: Callable[[str], bool] = default_overwrite_callback,
        error_callback: Callable[[str], bool] = _default_error_callback,
        warning_callback: Callable[[str], bool] = _default_warning_callback,
        info_callback: Callable[[str], bool] = _default_info_callback,
    ):
        """`Callbacks` Callbacks on specific events

        Args:
        - `progressbar_callback` (`Callable[[ProgressBar], bool]`, optional): What to call when \
          the progress bar updates. Defaults to `_default_progressbar_callback`.
        - `overwrite_callback` (`Callable[[str], bool]`, optional): What to call when files are \
          about to be overwitten. Defaults to `_default_overwrite_callback`.
        - `error_callback` (`Callable[[str], bool]`, optional): What to call on error. Defaults \
          to `_default_error_callback`.
        - `warning_callback` (`Callable[[str], bool]`, optional): What to call on a warning. \
          Defaults to `_default_warning_callback`.
        - `info_callback` (`Callable[[str], bool]`, optional): What to call on an info message. \
          Defaults to `_default_info_callback`.

        Returns:
        - `Callbacks`: Object holding various callbacks
        """
        self._progressbar_callback = progressbar_callback
        self._overwrite_callback = overwrite_callback
        self._error_callback = error_callback
        self._warning_callback = warning_callback
        self._info_callback = info_callback

    # pylint: enable=too-many-arguments
    @property
    def progressbar(self):
        """`progressbar` callback for updating the progress of the operation

        Returns:
        - `Callable[[ProgressBar], bool]`: Function to call. Progress data should \
          be specified via the parameter. If the user cancels the operation, this \
          should return `True`
        """
        return self._progressbar_callback

    @property
    def overwrite(self):
        """`overwrite` callback executed when a file is about to be overwitten

        Returns:
        - `Callable[[str], bool]`: Function to call. Path to overwite should be specified \
          as the string. If the function returns `True` the file should be overwritten. If the \
          user cancels the operation this function should return None
        """
        return self._overwrite_callback

    @property
    def error(self):
        """`error` callback executed when an error occurs

        Returns:
        - `Callable[[str], bool]`: Function to call. Error message should be specified via \
          the parameter. If the user cancels the operation, this should return `True`
        """
        return self._error_callback

    @property
    def warning(self):
        """`warning` callback executed when an warning occurs

        Returns:
        - `Callable[[str], bool]`: Function to call. Warning message should be specified via \
          the parameter. If the user cancels the operation, this should return `True`
        """
        return self._warning_callback

    @property
    def info(self):
        """`info` callback executed when an info message occurs

        Returns:
        - `Callable[[str], bool]`: Function to call. Info message should be specified via \
          the parameter. If the user cancels the operation, this should return `True`
        """
        return self._info_callback
