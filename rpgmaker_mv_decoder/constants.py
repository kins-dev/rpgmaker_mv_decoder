"""`constants.py` Constants for use by modules"""

import click

# File Sanity Check
RPG_MAKER_MV_MAGIC = b"RPGMV\x00\x00\x00\x00\x03\x01\x00\x00\x00\x00\x00"

# Lib Magic constants
OCT_STREAM = "application/octet-stream"

# PNG Constants
IHDR_SECTION = b"IHDR"
PNG_HEADER = b"\x89PNG\r\n\x1a\n\x00\x00\x00\r" + IHDR_SECTION
NOT_A_PNG = "Invalid checksum"

# HELP Constants
CLI_SOURCE_STR = (
    "The source directory. For best results this should be the parent of the 'www' or 'img' "
    "directory."
)

CLI_DESTINATION_STR = (
    "The parent destination directory. This script will create a project directory under this "
    "path if it doesn't already exist."
)

CLI_DECODE_KEY_STR = (
    "The decoding key to use. This argument is optional. If the key is omitted it will be "
    "inferred (if possible) based on the file contents."
)

CLI_ENCODE_KEY_STR = "The encoding key to use."

CLI_OVERWRITE_HELP = "Overwrite files without prompting"
CLI_VERSION_HELP = "Prints the version number"

CMD_HELP_DECODE = "Decodes RPGMaker files under <Source> directory to <Destination> directory."

CMD_HELP_ENCODE = "Encodes image and audio files under <Source> directory."

TYPE_HELP = (
    "Detect the file type and use the associated file extension. By default .rpgmvp becomes "
    ".png and .rpgmvo becomes .ogg regardless of the file contents."
)

# Click constants
CLICK_SRC_PATH = click.Path(exists=True, file_okay=False, resolve_path=True)
CLICK_DST_PATH = click.Path(exists=False, writable=True, file_okay=False, resolve_path=True)
