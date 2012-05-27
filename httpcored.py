#!/usr/bin/env python2

import json
import os
import sys
import threading

import cherrypy
from core import pycore, coreobj

class Session(object):
    'Small wrapper around a session to handle HTTP methods.'

    def __init__(self, session):
        self.session = session

    def _json_(self):
        return self.session._json_()

    @cherrypy.expose
    def index(self):
        if cherrypy.request.method == 'GET':
            return json_dumps(self.session)
        else:
            raise cherrypy.HTTPError(405)

    @cherrypy.expose
    def nodes(self, *args, **kwargs):
        if cherrypy.request.method == 'GET':
            return json_dumps({'nodes': list(self.session.objs())})

        elif cherrypy.request.method == 'POST':
            req = cherrypy.request.json

            if req['type'] == 'wifi':
                cls = pycore.nodes.WlanNode
            else:
                cls = pycore.nodes.CoreNode

            name = req['name']
            if len(name) == 0:
                name = None

            node = self.session.addobj(cls,
                    objid=len(list(self.session.objs())),
                    name=name)
            return json_dumps(node)

        else:
            raise cherrypy.HTTPError(405)

class Sessions(object):
    def __init__(self):
        self.sessions = []
        self.lock = threading.Lock()

    def _cp_dispatch(self, vpath):
        '''Get the correct session instance to continue method dispatch.

        The cherrypy dispatcher calls this with URLs like "/sessions/10/..."
        Since we can't have an attribute named "10" on this session, this
        function gets called to provide that.
        '''
        return self.sessions[int(vpath.pop(0))]

    @cherrypy.expose
    def index(self, **kwargs):
        if cherrypy.request.method == 'GET':
            return json_dumps({'sessions': self.sessions})

        elif cherrypy.request.method == 'POST':
            return json_dumps(self.create_session(cherrypy.request.json))

        else:
            raise cherrypy.HTTPError(405)

    def create_session(self, req):
        with self.lock:
            # Need to lock creating the session
            core_session = pycore.Session(len(self.sessions))
            session = Session(core_session)
            self.sessions.append(session)

        if req.has_key('name'):
            core_session.name = req['name']

        if req.has_key('filename'):
            core_session.filename = req['filename']

        if req.has_key('node_count'):
            core_session.node_count = int(req['node_count'])

        if req.has_key('thumbnail'):
            core_session.setthumbnail(req['thumbnail'])

        if req.has_key('user'):
            core_session.setuser(req['user'])

        return core_session

class Root(object):
    def __init__(self):
        self.sessions = Sessions()

    @cherrypy.expose
    def index(self):
        path = os.path.join(os.path.abspath(os.path.split(__file__)[0]),
                            'static', 'index.html')
        return cherrypy.lib.static.serve_file(path)

def session_json(self):
    return {
        'id': self.sessionid,
        'name': self.name,
        'user': self.user,
        'nodes': [n.objid for n in self.objs()]
    }
pycore.Session._json_ = session_json

def node_json(self):
    return {
        'id': self.objid,
        'name': self.name,
        'type': str(type(self)),
        'session_id': self.session.sessionid,
        'position': self.position
    }
pycore.nodes.PyCoreObj._json_ = node_json

def position_json(self):
    x, y, z = self.get()
    return {
        'x': x,
        'y': y,
        'z': z,
    }
coreobj.Position._json_ = position_json

class CoreJSONEncoder(json.JSONEncoder):
    def default(self, o):
        print 'TYPE:', type(o)
        try:
            return o._json_()
        except AttributeError:
            return super(CoreJSONEncoder, self).default(o)

def json_dumps(x):
    x = json.dumps(x, indent=4, cls=CoreJSONEncoder)
    print 'JSON:', x
    return x

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
