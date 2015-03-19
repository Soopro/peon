#coding=utf-8
from __future__ import absolute_import
import os, sys, shutil, time, hashlib, json, glob, argparse

# variables
CONFIG = {}
TEMP_FILE = '_temp_.html'
default_libs_dir = 'src/libs/'

# functions
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

def load_config(config_type="build"):
    global CONFIG
    peon_data = open('peon.json')
    config_data = json.load(peon_data)
    peon_data.close()
    
    CONFIG = config_data.get(config_type)
    if not CONFIG:
        raise "Invalid config file."
    print "peon: Ready to work"


def rev():
    rev_rule=CONFIG.get('rev')
    find = rev_rule.get('find')
    if rev_rule.get('pattern'):
        pattern = str(rev_rule['pattern'])
        if find:
            find = str(find)
        else:
            find = pattern
        pattern=find.replace(pattern, gen_md5())
        replacements = {find:pattern}

    cwd = safe_path(rev_rule.get('cwd',''))
    
    files = rev_rule.get('src') or []
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


def copy(force=True):
    copy_rules=CONFIG.get('copy')
    for key in copy_rules:
        rule = copy_rules[key]
        dest = rule.get('dest', default_libs_dir)
        is_flatten = rule.get('flatten', False)
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
    
    print "peon: Work work ..."


def construct(opts):
    config_type = 'build'
    if opts.init:
        config_type = 'init'

    load_config(config_type)
        
    if CONFIG.get('copy'):
        copy()
        
    if CONFIG.get('rev'):
        rev()
    
    print "peon: No more work ..."


if __name__ == '__main__':
    # command line options
    parser = argparse.ArgumentParser(
                    description='Options of run Peon dev server.')

    parser.add_argument('--init', 
                        dest='init',
                        action='store_const',
                        const=True,
                        help='Run Peon init tasks.')

    parser.add_argument('--build', 
                        dest='build',
                        action='store_const',
                        const=True,
                        help='Run Peon build tasks.')

    opts, unknown = parser.parse_known_args()
    
    construct(opts)
