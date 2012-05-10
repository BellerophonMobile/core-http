#!/usr/bin/env python2

import json
import os
import sys

import cherrypy
from core import pycore

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
    def objects(self, *args, **kwargs):
        if cherrypy.request.method == 'GET':
            return json_dumps({'objects': list(self.session.objs())})

        elif cherrypy.request.method == 'POST':
            if kwargs['type'] == 'wifi':
                cls = pycore.nodes.WlanNode
            else:
                cls = pycore.nodes.CoreNode

            node = self.session.addobj(cls,
                    objid=len(list(self.session.objs())),
                    name=kwargs['name'])
            return json_dumps(node)

        else:
            raise cherrypy.HTTPError(405)

class Sessions(object):
    def __init__(self):
        self.sessions = []

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
            core_session = pycore.Session(len(self.sessions))
            session = Session(core_session)
            self.sessions.append(session)

            if kwargs.has_key('name'):
                core_session.name = kwargs['name']

            if kwargs.has_key('filename'):
                core_session.filename = kwargs['filename']

            if kwargs.has_key('node_count'):
                core_session.node_count = int(kwargs['node_count'])

            if kwargs.has_key('thumbnail'):
                core_session.setthumbnail(kwargs['thumbnail'])

            if kwargs.has_key('user'):
                core_session.setuser(kwargs['user'])

            return json_dumps(session)

        else:
            raise cherrypy.HTTPError(405)

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
        'filename': self.filename,
        'thumbnail': self.thumbnail,
        'user': self.user,
        'node_count': self.node_count,
    }
pycore.Session._json_ = session_json

def object_json(self):
    return {
        'name': self.name,
        'type': str(type(self)),
    }
pycore.nodes.PyCoreObj._json_ = object_json

class CoreJSONEncoder(json.JSONEncoder):
    def default(self, o):
        print 'TYPE:', type(o)
        try:
            return o._json_()
        except AttributeError:
            return super(CoreJSONEncoder, self).default(o)

def json_dumps(x):
    return json.dumps(x, indent=4, cls=CoreJSONEncoder)

def main(argv):
    root = Root()

    config = {
        'global': {
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 8080,
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.abspath(
                os.path.split(__file__)[0]), 'static')
        },
    }

    cherrypy.quickstart(root, '/', config)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
