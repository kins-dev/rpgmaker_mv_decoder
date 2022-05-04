#!/usr/bin/env python3
"""decode.py is the entry script for CLI decoding"""
import sys

import click

from rpgmaker_mv_decoder.cli_help import DecodeHelp
from rpgmaker_mv_decoder.constants import CLICK_DST_PATH, CLICK_SRC_PATH, CMD_HELP_DECODE, TYPE_HELP
from rpgmaker_mv_decoder.projectdecoder import ProjectDecoder
from rpgmaker_mv_decoder.projectkeyfinder import ProjectKeyFinder


@click.command(cls=DecodeHelp, help=CMD_HELP_DECODE)
@click.argument("source", required=True, metavar="<Source>", type=CLICK_SRC_PATH)
@click.argument("destination", required=True, metavar="<Destination>", type=CLICK_DST_PATH)
@click.argument("key", type=str, required=False, metavar="[<Key>]")
@click.option("--detect_type", is_flag=True, help=TYPE_HELP)
def decode(
    source: click.Path = None,
    destination: click.Path = None,
    key: str = None,
    detect_type: bool = False,
) -> None:
    """`decode` The main function

    Args:
    - `source` (`click.Path`): Source directory
    - `destination` (`click.Path`): Destination directory
    - `key` (`str`, optional): Hex key to use. Defaults to None
    - `detect_type` (`bool`): If file should have extensions based on file contents
    """
    if key is None:
        key = ProjectKeyFinder(source).find_key()
    ProjectDecoder(source, destination, key).decode(detect_type)
    return 0


if __name__ == "__main__":
    sys.exit(decode())  # pragma: no cover
