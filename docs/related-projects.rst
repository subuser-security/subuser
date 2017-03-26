Related projects
================

 * `snap <https://www.ubuntu.com/desktop/snappy>`_

 Snap is Canonical's new packaging and sandboxing system. It is quite similar to subuser. It supports packaging your apps for cross platform distribution, sandboxing your apps so that you can run untrusted code, and reverting/rolling back application upgrades just like subuser. The main difference is that subuser uses a more freeform packaging system, allowing you to package your apps simply by writting a Dockerfile. Snap is, on the other hand, a **real** packaging manager with a dependency resolution engine and everything. The result is that, snap packages install quicker, upgrade quicker, and use less space on disk, but subuser packages are much easier to create, especially for out of date or esoteric code. In the future, subuser will support `CAS <http://doc.cat-v.org/plan_9/4th_edition/papers/venti/>`_ deduplication and snap's advantages will fall away, allowing users to take advantage of the ease of packaging for subuser and the speed of snap at the same time. In the mean time snap and subuser can run side by side on the same system without interfering with eachother, so if you want to run evince using snap and some hard to package esoteric IDE with subuser, that's totally possible.

 * `flatpak <http://flatpak.org/>`_

 Flatpak is Redhat corporation's response to subuser and snap. It has its own special packaging format, so you'll have to rebuild and repackage your applications to work with flatpak. They got press for `having packaged libreoffice <https://whatofhow.wordpress.com/2015/08/11/libreoffice-in-a-box/>`_ for flatpak. No such blog post could be written for subuser, because with subuser, packaging libreoffice is as simple as writting the two line Dockerfile ``FROM debian``, ``RUN apt-get update && apt-get install -y libreoffice`` and adding a `permissions.json <http://subuser.org/subuser-standard/permissions-dot-json-file-format.html>`_ file. Flatpak also uses its own "ports" protocol for sandboxing so only applications that are specifically designed for flatpak's sandbox can be contained. Finally, the sandbox is disabled by default which means that when you install an application with flatpak you don't know if it is safe or not. On the bright side, flatpak uses `OSTree <https://github.com/ostreedev/ostree>`_ under the hood, which supports seamless file deduplication and thus is way better at efficiently storing and updating images than subuser/Docker's layered image format. Another point in flatpak's favor, is that their ports protocol will likely lead to better desktop integration for those apps which decide to take the jump and design with flatpak in mind. The best news of all, is that flatpak and subuser can run side by side on the same system without interfering with eachother, so if you want to run evince using flatpak and some hard to package esoteric IDE with subuser, that's totally possible.

 * `Qubes OS <https://qubes-os.org/>`_

 Qubes OS aims to be the more secure, more resource intensive, big brother to subuser.  It divides your computer into security domains which each run on their own separate virtual machine.  If you want rock solid NSA proof security, I strongly recommend you check it out.

 * `Subgraph OS <https://subgraph.com/>`_

 Subgraph OS, like subuser, aims to securely partition the operating system at the application level. Subgraph's goals are purely security based, where-as subuser focuses on portability and maintainability as well. Subgraph is able to take advantage of specialized kernel features like grsec and thus has a level of security which exceeds that of subuser. However, unlike subuser, the user of subgraph must specially configure their operating system/kernel for use with subgraph. In the security by isolation spectrum, subgraph is one step bellow Qubes OS. It is less resource intensive and less secure than Qubes. Subuser is one step bellow subgraph. Subuser is more portable and less secure than subgraph.

 * `Apiary Desktop <https://www.usenix.org/conference/usenix-atc-10/apiary-easy-use-desktop-application-fault-containment-commodity-operating>`_

 A 2010 academic project which had a very similar design to subuser. No code has been published, however the talk is interesting.

 * `Bedrock linux <http://bedrocklinux.org>`_

 Bedrock Linux is a project that I learned about long after I started working on subuser. Like subuser, it allows you to install software packaged for a variety of Linux distributions. Unlike subuser, which installs and runs programs in isolated environments running within a base system, Bedrock Linux mixes everything together at the same level without any segregation.

 * `X11-Docker <https://github.com/mviereck/x11docker>`_

 Run applications in docker with access to the X11 server also supports xpra and xephyr for secure window display, just like subuser. Looks very nice and UNIXy! Certainly more flexible/manual than subuser. Written in bash. Is more traditional in its approach to dependencies, for instance, using xpra actually requires xpra to be installed on your host system as well as within the container ;). On subuser this isn't needed!

 * `zero-install <http://zero-install.sourceforge.net/>`_, `Portable Linux Apps <http://portablelinuxapps.org/>`_, `Autopackage <https://en.wikipedia.org/wiki/Autopackage>`_, `Listaller <http://listaller.tenstral.net/>`_, `Limba <http://blog.tenstral.net/2015/03/limba-project-progress.html>`_, and to a lesser extent: `PPAs <http://www.ubuntu.com/news/launchpad-ppa>`_ and `One Click Install <http://en.opensuse.org/openSUSE:One_Click_Install>`_

 These allow one to package software "universally" so that the software may be installed and run on any distribution.  They have two flaws:

  - It is hard to package software for these systems
  - They don't deal with the security implications of running untrusted third party code

 Subuser solves both of these problems.

 * `Android permissions <http://developer.android.com/guide/topics/security/permissions.html>`_

 Subuser's permission sets were inspired by Android permissions.  We build off experience from the Android project and avoid the mistakes of using overly broad permissions and permissions that the user cannot easily deny.

 * `Java Web Start <https://en.wikipedia.org/wiki/Java_Web_Start>`_

 Subuser has many of the same goals as Java Web Start.  We want users to be able to easily and safely install and run programs that they find on the internet.  We mostly learn from Java Web Start's mistakes here.  Don't ask/warn users every time a program tries to open a file, don't restrict programs to using GUI toolkits with crappy fonts ect.

 * `The sub-identity toolkit <https://www3.nd.edu/~ccl/software/subid/>`_

 This is an academic project that I learned about after I started working on subuser.  It's main utility share's the name subuser. It has some of the same goals when it comes to security via containment.

 * `AppArmor <https://en.wikipedia.org/wiki/AppArmor>`_ , `SELinux <https://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_, `TOMOYO <http://tomoyo.sourceforge.jp>`_, `Smack <http://schaufler-ca.com/home>`_

 These are competing programs which enforce `Mandatory Access Control(MAC) <https://en.wikipedia.org/wiki/Mandatory_access_control>`_ policies.  Those are either white lists or black lists of what the program is allowed to do.  While these pieces of software work fine for protecting the system, they are complicated to set up and provide overly wide access to user data.  Normally, when a program is expected to work with user data under SELinux or AppArmor, that program is given full access to the user's home directory.

 * `grsecurity <https://grsecurity.net>`_

 This is a patchset for the Linux kernel which improves kernel security.  It can help make subuser more secure by reducing the risk that a program will escape it's container by finding a kernel exploit.

 * `Docker <https://docker.com>`_

 Docker is the containment system that powers subuser.

 * `LXC <https://linuxcontainers.org>`_

 LXC is a competitor and backend to Docker.

 * `Jails <https://en.wikipedia.org/wiki/Jail_%28computer_security%29>`_

 There are many different chroot type setups.

 * `Firejail <https://github.com/netblue30/firejail>`_

 Firejail is a sandboxing program based on Linux namespaces, seccomp-bpf and Linux capabilities.

Papers and publications
-----------------------

 * Cliffe Schreuders Z, McGill T, Payne C, `The State of the Art of Application Restrictions and Sandboxes: A Survey of Application-oriented Access Controls and their Shortfalls, Computers & Security (2012) <http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.300.4042&rep=rep1&type=pdf>`_
