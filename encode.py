#!/usr/bin/env python3
"""encode.py is the entry script for CLI encoding"""
import sys
from argparse import HelpFormatter
from gettext import gettext as _

import click

from rpgmaker_mv_decoder.projectencoder import ProjectEncoder

# pylint: disable=duplicate-code

SOURCE_STR = (
    "The source directory. For best results this should be the parent "
    "of the 'www' or 'img' directory."
)
DESTINATION_STR = (
    "The parent destination directory. This script will create a project "
    "directory under this path if it doesn't already exist."
)
KEY_STR = "The encoding key to use."


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


CMD_HELP = "Encodes image and audio files under <Source> directory."


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
@click.argument("key", type=str, required=True, metavar="<Key>")
def main(source: click.Path = None, destination: click.Path = None, key: str = None) -> None:
    """`main` The main function

    Arguments are handled by Click.

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
    sys.exit(main())  # pragma: no cover
