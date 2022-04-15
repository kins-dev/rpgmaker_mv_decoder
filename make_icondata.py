#!/usr/bin/env python3
"""encode.py is the entry script for CLI encoding"""
from pprint import pprint
from typing import Dict

icon: Dict = {}
with open("icon_data.py", "w", encoding="utf-8") as output:
    output.write("# pylint: skip-file\n")
    output.write("TITLE_BAR_ICON = ")
    with open("assets/icon.png", "rb") as file:
        icon["format"] = "png"
        icon["data"] = file.read()
    pprint(icon, output, indent=1)
    output.write("\n")
    output.write("ABOUT_ICON = ")
    with open("assets/about.png", "rb") as file:
        icon["format"] = "png"
        icon["data"] = file.read()

    pprint(icon, output, indent=1)
    output.write("\n")
