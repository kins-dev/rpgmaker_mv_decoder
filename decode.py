#!/usr/bin/env python3

from rpgmaker_mv_decoder.utils import decode_files, guess_at_key
import sys
import click


@click.command()
@click.argument('source', type=click.Path(exists=True, file_okay=False, resolve_path=True), required=True, prompt=True)
@click.argument('destination', type=click.Path(exists=True, writable=True, file_okay=False, resolve_path=True), required=True, prompt=True)
@click.argument('key', type=str, required=False)
@click.option('--file_types', is_flag=True)
def main(source, destination, key, file_types):
    src = source
    dst = destination
    if key == None:
        key = guess_at_key(src)
    decode_files(src, dst, key, file_types)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
