Subuser repositories
====================

Subuser repositories are git repositories.  Directories within subuser repositories represent subuser image sources. Each of these directories contains a :doc:`permissions.json permissions-dot-json-file-format` file.

It also contains a ``docker-image`` directory.

The ``docker-image`` directory contains files required to build subuser images.  If the ``docker-image`` directory contains a ``SubuserImagefile``, then the image will be built from the ``SubuserImagefile``.  The format for ``SubuserImagefile`` s is the same as the format for `Dockerfile <http://docs.docker.com/reference/builder/>`_ s with the addition of one command:  ``FROM-SUBUSER-IMAGE``.  The ``FROM-SUBUSER-IMAGE`` command takes as it's argument a subuser image source identifier.


