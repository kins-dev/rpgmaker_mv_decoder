.. code-block:: none
    :emphasize-lines: 1

    Usage: decode.py [OPTIONS] <Source> <Destination> [<Key>]

      Decodes RPGMaker files under <Source> directory to <Destination> directory.

    Arguments:
      <Source>       The source directory. For best results this should be the
                     parent of the 'www' or 'img' directory.
      <Destination>  The parent destination directory. This script will create a
                     project directory under this path if it doesn't already
                     exist.
      <Key>          The decoding key to use. This argument is optional. If the
                     key is omitted it will be inferred (if possible) based on the
                     file contents.

    Options:
      --find_types  Put an extension on the file extension based on the content.
                    By default .rpgmvp becomes .png and .rpgmvo becomes .ogg
                    regardless of the file contents.
      --help        Show this message and exit.
