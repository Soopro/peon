#coding=utf-8
from __future__ import absolute_import

import os, sys, shutil, datetime
import subprocess

from .utlis import makeZip
from .config import load_config

DEFAULT_ACTION = "backup"

def copy(cfg):
    name = "files"
    src = cfg.get("src",[])
    dest = name
    
    for s in src:
        to = os.path.join(dest, s.lstrip("/"))
        try:
            shutil.copytree(s, to)
        except Exception as e:
            raise e
    
    makeZip(name, name+".zip", include_hidden=True)


def shell(cfg):
    for cmd in cfg:
        subprocess.call(cmd, shell=True)


def redis(cfg):
    name = "redis"
    
    dbhost = cfg.get("dbhost")
    dbhost = " -h " + dbhost if dbhost else ""
    port = cfg.get("port")
    port = " -p " + port if port else ""
    pwd = cfg.get("pwd")
    pwd = " -a " + pwd if pwd else ""
    src =  cfg.get("src")
    dest = name
    if not os.path.isdir(dest):
        os.mkdir(dest)
    try:
        subprocess.call("redis-cli"+dbhost+port+pwd+" "+"save", shell=True)
        shutil.copy(src, dest)
        makeZip(name, name+".zip")
    except Exception as e:
        raise e


def mongodb(cfg):
    
    name = "mongodb"
    
    dbhost = cfg.get("dbhost")
    port = cfg.get("port")
    if dbhost and port:
        dbhost = dbhost+":"+"port"
    dbhost = " -h " + dbhost if dbhost else ""
    dbname = cfg.get("dbname")
    dbname = " -d " + dbname if dbname else ""
    
    user = cfg.get("user")
    user = " -u " + user if user else ""
    
    pwd = cfg.get("pwd")
    pwd = " -p " + pwd if pwd and user else ""

    dest = " -o " + name

    try:
        subprocess.call("mongodump"+dbhost+dbname+user+pwd+dest, shell=True)

        makeZip(name, name+".zip")
    except Exception as e:
        raise e


def create_backup_folder():
    now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    if not os.path.isdir(now):
        os.mkdir(now)
    return now


def backup():
    config = load_config(DEFAULT_ACTION)
    new_dir = create_backup_folder()
    old_dir = os.getcwd()
    os.chdir(new_dir)

    for k, v in config.iteritems():
        if k == 'redis':
            redis(v)
        elif k == 'mongodb':
            mongodb(v)
        elif k == 'files':
            copy(v)
        elif k == 'shell':
            shell(v)

    os.chdir(old_dir)
    print "peon: finish backups ..."


if __name__ == '__main__':
    backup()
