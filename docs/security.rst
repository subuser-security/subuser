Security
========

How secure is subuser?
----------------------

Subuser provides security by isolation.  It isolates programs from one another so that one malicious or faulty program cannot harm the rest of the system.  Some paranoid people have been wondering just how secure/insecure subuser is.  It has been rightfully pointed out that Docker is not a specialized security solution and that there is a high likelihood that exploits for Docker will continue to appear at a relatively high rate.

Subuser is not, and will never be, completely secure.  However, there are degrees of security.  Some attacks can be blocked, while others get through.

**Levels of isolation:**

0. Most Linux distributions provide isolation between users out of the box.  They may also use AppArmor or SELinux to contain some daemons and applications.  If kept up to date they provide a relatively high level of security against remote network attackers and allow one to open common non-executable file formats without significant risk to your system.  However, installing untrusted software onto such a system is impossible without completely compromising the security of the system.

1. Linux, as secured with subuser, provides isolation at the application level.  Subuser should not reduce the security of single user computers.  It should have most of the same positive security properties as standard Linux.  However, it allows one to run untrusted code with a relatively high level of containment.  Up to date subuser installations are still susceptible to zero day kernel exploits.  If you're trying to protect yourself from spyware and botnet software, then subuser will do a great deal of good. It is better than an antivirus program as the isolation model does not rely on the malware being known about.  It is also better than antivirus software in that it protects against SpWiCB (Spyware With Corporate Backing) a problem which the commercial AVs ignore. If the NSA thinks you are worth a custom zero day than subuser won't help much.

2. `Qubes OS <https://qubes-os.org>`_ provides a much higher level of security than subuser.  Qubes isolates security domains using individual virtual machines. It is forced to isolate "security domains" rather than individual programs due to the high overhead of the virtual machines.  This means that using subuser+Qubes is not a bad idea. You can use Qubes for low granularity isolation and subuser for high granularity isolation. Qubes' isolation is potentially NSA proof.  It is certainly **very** hard to defeat.

Security Bulletins
------------------

2017
^^^^

1. 06.04.2017 - The ``build-context`` property of ``.subuser.json`` could contain a relative path which was outside of the image repository when using local file based repositories (this did not effect git).

2016
^^^^

1. 02.03.2016 - Container break out possible when enabling the sound-card permission. Due to mounting the ``/dev/snd`` volume as read-write rather than read only it is possible to escape a subuser container when running the development version of Docker. This is a chain of two factors: It is possible to get root in a container using a `SUID binary <https://github.com/subuser-security/subuser/issues/229>`_.  The ``--device`` flag now `follows symlinks <https://github.com/docker/docker/pull/20684#discussion_r54466051>`_. This issue is fixed in subuser-0.5.3.

