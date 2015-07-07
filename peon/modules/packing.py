#coding=utf-8
from __future__ import absolute_import

import os

from ..utlis import makeZip, uploadFile, safe_path
from ..config import CONFIG_FILE
from .helpers import load_config, run_task

# variables
DEFAULT_PATH = './'

# methods
def _get_filename(cwd=None):
    if isinstance(cwd, (str,unicode)):
        filename = cwd.strip("/").rsplit('/', 1)
    else:
        filename = os.getcwd().strip("/").rsplit('/', 1)

    if len(filename) >= 1:
        filename = "{}.{}".format(filename[-1], "zip")
    else:
        raise Exception("File cwd invalid")
    return filename


def upload(cfg):
    cwd = safe_path(cfg.get("cwd"))
    old_dir = os.getcwd()
    if cwd:
        os.chdir(cwd)

    file = cfg.get("file") or _get_filename(cwd)
    
    url = cfg.get('url')
    headers = cfg.get('headers')
    data = cfg.get('data')
    params = cfg.get('params')
    file_path = os.path.join(os.getcwd(), file)
    try:
        uploadFile(file_path, url, data=data, params=params, headers=headers)
    except Exception as e:
        raise e

    os.chdir(old_dir)
    print "peon: package is uploaded..."


def packzip(cfg):
    cwd = safe_path(cfg.get("cwd"))
    old_dir = os.getcwd()
    if cwd:
        os.chdir(cwd)
    # gen file name
    filename = cfg.get("file") or _get_filename(cwd)
    # remove file if is exist
    if os.path.isfile(filename):
        os.remove(filename)
    
    # parse config
    include_hidden = cfg.get("include_hidden")
    include_cfg = cfg.get("include_peon_config")
    exclude_list = cfg.get("excludes")

    if not isinstance(exclude_list, list):
        exclude_list = []
    
    if not include_cfg:
        exclude_list.append(CONFIG_FILE)
    
    makeZip(DEFAULT_PATH,
            filename,
            excludes=exclude_list,
            include_hidden=include_hidden)
    
    os.chdir(old_dir)
    print "peon: files in the package ..."

  
#-------------
# main
#-------------
DEFAULT_ACTION = "packing"

COMMANDS = {
    "zip":packzip,
    "upload":upload
}

def _ensure_cfg(config, opts):
    if not config:
        config = [{}]

    for cfg in config:
        cfg.setdefault("zip", {})
        _zipcfg = cfg.get("zip")
        _zipcfg.setdefault("excludes", [])
        if opts.exclude:
            _zipcfg["excludes"].append(opts.exclude)

    return config


def packing(opts):
    peon_config = load_config(DEFAULT_ACTION, False)
    peon_config = _ensure_cfg(peon_config, opts)

    run_task(peon_config, COMMANDS)

    print "peon: Finish packing ..."
    


if __name__ == '__main__':
    import argparse
    # command line options
    parser = argparse.ArgumentParser(
                    description='Run Peon packing zip file.')
    
    parser.add_argument('-z', '--zip', 
                        dest='zip',
                        action='store',
                        nargs='?',
                        const=None,
                        help='Run Peon packing zip file.')

    parser.add_argument('--exclude', 
                        dest='exclude',
                        action='store',
                        type=str,
                        help='Exclude filename pattern from packing.')

    
    opts, unknown = parser.parse_known_args()
    
    packing(opts)
