Design flaws/bugs in subuser
============================

* Application startup time is significantly slowed

* Certain things involving sharing of data between applications, like the clipboard in `vim`, just won't work.

* The security advantages of running x11 apps in docker is *very* iffy at best.
 - This will be fixed in the very near future.

* DBUS/gsettings don't work between subusers.  They also don't work between a given subuser and the host system.

* Inheriting the $PWD is a generally shitty idea.  If I run `vim` in my home dir, it can see and edit all of my files.  The only security advantage is if I run `vim` in some subdirectory.
 - I hope this will be fixed by something more sophisticated like giving access only to paths specified in the command line arguments.

* Disk usage is several times greater when installing one container per application due to the reduced ability to share dependencies
 - This can be aleviated by stacking docker images or using shared read only volumes.
 - Maybe future versions of Docker will have a venti based storage driver thus solving the problem prefectly and elegantly.
