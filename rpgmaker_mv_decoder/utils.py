"""Main module."""
import os
from pathlib import Path, PurePath
from rpgmaker_mv_decoder.exceptions import FileFormatError
import sys
import click
import struct
import uuid
import magic

RPG_MAKER_MV_MAGIC = "5250474d560000000003010000000000"
PNG_HEADER = "89504e470d0a1a0a0000000d49484452"
OCT_STREAM = "application/octet-stream"

def int_xor(var, key):
    key = key[:len(var)]
    int_var = int.from_bytes(var, sys.byteorder)
    int_key = int.from_bytes(key, sys.byteorder)
    int_enc = int_var ^ int_key
    return int_enc.to_bytes(len(var), sys.byteorder)

def read_header_and_id(file_content, binary_key):
    (id, header) = struct.unpack("!16s16s", file_content[:32])
    if id.hex() != RPG_MAKER_MV_MAGIC:
        raise FileFormatError('"%s" != "%s"' % (id.hex(), RPG_MAKER_MV_MAGIC), "First 16 bytes look wrong on this file")
    return int_xor(binary_key,header)

def get_likely_key(keys, count):
    # There's probably a better way...
    sorted_keys = dict(sorted(keys.items(), key=lambda item: item[1], reverse=True))
    main_key = list(sorted_keys.keys())[0]
    if len(sorted_keys) != 1:
        ratio = sorted_keys[main_key]/(count - (len(keys) - 1))
        click.echo("%.2f%% confident for images" % (((ratio)*100)))
        cnt = 0
        for item in sorted_keys:
            if cnt == 0:
                click.echo("Possible keys: %s used in %d of %d images" % (item, sorted_keys[item], count))
            else:
                click.echo("               %s used in %d of %d images" % (item, sorted_keys[item], count))
            cnt += 1
            if cnt == 10:
                break
    return main_key

def guess_at_key(src):
    # standard png header
    bKey = bytes.fromhex(PNG_HEADER)
    files = sorted(Path(src).glob('**/*.rpgmvp'))
    keys = {}
    count = 0

    with click.progressbar(files, label="Finding key") as bar:
        for filename in bar:
            with click.open_file(filename, 'rb') as file:
                try:
                    item = read_header_and_id(file.read(32), bKey).hex()
                except FileFormatError as ffe:
                    click.echo(ffe.expression)
                    continue
                count += 1
                try:
                    keys[item] += 1
                except KeyError:
                    keys[item] = 1
    return get_likely_key(keys, count)



def update_src_dest(src, dst):
    if Path(src).joinpath("img").exists():
        click.echo("Found 'img' in source path, using parent directory name")
        src = src.parent.parent
    elif Path(src).joinpath("www").exists():
        click.echo("Found 'www' in source path, using parent directory name")
        src = src.parent
    else:
        tmp_dir = uuid.uuid4()
        dst = dst.joinpath(str(tmp_dir))
    return (src, dst)

def get_file_ext(data):
    filetype = magic.from_buffer(data, mime=True)
    if filetype == OCT_STREAM:
        raise FileFormatError('"%s" == "%s"' % (filetype, OCT_STREAM), "Found octlet stream, key is probably incorrect.")
    return '.'+filetype.split('/')[-1]


def decode_files(src, dst, key):
    bKey = bytes.fromhex(key)

    (source,dest) = update_src_dest(PurePath(src), PurePath(dst))

    click.echo('Reading from: %s' % click.format_filename(str(source)))
    click.echo('Writing to: %s' % click.format_filename(str(dest)))

    files=sorted(Path(src).glob('**/*.rpgmv[op]'))

    with click.progressbar(files, label="Decoding files") as bar:
        for filename in bar:
            outputFile = dest.joinpath(PurePath(filename).relative_to(source))

            with click.open_file(filename, 'rb') as file:
                fileContent = file.read()
                try:
                    result = read_header_and_id(fileContent, bKey) + fileContent[32:]
                except FileFormatError as ffe:
                    click.echo(ffe.expression)
                    continue

            try:
                outputFile = outputFile.with_suffix(get_file_ext(result))
            except FileFormatError:
                click.echo("Found octlet stream, key is probably incorrect, skipping %s" % click.format_filename(str(filename)))
                continue

            try:
                os.makedirs(outputFile.parent)
            except FileExistsError:
                pass
            with open(outputFile, mode='wb') as file:
                file.write(result)
