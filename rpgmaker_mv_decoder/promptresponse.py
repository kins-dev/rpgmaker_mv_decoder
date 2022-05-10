"""`promptresponse.py` How the user can respond to a prompt"""
from enum import Flag, auto
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
