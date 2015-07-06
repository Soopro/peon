#coding=utf-8
from __future__ import absolute_import

import os, time, shutil
import subprocess
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler

from .utlis import BeautifyPrint as bpcolor

# variables
COMPILE_TYPES = {
    "coffee":"js",
    "jade":"html",
    "less":"css",
    "sass":"css",
    "scss":"css",
}
SLEEP_TIME = 1

# exception
class SubprocessError(Exception):
    status_msg = 'SubprocessError'
    affix_msg = None
    
    def __init__(self, message=None):
        self.affix_msg = message

    def __str__(self):
        return '↑ {}:{}'.format(self.status_msg,
                                bpcolor.OKBLUE+self.affix_msg+bpcolor.ENDC)

# handlers
class RenderHandler(object):
    def __init__(self, opts = {},
                       dest_dir='.',
                       src_dir='.',
                       patterns=None,
                       replacement={},
                       include_marks={}):
        
        if not opts:
            opts = {}

        self.root_dir = os.getcwd()
        self.src_dir = opts.get('src', '.')
        self.dest_dir = opts.get('dest', '.')
        self.replacement = opts.get('replacement', {})

        if not os.path.isdir(self.dest_dir):
            os.mkdir(self.dest_dir)
        
        include_marks = opts.get('include_marks', {})

        self.incl_mark = include_marks.get('base', '_')
        self.incl_global_mark = include_marks.get('global', '_g_')
        self.incl_root_mark = include_marks.get('root', '__')
 

    def _raise_exception(self, e, src_path):
        print "--------------------"
        print "[{}Exception{}]: {}".format(bpcolor.FAIL, bpcolor.ENDC, e)
        print "[src_path]: {}".format(src_path)
        print "--------------------"
    
    def _print_message(self, message):
        print "[{}] {}".format(int(time.time()), message)
    
    def find_dest_path(self, path):
        if path.startswith(self.src_dir):
            path = path.replace(self.src_dir, '', 1).lstrip('/')
        filepath, ext = os.path.splitext(path)
        ext = ext[1:]
        comp_ext = self.replacement.get(ext, ext)
        compile_path = "{}/{}".format(self.dest_dir, filepath)
        if comp_ext:
            compile_path = "{}.{}".format(compile_path, comp_ext)
        return compile_path, comp_ext
    
    def get_file_path(self, path):
        filepath, ext = os.path.splitext(path)
        filepath = filepath.rsplit('/',1)
        return filepath[0], filepath[1], ext[1:]
    
    def find_files(self, path='.', file_type=None, includes=False):
        results = []
        
        def add_files(files, dirpath):
            for f in files:
                filename, ext = os.path.splitext(f)

                if filename.startswith('.'):
                    continue
            
                is_includes = self.is_include_file(filename)
                
                if not includes and is_includes:
                    continue
                if includes and not is_includes:
                    continue
                if ext[1:] == file_type or not file_type:
                    results.append(os.path.join(dirpath, f))

        def add_dirs(dirs, dirpath):
            for d in dirs:
                results.append(os.path.join(dirpath, d))
                
        if not path:
            add_files(os.listdir(self.src_dir), self.src_dir)
        else:
            for dirpath, dirs, files in os.walk(path):
                add_dirs(dirs, dirpath)
                add_files(files, dirpath)

        return results
    
    def is_include_file(self, filename):
        is_incl_file = filename.startswith(self.incl_mark) \
                               or filename.endswith(self.incl_mark)
        return is_incl_file
    
    def clean(self):
        if self.src_dir != self.dest_dir:
            shutil.rmtree(self.dest_dir)
        
    def render_all(self):
        files = self.find_files(self.src_dir)
        for f in files:
            self.render(f, includes=False)
        self._print_message("[ {}/**/* ==> {}/**/* ]".format(self.src_dir,
                                                             self.dest_dir))

    def render(self, src_path, includes=True, replace=True):
        if os.path.isdir(src_path):
            self.dirs(src_path)
            return
        filedir, filename, ext,  = self.get_file_path(src_path)
        dest_path, comp_ext = self.find_dest_path(src_path)
        
        if not replace and os.path.isfile(dest_path):
            return
        
        if includes and self.is_include_file(filename):
            if filename.startswith(self.incl_root_mark):
                path = None
            elif filename.startswith(self.incl_global_mark):
                path = self.src_dir
            else:
                path = filedir
            
            files = self.find_files(path, ext)
            for f in files:
                self.render(f)
            return
        
        try:
            if ext == 'coffee':
                result = subprocess.call(["coffee", "-c", src_path])
                print result
                if result == -2:
                    exit()
                elif result > 0:
                    raise SubprocessError('coffee')

            elif ext == 'less':
                result = subprocess.call(["lessc", src_path, dest_path])
                if result == -2:
                    exit()
                elif result > 0:
                    raise SubprocessError('less')
        
            elif ext in ['sass','scss']:
                result = subprocess.call(["sass", "--sourcemap=none",
                                          src_path, dest_path])
                print result
                if result == -2:
                    exit()
                elif result > 0:
                    raise SubprocessError('sass')

            elif ext == 'jade':
                result = subprocess.call(["jade", '-P', src_path, dest_path])
                print result
                if result == -2:
                    exit()
                elif result > 0:
                    raise SubprocessError('jade')

            elif self.src_dir != self.dest_dir:
                if os.path.isfile(src_path):
                    if not os.path.exists(os.path.dirname(dest_path)):
                        os.makedirs(os.path.dirname(dest_path))
                    shutil.copy2(src_path, dest_path)
            else:
                return False
        except Exception as e:
            self._raise_exception(e, src_path)
            return
    
        self._print_message("RENDERED: {} --> {}".format(src_path, dest_path))
    
    def dirs(self, src_path):
        dest_path, _ = self.find_dest_path(src_path)
        if os.path.isdir(src_path) and not os.path.isdir(dest_path):
            os.makedirs(dest_path)
    
    def move(self, src_path, move_to_path):
        dest_path, comp_ext = self.find_dest_path(src_path)
        dest_moved_path, _ = self.find_dest_path(move_to_path)
        _, moved_filename, _,  = self.get_file_path(dest_moved_path)
        
        if self.is_include_file(moved_filename) and os.path.isfile(dest_path):
            try:
                os.remove(dest_path)
            except Exception as e:
                self._raise_exception(e, src_path)
                return
            self._print_message("DELETED: {}".format(dest_path))
        else:
            try:
                if os.path.exists(dest_path):
                    shutil.move(dest_path, dest_moved_path)
                else:
                    # render the moved file if not exists.
                    self.render(move_to_path)

            except Exception as e:
                self._raise_exception(e, src_path)
                return
            self._print_message("MOVED: {} --> {}".format(dest_path,
                                                          dest_moved_path))
    
    def delete(self, src_path):
        dest_path, comp_ext = self.find_dest_path(src_path)
        try:
            if os.path.isfile(dest_path):
                os.remove(dest_path)
            elif os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            else:
                return
        except Exception as e:
            self._raise_exception(e, src_path)
            return
            
        self._print_message("DELETED: {}".format(dest_path))
    

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
        tmp_path_list = path.rsplit('/',1)
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

def watch(opts):
    print "---------- Peon Wacther start working ----------"
    
    src_dir = opts.src_dir or "src"
    dest_dir = opts.dest_dir or "build"
    
    render_opts = {
        "src": src_dir,
        "dest": dest_dir,
        "replacement": COMPILE_TYPES,
    }
    render = RenderHandler(render_opts)
    
    if opts.watcher == 'init':
        render.clean()
        render.render_all()
    
    server_progress = None
    if opts.port:
        port = str(opts.port or '')
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
        
    observer.join()
    


if __name__ == '__main__':
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
