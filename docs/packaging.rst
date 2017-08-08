Packaging programs to run with subuser
======================================

Subuser allows anyone to create and share repositories of subuser images.  This allows anyone to become a packager and maintainer of subuser images.  There is no need for any bureaucracy, the process is entirely distributed.

Packaging programs for use with subuser is much simpler than packaging for say, Debian.  Furthermore, if your program is already packaged for a linux distribution then almost all of your work is already done.

A subuser repository is a git repository.  Repositories have the following file structure::

  image-name/
    image/
      SubuserImagefile
      docker-build-context...
    permissions.json

Quick packaging tutorial
------------------------

1. Create a directory for your own personal subuser repository:

::
  
  $ mkdir my-subuser-programs
  $ cd my-subuser-programs
  $ subuser pkg init
  
2. Add subuser images:

::

   $ subuser pkg add xterm # You will be prompted to edit the new image sources permissions and build files.

3. Install your new subuser image:

::

   $ subuser subuser add xterm xterm@./

4. Publish your subuser repository:

::

  $ git init
  $ git add .
  $ git commit
  $ git remote add origin <url>
  $ git push origin master

5. If you publish your new git repository to a website such as `Gitlab <https://gitlab.com>`_, `Bitbucket <https://bitbucket.org>`_, or `Github <https://github.com>`_, others will be able to install your images with a command similar to the one bellow.

::

  $ subuser subuser add subuser-name my-subuser-image@https://github.com/timthelion/my-subuser-programs.git

Creating a `permissions.json` file
----------------------------------

Here is an example::

  {
    "description"                : "Simple universal text editor."
    ,"maintainer"                : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"
    ,"executable"                : "/usr/bin/vim"
    ,"access-working-directory"  : true
    ,"basic-common-permissions"  : true
  }

**Note**: Listing every permission is not necessary. When a permission is not listed, it is denied by default.

You can find a full specification for the `permissions.json` file format :doc:`here <subuser-standard/permissions-dot-json-file-format>`.

Creating a `SubuserImagefile`
-----------------------------

Create a directory called `image` and add a `SubuserImagefile` to that directory. This is a very similar format to that of the Dockerfile.

The only difference is the addition of a special `FROM-SUBUSER-IMAGE` command which takes :doc:`the identifier of a subuser image source <subuser-standard/image-source-identifiers>` as it's argument. For information on creating a Dockerfile, please see the `official documentation for writing Dockerfiles <https://docs.docker.com/reference/builder/>`_.

Example `SubuserImagefile`::

  FROM debian
  RUN apt-get update && apt-get install -yyq vim

Example 2::

  FROM-SUBUSER-IMAGE libx11@default
  RUN apt-get update && apt-get install -yyq iceweasel

Example 3::

  FROM debian
  RUN apt-get update && apt-get install -yyq iceweasel

.. note :: Examples 2 and 3 do the **SAME** thing, it's just that Example 3 takes a little longer to build and uses more space on disk.  There is **no magic** in the ``libx11`` image and never will be(we hope).

