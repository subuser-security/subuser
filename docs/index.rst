
Subuser - Securing the linux desktop with Docker
================================================

.. toctree::

  what-is-subuser
  security
  installation
  tutorial-use
  user-manual/index
  packaging
  flaws
  related-projects

Updating programs
------------------

You can update your subuser programs with::

  $ subuser update all


Removing subusers
-----------------

To remove the subuser named vim you can run::

  $ subuser subuser remove vim

To remove vim's home dir::

  $ rm -rf ~/.subuser/homes/vim

To clean up old images which have been installed, but no longer are used by any subuser::

  $ subuser remove-old-images
