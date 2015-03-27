#coding=utf-8
from __future__ import absolute_import

import os, argparse
from .utlis import makeZip, uploadFile
from .config import load_config, CONFIG_FILE

DEFAULT_PATH = './'
DEFAULT_ACTION = "packing"

def upload_zip(filename, cfg):
    url = cfg.get('url')
    headers = cfg.get('headers')
    data = cfg.get('data')
    params = cfg.get('params')
    file_path = os.path.join(os.getcwd(), filename)
    try:
        uploadFile(file_path, url, data=data, params=params, headers=headers)
    except Exception as e:
        raise e


def packing(opts):
    peon_config = load_config(DEFAULT_ACTION, False)
    
    # gen file name
    if isinstance(opts.zip, (str,unicode)):
        target_path = opts.zip
        _splist = target_path.strip("/").split('/', 1)
    else:
        target_path = DEFAULT_PATH
        _splist = os.getcwd().strip("/").rsplit('/', 1)

    if len(_splist) > 0:
        zip_filename = "{}.{}".format(_splist[1], "zip")
    else:
        raise Exception("File path invalid")
    
    # remove file if is exist
    if os.path.isfile(zip_filename):
        os.remove(zip_filename)
    
    # parse config
    include_hidden = peon_config.get("include_hidden")
    include_peon_config = peon_config.get("include_peon_config")
    exclude_list = peon_config.get("excludes")
    upload_info = peon_config.get("upload")
    if not isinstance(exclude_list, list):
        exclude_list = []

    if opts.exclude:
        exclude_list.append(opts.exclude)
    
    if not include_peon_config:
        exclude_list.append(CONFIG_FILE)
    
    filename = makeZip(target_path,
                       zip_filename,
                       excludes=exclude_list,
                       include_hidden=include_hidden)
    
    print "peon: files in the package ..."
    
    # make upload
    if upload_info:
        upload_zip(filename, upload_info)
        print "peon: package is uploaded..."
    


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
                        help='Exclude filenames from packing.')

    
    opts, unknown = parser.parse_known_args()
    
    packing(opts)
