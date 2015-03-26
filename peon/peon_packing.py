#coding=utf-8
from __future__ import absolute_import
import os

from zipfile import ZipFile
import subprocess


def zipdir(path, zip):
    if not isinstance(zip, ZipFile):
        return None
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.startswith('.'):
                print os.path.join(root, file)
                zip.write(os.path.join(root, file))


def packing():
    _path_list = os.getcwd().strip("/").rsplit('/', 1)
    if len(_path_list) > 0:
        zip_filename = "{}.{}".format(_path_list[1], "zip")
    else:
        raise Exception("File path invalid")

    if os.path.isfile(zip_filename):
        os.remove(zip_filename)
    zfile = ZipFile(zip_filename, 'w')
    zipdir('./', zfile)
    zfile.close()
    
    print "peon: files in the package ..."


if __name__ == '__main__':
    packing()
