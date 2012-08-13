#!/usr/bin/env python2

import json
import os
import sys
import threading

import cherrypy
from core import pycore

class SessionWrapper(object):
    'Small wrapper around a session to handle HTTP methods.'

    def __init__(self, session, manager):
        self.session = session
        self.manager = manager

    def _json_(self):
        return self.session._json_()

    @cherrypy.expose
    def index(self):
        if cherrypy.request.method == 'GET':
            return json_dumps(self.session)
        elif cherrypy.request.method == 'DELETE':
            return self.manager.remove_session(self)
        else:
            raise cherrypy.HTTPError(405)

    @cherrypy.expose
    def nodes(self, *args, **kwargs):
        if cherrypy.request.method == 'GET':
            return json_dumps(list(self.session.objs()))

        elif cherrypy.request.method == 'POST':
            return self.create_node(cherrypy.request.json)
        else:
            raise cherrypy.HTTPError(405)

    def create_node(self, req):
        if req['type'] == 'wlan':
            cls = pycore.nodes.WlanNode
        else:
            cls = pycore.nodes.CoreNode

        name = req['name']
        if len(name) == 0:
            name = None

        node = self.session.addobj(cls,
                objid=len(list(self.session.objs())),
                name=name)

        x = None
        y = None
        z = None
        if req.has_key('x'):
            x = req['x']
        if req.has_key('y'):
            y = req['y']
        if req.has_key('z'):
            z = req['z']
        node.setposition(x, y, z)

        return json_dumps(node)

class SessionManager(object):
    def __init__(self):
        self.wrappers = {}
        self.sid = 0
        self.lock = threading.Lock()

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
        with self.lock:
            # Need to lock creating the session
            self.sid += 1
            session = pycore.Session(self.sid)
            wrapper = SessionWrapper(session, self)
            self.wrappers[session.sessionid] = wrapper

        if req.has_key('name'):
            session.name = req['name']

        if req.has_key('user'):
            session.setuser(req['user'])

        return wrapper

    def remove_session(self, wrapper):
        with self.lock:
            self.wrappers.pop(wrapper.session.sessionid)
        wrapper.session.shutdown()
        wrapper.session.delsession(wrapper.session)

class Root(object):
    def __init__(self):
        self.sessions = SessionManager()

    @cherrypy.expose
    def index(self):
        path = os.path.join(os.path.abspath(os.path.split(__file__)[0]),
                            'static', 'index.html')
        return cherrypy.lib.static.serve_file(path)

def session_json(self):
    return {
        'sid': self.sessionid,
        'name': self.name,
        'user': self.user,
        'nodes': [n.objid for n in self.objs()]
    }
pycore.Session._json_ = session_json

def node_json(self):
    return {
        'nid': self.objid,
        'name': self.name,
        'type': str(type(self)),
        'sid': self.session.sessionid,
        'x': self.position.x,
        'y': self.position.y,
        'z': self.position.z,
    }
pycore.nodes.PyCoreObj._json_ = node_json

class CoreJSONEncoder(json.JSONEncoder):
    def default(self, o):
        print 'TYPE:', type(o)
        try:
            return o._json_()
        except AttributeError:
            return super(CoreJSONEncoder, self).default(o)

def json_dumps(x):
    dbg = json.dumps(x, indent=4, cls=CoreJSONEncoder)
    print 'JSON:', dbg
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
