#coding=utf-8
from __future__ import absolute_import

import os, subprocess, time
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler

from ..services import RenderHandler
from .helpers import load_config

# variables
SLEEP_TIME = 1
DEFAULT_SRC_DIR = 'src'
DEFAULT_DEST_DIR = 'build'

# handlers
class WatchPatternsHandler(PatternMatchingEventHandler):
    
    def __init__(self, render_handler,
                       include_mark = None,
                       patterns = None,
                       ignore_patterns = None,
                       ignore_directories = False,
                       case_sensitive = False):

        super(PatternMatchingEventHandler, self).__init__()
        self._patterns = patterns
        self._ignore_patterns = ignore_patterns
        self._ignore_directories = ignore_directories
        self._case_sensitive = case_sensitive
        
        if isinstance(render_handler, RenderHandler):
            self.render = render_handler
        else:
            raise Exception("Render is invalid.")
        
        self.incl_mark = include_mark
    
    def _find_end_path(self, path):
        if not path:
            return None
        tmp_path_list = path.rsplit(os.path.sep,1)
        if len(tmp_path_list) > 0:
            return tmp_path_list[1]
        else:
            return None

    def on_created(self, event):
        self.render.render(event.src_path)
    
    def on_modified(self, event):
        self.render.render(event.src_path)
    
    def on_moved(self, event):
        end_src_path = self._find_end_path(event.src_path)
        end_dest_path = self._find_end_path(event.dest_path)
        if end_src_path != end_dest_path:
            self.render.move(event.src_path, event.dest_path)
    
    def on_deleted(self, event):
        self.render.delete(event.src_path)
    


#-------------
# main
#-------------
DEFAULT_ACTION = 'watch'


def watch(opts):
    peon_config = load_config(DEFAULT_ACTION)
    
    print "------------"
    print "Peon Wacther started"
    print "------------"
    
    src_dir = opts.src_dir or peon_config.get('src_dir', DEFAULT_SRC_DIR)
    dest_dir = opts.dest_dir or peon_config.get('dest_dir', DEFAULT_DEST_DIR)
    init_dest = opts.watcher == 'init' or peon_config.get('init')
    server_port = opts.port or peon_config.get('port')
    
    render_opts = {
        "src": src_dir,
        "dest": dest_dir,
    }
    render = RenderHandler(render_opts)
    
    if init_dest:
        render.clean()
        render.render_all()
    
    if server_port:
        try:
            port = str(server_port)
        except:
            port = ''
        args = ['peon', '-s', port, '--http', '--dir', dest_dir]
        server_progress = subprocess.Popen(args)
    
    observer = Observer()
    watcher = WatchPatternsHandler(render_handler = render,
                                   ignore_patterns = ['*/.*'])

    observer.schedule(watcher, src_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        observer.stop()
        print "------------"
        print "Peon Wacther stoped"
        print "------------"
        
    observer.join()
    


if __name__ == '__main__':
    import argparse
    # command line options
    parser = argparse.ArgumentParser(
                        description='Options of run Peon watcher.')
    
    parser.add_argument('--dest',
                        dest='dest_dir',
                        action='store',
                        nargs='?',
                        const='build',
                        help='Define operation dest dir.')
    
    parser.add_argument('--src', 
                        dest='src_dir',
                        action='store',
                        nargs='?',
                        const='src',
                        help='Define operation src dir.')
    
    parser.add_argument('-w', '--watcher', 
                        dest='watcher',
                        action='store',
                        nargs='?',
                        const=True,
                        help='Run Peon watcher file changes.')

    opts, unknown = parser.parse_known_args()

    watch(opts)
