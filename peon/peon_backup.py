#coding=utf-8
from __future__ import absolute_import
import os, sys, shutil, time
import subprocess

BACKUP_FILE = "backups.json"

BASE_DIR = "./"

def copy(cfg):
    src = cfg.get("src",[])
    dest = cfg.get("dest", BASE_DIR)
    for s in src:
        shutil.copytree(src, dest)

def shell(cfg):
    for cmd in cfg:
        subprocess.call(cmd, shell=True)

def redis(cfg):
    dbhost = cfg.get("dbhost")
    dbhost = "-h " + dbhost if dbhost else ""
    port = cfg.get("port")
    port = "-p " + port if port else ""
    pwd = cfg.get("pwd")
    pwd = "-a " + pwd if pwd else ""
    src =  cfg.get("src")
    dest = cfg.get("dest", os.path.join(BASE_DIR,"redis"))
    try:
        subprocess.call(["redis-cli", dbhost, port, pwd, "save"])
        shutil.copy(src, dest)
    except Exception as e:
        raise e

def monogodb(cfg):
    dbhost = cfg.get("dbhost")
    port = cfg.get("port")
    if dbhost and port:
        dbhost = dbhost+":"+"port"
    dbhost = "-h " + dbhost if dbhost else ""
    dbname = cfg.get("dbname")
    dbname = "-d " + dbname if dbname else ""
    
    user = cfg.get("user")
    user = "-u " + user if user else ""
    
    pwd = cfg.get("pwd")
    pwd = "-p " + pwd if pwd and user else ""
    
    dest = cfg.get("dest", os.path.join(BASE_DIR,"mongodb"))
    
    dest = "-o " + dest if dest else ""

    subprocess.call(["mongodump", dbhost, dbname, user, pwd, dest])


def load_config():
    config_file = open(BACKUP_FILE)
    config_data = json.load(peon_data,
                            object_pairs_hook=OrderedDict)
    config_file.close()
    
    print "peon: Ready to backup"

    return config_data

def create_backup_folder():
    now = datetime.datetime.now().strftime("%y_%m_%d")
    if not os.path.isdir(now):
        os.mkdir(now)
    return now


def backup():
    global BASE_DIR
    config = load_config()
    BASE_DIR = create_backup_folder()
    
    for k, v in config.iteritems():
        if k is 'redis':
            redis(v)
        elif k is 'files':
            copy(v)
        elif k is 'shell':
            shell(v)
    
    print "peon: finish backup files and datas ..."


if __name__ == '__main__':
    backup()
