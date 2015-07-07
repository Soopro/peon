#coding=utf-8
from __future__ import absolute_import

import os, time, shutil, re
import htmlmin, jsmin, slimit, cssmin

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
    build_regex = re.compile('(<\!--\s*build:([\[]?\s*\w+\s*[\]]?)'+\
                             '\s+([\w\$\-\./]*)\s*-->'+\
                             '(.*?)<\!--\s*/build\s-->)',
                             re.MULTILINE | re.DOTALL | re.IGNORECASE)
                             
    attr_regex = re.compile('\[["\']?\s*([^"\']+)\s*["\']?\]', re.IGNORECASE)
    src_regex = re.compile('src=["\']?\s*([^"\']+)\s*["\']?', re.IGNORECASE)
    href_regex = re.compile('href=["\']?\s*([^"\']+)\s*["\']?', re.IGNORECASE)
    
    cwd_dir = 'build'
    dest_dir = 'dist'
    
    def __init__(self, cwd):
        self.cwd_dir = cwd
    
    def read_file(self, file_path):
        try:
            file = open(file_path)
            file_source = file.read().decode("utf-8")
            file.close()
            return file_source
        except Exception as e:
            print e
            raise CompressError('read_file')

    def write_file(self, file_path, file_source):
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
        
    
    def process_html(self, file_path):
        build_regex = self.build_regex
        src_regex = self.src_regex
        href_regex = self.href_regex
        attr_regex = self.attr_regex
        
        curr_dir = os.path.dirname(file_path)
        
        content = self.read_file(file_path)
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
                    
                    css_series.append(self.read_file(_path))
                
                self.css('\n'.join(css_series), comp_file_path)
                
                new_css_tpl = '<link rel="stylesheet" href="{}">'
                replacement = new_css_tpl.format(comp_file)
                
            elif comp_type == 'js':
                js_series = []
                for src in src_regex.findall(text):
                    if src.startswith('/'):
                        _path = os.path.join(self.cwd_dir, src[1:])
                    else:
                        _path = os.path.join(curr_dir, src)
                    js_series.append(self.read_file(_path))

                self.js('\n'.join(js_series), comp_file_path)
                
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
        
        self.write_file(file_path, content)
        print "peon: HTML processed -> {}".format(file_path)
    
    def minifed(self, dest_path, content):
        if not dest_path:
            return content
        else:
            self.write_file(dest_path, content)
            return None
    
    def css(self, source, dest_path = None):
        try:
            minifed = cssmin.cssmin(source)
        except Exception as e:
            print e
            raise CompressError('css')
        return self.minifed(dest_path, minifed)
        
    
    def js(self, source, dest_path = None):
        try:
            # minifed = jsmin.jsmin(source)
            minifed = slimit.minify(source, mangle=True, mangle_toplevel=True)
        except Exception as e:
            print e
            raise CompressError('js')
        return self.minifed(dest_path, minifed)

    
    def html(self, source, dest_path = None):
        try:
            minifed = htmlmin.minify(source)
        except Exception as e:
            print e
            raise CompressError('html')
        return self.minifed(dest_path, minifed)

    