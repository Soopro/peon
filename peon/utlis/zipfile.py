#coding=utf-8
from __future__ import absolute_import

import os
import fnmatch
from zipfile import ZipFile ZIP_DEFLATED

TEMP_ZIP = '._tmp_zip'


def _zipdir(path, zip, excludes=None, include_hidden=False):
    exclude_list = []
    if isinstance(excludes, list):
        exclude_list = excludes

    for root, dirs, files in os.walk(path):
        if not include_hidden:
            files = [f for f in files if not f[0] == '.']
            dirs[:] = [d for d in dirs if not d[0] == '.']

        for file in files:
            is_exclude = False
            for exclude in exclude_list:
                if isinstance(exclude, (str, unicode)) \
                and fnmatch.fnmatch(file, exclude):
                    is_exclude = True

            if file != TEMP_ZIP and not is_exclude:
                zip.write(os.path.join(root, file))


def makeZip(target_path, zip_filename, excludes=None, include_hidden=False):
    print "excludes:", excludes
    zfile = ZipFile(TEMP_ZIP, 'w', ZIP_DEFLATED)
    _zipdir(target_path, zfile, excludes, include_hidden)
    zfile.close()
    os.rename(TEMP_ZIP, zip_filename)
    return zip_filename
