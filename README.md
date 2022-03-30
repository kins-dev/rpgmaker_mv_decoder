# rpgmaker_mv_decoder v0.2.0

[![Documentation Status](https://readthedocs.org/projects/rpgmaker-mv-decoder/badge/?version=latest)](https://rpgmaker-mv-decoder.readthedocs.io/en/latest/?version=latest)

This is a python script for decoding RPG Maker MV/MZ game assets.

This has a handy feature, it will figure out (if possible) the key automatically.
It will also use the file header info for creating the extension.
If you know the key, you can pass it in.

If you want you can use the [API](https://rpgmaker-mv-decoder.readthedocs.io) instead

## Features

- GUI for those who need that
- Fast
- No key needed if there's any encoded png images
- Can put proper file extensions on the decoded files

## Example usage

```bash
./decoder.py "<source path>" "<destination path>" ["<optional key>"]
```

```bash
./gui.py
```

## Help

You can use the standard `--help` option for full documentation:

```plain
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
  --detect_type  Detect the file type and use the associated file extension.
                 By default .rpgmvp becomes .png and .rpgmvo becomes .ogg
                 regardless of the file contents.
  --help         Show this message and exit.
```
