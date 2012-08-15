#!/usr/bin/env python2

from __future__ import print_function

import json
import os
import sys

import cherrypy
from core import pycore

class SessionWrapper(object):
    'Small wrapper around a session to handle HTTP methods.'

    def __init__(self, session, manager):
        self.session = session
        self.manager = manager
        self.nodes = NodeManager(session)

    def _json_(self):
        return {
            'sid': self.session.sessionid,
            'name': self.session.name,
            'user': self.session.user,
            'nodes': [n.objid for n in self.session.objs()]
        }

    @cherrypy.expose
    def index(self):
        if cherrypy.request.method == 'GET':
            return json_dumps(self)

        elif cherrypy.request.method == 'DELETE':
            return self.manager.destroy_session(self)

        else:
            raise cherrypy.HTTPError(405)

class SessionManager(object):
    def __init__(self):
        self.wrappers = {}
        self.sid = 0

    def _cp_dispatch(self, vpath):
        '''Get the correct session instance to continue method dispatch.

        The cherrypy dispatcher calls this with URLs like "/sessions/10/..."
        Since we can't have an attribute named "10" on this session, this
        function gets called to provide that.
        '''
        return self.wrappers[int(vpath.pop(0))]

    @cherrypy.expose
    def index(self, **kwargs):
        if cherrypy.request.method == 'GET':
            return json_dumps(self.wrappers.values())

        elif cherrypy.request.method == 'POST':
            print('INCOMING JSON', cherrypy.request.json)
            return json_dumps(self.create_session(cherrypy.request.json))

        else:
            raise cherrypy.HTTPError(405)

    def create_session(self, req):
        self.sid += 1
        session = pycore.Session(self.sid)
        wrapper = SessionWrapper(session, self)
        self.wrappers[session.sessionid] = wrapper

        if req.has_key('name'):
            session.name = req['name']

        if req.has_key('user'):
            session.setuser(req['user'])

        return wrapper

    def destroy_session(self, wrapper):
        self.wrappers.pop(wrapper.session.sessionid)
        wrapper.session.shutdown()
        wrapper.session.delsession(wrapper.session)

class NodeManager(object):
    NODE_TYPES = {
        'default': pycore.nodes.CoreNode,
        'hub': pycore.nodes.HubNode,
        'rj45': pycore.nodes.RJ45Node,
        'switch': pycore.nodes.SwitchNode,
        'tunnel': pycore.nodes.TunnelNode,
        'wlan': pycore.nodes.WlanNode,
    }

    def __init__(self, session):
        self.session = session
        self.wrappers = {}

    def _cp_dispatch(self, vpath):
        'Get the correct node instance to continue method dispatch.'
        return self.wrappers[int(vpath.pop())]

    @cherrypy.expose
    def index(self):
        if cherrypy.request.method == 'GET':
            return json_dumps(self.wrappers.values())

        elif cherrypy.request.method == 'POST':
            return json_dumps(self.create_node(cherrypy.request.json))

        else:
            raise cherrypy.HTTPError(405)

    def create_node(self, req):
        cls = NodeManager.NODE_TYPES[req.get('type', 'default')]

        name = req['name']
        if len(name) == 0:
            name = None

        node = self.session.addobj(cls,
                objid=len(list(self.session.objs())),
                name=name)

        wrapper = NodeWrapper(node, self)
        self.wrappers[node.objid] = wrapper

        wrapper.update_node(req)

        return wrapper

    def destroy_node(self, wrapper):
        self.wrappers.pop(wrapper.node.objid)
        self.session.delobj(wrapper.node.objid)

class NodeWrapper(object):
    def __init__(self, node, manager):
        self.node = node
        self.manager = manager

    def _json_(self):
        return {
            'nid': self.node.objid,
            'name': self.node.name,
            'type': str(type(self.node)),
            'sid': self.node.session.sessionid,
            'position': self.node.position.get(),
        }

    @cherrypy.expose
    def index(self):
        if cherrypy.request.method == 'GET':
            return json_dumps(self)

        elif cherrypy.request.method == 'POST':
            return json_dumps(self.update_node(cherrypy.request.json))

        elif cherrypy.request.method == 'DELETE':
            return self.manager.destroy_node(self)

        else:
            raise cherrypy.HTTPError(405)

    def update_node(self, req):
        if req.has_key('position'):
            x, y, z = map(int, req['position'])
            self.node.setposition(x, y, z)

        return self

class Root(object):
    def __init__(self):
        self.sessions = SessionManager()

    @cherrypy.expose
    def index(self):
        path = os.path.join(os.path.abspath(os.path.split(__file__)[0]),
                            'static', 'index.html')
        return cherrypy.lib.static.serve_file(path)


class CoreJSONEncoder(json.JSONEncoder):
    def default(self, o):
        print('TYPE:', type(o))
        if hasattr(o, '_json_'):
            return o._json_()
        else:
            return super(CoreJSONEncoder, self).default(o)

def json_dumps(x):
    dbg = json.dumps(x, indent=4, cls=CoreJSONEncoder)
    print('JSON:', dbg)
    return json.dumps(x, separators=(',', ':'), cls=CoreJSONEncoder)

def main(argv):
    root = Root()

    config = {
        'global': {
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 8080,
            'request.body.processors': {
                'application/json': cherrypy.lib.jsontools.json_processor,
            }
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.abspath(
                os.path.split(__file__)[0]), 'static')
        },
        '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(os.path.abspath(
                os.path.split(__file__)[0]), 'static', 'favicon.ico'),
        }
    }

    cherrypy.quickstart(root, '/', config)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
