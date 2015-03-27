#coding=utf-8
from __future__ import absolute_import

import os, sys, glob, argparse
import subprocess

from .utlis import now, gen_md5, copy_file, safe_path, ensure_dir
from .config import load_config

# variables
TEMP_FILE = '_temp_.html'
default_libs_dir = 'src/libs/'
DEFAULT_ACTION = 'release'


# main
def install(cfg):
    for c in cfg:
        if c is "bower":
            try:
                subprocess.call(["bower","update"])
                subprocess.call(["bower","install"])
            except Exception as e:
                raise e
        elif c is "npm":
            try:
                subprocess.call(["npm","update"])
                subprocess.call(["npm","install"])
            except Exception as e:
                raise e

def shell(cfg):
    for cmd in cfg:
        subprocess.call(cmd, shell=True)


def rev(cfg):
    if cfg.get('pattern'):
        pattern = str(cfg['pattern'])
        find = cfg.get('find')
        if find:
            find = str(find)
        else:
            find = pattern
        pattern=find.replace(pattern, gen_md5())
        replacements = {find:pattern}
    cwd = safe_path(cfg.get('cwd',''))
    
    files = cfg.get('src') or []
    if not isinstance(files,list):
        files = [files]
    
    path_list = []
    for file in files:
        file = safe_path(file)
        file_path = safe_path(os.path.join(cwd,file))
        _paths = glob.glob(file_path)
        for p in _paths:
            if p not in path_list:
                path_list.append(p)

    for path in path_list:
        if not os.path.isfile(path):
            print "peon: Failed -> " + path +" (not exist)"
            continue
        file = open(path)
        if os.path.isfile(TEMP_FILE):
            os.remove(TEMP_FILE)
        tmp = open(TEMP_FILE,'w')
        for line in file:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            tmp.write(line)
        tmp.close()
        file.close()
        try:
            os.rename(TEMP_FILE, path)
            print "peon: MD5ify -> " + path
        except Exception as e:
            print('Error: %s' % e)
            raise e

    if os.path.isfile(TEMP_FILE):
        os.remove(TEMP_FILE)
        
    print "peon: Work work ..."


def copy(cfg):
    for key in cfg:
        rule = cfg[key]
        dest = rule.get('dest', default_libs_dir)
        is_flatten = rule.get('flatten', False)
        force = rule.get('force', True)
        cwd = rule.get('cwd','')

        cwd, dest = safe_path(cwd, dest)
    
        files = rule.get('src') or []
        if not isinstance(files,list):
            files = [files]

        path_list = []
        for file in files:
            file = safe_path(file)
            file_path = os.path.join(cwd,file)
            _path = glob.glob(file_path)
            for p in _path:
                if p not in path_list:
                    path_list.append(p)

        for path in path_list:
            if not os.path.isfile(path):
                print "peon: Failed -> " + path +" (not exist)"
                continue
            if not is_flatten:
                _path = safe_path(path.replace(cwd,""))
                _dest = safe_path(os.path.join(dest, _path))
                ensure_dir(_dest, True)
            else:
                _dest = dest
                ensure_dir(_dest)

            if force or not os.path.isfile(_dest):
                copy_file(path, _dest)
                print "peon: Copied -> " + path
            else:
                continue
    
    print "peon: Work work ...(copy)"


def construct(opts):
    config_type = opts.construct_action or DEFAULT_ACTION

    peon_config = load_config(config_type)

    for key in peon_config:
        cmd = COMMANDS.get(key)
        if cmd:
            cmd(config[key])
    
    print "peon: finish work ..."


COMMANDS = {
    "install":install,
    "copy":copy,
    "rev":rev,
    "shell":shell
}


if __name__ == '__main__':
    # command line options
    parser = argparse.ArgumentParser(
                    description='Options of run Peon dev server.')

    parser.add_argument('--init', 
                        dest='construct_action',
                        action='store_const',
                        const='init',
                        help='Run Peon init tasks.')

    parser.add_argument('--release', 
                        dest='construct_action',
                        action='store_const',
                        const='release',
                        help='Run Peon build tasks.')

    opts, unknown = parser.parse_known_args()
    
    construct(opts)
