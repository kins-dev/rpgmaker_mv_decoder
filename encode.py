#!/usr/bin/env python3
"""encode.py is the entry script for CLI encoding"""
import sys

import click

from rpgmaker_mv_decoder.cli_help import EncodeHelp
from rpgmaker_mv_decoder.constants import CLICK_DST_PATH, CLICK_SRC_PATH, CMD_HELP_ENCODE
from rpgmaker_mv_decoder.projectencoder import ProjectEncoder


@click.command(cls=EncodeHelp, help=CMD_HELP_ENCODE)
@click.argument("source", required=True, metavar="<Source>", type=CLICK_SRC_PATH)
@click.argument("destination", required=True, metavar="<Destination>", type=CLICK_DST_PATH)
@click.argument("key", type=str, required=True, metavar="<Key>")
def encode(source: click.Path = None, destination: click.Path = None, key: str = None) -> None:
    """`encode` The main function
    Args:
    - `source` (`click.Path`): Source directory
    - `destination` (`click.Path`): Destination directory
    - `key` (`str`): Hex key to use
    """
    if key is None:
        return 1
    ProjectEncoder(source, destination, key).encode()
    return 0


if __name__ == "__main__":
    sys.exit(encode())  # pragma: no cover
