# rpgmaker_mv_decoder v0.1.1

This is a python script for decoding RPG Maker MV/MZ game assets.

This has a handy feature, it will figure out (if possible) the key automatically.
It will also use the file header info for creating the extension.
If you know the key, you can pass it in.

## Features

- Fast
- No key needed if there's any encoded png images
- Can put proper file extensions on the decoded files

## Example usage

```bash
./decoder.py source_path destination_path optional_key
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
