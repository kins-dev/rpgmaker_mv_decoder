"""`callback` module

Used to handle callbacks in a single object rather than multiple parameters
"""
from typing import Callable, List, TypeVar

import click
from click._termui_impl import ProgressBar

from rpgmaker_mv_decoder import __version__ as VERSION
from rpgmaker_mv_decoder.messagetypes import MessageType
from rpgmaker_mv_decoder.promptresponse import PromptResponse

_T = TypeVar("_T", bound="Callbacks")


def show_version(ctx: click.Context, _, value: bool):
    """`show_version` Click callback that displays the version number to the user

    Args:
    - `ctx` (`click.Context`): context for options parsing
    - `_` (`_type_`): ignored
    - `value` (`bool`): if true, show the version number and exit
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"Version: {VERSION}")
    ctx.exit()


def _default_progressbar_callback(_: ProgressBar) -> bool:
    return False


def default_message_callback(
    level: MessageType,
    text: str,
) -> None:
    """`default_message_callback` default handling of messages

    Args:
    - `level` (`MessageType`): What kind of message this is
    - `text` (`str`): What to display
    """
    text = f"{level.get_message_header()}{text}"
    if level == MessageType.DEBUG:
        click.secho(text, bold=True, fg="blue")
    elif level == MessageType.INFO:
        click.echo(text)
    elif level == MessageType.WARNING:
        click.secho(text, bold=True, fg="yellow")
    elif level == MessageType.ERROR:
        click.secho(text, bold=True, fg="red")


def default_prompt_callback(
    message_type: MessageType = MessageType.DEBUG,
    message: str = "",
    responses: PromptResponse = PromptResponse.OK,
) -> bool:
    """`default_prompt_callback` default prompt

    Args:
    - `message_type` (`MessageType`, optional): What type of message is this. Defaults to\
      `MessageType.DEBUG`.
    - `message` (`str`, optional): What to display to the user. Defaults to `""`.
    - `responses` (`PromptResponse`, optional): What kind of repsones can the user give.\
      Defaults to `PromptResponse.OK`.

    Returns:
    - `bool`: `True` if the operation should run the action, `False` if the action should\
      be skipped and `None` if the operation should be canceled.
    """
    default_message_callback(message_type, message)
    if responses != PromptResponse.NONE:
        choice_list: List[str] = responses.get_responses()

        choice: str = click.prompt(
            "Do you want to do this?",
            default=choice_list[-1],
            type=click.Choice(choice_list, False),
        )
        if choice == "Cancel":
            return None
        if choice == "Skip":
            return False
        if choice == "No":
            return False
    return True


class Callbacks:
    """`Callbacks` encapsulates all the callbacks that might be used during execution"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        progressbar_callback: Callable[[ProgressBar], bool] = _default_progressbar_callback,
        prompt_callback: Callable[
            [MessageType, str, PromptResponse, bool], bool
        ] = default_prompt_callback,
        message_callback: Callable[[MessageType, str, bool], None] = default_message_callback,
    ) -> _T:
        """`Callbacks` constructor

        Args:
        - `progressbar_callback` (`Callable[ [ProgressBar], bool ]`, optional): How to display \
          progress. Defaults to `_default_progressbar_callback`.
        - `prompt_callback` (`Callable[ [MessageType, str, PromptResponse], bool ]`, optional):\
          How to ask the user for the appropriate action. Defaults to `default_prompt_callback`.
        - `message_callback` (`Callable[[MessageType, str], None]`, optional): What to do when\
          displaying messages. Defaults to `default_message_callback`.
        """
        self._progressbar_callback = progressbar_callback
        self._message_callback = message_callback
        self._prompt_callback = prompt_callback
        self._in_progress: bool = False

    # pylint: enable=too-many-arguments
    @property
    def progressbar(self: _T):
        """`progressbar` callback for updating the progress of the operation

        Returns:
        - `Callable[[ProgressBar], bool]`: Function to call. Progress data should \
          be specified via the parameter. If the user cancels the operation, this \
          should return `True`
        """
        return self._progressbar_callback

    @property
    def prompt(self: _T) -> Callable[[MessageType, str, PromptResponse], bool]:
        """`prompt` callback for asking the user a question

        Returns:
        - `Callable[[MessageType, str, PromptResponse], bool]`: Function to call. First\
          argument is the type of message, second is the message, third is the responses\
          a user can give.
        """
        return self._prompt_callback

    @property
    def message(self: _T) -> Callable[[MessageType, str], None]:
        """`message` callback for displaying a message to the user

        Returns:
        - `Callable[[MessageType, str], None]`: Function to call. First argument is the type of\
          message, second is the message
        """
        return self._message_callback

    def debug(self: _T, text: str) -> None:
        """`debug` helper function for printing a debug message

        Args:
        - `self` (`Callbacks`): callbacks object
        - `text` (`str`): text to display
        """
        self.message(MessageType.DEBUG, text)

    def info(self: _T, text: str) -> None:
        """`info` helper function for printing a info message

        Args:
        - `self` (`Callbacks`): callbacks object
        - `text` (`str`): text to display
        """
        self.message(MessageType.INFO, text)

    def warning(self: _T, text: str) -> None:
        """`warning` helper function for printing a warning message

        Args:
        - `self` (`Callbacks`): callbacks object
        - `text` (`str`): text to display
        """
        self.message(MessageType.WARNING, text)

    def error(self: _T, text: str) -> None:
        """`error` helper function for printing a error message

        Args:
        - `self` (`Callbacks`): callbacks object
        - `text` (`str`): text to display
        """
        self.message(MessageType.ERROR, text)
