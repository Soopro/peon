# coding=utf-8


import json
import requests


def getData(url, params=None, headers=None, is_json=True):
    request_headers = {'content-type': 'application/json'} if is_json else {}
    request_headers.update(headers)
    r = None
    try:
        r = requests.get(url,
                         params=params,
                         headers=request_headers)
        r.raise_for_status()
    except requests.RequestException as e:
        print('========== Requests ==========')
        print(e)
        print('------------------------------')
        if r is not None:
            print(r.json())
        print('==============================')
        raise e

    return r


def uploadData(url, data=None, params=None, headers=None, is_json=True):
    r = None
    request_headers = {'content-type': 'application/json'} if is_json else {}
    request_headers.update(headers)
    request_data = json.dumps(data)
    try:
        r = requests.post(url,
                          data=request_data,
                          params=params,
                          headers=request_headers)
        r.raise_for_status()
    except requests.RequestException as e:
        print('========== Requests ==========')
        print(e)
        print('------------------------------')
        if r is not None:
            print(r.json())
        print('==============================')
        raise e
    return r


def uploadFile(file_path, url,
               data=None, params=None, headers=None, timeout=30):
    try:
        files = {'file': open(file_path, 'rb')}
    except Exception as e:
        raise e

    r = None
    try:
        r = requests.post(url,
                          files=files,
                          data=data,
                          params=params,
                          headers=headers,
                          timeout=timeout)
        r.raise_for_status()
    except requests.RequestException as e:
        print('========== Requests ==========')
        print(e)
        print('------------------------------')
        if r is not None:
            print(r.json())
        print('==============================')
        raise e

    return r
