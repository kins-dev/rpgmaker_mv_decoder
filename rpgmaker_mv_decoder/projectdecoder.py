"""Class for decoding a project"""


import struct
from pathlib import Path, PurePath
from typing import List, TypeVar

import click
import magic

from rpgmaker_mv_decoder.callback import Callback
from rpgmaker_mv_decoder.constants import OCT_STREAM, RPG_MAKER_MV_MAGIC
from rpgmaker_mv_decoder.exceptions import FileFormatError, RPGMakerHeaderError
from rpgmaker_mv_decoder.project import Project
from rpgmaker_mv_decoder.utils import int_xor

_T = TypeVar("_T", bound="ProjectDecoder")


class ProjectDecoder(Project):
    """Handles a project and runs operations"""

    def __init__(
        self: _T,
        source: PurePath,
        destination: PurePath,
        key: str,
        callbacks: Callback = Callback(),
    ) -> _T:
        """`__init__` ProjectDecoder constructor

        Args:
        - `self` (`_T`): ProjectDecoder object
        - `source` (`PurePath`): Where to find the files to decode
        - `destination` (`PurePath`): Where to save the files to decode
        - `key` (`str`): Key to use when decoding
        - `callbacks` (`Callback`, optional): Callbacks to run on events.\
          Defaults to `Callback()`.

        Returns:
        - `_T`: _description_
        """
        Project.__init__(self, source, destination, key, callbacks)

    def _get_output_filename(self: _T, filename: Path, data: bytes = None) -> str:
        """`_get_output_filename` Returns a file name for the specified file

        If data is not `None`, uses libmagic to figure out the actual file type
        and place a proper extension on the file. Otherwise it uses the
        original name to generate the extension.

        Args:
        - `self` (`_T`): Project object
        - `filename` (`Path`): Original file path.
        - `data` (`bytes`, optional): File data (decoded) for libmagic. \
        Defaults to `None`.

        Raises:
        - `FileFormatError`: If libmagic can't determine the file type\
        or the existing file extension is unknown.

        Returns:
        - `str`: The decoded file extension
        """
        output_file: PurePath = self.project_paths.output_directory.joinpath(
            PurePath(filename).relative_to(self.project_paths.source)
        )
        if data:
            filetype: str = magic.from_buffer(data, mime=True)
            if filetype == OCT_STREAM:
                raise FileFormatError(
                    f'"{filetype}" == "{OCT_STREAM}"',
                    "Found octlet stream, key is probably incorrect.",
                )
            return output_file.with_suffix("." + filetype.split("/")[-1])
        if not filename:
            raise ValueError("data and filename are both None")
        if filename.suffix == ".rpgmvp":
            return output_file.with_suffix(".png")
        if filename.suffix == ".rpgmvo":
            return output_file.with_suffix(".ogg")
        raise FileFormatError(
            f'"{filename.suffix}"',
            f'Unknown extension "{filename.suffix}"',
        )

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
        return int_xor(bytes.fromhex(self.key), header)

    def decode_file(self: _T, input_file: PurePath, detect_type: bool) -> bool:
        """`encode_file` Takes a path and decodes a file

        Args:
        - `self` (`Project`): Project object
        - `input_file` (`PurePath`): File to read and modify

        Returns:
        - `bool`: True if the operation should continue
        """

        output_file = self._get_output_filename(input_file)
        data: bytes
        with click.open_file(input_file, "rb") as file:
            data: bytes = self.decode_header(file.read(32))
            data += file.read()
        if detect_type:
            output_file = self._get_output_filename(input_file, data)
        return self._save_file(output_file, data)

    def decode(
        self: _T,
        detect_type: bool,
    ):
        """Not ready yet"""
        click.echo(f"Reading from: '{self.project_paths.source}'")
        click.echo(f"Writing to:   '{self.project_paths.output_directory}'")
        files: List[Path] = self.project_paths.encoded_files
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
