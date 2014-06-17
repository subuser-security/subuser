Subuser - Securing the linux desktop with Docker
--------------------------
[**Video: What is subuser?**](http://www.youtube.com/watch?v=-9F8uXFcVFA)

[![What is subuser?](http://img.youtube.com/vi/-9F8uXFcVFA/0.jpg)](http://www.youtube.com/watch?v=-9F8uXFcVFA)


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

Subuser turns a docker container into a normal program.  But this program is not fully privilaged.  It can only access the directory from which it was called, [not my entire home dir](http://xkcd.com/1200/).  The end goal of the project is to assign each application on your system a specific set of permissions, just like in Android.

Subuser is just a Docker wrapper:
----------------------------------------

Subuser is meant to be easilly installed and in and of itself technically insignificant.  It is *just* a wrapper around docker, nothing more.

Subuser launches docker containers with [volumes](http://docs.docker.io/en/latest/use/working_with_volumes/) shared between the host and the child container. That's all.

Installing subuser:
-------------------

**System Requirements**

 * Docker(The latest version)

 * Python >= 2.7

**Instalation**

1. Install [docker](http://www.docker.io/gettingstarted/#h_installation). Then [add yourself to the docker group](http://docs.docker.io/en/v0.7.3/use/basics/).

2. Download this repository to your home directory:

  ````
  $ cd
  $ git clone https://github.com/subuser-security/subuser
  ````

3. Add `~/subuser/bin` to your path by adding the line `PATH=$HOME/subuser/bin:$PATH` to the end of your `.bashrc` file.

  - **Note**: Doing this will give `subuser` programs precedence over "normal" programs.  If you don't want this, you can add the `~/subuser/bin` directory to the END of your `$PATH` like so: `PATH=$PATH:$HOME/subuser/bin`.  Then, in order to run programs that are already installed on your computer with subuser you will have to use the `subuser run` command.

4. Log out and then back in again.

5. Done!

[**Installation video:**](http://www.youtube.com/watch?v=ahgRx5U4V7E)

[![Installing subuser](http://img.youtube.com/vi/ahgRx5U4V7E/0.jpg)](http://www.youtube.com/watch?v=ahgRx5U4V7E)

Using subuser:
--------------

[Video:](http://www.youtube.com/watch?v=KZrs8KngN68)

[![Using subuser](http://img.youtube.com/vi/KZrs8KngN68/0.jpg)](http://www.youtube.com/watch?v=KZrs8KngN68)

Installing a program with subuser:
----------------------------------

You can see a list of instalable programs by doing:

````
$ subuser list available
````

You can install one of these programs with:

````
$ subuser install vim
````

Run the program by typing it's name at the command line.

````
$ vim SomeTextFileToEdit
````

Installing programs not yet in the database:
----------------------------------------

Add a new installation directory for your program to the `programsThatCanBeInstalled` directory.

````
$ cd ~/subuser/programsThatCanBeInstalled
$ mkdir executable-name
$ cd executable-name
$ mkdir docker-image
````

Create an `permissions.json` file.  Here is an example:

````json
{
 "description"                : "Simple universal text editor."
 ,"maintainer"                : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"
 ,"executable"                : "/usr/bin/vim"
    // Path to executable within the docker image.
 ,"user-dirs"                 : []
    // Optional: A list of directories in the users home directory that this application should have read-write access to.
    //These are relative paths, Ex: "Downloads" instead of "$HOME/Downloads".
 ,"system-dirs"               : []
    // Optional: A list of directories that this application should have read only access to.  Absolute paths: Ex: "/usr"
 ,"x11"                       : false
    // Optional: This program is allowed to display x11 windows.
 ,"sound-card"                : false
    // Optional: Give this program access to your soundcard?
 ,"inherit-working-directory" : true
    // Should this program be able to read-write to the directory from which it was called.
 ,"allow-network-access"      : false
    // Optional: Should this program be allowed to access the internet?
}
````

You can find a full specification for the `permissions.json` file format [here](docs/permissions-dot-json-file-format.md).

**Note**: Listing every permission is not necesary.  All permissions always default to their more secure variant.

Now create a directory called `docker-image` and add a `Dockerfile` to that directory.  This docker file shoule describe a container with vim installed in it.

Updating programs:
------------------

You can update your subuser programs with:

````
$ cd ~/subuser
$ git pull
$ subuser update all
````

Or, if you happen to know that a program is out of date(say you've installed it through git in your dockerfile...)

````
$ subuser update vim-git
````


Uninstalling programs:
----------------------

To uninstall the docker images and remove vim from your `PATH` run:

````
$ subuser uninstall vim
````

To remove any settings and configuration files:

````
$ rm -r ~/subuser/homes/vim
````

Support:
--------
You can contact us on the [subuser mailing list](https://groups.google.com/forum/#!forum/subuser).

Design flaws/bugs in subuser:
------------------------

* Application startup time is significantly slowed

* Certain things involving sharing of data between applications, like the clipboard in `vim`, just won't work.

* The security advantages of running x11 apps in docker is *very* iffy at best.

* DBUS/gsettings don't work

* Inheriting the $PWD is a generally shitty idea.  If I run `vim` in my home dir, it can see and edit all of my files.  The only security advantage is if I run `vim` in some subdirectory.
 - I hope this will be fixed by something more sophisticated like giving access only to paths specified in the command line arguments.

* Disk usage is several times greater when installing one container per application due to the reduced ability to share dependencies
 - This can be aleviated by stacking docker images or using shared read only volumes.

See also links:
---------------

 * [Qubes OS](http://qubes-os.org/trac)

 * [Java Web Start](http://en.wikipedia.org/wiki/Java_Web_Start)

 * [The sub-identity toolkit](https://www3.nd.edu/~ccl/software/subid/)

 * [AppArmor](http://en.wikipedia.org/wiki/AppArmor)

 * [SELinux](http://en.wikipedia.org/wiki/Security-Enhanced_Linux)
 
 * [Android permissions](http://developer.android.com/guide/topics/security/permissions.html)

 * [Jails](http://en.wikipedia.org/wiki/Jail_%28computer_security%29)
