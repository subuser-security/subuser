Special files found within the subuser image
============================================

For the most part, subuser specific files are found in the ``/subuser`` directory within the subuser image.

Files and directories created by subuser
----------------------------------------

``/pwd/``
^^^^^^^^^

This is the directory which is bind-mounted to the $PWD at launch if the ``access-working-directory`` permission has been set.

``/subuser/userdirs``
^^^^^^^^^^^^^^^^^^^^^

This directory contains bind mounts of user directories specified by the ``user-dirs`` permission.

``/subuser/execute``
^^^^^^^^^^^^^^^^^^^^

This directory is bind-mounted to the directory containing the execution spool, in case the ``run-commands-on-host`` permission is set.

Files and directories installed by the image creator
----------------------------------------------------

``/subuser/check-for-updates``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This executable is run each time the user issues ``subuser update all``. If the executable exits with a zero exit code, then the image needs to be updated. This executable is run in a special restricted container which has equivelent permissions to the containers launched by ``docker build``.
