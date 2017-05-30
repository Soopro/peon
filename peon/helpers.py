# coding=utf-8
from __future__ import absolute_import

import json
from collections import OrderedDict

from .config import CONFIG_FILE_NAME
from .utlis import BeautifyPrint as bpcolor


def load_config(command):
    try:
        with open(CONFIG_FILE_NAME) as f:
            config_data = json.load(f, object_pairs_hook=OrderedDict)
        config = config_data.get(command, {})
    except Exception as e:
        print '--------------------'
        print '{}Config error{}:'.format(bpcolor.FAIL, bpcolor.ENDC)
        raise e

    print '--------------------------------------------'
    print 'Peon: Ready to work.'
    print '--------------------------------------------'
    return config
