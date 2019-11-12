# coding=utf-8


import os
import time

from ..utlis import makeZip, uploadFile, safe_paths
from ..helpers import load_config


# variables
DEFAULT_PATH = '.'


def _get_filename(cwd=None):
    if isinstance(cwd, str):
        filename = cwd.strip(os.path.sep).rsplit(os.path.sep, 1)
    else:
        filename = os.getcwd().strip(os.path.sep).rsplit(os.path.sep, 1)

    if len(filename) >= 1:
        filename = '{}.{}'.format(filename[-1], 'zip')
    else:
        raise Exception('File cwd invalid')
    return filename


# methods
def upload(cfg):
    cwd = safe_paths(cfg.get('cwd'))

    file = cfg.get('file') or _get_filename(cwd)

    url = cfg.get('url')
    headers = cfg.get('headers')
    data = cfg.get('data')
    params = cfg.get('params')
    delete = cfg.get('delete')
    file_path = os.path.join(os.getcwd(), cwd, file)
    os.path.normpath(file_path)
    start_time = time.time()
    try:
        uploadFile(file_path, url, data=data, params=params, headers=headers)
    except Exception as e:
        raise e

    if delete:
        os.remove(file_path)

    print('peon: package is uploaded...', time.time() - start_time)


def packzip(cfg):
    cwd = safe_paths(cfg.get('cwd'))
    dest = safe_paths(cfg.get('dest'))
    start_dir = os.getcwd()
    if cwd:
        os.chdir(cwd)
    # gen file name
    filename = cfg.get('file') or _get_filename(cwd)
    # remove file if is exist
    if os.path.isfile(filename):
        os.remove(filename)

    # parse config
    include_hidden = cfg.get('include_hidden')
    exclude_list = cfg.get('excludes')

    if not isinstance(exclude_list, list):
        exclude_list = []

    makeZip(DEFAULT_PATH,
            filename,
            excludes=exclude_list,
            include_hidden=include_hidden)

    if dest:
        abs_file_path = os.path.join(start_dir, dest, filename)
        abs_file_path = os.path.normpath(abs_file_path)
        if os.path.exists(abs_file_path):
            os.remove(abs_file_path)
        os.rename(filename, abs_file_path)

    os.chdir(start_dir)
    print('peon: files in the package ...')


# -------------
# main
# -------------
def packing(config_path=None):
    cmd_cfg = load_config('packing', config_path)

    zip_cfg = cmd_cfg.get('zip')
    upload_cfg = cmd_cfg.get('upload')

    if zip_cfg:
        packzip(zip_cfg)
    if upload_cfg:
        upload(upload_cfg)

    print('peon: Finish packing ...')
