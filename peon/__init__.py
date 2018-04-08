# coding=utf-8
from __future__ import absolute_import
import argparse

from .modules import (construct, packing, watch, server)

__version_info__ = ('1', '4', '5')
__version__ = '.'.join(__version_info__)


def command_options():

    parser = argparse.ArgumentParser(
        description='Options of run Peon dev server.')

    parser.add_argument('-v', '--version',
                        dest='version',
                        action='store_const',
                        const=True,
                        help='Show current version.')

    parser.add_argument('--config',
                        dest='config_path',
                        action='store',
                        nargs='?',
                        type=str,
                        default=None,
                        const=None,
                        help='Define the config file path.')

    # Server
    parser.add_argument('-s', '--server',
                        dest='port',
                        action='store',
                        nargs='?',
                        type=int,
                        const=9527,
                        help='Start dev server at port.')

    parser.add_argument('--dir',
                        dest='dir',
                        action='store',
                        nargs='?',
                        type=str,
                        const=None,
                        help='Define dev server operation dir.')

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
        print 'Peon:', __version__
    elif opts.watcher:
        watch(opts.config_path)
    elif opts.construct:
        construct(opts, opts.config_path)
    elif opts.zip:
        packing(opts.config_path)
    else:
        server(opts)
