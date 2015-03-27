#coding=utf-8
from __future__ import absolute_import
import os, time, hashlib, shutil

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