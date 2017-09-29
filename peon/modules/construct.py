# coding=utf-8
from __future__ import absolute_import

import os
import re
import glob
import fnmatch

from ..core import RenderHandler, MinifyHandler
from ..utlis import (gen_md5, copy_file, safe_paths, grounded_paths,
                     child_of_path, ensure_dir, remove_dir, remove_file)
from ..helpers import load_config


# variables
TEMP_FILE = '_construct_temp_.tmp'
DEFAULT_SRC_DIR = 'src'
DEFAULT_BUILD_DIR = 'build'
DEFAULT_DIST_DIR = 'dist'
nested_regex = re.compile(r'[\*/]*\*\*/([\*]*.*)$', re.IGNORECASE)


# helpers
def _nested_files(nested, pattern, cwd_pattern):
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

    print 'peon: Nested files -> {}/ [{}][{}]'.format(nested_path,
                                                      nested_suffix,
                                                      nested_level)
    return paths


def _find_path_list(src, cwd):
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
            paths = _nested_files(nested, file, file_path_pattern)
        else:
            paths = glob.glob(file_path_pattern)

        for path in paths:
            if not os.path.exists(path):
                print 'peon: Failed -> ' + path + ' (not exist)'
                continue
            if path not in path_list:
                path_list.append(path)

    for file in src:
        if not file.startswith('!'):
            continue
        file = safe_paths(file[1:])
        file_path_pattern = os.path.join(cwd, file)
        nested = nested_regex.search(file_path_pattern)
        if nested:
            paths = _nested_files(nested, file, file_path_pattern)
        else:
            paths = glob.glob(file_path_pattern)

        for path in paths:
            if path in path_list:
                path_list.remove(path)

    return [path for path in path_list if grounded_paths(cwd, path)]


# methods
def copy(rules):
    for rule in rules:
        is_flatten = rule.get('flatten', False)
        overwrite = rule.get('overwrite', True)
        cwd, dest = safe_paths(rule.get('cwd', ''), rule.get('dest', ''))

        files = rule.get('src', [])
        path_list = _find_path_list(files, cwd)
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

            if overwrite or not os.path.isfile(dest_path):
                copy_file(path, dest_path)
            else:
                continue
    print 'peon: Work work ...(copy)'


def rev(cfg):
    try:
        find_str = cfg.get('find')
    except Exception:
        find_str = '?md5=<rev>'

    if isinstance(find_str, unicode):
        find_str = find_str.encode('utf-8')
    rev_str = find_str.replace('<rev>', gen_md5())

    cwd = safe_paths(cfg.get('cwd', DEFAULT_DIST_DIR))
    files = cfg.get('src', [])
    path_list = _find_path_list(files, cwd)

    for path in path_list:
        file = open(path)
        if os.path.isfile(TEMP_FILE):
            os.remove(TEMP_FILE)
        with open(TEMP_FILE, 'w') as tmp:
            for line in file:
                try:
                    line = line.replace(find_str, rev_str)
                except Exception as e:
                    print '---------->'
                    print 'line:', line,
                    print 'find:', find_str
                    print 'rev:', rev_str
                    raise e
                tmp.write(line)

        file.close()
        if os.path.isfile(path):
            os.remove(path)
        os.rename(TEMP_FILE, path)
        print 'peon: MD5ify -> ' + path

    if os.path.isfile(TEMP_FILE):
        os.remove(TEMP_FILE)

    print 'peon: Work work ...(rev)'


def render(cfg):
    src_dir = cfg.get('cwd', DEFAULT_SRC_DIR)
    dest_dir = cfg.get('dest', DEFAULT_BUILD_DIR)
    render_aliases = cfg.get('render_aliases', [])
    skip_includes = cfg.get('skip_includes', [])
    render = RenderHandler(src_dir, dest_dir,
                           aliases=render_aliases,
                           skips=skip_includes)
    if cfg.get('clean', True):
        render.clean()
    render.render_all()
    print 'peon: Work work ...(render)'


def replace(cfg):
    files = cfg.get('src', [])
    cwd = safe_paths(cfg.get('cwd', DEFAULT_DIST_DIR))
    replacing = cfg.get('replacing', [])
    path_list = _find_path_list(files, cwd)
    for path in path_list:
        file = open(path)
        if os.path.isfile(TEMP_FILE):
            os.remove(TEMP_FILE)
        tmp = open(TEMP_FILE, 'w')
        for line in file:
            for _rule in replacing:
                pattern = _rule.get('from')
                replace = _rule.get('to')
                if pattern is None or replace is None:
                    print 'peon: Failed -> replace is no pattern'
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
        print 'peon: Replaced --> ' + path

    if os.path.isfile(TEMP_FILE):
        os.remove(TEMP_FILE)

    print 'peon: Work work ...(replace)'


def clean(paths):
    path_list = _find_path_list(paths, '')
    for path in path_list:
        if child_of_path(path, DEFAULT_SRC_DIR):
            error = 'peon: Error -> Path [{}] is protected ...(clean)'
            raise Exception(error.format(path))
            continue
        if os.path.isdir(path):
            remove_dir(path)
    print 'peon: Work work ...(clean)'


def scrap(cfg):
    cwd = safe_paths(cfg.get('cwd', DEFAULT_DIST_DIR))
    files = cfg.get('src', [])
    path_list = _find_path_list(files, cwd)
    for path in path_list:
        if child_of_path(path, DEFAULT_SRC_DIR):
            error = 'peon: Path [{}] is protected ...(scrap)'
            print error.format(path)
            continue
        if os.path.isdir(path):
            remove_dir(path)
        elif os.path.isfile(path):
            remove_file(path)
    print 'peon: Work work ...(scrap)'


def compress(rules):
    for rule in rules:
        cwd = safe_paths(rule.get('cwd', DEFAULT_DIST_DIR))
        minify_includes = rule.get('minify_includes', False)
        minify = MinifyHandler(cwd, minify_includes)
        files = rule.get('src', [])
        minify_type = rule.get('type')
        minify_output = safe_paths(rule.get('output'))
        minify_beautify = rule.get('beautify', False)

        path_list = _find_path_list(files, cwd)

        if minify_type == 'html':
            minify.html(path_list)
        elif minify_type == 'css':
            minify.css(path_list, minify_output, minify_beautify)
        elif minify_type == 'js':
            minify.js(path_list, minify_output, minify_beautify)
        elif minify_type == 'process_html':
            process_minify = rule.get('minify', True)
            minify.process_html(path_list, process_minify, minify_beautify)
        elif minify_type == 'inline_angular_templates':
            minify.concat_angular_template(path_list,
                                           minify_output,
                                           rule.get('prefix', ''),
                                           minify_beautify)

    print 'peon: Work work ...(compress)'


# -------------
# main
# -------------
alias = ('construct', 'release', 'init', 'build')
COMMANDS = {
    'clean': clean,
    'copy': copy,
    'render': render,
    'compress': compress,
    'replace': replace,
    'scrap': scrap,
    'rev': rev,
}


def construct(opts):
    """
    Construct actions: `construct` as default, `init`, `build`, `release`
    """
    if opts.construct not in alias:
        opts.construct = 'construct'

    cmd_cfg = load_config(opts.construct)
    if not isinstance(cmd_cfg, list):
        cmd_cfg = [cmd_cfg]

    for task in cmd_cfg:
        for k, v in task.iteritems():
            cmd = COMMANDS.get(k)
            if cmd:
                cmd(v)

    print 'peon: finish construct ...'
