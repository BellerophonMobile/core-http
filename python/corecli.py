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
            '  session ID [...]            Interact with a particular session',
        )).format(sys.argv[0]))

    @staticmethod
    def do_list():
        sessions = Daemon().sessions()
        if len(sessions) == 0:
            print('No active sessions')
            return

        print('{} active sessions'.format(len(sessions)))
        print('ID\tName\tOwner\tState')
        for session in sessions:
            print('{}\t{}\t{}\t{}'.format(session.sid, session.name,
                                          session.user, session.state))

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
        self.session = Daemon().get_session(sid)

    def do_help(self, *args):
        print('\n'.join((
            'Usage: {0} session {1} OBJECT',
            '  session {1} help            This help',
            '  session {1} state <state>   Set the state of this session',
            '  session {1} node            Manipulate nodes of this session',
            '  session {1} link <nid> <nid_a> <ifid_a> Link two nodes together',
        )).format(sys.argv[0], self.session.sid))

    def do_node(self, *args):
        return Node(self.session).run(*args)

    def do_link(self, nid, nid_a, ifid_a):
        self.session.link(nid, nid_a, ifid_a)

    def do_state(self, state):
        self.session.state = state

class Node(Cli):
    def __init__(self, session):
        self.session = session

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
        )).format(sys.argv[0], self.session.sid))

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
        return SelectedNode(self.session, nid).run(*args)

class SelectedNode(Cli):
    def __init__(self, session, nid):
        self.session = session
        self.node = self.session.get_node(nid)

    def do_help(self, *args):
        print('\n'.join((
            'Usage: {0} session {1} node get {2} COMMAND',
            '  node {2} help                          This help',
            '  node {2} info                          List information about node',
            '  node {2} position X Y Z                Set current position',
            '  node {2} netif new <nid> <addr>/<mask> Create a new network interface',
            '  node {2} execute <command> [args...]   Execute a command on node',
            '  node {2} socket <addr> <port>          Open a socket on a node',
        )).format(sys.argv[0], self.session.sid, self.node.nid))

    def do_info(self):
        print('ID:', self.node.nid)
        print('Name:', self.node.name)
        print('Type:', self.node.ntype)
        print('Position: ({}, {}, {})'.format(*self.node.position))
        for iface in self.node.interfaces:
            print('Interface:', iface['ifindex'])
            print('    Name:', iface['name'])
            print('    MTU:', iface['mtu'])
            print('    MAC:', iface['hwaddr'])
            print('    Addresses:')
            for address in iface['addresses']:
                print('       ', address)

    def do_position(self, x=0, y=0, z=0):
        self.node.position = (x, y, z)

    def do_netif(self, action, *args):
        if action == 'new':
            nid, addr = args
            self.node.new_netif(nid, addr)
        else:
            printf('Error: Invalid action "{}". [new]'.format(action))

    def do_execute(self, *args):
        out = self.node.execute(args)
        print(out['output'])
        return out['status']

    def do_socket(self, address, port):
        self.node.socket(address, port, sys.stdin)

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
