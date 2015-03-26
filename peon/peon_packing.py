#coding=utf-8
from __future__ import absolute_import
import os, argparse
from .utlis import makeZip

DEFAULT_PATH = './'
exclude_from_zip=['sercet_key.json']

def upload(filename):
    pass


def packing(opts):
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
    
    if os.path.isfile(zip_filename):
        os.remove(zip_filename)
    
    filename = makeZip(target_path, zip_filename, exclude=exclude_from_zip)
    
    if opts.upload:
        upload(filename)
    
    print "peon: files in the package ..."


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
                        
    opts, unknown = parser.parse_known_args()
    
    packing(opts)
