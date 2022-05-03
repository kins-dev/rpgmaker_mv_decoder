"""`project.py`

Module for dealing with RPGMaker projects
"""
from pathlib import Path, PurePath
from typing import List, TypeVar
from uuid import UUID, uuid4

import click

_T = TypeVar("_T", bound="ProjectPaths")


class ProjectPaths:
    """Object that holds/validates project paths"""

    def __init__(
        self: _T,
        source: PurePath = None,
        destination: PurePath = None,
    ) -> _T:
        self.source: PurePath = source
        self.destination: PurePath = destination
        self._cached_output_directory: PurePath = None

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
            destination_directory: Path = Path(value).resolve(strict=False)
            if not destination_directory.exists() or destination_directory.is_dir():
                self._destination = PurePath(destination_directory)
                return
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
                    if source_directory.name == "audio":
                        source_directory = source_directory.parent
                    if source_directory.name == "img":
                        source_directory = source_directory.parent
                    if source_directory.name == "www":
                        source_directory = source_directory.parent
                    self._source = PurePath(source_directory)
                    return
            except FileNotFoundError:
                pass
        self._source = None
        return

    @property
    def output_directory(self: _T) -> PurePath:
        """`output_directory` returns the name of the output directory including the project
        name"""
        if self._cached_output_directory:
            return self._cached_output_directory
        if Path(self.source.joinpath("www")).exists():
            self._cached_output_directory = self.destination.joinpath(self.source.name)
        elif Path(self.source.joinpath("img")).exists():
            self._cached_output_directory = self.destination.joinpath(self.source.name)
        else:
            tmp_dir: UUID = uuid4()
            self._cached_output_directory = self.destination.joinpath(str(tmp_dir))
            click.echo(
                f"Unable to find 'www' or 'img' directly under '{self.source}',"
                " generating random project directory name"
            )
        return self._cached_output_directory

    @property
    def encoded_images(self: _T) -> List[Path]:
        """`encoded_images` list of encoded images under the source path

        Creates a sorted list of `Path` objects ending with ".rpgmvp" under the source path, or
        `None` if the source path is unset"""
        return sorted(Path(self.source).glob("**/*.rpgmvp")) if self.source else None

    @property
    def encoded_files(self: _T) -> List[Path]:
        """`encoded_files` list of encoded files under the source path

        Creates a sorted list of `Path` objects ending with ".rpgmvp" or ".rpgmvo under the
        source path, or `None` if the source path is unset"""
        return sorted(Path(self.source).glob("**/*.rpgmv[op]")) if self.source else None

    @property
    def all_files(self: _T) -> List[Path]:
        """`all_files` list of all files under the source path

        Creates a sorted list of `Path` objects that are files under the source path, or `None`
        if the source path is unset
        """
        if self.source is None:
            return None
        paths: List[Path] = sorted(Path(self.source).glob("**/*"))
        return [e for e in paths if e.is_file()]
