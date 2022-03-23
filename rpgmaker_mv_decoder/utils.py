#!/usr/bin/env python3
"""Main module."""
import os
from pathlib import Path, PurePath
from rpgmaker_mv_decoder.exceptions import FileFormatError
from typing import Dict, List, Tuple
import sys
import click
import struct
from uuid import UUID, uuid4
import magic
from binascii import crc32
RPG_MAKER_MV_MAGIC = "5250474d560000000003010000000000"
PNG_HEADER = "89504e470d0a1a0a0000000d49484452"
OCT_STREAM = "application/octet-stream"
IHDR_TEXT=b'IHDR'
NOT_A_PNG="Invalid checksum"

def int_xor(var: bytes, key: bytes) -> bytes:
    """`int_xor` integer xor

    Runs XOR on 2 bytes streams (must be less than 64 bytes)

    Args:
    - `var` (`bytes`): Input 1
    - `key` (`bytes`): Input 2

    Returns:
    - `bytes`: XOR of input 1 and input 2
    """
    key = key[:len(var)]
    int_var: int = int.from_bytes(var, sys.byteorder)
    int_key: int = int.from_bytes(key, sys.byteorder)
    int_enc: int = int_var ^ int_key
    return int_enc.to_bytes(len(var), sys.byteorder)

def read_header_and_id(file_header:bytes, png_checksum: bytes, binary_key: bytes, guessing: bool = False) -> bytes:
    """`read_header_and_id` _summary_

    _extended_summary_

    Args:
    - `file_header` (`bytes`): _description_
    - `png_checksum` (`bytes`): _description_
    - `binary_key` (`bytes`): _description_
    - `guessing` (`bool`, optional): _description_. Defaults to `False`.

    Raises:
    ``
    - `FileFormatError`: _description_
    `
    - `FileFormatError`: _description_

    Returns:
    - `bytes`: _description_
    """
    id:bytes
    header:bytes
    (id, header) = struct.unpack("!16s16s", file_header)
    if id.hex() != RPG_MAKER_MV_MAGIC:
        raise FileFormatError(f'"{id.hex()}" != "{RPG_MAKER_MV_MAGIC}"', "First 16 bytes look wrong on this file")
    if(guessing):
        (ihdr_data, crc) = struct.unpack("!13s4s", png_checksum)
        checksum = crc32(IHDR_TEXT + ihdr_data).to_bytes(4, 'big')
        if (checksum != crc):
            raise FileFormatError(NOT_A_PNG, "This file doesn't checksum correctly for a png image")
    return int_xor(binary_key, header)

def print_possible_keys(sorted_keys: Dict[bytes, int], count:int) -> None:
    """`print_possible_keys` _summary_

    _extended_summary_

    Args:
    - `sorted_keys` (`Dict[bytes, int]`): _description_
    - `count` (`int`): _description_
    """
    item: bytes = list(sorted_keys.keys())[0]
    ratio: float = sorted_keys[item]/(count - (len(sorted_keys) - 1))
    click.echo("%.2f%% confidence for images" % (((ratio)*100)))
    click.echo(f"Possible keys: {item} used in {sorted_keys[item]} of {count} images")
    for item in list(sorted_keys.keys())[1:10]:
        click.echo(f"               {item} used in {sorted_keys[item]} of {count} images")

def get_likely_key(keys: Dict[bytes, int], count):
    """`get_likely_key` _summary_

    _extended_summary_

    Args:
    - `keys` (`Dict[bytes, int]`): _description_
    - `count` (`_type_`): _description_

    Returns:
    - `_type_`: _description_
    """
    main_key:bytes = list(keys.keys())[0]
    if len(keys) != 1:
        # There's probably a better way...
        sorted_keys = dict(sorted(keys.items(), key=lambda item: item[1], reverse=True))
        main_key:bytes = list(sorted_keys.keys())[0]
        print_possible_keys(sorted_keys, len(keys), main_key, count)

    return main_key

