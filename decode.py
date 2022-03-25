#!/usr/bin/env python3

from argparse import HelpFormatter
from gettext import gettext as _
import inspect
from rpgmaker_mv_decoder.utils import decode_files, guess_at_key
import sys
import click




class CmdHelp(click.Command):
    def format_help_text(self, ctx: click.Context, formatter: HelpFormatter):
        """Writes the help text to the formatter if it exists."""
        click.Command.format_help_text(self, ctx, formatter)
        with formatter.section(_("Arguments")):
            formatter.write_dl([('<Source>', "The source directory. For best results this should be the parent of the 'www' or 'img' directory."),
        ('<Destination>', "The parent destination directory. This script will create a project directory under this path if it doesn't already exist."),
        ('<Key>', "The decoding key to use. This argument is optional. If the key is omitted it will be inferred (if possible) based on the file contents.")])

@click.command(cls=CmdHelp, help="Decodes RPGMaker files under <Source> directory to <Destination> directory.")
@click.argument('source', type=click.Path(exists=True, file_okay=False, resolve_path=True), required=True,metavar='<Source>')
@click.argument('destination', type=click.Path(exists=True, writable=True, file_okay=False, resolve_path=True), required=True, metavar='<Destination>')
@click.argument('key', type=str, required=False,metavar='[<Key>]')
@click.option('--detect_type', is_flag=True, help="Detect the file type and use the associated file extension. By default .rpgmvp becomes .png and .rpgmvo becomes .ogg regardless of the file contents.")
#             '-------------'
def main(source: click.Path, destination: click.Path, key: str, detect_type: bool, help: bool) -> None:
    """`main` The main function

    Arguments are handled by Click.

    Args:
    - `source` (`click.Path`): Source directory
    - `destination` (`click.Path`): Destination directory
    - `key` (`str`): Hex key to use
    - `detect_type` (`bool`): If file should have extensions based on file contents
    """
    if key == None:
        key = guess_at_key(source)
    decode_files(source, destination, key, detect_type)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
