Installing subuser
=====================

System Requirements
--------------------

 * `Docker <https://docs.docker.com/engine/installation/linux/>`_ 1.3 or higher

 * Python >= 3

 * Git

 * X11 and the xauth utility (You almost certainly have this)

 * sudo (if you don't want to become a member of the docker group)

Installation: Common steps
--------------------------

#. Add yourself to the ``sudo`` group (Note: if you are a member of the ``docker`` group this is not needed.).

::

   $ sudo usermod -a -G sudo $USER

Install from your distributions package manager
-----------------------------------------------

 * `Arch linux AUR <https://aur.archlinux.org/packages/subuser/>`_
 * `Debian sid <https://packages.debian.org/unstable/main/subuser>`_
 * `Ubuntu <https://launchpad.net/ubuntu/+source/subuser>`_
 * `pipy <https://pypi.python.org/pypi/subuser>`_

Install with pip: Stable version
--------------------------------

#. Install subuser from ``pip3``::

   $ sudo pip3 install subuser

#. Add ``~/.subuser/bin`` to your path by adding the line ``PATH=$HOME/.subuser/bin:$PATH`` to the end of your ``~/.bashrc`` file.

#. Log out and then back in again.

#. Done!

Install from git: Development version
-------------------------------------

#. Download the subuser repository::

   $ cd
   $ git clone https://github.com/subuser-security/subuser

#. Add ``subuser/logic`` and ``~/.subuser/bin`` to your path by adding the line ``PATH=$HOME/subuser/logic:$HOME/.subuser/bin:$PATH`` to the end of your ``.bashrc`` file.

#. **Optional:** Subuser can run in place. If you want to install the development version system wide you can do so with.

    sudo python3 setup.py install

.. note:: You will need to change the path to ``subuser/logic`` to refer to the location to which you downloaded subuser.

#. Log out and then back in again.

#. Done!

Source
------

The subuser sourcecode is maintained on `github <https://github.com/subuser-security>`_. You can find release tarbals `here <http://subuser.org/rel/>`_.

