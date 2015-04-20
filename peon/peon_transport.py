#coding=utf-8
from __future__ import absolute_import

import argparse, os, sys, traceback, re, ast, json
import SimpleHTTPServer, SocketServer

from StringIO import StringIO
import subprocess

from .utlis import now, safe_path
from .helpers import load_config, run_task


DEFAULT_ACTION = "transport"

DEFAULT_CONTENT_TYPE = "page"
DEFAULT_SITE_FILE = 'site.json'
UPLOAD_MODE = "upload"
DOWNLOAD_MODE = "download"

def dict_to_md(data):
    meta = data.get("meta")
    content = data.get("content")

    meta_template = "{key}:{value}"
    meta = [meta_template.format(key=k.capitalize(), value=str(v)+"\n")
            for k, v in meta.iteritems()]

    meta = "".join(meta)

    file_template = "/*\n{meta}*/\n{content}"

    rv = file_template.format(meta=meta, content=content)
    return rv


def md_to_dict(md_file):
    md_pattern = r"(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)"
    md_pattern = re.compile(md_pattern)
    m = md_pattern.match(md_file)
    if not m:
        return None
    content = m.group("content").replace("\n","")
    meta = m.group("meta").split("\n")

    rv = dict()
    rv["meta"] = dict()
    for item in meta:
        if item:
            t = item.split(":")
            if len(t) == 2:
                try:
                    rv['meta'][t[0].lower()] = ast.literal_eval(t[1].strip())
                except Exception as e:
                    rv['meta'][t[0].lower()] = t[1].strip()
    rv['content'] = content
    return rv


def transport_upload(cfg):
    url = cfg.get("url")
    cwd = cfg.get("cwd")
    cwd = safe_path(cwd)
    if not os.path.isdir(cwd):
        raise Exception("Transport upload dir dose not exist.")
    payload = {
        "site_meta":{},
        "menus":{},
        "terms":{},
        "files":[]
    }
    for dirpath, dirs, files in os.walk(cwd):
        dirname = dirpath.split(cwd)[-1].strip("/")
        if not dirname:
            content_type = DEFAULT_CONTENT_TYPE
        else:
            content_type = dirname
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(cwd, dirname, file)
                f = open(file_path, "r")
                file_data = md_to_dict(f.read())
                file_data["content_type"] = content_type
                payload['files'].append(file_data)
    
    site_path = os.path.join(cwd, DEFAULT_SITE_FILE)
    if os.path.isfile(site_path):
        try:
            site_file = open(site_path)
            site_data = json.load(site_file)
            payload["site_meta"] = site_data.get("meta",{})
            payload["menus"] = site_data.get("menus",{})
            payload["terms"] = site_data.get("terms",{})
        except Exception as e:
            raise Exception("Site data error:", e)
    
    print payload
#-------------
# main
#-------------

def transport(opts):
    peon_config = load_config(DEFAULT_ACTION)

    if opts.transport == UPLOAD_MODE:
        COMMANDS = {
            "upload": transport_upload
        }
        run_task(peon_config, COMMANDS)
    elif opts.transport == DOWNLOAD_MODE:
        COMMANDS = {
            "download": transport_download,
        }
        run_task(peon_config, COMMANDS)
    else:
        raise Exception("Transport mode does not exist.")
    

if __name__ == "__main__":
    # command line options
    parser = argparse.ArgumentParser(
                    description='Options of run Peon transport.')
    
    parser.add_argument('-t', '--transport', 
                        dest='transport',
                        action='store',
                        nargs='?',
                        type=str,
                        help='Start Peon transport mode. upload or download')

    opts, unknown = parser.parse_known_args()
    
    transport(opts)