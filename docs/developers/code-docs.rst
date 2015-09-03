Implementation details
======================

It has become abundantly clear, that with enough eyes on the code, all bugs are deep.  Typos and off by one errors will be fixed by people casually browsing the code base, but deeper structural problems will remain. Few read the entire source and fewer still understand its structure.  Over time, these problems worsen as contributors unfamiliar with the code base bolt features on to the side with little planning or understanding.  It is for this reason that I have chosen to document subuser's architecture and I kindly request that you skim over this documentation before getting out the ducktape.

Basic file layout
-----------------

The subuser source is stored in the `logic <https://github.com/subuser-security/subuser/tree/master/logic>`_ directory.

 * `logic/subuser <https://github.com/subuser-security/subuser/blob/master/logic/subuser>`_ - This is the main subuser executable.

 * `logic/subuserCommands <https://github.com/subuser-security/subuser/tree/master/logic/subuserCommands>`_ - This is where individual built in subuser cli utilities/subcommands are found.

 * `logic/subuserlib <https://github.com/subuser-security/subuser/tree/master/logic/subuserlib>`_ - The source files found in this directory are a mixture of sparse utility functions and major functions which touch multiple classes and data structures.

 * `logic/subuserlib/classes <https://github.com/subuser-security/subuser/tree/master/logic/subuserlib/classes>`_ - This is where subuser class modules are stored.

Execution model
---------------

When you run subuser, a ``subuser`` executable is called which immediately passes execution on to a subuser command. Any executable found in the directory `logic/subuserCommands <https://github.com/subuser-security/subuser/tree/master/logic/subuserCommands>`_ is a subuser command. Any executable which is in the system path and starts with the string ``subuser-`` is also a subuser command. This makes it easy to add new subuser commands to the subuser cli. This model was taken from git.



Class structure
---------------

Subuser is written in Python with an object oriented architecture.  The main data structure in subuser is a tree of objects.  The base object is a ``subuserlib.classes.user.User`` object.

.. image:: images/object-hierarchy.png

.. toctree::

  code-docs/user
  code-docs/helperModules

