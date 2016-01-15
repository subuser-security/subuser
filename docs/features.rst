Features!
=========

Security features
-----------------

- Secure graphics: Using the :doc:`XPRA X11 bridge working <news/0.3>`, windows are displayed without giving programs unfettered access to X11.

- Editable permissions: If you don't like the permissions a program wants, you can change them! After all, its YOUR computer!

.. image:: ./images/usually_looks_scarier_than_it_is.png

Comic by `Abstruse Goose <http://abstrusegoose.com/>`_.

YOU HAVE THE RIGHT TO EDIT PERMISSIONS!

Other features
--------------

- Git backed subuser registry

   + Rollback changes and lock subusers from being updated: If you update your system and you don't like the result, you can rollback the changes, or you can lock a subuser from ever getting updated so you know it'll never break.
   + With ``subuser registry log`` you can see when what was installed or updated.

- Distributed design: Anyone can create a subuser repository and share their own image sources. The ``subuser pkg`` command helps you create and maintain your repositories.

- Full support for Dockerfiles, so you don't have to learn a new packaging system.
