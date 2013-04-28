"""
news.py -- NNTP for humans
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
    """Represents a given NNTP server.

    :param host: Hostname of the NNTP server. If not supplied,
      the :envvar:`NNTPSERVER` environment variable is used instead.
    :param port: Port of the NNTP server. Defaults to 119.
    :param user: Username to authenticate with.
    :param password: Password to authenticate with.

    Keeping your credentials in :file:`~/.netrc` also works. Just
    leave user/password blank.
    """
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
        """Welcome message returned after first connecting to the server.
        """
        return self._server.getwelcome()

    def newgroups(self, since):
        """Send a `NEWGROUPS`_ command.

        Returns a list of newsgroups created on the server since
        ``since`` timestamp.

        ``since`` can be a :class:`~datetime.datetime`,
        :class:`~datetime.timedelta`, or :func:`str`. If it's a
        :class:`~datetime.timedelta`, it is subtracted from
        :meth:`datetime.datetime.utcnow` first.

        For example::

            >>> from datetime import datetime, timedelta

            >>> server.newgroups(datetime(2012, 12, 01))
            [Group(name='misc.test', high='3002322', low='3000234', status='y'), ...]

            >>> server.newgroups(timedelta(days=120))
            [Group(name='misc.test', high='3002322', low='3000234', status='y'), ...]

            >>> server.newgroups('121201 000000')
            [Group(name='misc.test', high='3002322', low='3000234', status='y'), ...]

        ``Group`` is the same :func:`~collections.namedtuple` as
        returned in :meth:`list`.

        .. _NEWGROUPS: http://tools.ietf.org/html/rfc3977#section-7.3

        """
        ts = utils.format_timestamp(since)
        self.last_response, groups = self._server.longcmd("NEWGROUPS %s" % ts)
        return make_group_result(groups)

    def list(self, wildmat=None, keyword="ACTIVE"):
        """Send a `LIST`_ command.

        :param str wildmat: A `wildmat pattern`_.
        :param str keyword: A `list keyword`_.

        The most common use of LIST is to retrieve a list of
        newsgroups::

            >>> server.list()
            [Group(name='misc.test', high='3002322', low='3000234', status='y'), ...]

        To retrieve only some groups, provide a `wildmat pattern`_::

            >>> server.list("tx.*")
            [Group(name='tx.natives.recovery', high='89', low='56', status='y'), ...]

        ``Group`` is a :func:`~collections.namedtuple` with the
        attributes defined `here
        <http://tools.ietf.org/html/rfc3977#section-6.1.1.1>`_ (under
        "parameters").

        LIST is also able to supply other kinds of information. All
        you have to do is supply a valid `list keyword`_::

            >>> server.list(keyword="OVERVIEW.FMT")
            ['Subject:', 'From:', ..., 'Xref:full']

        .. _LIST:              http://tools.ietf.org/html/rfc3977#section-7.6
        .. _`wildmat pattern`: http://tools.ietf.org/html/rfc3977#section-4
        .. _`list keywords`:
        .. _`list keyword`:    http://tools.ietf.org/html/rfc3977#section-7.6.2
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
        """Send a `GROUP`_ command.

        Returns a :class:`Group` object::

            >>> group = server.group("comp.lang.python")

        Also sets the given group as :attr:`the current one <current_group>`.

        .. _GROUP: http://tools.ietf.org/html/rfc3977#section-6.1.1
        """
        self.last_response = self._server.shortcmd("GROUP %s" % name)
        (_, count, low, high, name) = self.last_response.split()

        stats = {"low": low, "high": high, "count": count}
        self.current_group = Group(name, self, stats)
        return self.current_group

    def __repr__(self):
        return "<Server: '%s:%d'>" % (self.host, self.port)

    def quit(self):
        """Send a `QUIT`_ command.

        Closes the server connection.

        .. _QUIT: http://tools.ietf.org/html/rfc3977#section-5.4
        """
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
