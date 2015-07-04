#coding=utf-8
from __future__ import absolute_import

import os, time, shutil
import subprocess
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler


# variables
COMPILE_TYPES = {
    "coffee":"js",
    "jade":"html",
    "less":"css",
    "sass":"css",
    "scss":"css",
}
SLEEP_TIME = 1

# handlers
class WatchPatternsHandler(PatternMatchingEventHandler):
    
    def __init__(self, dest_dir='.',
                       src_dir='.',
                       patterns=None,
                       replacement={},
                       include_marks={},
                       ignore_patterns=None,
                       ignore_directories=False,
                       case_sensitive=False):

        super(PatternMatchingEventHandler, self).__init__()
        self._patterns = patterns
        self._ignore_patterns = ignore_patterns
        self._ignore_directories = ignore_directories
        self._case_sensitive = case_sensitive
        
        self.replacement = replacement
        self.root_dir = os.getcwd()
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        if not os.path.isdir(self.dest_dir):
            os.mkdir(self.dest_dir)
        
        self.include_mark = include_marks.get('base', '_')
        self.include_global_mark = include_marks.get('global', '_g_')
        self.include_root_mark = include_marks.get('root', '__')
        
    def _print_message(self, message):
        print "[{}] {}".format(int(time.time()), message)
    
    def _raise_exception(self, e, src_path):
        print "--------------------"
        print "[Exception]: {}".format(e)
        print "--------------------"
    
    def _compile_path_filter(self, path):
        if path.startswith(self.src_dir):
            path = path.replace(self.src_dir, '', 1).lstrip('/')
        filename, ext = os.path.splitext(path)
        ext = ext[1:]
        comp_ext = self.replacement.get(ext, ext)
        compile_path = "{}/{}".format(self.dest_dir, filename)
        if comp_ext:
            compile_path = "{}.{}".format(compile_path, comp_ext)
        return compile_path, comp_ext
    
    def _file_path_filter(self, path):
        filename, ext = os.path.splitext(path)
        filename = filename.rsplit('/',1)
        return filename[1], ext[1:], filename[0]
    
    def _find_files(self, path='.', file_type=None, includes=False):
        results = []
        
        def _add_files(files, dirpath):
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
        
        if not path:
            _add_files(os.listdir(self.src_dir), self.src_dir)
        else:
            for dirpath, dirs, files in os.walk(path):
                _add_files(files, dirpath)

        return results
    
    
    def _find_end_path(self, path):
        if not path:
            return None
        tmp_path_list = path.rsplit('/',1)
        if len(tmp_path_list) > 0:
            return tmp_path_list[1]
        else:
            return None
            
    
    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        
        if event.event_type is 'created':
            self.render(event.src_path)
        elif event.event_type is 'modified':
            if not event.is_directory:
                self.render(event.src_path)
        elif event.event_type is 'moved':
            end_src_path = self._find_end_path(event.src_path)
            end_dest_path = self._find_end_path(event.dest_path)
            if end_src_path != end_dest_path:
                self.move(event.src_path, event.dest_path)
        elif event.event_type is 'deleted':
            self.delete(event.src_path)
        
    def is_include_file(self, filename):
        is_include_file = filename.startswith(self.include_mark) \
                               or filename.endswith(self.include_mark)
        return is_include_file
    
    def clean(self):
        if self.src_dir != self.dest_dir:
            shutil.rmtree(self.dest_dir)
        
    def render_all(self):
        files = self._find_files(self.src_dir)
        for f in files:
            self.render(f, includes=False)
        self._print_message(
            "[ {}/**/* ==> {}/**/* ]".format(self.src_dir, self.dest_dir)
        )
                
    def render(self, src_path, includes=True, replace=True):
        filename, ext, filepath = self._file_path_filter(src_path)
        dest_path, comp_ext = self._compile_path_filter(src_path)
        
        if not replace and os.path.isfile(dest_path):
            return
        
        if includes and self.is_include_file(filename):
            if filename.startswith(include_root_mark):
                path = None
            elif filename.startswith(include_global_mark):
                path = self.src_dir
            else:
                path = filepath
            
            files = self._find_files(path, ext)
            for f in files:
                self.render(f)
            return
        
        if ext == 'coffee':
            try:
                result = subprocess.call(["coffee", "-c", src_path])
                if result == -2:
                    exit()
            except Exception as e:
                self._raise_exception(e, src_path)
                return

        elif ext == 'less':
            try:
                result = subprocess.call(["lessc", src_path, dest_path])
                if result == -2:
                    exit()
            except Exception as e:
                self._raise_exception(e, src_path)
                return
        
        elif ext in ['sass','scss']:
            try:
                result = subprocess.call(["sass", "--sourcemap=none",
                                          src_path, dest_path])
                if result == -2:
                    exit()
            except Exception as e:
                self._raise_exception(e, src_path)
                return

        elif ext == 'jade':
            try:
                result = subprocess.call(["jade", '-P', src_path])
                if result == -2:
                    exit()
            except Exception as e:
                self._raise_exception(e, src_path)
                return

        elif self.src_dir != self.dest_dir:
            try:
                if os.path.isdir(src_path) and not os.path.isdir(dest_path):
                    os.makedirs(dest_path)
                elif os.path.isfile(src_path):
                    if not os.path.exists(os.path.dirname(dest_path)):
                        os.makedirs(os.path.dirname(dest_path))
                    shutil.copy2(src_path, dest_path)
            except Exception as e:
                self._raise_exception(e, src_path)
                return
        else:
            return
    
        self._print_message(
            "{} --> {}".format(src_path, dest_path)
        )
        
    
    def move(self, src_path, move_to_path):
        dest_path, comp_ext = self._compile_path_filter(src_path)
        dest_moved_path, _ = self._compile_path_filter(move_to_path)
        
        try:
            shutil.move(dest_path, dest_moved_path)
        except Exception as e:
            self._raise_exception(e, src_path)
            return

        self._print_message(
            "{} --> {}".format(dest_path, dest_moved_path)
        )
  
        
    def delete(self, src_path):
        dest_path, comp_ext = self._compile_path_filter(src_path)
        try:    
            if os.path.isfile(src_path):
                os.remove(dest_path)
            elif os.path.isdir(src_path):
                shutil.rmtree(dest_path)
            else:
                return
        except Exception as e:
            self._raise_exception(e, src_path)
            return
            
        self._print_message(
            "{} --> DELETED".format(dest_path)
        )

    
    def on_modified(self, event):
        self.process(event)
    
    def on_moved(self, event):
        self.process(event)
    
    def on_deleted(self, event):
        self.process(event)
    
    def on_created(self, event):
        self.process(event)


#-------------
# main
#-------------

def watch(opts):
    print "---------- Peon Wacther start working ----------"
    src_dir = 'src'
    dest_dir = 'build'
    
    observer = Observer()
    watcher = WatchPatternsHandler(dest_dir = dest_dir,
                                   src_dir = src_dir,
                                   replacement = COMPILE_TYPES,
                                   ignore_patterns = ['*/.*'])
    if opts.watcher == 'init':
        watcher.clean()
        watcher.render_all()

    observer.schedule(watcher, src_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        observer.stop()
        
    observer.join()
    


if __name__ == '__main__':
    watch()
