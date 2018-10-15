# coding=utf-8
from __future__ import absolute_import
import argparse

from .modules import (construct, packing, watch, server)

__version_info__ = ('1', '5', '1')
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
                        dest='server',
                        action='store_const',
                        const=True,
                        help='Start dev server.')

    parser.add_argument('--host',
                        dest='host',
                        action='store',
                        nargs='?',
                        type=str,
                        default='',
                        const=None,
                        help='Start dev server at host.')

    parser.add_argument('--port',
                        dest='port',
                        action='store',
                        nargs='?',
                        type=str,
                        default='9527',
                        const='9527',
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
    opts._print_help = parser.print_help

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
    elif opts.server:
        server(opts.host, opts.port)
    else:
        opts._print_help()
