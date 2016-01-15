The permissions.json file format
================================

A permissions.json file is a file which describes the rights or permissions of a given subuser.  These permissions pertain mainly to that image's ability to interact with it's host operating system.

Each permissions.json file is to be a valid `json <http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf>`_ file containing a single json object.

Prelude
-------

The permissions object always begins with the following permissions:

 * ``description``: This field describes what the subuser is/what it does.

  Ex::

    "description"                : "Simple universal text editor."

 * ``maintainer``: This field marks who is responsible for the ``permissions.json`` file, and accompanying ``Dockerfile``.  It does NOT mark who is responsible for the image itself.

  Ex::

    ,"maintainer"                : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"

 * ``executable``: This field denotes the absolute path within the Docker image where the given image's executable resides. This value is optional. if it is not present, than the subuser image cannot be run (but may be depended upon by other subuser images).

  Ex::

    ,"executable"                : "/usr/bin/vim"

  **Default**: The image has no executable and cannot be run(but it can be depended upon, as a library).

 * ``entry-points``: This optional feild allows you to add "entry-points" to your subuser. These are executables that can be added, if the user so wishes, to the PATH on the host system. This is a dictionary which maps "desired name on host" to "path within subuser image".

  Ex::

    ,"entry-points"                : {"mk":"/usr/bin/mk","cc","/usr/local/bin/cc"}

  **Default**: There are no entry points.

Permissions
-----------

All permissions are optional. If they are not included in the ``permissions.json`` file, than they are set to their default (and most restrictive) setting.

Setting a permission to an empty string is not a valid way of requesting it's default value.  If you want the default value, don't include the permission at all.

Permissions are categorized into 4 levels of permissiveness:

 1. conservative: These permissions should be 100% safe in all cases.
 2. moderate: These permissions have the potential to give the subuser access to some user data but not all.
 3. liberal: These permissions give the subuser access to some or all user data, and/or present a significantly increased risk of the subuser breaking out of the container.
 4. anarchistic: These permissions give the subuser full access to the system.

Conservative permissions
------------------------

 * ``basic-common-permissions``: This flag allows you to enable a set of basic, safe, and common permissions without having to list them individualy.  The basic common permissions are:

  - ``stateful-home``
  - ``inherit-locale``
  - ``inherit-timezone``

  If any of the basic common permissions are also set, their value over-rides this value.  For example, if ``stateful-home`` is explicitly set to ``false`` but ``basic-common-permissions`` is set to ``true``, ``stateful-home`` is ``false``.

 * ``stateful-home``: Changes that the subuser makes to it's home directory should be saved to a special subuser-homes directory.

  **Default**: ``false``

 * ``inherit-locale``: Automatically set the $LANG and $LANGUAGE environment variable in the container to the value outside of the container. Note: You do not have to set this if you have set ``basic-common-permissions``.

  **Default**: ``false``

 * ``inherit-timezone``: Automatically set the $TZ environment variable in the container to the value outside of the container.  Give the sub user read only access to the ``/etc/localtime`` file. Note: You do not have to set this if you have set ``basic-common-permissions``.

  **Default**: ``false``

Moderate permissions
--------------------

 * ``gui``: Is the subuser allowed to display a graphical user interface?  This permission has the following sub-permissions:

  - ``clipboard``: Is the subuser allowed to read and write to the clipboard?
  - ``system-tray``: Is this subuser allowed to display system-tray icons?
  - ``cursors``: Is this subuser allowed to change the way the mouse cursor is displayed?

  All sub-permissions are boolean and default to false.

  Ex::

    ,"gui" : {"system-tray":true,"clipboard":true}

  This example allows the subuser to display windows, display system-tray icons, and access the clipboard.  However, it cannot change the mouses cursor.

  Ex::

    ,"gui" : {}

  This example allows the subuser to display windows.

 * ``user-dirs``: A list of relative paths to user directories which are to be shared between the host and the given image. The subuser is given read-write access to any user directories listed.

  Ex::

     ,"user-dirs"                 : ["Downloads"]

  In this example, the subuser is able to access the ``~/Downloads`` directory on the host by visiting the ``~/Userdirs/Downloads`` directory within the container.


  **Default**: ``[]``

 * ``inherit-envvars``: A list of environment variables which the image will inherit from the host environment when started.

  Ex::

     ,"inherit-envvars"           : ["PGUSER","PGHOST"]

  **Default**: ``[]``

 * ``sound-card``:  The subuser is allowed to access the soundcard on the host.

  .. warning:: This means, not only can the subuser play sounds, but it may listen to your microphone too!

  **Default**: ``false``

 * ``webcam``: The subuser is allowed to access the computer's webcam/USB webcams.

  **Default**: ``false``

 * ``access-working-directory``: The subuser is given read-write access to the host user's current working directory.

  **Default**: ``false``

 * ``allow-network-access``: Should the subuser be allowed to access the network/internet?

  **Default**: ``false``

Liberal permissions
-------------------

 * ``x11``: The subuser is allowed to interact with the x11 server on the host.

  .. note:: Known to be insecure!

  **Default**: ``false``

 * ``system-dirs``: A dictionary of absolute paths to directories which are to be shared between the host and the given image. The subuser is given read-write access to any user directories listed.

  Ex::

     ,"system-dirs"                 : {"/var/log":"/host/var/log"}

  In this example, the subuser is able to access the ``/var/log`` directory on the host by visiting the ``/host/var/log`` directory within the container.

 * ``graphics-card``: The subuser is allowed to access the graphics-card directly(OpenGL).

  **Default**: ``false``

 * ``serial-devices``: The subuser is allowed to access serial devices: ``/dev/ttyACM*``, ``/dev/ttyUSB*``, and ``/dev/ttyS*``.

  **Default**: ``false``

 * ``system-dbus``: Should the subuser be allowed to communicate with the system wide dbus daemon?

  **Default**: ``false``

 * ``as-root``: Run the subuser as the root user within the container.

  **Default**: ``false``

 * ``sudo``: Grant the subuser sudo privileges within the container.

  **Default**: ``false``


Anarchistic permissions
-----------------------

 * ``privileged``: Should the subuser's Docker container be run in ``privileged`` mode?

  .. warning:: Completely insecure!

  **Default**: ``false``

 * ``run-commands-on-host``: Should the subuser be able to execute commands as the normal user on the host system? If this is enabled, a ``/subuser/execute`` file will be present in the container. Any text appended to this file will be piped to ``/bin/sh`` on the host machine.

  .. warning:: Obviously completely compromises security.

  **Default**: ``false``

Depricated
----------------------

 * ``last-update-time``: This field records the last time the image, or it's ``Dockerfile`` were known to be updated.  The purpose of this field is telling ``subuser`` if a image has been updated and must be re-installed.  It is important that this string be comparable with python's built in string comparison algorithm.

  Ex::

    ,"last-update-time"          : "2014-02-12-12:59"
