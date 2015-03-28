#coding=utf-8
from __future__ import absolute_import

import os, sys, shutil, datetime
import subprocess

from .utlis import makeZip, copy_file, copy_tree, ensure_dir
from .config import load_config, CONFIG_FILE

DEFAULT_ACTION = "backup"

def _make_backup_zip(filename):
    makeZip(filename,
            filename+".zip",
            include_hidden=True)

def files(cfg):
    name = "files"
    src = cfg.get("src",[])
    dest = name
    ensure_dir(dest)
    for s in src:
        d = os.path.join(dest, s.lstrip("/"))
        if os.path.isfile(s):
            ensure_dir(d, True)
            copy_file(s, d)
        else:
            copy_tree(s, d)

    try:
        _make_backup_zip(name)
    except Exception as e:
        raise e


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
    ensure_dir(dest)
    try:
        subprocess.call("redis-cli"+dbhost+port+pwd+" "+"save", shell=True)
        copy_file(src, dest)
    except Exception as e:
        raise e

    if os.path.isdir(name):
        _make_backup_zip(name)
    else:
        raise Exception("Can't not packing redis.")
    
    print "Backup: Redis -> OK"
    

def mongodb(cfg):
    name = "mongodb"
    dest = name
    ensure_dir(dest)
    
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

    odest = " -o " + dest

    try:
        subprocess.call("mongodump"+dbhost+dbname+user+pwd+odest, shell=True)
    except Exception as e:
        raise e

    if os.path.isdir(name):
        _make_backup_zip(name)
    else:
        raise Exception("Can't not packing mongodb.")
    
    print "Backup: Mongodb -> OK"


def create_backup_folder():
    now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    if not os.path.isdir(now):
        os.mkdir(now)
    else:
        now = None
    return now


def backup():
    peon_config = load_config(DEFAULT_ACTION)
    new_dir = create_backup_folder()
    if not new_dir:
        raise Exception("Backup folder is exist.")
    old_dir = os.getcwd()
    os.chdir(new_dir)

    for k, v in peon_config.iteritems():
        if k == 'redis':
            redis(v)
        elif k == 'mongodb':
            mongodb(v)
        elif k == 'files':
            files(v)
        elif k == 'shell':
            shell(v)

    os.chdir(old_dir)
    print "peon: finish backups ..."


if __name__ == '__main__':
    backup()
