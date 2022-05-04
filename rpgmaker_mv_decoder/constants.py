"""`constants.py` Constants for use by modules"""

import click

RPG_MAKER_MV_MAGIC = bytes.fromhex("5250474d560000000003010000000000")
PNG_HEADER = bytes.fromhex("89504e470d0a1a0a0000000d49484452")
OCT_STREAM = "application/octet-stream"
IHDR_SECTION = b"IHDR"
NOT_A_PNG = "Invalid checksum"

CLI_SOURCE_STR = (
    "The source directory. For best results this should be the parent "
    "of the 'www' or 'img' directory."
)

CLI_DESTINATION_STR = (
    "The parent destination directory. This script will create a project "
    "directory under this path if it doesn't already exist."
)

CLI_DECODE_KEY_STR = (
    "The decoding key to use. This argument is optional. If the key is "
    "omitted it will be inferred (if possible) based on the file contents."
)

CLI_ENCODE_KEY_STR = "The encoding key to use."

CMD_HELP_DECODE = "Decodes RPGMaker files under <Source> directory to <Destination> directory."

CMD_HELP_ENCODE = "Encodes image and audio files under <Source> directory."

TYPE_HELP = (
    "Detect the file type and use the associated file extension. "
    "By default .rpgmvp becomes .png and .rpgmvo becomes .ogg regardless "
    "of the file contents."
)

CLICK_SRC_PATH = click.Path(exists=True, file_okay=False, resolve_path=True)
CLICK_DST_PATH = click.Path(exists=False, writable=True, file_okay=False, resolve_path=True)
