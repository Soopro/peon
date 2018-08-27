# coding=utf-8
from __future__ import absolute_import

import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from ..core import RenderHandler
from ..utlis import BeautifyPrint as bpcolor
from ..helpers import load_config


# variables
SLEEP_TIME = 1
DEFAULT_SRC_DIR = 'src'
DEFAULT_DEST_DIR = 'build'


# handlers
class WatchPatternsHandler(PatternMatchingEventHandler):

    def __init__(self, render_handler,
                 include_mark=None,
                 patterns=None,
                 ignore_patterns=None,
                 ignore_directories=False,
                 case_sensitive=False):

        super(PatternMatchingEventHandler, self).__init__()
        self._patterns = patterns
        self._ignore_patterns = ignore_patterns
        self._ignore_directories = ignore_directories
        self._case_sensitive = case_sensitive

        if isinstance(render_handler, RenderHandler):
            self.render = render_handler
        else:
            raise Exception('Render is invalid.')

        self.incl_mark = include_mark

    def on_created(self, event):
        self.render.render(event.src_path)

    def on_modified(self, event):
        self.render.render(event.src_path)

    def on_moved(self, event):
        self.render.move(event.src_path, event.dest_path)

    def on_deleted(self, event):
        self.render.delete(event.src_path)


# -------------
# main
# -------------
def watch(config_path=None):
    peon_config = load_config('watch', config_path)

    print '------------'
    print 'Peon Wacther started'
    print '------------'

    src_dir = peon_config.get('cwd', DEFAULT_SRC_DIR)
    dest_dir = peon_config.get('dest', DEFAULT_DEST_DIR)
    render_aliases = peon_config.get('render_aliases', {})
    skip_includes = peon_config.get('skip_includes', [])
    clean_dest = peon_config.get('clean', True)
    server = peon_config.get('server')
    host = str(peon_config.get('host', ''))
    port = str(peon_config.get('port', ''))

    if dest_dir == DEFAULT_SRC_DIR:
        dest_dir = DEFAULT_DEST_DIR

    render = RenderHandler(src_dir, dest_dir,
                           aliases=render_aliases,
                           skips=skip_includes)
    if clean_dest:
        render.clean()
        render.render_all()

    if isinstance(server, basestring) and server:
        # live reload will be stop when run pyco with parent path,
        # ex. `python /pyco/pyco.py`.
        # that's why switch to shell=True.
        if server == 'pyco':
            args = ['python', 'pyco.py']
            if port or host:
                msg = '*** You must setup `port` and `host` in pyco config.'
                print '{}{}{}:'.format(bpcolor.FAIL, msg, bpcolor.ENDC)
            subprocess.Popen(args, cwd='pyco')
        elif server == 'mittens':
            # args = 'peon -s --port {} --host {}'.format(port, host)
            args = ['peon', '-s', '--port', port, '--host', host]
            subprocess.Popen(args, cwd='mittens')
    elif server:
        args = ['peon', '-s', '--port', port, '--host', host]
        subprocess.Popen(args, cwd=dest_dir)

    observer = Observer()
    watcher = WatchPatternsHandler(render_handler=render,
                                   ignore_patterns=['*/.*'])

    observer.schedule(watcher, src_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        observer.stop()
        print '------------'
        print 'Peon Wacther stoped'
        print '------------'

    observer.join()
