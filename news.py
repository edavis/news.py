"""
news.py -- NNTP for humans

requirements:

testing requirements:
- py.test==2.3.4
"""

import os
import nntplib

import utils

NNTP_PORT = 119

class Server(object):
    def __init__(self, host=None, port=NNTP_PORT, user=None, password=None):
        if host is None:
            host = os.environ.get("NNTPSERVER")
        self._server = nntplib.NNTP(host, port, user, password)

    @property
    def welcome_message(self):
        return self._server.getwelcome()

    def new_groups(self, since):
        """Return an iterator of all new groups added since `since`.
        """
        (date, time) = utils.split_timestamp(since)
        response, groups = self._server.newgroups(date, time)
        return iter(groups)

    def quit(self):
        return self._server.quit()

class Group(object):
    pass

class Article(object):
    pass
