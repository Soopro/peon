#coding=utf-8
from __future__ import absolute_import

import os, time, shutil, re, sys
import subprocess
import sass
from datetime import datetime

from ..utlis import BeautifyPrint as bpcolor

# exception
class RenderingError(Exception):
    status_msg = 'RenderingError'
    affix_msg = None

    def __init__(self, error = None, message = None):
        self.error = error
        self.affix_msg = message

    def __str__(self):
        return '{}:{} => \n{}'.format(self.status_msg,
                              bpcolor.FAIL+self.affix_msg+bpcolor.ENDC,
                              self.error)


# handlers
class RenderHandler(object):
    replacement = {
        'coffee': 'js',
        'less': 'css',
        'sass': 'css',
        'scss': 'css',
    }
    render_types = ['coffee', 'less', 'sass', 'scss',
                    'html', 'htm', 'xml', 'xhtml', 'shtml', 'tpl']

    incl_regex = re.compile(r'(\s*)(\{%\s*(?:include|import)\s+' +
                            r'["\']?\s*([\w\$\-\./\{\}\(\)]*)\s*["\']?' +
                            r'\s*[^%\}]*%\})',
                            re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def __init__(self, opts={}):

        if not isinstance(opts, dict):
            raise Exception('Render options is invalid. (opts)')

        self.root_dir = os.getcwd()
        self.src_dir = opts.get('src', '.').strip(os.path.sep)
        self.dest_dir = opts.get('dest', '.').strip(os.path.sep)

        self.replacement = opts.get('replacement', self.replacement)

        if not os.path.isdir(self.dest_dir):
            os.makedirs(self.dest_dir)

        skips = opts.get('skip_includes')
        if isinstance(skips, (str, unicode)):
            skips = [skips]
        elif not isinstance(skips, list):
            skips = []

        self.skip_includes = []
        for incl in skips:
            try:
                incl = str(incl)
            except Exception:
                continue
            self.skip_includes.append(incl.lower())

        print 'Skiped include types: {}'.format(self.skip_includes)

        include_marks = opts.get('include_marks', {})

        self.incl_mark = include_marks.get('base', '_')
        self.incl_parent_mark = include_marks.get('parent', '__')
        self.incl_global_mark = include_marks.get('global', '_g_')
        self.incl_root_mark = include_marks.get('root', '_r_')
        self.rendering_all = False

    def _raise_exception(self, err, src_path):
        sys.stdout.write("\a")
        print '--------------------'
        print '[{}Exception{}]: {}'.format(bpcolor.FAIL, bpcolor.ENDC, err)
        print '[src_path]: {}'.format(src_path)
        print '--------------------'
        raise err

    def _print_message(self, message):
        print '[{}] {}'.format(datetime.now().strftime('%H:%M:%S'), message)

    def _read_file(self, file_path):
        file = open(file_path)
        file_source = file.read().decode('utf-8')
        file.close()
        return file_source

    def _write_file(self, file_path, file_source):
        if os.path.isfile(file_path):
            os.remove(file_path)
        tmp = open(file_path, 'w')
        if isinstance(file_source, unicode):
            file_source = file_source.encode('utf-8')
        tmp.write(file_source)
        tmp.close()
        return file_path

    def _move_file(self, src_path, dest_path):
        if os.path.isfile(dest_path):
            os.remove(dest_path)
        if os.path.isfile(src_path):
            os.rename(src_path, dest_path)
        return src_path

    def _in_skip_includes(self, file_type):
        return any(x in self.skip_includes for x in ['*', file_type])

    def _coffee_all(self):
        try:
            subprocess.check_output([
                'coffee', '-c', '-o', self.dest_dir, self.src_dir
            ])
        except Exception as e:
            self._raise_exception(RenderingError(e, 'coffee all ↑'),
                                  self.src_dir)

    def _coffee(self, src_path, dest_path):
        try:
            subprocess.check_output(['coffee', '-c', '-o',
                                     os.path.dirname(dest_path), src_path])
        except Exception as e:
            self._raise_exception(RenderingError(e, 'coffee ↑'), src_path)

    def _less(self, src_path, dest_path):
        try:
            result = subprocess.check_output(['lessc', src_path])
            self._write_file(dest_path, result)
        except Exception as e:
            self._raise_exception(RenderingError(e, 'less ↑'), src_path)

    def _sass_all(self):
        # sass_update_path = "{}:{}".format(self.src_dir, self.dest_dir)
        try:
            # subprocess.check_output(["sass", "--sourcemap=none",
            #                          "--update", sass_update_path])
            sass.compile(dirname=(self.src_dir, self.dest_dir))
        except Exception as e:
            self._raise_exception(RenderingError(e, 'sass all ↑'),
                                  self.src_dir)

    def _sass(self, src_path, dest_path):
        try:
            result = sass.compile(filename=src_path)
            self._write_file(dest_path, result)
            # subprocess.check_output(["sass", "--sourcemap=none",
            #                          src_path, dest_path])
        except Exception as e:
            self._raise_exception(RenderingError(e, 'sass ↑'), src_path)

    def _relative_path(self, base, path):
        if path.startswith(os.path.sep):
            return os.path.join(self.src_dir, path[1:])
        else:
            return os.path.normpath(os.path.join(base, path))

    def _process_html_includes(self, src_path):
        content = self._read_file(src_path)
        regex_result = self.incl_regex.findall(content)
        for space, match, include_path in regex_result:
            sub_path = self._relative_path(os.path.dirname(src_path),
                                           include_path)
            sub_content = self._process_html_includes(sub_path)
            sub_splits = sub_content.splitlines()
            _line = u'{}'.format(space)
            # because the regex is match after spaces,
            # so only add spaces for other lines.
            content = content.replace(match, _line.join(sub_splits))
        return content

    def _html(self, src_path, dest_path):
        try:
            if os.path.isfile(src_path):
                if not os.path.exists(os.path.dirname(dest_path)):
                    os.makedirs(os.path.dirname(dest_path))

                _, _, ext = self.split_file_path(src_path)
                if self._in_skip_includes(ext.lower()):
                    html_content = self._read_file(src_path)
                else:
                    html_content = self._process_html_includes(src_path)
                self._write_file(dest_path, html_content)
        except Exception as e:
            self._raise_exception(RenderingError(e, 'html'), src_path)

    def _copy(self, src_path, dest_path):
        try:
            if os.path.isfile(src_path):
                if not os.path.exists(os.path.dirname(dest_path)):
                    os.makedirs(os.path.dirname(dest_path))
                shutil.copy2(src_path, dest_path)
        except Exception as e:
            self._raise_exception(RenderingError(e, 'file'), src_path)

    def find_dest_path(self, path, output_ext=True):
        if path.startswith(self.src_dir):
            path = path.replace(self.src_dir, '', 1).lstrip(os.path.sep)
        filepath, ext = os.path.splitext(path)
        ext = ext[1:].lower()
        comp_ext = self.replacement.get(ext, ext)
        compile_path = '{}{}{}'.format(self.dest_dir, os.path.sep, filepath)
        if comp_ext:
            compile_path = '{}.{}'.format(compile_path, comp_ext)
        if output_ext:
            return compile_path, comp_ext
        else:
            return compile_path

    def split_file_path(self, path):
        filepath, ext = os.path.splitext(path)
        filepath_split = filepath.rsplit(os.path.sep, 1)
        if len(filepath_split) < 2:
            filepath_split.insert(0, '')
        return filepath_split[0], filepath_split[1], ext[1:].lower()

    def find_files(self, path='.', file_type=None, recursive=True):
        results = []

        def add_files(files, dirpath):
            for f in files:
                _, filename, ext = self.split_file_path(f)

                if filename.startswith('.') or \
                   self.is_include_file(filename, ext):
                    continue

                if ext == file_type or not file_type:
                    results.append(os.path.join(dirpath, f))

        def add_dirs(dirs, dirpath):
            for d in dirs:
                results.append(os.path.join(dirpath, d))

        if not path:
            path = self.src_dir

        if not recursive:
            add_files(os.listdir(path), path)
        else:
            for dirpath, dirs, files in os.walk(path):
                add_dirs(dirs, dirpath)
                add_files(files, dirpath)

        return results

    def is_include_file(self, filename, ext):
        if self._in_skip_includes(ext.lower()):
            return False
        is_incl_file = filename.startswith(self.incl_mark) or \
            filename.endswith(self.incl_mark)
        return is_incl_file

    def clean(self):
        if self.src_dir != self.dest_dir:
            shutil.rmtree(self.dest_dir.lstrip(os.path.sep))

    def render_all(self):
        self._print_message('Rendering all: {}/**/*'.format(self.src_dir,
                                                            self.dest_dir))
        self.rendering_all = True
        has_coffee = False
        has_sass = False
        # lessc cli not support output to folder

        all_files = self.find_files(self.src_dir)
        excludes = []
        for f in all_files:
            _, _, ext = self.split_file_path(f)

            if ext == 'coffee':
                has_coffee = True
                excludes.append(f)
            elif ext in ['sass', 'scss']:
                has_sass = True
                excludes.append(f)

        if has_coffee:
            self._coffee_all()
        if has_sass:
            self._sass_all()

        _files = [f for f in all_files if f not in excludes]
        for f in _files:
            self.render(f)

        self.rendering_all = False

        # clean up invalid files in dest folder
        all_dest_path = [self.find_dest_path(f, False) for f in all_files]

        for dirpath, dirs, files in os.walk(self.dest_dir):
            for f in files:
                f_path = os.path.join(dirpath, f)
                if f_path not in all_dest_path:
                    os.remove(f_path)

        self._print_message('Rendered all: {}/**/*'.format(self.src_dir,
                                                           self.dest_dir))

    def render(self, src_path, replace=True):
        if os.path.isdir(src_path):
            self.dirs(src_path)
            return
        filedir, filename, ext = self.split_file_path(src_path)
        dest_path, comp_ext = self.find_dest_path(src_path)

        if not replace and os.path.isfile(dest_path):
            return

        if self.is_include_file(filename, ext):
            if ext not in self.render_types:
                # this cheat for some file not render to dest,
                # not really a includes
                return
            if filename.startswith(self.incl_root_mark):
                path = None
                recursive = False
            elif filename.startswith(self.incl_global_mark):
                path = None
                recursive = True
            elif filename.startswith(self.incl_parent_mark):
                path = filedir
                recursive = True
            else:
                path = filedir
                recursive = False

            files = self.find_files(path, ext, recursive)
            for f in files:
                self.render(f)
            return

        print '--------------------'
        try:
            if ext == 'coffee':
                self._coffee(src_path, dest_path)

            elif ext == 'less':
                self._less(src_path, dest_path)

            elif ext in ('sass', 'scss'):
                self._sass(src_path, dest_path)

            elif ext in ('html', 'tpl'):
                self._html(src_path, dest_path)

            elif self.src_dir != self.dest_dir:
                self._copy(src_path, dest_path)

            else:
                return False
        except Exception as e:
            if self.rendering_all:
                raise e
            else:
                return

        self._print_message('Rendered: {} --> {}'.format(src_path, dest_path))

    def dirs(self, src_path):
        dest_path, _ = self.find_dest_path(src_path)
        if os.path.isdir(src_path) and not os.path.isdir(dest_path):
            os.makedirs(dest_path)

    def move(self, src_path, move_to_path):
        dest_path, comp_ext = self.find_dest_path(src_path)
        dest_moved_path, _ = self.find_dest_path(move_to_path)
        _, moved_filename, moved_ext = self.split_file_path(move_to_path)

        if self.is_include_file(moved_filename, moved_ext):
            try:
                if os.path.isfile(dest_path):
                    os.remove(dest_path)
                else:
                    return
            except Exception as e:
                self._raise_exception(e, src_path, e)
                return
            self._print_message('Deleted: {}'.format(dest_path))
        else:
            try:
                if os.path.exists(dest_path):
                    shutil.move(dest_path, dest_moved_path)
                else:
                    # render the moved file if not exists.
                    self.render(move_to_path)

            except Exception as e:
                self._raise_exception(e, src_path, e)
                return
            self._print_message('Moved: {} --> {}'.format(dest_path,
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
            self._raise_exception(e, src_path, e)
            return

        self._print_message('Deleted: {}'.format(dest_path))
