#!/usr/bin/env python2
'''
    core.py - Python API for the HTTP CORE daemon
    Author: Tom Wambold <tom5760@gmail.com>
'''

import json

import requests

class Daemon(object):
    DEFAULT_ADDRESS = 'http://localhost:8080'

    def __init__(self, address=DEFAULT_ADDRESS):
        self.address = address

    def sessions(self):
        r = requests.get(make_url(self.address, 'sessions'))
        r.raise_for_status()
        return [Session(self.address, json) for json in r.json]

    def new_session(self, name, user):
        data = {
            'name': name,
            'user': user,
        }
        r = post_json((self.address, 'sessions'), data)
        r.raise_for_status()
        return Session(self.address, r.json)

    def get_session(self, sid):
        r = requests.get(make_url(self.address, 'sessions', sid))
        r.raise_for_status()
        return Session(self.address, r.json)

class Session(object):
    def __init__(self, address, json):
        self.address = address

        self._sid = json['id']
        self._name = json['name']
        self._user = json['user']

    def set_name(self, name):
        raise NotImplementedError()

    def set_user(self, user):
        raise NotImplementedError()

    def delete(self):
        r = requests.delete(make_url(self.address, 'sessions', self.sid))
        r.raise_for_status()

    sid = property(lambda self: self._sid, doc='Session ID')
    name = property(lambda self: self._name, set_name, doc='Session Name')
    user = property(lambda self: self._user, set_user, doc='Session Owner')

def make_url(*args, **kwargs):
    url = '/'.join(map(str, args))
    if kwargs.get('endslash', True) and url[-1] != '/':
        url += '/'
    return url

def post_json(url_parts, data, endslash=True):
    headers = {'Content-Type': 'application/json'}
    return requests.post(make_url(*url_parts, endslash=endslash),
                         headers=headers,
                         data=json.dumps(data))
