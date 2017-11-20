# coding=utf-8
from __future__ import absolute_import

import os

import shutil
import re
import subprocess
import htmlmin
import jsmin
import cssmin

from ..utlis.colors import BeautifyPrint as bpcolor
from ..utlis.base import ensure_dir


# exception
class CompressError(Exception):
    status_msg = 'CompressError'
    affix_msg = None

    def __init__(self, message=None):
        self.affix_msg = message

    def __str__(self):
        colored_text = bpcolor.FAIL + self.affix_msg + bpcolor.ENDC
        return '{}:{}'.format(self.status_msg, colored_text)


# handlers
class MinifyHandler(object):
    temp_file = '_minify_temp_.tmp'
    temp_js_file = '_minify_temp_.js'

    tmpl_regex = re.compile('<\!--\s*ng\-templates\s*-->', re.IGNORECASE)

    build_regex = re.compile('(<\!--\s*build:\s*(\[?\s*[\w-]+\s*\]?)' +
                             '\s+([\w\$\-\./\{\}\(\)]*)(\?.*?)*\s*-->' +
                             '(.*?)<\!--\s*/build\s*-->)',
                             re.MULTILINE | re.DOTALL | re.IGNORECASE)

    attr_regex = re.compile('\[["\']?\s*([^"\']+)\s*["\']?\]', re.IGNORECASE)
    src_regex = re.compile('src=["\']?\s*([^"\']+)\s*["\']?', re.IGNORECASE)
    href_regex = re.compile('href=["\']?\s*([^"\']+)\s*["\']?', re.IGNORECASE)

    comment_regex = re.compile('<\!--\s*(.*?)\s*-->', re.IGNORECASE)

    incl_mark = '_'
    incl_dir_mark = '{}{}'.format(os.path.sep, incl_mark)

    minify_includes = False
    mangle_js = False

    cwd_dir = 'dist'

    def __init__(self, cwd, minify_includes=False, mangle_js=False):
        self.cwd_dir = cwd.strip(os.path.sep)
        self.minify_includes = minify_includes
        self.mangle_js = mangle_js

    def _isfile(self, file_path):
        if os.path.isfile(file_path):
            return True
        else:
            _colored = bpcolor.OKBLUE + file_path + bpcolor.ENDC
            print 'peon: Minify skip file ---> {}'.format(_colored)
            return False

    def _read_file(self, file_path):
        try:
            file = open(file_path)
            file_source = file.read().decode('utf-8')
            file.close()
            return file_source
        except Exception as e:
            print e
            raise CompressError('read_file')

    def _write_file(self, file_path, file_source):
        if os.path.isfile(self.temp_file):
            os.remove(self.temp_file)
        try:
            tmp = open(self.temp_file, 'w')
            if isinstance(file_source, unicode):
                file_source = file_source.encode('utf-8')
            tmp.write(file_source)
            tmp.close()
        except Exception as e:
            print e
            raise CompressError('process_html:write')
        if os.path.isfile(file_path):
            os.remove(file_path)
        os.rename(self.temp_file, file_path)
        print 'peon: Minify writed ---> {}'.format(file_path)
        return file_path

    def is_include_file(self, path):
        if self.minify_includes:
            return False
        return self.incl_dir_mark in path or path.startswith(self.incl_mark)

    def _process_html(self, file_path, beautify=False):
        print "peon: Minify HTML process start"

        build_regex = self.build_regex
        src_regex = self.src_regex
        href_regex = self.href_regex
        attr_regex = self.attr_regex
        comment_regex = self.comment_regex

        curr_dir = os.path.dirname(file_path)

        content = self._read_file(file_path)
        regex_result = build_regex.findall(content)

        for match, comp_type, comp_file, comp_param, text in regex_result:
            replacement = ''

            if not comp_file or not comp_type:
                content = content.replace(match, '')
                continue

            if comp_file.startswith(os.path.sep):
                comp_file_path = os.path.join(self.cwd_dir, comp_file[1:])
            else:
                comp_file_path = os.path.join(curr_dir, comp_file)

            if comp_type == 'replace':
                replist = []
                for repl in comment_regex.findall(text):
                    replist.append(repl)
                replacement = u'\n'.join(replist)

            elif comp_type == 'css':
                css_series = []
                _text = re.sub(comment_regex, u'', text)
                for href in href_regex.findall(_text):
                    if href.startswith(os.path.sep):
                        _path = os.path.join(self.cwd_dir, href[1:])
                    else:
                        _path = os.path.join(curr_dir, href)

                    css_series.append(self._read_file(_path))

                if beautify:
                    css_source = u'\n'.join(css_series)
                else:
                    css_source = self._css(u'\n'.join(css_series))

                ensure_dir(comp_file_path, True)
                self._output(comp_file_path, css_source)

                new_css_tpl = u'<link rel="stylesheet" href="{}">'
                replacement = new_css_tpl.format(comp_file + comp_param)

            elif comp_type == 'js':
                js_series = []
                _text = re.sub(comment_regex, u'', text)
                for src in src_regex.findall(_text):
                    if src.startswith(os.path.sep):
                        _path = os.path.join(self.cwd_dir, src[1:])
                    else:
                        _path = os.path.join(curr_dir, src)

                    js_series.append(self._read_file(_path))

                if beautify:
                    js_source = u'\n'.join(js_series)
                else:
                    js_source = self._js(u'\n'.join(js_series))

                ensure_dir(comp_file_path, True)
                self._output(comp_file_path, js_source)

                new_js_tpl = u'<script src="{}"></script>'
                replacement = new_js_tpl.format(comp_file + comp_param)

            else:
                search_attr = attr_regex.search(comp_type)
                if search_attr:
                    attr_name = search_attr.group(1)
                if not attr_name:
                    continue
                _r_str = r'({}=["\']?\s*([^"\']+)\s*["\']?)'
                pattern = _r_str.format(attr_name)
                comp_attr_regex = re.compile(pattern, re.IGNORECASE)
                replacement = re.sub(comment_regex, u'', text)

                for attr_match, attr in comp_attr_regex.findall(text):
                    if attr.startswith(os.path.sep):
                        _src_path = os.path.join(self.cwd_dir, attr[1:])
                    else:
                        _src_path = os.path.join(curr_dir, attr)
                    if self._isfile(_src_path) and \
                       _src_path != comp_file_path:
                        ensure_dir(comp_file_path, True)
                        shutil.copy2(_src_path, comp_file_path)
                    new_attr = '{}="{}"'.format(attr_name,
                                                comp_file + comp_param)
                    replacement = replacement.replace(attr_match, new_attr)

            if not replacement:
                continue

            content = content.replace(match, replacement)

            print 'peon: processe_html {}'.format(comp_type)
            print '--------------------'
            print text.replace('\n', '').replace('  ', ' ')
            print '--->'
            print replacement.replace('\n', '').replace('  ', ' ')
            print '--------------------'

        return content

    def _output(self, dest_path, content):
        self._write_file(dest_path, content)
        return dest_path

    def _css(self, source):
        try:
            minifed = cssmin.cssmin(source)
        except Exception as e:
            print e
            raise CompressError('css')
        return minifed

    def _uglifyjs(self, source):
        try:
            tmp_path = self._write_file(self.temp_js_file, source)
            minifed = subprocess.check_output(["uglifyjs", tmp_path, '-m'])
            os.remove(tmp_path)
        except Exception as e:
            print e
            print "Make it sure uglifyjs is work fine!"
            raise CompressError('js')
        return minifed

    def _js(self, source):
        if self.mangle_js:
            return self._uglifyjs(source)
        try:
            minifed = jsmin.jsmin(source)
        except Exception as e:
            print e
            raise CompressError('js')
        return minifed

    def _html(self, source):
        try:
            """
            Remove comments found in HTML. Individual comments can be
            maintained by putting a ! as the first character inside the
            comment.
            <!-- FOO --> <!--! BAR --> become to <!-- BAR -->
            """
            minifed = htmlmin.minify(source,
                                     remove_comments=True,
                                     remove_empty_space=True)
        except Exception as e:
            print e
            raise CompressError('html')
        return minifed

    def _make_ng_tpl(self, tmpl_id, tmpl_content, beautify=False):
        if beautify:
            new_line = u'\n'
        else:
            tmpl_content = self._html(tmpl_content)
            new_line = ''
        template = u'<script type="text/ng-template" id="{}">{}{}{}</script>'
        return template.format(tmpl_id, new_line, tmpl_content, new_line)

    def _inject_ng_tpl(self, tmpl_content, inject_path):
        inject_source = self._read_file(inject_path)
        tmpl_content = u'\n{}'.format(tmpl_content)
        return re.sub(self.tmpl_regex, tmpl_content, inject_source, 1)

    def css(self, src_paths, output, beautify=False):
        css_series = []
        for path in src_paths:
            if os.path.isfile(path):
                if self.is_include_file(path):
                    continue
                if not output:
                    output = os.path.basename(path)
                css_series.append(self._read_file(path))
            else:
                raise CompressError('css not found')
        try:
            output_path = os.path.join(self.cwd_dir, output)
            ensure_dir(output_path, True)
        except Exception as e:
            print e
            raise CompressError('css output not found')

        if beautify:
            css_source = u'\n'.join(css_series)
        else:
            css_source = self._css(u'\n'.join(css_series))

        self._output(output_path, css_source)
        print 'peon: CSS minifed -> {}'.format(output_path)

    def js(self, src_paths, output, beautify=False):
        js_series = []
        for path in src_paths:
            if os.path.isfile(path):
                if self.is_include_file(path):
                    continue
                if not output:
                    output = os.path.basename(path)
                js_series.append(self._read_file(path))
            else:
                raise CompressError('js not found')
        try:
            output_path = os.path.join(self.cwd_dir, output)
            ensure_dir(output_path, True)
        except Exception as e:
            print e
            raise CompressError('js output not found')

        if beautify:
            js_source = u'\n'.join(js_series)
        else:
            js_source = self._js(u'\n'.join(js_series))

        self._output(output_path, js_source)
        print 'peon: JS minifed -> {}'.format(output_path)

    def html(self, src_paths):
        # html doesn't need concat files
        for path in src_paths:
            if os.path.isfile(path):
                if self.is_include_file(path):
                    continue
                html_source = self._html(self._read_file(path))
                self._output(path, html_source)
                print 'peon: HTML minifed -> {}'.format(path)
            else:
                raise CompressError('html not found')

    def process_html(self, src_paths, beautify=False):
        for path in src_paths:
            if os.path.isfile(path):
                html_source = self._process_html(path, beautify)
                self._output(path, html_source)
                print 'peon: HTML processed -> {}'.format(path)
            else:
                raise CompressError('html not found')

    def concat_angular_template(self, src_paths, output,
                                prefix='', beautify=False):
        if not output:
            output = 'index.html'

        inject_path = os.path.join(self.cwd_dir, output)
        if not os.path.isfile(inject_path):
            raise CompressError('angular templates inject path not found')

        tmpl_series = [u'<!-- Begin Templates -->']

        for path in src_paths:
            if os.path.isfile(path):
                if path == inject_path:
                    continue
                if self.is_include_file(path):
                    continue
                tmpl_id = path.replace(self.cwd_dir + os.path.sep, prefix, 1)
                tmpl_content = self._make_ng_tpl(tmpl_id,
                                                 self._read_file(path),
                                                 beautify)
                tmpl_series.append(tmpl_content)
            else:
                raise CompressError('angular templates not found')

        tmpl_series.append(u'<!-- End Templates -->')

        inject_source = self._inject_ng_tpl('\n'.join(tmpl_series),
                                            inject_path)

        self._output(inject_path, inject_source)
        print 'peon: Angular Template concated -> {}'.format(path)
