#coding=utf-8
from __future__ import absolute_import
import argparse

from .peon_construct import construct
from .peon_server import server
from .peon_watcher import watch
from .peon_packing import packing
from .peon_transport import transport
from .peon_backup import backup

__version_info__ = ('0', '0', '6')
__version__ = '.'.join(__version_info__)

def command_options():
    # Dev server
    parser = argparse.ArgumentParser(
                    description='Options of run Peon dev server.')
                    
    parser.add_argument('-v', '--version', 
                        dest='version',
                        action='store_const',
                        const=True,
                        help='Show Peon current version.')

    
    parser.add_argument('-s', '--server', 
                        dest='port',
                        action='store',
                        nargs='?',
                        type=int,
                        const=9527,
                        help='Start Peon dev server at port.')
    
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
                        action='store',
                        nargs='?',
                        const=True,
                        help='Run Peon watcher for coffee less and jade.')
    
    parser.add_argument('--hard', 
                        dest='hard',
                        action='store_const',
                        const=True,
                        help='Set Peon watcher delete file if source deleted.')
    
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