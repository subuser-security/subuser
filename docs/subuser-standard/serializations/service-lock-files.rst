Service lock files
==================

The service lock files are a series of JSON format lock files which are kept in the ``services`` subdirectory of the ``lock-dir`` (see ``config.json``). In the ``services`` directory there are subdirectories for each subuser bearing the name of that subuser. It is in these directories that the service lock files reside. The service lock files are named ``<service-name>.json``

Here is an example path:

``<lock-dir>/services/<subuser-name>/<service-name>.json``

In a typical service lock file path might look like:

``/home/timothy/.subuser/locks/iceweasel/xpra.json``

Services
--------

There are a number of service containers which may need to run in order to support the functioning of a subuser. In order to ensure that these service containers are started and stopped correctly, `lock files are needed <https://github.com/subuser-security/subuser/issues/31>`_.

 .. image:: http://timothy.hobbs.cz/subuser-client-service/lock-file.gif

xpra service containers
'''''''''''''''''''''''

`xpra <https://xpra.org>`_ service containers provide a contained X11 server for the subuser to draw windows to. This allows the subuser to display windows without compromising the security of the system.

The ``xpra.json`` lock file contains a JSON object with the following properites:

 * ``client-counter`` is an integer which records the number of currently running containers which are associated with the given subuser and thus require the service to be running as well.

 * ``xpra-server-service-pid`` is the process id of the xpra server process. That is the docker client process which launched the xpra server container.

 * ``xpra-client-service-pid`` is the process id of the xpra client process. That is the docker client process which launched the xpra client container.
