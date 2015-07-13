#coding=utf-8
from __future__ import absolute_import
import os, json
from collections import OrderedDict

from ..config import CONFIG_FILE
from ..utlis import BeautifyPrint as bpcolor

def load_config(config_type, force=True, multiple=True):
    config = {}
    if os.path.isfile(CONFIG_FILE):
        try:
            config_file = open(CONFIG_FILE)
            config_data = json.load(config_file,
                                    object_pairs_hook=OrderedDict)
            config_file.close()
            config = config_data.get(config_type, {})
        except Exception as e:
            print "--------------------"
            print "{}Config error{}:".format(bpcolor.FAIL, bpcolor.ENDC)
            raise e
            
    if force and not config:
        print "--------------------"
        print "{}Config is required{}:".format(bpcolor.FAIL, bpcolor.ENDC)
        raise Exception("Nothing loaded!")
    
    if multiple and not isinstance(config, list):
       config = [config]
    
    print "--------------------------------------------"
    print "peon: Ready to work."
    print "--------------------------------------------"
    return config


def run_task(config, commands):
    for task in config:
        for k, v in task.iteritems():
            cmd = commands.get(k)
            if cmd:
                cmd(v)