"""`promptresponse.py` How the user can respond to a prompt"""
from enum import Flag, auto
from tkinter import messagebox
from typing import List, TypeVar

_T = TypeVar("_T", bound="PromptResponse")


class PromptResponse(Flag):
    """`PromptResponse` types of responses the user can give

    Show `OK` unless `NO` is also specified, which then `OK` should be `YES`
    """

    NONE = 0
    OK = auto()
    YES = OK
    NO = auto()
    SKIP = auto()
    YES_NO = YES | NO
    YES_SKIP = YES | SKIP
    CANCEL = auto()
    OK_CANCEL = OK | CANCEL
    YES_NO_CANCEL = YES | NO | CANCEL
    YES_SKIP_CANCEL = YES | SKIP | CANCEL

    def get_responses(self: _T) -> List[str]:
        """`get_responses` List of response that this enum represents

        Returns:
        - `List[str]`: Possible user response to this message
        """
        responses: List[str] = []
        if self:
            if self & PromptResponse.OK:
                if self & PromptResponse.NO or self & PromptResponse.SKIP:
                    responses.append("Yes")
                else:
                    responses.append("OK")
            if self & PromptResponse.NO:
                responses.append("No")
            if self & PromptResponse.SKIP:
                responses.append("Skip")
            if self & PromptResponse.CANCEL:
                responses.append("Cancel")
        return responses

    def get_messagebox_response(self: _T) -> str:
        """`get_messagebox_response` gets the TK messagebox button set for this response

        Returns:
        - `str`: The TK messagebox button set for this response. None if nothing matches
        """
        if self == PromptResponse.YES_NO_CANCEL:
            return messagebox.YESNOCANCEL
        if self == PromptResponse.YES_NO:
            return messagebox.YESNO
        if self == PromptResponse.OK_CANCEL:
            return messagebox.OKCANCEL
        if self == PromptResponse.OK:
            return messagebox.OK
        return None
