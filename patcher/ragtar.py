#!/usr/bin/python
# -*- coding: UTF-8, tab-width: 4 -*-
# Python Coding Style: http://docs.python.org/tutorial/controlflow.html#intermezzo-coding-style
# Command Line Arguments Parser: http://docs.python.org/library/argparse.html


from __future__ import division

from sys import stdin, stdout, stderr, argv
from codecs import open as cfopen
from gzip import open as gzopen
maybe_gz_open = {True:gzopen, False:open}
from os import SEEK_CUR
from os.path import realpath, dirname, join as joinpath, exists as fexists


def main(invocation, *cli_args):
    args_iter = iter(cli_args)
    arg_modes = args_iter.next()
    arg_action_names = {
        'A': 'concatenate',
        'c': 'create',
        'd': 'diff',
        'r': 'append',
        't': 'list',
        'u': 'update',
        'x': 'extract',
        }
    arg_action = (lambda: [an for an in map(arg_action_names.get, arg_modes)
                              if an is not None])()
    if len(arg_action) == 1:
        arg_action = arg_action[0]
    elif len(arg_action) < 1:
        raise RuntimeError('no action given', arg_action_names)
    else:
        raise dunnohow('multiple actions', arg_action)

    if arg_action in ('list'):
        pass
    else:
        raise dunnohow('action ' + arg_action)


    src_fn = '<stdin>'
    src_stream = stdin
    log_stream = stdout
    if 'f' in arg_modes:
        src_fn = args_iter.next()
        src_stream = maybe_gz_open['z' in arg_modes](src_fn, 'rb')
    elif 'z' in arg_modes:
        raise dunnohow('stdin zlib')

    stats = { 'dirs': 0, 'files': 0, 'bytes': 0 }
    while True:
        item_type = src_stream.read(1)
        item_size = ord(src_stream.read(1))
        item_name = defuse_filename(src_stream.read(item_size))
        item_size = '?'
        if item_type == 'e':
            break
        elif item_type == 'f':
            stats['files'] += 1
            item_size = parse_little_endian(src_stream.read(4))
            stats['bytes'] += item_size
        elif item_type == 'd':
            stats['dirs'] += 1
            item_size = '/'
        if 'v' in arg_modes:
            print >>log_stream, '{:>7}\t{}'.format(item_size, item_name)
        if arg_action == 'list':
            if 'v' not in arg_modes:
                print >>log_stream, item_name + {True: '/'
                    }.get(item_type == 'd', '')
            if item_type == 'f':
                src_stream.seek(item_size, SEEK_CUR)

    if 'v' in arg_modes:
        print ('{:>7}\t{dirs} directories, {files} files, {bytes} bytes'
              ).format('=', **stats)
    return


def parse_little_endian(bytes):
    value = 0
    factor = 1
    for byte in bytes:
        value += ord(byte) * factor
        factor *= 256
    return value


def dunnohow(msg, *args, **kwargs):
    return NotImplementedError(msg + ': not supported yet', *args, **kwargs)


def defuse_filename(fn):
    fn = str(fn)
    if fn == '':
        return '__E_NO_FILENAME__'
    if len(fn) > 1:
        return ''.join([defuse_filename(ch) for ch in fn])
    if fn == '\\':
        return '/'
    if fn == '\x00':
        return ''
    if fn.isalnum() or (fn in ' ._-@,'):
        return fn
    return '%{:02X}'.format(ord(fn))














if __name__ == '__main__':
    main(*argv)
