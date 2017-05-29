# coding=utf-8
from __future__ import absolute_import
import argparse

from .modules import (construct, packing, watch, server)

__version_info__ = ('1', '0', '0')
__version__ = '.'.join(__version_info__)


def command_options():

    parser = argparse.ArgumentParser(
        description='Options of run Peon dev server.')

    parser.add_argument('-v', '--version',
                        dest='version',
                        action='store_const',
                        const=True,
                        help='Show current version.')

    # Server
    parser.add_argument('-s', '--server',
                        dest='port',
                        action='store',
                        nargs='?',
                        type=int,
                        const=9527,
                        help='Start dev server at port.')

    # Watcher
    parser.add_argument('-w', '--watcher',
                        dest='watcher',
                        action='store_const',
                        const=True,
                        help='Run watcher file changes.')

    # Construct
    parser.add_argument('-c', '--construct',
                        dest='construct',
                        action='store',
                        nargs='?',
                        type=str,
                        const='release',
                        help='Run construct to build files.')

    # Packing
    parser.add_argument('-z', '--zip',
                        dest='zip',
                        action='store',
                        nargs='?',
                        const=True,
                        help='Run packing zip file.')

    opts, unknown = parser.parse_known_args()

    return opts


def run():
    opts = command_options()
    if opts.version:
        print 'Project: Puss in boots'
        print 'Version:', __version__
    elif opts.watcher:
        watch(opts)
    elif opts.construct:
        construct(opts)
    elif opts.zip:
        packing(opts)
    else:
        server(opts)
