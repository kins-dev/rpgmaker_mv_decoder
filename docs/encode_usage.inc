.. code-block:: none
    :emphasize-lines: 1

    Usage: encode.py [OPTIONS] <Source> <Destination> <Key>

      Encodes image and audio files under <Source> directory.

    Arguments:
      <Source>       The source directory. For best results this should be the
                     parent of the 'www' or 'img' directory.
      <Destination>  The parent destination directory. This script will create a
                     project directory under this path if it doesn't already
                     exist.
      <Key>          The encoding key to use.

    Options:
      --version    Prints the version number
      --overwrite  Overwrite files without prompting
      --help       Show this message and exit.
