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
        config = {
            'danger_mode': True,
        }
        headers = {
            'Content-Type': 'application/json'
        }

        self.req = requests.session(config=config, headers=headers)

    def sessions(self):
        r = self.req.get(make_url(self.address, 'sessions'))
        return [Session(self.address, self.req, json) for json in r.json]

    def get_session(self, sid):
        r = self.req.get(make_url(self.address, 'sessions', sid))
        return Session(self.address, self.req, r.json)

    def new_session(self, name, user):
        data = json_dumps({
            'name': name,
            'user': user,
        })
        r = self.req.post(make_url(self.address, 'sessions'), data=data)
        return Session(self.address, self.req, r.json)

class Session(object):
    def __init__(self, address, req, json):
        self.address = address
        self.req = req

        self._sid = json['sid']
        self._name = json['name']
        self._user = json['user']

    def delete(self):
        r = self.req.delete(make_url(self.address, 'sessions', self.sid))

    def nodes(self):
        r = self.req.get(make_url(self.address, 'sessions', self.sid, 'nodes'))
        return [Node(self.address, self.req, json) for json in r.json]

    def get_node(self, nid):
        r = self.req.get(
                make_url(self.address, 'sessions', self.sid, 'nodes', nid))
        return Node(self.address, self.req, r.json)

    def new_node(self, ntype, name, x, y, z):
        data = json_dumps({
            'type': ntype,
            'name': name,
            'x': x,
            'y': y,
            'z': z,
        })
        r = self.req.post(make_url(self.address, 'sessions', self.sid,'nodes'),
                          data=data)
        return Node(self.address, self.req, r.json)

    sid = property(lambda self: self._sid, doc='Session ID')
    name = property(lambda self: self._name, doc='Session Name')
    user = property(lambda self: self._user, doc='Session Owner')

class Node(object):
    def __init__(self, address, req, json):
        self.address = address
        self.req = req

        self._nid = json['nid']
        self._sid = json['sid']
        self._name = json['name']
        self._type = json['type']
        self._position = (json['x'], json['y'], json['z'])

    def delete(self):
        r = self.req.delete(make_url(
            self.address, 'sessions', self.sid, 'nodes', self.nid))

    sid = property(lambda self: self._sid, doc='Session ID')
    nid = property(lambda self: self._nid, doc='Node ID')
    name = property(lambda self: self._name, doc='Node Name')
    ntype = property(lambda self: self._type, doc='Node Type')
    position = property(lambda self: self._position, doc='Node coordinates')

def make_url(*args, **kwargs):
    url = '/'.join(map(str, args))
    if kwargs.get('endslash', True) and url[-1] != '/':
        url += '/'
    return url

def json_dumps(x):
    return json.dumps(x, separators=(',', ':'))
