#coding=utf-8
from __future__ import absolute_import

import os, time, shutil, re
import htmlmin, slimit, cssmin

from ..utlis import BeautifyPrint as bpcolor

# exception
class CompressError(Exception):
    status_msg = 'CompressError'
    affix_msg = None
    
    def __init__(self, message=None):
        self.affix_msg = message

    def __str__(self):
        return '{}:{}'.format(self.status_msg,
                              bpcolor.OKBLUE+self.affix_msg+bpcolor.ENDC)

# handlers
class MinifyHandler(object):
    temp_file = '_minify_temp_.tmp'

    tmpl_regex = re.compile('(<\!--\s*ng\-templates\s*-->)',
                             re.MULTILINE | re.DOTALL | re.IGNORECASE)

    build_regex = re.compile('(<\!--\s*build:([\[]?\s*\w+\s*[\]]?)'+\
                             '\s*+([\w\$\-\./]*)\s*-->'+\
                             '(.*?)<\!--\s*/build\s*-->)',
                             re.MULTILINE | re.DOTALL | re.IGNORECASE)
                             
    attr_regex = re.compile('\[["\']?\s*([^"\']+)\s*["\']?\]', re.IGNORECASE)
    src_regex = re.compile('src=["\']?\s*([^"\']+)\s*["\']?', re.IGNORECASE)
    href_regex = re.compile('href=["\']?\s*([^"\']+)\s*["\']?', re.IGNORECASE)
    
    cwd_dir = 'build'
    dest_dir = 'dist'
    
    def __init__(self, cwd):
        self.cwd_dir = cwd
    
    def _read_file(self, file_path):
        try:
            file = open(file_path)
            file_source = file.read().decode("utf-8")
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
            tmp.write(file_source.encode("utf-8"))
            tmp.close()
        except Exception as e:
            print e
            raise CompressError('process_html:write')
        if os.path.isfile(file_path):
            os.remove(file_path)
        os.rename(self.temp_file, file_path)
        print "peon: Minify writed ---> {}".format(file_path) 
        return file_path
        
    
    def _process_html(self, file_path):
        print "peon: Minify HTML process start"
        
        build_regex = self.build_regex
        src_regex = self.src_regex
        href_regex = self.href_regex
        attr_regex = self.attr_regex
        
        curr_dir = os.path.dirname(file_path)
        
        content = self._read_file(file_path)
        for match, comp_type, comp_file, text in build_regex.findall(content):
            if not comp_file or not comp_type:
                content = content.replace(match, '')
                continue
            
            comp_file_args = ''
            comp_file_split = comp_file.rsplit('?', 1)
            if len(comp_file_split) > 1:
                comp_file_args = '?'+comp_file_split[1]
            
            if comp_file.startswith('/'):
                comp_file_path = os.path.join(self.dest_dir, comp_file[1:])
            else:
                comp_file_path = os.path.join(curr_dir, comp_file)

            if comp_type == 'css':
                css_series = []
                for href in href_regex.findall(text):
                    if href.startswith('/'):
                        _path = os.path.join(self.cwd_dir, href[1:])
                    else:
                        _path = os.path.join(curr_dir, href)
                    
                    css_series.append(self._read_file(_path))
                
                css_source = self._css('\n'.join(css_series))
                self._output(css_source, comp_file_path)
                
                new_css_tpl = '<link rel="stylesheet" href="{}">'
                replacement = new_css_tpl.format(comp_file)
                
            elif comp_type == 'js':
                js_series = []
                for src in src_regex.findall(text):
                    if src.startswith('/'):
                        _path = os.path.join(self.cwd_dir, src[1:])
                    else:
                        _path = os.path.join(curr_dir, src)
                    js_path_list.append(_path)

                self.js(js_path_list, comp_file_path)
                new_css_tpl = '<script src="{}"></script>'
                replacement = new_css_tpl.format(comp_file)
                
            else:
                attr_name = attr_regex.search(comp_type).group(1)
                if not attr_name:
                    continue
                pattern = r'({}=["\']?\s*([^"\']+)\s*["\']?)'.format(attr_name)
                comp_attr_regex = re.compile(pattern, re.IGNORECASE)
                replacement = text
                for attr_match, attr in comp_attr_regex.findall(text):
                    if attr.startswith('/'):
                        _src_path = os.path.join(self.cwd_dir, attr[1:])
                    else:
                        _src_path = os.path.join(curr_dir, attr)
                    if _src_path != comp_file_path:
                        shutil.copy2(_src_path, comp_file_path)
                    new_attr = '{}="{}"'.format(attr_name, comp_file)
                    replacement = replacement.replace(attr_match, new_attr)

            if not replacement:
                continue
            content = content.replace(match, replacement)
            print "peon: processe_html {}".format(comp_type)
            print "--------------------"
            print text
            print "--->"
            print replacement
            print "--------------------"
        
        return content
    
    def _output(self, content, dest_path):
        self._write_file(dest_path, content)
        return dest_path
    
    def _css(self, source):
        try:
            minifed = cssmin.cssmin(source)
        except Exception as e:
            print e
            raise CompressError('css')
        return minifed
    
    def _js(self, source):
        try:
            # minifed = jsmin.jsmin(source)
            minifed = slimit.minify(source, mangle=True, mangle_toplevel=True)
        except Exception as e:
            print e
            raise CompressError('js')
        return self.minifed(dest_path, minifed)
    
    def _html(self, source):
        try:
            minifed = htmlmin.minify(source)
        except Exception as e:
            print e
            raise CompressError('html')
        return minifed
    
    def _make_ng_tpl(self, tmpl_id, tmpl_content):
        template = '<script type="text/ng-template" id="{}">{}</script>'
        return template.format(tmpl_id, tmpl_content)
    
    def _inject_ng_tpl(self, tmpl_series, inject_path):
        inject_source = self._read_file(inject_path)
        inject_source.replace(self.tmpl_regex, '\n'.join(tmpl_series), 1)
        return inject_source
    
    def css(self, src_paths, output_path):
        css_series = []
        for path in src_paths:
            if os.path.isfile(path):
                css_series.append(self._read_file(path))
            else:
                raise CompressError('css not found')
        css_source = self._css('\n'.join(css_series))
        output_path = os.path.join(self.cwd_dir, output_path)
        self._output(css_source, output_path)
        print "peon: CSS minifed -> {}".format(output_path)

    def js(self, src_paths, output_path):
        js_series = []
        for path in src_paths:
            if os.path.isfile(path):
                js_series.append(self._read_file(path))
            else:
                raise CompressError('js not found')
        js_source = self._css('\n'.join(js_series))
        output_path = os.path.join(self.cwd_dir, output_path)
        self._output(js_source, outpu_path)
        print "peon: JS minifed -> {}".format(output_path)
        
    def html(self, src_paths):
        # html doesn't need concat files
        for path in src_paths:
            if os.path.isfile(path):
                html_source = self._html(self._read_file(path))
                self._output(html_source, path)
                print "peon: HTML minifed -> {}".format(path)
            else:
                raise CompressError('html not found')

    def process_html(self, src_paths):
        for path in src_paths:
            if os.path.isfile(path)
                html_source = _process_html(path)
                self._output(html_source, path)
                print "peon: HTML processed -> {}".format(path)
            else:
                raise CompressError('html not found')
    
    def concat_angular_template(self, src_paths, inject_path, prefix=''):
        tmpl_series = ["<!-- Begin Templates -->"]
        for path in src_paths:
            if os.path.isfile(path)
                tmpl_id = path.replace(self.cwd_dir+'/', prefix, 1)
                tmpl_content = _make_ng_tpl(tmpl_id, self._read_file(path))
                tmpl_series.append(tmpl_content)
            else:
                raise CompressError('angular template not found')
        tmpl_series.append("<!-- End Templates -->")
        inject_path = os.path.join(self.cwd_dir, inject_path)
        inject_source = _inject_ng_tpl(tmpl_series, inject_path)
        self._output(inject_source, inject_path)
        print "peon: Angular Template concated -> {}".format(path)