# rpgmaker_mv_decoder

Python script for decoding RPG Maker MV/MZ game assets

This has a handy feature, it will figure out (if possible) the key automatically.  It will also use the file header info for creating the extension.  If you know the key, you can pass it in.

Runs significantly faster than other solutions.

```bash
python3 -m rpgmaker_mv_decoder source_path destination_path optional_key
```

Still need to version this and do some work on it, but it is good enough for the moment
