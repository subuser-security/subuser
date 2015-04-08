Related projects
==============

 * `Qubes OS <https://qubes-os.org/>`_

 Qubes OS aims to be the more secure, more resource intensive, big brother to subuser.  It divides your computer into security domains which each run on their own separate virtual machine.  If you want rock solid NSA proof security, I strongly recommend you check it out.

 * `Bedrock linux <http://bedrocklinux.org>`_ 

 Bedrock Linux is a project that I learned about long after I started working on subuser. Like subuser, it allows you to install software packaged for a variety of Linux distributions. Unlike subuser, which installs and runs programs in isolated environments running within a base system, Bedrock Linux mixes everything together at the same level without any segregation.

 * `Gnome sandboxes <https://wiki.gnome.org/Projects/SandboxedApps>`_

 This is a project started after Subuser was already around for a while. While this seems in some abstract sence to be quite similar to subuser it seems to be very Gnome specific.

 * `zero-install <http://zero-install.sourceforge.net/>`_, `Portable Linux Apps <http://portablelinuxapps.org/>`_, `Autopackage <https://en.wikipedia.org/wiki/Autopackage>`_, `Listaller <http://listaller.tenstral.net/>`_, `Limba <http://blog.tenstral.net/2015/03/limba-project-progress.html>`_, and to a lesser extent: `PPAs <http://www.ubuntu.com/news/launchpad-ppa>`_ and `One Click Install <http://en.opensuse.org/openSUSE:One_Click_Install>`_

 These allow one to package software "universally" so that the software may be installed and run on any distribution.  They have two flaws:

  - It is hard to package software for these systems
  - They don't deal with the security implications of running untrusted third party code

 Subuser solves both of these problems.

 * `Android permissions <http://developer.android.com/guide/topics/security/permissions.html>`_

 Subuser's permission sets were inspired by Android permissions.  We build off experience from the Android project and avoid the mistakes of using overly broad permissions and permissions that the user cannot easily deny.

 * `Java Web Start <http://en.wikipedia.org/wiki/Java_Web_Start>`_

 Subuser has many of the same goals as Java Web Start.  We want users to be able to easilly and safely install and run programs that they find on the internet.  We mostly learn from Java Web Start's mistakes here.  Don't ask/warn users every time a program tries to open a file, don't restrict programs to using GUI toolkits with crapy fonts ect.

 * `The sub-identity toolkit <https://www3.nd.edu/~ccl/software/subid/>`_

 This is an academic project that I learned about after I started working on subuser.  It's main utility share's the name subuser. It has some of the same goals when it comes to security via containment.

 * `AppArmor <http://en.wikipedia.org/wiki/AppArmor>`_ , `SELinux <http://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_, `TOMOYO <http://tomoyo.sourceforge.jp>`_, `Smack <http://schaufler-ca.com/home>`_

 These are competing programs which enforce `Mandatory Access Control(MAC) <http://en.wikipedia.org/wiki/Mandatory_access_control>`_ policies.  Those are either white lists or black lists of what the program is allowed to do.  While these pieces of software work fine for protecting the system, they are complicated to set up and provide overly wide access to user data.  Normally, when a program is expected to work with user data under SELinux or Apparmour, that program is given full access to the user's home directory.

 * `grsecurity <https://grsecurity.net>`_

 This is a patchset for the Linux kernel which improves kernel security.  It can help make subuser more secure by reducing the risk that a program will escape it's container by finding a kernel exploit.
 
 * `Docker <http://docker.com>`_

 Docker is the containment system that powers subuser.

 * `LXC <http://linuxcontainers.org>`_

 LXC is a competitor and backend to Docker.

 * `Jails <http://en.wikipedia.org/wiki/Jail_%28computer_security%29>`_

 There are many different chroot type setups.

