"""`callback` module

Used to handle callbacks in a single object rather than multiple parameters
"""
from typing import Callable

from click._termui_impl import ProgressBar


def _default_progressbar_callback(_: ProgressBar) -> bool:
    return False


def _default_overwrite_callback(_: str) -> bool:
    return True


def _default_error_callback(_: str) -> bool:
    return False


def _default_warning_callback(_: str) -> bool:
    return False


class Callback:
    """`Callback` encapsulates all the callbacks that might be used during execution"""

    def __init__(
        self,
        progressbar_callback: Callable[[ProgressBar], bool] = _default_progressbar_callback,
        overwrite_callback: Callable[[str], bool] = _default_overwrite_callback,
        error_callback: Callable[[str], bool] = _default_error_callback,
        warning_callback: Callable[[str], bool] = _default_error_callback,
    ):
        self._progressbar_callback = progressbar_callback
        self._overwrite_callback = overwrite_callback
        self._error_callback = error_callback
        self._warning_callback = warning_callback

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
