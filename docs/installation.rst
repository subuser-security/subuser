Installing subuser
=====================

System Requirements
--------------------

 * Docker 1.3 or higher

 * Python >= 2.7

 * Git

Installation
-------------

1. Install `Docker <http://www.docker.io/gettingstarted/#h_installation). Then [add yourself to the docker group](http://docs.docker.io/en/v0.7.3/use/basics/>`_ and add your user to the ``docker`` group.

.. note:: Being a member of the ``docker`` group is equivalent to having root access.

2. Download the subuser repository
  ::

  $ cd
  $ git clone https://github.com/subuser-security/subuser

3. Add ``subuser/logic`` and ``~/.subuser/bin`` to your path by adding the line ``PATH=$HOME/subuser/logic:$HOME/.subuser/bin:$PATH`` to the end of your ``.bashrc`` file.

.. note:: You will need to change the path to ``subuser/logic`` to refer to the location to which you downloaded subuser.

4. Log out and then back in again.

5. Done!

