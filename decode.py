#!/usr/bin/env python3

from rpgmaker_mv_decoder.utils import decode_files, guess_at_key
import sys
import click


@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, writable=True, file_okay=False, resolve_path=True), required=True)
@click.argument('key', type=str, required=False)
def main(src, dst, key):
    if key == None:
        key = guess_at_key(src)
    decode_files(src, dst, key)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
