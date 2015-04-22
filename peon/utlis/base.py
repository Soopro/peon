#coding=utf-8
from __future__ import absolute_import
import os, re, time, hashlib, shutil

def now():
    return int(time.time())

def gen_md5():
    md5 = hashlib.md5(str(now())).hexdigest()
    return md5[:10]

def copy_tree(src, dest):
    try:
        shutil.copytree(src, dest)
        print "peon: Copied -> " + src
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('peon: Error -> %s' % e)
        raise e
    # eg. source or destination doesn't exist
    except IOError as e:
        print('peon: Error -> %s' % e.strerror)
        raise e

def copy_file(src, dest):
    try:
        shutil.copy2(src, dest)
        print "peon: Copied -> " + src
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
        if isinstance(args[0], (str, unicode)):
            return args[0].strip("/")
        return None
    p_list = []
    for path in args:
        if isinstance(path, (str, unicode)):
            p_list.append(path.strip("/"))
        else:
            p_list.append(None)

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
        

def replace(pattern, replacement, content):
    if isinstance(pattern, (str, unicode)):
        pattern = re.escape(pattern)
    pattern = re.compile(pattern, re.IGNORECASE)
    content = re.sub(pattern, replacement, content)
    return content