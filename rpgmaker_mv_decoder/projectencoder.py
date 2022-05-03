"""Class for encoding a project"""


from pathlib import Path, PurePath
from typing import List, TypeVar

import click
import magic

from rpgmaker_mv_decoder.callback import Callback
from rpgmaker_mv_decoder.constants import RPG_MAKER_MV_MAGIC
from rpgmaker_mv_decoder.project import Project
from rpgmaker_mv_decoder.utils import int_xor

_T = TypeVar("_T", bound="ProjectEncoder")


class ProjectEncoder(Project):
    """Class for encoding a project"""

    def __init__(
        self: _T,
        encoding_source: PurePath,
        destination: PurePath,
        key: str,
        encoding_callbacks: Callback = Callback(),
    ) -> _T:
        Project.__init__(self, encoding_source, destination, key, encoding_callbacks)

    def encode_header(self: _T, file_header: bytes) -> bytes:
        """`encode_header` Encode a file with a key

        Takes first 16 bytes and encodes per RPGMaker MV standard

        Args:
        - `file_header` (`bytes`): 16 bytes
        - `key` (`str`): Key to encode with

        Returns:
        - `bytes`: First 32 bytes of the encoded file
        """
        return RPG_MAKER_MV_MAGIC + int_xor(bytes.fromhex(self.key), file_header)

    def encode_file(self: _T, input_file: PurePath) -> bool:
        """`encode_file` Takes a path and encodes a file

        Args:
        - `self` (`Project`): Project object
        - `input_file` (`PurePath`): File to read and modify

        Returns:
        - `bool`: True if the operation should continue
        """
        output_file: PurePath = self.project_paths.output_directory.joinpath(
            PurePath(input_file).relative_to(self.project_paths.source)
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
        files: List[Path] = self.project_paths.all_files
        click.echo(f"Reading from: '{self.project_paths.source}'")
        click.echo(f"Writing to:   '{self.project_paths.output_directory}'")
        with click.progressbar(files, label="Encoding files") as all_files:
            filename: Path
            for filename in all_files:
                if self._callbacks.progressbar(all_files):
                    break
                if not self.encode_file(filename):
                    break
        self._callbacks.progressbar(None)
