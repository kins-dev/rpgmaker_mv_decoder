# rpgmaker_mv_decoder
Python script for decoding RPG Maker MV/MZ game assets

This has a handy feature, it will figure out (if possible) the key automatically.  It will also use the file header info for creating the extension.  If you know the key, you can pass it in.

Runs significantly faster than other solutions.

```bash
./rpgmaker_decoder.py source_path destination_path optional_key
```
