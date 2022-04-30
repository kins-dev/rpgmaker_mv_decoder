"""`project.py`

Module for dealing with RPGMaker projects
"""
# pylint: disable=duplicate-code

import os
import re
import struct
import sys
from binascii import crc32
from pathlib import Path, PurePath
from time import sleep
from typing import List, TypeVar

import click
import magic

from rpgmaker_mv_decoder.callback import Callback
from rpgmaker_mv_decoder.constants import IHDR_SECTION, OCT_STREAM, RPG_MAKER_MV_MAGIC
from rpgmaker_mv_decoder.exceptions import FileFormatError, RPGMakerHeaderError
from rpgmaker_mv_decoder.projectpaths import ProjectPaths

_T = TypeVar("_T", bound="Project")


def __int_xor(var: bytes, key: bytes) -> bytes:
    """`int_xor` integer xor

    Runs XOR on 2 bytes streams (must be less than 64 bytes)

    Args:
    - `var` (`bytes`): Input 1
    - `key` (`bytes`): Input 2

    Returns:
    - `bytes`: XOR of input 1 and input 2

    """
    key = key[: len(var)]
    int_var: int = int.from_bytes(var, sys.byteorder)
    int_key: int = int.from_bytes(key, sys.byteorder)
    int_enc: int = int_var ^ int_key
    return int_enc.to_bytes(len(var), sys.byteorder)


def _get_file_ext(filename: Path, detect: bool, data: bytes) -> str:
    if detect:
        filetype: str = magic.from_buffer(data, mime=True)
        if filetype == OCT_STREAM:
            raise FileFormatError(
                f'"{filetype}" == "{OCT_STREAM}"',
                "Found octlet stream, key is probably incorrect.",
            )
        return "." + filetype.split("/")[-1]
    if filename.suffix == ".rpgmvp":
        return ".png"
    if filename.suffix == ".rpgmvo":
        return ".ogg"
    raise FileFormatError(
        f'"{filename.suffix}"',
        f'Unknown extension "{filename.suffix}"',
    )


def _is_png_image(png_ihdr_data: bytes) -> bool:
    ihdr_data: bytes
    crc: bytes
    (ihdr_data, crc) = struct.unpack("!13s4s", png_ihdr_data)
    checksum = crc32(IHDR_SECTION + ihdr_data).to_bytes(4, "big")
    if checksum != crc:
        return False
    return True


class Project:
    """Handles a project and runs operations"""

    def __init__(
        self: _T,
        source: PurePath = None,
        destination: PurePath = None,
        key: str = None,
        callbacks: Callback = Callback(),
    ) -> _T:
        self._project_paths: ProjectPaths = ProjectPaths(source, destination)
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

    def encode_header(self: _T, file_header: bytes) -> bytes:
        """`encode_header` Encode a file with a key

        Takes first 16 bytes and encodes per RPGMaker MV standard

        Args:
        - `file_header` (`bytes`): 16 bytes
        - `key` (`str`): Key to encode with

        Returns:
        - `bytes`: First 32 bytes of the encoded file
        """
        return RPG_MAKER_MV_MAGIC + __int_xor(bytes.fromhex(self.key), file_header)

    def encode_file(self: _T, input_file: PurePath) -> bool:
        """`encode_file` Takes a path and encodes a file

        Args:
        - `self` (`Project`): Project object
        - `input_file` (`PurePath`): File to read and modify

        Returns:
        - `bool`: True if the operation should continue
        """
        output_file: PurePath = self._project_paths.output_directory.joinpath(
            PurePath(input_file).relative_to(self._project_paths.source)
        )
        filetype: str
        with click.open_file(input_file, "rb") as file:
            file_header: bytes = file.read(16)
            data: bytes = file.read()
            filetype = magic.from_buffer(file_header + data, mime=True)
            data = self.encode_header(file_header) + data
        if filetype.startswith("image"):
            output_file = output_file.with_suffix(".rpgmvp")
        elif filetype.startswith("audio"):
            output_file = output_file.with_suffix(".rpgmvp")
        return self._save_file(output_file, data)

    def encode(self: _T):
        """Not ready yet"""
        files: List[Path] = self._project_paths.all_files
        click.echo(f"Reading from: '{self._project_paths.source}'")
        click.echo(f"Writing to:   '{self._project_paths.output_directory}'")
        with click.progressbar(files, label="Encoding files") as all_files:
            filename: Path
            for filename in all_files:
                if self._callbacks.progressbar(all_files):
                    break
                if not self.encode_file(filename):
                    break
        self._callbacks.progressbar(None)

    def decode_header(self: _T, file_header: bytes) -> bytes:
        """`decode_header` take a RPGMaker header and return the key or the actual file header

        Check's the first 16 bytes for the standard RPGMaker header, then drops them. Takes the
        next 16 bytes and either calculates the key based on a PNG image, or uses the specify key
        to decode. If png_ihdr_data is provided, checks that the IHDR section checksums correctly.

        Args:
        - `file_header` (`bytes`): First 32 bytes from the file, 16 bytes are the RPGMaker header,\
        followed by 16 bytes of the file header

        Raises:
        - `RPGMakerHeaderError`: The header doesn't match RPGMaker's header

        Returns:
        - `bytes`: If key was None, the key needed for a PNG image header, otherwise the decoded\
        file header.

        """
        file_id: bytes
        header: bytes
        (file_id, header) = struct.unpack("!16s16s", file_header)
        if file_id != RPG_MAKER_MV_MAGIC:
            raise RPGMakerHeaderError(
                f'"{file_id.hex()}" != "{RPG_MAKER_MV_MAGIC.hex()}"',
                "First 16 bytes of this file do not match the RPGMaker header, "
                "is this a RPGMaker file?",
            )
        return __int_xor(bytes.fromhex(self.key), header)

    def decode_file(self: _T, input_file: PurePath, detect_type: bool) -> bool:
        """`encode_file` Takes a path and decodes a file

        Args:
        - `self` (`Project`): Project object
        - `input_file` (`PurePath`): File to read and modify

        Returns:
        - `bool`: True if the operation should continue
        """
        output_file: PurePath = self._project_paths.output_directory.joinpath(
            PurePath(input_file).relative_to(self._project_paths.source)
        )
        data: bytes
        with click.open_file(input_file, "rb") as file:
            data: bytes = self.decode_header(file.read(32))
            data += file.read()
        output_file = output_file.with_suffix(_get_file_ext(input_file, detect_type, data))
        return self._save_file(output_file, data)

    def decode(
        self: _T,
        detect_type: bool,
    ):
        """Not ready yet"""
        click.echo(f"Reading from: '{self._project_paths.source}'")
        click.echo(f"Writing to:   '{self._project_paths.output_directory}'")
        files: List[Path] = self._project_paths.encoded_files
        with click.progressbar(files, label="Decoding files") as all_files:
            filename: Path
            for filename in all_files:
                if self._callbacks.progressbar(all_files):
                    break
                try:
                    if not self.decode_file(filename, detect_type):
                        break
                except RPGMakerHeaderError as ffe:
                    self._callbacks.warning(ffe.expression)
                except FileFormatError:
                    click.echo()
                    click.echo(
                        "Found octlet stream, key is probably incorrect, "
                        f"skipping {click.format_filename(str(filename))}"
                    )
        self._callbacks.progressbar(None)

    def find_key(self: _T):
        """Not ready yet"""
