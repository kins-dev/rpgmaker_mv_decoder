#!/usr/bin/env python3

import struct
import sys
import click
from pathlib import Path, PurePath
import os
import uuid
import magic
import time

def int_xor(var, key):
    key = key[:len(var)]
    int_var = int.from_bytes(var, sys.byteorder)
    int_key = int.from_bytes(key, sys.byteorder)
    int_enc = int_var ^ int_key
    return int_enc.to_bytes(len(var), sys.byteorder)

def guess_at_key(src):
    # standard png header
    bKey = bytes.fromhex("89504e470d0a1a0a0000000d49484452")
    files = sorted(Path(src).glob('**/*.rpgmvp'))
    keys = {}
    count = 0
    with click.progressbar(files, label="Finding key") as bar:
        for filename in bar:
            with click.open_file(filename, 'rb') as file:
                fileContent = file.read(32)
                (id, header) = struct.unpack("!16s16s", fileContent)
                if id.hex() != "5250474d560000000003010000000000":
                    click.echo("ID Looks wrong, skipping")
                    continue
                count += 1
                item = int_xor(bKey,header).hex()
                try:
                    keys[item] += 1
                except KeyError:
                    keys[item] = 1
    max = 0
    key = ""
    second_max = 0
    second_key = ""
    for item in keys:
        if keys[item] > max:
            second_max = max
            second_key = key
            max = keys[item]
            key = item
        elif keys[item] > second_max:
            second_max = keys[item]
            second_key = item
    ratio = max/(count - (len(keys) - 1))

    if second_max != 0:
        click.echo("%.2f%% confident for images" % (((ratio)*100)))
        click.echo("Possible keys: %s used in %d of %d images" % (key, max, count))
        click.echo("               %s used in %d of %d images" % (second_key, second_max, count))
    return key

@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, writable=True, file_okay=False, resolve_path=True), required=True)
@click.argument('key', type=str, required=False)
def cli(src, dst, key):
    if key == None:
        key = guess_at_key(src)
    bKey = bytes.fromhex(key)
    source = PurePath(src)
    destin = PurePath(dst)
    if Path(src).joinpath("img").exists():
        click.echo("Found 'img' in source path, using parent directory name")
        source = source.parent.parent
    elif Path(src).joinpath("www").exists():
        click.echo("Found 'www' in source path, using parent directory name")
        source = source.parent
    else:
        tmp_dir = uuid.uuid4()
        destin = destin.joinpath(str(tmp_dir))
        click.echo('Unknown structure, dumping to: %s' % click.format_filename(str(destin)))
    files=sorted(Path(src).glob('**/*.rpgmv[op]'))

    with click.progressbar(files, label="Decoding files") as bar:
        for filename in bar:
            outputFile = destin.joinpath(PurePath(filename).relative_to(source))
            result=bytes()
            with click.open_file(filename, 'rb') as file:
                fileContent = file.read()
                (id, header) = struct.unpack("!16s16s", fileContent[:32])
                if id.hex() != "5250474d560000000003010000000000":
                    click.echo("ID Looks wrong, skipping")
                    continue

                result=int_xor(bKey,header) + fileContent[32:]

            filetype = magic.from_buffer(result, mime=True)
            if filetype == "application/octet-stream":
                #click.echo("Found octlet stream, key is probably incorrect, skipping %s" % click.format_filename(str(filename)))
                continue
            outputFile = outputFile.with_suffix('.'+filetype.split('/')[-1])
            #click.echo("%s => %s" % (click.format_filename(str(filename)),click.format_filename(str(outputFile))))
            try:
                os.makedirs(outputFile.parent)
            except FileExistsError:
                pass
            with open(outputFile, mode='wb') as file: # b is important -> binary
                file.write(result)

if __name__ == '__main__':
    cli()