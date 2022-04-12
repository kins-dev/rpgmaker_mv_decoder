#!/usr/bin/env python3
"""Utility functions"""
import os
import struct
import sys
from binascii import crc32
from pathlib import Path, PurePath
from tkinter.ttk import Progressbar
from typing import Callable, Dict, List, Tuple
from uuid import UUID, uuid4

import click
import magic
from click._termui_impl import ProgressBar

from rpgmaker_mv_decoder.exceptions import (
    FileFormatError,
    NoValidFilesFound,
    PNGHeaderError,
    RPGMakerHeaderError,
)

RPG_MAKER_MV_MAGIC = bytes.fromhex("5250474d560000000003010000000000")
PNG_HEADER = "89504e470d0a1a0a0000000d49484452"
OCT_STREAM = "application/octet-stream"
IHDR_SECTION = b"IHDR"
NOT_A_PNG = "Invalid checksum"


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


def encode_header(file_header: bytes, key: str) -> bytes:
    """`encode_header` Encode a file with a key

    Takes first 16 bytes and encodes per RPGMaker MV standard

    Args:
    - `file_header` (`bytes`): 16 bytes
    - `key` (`str`): Key to encode with

    Returns:
    - `bytes`: First 32 bytes of the encoded file
    """
    return RPG_MAKER_MV_MAGIC + __int_xor(bytes.fromhex(key), file_header)


