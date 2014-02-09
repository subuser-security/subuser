Subuser - Securing the linux desktop with Docker
--------------------------

As free software developers we like to share.  We surf the web and discover new code.  We are eager to try it out.  We live out an orgy of love and trust, unafraid that some code we cloned from git might be faulty or malicious.  We live in the 60s, carefree hippies.

This is utopia.

But sharing code isn't safe.  Every time we try out some strangers script we put ourselves at risk.  Despite the ocational claim that linux is a secure operating system, haphazardly sharing programs is NOT secure.

Docker promises to solve this problem.  Docker is not yet in a stable release, but with the help of subuser, we can already use it to make our computers more secure.

Subuser turns docker containers into normal linux programs:
------------------------------------------------------------

Right now I'm editing this file in `vim`.  `vim` is not installed on my computer though.  It is installed in a docker container.  However, in order to edit this file, all I had to do was type:

````
$ vim README.md
````

Subuser turns a docker container into a normal program.  But this program is not fully privilaged.  It can only access the directory from which it was called, not my entire home dir.  The end goal of the project is to assign each application on your system a specific set of permissions, just like in Android.

Subuser is just Docker in a pretty skirt:
----------------------------------------

Subuser is meant to be easilly installed and in and of itself technically insignificant.  It is *just* a wrapper around docker, nothing more.

Subuser launches docker containers with [volumes](http://docs.docker.io/en/latest/use/working_with_volumes/) shared between the host and the child container.  For X11 apps it uses X11 over ssh. That's all.

Installing subuser:
-------------------

1. Install [docker](http://www.docker.io/gettingstarted/#h_installation). Then [add yourself to the docker group](http://docs.docker.io/en/v0.7.3/use/basics/).

2. Download this repository to your home directory:

````
$ cd
$ git clone http://github.com/timthelion/subuser
````

3. Add `~/subuser/bin` to your path by adding the line `PATH=$HOME/subuser/bin/:$PATH` to the end of your `.bashrc` file.

4. Done!

Installing a program with subuser:
----------------------------------

You can see a list of instalable programs by doing:

````
$ subuser list availiable
````

You can install one of these programs with:

````
$ subuser install vim
````

Installing programs not yet in the database:
----------------------------------------

Create a new installation directory for your program.

````
$ cd ~/subuser/subusers
$ mkdir executable-name
$ cd executable-name
$ mkdir docker-image
````

Create an `permissions.json` file with the following form:

````
{
 "description"  : "Simple universal text editor."
 ,"maintainer"  : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"
 ,"executable"  : "/usr/bin/vim"
    // Path to executable within the docker image.
 ,"user-dirs" : []
    // A list of directories in the users home directory that this application should have read-write access to.
    //These are relative paths, Ex: "Downloads" instead of "$HOME/Downloads".
 ,"system-dirs" : []
    // A list of directories that this application should have read only access to.  Absolute paths: Ex: "/usr"
 ,"x11" : false
    // This program displays an x11 window.
 ,"inherit-working-directory" : true
    // Should this program be able to read-write to the directory from which it was called.
 ,"allow-network-access" : false
    // Should this program be allowed to access the internet?
}
````

Now create a `Dockerfile` in the `docker-image` directory with vim installed in it.


Uninstalling programs:
----------------------

To uninstall the docker images and remove vim from your `PATH` run:

````
$ subuser uninstall vim
````

To remove any settings and configuration files:

````
$ rm -r ~/subuser/subuser-home/vim
````

Design flaws in subuser:
------------------------

* Application startup time is significantly slowed

* Running X11 programs through ssh on a local machine is just weird

* Certain things involving sharing of data between applications, like the clipboard in `vim`, just won't work.

* Sound. I've got no idea...

* Inheriting the $PWD is a generally shitty idea.  If I run `vim` in my home dir, it can see and edit all of my files.  The only security advantage is if I run `vim` in some subdirectory.
 - I hope this will be fixed by something more sophisticated like giving access only to paths specified in the command line arguments.

* Disk usage is several times greater when installing one container per application due to the reduced ability to share dependencies
 - This can be aleviated by stacking docker images or using shared read only volumes.
