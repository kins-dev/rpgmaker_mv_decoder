"""`clickdisplay.py` Simple helper class for the click progress bar"""

from pathlib import Path
from typing import Iterable, TypeVar

_T = TypeVar("_T", bound="ClickDisplay")


class ClickDisplay:
    """`ClickDisplay` class for handling item display in click progress bar"""

    def __init__(self, items: Iterable[Path]) -> _T:
        """`ClickDisplay` Constructor

        Args:
        - `items` (`Iterable[Path]`): Items being passed to the click progress bar
        """
        self._max_filename_len: int = 0
        self.setup(items)

    def setup(self, items: Iterable[Path]) -> None:
        """`setup` figures out the width of the display needed for filenames

        Args:
        - `items` (`Iterable[Path]`): Items being passed to the click progress bar
        """
        for item in items:
            self._max_filename_len = max(self._max_filename_len, len(item.name))

    def show_item(self: _T, item: Path) -> str:
        """`show_item` Pads the item name so it is shown correctly

        This is used as a callback in the click progress bar

        Args:
        - `item` (`Path`): Item to display

        Returns:
        - `str`: String to append to progress info. Trailing spaces will be removed.
        """
        return "[" + item.name.center(self._max_filename_len) + "]" if item else None
