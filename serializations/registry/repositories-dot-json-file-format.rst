The repositories.json file format
=================================

In the context of subuser, a ``repositories.json`` file is a file which describes where subuser images may be installed from.

The ``repositories.json`` files are to be arranged into a hierarchy.  Subuser will build the repository list by first looking in the file ``~/.subuser/registry/repositories.json`` then adding an additional ``system repositories`` found in:

 * ``$HOME/.subuser/repositories.json``

 * ``/etc/subuser/repositories.json``

 * ``$SUBUSERDIR/repositories.json``

``$SUBUSERDIR`` is the directory where the subuser source resides.

Each repositories.json file is to be a valid `json <http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf>`_ file containing a single json object.

This object is a set of key value pairs where each key is the name of a subuser repository.

Repository names must not contain any of the following characters: ``\``, ``:`` .

The value is a json object with the following properties:

Properties
-----------

 * ``git-origin``: The URI of the repositories git origin.

 Ex::

    "git-origin" : "https://github.com/subuser-security/subuser-default-repository.git/"

 * ``source-dir``: When maintaining a repository, it is not desireable to have to commit your changes to git before being able to test them out. For this reason, it is possible to have repositories which are not in git, which refer directly to a source directory on your local machine. If ``source-dir`` is specified, than the repository is assumed to be such a development repo and ``git-origin`` is ignored.

 Ex::

    "source-dir" : "/home/timothy/current/subuser-repo"


 * ``temporary`` : Is this a temporary repository?
  .. note:: this property defaults to false and is not mandatory.  In fact it looks cleaner if you don't include it when false ;).

Example repositories.json file
--------------------------------

::

    {
     "default" : {"git-origin" : "https://github.com/subuser-security/subuser-default-repository.git/"}
    }

This file states that there is one repository named ``default`` which was downloaded from ``https://github.com/subuser-security/subuser-default-repository.git/``.

