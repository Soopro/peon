#coding=utf-8
from __future__ import absolute_import

import argparse, os, sys, traceback, re, yaml, json
import SimpleHTTPServer, SocketServer

from StringIO import StringIO
import subprocess

from .utlis import now, safe_path, uploadData, getData, replace
from .helpers import load_config, run_task


DEFAULT_ACTION = "transport"

DEFAULT_CONTENT_DIR = "content"
DEFAULT_CONTENT_TYPE = "page"
DEFAULT_SITE_FILE = 'site.json'
UPLOAD_MODE = "upload"
DOWNLOAD_MODE = "download"


def convert_data(x):
    if isinstance(x, dict):
        return dict((k.lower(), convert_data(v)) 
                     for k, v in x.iteritems())
    elif isinstance(x, list):
        return list([convert_data(i) for i in x])
    elif isinstance(x, str):
        return x.decode("utf-8")
    elif isinstance(x, (unicode, int, float, bool)):
        return x
    else:
        try:
            x = str(x).decode("utf-8")
        except Exception as e:
            print e
            pass
    return x


def dict_to_md(data):
    meta = data.get("meta")
    content = data.get("content").encode("utf-8")
    meta = {k.capitalize():v for k, v in meta.iteritems()}
    meta = yaml.safe_dump(meta, default_flow_style=False, indent=2)
    # meta_template = "{key}:{value}"
    #
    # def make_str(value):
    #     if isinstance(value, unicode):
    #         value = value.encode("utf-8")
    #     elif not isinstance(value, str):
    #         value = repr(value)
    #     return str(value)
    #
    # meta = [meta_template.format(key= k.capitalize(),
    #                              value= make_str(v)+"\n")
    #
    #         for k, v in meta.iteritems()]
    #
    # meta = "".join(meta)

    file_template = "/*\n{meta}*/\n{content}"

    file = file_template.format(meta=meta, content=content)
    return file


def md_to_dict(md_file):
    md_pattern = r"(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)"
    md_pattern = re.compile(md_pattern)
    m = md_pattern.match(md_file)
    if not m:
        return None
    content = m.group("content").replace("\n","")
    meta_string = m.group("meta")

    rv = dict()
    yaml_data = yaml.safe_load(meta_string)
    rv["meta"] = convert_data(yaml_data)
    # for item in meta:
#         if item:
#             t = item.split(":", 1)
#             if len(t) == 2:
#                 try:
#                     tmp_obj = ast.literal_eval(t[1].strip())
#                     rv['meta'][t[0].lower()] = convert_unicode(tmp_obj)
#                 except Exception as e:
#                     rv['meta'][t[0].lower()] = t[1].strip()
    rv['content'] = content
    return rv


def transport_download(cfg):
    url = cfg.get("url")
    headers = cfg.get('headers')
    params = cfg.get('params')
    dest = cfg.get("dest", DEFAULT_CONTENT_DIR)
    dest = safe_path(dest)
    replace_rules = cfg.get("replace", [])
    
    if not os.path.isdir(dest):
        os.mkdir(dest)
    try:
        r = getData(url, params=params, headers=headers)
        data = r.json()
    except Exception as e:
        raise e
    site_data = {
        "meta": data.get("site_meta"),
        "menus": data.get("menus"),
        "terms": data.get("terms"),
        "content_types": data.get("content_types"),
        # "files": data.get("files")
    }   
    
    json_unicode = json.dumps(site_data,
                             indent=2,
                             sort_keys=True,
                             separators=(',', ': '),
                             ensure_ascii=False)

    for rule in replace_rules:
        json_unicode = replace(rule.get("pattern"),
                              rule.get("replacement"),
                              json_unicode)
    
    site_file_path = os.path.join(dest, DEFAULT_SITE_FILE)
    site_file = open(site_file_path, 'w')
    site_file.write(json_unicode.encode("utf-8"))
    site_file.close()
    
    files = data.get("files")
    for file in files:
        file_type = file.get("content_type")
        file_alias = file.get("alias")
        file_dest = dest
        if not file_type or not file_alias:
            print "Write file filed:", file
            continue
        elif file_type != DEFAULT_CONTENT_TYPE:
            file_dest = os.path.join(dest, file_type)
            
        if not os.path.isdir(file_dest):
            os.mkdir(file_dest)
        
        new_file = {}
        new_file["meta"] = file["meta"]
        new_file["content"] = file["content"]
        new_file["meta"]["status"] = file["status"]
        new_file["meta"]["priority"] = file["priority"]
        
        file_string = dict_to_md(new_file).decode("utf-8")
        for rule in replace_rules:
            file_string = replace(rule.get("pattern"),
                                  rule.get("replacement"),
                                  file_string)
        file_path = os.path.join(file_dest, "{}.md".format(file_alias))
        f = open(file_path, 'w')
        f.write(file_string.encode("utf-8"))
        f.close()
        


def transport_upload(cfg):
    url = cfg.get("url")
    headers = cfg.get('headers')
    params = cfg.get('params')
    cwd = cfg.get("cwd", DEFAULT_CONTENT_DIR)
    cwd = safe_path(cwd)
    replace_rules = cfg.get("replace", [])
    
    if not os.path.isdir(cwd):
        raise Exception("Transport upload dir dose not exist.")
    payload = {
        "site_meta":{},
        "menus":{},
        "content_types":{},
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
                filename = file[0:-3]
                file_path = os.path.join(cwd, dirname, file)
                f = open(file_path, "r")
                file_source = f.read().decode("utf-8")
                for rule in replace_rules:
                    file_source = replace(rule.get("pattern"),
                                          rule.get("replacement"),
                                          file_source)
                file_data = md_to_dict(file_source)
                file_data["alias"] = filename
                meta = file_data["meta"]
                
                file_data["content_type"] = meta.get("type", content_type)
                meta.pop("type", None)
                
                file_data["status"] = meta.get("status", 1)
                meta.pop("status", None)
                
                file_data["priority"] = meta.get("priority", 0)
                meta.pop("priority", None)
                
                file_data["meta"] = meta
                payload['files'].append(file_data)
    
    site_path = os.path.join(cwd, DEFAULT_SITE_FILE)
    if os.path.isfile(site_path):
        try:
            site_file = open(site_path, "r")
            site_file_source = site_file.read().decode("utf-8")
            for rule in replace_rules:
                site_file_source = replace(rule.get("pattern"),
                                           rule.get("replacement"),
                                           site_file_source)

            site_data = json.loads(site_file_source)

            payload["site_meta"] = site_data.get("meta",{})
            payload["content_types"] = site_data.get("content_types",{})
            payload["menus"] = site_data.get("menus",{})
            payload["terms"] = site_data.get("terms",{})
        except Exception as e:
            raise Exception("Site data error:", e)
    
    try:
        r = uploadData(url, data=payload, params=params, headers=headers)
        print r.json()
    except Exception as e:
        raise e
    
    
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
    
    print "peon: finish transport ..."
    

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