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
        print('peon: shutil Error -> %s' % e)
        raise e
    # eg. source or destination doesn't exist
    except IOError as e:
        print('peon: IOError -> %s' % e.strerror)
        raise e
    # other errors
    except Exception as e:
        print('peon: Error -> %s' % e)
        raise e
 
def copy_file(src, dest):
    try:
        shutil.copy2(src, dest)
        print "peon: Copied ---> " + dest
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('peon: shutil Error -> %s' % e)
        raise e
    # eg. source or destination doesn't exist
    except IOError as e:
        print('peon: IOError -> %s' % e.strerror)
        raise e
    # other errors
    except Exception as e:
        print('peon: Error -> %s' % e)
        raise e

def remove_file(path):
    try:
        os.remove(path)
        print "peon: Removed ---> " + path
    # eg. source or destination doesn't exist
    except IOError as e:
        print('peon: IOError -> %s' % e.strerror)
        raise e
    # other errors
    except Exception as e:
        print('peon: Error -> %s' % e)
        raise e
    
def safe_path(*args):
    if len(args) == 0:
        return None
    if len(args) == 1:
        if isinstance(args[0], (str, unicode)):
            return args[0].strip(os.path.sep)
        return None
    p_list = []
    for path in args:
        if isinstance(path, (str, unicode)):
            p_list.append(path.strip(os.path.sep))
        else:
            p_list.append(None)

    return p_list

def ensure_dir(path, is_file = False):
    if is_file:
        dirname = os.path.dirname(path)
        if dirname and not os.path.isdir(dirname):
            os.makedirs(dirname)
            print('peon: Create dir -> %s' % dirname)
    
    else:
        if not os.path.isdir(path):
            os.makedirs(path)
            print('peon: Create dir -> %s' % path)

def remove_dir(path):
    try:
        dir_path = safe_path(path)
        shutil.rmtree(dir_path)
        print "peon: Removed dir -> " + dir_path
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('peon: shutil Error -> %s' % e)
        raise e
    # eg. source or destination doesn't exist
    except IOError as e:
        print('peon: IOError -> %s' % e.strerror)
        raise e
    # other errors
    except Exception as e:
        print('peon: Error -> %s' % e)
        raise e

def replace(pattern, replacement, content):
    if isinstance(pattern, (str, unicode)):
        pattern = re.escape(pattern)
    pattern = re.compile(pattern, re.IGNORECASE)
    content = re.sub(pattern, replacement, content)
    return content