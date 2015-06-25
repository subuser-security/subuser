The config.json file format
===========================

In the context of subuser, a ``config.json`` file is a file with subuser settings.

The ``config.json`` files are to be arranged into a fallback-hierarchy.  Subuser will first look up properties in the file ``~/.subuser/config.json`` falling back to:

 * ``/etc/subuser/config.json``

 * ``$SUBUSERDIR/config.json``

Each config file may be partial.  That is, if the user wants to specify some options, but leave others as their default values, they can simply ommit those options that they do not wish to change.

``$SUBUSERDIR`` is the directory where the subuser source resides.  It corresponds to the root of this git repository.

Each config.json file is to be a valid `json <http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf>`_ file containing a single json object.

Properties
-----------
The defaults settings for these properties may be found in ``$SUBUSERDIR/config.json``.

**Note on paths**: Each path is to be absolute.  Any environment variables of the form ``$VARIABLE_NAME`` will be expanded.

 * ``bin-dir``: This is the directory where subuser "executables" are to be installed.  This directory should be in the user's path.

  ``type``: string - path to directory

 * ``registry-dir`` : This is the path to the git repository where the registry files for subusers and installed images are stored.

  ``type``: string - path to git repository

 * ``repositories-dir`` : This is the path to the directory where subuser repositories are stored.

  ``type``: string - path to git repository

 * ``user-set-permissions-dir``:

  ``type``: string - path to directory

 * ``installed-images-list``: path of installed-images.json file

  ``type``: string - path to json file

 * ``runtime-cache``: path of the runtime-cache directory

  ``type``: string - path to a directory

 * ``locked-subusers-path``: path to locked-subusers.json file.

  ``type``: path to json file.

 * ``subuser-home-dirs-dir``: The directory where subuser is to store the home directories of each subuser.

  ``type``: string - path to directory

 * ``lock-dir``: Path to directory which contains lock files. (Currently, the only lock fike is the ``registry.lock`` file which is present when a subuser process is modifying the registry.

  ``type``: string - path to directory

