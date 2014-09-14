
Subuser - Securing the linux desktop with Docker
================================================

.. toctree::

  index


What is subuser?
================

`Subuser is open source(LGPL3) and you can download the source code by clicking here <http://github.com/subuser-security/subuser>`_ 

The problem
-----------

As free software developers we like to share.  We surf the web and discover new code.  We are eager to try it out.  We live out an orgy of love and trust, unafraid that some code we cloned from git might be faulty or malicious.  We live in the 60s, carefree hippies.

This is utopia.

But sharing code isn't safe.  Every time we try out some strangers script we put ourselves at risk.  Despite the ocational claim that linux is a secure operating system, haphazardly sharing programs is NOT secure.

Furthermore, the fragmentation of linux desktop means that packaging work is needlessly repeated.  Programs that build and run on Fedora must be repackaged for Ubuntu.

Subuser with Docker attack both problems symultaneously.  Docker provides an isolated and consistent environment for your programs to run in.  Subuser gives your desktop programs access to the reasources they need in order to function normally.

Subuser turns Docker containers into normal linux programs
------------------------------------------------------------

Right now I'm editing this file in `vim`.  `vim` is not installed on my computer though.  It is installed in a docker container.  However, in order to edit this file, all I had to do was type::

  $ vim README.md

Subuser turns a docker container into a normal program.  But this program is not fully privilaged.  It can only access the directory from which it was called, `not my entire home dir <http://xkcd.com/1200/>`_.  Each subuser is assigned a specific set of permissions, just like in Android.  You can see an example `permissions.json` file bellow::

  {
    "description"                : "Simple universal text editor."
    ,"maintainer"                : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"
    // Path to executable within the docker image.
    ,"executable"                : "/usr/bin/vim"
    // A list of directories the program should have Read/Write access to.
    // Paths are relative to your home. Ex: "Downloads" will access "$HOME/Downloads".
    ,"user-dirs"                 : [ 'Downloads', 'Documents' ]  // Default: []
    // Allowed the program to display x11 windows.
    ,"x11"                       : true        // Default: false
    // Allow the program access to your sound playing and recording.
    ,"sound-card"                : true        // Default: false
    // Allow the program access to Read/Write access to the directory from which it was initialized.
    ,"access-working-directory" : true        // Default: false
    // Allow the program access to the internet.
    ,"allow-network-access"      : true        // Default: false
  }

How secure is subuser?
======================

.. warning:: Right now, subuser 0.2 is really alpha software.  running x11 applications with subuser 0.2 is **NOT** secure.

Subuser provides security via isolation.  It isolates programs from one another, so that one malicious or faulty program cannot harm the rest of the system.  Some paranoid people have been wondering just how secure/insecure subuser is.  It has been rightfully pointed out that Docker is not a specialized security solution and that there is a high likelyhood that exploits for Docker will continue to appear at a relatively high rate.

Subuser is not, and will never be, completely secure.  However, there are degrees of security.  Some attacks can be blocked, while others get through.

**Levels of isolation:**

0. Most linux distributions out of the box provide isolation between users.  They may also use Apparmour or SELinux to contain some daemons.  If kept up to date, they provide a relatively high level of security against remote network attackers and allow one to open common non-executable file formats without significant risk to your system.  However, installing untrusted software onto such a system is impossible without completely compromising the security of the system.

1. Linux as secured with subuser provides isolation at the application level.  Subuser should not reduce the security of single user computers.  It should have most of the same positive security properties as standard linux.  However, it allows one to run untrusted code with a relatively high level of containment.  Up to date subuser installations are still succeptible to zero day kernel exploits.  If you're trying to protect yourself from spyware and botnet software then subuser will do a great deal of good.  If the NSA thinks you are worth a custom zero day than subuser won't help much.

2. `Qubes OS <https://qubes-os.org>`_ provides a much higher level of security than subuser.  Qubes isolates security domains using individual virtual machines. It is forced to isolate "security domains" rather than individual programs due to the high overhead of the virtual machine.  This means that using subuser+qubes is not a bad idea. You can use qubes for low granualrity isolation and subuser for high granularity isolation. Qubes' isolation is potentially NSA proof.  It is certainly **very** hard to defeat.

Installing subuser
=====================

System Requirements
--------------------

 * Docker 1.2 or higher

 * Python >= 2.7

 * Git

Instalation
------------

1. Install `docker <http://www.docker.io/gettingstarted/#h_installation). Then [add yourself to the docker group](http://docs.docker.io/en/v0.7.3/use/basics/>`_.

