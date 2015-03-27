#coding=utf-8
from __future__ import absolute_import
import os, json
from collections import OrderedDict

CONFIG_FILE = 'peon.json'

def load_config(config_type, force=True):
    config = {}
    if os.path.isfile(CONFIG_FILE):
        try:
            config_file = open(CONFIG_FILE)
            config_data = json.load(config_file,
                                    object_pairs_hook=OrderedDict)
            config_file.close()
            config = config_data.get(config_type,{})
        except Exception as e:
            if force:
                raise Exception("Config error:", e)
            print "Config error: ", e
            
    if force and not config:
        raise Exception("Config error: Nothing loaded!")
        
    print "peon: Ready to work."
    
    return config