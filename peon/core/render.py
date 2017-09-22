# coding=utf-8
from __future__ import absolute_import

import os
import shutil
import re
import sys
import subprocess
import sass
from datetime import datetime

from ..utlis import BeautifyPrint as bpcolor


# exception
class RenderingError(Exception):
    status_msg = 'RenderingError'
    affix_msg = None

    def __init__(self, error=None, message=None):
        self.error = error
        self.affix_msg = message

    def __str__(self):
        colored = bpcolor.FAIL + self.affix_msg + bpcolor.ENDC
        return '{}:{} => \n{}'.format(self.status_msg, colored, self.error)


# handlers
class RenderHandler(object):
    replacement = {
        'coffee': 'js',
        'decaf': 'js',  # `decaf` is coffeescript without header and wrapper.
        'less': 'css',
        'sass': 'css',
        'scss': 'css',
    }
    render_types = ['coffee', 'decaf', 'less', 'sass', 'scss',
                    'html', 'htm', 'tpl', 'tmpl']

    incl_mark = '_'  # current
    incl_parent_mark = '__'  # parent
    incl_global_mark = '_g_'  # global
    incl_root_mark = '_r_'  # root
    incl_init_mark = '__init__'  # root and equals
    incl_dir_mark = '{}{}'.format(os.path.sep, incl_mark)  # dir

    tmpl_file_type = 'tmpl'
    base_file_type = 'html'

    incl_regex = re.compile(r'(\s*)(\{%\s*(?:include|import)\s+' +
                            r'["\']?\s*([\w\$\-\./\{\}\(\)]*)\s*["\']?' +
                            r'\s*[^%\}]*%\})',
                            re.MULTILINE | re.DOTALL | re.IGNORECASE)
    tmpl_regex = re.compile(r'(\s*)(\{%\s*templates\s*%\})',
                            re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def __init__(self, src_dir='.', dest_dir='.', skips=None):

        self.root_dir = os.getcwd()
        self.src_dir = src_dir.strip(os.path.sep)
        self.dest_dir = dest_dir.strip(os.path.sep)

        self.dirs(self.dest_dir)

        if isinstance(skips, basestring):
            skips = [skips]
        elif not isinstance(skips, list):
            skips = []

        self.skip_includes = [str(incl).lower() for incl in (skips or [])]
        print 'Skiped include types: {}'.format(self.skip_includes)

        self.rendering_all = False

    def _raise_exception(self, err, src_path):
        sys.stdout.write('\a')
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
        self.dirs(os.path.dirname(file_path))
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

    def _in_skip_includes(self, file_ext):
        return any(x in self.skip_includes for x in ['*', file_ext])

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

    def _decaf_all(self):
        try:
            subprocess.check_output([
                'coffee', '-c', '-o', self.dest_dir, self.src_dir,
                '-b', '--no-header'
            ])
        except Exception as e:
            self._raise_exception(RenderingError(e, 'coffee all ↑'),
                                  self.src_dir)

    def _decaf(self, src_path, dest_path):
        try:
            subprocess.check_output(['coffee', '-c', '-o',
                                     os.path.dirname(dest_path), src_path,
                                     '-b', '--no-header'])
        except Exception as e:
            self._raise_exception(RenderingError(e, 'coffee ↑'), src_path)

    def _less(self, src_path, dest_path):
        try:
            result = subprocess.check_output(['lessc', src_path])
            self._write_file(dest_path, result)
        except Exception as e:
            self._raise_exception(RenderingError(e, 'less ↑'), src_path)

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
        if os.path.isdir(src_path):
            src_path = os.path.join(src_path, self.incl_init_mark)

        content = self._read_file(src_path)
        regex_result = self.incl_regex.findall(content)
        for space, match, include_path in regex_result:
            sub_path = self._relative_path(os.path.dirname(src_path),
                                           include_path)
            sub_content = self._process_html_includes(sub_path)
            # sub_splits = sub_content.splitlines()
            # _lines = u'{}'.format(space).join(sub_splits)
            """
            splitlines then join will cause multiple empty lines.
            also file shall not too larget.
            that's why it's ok not process by lines.
            """
            content = content.replace(match, sub_content)
        return content

    def _aggregate_templates(self, content, self_path):
        regex_result = self.tmpl_regex.findall(content)
        tmpl_ext = self.tmpl_file_type
        for space, match in regex_result:
            tmpl_series = [u'<!-- Begin Templates -->']
            for path in self.find_files(self.src_dir, file_ext=tmpl_ext):
                if os.path.isfile(path) and path != self_path:
                    _content = self._process_html_includes(path)
                    tmpl_series.append(_content)
            tmpl_series.append(u'<!-- End Templates -->')
            content = content.replace(match, '\n'.join(tmpl_series))
        return content

    def _html(self, src_path, dest_path, ext):
        try:
            if os.path.isfile(src_path):
                _, _, ext = self.split_file_path(src_path)
                if self._in_skip_includes(ext.lower()):
                    _content = self._read_file(src_path)
                else:
                    _content = self._process_html_includes(src_path)
                html_content = self._aggregate_templates(_content, src_path)
                self._write_file(dest_path, html_content)
        except Exception as e:
            self._raise_exception(RenderingError(e, 'html'), src_path)

    def _copy(self, src_path, dest_path):
        try:
            if os.path.isfile(src_path):
                self.dirs(os.path.dirname(dest_path))
                shutil.copy2(src_path, dest_path)
        except Exception as e:
            self._raise_exception(RenderingError(e, 'file'), src_path)

    def find_dest_path(self, path):
        if path.startswith(self.src_dir):
            path = path.replace(self.src_dir, '', 1).lstrip(os.path.sep)
        filepath, ext = os.path.splitext(path)
        ext = ext[1:].lower()
        comp_ext = self.replacement.get(ext, ext)
        compile_path = '{}{}{}'.format(self.dest_dir, os.path.sep, filepath)
        if comp_ext:
            compile_path = '{}.{}'.format(compile_path, comp_ext)
        return compile_path, comp_ext

    def split_file_path(self, path):
        filepath, ext = os.path.splitext(path)
        filepath_split = filepath.rsplit(os.path.sep, 1)
        if len(filepath_split) < 2:
            filepath_split.insert(0, '')
        return filepath_split[0], filepath_split[1], ext[1:].lower()

    def find_files(self, path='.', file_ext=None, recursive=True):
        results = []

        if file_ext and isinstance(file_ext, basestring):  # ext could ''
            file_ext = set([file_ext])
        elif isinstance(file_ext, list):
            file_ext = set(file_ext)

        def add_files(files, dirpath):
            for f in files:
                _, filename, ext = self.split_file_path(f)
                if filename.startswith('.') or self.is_include_file(f, ext):
                    continue
                if not file_ext or (ext in file_ext):
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
                if self.incl_dir_mark not in dirpath:
                    add_dirs(dirs, dirpath)
                    add_files(files, dirpath)
        return results

    def is_tmpl_file(self, filename, ext):
        return self.tmpl_file_type == ext

    def is_include_file(self, path, ext):
        if self._in_skip_includes(ext.lower()):
            return False
        return self.incl_dir_mark in path or path.startswith(self.incl_mark)

    def clean(self):
        if self.src_dir != self.dest_dir:
            shutil.rmtree(self.dest_dir.lstrip(os.path.sep))

    def render_all(self):
        print '\n<--- Rendering: {}/**/* --->\n'.format(self.src_dir)

        self.rendering_all = True
        has_coffee = False
        has_decaf = False
        # lessc cli not support output to folder

        all_files = self.find_files(self.src_dir)
        excludes = set(self.find_files(self.src_dir, self.tmpl_file_type))
        for f in all_files:
            _, _, ext = self.split_file_path(f)

            if ext == 'coffee':
                has_coffee = True
                excludes.add(f)
            if ext == 'decaf':
                has_decaf = True
                excludes.add(f)

        if has_coffee:
            self._coffee_all()
        if has_decaf:
            self._decaf_all()

        for f in [f for f in all_files if f not in excludes]:
            self.render(f)

        self.rendering_all = False

        print '\n<--- Rendered to: {}/**/* --->\n'.format(self.dest_dir)

    def render(self, src_path, replace=True):
        if os.path.isdir(src_path):
            self.dirs(src_path)
            return

        filedir, filename, ext = self.split_file_path(src_path)
        dest_path, comp_ext = self.find_dest_path(src_path)

        if not replace and os.path.isfile(dest_path):
            return

        if self.is_include_file(src_path, ext):
            if not ext:
                ext = self.base_file_type

            if ext not in self.render_types:
                # no ext file will render every file matched path,
                # such as `__init__` will render files form root dir.
                # `_g_` will render all file from root dir and every sub dir.
                return

            if filename.startswith(self.incl_root_mark) or \
               filename == self.incl_init_mark:
                path = None
                recursive = False
            elif filename.startswith(self.incl_global_mark):
                path = None
                recursive = True
            elif filename.startswith(self.incl_parent_mark):
                path = filedir
                recursive = True
            else:
                path_pairs = filedir.split(self.incl_dir_mark)
                path = path_pairs[0]
                recursive = False

            files = self.find_files(path, ext, recursive)

            for f in files:
                self.render(f)

            return

        elif self.is_tmpl_file(filename, ext):
            # when tmpl file chagned render all root files once
            root_files = self.find_files(self.src_dir,
                                         ('html', 'htm', 'tpl'),
                                         recursive=False)
            files = [rf for rf in root_files if not os.path.isdir(rf)]
            for f in files:
                self.render(f)
            return

        print '--------------------'
        try:
            if ext == 'coffee':
                self._coffee(src_path, dest_path)
            elif ext == 'decaf':
                self._decaf(src_path, dest_path)

            elif ext == 'less':
                self._less(src_path, dest_path)

            elif ext in ('sass', 'scss'):
                self._sass(src_path, dest_path)

            elif ext in ('html', 'tpl'):
                self._html(src_path, dest_path, ext)

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

    def dirs(self, dir_path):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

    def move(self, src_path, move_to_path):
        dest_path, comp_ext = self.find_dest_path(src_path)
        dest_moved_path, _ = self.find_dest_path(move_to_path)
        _, moved_filename, moved_ext = self.split_file_path(move_to_path)

        if self.is_include_file(move_to_path, moved_ext) or \
           self.is_tmpl_file(moved_filename, moved_ext):
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
