#!/usr/bin/env python2

from __future__ import print_function

import json
import os
import sys
import threading

import cherrypy
from core import pycore

class EventPublisher(object):
    TYPE_CREATED = 'created'
    TYPE_MODIFIED = 'modified'
    TYPE_DELETED = 'deleted'

    def __init__(self, parent=None):
        self.parent = parent
        # Condition for blocking the client threads
        self.listener_cond = threading.Condition()
        self.path = None
        self.msg = None

        # Register with cherrypy so we can shut down client threads cleanly
        cherrypy.engine.subscribe('stop', self.stop, -99999999)

    @cherrypy.expose
    def events(self):
        if cherrypy.request.method != 'GET':
            raise cherrypy.HTTPError(405)

        if (cherrypy.request.headers.has_key('Accept') and
                cherrypy.request.headers['Accept'] == 'text/event-stream'):
            cherrypy.response.headers['Content-Type'] = 'text/event-stream'
            do_sse = True
        else:
            cherrypy.response.headers['Content-Type'] = 'application/json'
            do_sse = False

        return self.send_response(do_sse)
    events._cp_config = {'response.stream': True}

    def send_response(self, do_sse=False):
        i = 0
        while True:
            with self.listener_cond:
                self.listener_cond.wait()
                data_dict = {
                    'path': self.path,
                    'msg': self.msg,
                    'msg_type': self.msg_type,
                }

            if data_dict['path'] is None:
                break

            data = json_dumps(data_dict)

            if do_sse:
                # Prefix each line with 'data:'
                data = ''.join(map(
                    lambda x: 'data: {}\n'.format(x), data.split('\n')))
                # Put the event name and id numbers in front
                # This puts a second \n at the end of the message to end
                data = 'event: {}\nid: {}\n{}\n'.format(
                        data_dict['msg_type'], i, data)
                i += 1

            yield data

    def publish_event(self, path, msg, msg_type):
        with self.listener_cond:
            self.path = path
            self.msg = msg
            self.msg_type = msg_type
            self.listener_cond.notify_all()
            if self.parent:
                self.parent.publish_event(path, msg, msg_type)

    def stop(self):
        self.publish_event(None, None, None)

class Root(EventPublisher):
    def __init__(self):
        super(Root, self).__init__()
        self.sessions = SessionManager(self)

    @cherrypy.expose
    def index(self):
        path = os.path.join(os.path.abspath(os.path.split(__file__)[0]),
                            'static', 'index.html')
        return cherrypy.lib.static.serve_file(path)

class SessionManager(EventPublisher):
    def __init__(self, parent):
        super(SessionManager, self).__init__(parent)
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

        self.publish_event(wrapper.path, wrapper, EventPublisher.TYPE_CREATED)

        return wrapper

    def destroy_session(self, wrapper):
        self.wrappers.pop(wrapper.session.sessionid)
        self.publish_event(wrapper.path, None, EventPublisher.TYPE_DELETED)
        wrapper.session.shutdown()
        wrapper.session.delsession(wrapper.session)

class SessionWrapper(EventPublisher):
    'Small wrapper around a session to handle HTTP methods.'

    def __init__(self, session, manager):
        super(SessionWrapper, self).__init__(manager)
        self.session = session
        self.manager = manager
        self.nodes = NodeManager(session, self)

        self.path = 'sessions/{}'.format(self.session.sessionid)

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

class NodeManager(EventPublisher):
    NODE_TYPES = {
        'default': pycore.nodes.CoreNode,
        'hub': pycore.nodes.HubNode,
        'rj45': pycore.nodes.RJ45Node,
        'switch': pycore.nodes.SwitchNode,
        'tunnel': pycore.nodes.TunnelNode,
        'wlan': pycore.nodes.WlanNode,
    }

    def __init__(self, session, session_manager):
        super(NodeManager, self).__init__(session_manager)
        self.session = session
        self.wrappers = {}

    def _cp_dispatch(self, vpath):
        'Get the correct node instance to continue method dispatch.'
        return self.wrappers[int(vpath.pop(0))]

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

        self.publish_event(wrapper.path, wrapper, EventPublisher.TYPE_CREATED)

        return wrapper

    def destroy_node(self, wrapper):
        self.wrappers.pop(wrapper.node.objid)
        self.session.delobj(wrapper.node.objid)

class NodeWrapper(EventPublisher):
    def __init__(self, node, manager):
        super(NodeWrapper, self).__init__(manager)
        self.node = node
        self.manager = manager

        self.path = 'sessions/{}/nodes/{}'.format(node.session.sessionid,
                                                  node.objid)

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
            rv = self.update_node(cherrypy.request.json)
            self.publish_event(self.path, self, EventPublisher.TYPE_MODIFIED)
            return json_dumps(rv)

        elif cherrypy.request.method == 'DELETE':
            self.publish_event(self.path, None, EventPublisher.TYPE_DELETED)
            return self.manager.destroy_node(self)

        else:
            raise cherrypy.HTTPError(405)

    @cherrypy.expose
    def execute(self):
        print(0)
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405)

        print(1)
        req = cherrypy.request.json

        cmd = req['command']
        print(2)
        status, output = self.node.cmdresult(cmd)
        print(3)
        return json_dumps({
            'command': cmd,
            'status': status,
            'output': output,
        })

    def update_node(self, req):
        if req.has_key('position'):
            x, y, z = map(int, req['position'])
            self.node.setposition(x, y, z)
        return self


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
