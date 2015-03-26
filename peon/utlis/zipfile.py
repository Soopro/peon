#coding=utf-8
from __future__ import absolute_import
import os

from zipfile import ZipFile, ZIP_DEFLATED


TEMP_ZIP = '._tmp_zip'

def zipdir(path, zip):
    if not isinstance(zip, ZipFile):
        return None
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.startswith('.') and file != TEMP_ZIP:
                zip.write(os.path.join(root, file))


def makeZip(target_path, zip_filename):
    zfile = ZipFile(TEMP_ZIP, 'w', ZIP_DEFLATED)
    zipdir(target_path, zfile)
    zfile.close()
    os.rename(TEMP_ZIP, zip_filename)
    return True