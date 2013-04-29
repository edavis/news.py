API documentation
=================

.. py:currentmodule:: news

.. class:: Server([host[, port=119[, user=None[, password=None]]]])

   An NNTP server.

   :param host: Hostname of the NNTP server. If not supplied,
     the :envvar:`NNTPSERVER` environment variable is used instead.
   :param port: Port of the NNTP server. Defaults to 119.
   :param user: Username to authenticate with.
   :param password: Password to authenticate with.

   Keeping your credentials in :file:`~/.netrc` also works. Just
   leave user/password blank.

   .. method:: list([wildmat=None[, keyword='ACTIVE']])

      Send a LIST_ command.

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

   .. method:: newgroups(since)

      Send a NEWGROUPS_ command.

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

   .. method:: group(name)

      Send a `GROUP`_ command.

      Returns a :class:`Group` object::

          >>> group = server.group("comp.lang.python")

      Also sets the given group as :attr:`the current one <current_group>`.

      .. _GROUP: http://tools.ietf.org/html/rfc3977#section-6.1.1

   .. automethod:: quit

   Each server instance also has the following attributes:

   .. attribute:: last_response

      Contains the last response returned from the server.

   .. autoattribute:: welcome_message

   .. attribute:: current_group

      Contains the currently selected :class:`Group` for this
      connection.

.. class:: Group

   Represents a newsgroup on a given NNTP server.

   Obtain by calling :meth:`~Server.group` on a server object::

       >>> group = server.group("comp.lang.python")

   Here's how to obtain article headers and/or bodies:

   .. method:: head(num_or_msgid)

      Get an article's headers.

      :param str num_or_msgid: An article number or Message-ID.

      This method returns an :class:`Article` object with a
      :attr:`~Article.headers` attribute that contains the requested
      article's headers.

      To view all headers, pass the attribute through :func:`dict`:

          >>> article = group.head('506577')
          >>> dict(article.headers)
          {'Complaints-To': 'groups-abuse@google.com',
           'Content-Type': 'text/plain; charset=ISO-8859-1',
           'Date': 'Sun, 28 Apr 2013 16:40:02 -0700 (PDT)',
           'In-Reply-To': '<7df67006-2176-42cb-a8ce-95a72339e7e2@googlegroups.com>',
           'Newsgroups': 'comp.lang.python',
           'Message-ID': '<979db8bf-4d5c-4c7f-8a05-cfade946026f@googlegroups.com>',
           'References': '<7df67006-2176-42cb-a8ce-95a72339e7e2@googlegroups.com>',
           'Subject': 'Re: Unwanted window spawns when using Tkinter with multiprocessing.',
           'User-Agent': 'G2/1.0'}
          >>> article.headers['date']
          'Sun, 28 Apr 2013 16:40:02 -0700 (PDT)'

      The :attr:`~Article.headers` attribute is an instance of
      :class:`email.parser.Parser`.

      Searching by keys is case-insensitive.

   .. method:: body(num_or_msgid)

      Get an article's body.

      :param str num_or_msgid: An article number or Message-ID.

      This method returns an :class:`Article` object with a
      :attr:`~Article.body` attribute that contains the requested
      article's body as a string::

          >>> article = group.body('<979db8bf-4d5c-4c7f-8a05-cfade946026f@googlegroups.com>')
          >>> article.body[:100]
          'On 04/28/2013 07:40 PM, changed.email@rocketmail.com wrote:\n> Well I saw this clause on most of the '

   .. method:: article(num_or_msgid)

      Get an entire article (headers + body).

      :param str num_or_msgid: An article number or Message-ID.

      This returns an :class:`Article` object with both the
      :attr:`~Article.headers` and :attr:`~Article.body` attributes
      filled in.

      Use this instead of making separate :meth:`head` and then
      :meth:`body` calls.

   Each group object has the follow attributes:

   .. attribute:: name

      The name of the newsgroup.

   .. attribute:: high, low

      The "high water mark" and "low water mark" of article numbers in the group.

   .. attribute:: count

      The (estimated) number of articles in the group.

   Note that each of the above attributes is a string::

       >>> (group.name, group.high, group.low, group.count)
       ('comp.lang.python', '506576', '369114', '137463')

.. class:: Article

   Represents an article's headers and/or body.

   An Article object is obtained by calling a head/body/article method
   on :class:`Group`.

   .. attribute:: headers

      An :class:`email.parser.Parser` instance of the article's headers.

   .. attribute:: body

      The article's body as a string.

   .. method:: save(filename)

      Save :attr:`body` to the supplied filename.
