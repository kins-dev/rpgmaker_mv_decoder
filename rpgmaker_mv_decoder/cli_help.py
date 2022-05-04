"""Command line interface help classes"""

from argparse import HelpFormatter
from gettext import gettext as _

import click

from rpgmaker_mv_decoder.constants import (
    CLI_DECODE_KEY_STR,
    CLI_DESTINATION_STR,
    CLI_ENCODE_KEY_STR,
    CLI_SOURCE_STR,
)


class DecodeHelp(click.Command):
    """`DecodeHelp` help command override

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
                    ("<Source>", CLI_SOURCE_STR),
                    ("<Destination>", CLI_DESTINATION_STR),
                    ("<Key>", CLI_DECODE_KEY_STR),
                ]
            )


class EncodeHelp(click.Command):
    """`EncodeHelp` help command override

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
                    ("<Source>", CLI_SOURCE_STR),
                    ("<Destination>", CLI_DESTINATION_STR),
                    ("<Key>", CLI_ENCODE_KEY_STR),
                ]
            )
