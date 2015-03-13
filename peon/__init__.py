#coding=utf-8
import argparse
from peon_construct import construct
from peon_server import server
from peon_watcher import watch

__version_info__ = ('0', '0', '3')
__version__ = '.'.join(__version_info__)

def command_options():
    # Dev server
    parser = argparse.ArgumentParser(
                    description='Options of run Peon dev server.')
    
    parser.add_argument('-s', '--server', 
                        dest='server',
                        action='store_const',
                        const=True,
                        help='Start Peon dev server.')
    
    parser.add_argument('-p', '--port', 
                        dest='server_port',
                        action='store',
                        type=int,
                        help='Setup Peon dev server port.')

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
                        help='Run Peon watcher for coffee less and jade.')
    
    # Construct
    parser.add_argument('-c', '--construct', 
                        dest='construct',
                        action='store_const',
                        const=True,
                        help='Run Peon construct to build files.')

    parser.add_argument('--init', 
                        dest='init',
                        action='store_const',
                        const=True,
                        help='Run Peon init tasks.')

    parser.add_argument('--build', 
                        dest='build',
                        action='store_const',
                        const=True,
                        help='Run Peon build tasks.')

    opts, unknown = parser.parse_known_args()

    return opts


def run():
    opts = command_options()
    if opts.watcher:
        peon_watcher.watch()
    elif opts.construct:
        peon_construct.construct(opts)
    else:
        peon_server.server(opts)


if __name__ == '__main__':
    run()