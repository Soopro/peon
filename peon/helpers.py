# coding=utf-8


import json
from collections import OrderedDict

from .config import DEFAULT_CONFIG_PATH
from .utlis import BeautifyPrint as bpcolor


def load_config(command, config_path=None):
    if not config_path:
        config_path = DEFAULT_CONFIG_PATH
    try:
        with open(config_path) as f:
            config_data = json.load(f, object_pairs_hook=OrderedDict)
        config = config_data.get(command, {})
    except Exception as e:
        print('--------------------')
        print('{}Config error{}:'.format(bpcolor.FAIL, bpcolor.ENDC))
        raise e

    print('--------------------------------------------')
    print('Peon: Ready to work.')
    print('--------------------------------------------')
    return config
