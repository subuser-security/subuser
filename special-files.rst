Special files found within the subuser image
============================================

``/subuser/check-for-updates``
--------------------------------

This executable is run each time the user issues ``subuser update all``. If the executable exits with a zero exit code, then the image needs to be updated. This executable is run in a special restricted container which has equivelent permissions to the containers launched by ``docker build``.

