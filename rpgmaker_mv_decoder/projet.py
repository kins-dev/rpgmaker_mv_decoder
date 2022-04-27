"""`project.py`

Module for dealing with RPGMaker projects
"""
import re
from pathlib import Path, PurePath
from typing import List, TypeVar

from regex import Pattern

from rpgmaker_mv_decoder.callback import Callback

_T = TypeVar("_T", bound="Project")


class Project:
    """Not in use yet"""

    def __init__(
        self: _T,
        source: PurePath = None,
        destination: PurePath = None,
        key: str = None,
        callbacks: Callback = Callback(),
    ) -> _T:
        self.source: PurePath = source
        self.destination: PurePath = destination
        self.key = key
        self._callbacks = callbacks

    def encode(self: _T):
        """Not ready yet"""

    def decode(self: _T):
        """Not ready yet"""

    def find_key(self: _T):
        """Not ready yet"""

    @property
    def key(self: _T) -> str:
        """Gets the `key` or returns `None` if the key is not valid"""
        return self._key if self._key else None

    @key.setter
    def key(self: _T, value: str):
        """Sets the `key`. Must be a 32 charcater hex string or the key will be set to None"""
        if value:
            pattern: Pattern = re.compile(r"^[0-9a-fA-F]{32}$")
            if pattern.match(value):
                self._key = value
                return
        self._key = None

    @property
    def destination(self: _T) -> PurePath:
        """Gets the `destination` path to use or returns `None` if the `destination` path is not
        valid"""
        return self._destination if self._destination else None

    @destination.setter
    def destination(self: _T, value: PurePath):
        """Sets the `destination` path. Value must exist on disk and be a directory. Passing an
        invalid path sets `destination` to `None`"""
        if value:
            try:
                destination_directory: Path = Path(value).resolve(strict=True)
                if destination_directory.is_dir():
                    self._destination = PurePath(destination_directory)
                    return
            except FileNotFoundError:
                pass
        self._destination = None
        return

    @property
    def source(self: _T) -> PurePath:
        """Gets the `source` path to use or returns `None` if the `source` path is not valid"""
        return self._source if self._source else None

    @source.setter
    def source(self: _T, value: PurePath):
        """Sets the `source` path. Value must exist on disk and be a directory. Passing an
        invalid path sets `source` to `None`"""
        if value:
            try:
                source_directory: Path = Path(value).resolve(strict=True)
                if source_directory.is_dir():
                    self._source = PurePath(source_directory)
                    return
            except FileNotFoundError:
                pass
        self._source = None
        return

    @property
    def encoded_images(self: _T) -> List[Path]:
        """`encoded_images` list of encoded images under the source path

        Creates a sorted list of `Path`s ending with ".rpgmvp" under the source path, or `None`
        if the source path is unset"""
        return sorted(Path(self.source).glob("**/*.rpgmvp")) if self.source else None

    @property
    def encoded_files(self: _T) -> List[Path]:
        """`encoded_files` list of encoded files under the source path

        Creates a sorted list of `Path`s ending with ".rpgmvp" or ".rpgmvo under the
        source path, or `None` if the source path is unset"""
        return sorted(Path(self.source).glob("**/*.rpgmv[op]")) if self.source else None

    @property
    def all_files(self: _T) -> List[Path]:
        """`all_files` list of all files under the source path

        Creates a sorted list of `Path`s that are files under the source path, or `None` if the
        source path is unset
        """
        if self.source is None:
            return None
        paths: List[Path] = sorted(Path(self.source).glob("**/*"))
        return [e for e in paths if e.is_file()]
