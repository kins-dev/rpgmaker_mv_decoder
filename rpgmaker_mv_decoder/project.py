"""`project.py`

Module for dealing with RPGMaker projects
"""
# pylint: disable=duplicate-code

import os
import re
from abc import ABC
from pathlib import Path, PurePath
from typing import TypeVar

import click

from rpgmaker_mv_decoder.callbacks import Callbacks
from rpgmaker_mv_decoder.messagetypes import MessageType
from rpgmaker_mv_decoder.projectpaths import ProjectPaths
from rpgmaker_mv_decoder.promptresponse import PromptResponse

_T = TypeVar("_T", bound="Project")


class Project(ABC):
    """Handles a project and runs operations"""

    def __init__(
        self: _T,
        source_path: PurePath = None,
        destination_path: PurePath = None,
        key: str = None,
        callbacks: Callbacks = Callbacks(),
    ) -> _T:
        """`Project` constructor

        Args:
        - `source` (`PurePath`): Where to find the files
        - `destination` (`PurePath`): Where to save the files
        - `key` (`str`): Key to use
        - `callbacks` (`Callback`, optional): Callbacks to run on events.\
          Defaults to `Callback()`.
        - `overwrite` (`bool`, optional): if files should be overwritten. `None` will cause the\
          system to prompt the user. Defaults to `None`

        Returns:
        - `Project`: Object

        Notes:
        - This is an Abstract Base Class, do not use this directly
        """
        self.project_paths: ProjectPaths = ProjectPaths(source_path, destination_path)
        self.key: str = key
        self._callbacks: Callbacks = callbacks
        self._overwrite: bool = None

    def _save_file(self: _T, filename: PurePath, data: bytes) -> bool:
        """`_save_file` Saves the file to disk, calling the overwrite callback
        if the file exists already.

        Args:
        - `filename` (`PurePath`): File to save
        - `data` (`bytes`): What to write into the file

        Returns:
        - `bool`: True if the current operation should continue
        """
        overwrite: bool = True

        if Path(filename).exists():
            if self.overwrite is None:
                response = self._callbacks.prompt(
                    MessageType.WARNING,
                    f"""The file:
  {filename}
Is about to be overwritten.""",
                    PromptResponse.YES_NO_CANCEL,
                )
                if response is None:
                    return False
            else:
                overwrite = self.overwrite
        if overwrite:
            try:
                os.makedirs(filename.parent)
            except FileExistsError:
                pass
            with click.open_file(filename, mode="wb") as file:
                file.write(data)
        return True

    @property
    def overwrite(self: _T) -> bool:
        """if files should be overwritten. `None` will cause the system to prompt the user."""
        return self._overwrite

    @overwrite.setter
    def overwrite(self: _T, value: bool) -> bool:
        """if files should be overwritten. `None` will cause the system to prompt the user."""
        self._overwrite = value

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
