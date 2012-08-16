#!/usr/bin/env python2
'''
    corecli.py - Command-line tool to manipulate CORE sessions.
    Author: Tom Wambold <tom5760@gmail.com>
'''

from __future__ import print_function

import sys

from core import Daemon

class Cli(object):
    def run(self, *args):
        try:
            arg = args[0]
        except IndexError:
            arg = 'help'

        try:
            func = getattr(self, 'do_' + arg)
            func_args = args[1:]
        except AttributeError:
            try:
                func = getattr(self, 'default')
                func_args = args
            except AttributeError:
                print('Invalid argument "{}"'.format(arg))
                return 1

        return func(*func_args)

    @staticmethod
    def do_help(*args):
        print('\n'.join((
            'Usage: {} OBJECT',
            'where OBJECT := {{ session | event | help }}',
        )).format(sys.argv[0]))

    @staticmethod
    def do_session(*args):
        return Session().run(*args)

class Session(Cli):
    @staticmethod
    def do_help(*args):
        print('\n'.join((
            'Usage: {} session COMMAND',
            '  session help                This help',
            '  session list                List all active sessions',
            '  session new NAME USER       Create a new session',
            '  session del ID              Destroys a session',
            '  session ID [...]        Interact with a particular session',
        )).format(sys.argv[0]))

    @staticmethod
    def do_list():
        sessions = Daemon().sessions()
        if len(sessions) == 0:
            print('No active sessions')
            return

        print('{} active sessions'.format(len(sessions)))
        print('ID\tName\tOwner')
        for session in sessions:
            print('{}\t{}\t{}'.format(session.sid, session.name, session.user))

    @staticmethod
    def do_new(name, user):
        session = Daemon().new_session(name, user)
        print('ID:', session.sid)

    @staticmethod
    def do_del(sid):
        Daemon().get_session(sid).delete()

    @staticmethod
    def default(sid, *args):
        return SelectedSession(sid).run(*args)

class SelectedSession(Cli):
    def __init__(self, sid):
        self.sid = sid

    def do_help(self, *args):
        print('\n'.join((
            'Usage: {0} session {1} OBJECT',
            '  session {1} help            This help',
            '  session {1} node            Manipulate nodes of this session',
            '  session {1} link            Manipulate links of this session',
        )).format(sys.argv[0], self.sid))

    def do_node(self, *args):
        return Node(self.sid).run(*args)

    def do_link(self, *args):
        return Link(self.sid).run(*args)

class Node(Cli):
    def __init__(self, sid):
        self.sid = sid
        self.session = Daemon().get_session(self.sid)

    def do_help(self, *args):
        print('\n'.join((
            'Usage: {} session {} node COMMAND',
            '  node help                   This help',
            '  node list                   List all nodes',
            '  node new TYPE NAME X Y Z    Create a new node',
            '  node del ID                 Destroy a node',
            '  node ID [...]           Interact with a particular node',
            '',
            'Types: default, wlan',
        )).format(sys.argv[0], self.sid))

    def do_list(self):
        nodes = self.session.nodes()
        if len(nodes) == 0:
            print('No nodes')
            return

        print('{} nodes'.format(len(nodes)))
        print('ID\tName\tType\tCoordinate')
        for node in nodes:
            print('{0}\t{1}\t{2}\t({3[0]}, {3[1]}, {3[2]})'.format(
                    node.nid, node.name, node.ntype, node.position))

    def do_new(self, ntype, name, x, y, z):
        node = self.session.new_node(ntype, name, x, y, z)
        print('ID:', node.nid)

    def do_del(self, nid):
        self.session.get_node(nid).delete()

    def default(self, nid, *args):
        return SelectedNode(self.sid, nid, self.session).run(*args)

class SelectedNode(Cli):
    def __init__(self, sid, nid, session):
        self.sid = sid
        self.nid = nid
        self.session = session
        self.node = self.session.get_node(self.nid)

    def do_help(self, *args):
        print('\n'.join((
            'Usage: {0} session {1} node get {2} COMMAND',
            '  node {2} help                        This help',
            '  node {2} position get                Get current position',
            '  node {2} position set X Y Z          Set current position',
            '  node {2} execute <command> [args...] Execute a command on node',
        )).format(sys.argv[0], self.sid, self.nid))

    def do_position(self, action, x=0, y=0, z=0):
        if action == 'get':
            print('{0[0]}, {0[1]}, {0[2]}'.format(self.node.position))
        elif action == 'set':
            self.node.position = (x, y, z)
        else:
            print('Error: Invalid action "{}".  [get|set]'.format(action))
            return 1

    def do_execute(self, *args):
        out = self.node.execute(args)
        print(out['output'])
        return out['status']

class Link(Cli):
    def __init__(self, sid):
        self.sid = sid

    def do_help(self, *args):
        print('\n'.join((
            'Usage: {} session {} link COMMAND',
            '  link help                   This help',
            '  link list                   List all links',
            '  link new <a> <b>            Create a link between two nodes',
            '  link del <lid>              Destroy a link',
        )).format(sys.argv[0], self.sid))

def main(argv):
    return Cli().run(*argv[1:])

if __name__ == '__main__':
    sys.exit(main(sys.argv))
