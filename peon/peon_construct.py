#coding=utf-8
from __future__ import absolute_import
import os, sys, shutil, time, hashlib, json, glob, argparse
from collections import OrderedDict
from zipfile import ZipFile
import subprocess

# variables
TEMP_FILE = '_temp_.html'
default_libs_dir = 'src/libs/'
DEFAULT_ACTION = 'release'


# helpers
def now():
    return int(time.time())

def gen_md5():
    md5 = hashlib.md5(str(now())).hexdigest()
    return md5[:10]

def copy_file(src, dest):
    try:
        shutil.copy2(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('peon: Error -> %s' % e)
        raise e
    # eg. source or destination doesn't exist
    except IOError as e:
        print('peon: Error -> %s' % e.strerror)
        raise e
        
def safe_path(*args):
    if len(args) == 0:
        return None
    if len(args) == 1:
        return args[0].strip("/")
    p_list = []
    for path in args:
        p_list.append(path.strip("/"))

    return p_list

def ensure_dir(path, isFile=False):
    if not os.path.exists(os.path.dirname(path)):
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname)
            print('peon: Create dir -> %s' % dirname)
    
    if not os.path.isdir(path) and not isFile:
        os.makedirs(path)
        print('peon: Create dir -> %s' % path)

# main

def load_config(config_type=DEFAULT_ACTION):
    peon_data = open('peon.json')
    config_data = json.load(peon_data,
                            object_pairs_hook=OrderedDict)
    peon_data.close()
    
    config = config_data.get(config_type)
    if not config:
        raise Exception("Invalid config file.")
    else:
        print "peon: Ready to work"

    return config


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

    config = load_config(config_type)

    for key in config:
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
