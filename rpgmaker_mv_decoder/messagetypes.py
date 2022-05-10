"""`messagetypes.py` Types of messages for the UI"""
from enum import Enum, auto
from tkinter import messagebox
from typing import TypeVar

_T = TypeVar("_T", bound="MessageType")


class MessageType(Enum):
    """`MessageType` Is a message debug, informational, warning or error"""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

    def get_message_header(self: _T) -> str:
        """`get_message_header` Header for this message type

        Returns:
        - `str`: Header to prepend to the message
        """
        if self == MessageType.ERROR:
            return "Error: "
        if self == MessageType.WARNING:
            return "Warning: "
        if self == MessageType.INFO:
            return ""
        return "Debug: "

    def get_icon(self: _T) -> str:
        """`get_icon` Returns the TK icon for this message type

        Returns:
        - `str`: The TK icon for this message type
        """
        if self == MessageType.ERROR:
            return messagebox.ERROR
        if self == MessageType.WARNING:
            return messagebox.WARNING
        if self == MessageType.INFO:
            return messagebox.INFO
        return messagebox.QUESTION
