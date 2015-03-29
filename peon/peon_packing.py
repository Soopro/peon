#coding=utf-8
from __future__ import absolute_import

import os, argparse
from .utlis import makeZip, uploadFile
from .helpers import load_config, run_task
from .config import CONFIG_FILE

DEFAULT_PATH = './'
DEFAULT_ACTION = "packing"

def _get_filename(target=None):
    if isinstance(target, (str,unicode)):
        filepath = target
        filename = file.strip("/").split('/', 1)
    else:
        filepath = DEFAULT_PATH
        filename = os.getcwd().strip("/").rsplit('/', 1)

    if len(filename) > 1:
        filename = "{}.{}".format(filename[1], "zip")
    else:
        raise Exception("File path invalid")

    return filename, filepath


def upload(cfg):
    target = cfg.get("target")
    file, _ = _get_filename(target)
    
    url = cfg.get('url')
    headers = cfg.get('headers')
    data = cfg.get('data')
    params = cfg.get('params')
    file_path = os.path.join(os.getcwd(), file)
    try:
        uploadFile(file_path, url, data=data, params=params, headers=headers)
    except Exception as e:
        raise e
    print "peon: package is uploaded..."


def packzip(cfg):
    # gen file name
    target = cfg.get("target")
    filename, filepath = _get_filename(target)

    
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
    
    makeZip(filepath,
            filename,
            excludes=exclude_list,
            include_hidden=include_hidden)
    
    print "peon: files in the package ..."

  
#-------------
# main
#-------------

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
