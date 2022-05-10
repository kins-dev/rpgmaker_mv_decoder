#!/usr/bin/env python3
"""encode.py is the entry script for CLI encoding"""
import sys

import click

from rpgmaker_mv_decoder.callbacks import show_version
from rpgmaker_mv_decoder.cli_help import EncodeHelp
from rpgmaker_mv_decoder.constants import (
    CLI_OVERWRITE_HELP,
    CLI_VERSION_HELP,
    CLICK_DST_PATH,
    CLICK_SRC_PATH,
    CMD_HELP_ENCODE,
)
from rpgmaker_mv_decoder.projectencoder import ProjectEncoder


@click.command(cls=EncodeHelp, help=CMD_HELP_ENCODE)
@click.argument("source", required=True, metavar="<Source>", type=CLICK_SRC_PATH)
@click.argument("destination", required=True, metavar="<Destination>", type=CLICK_DST_PATH)
@click.argument("key", type=str, required=True, metavar="<Key>")
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=show_version,
    help=CLI_VERSION_HELP,
)
@click.option("--overwrite", is_flag=True, help=CLI_OVERWRITE_HELP)
def encode(
    source: click.Path = None,
    destination: click.Path = None,
    key: str = None,
    overwrite: bool = False,
) -> None:
    """`encode` The main function
    Args:
    - `source` (`click.Path`): Source directory
    - `destination` (`click.Path`): Destination directory
    - `key` (`str`): Hex key to use
    - `overwrite` (`bool`): if files should be overwritten without prompting
    """
    if key is None:
        return 1
    encoder: ProjectEncoder = ProjectEncoder(source, destination, key)
    if overwrite:
        encoder.overwrite = True
    encoder.encode()
    return 0


if __name__ == "__main__":
    sys.exit(encode())  # pragma: no cover
