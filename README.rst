
RPGMaker MV Decoder v1.1.0
==========================


.. image:: https://img.shields.io/github/workflow/status/kins-dev/rpgmaker_mv_decoder/CodeQL/v1.1.0?label=v1.1.0%20CodeQL&logo=GitHub
   :target: https://github.com/kins-dev/rpgmaker_mv_decoder/actions/workflows/codeql-analysis.yml
   :alt: v1.1.0 CodeQL Status
 
.. image:: https://img.shields.io/github/workflow/status/kins-dev/rpgmaker_mv_decoder/Python%20application/v1.1.0?label=v1.1.0%20Python%20application&logo=GitHub
   :target: https://github.com/kins-dev/rpgmaker_mv_decoder/actions/workflows/python-app.yml
   :alt: v1.1.0 Python Application Status
 
.. image:: https://img.shields.io/github/workflow/status/kins-dev/rpgmaker_mv_decoder/Upload%20Python%20Package/v1.1.0?label=v1.1.0%20Upload%20Python%20Package&logo=GitHub
   :target: https://github.com/kins-dev/rpgmaker_mv_decoder/actions/workflows/python-publish.yml
   :alt: v1.1.0 Pylint Status
 
.. image:: https://img.shields.io/readthedocs/rpgmaker_mv_decoder/v1.1.0?label=v1.1.0%20Documentation&logo=readthedocs
   :target: https://rpgmaker-mv-decoder.readthedocs.io/en/v1.1.0/
   :alt: Documentation status


.. image:: https://img.shields.io/pypi/v/rpgmaker_mv_decoder?label=Latest%20pypi%20release&logo=pypi&color=blue
   :target: https://pypi.python.org/pypi/rpgmaker_mv_decoder
   :alt: Latest pypi release


This is a set of python scripts for decoding and encoding RPGMaker MV/MZ game assets.

Decoding has a handy feature, it will figure out (if possible) the key automatically.
It will also can use the file data for creating the extension.
If you know the key, you can pass it in.

If you want you can use the `API <https://rpgmaker-mv-decoder.readthedocs.io>`_ instead

Features
--------


* GUI for those who need that
* Fast
* No key needed if there's any encoded png images
* Can put proper file extensions on the decoded files

Example usage
-------------

.. code-block:: bash

   ./decoder.py "<source path>" "<destination path>" ["<optional key>"]

.. code-block:: bash

   ./encoder.py "<source path>" "<destination path>" "<key>"

.. code-block:: bash

   ./gui.py

Help
----

You can use the standard ``--help`` option for full documentation:

Decoding
^^^^^^^^

.. code-block:: plain

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

Encoding
^^^^^^^^

.. code-block:: plain

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
