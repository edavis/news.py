"""
news.py -- NNTP for humans

requirements:

testing requirements:
- py.test==2.3.4
"""

import os
import nntplib
import collections
from email.parser import HeaderParser

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
        self.current_group = None

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

    def group(self, name):
        """Send a GROUP command.

        Selects the active group.
        """
        self.last_response = self._server.shortcmd("GROUP %s" % name)
        (_, count, low, high, name) = self.last_response.split()

        stats = {"low": low, "high": high, "count": count}
        self.current_group = Group(name, self, stats)
        return self.current_group

    def __repr__(self):
        return "<Server: '%s:%d'>" % (self.host, self.port)

    def quit(self):
        """Send a QUIT command."""
        return self._server.quit()

class Group(object):
    def __init__(self, name, server, stats):
        self.name = name
        self.server = server
        self._server = server._server

        self.high = stats['high']
        self.low = stats['low']
        self.count = stats['count']

    def _get(self, cmd, msg_id):
        response, results = self._server.longcmd("%s %s" % (cmd, str(msg_id)))
        self.server.last_response = response
        if cmd == "HEAD":
            return Article(headers=results)
        elif cmd == "BODY":
            return Article(body=results)

    def head(self, msg_id):
        return self._get("HEAD", msg_id)

    def body(self, msg_id):
        return self._get("BODY", msg_id)

    def article(self, msg_id):
        response, result = self._server.longcmd("ARTICLE %s" % str(msg_id))
        combined = "\n".join(result)
        (headers, body) = combined.split("\n\n", 1)
        return Article(headers, body.lstrip())

    def __repr__(self):
        return "<Group: '%s' (on %s:%d)>" % (self.name, self.server.host,
                                             self.server.port)

class Article(object):
    def __init__(self, headers=None, body=None):
        self.headers = headers
        self.body = body

        if headers is not None:
            parser = HeaderParser()
            headers = self._join_if_needed(headers)
            self.headers = parser.parsestr(headers, headersonly=True)

        if body is not None:
            self.body = self._join_if_needed(body)

    def _join_if_needed(self, content):
        """Normalize how we handle headers/body.

        - HEAD and BODY return lists of strings so we newline join them.
        - ARTICLE is already joined by newlines, so return as-is.
        """
        if isinstance(content, list):
            return "\n".join(content)
        elif isinstance(content, basestring):
            return content

    def save(self, fname):
        """Save the article's body to fname."""
        assert self.body is not None, "no body, not writing"
        with open(os.path.expanduser(fname), "wb") as fp:
            fp.write(self.body)

    def __repr__(self):
        return "<Article: '%s'>" % self.headers['message-id']
