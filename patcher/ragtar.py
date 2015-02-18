#!/usr/bin/python
# -*- coding: UTF-8, tab-width: 4 -*-
# Python Coding Style: http://docs.python.org/tutorial/controlflow.html#intermezzo-coding-style
# Command Line Arguments Parser: http://docs.python.org/library/argparse.html


from __future__ import division

from sys import stdin, stdout, stderr, argv
from codecs import open as cfopen
from gzip import open as gzopen
maybe_gz_open = {True:gzopen, False:open}
from os import SEEK_CUR, mkdir
from os.path import normpath, exists as fexists, isdir


def noop(*ignore, **kwignore):
    pass


def main(invocation, *cli_args):
    arg_opts, args_iter = filter_arg_opts(cli_args)
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
    if 'v' in arg_modes:
        arg_opts()['verbose'] = True

    if arg_action in ('list', 'extract'):
        pass
    else:
        raise dunnohow('action ' + arg_action)

    src_fn = '<stdin>'
    src_stream = stdin
    log_stream = stdout
    def logp(fmt, *args, **kwargs):
        print >>log_stream, fmt.format(*args, **kwargs)
    if arg_opts('verbose'):
        logv = logp
    else:
        logv = noop

    if 'f' in arg_modes:
        src_fn = args_iter.next()
        src_stream = maybe_gz_open['z' in arg_modes](src_fn, 'rb')
    elif 'z' in arg_modes:
        raise dunnohow('stdin zlib')

    item_addr = '?'
    stats = { 'dirs': 0, 'files': 0, 'bytes': 0 }
    while True:
        item_addr = '@{:07x}'.format(src_stream.tell())
        item_type = src_stream.read(1)
        item_size = ord(src_stream.read(1))
        item_name = src_stream.read(item_size).split('\x00')
        if len(item_name) < 1:
            logp('W: {}: filename not zero-terminated', item_addr)
        if (len(item_name) != 2) or (item_name[-1] != ''):
            logp('W: {}: unexpected zero-byte in filename', item_addr)
        item_name = defuse_filename(item_name[0])
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
        if arg_action == 'extract':
            if item_type == 'd':
                if isdir(item_name):
                    logv('dir exists:\t{}', item_name)
                else:
                    logv('create dir:\t{}', item_name)
                    mkdir(item_name)
            elif item_type == 'f':
                item_replace = check_replace_dest(item_name, arg_opts)
                logv('{1} file:\t{0}', item_name, { None: 'create',
                        True: 'replace', False: 'skip' }[item_replace])
                if item_replace in (True, None):
                    copy_stream_blocks(src_stream, item_name, bytes=item_size,
                                       opts=arg_opts)
                else:
                    src_stream.seek(item_size, SEEK_CUR)
            else:
                raise dunnohow('extract item type ' + item_type)
        if arg_action in ('list',):
            if arg_opts('verbose'):
                logp('{} {:>6}\t{}', item_addr, item_size, item_name)
            else:
                logp('{}{}', item_name, {'d':'/', 'f':''}.get(item_type, '?'))
        if arg_action in ('list',):
            if item_type == 'f':
                src_stream.seek(item_size, SEEK_CUR)

    if arg_action in ('list',):
        logv('{} {:>6}\t{dirs} directories, {files} files, {bytes} bytes',
             item_addr, '=', **stats)
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


def filter_arg_opts(args_iter):
    opts = {}
    files = []
    for arg in args_iter:
        if arg.startswith('--'):
            if arg == '--':
                files += list(args_iter)
                break
            arg = arg[2:].split('=', 1)
            if len(arg) < 2:
                arg.append(True)
            opts[arg[0]] = arg[1]
        else:
            files.append(arg)
    def getopts(key=None, dflt=None):
        if key is None:
            return opts
        return opts.get(key, dflt)
    return getopts, iter(files)


def defuse_filename(orig_fn):
    orig_fn = str(orig_fn)
    if orig_fn == '':
        return '__E_NO_FILENAME__'

    def esc_char(ch):
        if ch == '\\':
            return '/'
        if ch == '\x00':
            return ''
        if ch.isalnum() or (ch in ' ._-@,'):
            return ch
        return '%{:02X}'.format(ord(ch))

    safe_fn = ''.join([esc_char(ch) for ch in orig_fn])
    safe_fn = normpath(safe_fn)
    for suspi in ('./', '/..',):
        if suspi in safe_fn:
            raise ValueError('suspicious substring found in filename',
                             suspi, safe_fn)

    return safe_fn


def copy_stream_blocks(src, dest, bytes, opts=None):
    if opts is None:
        opts = lambda opt, dflt: dflt
    elif isinstance(opts, dict):
        opts = opts.get
    bytes_remain = bytes
    cleanup = None

    if isinstance(dest, basestring):
        output = open(dest, 'wb')
        cleanup = output.close
        output = output.write
    else:
        output = dest.write

    blocksize = long(opts('blocksize', 4096))

    while bytes_remain > 0:
        buf = src.read(min(bytes_remain, blocksize))
        bytes_remain -= len(buf)
        output(buf)
    if cleanup is not None:
        cleanup()


def check_replace_dest(fn, opts):
    if not fexists(fn):
        return None
    strat = opts('exist')
    if strat == 'skip':
        return False
    if strat == 'replace':
        return True
    raise IOError('destination file already exists', fn)


























if __name__ == '__main__':
    main(*argv)