def guess_at_key(src):
    """`guess_at_key` _summary_

    _extended_summary_

    Args:
    - `src` (`_type_`): _description_

    Returns:
    - `_type_`: _description_
    """
    # standard png header
    bKey:bytes = bytes.fromhex(PNG_HEADER)
    files: List[Path] = sorted(Path(src).glob('**/*.rpgmvp'))
    keys: Dict[bytes, int] = {}
    count: int = 0
    min_found: len(files) / 20
    if min_found < 50:
        min_found = 50

    with click.progressbar(files, label="Finding key") as bar:
        filename:Path
        for filename in bar:
            with click.open_file(filename, 'rb') as file:
                item: bytes
                try:
                    item = read_header_and_id(file.read(32), file.read(17), bKey, True).hex()
                except FileFormatError as ffe:
                    if ffe.expression != NOT_A_PNG:
                        click.echo(ffe.expression)
                    continue
                count += 1
                try:
                    keys[item] += 1
                except KeyError:
                    keys[item] = 1
                if count >= min_found and keys[item] == count:
                    break
    return get_likely_key(keys, count)

def update_src_dest(src: PurePath, dst:PurePath) -> Tuple[PurePath, PurePath]:
    """`update_src_dest` _summary_

    _extended_summary_

    Args:
    - `src` (`PurePath`): _description_
    - `dst` (`PurePath`): _description_

    Returns:
    - `Tuple[PurePath, PurePath]`: _description_
    """
    if Path(src).joinpath("img").exists():
        click.echo("Found 'img' in source path, using parent directory name")
        src = src.parent.parent
    elif Path(src).joinpath("www").exists():
        click.echo("Found 'www' in source path, using parent directory name")
        src = src.parent
    else:
        tmp_dir: UUID = uuid4()
        dst = dst.joinpath(str(tmp_dir))
    return (src, dst)

def get_file_ext(data: bytes) -> str:
    """`get_file_ext` _summary_

    _extended_summary_

    Args:
    - `data` (`bytes`): _description_

    Raises:
    ``
    - `FileFormatError`: _description_

    Returns:
    - `str`: _description_
    """
    filetype = magic.from_buffer(data, mime=True)
    if filetype == OCT_STREAM:
        raise FileFormatError('"%s" == "%s"' % (filetype, OCT_STREAM), "Found octlet stream, key is probably incorrect.")
    return '.'+filetype.split('/')[-1]


def decode_files(src: str, dst: str, key: str, file_types: bool):
    """`decode_files` decodes rpgmaker encoded files

    _extended_summary_

    Args:
    - `src` (`str`): _description_
    - `dst` (`str`): _description_
    - `key` (`str`): _description_
    - `file_types` (`bool`): _description_
    """
    bKey: bytes = bytes.fromhex(key)

    (source,dest) = update_src_dest(PurePath(src), PurePath(dst))

    click.echo('Reading from: %s' % click.format_filename(str(source.joinpath(PurePath(src).relative_to(source)))))
    click.echo('Writing to: %s' % click.format_filename(str(dest.joinpath(PurePath(src).relative_to(source)))))

    files:List[Path] = sorted(Path(src).glob('**/*.rpgmv[op]'))

    with click.progressbar(files, label="Decoding files") as bar:
        filename:Path
        for filename in bar:
            outputFile: PurePath = dest.joinpath(PurePath(filename).relative_to(source))
            result: bytes
            with click.open_file(filename, 'rb') as file:
                fileHeader: bytes = file.read(32)
                pngHeader: bytes = file.read(17)
                try:
                    result = read_header_and_id(fileHeader, pngHeader, bKey)
                    result += pngHeader
                    result += file.read()
                except FileFormatError as ffe:
                    click.echo(ffe.expression)
                    continue
            if(file_types):
                try:
                    outputFile = outputFile.with_suffix(get_file_ext(result))
                except FileFormatError:
                    click.echo("Found octlet stream, key is probably incorrect, skipping %s" % click.format_filename(str(filename)))
                    continue
            else:
                if outputFile.suffix == ".rpgmvp":
                    outputFile = outputFile.with_suffix(".png")
                if outputFile.suffix == ".rpgmvo":
                    outputFile = outputFile.with_suffix(".ogg")
            try:
                os.makedirs(outputFile.parent)
            except FileExistsError:
                pass
            with open(outputFile, mode='wb') as file:
                file.write(result)
