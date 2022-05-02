"""Class for decoding a project"""


import struct
from binascii import crc32
from pathlib import Path, PurePath
from typing import Dict, List, TypeVar

import click
from click._termui_impl import ProgressBar

from rpgmaker_mv_decoder.callback import Callback
from rpgmaker_mv_decoder.constants import IHDR_SECTION, PNG_HEADER, RPG_MAKER_MV_MAGIC
from rpgmaker_mv_decoder.exceptions import NoValidFilesFound
from rpgmaker_mv_decoder.project import Project
from rpgmaker_mv_decoder.projectpaths import ProjectPaths
from rpgmaker_mv_decoder.utils import int_xor

_T = TypeVar("_T", bound="ProjectKeyFinder")


def _is_png_image(png_ihdr_data: bytes) -> bool:
    ihdr_data: bytes
    crc: bytes
    (ihdr_data, crc) = struct.unpack("!13s4s", png_ihdr_data)
    checksum = crc32(IHDR_SECTION + ihdr_data).to_bytes(4, "big")
    if checksum != crc:
        return False
    return True


class ProjectKeyFinder(Project):
    """Handles finding a project key"""

    def __init__(
        self: _T,
        source: PurePath,
        callbacks: Callback = Callback(),
    ) -> _T:
        Project.__init__(self, ProjectPaths(source, None), None, callbacks)
        self._keys: Dict[str, int] = {}
        self._main_key: bytes = None
        self._count: int = 0
        self._keys_modified = False

    @property
    def keys(self: _T) -> Dict[str, int]:
        """`keys` sorted dictionary of possible keys for this project"""
        if self._keys_modified:
            self._keys = dict(sorted(self._keys.items(), key=lambda item: item[1], reverse=True))
            self._keys_modified = False
        return self._keys

    @keys.setter
    def keys(self: _T, value: str):
        self._keys_modified = True
        try:
            self._keys[value] += 1
        except KeyError:
            self._keys[value] = 1

    def __print_possible_keys(self: _T) -> None:
        """`__print_possible_keys` Prints a list (maximum 10) of keys for decoding

        Prints a list of possible keys for this project to the user, shows the confidence
        as a percentage for each key found

        Args:
        - `sorted_keys` (`Dict[str, int]`): Keys sorted by frequency
        - `count` (`int`): Total number of files checked

        """
        item: str = list(self.keys.keys())[0]
        ratio: float = self.keys[item] / (self._count - (len(self.keys) - 1))
        click.echo(f"{ratio*100:.2f}% confidence for images")
        click.echo(f"Possible keys: {item} used in {self.keys[item]} of {self._count} images")
        for item in list(self.keys.keys())[1:10]:
            click.echo(f"               {item} used in {self.keys[item]} of {self._count} images")

    def __get_likely_key(self: _T) -> None:
        """`__get_likely_key` Takes a list of keys and returns the most likely key

        Sorts the keys by frequency then returns the key that's used the most

        Args:
        - `keys` (`Dict[str, int]`): Keys found and how many times they showed up
        - `count` (`_type_`): Total number of files checked

        Returns:
        - `str`: Key to use for decoding

        """
        self.key = list(self.keys.keys)[0]
        if len(self.keys) != 1:
            self.__print_possible_keys()

    def _report_results(self: _T, all_files: ProgressBar, checked: int, item):
        files_skipped: int = checked - self._count
        percentage: float = (self._count * 100.0) / all_files.length
        click.echo(None)
        click.echo(f"Found {files_skipped} files ending with .rpgmvp that were not PNG images")
        click.echo(
            f"Found the same key for {self._count}/{all_files.length} ({percentage:0.02f}%) files"
        )
        click.echo(f"Using '{item}' as the key")

    def _handle_files(self: _T, all_files: ProgressBar) -> int:
        min_found: int = max(9, all_files.length // 20) + 1
        filename: Path
        count: int = 0
        checked: int = 0
        for filename in all_files:
            item: str = None
            if self._callbacks.progressbar(all_files):
                break

            with click.open_file(filename, "rb") as file:
                checked += 1
                rpgmaker_header = file.read(16)
                file_header = file.read(16)
                png_ihdr = file.read(17)
                if rpgmaker_header != RPG_MAKER_MV_MAGIC:
                    continue
                if not _is_png_image(png_ihdr):
                    continue
                item = int_xor(file_header, PNG_HEADER).hex()
                count += 1
                self.keys = item
                if len(self.keys) == 1 and count >= min_found:
                    all_files.update(all_files.length - count)
                    self._report_results(all_files, checked, item)
                    break

        self._callbacks.progressbar(None)
        return count

    def guess_at_key(self: _T) -> str:
        """`guess_at_key` Check the path for PNG images and return the decoding key

        Finds image files under the specified path and looks for a key to decode all the files.
        This can fail if only a small number (less than 3) of the .rpgmvp files are .png images.

        Args:
        - `src` (`Path`): Path to search for .rpgmvp files
        - `callbacks` (`Callback`, optional): Callbacks to use for the UI. Defaults to an empty\
        set of callbacks

        Raises:
        - `NoValidFilesFound`: If no valid PNG images are found

        Returns:
        - `str`: Decoding key

        """
        files: List[Path] = sorted(Path(self._project_paths.source).glob("**/*.rpgmvp"))
        with click.progressbar(files, label="Finding key") as all_files:
            self._count = self._handle_files(all_files)

        if self._count == 0:
            raise NoValidFilesFound(f"No png files found under: '{Path}'")
        self.__get_likely_key()
        return self.key
