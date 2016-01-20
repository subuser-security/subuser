Design flaws/bugs in subuser
============================

* Application startup time is slowed.  On my system with Docker's ``aufs`` backend it takes 2.5 seconds extra time for all applications, be it ``vim`` or ``iceweasel``.  I have read reports that on newer systems with SSDs and ``btrfs`` this can be reduced to a quarter of a second.

* Certain things involving sharing of data between applications, like the clipboard in `vim`, just won't work.

* DBUS/gsettings don't work between subusers.

* Inheriting the $PWD is a generally shitty idea.  If I run `vim` in my home dir, it can see and edit all of my files.  The only security advantage is if I run `vim` in some subdirectory.
 - I hope this will be fixed by something more sophisticated like giving access only to paths specified in the command line arguments.

* Disk usage is several times greater when installing one container per application due to the reduced ability to share dependencies
 - Docker will soon have `ZFS <http://zfsonlinux.org/>`_ support, which has limited support for block deduplication.  Maybe future versions of Docker will have a `venti <http://doc.cat-v.org/plan_9/4th_edition/papers/venti/>`_ based storage driver thus solving the problem perfectly and elegantly and also making updates even faster than on a traditional system.

