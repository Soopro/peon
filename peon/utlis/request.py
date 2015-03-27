#coding=utf-8
from __future__ import absolute_import
import os, requests

def _get_method(method="get"):
    do_request = 'get'

    if method == 'post':
        do_request = requests.post
    elif method == 'put':
        do_request = requests.put
    elif method == 'delte':
        do_request = requests.delte
    return do_request


def uploadFile(file_path, url, data=None, params=None, headers=None):
    try:
        files = {'file': open(file_path, 'rb')}
    except Exception as e:
        raise e

    try:
        r = requests.post(url,
                          files=files,
                          data=data,
                          params=None,
                          headers=headers)
        r.raise_for_status()
    except requests.RequestException as e:
        print r.json()
        raise e
    
    return r


def request_json(data, url, method):
    headers = {'content-type': 'application/json'}
    do_request = _get_method(method)
    try:
        r = do_request(url, data=data, headers=headers)
        r.raise_for_status()
    except requests.RequestException as e:
        raise e
    return r