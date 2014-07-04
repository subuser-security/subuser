#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,os,getpass,grp,subprocess
#internal imports
import subprocessExtras,executablePath

def getDockerExecutable():
  """ Return the name of the docker executable. Exits and displays a user friendly error message if docker is not setup correctly. """
  if executablePath.which("docker.io"): # Docker is called docker.io on debian.
    return "docker.io"
  if executablePath.which("docker"):
    return "docker"
  sys.exit("""Error: Docker is not installed.

For installation instructions see <https://www.docker.io/gettingstarted/#h_installation>""")
  if not os.path.exists("/var/run/docker.pid"):
    sys.exit("""Error: Docker is not running.  You can launch it as root with:

# docker -d
""")
 
  username = getpass.getuser()
  if not username in grp.getgrnam("docker").gr_mem:
    sys.exit("""Error: You are not a member of the docker group.

To learn how to become a member of the docker group please watch this video: <http://www.youtube.com/watch?v=ahgRx5U4V7E>""")


def runDocker(args):
  """ Run docker with the given command line arguments. """
  return subprocess.call([getDockerExecutable()]+args)

def getDockerOutput(args):
  """ Run docker with the given command line arguments and return it's output. """
  return subprocess.check_output([getDockerExecutable()]+args)

def runDockerAndExitIfItFails(args):
  """ Run docker with the given command line arguments.  If the command returns a non-zero exit code, exit with an error message. """
  subprocessExtras.subprocessCheckedCall([getDockerExecutable()]+args)
