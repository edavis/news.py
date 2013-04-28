"""
news.py -- NNTP for humans

requirements:

testing requirements:
- py.test==2.3.4
"""

import os
import nntplib
import collections

import utils

NNTP_PORT = 119

GroupResult = collections.namedtuple("Group", "name, high, low, status")

def make_group_result(groups):
    return map(GroupResult._make, (group.split() for group in groups))

class Server(object):
    def __init__(self, host=None, port=NNTP_PORT, user=None, password=None):
        if host is None:
            host = os.environ.get("NNTPSERVER")
        self._server = nntplib.NNTP(host, port, user, password)
        self.last_response = self.welcome_message
        self.host = host
        self.port = port

    @property
    def welcome_message(self):
        return self._server.getwelcome()

    def newgroups(self, since):
        """Perform a NEWGROUPS command.

        :param since: Get groups created after this timestamp. Can be
        either a datetime, timedelta, or string.

        - If a timedelta, subtract from `utcnow` first.
        - If a datetime, format and return.
        - If a string, return as-is.
        """
        ts = utils.format_timestamp(since)
        self.last_response, groups = self._server.longcmd("NEWGROUPS %s" % ts)
        return make_group_result(groups)

    def list(self, wildmat=None, keyword="ACTIVE"):
        """Perform a LIST command.

        By default, it's a "LIST ACTIVE" command but that can be
        altered by changing the `keyword` param.

        The first argument is a wildmat pattern. It can be left empty.

        To get all groups on the server:

            >>> server.list() # -> LIST ACTIVE
            [Group(name='misc.test', high='3002322', low='3000234', status='y'), ...]

        To get only some groups on the server, pass a wildmat string:

            >>> server.list("tx.*") # -> LIST ACTIVE tx.*
            [Group(name='tx.natives.recovery', high='89', low='56', status='y'), ...]

        (http://tools.ietf.org/html/rfc3977#section-4 has more on this format)

        All standard LIST keywords
        (http://tools.ietf.org/html/rfc3977#section-7.6.2) are
        supported, just pass them in via 'keyword':

            >>> server.list(keyword="OVERVIEW.FMT") # LIST OVERVIEW.FMT
            ['Subject:', 'From:', ..., 'Xref:full']
        """
        cmd = "LIST %s" % keyword
        if wildmat is not None:
            cmd += " " + wildmat
        self.last_response, lines = self._server.longcmd(cmd)

        if wildmat is not None:
            return make_group_result(lines)
        else:
            return [line.strip() for line in lines]

    def __repr__(self):
        return "<Server: '%s:%d'>" % (self.host, self.port)

    def quit(self):
        return self._server.quit()

class Group(object):
    pass

class Article(object):
    pass
