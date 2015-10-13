#coding=utf-8
from __future__ import absolute_import
import argparse

from .modules import (construct, backup, transport, packing, watch, server)

__version_info__ = ('0', '3', '2')
__version__ = '.'.join(__version_info__)

def command_options():
    
    parser = argparse.ArgumentParser(
                        description='Options of run Peon dev server.')
                    
    parser.add_argument('-v', '--version', 
                        dest='version',
                        action='store_const',
                        const=True,
                        help='Show Peon current version.')

    parser.add_argument('--dest', 
                        dest='dest_dir',
                        action='store',
                        nargs='?',
                        const=True,
                        help='Define operation dest dir.')
    
    parser.add_argument('--src', 
                        dest='src_dir',
                        action='store',
                        nargs='?',
                        const=True,
                        help='Define operation src dir.')
    
    parser.add_argument('--dir', 
                        dest='dir',
                        action='store',
                        nargs='?',
                        type=str,
                        const=None,
                        help='Define operation dir.')
    
    parser.add_argument('--skip',
                        dest='skip_includes',
                        action='append',
                        type=str,
                        help='Skip type of include files with rendering.')
    
    # Server
    parser.add_argument('-s', '--server', 
                        dest='port',
                        action='store',
                        nargs='?',
                        type=int,
                        const=9527,
                        help='Start Peon dev server at port.')
    
    parser.add_argument('--pyco', 
                        dest='pyco',
                        action='store',
                        nargs='?',
                        type=str,
                        const='pyco',
                        help='Start Pyco dev server by path.')
    
    parser.add_argument('--http', 
                        dest='http_server',
                        action='store_const',
                        const=True,
                        help='Start Peon with simplehttp server.')
    
    parser.add_argument('--harp', 
                        dest='harp_server',
                        action='store_const',
                        const=True,
                        help='Start Peon with harp server.')
    
    # Watcher
    parser.add_argument('-w', '--watcher', 
                        dest='watcher',
                        action='store_const',
                        const=True,
                        help='Run Peon watcher file changes.')
    
    parser.add_argument('--clean',
                        dest='clean',
                        action='store_const',
                        const=True,
                        help='Clean dest folder before take actions.')
    
    
    # Construct
    parser.add_argument('-c', '--construct', 
                        dest='construct',
                        action='store',
                        nargs='?',
                        type=str,
                        const='release',
                        help='Run Peon construct to build files.')

    
    # Packing
    parser.add_argument('-z', '--zip', 
                        dest='zip',
                        action='store',
                        nargs='?',
                        const=True,
                        help='Run Peon packing zip file.')
    
    parser.add_argument('--exclude', 
                        dest='exclude',
                        nargs='?',
                        action='store',
                        type=str,
                        help='Exclude filename pattern from packing.')

    # Transport
    parser.add_argument('-t', '--transport', 
                        dest='transport',
                        action='store',
                        nargs='?',
                        type=str,
                        const=1,
                        help='Start Peon transport mode. upload or download')
    
    # Backup
    parser.add_argument('-b', '--backup', 
                        dest='backup',
                        action='store_const',
                        const=True,
                        help='Run Peon backup files and datas.')
    
    opts, unknown = parser.parse_known_args()

    return opts


def run():
    opts = command_options()
    if opts.version:
        print "Peon - Version:", __version__
    elif opts.watcher:
        watch(opts)
    elif opts.construct:
        construct(opts)
    elif opts.zip:
        packing(opts)
    elif opts.transport:
        transport(opts)
    elif opts.backup:
        backup(opts)
    else:
        server(opts)


if __name__ == '__main__':
    run()