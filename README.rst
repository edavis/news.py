news.py -- NNTP for humans
==========================

A modern Python library for working with NNTP_:

.. _NNTP: http://en.wikipedia.org/wiki/Network_News_Transfer_Protocol

.. code-block:: python

   >>> import news
   >>> server = news.Server("news.gmane.org")
   >>> py = server.group("gmane.comp.python.general")
   >>> latest = py.article(py.high)

   >>> latest.headers['subject']
   'Re: Unwanted window spawns when using Tkinter with multiprocessing.']
   >>> latest.headers['date']
   'Sun, 28 Apr 2013 20:24:22 -0400'
   >>> latest.body[:100]
   'On 04/28/2013 07:40 PM, hidden@rocketmail.com wrote:\n> Well I saw this clause on most of the '