2. Download this repository
  ::

  $ cd
  $ git clone https://github.com/subuser-security/subuser

3. Add `subuser/logic` and `~/.subuser/bin` to your path by adding the line `PATH=$PATH:$HOME/subuser/bin:$HOME/.subuser/bin` to the end of your `.bashrc` file.  You will need to change the path to `subuser/logic` to refer to the location to which you downloaded subuser.

4. Log out and then back in again.

5. Done!

Using subuser
=============

Installing a program with subuser
---------------------------------

You can see a list of instalable programs(also refered to as images) by doing::

  $ subuser list available

You can install one of these images by adding a subuser for it:

::

  $ subuser subuser add vim vim@default

This adds a new subuser named vim based on the image vim from the default repository.

You can run the subuser with::

  $ subuser run vim SomeTextFileToEdit

You can turn a subuser into a "normal" program by running::

  $ subuser subuser create-shortcut vim

Now you can launch vim with::

  $ vim SomeTextFileToEdit

Installing programs not yet in the database
----------------------------------------

Subuser allows anyone to create and share repositories of subuser images.  Repositories are arranged the following structure::

  image-name/
    docker-image/
      SubuserImagefile
      docker-build-context
    permissions.json

To create your own subuser repository:

1. Create a git repository for your own personal subuser repository:

::
  
  $ mkdir my-subuser-programs
  $ cd my-subuser-programs
  $ git init
  
2. Add subuser images:

Create a folder in your subuser repository for your new subuser image and add a `docker-image` subdirectory.:

::

  $ mkdir my-subuser-image
  $ cd my-subuser-image
  $ mkdir docker-image

Create an `permissions.json` file.  Here is an example::

  {
    "description"                : "Simple universal text editor."
    ,"maintainer"                : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"
    // Path to executable within the docker image.
    ,"executable"                : "/usr/bin/vim"
    // A list of directories the program should have Read/Write access to.
    // Paths are relative to your home. Ex: "Downloads" will access "$HOME/Downloads".
    ,"user-dirs"                 : [ 'Downloads', 'Documents' ]  // Default: []
    // Allowed the program to display x11 windows.
    ,"x11"                       : true        // Default: false
    // Allow the program access to your sound playing and recording.
    ,"sound-card"                : true        // Default: false
    // Allow the program access to Read/Write access to the directory from which it was initialized.
    ,"access-working-directory" : true        // Default: false
    // Allow the program access to the internet.
    ,"allow-network-access"      : true        // Default: false
  }

**Note**: Listing every permission is not necessary.

You can find a full specification for the `permissions.json` file format `here <https://github.com/subuser-security/subuser-standard/blob/master/permissions-dot-json-file-format.md>`_.

Now create a directory called `docker-image` and add a `SubuserImagefile` to that directory.  This is the same as a Dockerfile except for the adition of a special `FROM-SUBUSER-IMAGE` command which takes the identifier of a subuser image source as it's argument. For information on creating a Dockerfile, please see the `builder documentation for docker <https://docs.docker.com/reference/builder/>`_.

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

Design flaws/bugs in subuser
============================

* Application startup time is significantly slowed

* Certain things involving sharing of data between applications, like the clipboard in `vim`, just won't work.

* The security advantages of running x11 apps in docker is *very* iffy at best.
 - This will be fixed in the very near future.

* DBUS/gsettings don't work

* Inheriting the $PWD is a generally shitty idea.  If I run `vim` in my home dir, it can see and edit all of my files.  The only security advantage is if I run `vim` in some subdirectory.
 - I hope this will be fixed by something more sophisticated like giving access only to paths specified in the command line arguments.

* Disk usage is several times greater when installing one container per application due to the reduced ability to share dependencies
 - This can be aleviated by stacking docker images or using shared read only volumes.

See also links
==============

 * `Qubes OS <http://qubes-os.org/trac>`_

 * `Java Web Start <http://en.wikipedia.org/wiki/Java_Web_Start>`_

 * `The sub-identity toolkit <https://www3.nd.edu/~ccl/software/subid/>`_

 * `AppArmor <http://en.wikipedia.org/wiki/AppArmor>`_

 * `SELinux <http://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_
 
 * `Android permissions <http://developer.android.com/guide/topics/security/permissions.html>`_

 * `Jails <http://en.wikipedia.org/wiki/Jail_%28computer_security%29>`_
