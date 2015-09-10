Installing subuser
=====================

System Requirements
--------------------

 * `Docker <http://www.docker.io/gettingstarted/#h_installation>`_ 1.3 or higher

 * Python >= 2.7

 * Git

 * X11 and the xauth utility (You almost certainly have this)

Install with pip: Stable version
--------------------------------

1. Add yourself to the docker group.

.. note:: Being a member of the ``docker`` group is equivalent to having root access.

::

   $ sudo nano /etc/group

Find ``docker`` and add your username to the end of the line.

2. Install subuser from pip.

  $ sudo pip install subuser

3. Add ``~/.subuser/bin`` to your path by adding the line ``PATH=$HOME/.subuser/bin:$PATH`` to the end of your ``.bashrc`` file.

4. Log out and then back in again.

5. Done!

Install from git: Development version
-------------------------------------

1. Add yourself to the docker group.

.. note:: Being a member of the ``docker`` group is equivalent to having root access.

::

   $ sudo nano /etc/group

Find ``docker`` and add your username to the end of the line.

2. Download the subuser repository
  ::

  $ cd
  $ git clone https://github.com/subuser-security/subuser

3. Add ``subuser/logic`` and ``~/.subuser/bin`` to your path by adding the line ``PATH=$HOME/subuser/logic:$HOME/.subuser/bin:$PATH`` to the end of your ``.bashrc`` file.

.. note:: You will need to change the path to ``subuser/logic`` to refer to the location to which you downloaded subuser.

4. Log out and then back in again.

5. Done!
