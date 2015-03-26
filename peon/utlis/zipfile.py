#coding=utf-8
from __future__ import absolute_import
import os

from zipfile import ZipFile, ZIP_DEFLATED


TEMP_ZIP = '._tmp_zip'

def zipdir(path, zip, exclude=None, include_hidden=False):
    exclude_list =parse_exclude(exclude)
    
    if not isinstance(zip, ZipFile):
        return None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file in exclude_list:
                continue

            if not include_hidden and file.startswith('.'):
                continue
                
            if file != TEMP_ZIP:
                zip.write(os.path.join(root, file))


def parse_exclude(exclude=None):
    exclude_list = []
    if exclude is None:
        return exclude_list
    elif isinstance(exclude, (str, unicode)):
        exclude_list.append(exclude)
        return exclude_list
    elif isinstance(exclude, list):
        for item in exclude:
            if isinstance(item, (str, unicode)):
                exclude_list.append(item)
        return exclude_list
    else:
        raise Exception("Exclude is invalid")


def makeZip(target_path, zip_filename, exclude=None, include_hidden=False):
    zfile = ZipFile(TEMP_ZIP, 'w', ZIP_DEFLATED)
    zipdir(target_path, zfile, exclude, include_hidden)
    zfile.close()
    os.rename(TEMP_ZIP, zip_filename)
    return zip_filename