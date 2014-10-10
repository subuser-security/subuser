Using subuser - a quick tutorial
=============

Installing a program with subuser
---------------------------------

You can see a list of installable programs (also refered to as images) by doing::

  $ subuser list available

You can install one of these images by adding a subuser for it:

::

  $ subuser subuser add vim vim@default

This adds a new subuser named vim based on the image vim from the default repository.

Running subusers
----------------

You can run the subuser with::

  $ subuser run vim SomeTextFileToEdit

You don't have to type ``subuser run`` every time you launch a program
--------------------------

You can turn a subuser into a "normal" program by running::

  $ subuser subuser create-shortcut vim

Now you can launch vim with::

  $ vim SomeTextFileToEdit

Updating programs
------------------

You can update your subuser programs with::

  $ subuser update all


Removing subusers
-----------------

To remove the subuser named vim you can run::

  $ subuser subuser remove vim

To remove vim's home dir::

  $ rm -rf ~/.subuser/homes/vim

To clean up old images which have been installed, but no longer are used by any subuser::

  $ subuser remove-old-images
