Subuser repositories
====================

Subuser repositories are used to package and distribute subuser image sources. Subuser repositories can be created by software developers wishing to distribute their software to users of subuser. They may also be created by third parties wishing to aid in the distribution of softare. Or even users, wishing to ease the instalation or isolation of software.

Subuser repositories reside within git repositories.

Typically, in a subuser repository, there is one subdirectory per subuser image source. These subdirectories reside at the ``subuser-repository-root`` which is the root of the git repository by default. Subuser will automatically build a list of image sources in the repository simply by looking through ``subuser-repository-root`` for folders which match the image source directory format. It is also possible to give subuser an explicit list of image sources in the repository by setting ``explicit-image-sources`` in the repositories configuration file. This is usefull when one cannot match the standard image source directory format due to restrictions caused by an existing git repositories layout.

Image source directories
------------------------

Each image source directory contains a :doc:`permissions.json <permissions-dot-json-file-format>` file.

It also contains a ``image`` directory (previously, this directory was named ``docker-image`` that name is now deprecated).

The ``image`` directory contains files required to build subuser images:
 A) If the ``image`` directory contains a ``SubuserImagefile``, then the image will be built from the ``SubuserImagefile``. The format for ``SubuserImagefile`` s is the same as the format for `Dockerfile <http://docs.docker.com/reference/builder/>`_ s with the addition of one command:  ``FROM-SUBUSER-IMAGE``.  The ``FROM-SUBUSER-IMAGE`` command takes as it's argument a subuser image source identifier. The build context for the ``SubuserImageFile`` is the ``image`` directory.

The ``.subuser.json`` file
--------------------------

Any git repository which contains a subuser repositry may contain a ``.subuser.json`` file. This file resides at the root of the git repository. A ``.subuser.json`` file is a valid JSON file consisting of a single JSON object. This object may have the following properties:

 * ``image-sources-dir``: A relative path to the directory where the subuser image source directories are stored. This is usefull if the repository is already a git repository being used for a project related to the packaged image sources.

 * ``explicit-image-sources``: A dictionary of explicitly defined image sources. This is useful when you have a git repository for an application and you would like to package that application with subuser. You can explicitly set the entire repository as the image build context. This dictionary maps image source names to a JSON objects with the following values:

   - ``image-file``: Path to the image file used to build the image.

     Ex: ``./subuser/Dockerfile``
   - ``build-context``: The image build context that will be used when building the subuser.
     Ex: ``./``

   - ``permissions-file``: The path to the image's ``permissions.json`` file.

     Ex: ``./subuser/permissions.json``

 Here is an example ``explicit-image-sources`` object that one might find in the source directory for the FreeCAD cad application::

    {"explicit-image-sources":
      {"freecad":{"image-file":"./subuser/SubuserImagefile"
                 ,"build-context":"./"
                 ,"permissions-file":"./subuser/permissions.json"}}}

   - ``subuser-version-constraints``: This is a list of lists mapping subuser versions to the repositories git commits/branches. Each sublist has three elements: a comparison operator, a version, and a git commit or branch. The list is processed from start to end. The first mapping which applies to the current subuser version is used. Therefore, order of this list is significant.

   When reading ``.subuser.json`` subuser first reads the ``.subuser.json`` file found at ``master`` and subsiquently interacts with the proper branch or commit based on the ``subuser-version-constraints``. After the switch, it re-reads ``.subuser.json``.

   Example::

    {"subuser-version-constraints":
      [[">=","0.7","latest"]
      ,[">=","0.6","subuser-0.6"]
      ,["<","0.6","35d670fc80a11d3029a049f754c99969b9477b09"]]}

   In this example, versions of subuser from ``0.7`` onward will use ``latest``. Between 0.6 and 0.7 the ``subuser-0.6`` branch will be used. Earlier versions of subuser will use the specified commit. The default is master and subuser versions before 0.4 do not read ``subuser-version-constraints``, so in reality, in this example subuser versions up till ``0.4`` will use the ``master`` branch.

   The version comparison operators are: ``<``, ``<=``, ``==``, ``>=``, and ``>``.
