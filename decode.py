#!/usr/bin/env python3
"""decode.py is the entry script for CLI decoding"""
# pylint: disable=duplicate-code

import sys
from argparse import HelpFormatter
from gettext import gettext as _

import click

from rpgmaker_mv_decoder.project import Project
from rpgmaker_mv_decoder.utils import guess_at_key

SOURCE_STR = (
    "The source directory. For best results this should be the parent "
    "of the 'www' or 'img' directory."
)
DESTINATION_STR = (
    "The parent destination directory. This script will create a project "
    "directory under this path if it doesn't already exist."
)
KEY_STR = (
    "The decoding key to use. This argument is optional. If the key is "
    "omitted it will be inferred (if possible) based on the file contents."
)


class CmdHelp(click.Command):
    """`CmdHelp` help command override

    Used to customize click help
    """

    def format_help_text(self, ctx: click.Context, formatter: HelpFormatter):
        """`format_help_text` formats the help

        Override that adds arguments to the help properly

        Args:
        - `ctx` (`click.Context`): context for click
        - `formatter` (`HelpFormatter`): formatter to use
        """
        click.Command.format_help_text(self, ctx, formatter)
        with formatter.section(_("Arguments")):
            formatter.write_dl(
                [
                    ("<Source>", SOURCE_STR),
                    ("<Destination>", DESTINATION_STR),
                    ("<Key>", KEY_STR),
                ]
            )


TYPE_HELP = (
    "Detect the file type and use the associated file extension. "
    "By default .rpgmvp becomes .png and .rpgmvo becomes .ogg regardless "
    "of the file contents."
)

CMD_HELP = "Decodes RPGMaker files under <Source> directory to <Destination> directory."


@click.command(cls=CmdHelp, help=CMD_HELP)
@click.argument(
    "source",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=True,
    metavar="<Source>",
)
@click.argument(
    "destination",
    type=click.Path(exists=True, writable=True, file_okay=False, resolve_path=True),
    required=True,
    metavar="<Destination>",
)
@click.argument("key", type=str, required=False, metavar="[<Key>]")
@click.option("--detect_type", is_flag=True, help=TYPE_HELP)
#             '-------------'
def main(
    source: click.Path = None,
    destination: click.Path = None,
    key: str = None,
    detect_type: bool = False,
) -> None:
    """`main` The main function

    Arguments are handled by Click.

    Args:
    - `source` (`click.Path`): Source directory
    - `destination` (`click.Path`): Destination directory
    - `key` (`str`): Hex key to use
    - `detect_type` (`bool`): If file should have extensions based on file contents
    """
    if key is None:
        key = guess_at_key(source)
    Project(source, destination, key).decode(detect_type)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
