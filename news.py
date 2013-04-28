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

class Server(object):
    def __init__(self, host=None, port=NNTP_PORT, user=None, password=None):
        if host is None:
            host = os.environ.get("NNTPSERVER")
        self._server = nntplib.NNTP(host, port, user, password)
        self.last_response = self.welcome_message

    @property
    def welcome_message(self):
        return self._server.getwelcome()

    def new_groups(self, since):
        """Return an iterator of all new groups added since `since`.
        """
        ts = utils.format_timestamp(since)
        self.last_response, groups = self._server.longcmd("NEWGROUPS %s" % ts)
        return map(GroupResult._make, (group.split() for group in groups))

    def __repr__(self):
        return "<Server: %s:%d>" % (self._server.host, self._server.port)

    def quit(self):
        return self._server.quit()

class Group(object):
    pass

class Article(object):
    pass