def read_header_and_decode(
    file_header: bytes, png_ihdr_data: bytes = None, key: str = PNG_HEADER
) -> bytes:
    """`read_header_and_decode` take a RPGMaker header and return the key or the actual file header

    Check's the first 16 bytes for the standard RPGMaker header, then drops them. Takes the next 16
    bytes and either calculates the key based on a PNG image, or uses the specify key to decode. If
    png_ihdr_data is provided, checks that the IHDR section checksums correctly.

    Args:
    - `file_header` (`bytes`): First 32 bytes from the file, 16 bytes are the RPGMaker header,\
    followed by 16 bytes of the file header
    - `png_ihdr_data` (`bytes`): Next 17 bytes for a PNG image to check the IHDR section
    - `key` (`str`): Key to use for xor, defaults to a standard PNG header if left unspecified

    Raises:
    - `RPGMakerHeaderError`: The header doesn't match RPGMaker's header
    - `PNGHeaderError`: The PNG's IHDR section doesn't checksum correctly

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
    if png_ihdr_data is not None:
        ihdr_data: bytes
        crc: bytes
        (ihdr_data, crc) = struct.unpack("!13s4s", png_ihdr_data)
        checksum = crc32(IHDR_SECTION + ihdr_data).to_bytes(4, "big")
        if checksum != crc:
            raise PNGHeaderError(
                f"'{checksum.hex()}' != '{crc.hex()}'",
                "This PNG's IHDR section doesn't checksum correctly, " "is this a PNG image?",
            )
    return __int_xor(bytes.fromhex(key), header)


def __print_possible_keys(sorted_keys: Dict[str, int], count: int) -> None:
    """`__print_possible_keys` Prints a list (maximum 10) of keys for decoding

    Prints a list of possible keys for this project to the user, shows the confidence
    as a percentage for each key found

    Args:
    - `sorted_keys` (`Dict[str, int]`): Keys sorted by frequency
    - `count` (`int`): Total number of files checked

    """
    item: str = list(sorted_keys.keys())[0]
    ratio: float = sorted_keys[item] / (count - (len(sorted_keys) - 1))
    click.echo(f"{ratio*100:.2f}% confidence for images")
    click.echo(f"Possible keys: {item} used in {sorted_keys[item]} of {count} images")
    for item in list(sorted_keys.keys())[1:10]:
        click.echo(f"               {item} used in {sorted_keys[item]} of {count} images")


def __get_likely_key(keys: Dict[str, int], count) -> str:
    """`__get_likely_key` Takes a list of keys and returns the most likely key

    Sorts the keys by frequency then returns the key that's used the most

    Args:
    - `keys` (`Dict[str, int]`): Keys found and how many times they showed up
    - `count` (`_type_`): Total number of files checked

    Returns:
    - `str`: Key to use for decoding

    """
    main_key: str = list(keys.keys())[0]
    if len(keys) != 1:
        # There's probably a better way...
        sorted_keys = dict(sorted(keys.items(), key=lambda item: item[1], reverse=True))
        main_key: bytes = list(sorted_keys.keys())[0]
        __print_possible_keys(sorted_keys, count)

    return main_key


def guess_at_key(src: Path, pb_cb: Callable[[Progressbar], bool] = None) -> str:
    """`guess_at_key` Check the path for PNG images and return the decoding key

    Finds image files under the specified path and looks for a key to decode all the files.
    This can fail if only a small number (less than 3) of the .rpgmvp files are .png images.

    Args:
    - `src` (`Path`): Path to search for .rpgmvp files
    - `pb_cb` (`Callable[[click._termui_impl.Progressbar], bool]`, optional): Callback to\
    display current progress. Call with `None` when bar is complete. Returns `True` if the\
    user has canceled the operation. Defaults to `None`.

    Raises:
    - `NoValidFilesFound`: If no valid PNG images are found

    Returns:
    - `str`: Decoding key

    """
    files: List[Path] = sorted(Path(src).glob("**/*.rpgmvp"))
    keys: Dict[str, int] = {}
    count: int
    with click.progressbar(files, label="Finding key") as all_files:
        count = _handle_files(pb_cb, keys, all_files)
    if pb_cb is not None:
        pb_cb(None)

    if count == 0:
        raise NoValidFilesFound(f"No png files found under: '{Path}'")
    return __get_likely_key(keys, count)


def _handle_files(pb_cb, keys, all_files: ProgressBar) -> int:
    skipped: bool = False
    min_found: int = max(10, all_files.length // 20)
    filename: Path
    count: int = 0
    item: bytes = None
    for filename in all_files:
        if pb_cb is not None:
            if pb_cb(all_files):
                break
        if skipped or (count >= min_found and item is not None and keys[item] == count):
            skipped = True
            # move the progress bar to 100%
            continue
        with click.open_file(filename, "rb") as file:
            try:
                item = read_header_and_decode(file.read(32), png_ihdr_data=file.read(17)).hex()
            except RPGMakerHeaderError as exception:
                # This is not expected, so make sure the user knows
                click.echo(exception.message)
                click.echo(exception.expression)
                continue
            except PNGHeaderError:
                # Expect this to happen if the file is not a png (eg. webp)
                # Just continue on, no need to tell the user
                continue
            count += 1
            _update_key_dict(keys, item)
    if skipped:
        _report_results(all_files, count, item)
    return count


def _update_key_dict(keys, item):
    try:
        keys[item] += 1
    except KeyError:
        keys[item] = 1


def _report_results(all_files: ProgressBar, count, item):
    percentage: float = (count * 100.0) / all_files.length
    click.echo(None)
    click.echo(
        f"Calculated the same key for {count}/{all_files.length} ({percentage:0.02f}%) files"
    )
    click.echo(f"Using '{item}' as the key")


def __update_src_dest(source: Path, destination: PurePath) -> Tuple[PurePath, PurePath]:
    """`__update_src_dest` Updates the source and destination paths

    Looks for the www and img directories, then uses that to generate the
    output directory name. If neither exists, then generates a new GUID
    as the output directory name.

    Args:
    - `source` (`Path`): Directory containing encoded files
    - `destination` (`PurePath`): Parent directory for the decoded files

    Returns:
    - `Tuple[PurePath, PurePath]`: Updated source and destination directories\
    based on the filesystem

    """
    if source.name == "www":
        source = source.parent
        destination = destination.joinpath(str(source.name))
    elif source.joinpath("img").exists():
        destination = destination.joinpath(str(source.name))
    elif source.joinpath("www").exists():
        destination = destination.joinpath(source.name)
    else:
        tmp_dir: UUID = uuid4()
        destination = destination.joinpath(str(tmp_dir))
        click.echo(
            f"Unable to find 'www' or 'img' directly under '{source}',"
            " generating random project directory name"
        )
    return (PurePath(source), PurePath(destination))


def get_file_ext(data: bytes) -> str:
    """`get_file_ext` Returns a file extension based on the file contents

    Uses libmagic to figure out the actual file type and place a proper
    extension on the file

    Args:
    - `data` (`bytes`): File data

    Raises:
    - `FileFormatError`: Error if the file type is unknown

    Returns:
    - `str`: Extension for the file

    """
    filetype = magic.from_buffer(data, mime=True)
    if filetype == OCT_STREAM:
        raise FileFormatError(
            f'"{filetype}" == "{OCT_STREAM}"',
            "Found octlet stream, key is probably incorrect.",
        )
    return "." + filetype.split("/")[-1]


def decode_files(
    src: str,
    dst: str,
    key: str,
    detect_type: bool,
    pb_cb: Callable[[Progressbar], bool] = None,
) -> None:
    """`decode_files` Decodes the files

    Finds all rpgmvp and rpgmvo files and decodes them

    Args:
    - `src` (`str`): Source directory to search
    - `dst` (`str`): Destination directory for output
    - `key` (`str`): Key to use for decoding
    - `detect_type` (`bool`): If file extensions should be detected from the file contents
    - `pb_cb` (`Callable[[click._termui_impl.Progressbar], bool]`, optional): Callback to\
    display current progress. Call with `None` when bar is complete. Returns `True` if the\
    user has canceled the operation. Defaults to `None`.
    """
    # pylint: disable=too-many-locals
    source_dir = Path(src).resolve()
    target_dir = Path(dst).resolve()
    (source, destination) = __update_src_dest(source_dir, target_dir)

    click.echo(f"Reading from: '{source}'")
    click.echo(f"Writing to:   '{destination}'")

    files: List[Path] = sorted(source_dir.glob("**/*.rpgmv[op]"))

    with click.progressbar(files, label="Decoding files") as all_files:
        filename: Path
        for filename in all_files:
            if pb_cb is not None:
                if pb_cb(all_files):
                    break
            output_file: PurePath = destination.joinpath(PurePath(filename).relative_to(source))
            result: bytes
            with click.open_file(filename, "rb") as file:
                file_header: bytes = file.read(32)
                try:
                    result = read_header_and_decode(file_header, key=key)
                    result += file.read()
                except FileFormatError as ffe:
                    click.echo(ffe.expression)
                    continue
            if detect_type:
                try:
                    output_file = output_file.with_suffix(get_file_ext(result))
                except FileFormatError:
                    click.echo()
                    click.echo(
                        "Found octlet stream, key is probably incorrect, "
                        f"skipping {click.format_filename(str(filename))}"
                    )
                    continue
            else:
                output_file = _get_std_ext(output_file)
            _save_file(output_file, result)
    if pb_cb is not None:
        pb_cb(None)


def encode_files(
    src: str,
    dst: str,
    key: str,
    pb_cb: Callable[[Progressbar], bool] = None,
) -> None:
    """`encode_files` Encodes the files

    Finds all images and audio files and encodes them

    Args:
    - `src` (`str`): Source directory to search
    - `dst` (`str`): Destination directory for output
    - `key` (`str`): Key to use for encoding
    - `pb_cb` (`Callable[[click._termui_impl.Progressbar], bool]`, optional): Callback to\
    display current progress. Call with `None` when bar is complete. Returns `True` if the\
    user has canceled the operation. Defaults to `None`.
    """
    # pylint: disable=too-many-locals
    source_dir = Path(src).resolve()
    target_dir = Path(dst).resolve()
    (source, destination) = __update_src_dest(source_dir, target_dir)

    click.echo(f"Reading from: '{source}'")
    click.echo(f"Writing to:   '{destination}'")

    files: List[Path] = sorted(source_dir.glob("**/*.*"))

    with click.progressbar(files, label="Encoding files") as all_files:
        filename: Path
        for filename in all_files:
            if pb_cb is not None:
                if pb_cb(all_files):
                    break
            output_file: PurePath = destination.joinpath(PurePath(filename).relative_to(source))
            filetype: str
            with click.open_file(filename, "rb") as file:

                file_header: bytes = file.read(16)
                data: bytes = file.read()
                filetype = magic.from_buffer(file_header + data, mime=True)
                data = encode_header(file_header, key=key) + data
            if filetype.startswith("image"):
                output_file = output_file.with_suffix(".rpgmvp")
            elif filetype.startswith("audio"):
                output_file = output_file.with_suffix(".rpgmvp")
            _save_file(output_file, data)
    if pb_cb is not None:
        pb_cb(None)


def _get_std_ext(output_file):
    if output_file.suffix == ".rpgmvp":
        output_file = output_file.with_suffix(".png")
    if output_file.suffix == ".rpgmvo":
        output_file = output_file.with_suffix(".ogg")
    return output_file


def _save_file(output_file, result):
    try:
        os.makedirs(output_file.parent)
    except FileExistsError:
        pass
    with open(output_file, mode="wb") as file:
        file.write(result)
