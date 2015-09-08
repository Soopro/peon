#coding=utf-8
from __future__ import absolute_import

import os, sys, re, glob, fnmatch
import subprocess

from ..services import RenderHandler, MinifyHandler
from ..utlis import (now, gen_md5, copy_file, safe_paths, grounded_paths,
                     child_of_path, ensure_dir, remove_dir, remove_file)
from .helpers import load_config, run_task


# variables
TEMP_FILE = '_construct_temp_.tmp'
DEFAULT_SRC_DIR = 'src'
DEFAULT_BUILD_DIR = 'build'
DEFAULT_DIST_DIR = 'dist'
nested_regex = re.compile('[\*/]*\*\*/([\*]*.*)$', re.IGNORECASE)

# helpers
def help_find_nested_files(nested, pattern, cwd_pattern):
    nested_path = cwd_pattern.replace(nested.group(0), '').strip() or '.'
    nested_suffix = nested.group(1)
    nested_level = len(pattern.split(os.path.sep))
    paths = []
    for dirpath, dirnames, files in os.walk(nested_path):
        for f in fnmatch.filter(files, nested_suffix):
            f_path = os.path.join(dirpath, f)
            f_level = len(f_path.split(os.path.sep))
            # nested pattern '**/*' has 2 level,
            # f_path alwasy '<cwd>/file_path' even cwd is '.',
            # so f_level always 1+ than nested_level,
            # that's why the '**/*' can match parent level files.
            # and should do that right.
            if f_level >= nested_level:
                paths.append(f_path)

    print "peon: Nested files -> {}/ [{}][{}]".format(nested_path,
                                                      nested_suffix,
                                                      nested_level)
    return paths


def helper_find_path_list(src, cwd):
    if not isinstance(src, list):
        src = [src]
    
    cwd = safe_paths(cwd)
    path_list = []
    
    for file in src:
        if file.startswith('!'):
            continue
        file = safe_paths(file)
        file_path_pattern = os.path.join(cwd, file)
        nested = nested_regex.search(file_path_pattern)
        if nested:
            paths = help_find_nested_files(nested, file, file_path_pattern)
        else:
            paths = glob.glob(file_path_pattern)

        for path in paths:
            if not os.path.exists(path):
                print "peon: Failed -> " + path + " (not exist)"
                continue
            if not path in path_list:
                path_list.append(path)
                
    for file in src:
        if not file.startswith('!'):
            continue
        file = safe_paths(file[1:])
        file_path_pattern = os.path.join(cwd, file)
        nested = nested_regex.search(file_path_pattern)
        if nested:
            paths = help_find_nested_files(nested, file, file_path_pattern)
        else:
            paths = glob.glob(file_path_pattern)
        
        for path in paths:
            if path in path_list:
                path_list.remove(path)
    
    return [path for path in path_list if grounded_paths(cwd, path)]

# methods
def install(cfg):
    for c in cfg:
        if c == "bower":
            try:
                print "Bower installing......"
                subprocess.call(["bower", "update"])
                subprocess.call(["bower", "install"])
            except Exception as e:
                raise e

        elif c == "npm":
            try:
                print "Npm installing......"
                subprocess.call(["npm", "update"])
                subprocess.call(["npm", "install"])
            except Exception as e:
                raise e


def shell(cfg):
    for cmd in cfg:
        subprocess.call(cmd, shell=True)

def replace(cfg):
    files = cfg.get('src', [])
    cwd = safe_paths(cfg.get('cwd', ''))
    replacements = cfg.get('replacements', [])
    path_list = helper_find_path_list(files, cwd)
    for path in path_list:
        file = open(path)
        if os.path.isfile(TEMP_FILE):
            os.remove(TEMP_FILE)
        tmp = open(TEMP_FILE, 'w')
        for line in file:
            for replace_rule in replacements:
                pattern = replace_rule.get('pattern')
                replace = replace_rule.get('replace')
                if pattern is None or replace is None:
                    print "peon: Failed -> replace (no pattern)"
                    continue
                if isinstance(pattern, unicode):
                    pattern = pattern.encode('utf-8')
                if isinstance(replace, unicode):
                    replace = replace.encode('utf-8')
                line = line.replace(pattern, replace)
            tmp.write(line)
        tmp.close()
        file.close()
        if os.path.isfile(path):
            os.remove(path)
        os.rename(TEMP_FILE, path)
        print "peon: Replaced --> " + path
    
    if os.path.isfile(TEMP_FILE):
        os.remove(TEMP_FILE)
        
    print "peon: Work work ...(replace)"
    
    
    
