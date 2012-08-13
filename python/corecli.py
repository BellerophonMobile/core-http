#!/usr/bin/env python2
'''
    corecli.py - Command-line tool to manipulate CORE sessions.
    Author: Tom Wambold <tom5760@gmail.com>
'''

import sys

from core import Daemon

class Cli(object):
    @classmethod
    def run(cls, *args):
        try:
            arg = args[0]
        except IndexError:
            arg = 'help'

        try:
            func = getattr(cls, 'do_' + arg)
        except AttributeError:
            print 'Invalid argument "{}"'.format(arg)
            return 1

        return getattr(cls, 'do_' + arg)(*args[1:])

    @staticmethod
    def do_help(*args):
        print '\n'.join((
            'Usage: {} OBJECT',
            'where OBJECT := {{ session | event | help }}',
        )).format(sys.argv[0])

    @staticmethod
    def do_session(*args):
        return Session.run(*args)

class Session(Cli):
    @staticmethod
    def do_help(*args):
        print '\n'.join((
            'Usage: {} session COMMAND',
            '  session help                This help',
            '  session list                List all active sessions',
            '  session new <name> <user>   Create a new session',
            '  session del <id>            Destroys a session',
        )).format(sys.argv[0])

    @staticmethod
    def do_list():
        sessions = Daemon().sessions()
        if len(sessions) == 0:
            print 'No active sessions'
            return

        print '{} active sessions'.format(len(sessions))
        print 'ID\tName\tOwner'
        for session in sessions:
            print '{}\t{}\t{}'.format(session.sid, session.name, session.user)

    @staticmethod
    def do_new(name, user):
        session = Daemon().new_session(name, user)
        print 'ID: {}'.format(session.sid)

    @staticmethod
    def do_del(sid):
        Daemon().get_session(sid).delete()

def main(argv):
    return Cli.run(*argv[1:])

if __name__ == '__main__':
    sys.exit(main(sys.argv))
