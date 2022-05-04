# RPGMaker MV Decoder v1.3.0

[![v1.3.0 CodeQL Status](https://img.shields.io/github/workflow/status/kins-dev/rpgmaker_mv_decoder/CodeQL/v1.3.0?label=v1.3.0%20CodeQL&logo=GitHub)](https://github.com/kins-dev/rpgmaker_mv_decoder/actions/workflows/codeql-analysis.yml) [![v1.3.0 Python Application Status](https://img.shields.io/github/workflow/status/kins-dev/rpgmaker_mv_decoder/Python%20application/v1.3.0?label=v1.3.0%20Python%20application&logo=GitHub)](https://github.com/kins-dev/rpgmaker_mv_decoder/actions/workflows/python-app.yml) [![v1.3.0 Pylint Status](https://img.shields.io/github/workflow/status/kins-dev/rpgmaker_mv_decoder/Upload%20Python%20Package/v1.3.0?label=v1.3.0%20Upload%20Python%20Package&logo=GitHub)](https://github.com/kins-dev/rpgmaker_mv_decoder/actions/workflows/python-publish.yml) [![Documentation status](https://img.shields.io/readthedocs/rpgmaker_mv_decoder/v1.3.0?label=v1.3.0%20Documentation&logo=readthedocs)](https://rpgmaker-mv-decoder.readthedocs.io/en/v1.3.0/)
[![Latest pypi release](https://img.shields.io/pypi/v/rpgmaker_mv_decoder?label=Latest%20pypi%20release&logo=pypi&color=blue)](https://pypi.python.org/pypi/rpgmaker_mv_decoder)

This is a set of python scripts for decoding and encoding RPGMaker MV/MZ game assets.

Decoding has a handy feature, it will figure out (if possible) the key automatically.
It will also can use the file data for creating the extension.
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
./encoder.py "<source path>" "<destination path>" "<key>"
```

```bash
./gui.py
```

The GUI has a fairly simple main window:

![Main Window](https://raw.githubusercontent.com/kins-dev/rpgmaker_mv_decoder/main/docs/_static/screenshots/main.png)

Progress will be shown while finding the key, decoding the files or encoding the files:

![Progress Dialog](https://raw.githubusercontent.com/kins-dev/rpgmaker_mv_decoder/main/docs/_static/screenshots/progress.png)

Hitting the question mark will bring up the about box, which gives some handy links:

![About Dialog](https://raw.githubusercontent.com/kins-dev/rpgmaker_mv_decoder/main/docs/_static/screenshots/about.png)

## Help

You can use the standard `--help` option for full documentation:

### Decoding

```text
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

### Encoding

```text
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
  --help  Show this message and exit.
```
