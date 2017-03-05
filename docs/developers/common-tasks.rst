Common coding tasks
===================

Adding a new permission
-----------------------

 1. Set the permission's default value, description, and other attributes in the `permissions module <https://github.com/subuser-security/subuser/blob/master/logic/subuserlib/permissions.py>`_

 2. Tell subuser how to apply the permission in the `runtime class <https://github.com/subuser-security/subuser/blob/master/logic/subuserlib/classes/subuserSubmodules/run/runtime.py>`_

 3. Test your permission by adding it to the `all-permissions` image in the test suit and running the test suit.

Running the test suit
---------------------

In the root source directory run::

    subuser dev texttest-dev

To run the xpra-bridge test suit run::

    ./logic/test xpra-bridge

Building the docs
-----------------

In order to build the docs, you must have the subuser-standard within the docs directory.  In order to get the subser-standard issue::

    cd ~/<subuser-git-repo>/docs
    git clone https://github.com/subuser-security/subuser-standard.git

To build the docs, cd to this repositories root, run ``subuser dev docs`` and run ``make html`` in the docs directory::

    cd ~/<subuser-git-repo>/
    subuser dev docs-dev
    cd docs
    make html

Profiling
---------

Running a built in command, with the exception of ``test``, with the ``SUBUSER_RUN_PROFILER`` environment variable set will run those commands and print profiler output once the command has finnished.

Debugging the XPRA bridge
-------------------------

If you set the ``SUBUSER_DEBUG_XPRA`` environment variable then XPRA logs will be left in ``~/.subuser/volumes/xpra/<subuser-name>/xpra-home/``. XPRA will also spew out a bunch of garbage to the screen that you can read through.

Running with a higher verbosity level
-------------------------------------

Set the ``SUBUSER_VERBOSITY`` environment variable to 3 to see more messages. The default is 2. 1 is very terse.

Prepairing a release
--------------------
1. Run all test suits including the xpra-bridge test suit.
2. Bump ``VERSION`` file.
3. Tag release::

    $ git tag -s major.minor.reallyminor

4. Make packages and test them::

    $ make packages
    $ su
    # pip3 uninstall subuser
    # pip3 install ./dist/subuser-0.5.8-py3-none-any.whl

5. Deploy everything::

    $ make deploy
    $ git push origin 0.5.8