def rev(cfg):
    if not cfg.get('pattern'):
        print "peon: Failed -> rev (no pattern)"
        return
    pattern = str(cfg['pattern'])
    find = cfg.get('find')
    if find:
        find = str(find)
    else:
        find = pattern
    pattern = find.replace(pattern, gen_md5())
    replacements = {find: pattern}
    cwd = safe_paths(cfg.get('cwd',''))
    files = cfg.get('src', [])
    path_list = helper_find_path_list(files, cwd)

    for path in path_list:
        file = open(path)
        if os.path.isfile(TEMP_FILE):
            os.remove(TEMP_FILE)
        tmp = open(TEMP_FILE, 'w')
        for line in file:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            tmp.write(line)
        tmp.close()
        file.close()
        if os.path.isfile(path):
            os.remove(path)
        os.rename(TEMP_FILE, path)
        print "peon: MD5ify -> " + path

    if os.path.isfile(TEMP_FILE):
        os.remove(TEMP_FILE)
        
    print "peon: Work work ...(rev)"


def copy(cfg):
    for key in cfg:
        rule = cfg[key]
        is_flatten = rule.get('flatten', False)
        force = rule.get('force', True)
        cwd, dest = safe_paths(rule.get('cwd', ''),
                              rule.get('dest', ''))
        
        files = rule.get('src', [])
        path_list = helper_find_path_list(files, cwd)
        ensure_dir(dest)
        
        for path in path_list:
            if is_flatten:
                dest_path = dest
                ensure_dir(dest_path)
            else:
                _cwd = os.path.join(cwd, '')
                _path = safe_paths(path.replace(_cwd, '', 1))
                dest_path = safe_paths(os.path.join(dest, _path))
                ensure_dir(dest_path, True)

            if os.path.isdir(path):
                ensure_dir(dest_path)
                continue
            
            if force or not os.path.isfile(dest_path):
                copy_file(path, dest_path)
            else:
                continue
    
    print "peon: Work work ...(copy)"


def render(cfg):
    render_opts = {
        "src": cfg.get('cwd', DEFAULT_SRC_DIR),
        "dest": cfg.get('dest', DEFAULT_BUILD_DIR),
        "skip_includes": cfg.get('skip_includes', []),
    }
    render = RenderHandler(render_opts)
    if cfg.get('clean') is True:
        render.clean()
    render.render_all()
    print "peon: Work work ...(render)"


def clean(paths):
    path_list = helper_find_path_list(paths, '')
    for path in path_list:
        if child_of_path(path, DEFAULT_SRC_DIR):
            error = "peon: Error -> Path [{}] is protected ...(clean)"
            raise Exception(error.format(path))
            continue
        if os.path.isdir(path):
            remove_dir(path)
    print "peon: Work work ...(clean)"


def scrap(cfg):
    cwd = safe_paths(cfg.get('cwd', DEFAULT_DIST_DIR))
    files = cfg.get('src', [])
    path_list = helper_find_path_list(files, cwd)
    for path in path_list:
        if child_of_path(path, DEFAULT_SRC_DIR):
            error = "peon: Path [{}] is protected ...(scrap)"
            print error.format(path)
            continue
        if os.path.isdir(path):
            remove_dir(path)
        elif os.path.isfile(path):
            remove_file(path)
    print "peon: Work work ...(scrap)"


def compress(cfg):
    for key in cfg:
        rule = cfg[key]
        cwd = safe_paths(rule.get('cwd', DEFAULT_DIST_DIR))
        allow_includes = rule.get('allow_includes', False)
        minify = MinifyHandler(cwd, allow_includes)
        files = rule.get('src', [])
        minify_type = rule.get('type')
        minify_output = safe_paths(rule.get('output'))
        # safe_paths('') will generate '.' which I don't want here.
        
        minify_process = rule.get('minify', True)
        minify_prefix = rule.get('prefix', '') 
        minify_beautify = rule.get('beautify', False)
        
        path_list = helper_find_path_list(files, cwd)

        if minify_type == 'html':
            minify.html(path_list)
        elif minify_type == 'css':
            minify.css(path_list, minify_output)
        elif minify_type == 'js':
            minify.js(path_list, minify_output)
        elif minify_type == 'process_html':
            minify.process_html(path_list, minify_process)
        elif minify_type == 'inline_angular_templates':
            minify.concat_angular_template(path_list,
                                           minify_output,
                                           minify_prefix,
                                           minify_beautify)
    
    print "peon: Work work ...(compress)"


#-------------
# main
#-------------
DEFAULT_ACTION = 'release'
ALLOWED_ACTION_TYPES = ['construct', 'release', 'init', 'build']

COMMANDS = {
    "install": install,
    "copy": copy,
    "clean": clean,
    "scrap": scrap,
    "replace": replace,
    "render": render,
    "compress": compress,
    "rev": rev,
    "shell": shell
}

def construct(opts):
    config_type = opts.construct or DEFAULT_ACTION
    peon_config = load_config(config_type)

    run_task(peon_config, COMMANDS)
    
    print "peon: finish construct ..."



if __name__ == '__main__':
    import argparse
    # command line options
    parser = argparse.ArgumentParser(
                    description='Options of run Peon dev server.')
                        
    parser.add_argument('-c', '--construct', 
                        dest='construct',
                        action='store',
                        nargs='?',
                        type=str,
                        const='release',
                        help='Run Peon construct to build files.')

    opts, unknown = parser.parse_known_args()
    
    construct(opts)
