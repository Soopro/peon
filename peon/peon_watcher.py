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
    
    def _come_path_filter(self, path):
        filename, ext = os.path.splitext(path)
        ext = ext[1:]
        comp_ext = self._replacement[ext]
        comp_path = "{}.{}".format(filename, comp_ext)
        return comp_path, comp_ext
    
    def _file_filter(self, path):
        filename, ext = os.path.splitext(path)
        filename = filename.rsplit('/',1)
        return filename[1], ext[1:]
    
    def _find_files(self, file_type, includes=False):
        results = []
        
        for dirpath, dirs, files in os.walk("."):
            for f in files:
                filename, ext = os.path.splitext(f)
                if filename.startswith('.'):
                    continue

                is_includes = False
                if filename.startswith('_') or filename.endswith('_'):
                    is_includes = True
                    
                if not includes and is_includes:
                    continue
                if includes and not is_includes:
                    continue
                if ext[1:] == file_type:
                    results.append(os.path.join(dirpath, f))
        return results
    
    def render(self, src_path):
        filename, ext = self._file_filter(src_path)
        src_comp_path, comp_ext = self._come_path_filter(src_path)

        is_includes = False
        if filename.startswith('_') or filename.endswith('_'):
            is_includes = True
            files = self._find_files(ext)
            for f in files:
                self.render(f)
            return
        
        if ext == 'coffee':
            try:
                subprocess.call(["coffee","-c", src_path])
            except Exception as e:
                self._raise_exception(e, src_path)

        elif ext == 'less':
            try:
                subprocess.call(["lessc", src_path, src_comp_path])
            except Exception as e:
                self._raise_exception(e, src_path)

        elif ext == 'jade':
            try:
                subprocess.call(["jade", '-P', src_path])
            except Exception as e:
                self._raise_exception(e, src_path)
        
        report = {"src": src_path, "dest": src_comp_path}
        print "{src} ==> {dest}".format(**report)
        self._print_line()
        
    
    def move(self, src_path, dest_path):
        src_comp_path, comp_ext = self._come_path_filter(src_path)
        dest_comp_path, _ = self._come_path_filter(dest_path)
        
        try:
            if os.path.isfile(src_comp_path):
                os.rename(src_comp_path, dest_comp_path)
            else:
                comp_ext = None
        except Exception as e:
            self._raise_exception(e, src_path)
        
        report = {"src": src_path, "dest": dest_path, "ext": comp_ext}
        print "{src}({ext}) --> {dest}({ext})".format(**report)
        self._print_line()
  
        
    def delete(self, src_path):
        src_comp_path, comp_ext = self._come_path_filter(src_path)
        try:    
            if os.path.isfile(src_comp_path):
                os.remove(src_comp_path)
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
        self.process(event)
    
    def on_created(self, event):
        self.process(event)

# functions
def watch():
    print "---------- Peon Wacther start working ----------"
    observer = Observer()
    watch_patterns = []
    watcher = WatchPatternsHandler(patterns=WATCH_FILE_TYPES)
    
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
