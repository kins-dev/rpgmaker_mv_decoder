"""`project.py`

Module for dealing with RPGMaker projects
"""
# pylint: disable=duplicate-code

import os
import re
from pathlib import Path, PurePath
from time import sleep
from typing import TypeVar

import click

from rpgmaker_mv_decoder.callback import Callback
from rpgmaker_mv_decoder.projectpaths import ProjectPaths

_T = TypeVar("_T", bound="Project")


class Project:
    """Handles a project and runs operations"""

    def __init__(
        self: _T,
        source_path: PurePath = None,
        destination_path: PurePath = None,
        key: str = None,
        callbacks: Callback = Callback(),
    ) -> _T:
        self.project_paths: ProjectPaths = ProjectPaths(source_path, destination_path)
        self.key = key
        self._callbacks = callbacks

    def _save_file(self: _T, filename: PurePath, data: bytes) -> bool:
        """`_save_file` Saves the file to disk, calling the overwrite callback
        if the file exists already.

        Args:
        - `self` (`Project`): Project object
        - `filename` (`PurePath`): File to save
        - `data` (`bytes`): What to write into the file

        Returns:
        - `bool`: True if the current operation should continue
        """
        overwrite: bool = True
        # needed to prevent UI deadlock with TK
        sleep(0.01)
        if Path(filename).exists():
            overwrite = self._callbacks.overwrite(filename.name)
            if overwrite is None:
                return False
        if overwrite:
            try:
                os.makedirs(filename.parent)
            except FileExistsError:
                pass
            with click.open_file(filename, mode="wb") as file:
                file.write(data)
        return True

    def warning(self: _T, text: str) -> bool:
        """`Warning` Runs the warning callback

        Args:
        - `self` (`_T`): Project object
        - `text` (`str`): Text for warning

        Returns:
        - `bool`: `True` if the operation should continue
        """
        return self._callbacks.warning(text)

    @property
    def key(self: _T) -> str:
        """Gets the `key` or returns `None` if the key is not valid"""
        return self._key if self._key else None

    @key.setter
    def key(self: _T, value: str):
        """Sets the `key`. Must be a 32 charcater hex string or the key will be set to `None`"""
        if value:
            if re.compile(r"^[0-9a-fA-F]{32}$").match(value):
                self._key = value
                return
        self._key = None
