"""
news.py -- NNTP for humans

requirements:

testing requirements:
- py.test==2.3.4
"""

import nntplib

import utils

class Server(object):
    def __init__(self, host, port, user, password):
        self._server = nntplib.NNTP(host, port, user, password)

    @property
    def welcome_message(self):
        return self._server.getwelcome()

    def quit(self):
        return self._server.quit()

class Group(object):
    pass

class Article(object):
    pass
