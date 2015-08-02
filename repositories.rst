Subuser repositories
====================

Subuser repositories are used to package and distribute subuser image sources. Subuser repositories can be created by software developers wishing to distribute their software to users of subuser. They may also be created by third parties wishing to aid in the distribution of softare. Or even users, wishing to ease the instalation or isolation of software.

Subuser repositories reside within git repositories.

In a subuser repository, there is one subdirectory per subuser image source. These subdirectories reside at the ``subuser-repository-root`` which is the root of the git repository by default.

Image source directories
------------------------

Each image source directory contains a :doc:`permissions.json <permissions-dot-json-file-format>` file.

It also contains a ``docker-image`` directory.

The ``docker-image`` directory contains files required to build subuser images:
 A) If the ``docker-image`` directory contains a ``SubuserImagefile``, then the image will be built from the ``SubuserImagefile``. The format for ``SubuserImagefile`` s is the same as the format for `Dockerfile <http://docs.docker.com/reference/builder/>`_ s with the addition of one command:  ``FROM-SUBUSER-IMAGE``.  The ``FROM-SUBUSER-IMAGE`` command takes as it's argument a subuser image source identifier. The build context for the ``SubuserImageFile`` is the ``docker-image`` directory.

The ``.subuser.json`` file
--------------------------

Any git repository which contains a subuser repositry may contain a ``.subuser.json`` file. This file resides at the root of the git repository. A ``.subuser.json`` file is a valid JSON file consisting of a single JSON object. This object may have the following properties:

 * ``subuser-repository-root``: The root of the subuser repository. A relative path to the directory where the subuser image source directories are stored.

