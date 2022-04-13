#!/usr/bin/env python3
"""encode.py is the entry script for CLI encoding"""
from pprint import pprint
from typing import Dict

icon: Dict = {}
with open("assets/icon.png", "rb") as file:
    icon["format"] = "png"
    icon["data"] = file.read()
with open("icon_data.py", "w", encoding="utf-8") as file:
    file.write("# pylint: skip-file\n")
    file.write("ICON = ")
    pprint(icon, file, indent=1)
    file.write("\n")
