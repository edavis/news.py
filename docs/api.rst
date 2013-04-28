API documentation
=================

.. py:currentmodule:: news

.. autoclass:: Server

   .. automethod:: list

   .. automethod:: newgroups

   .. automethod:: group

   .. automethod:: quit

   .. attribute:: last_response

      Contains the last response returned from the server.

   .. attribute:: welcome_message

      Contains the welcome message returned from the server when you
      first connected.

   .. attribute:: current_group

      Contains the currently selected :class:`Group` for this
      connection.

.. class:: Group()
