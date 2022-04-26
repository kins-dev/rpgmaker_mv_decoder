"""`project.py`

Module for dealing with RPGMaker projects
"""
from pathlib import PurePath
from typing import TypeVar

from rpgmaker_mv_decoder.callback import Callback

_T = TypeVar("_T", bound="Project")


class Project:
    """Not in use yet"""

    def __init__(
        self: _T,
        source: PurePath,
        destination: PurePath,
        key: str = None,
        callbacks: Callback = Callback(),
    ) -> _T:
        self._source = source
        self._destination = destination
        self._key = key
        self._callbacks = callbacks

    def encode(self: _T):
        """pass"""

    def decode(self: _T):
        """pass"""
