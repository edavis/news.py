API documentation
=================

.. py:currentmodule:: news

.. autoclass:: Server

   .. automethod:: list

   .. automethod:: newgroups

   .. automethod:: group

   .. automethod:: quit

   Each server instance also has the following attributes:

   .. attribute:: last_response

      Contains the last response returned from the server.

   .. attribute:: welcome_message

      Contains the welcome message returned from the server when you
      first connected.

   .. attribute:: current_group

      Contains the currently selected :class:`Group` for this
      connection.

.. class:: Group

   Represents a newsgroup on a given NNTP server.

   Obtained by calling the :meth:`~Server.group` method on a
   :class:`Server` instance::

       >>> group = server.group("comp.lang.python")

   Each group object has the following attributes:

   .. attribute:: name

      The name of the newsgroup.

   .. attribute:: high, low

      The "high water mark" and "low water mark" of article numbers in the group.

   .. attribute:: count

      The (estimated) number of articles in the group.

   Note that each of the above attributes is a string::

       >>> (group.name, group.high, group.low, group.count)
       ('comp.lang.python', '506576', '369114', '137463')

   You have three choices of how to get article(s) from a given group.

   If you're only interested in the article's **headers**, use:

   .. method:: head(num_or_msgid)

   If you're only interest in the article's **body**, use:

   .. method:: body(num_or_msgid)

   But if you're interesting in both the headers and the body, use:

   .. method:: article(num_or_msgid)

.. class:: Article
