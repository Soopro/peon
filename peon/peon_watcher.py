#coding=utf-8
from __future__ import absolute_import

import os, time, shutil
import subprocess
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler


# variables
WATCH_FILE_TYPES = {
    "coffee":"js",
    "jade":"html",
    "less":"css"
}
SLEEP_TIME = 1

INCL_MARK = "_"
INCL_ROOT_MARK = "__"
INCL_G_MARK = "_g_"

# handlers
class WatchPatternsHandler(PatternMatchingEventHandler):
    
    def __init__(self, patterns=None, ignore_patterns=None,
                     ignore_directories=False, case_sensitive=False):
        super(PatternMatchingEventHandler, self).__init__()

        self._replacement = patterns
        _tmp_patterns = []
        for p in patterns:
            _tmp_patterns.append("*."+p)

        self._patterns = _tmp_patterns
        self._ignore_patterns = ignore_patterns
        self._ignore_directories = ignore_directories
        self._case_sensitive = case_sensitive
        self._hard_delete = False
        self.root = os.getcwd()
    
    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
  
        if event.event_type in ('modified','created'):
            self.render(event.src_path)
        elif event.event_type is 'moved':
            dest_path = event.dest_path if event.dest_path else None
            self.move(event.src_path, dest_path)
        elif event.event_type is 'deleted':
            self.delete(event.src_path)

    def _print_line(self):
        print "-------------------------------", time.time()
    
    def _raise_exception(self, e, src_path):
        print "---------- Exception ----------"
        print e
    
    def _compile_path_filter(self, path):
        filename, ext = os.path.splitext(path)
        ext = ext[1:]
        comp_ext = self._replacement.get(ext)
        compile_path = "{}.{}".format(filename, comp_ext)
        return compile_path, comp_ext
    
    def _file_filter(self, path):
        filename, ext = os.path.splitext(path)
        filename = filename.rsplit('/',1)
        return filename[1], ext[1:], filename[0]
    
    def _find_files(self, file_type=None, path='.', includes=False):
        results = []
        
        def _add_files(files, dirpath):
            for f in files:
                filename, ext = os.path.splitext(f)

                if filename.startswith('.') or ext[1:] not in WATCH_FILE_TYPES:
                    continue
            
                is_includes = False
                if filename.startswith(INCL_MARK) \
                or filename.endswith(INCL_MARK):
                    is_includes = True
                
                if not includes and is_includes:
                    continue
                if includes and not is_includes:
                    continue
                if ext[1:] == file_type or not file_type:
                    results.append(os.path.join(dirpath, f))
        
        if not path:
            _add_files(os.listdir("."), ".")
        else:
            for dirpath, dirs, files in os.walk(path):
                _add_files(files, dirpath)

        return results
    
    def set_hard_delete(self, hard=True):
        self._hard_delete = hard
    
    def render_all(self):
        files = self._find_files()
        for f in files:
            self.render(f, includes=False)
        print "---------- All files rendered. ----------"
                
    def render(self, src_path, includes=True, replace=True):
        filename, ext, filepath = self._file_filter(src_path)
        src_compile_path, comp_ext = self._compile_path_filter(src_path)
        
        if not comp_ext:
            return
        if not replace and os.path.isfile(src_compile_path):
            return
        
        if filename.startswith(INCL_MARK) or filename.endswith(INCL_MARK):
            if includes:
                if filename.startswith(INCL_ROOT_MARK):
                    path = None
                elif filename.startswith(INCL_G_MARK):
                    path = "."
                else:
                    path = filepath
                
                files = self._find_files(ext, path)
                for f in files:
                    self.render(f)
                return
            else:
                return
        
        if ext == 'coffee':
            try:
                result = subprocess.call(["coffee", "-c", src_path])
                if result == -2:
                    exit()
            except Exception as e:
                self._raise_exception(e, src_path)

        elif ext == 'less':
            try:
                result = subprocess.call(["lessc", src_path, src_compile_path])
                if result == -2:
                    exit()
            except Exception as e:
                self._raise_exception(e, src_path)

        elif ext == 'jade':
            try:
                result =subprocess.call(["jade", '-P', src_path])
                if result == -2:
                    exit()
            except Exception as e:
                self._raise_exception(e, src_path)
        
        report = {"src": src_path, "dest": src_compile_path}
        print "{src} ==> {dest}".format(**report)
        self._print_line()
        
    
    def move(self, src_path, dest_path):
        src_compile_path, comp_ext = self._compile_path_filter(src_path)
        dest_compile_path, _ = self._compile_path_filter(dest_path)
        
        try:
            if os.path.isfile(src_compile_path):
                os.rename(src_compile_path, dest_compile_path)
            else:
                comp_ext = None
        except Exception as e:
            self._raise_exception(e, src_path)
        
        report = {"src": src_path, "dest": dest_path, "ext": comp_ext}
        print "{src}({ext}) --> {dest}({ext})".format(**report)
        self._print_line()
  
        
    def delete(self, src_path):
        src_compile_path, comp_ext = self._compile_path_filter(src_path)
        try:    
            if os.path.isfile(src_compile_path):
                os.remove(src_compile_path)
            else:
                comp_ext = None
        except Exception as e:
            self._raise_exception(e, src_path)
        
        report = {"src": src_path, "ext": comp_ext}
        print "{src}({ext}) --> x".format(**report)
        self._print_line()

    
    def on_modified(self, event):
        self.process(event)
    
    def on_moved(self, event):
        self.process(event)
    
    def on_deleted(self, event):
        if self._hard_delete:
            self.process(event)
    
    def on_created(self, event):
        self.process(event)


#-------------
# main
#-------------

def watch(opts):
    print "---------- Peon Wacther start working ----------"
    observer = Observer()
    
    watcher = WatchPatternsHandler(patterns=WATCH_FILE_TYPES)
    if opts.watcher == 'init':
        watcher.render_all()
    
    if opts.hard:
        watcher.set_hard_delete(True)

    observer.schedule(watcher, '.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        observer.stop()
        
    observer.join()
    


if __name__ == '__main__':
    watch()
