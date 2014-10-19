#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This module helps us interact with the Docker executable directly.
"""


#external imports
import sys,os,getpass,grp,subprocess
#internal imports
import subuserlib.subprocessExtras,subuserlib.executablePath

def getDockerExecutable():
  """ Return the name of the docker executable or None if docker is not installed. """
  if subuserlib.executablePath.which("docker.io"): # Docker is called docker.io on debian.
    return "docker.io"
  if subuserlib.executablePath.which("docker"):
    return "docker"
  return None

def getAndVerifyDockerExecutable():
  """ Return the name of the docker executable. Exits and displays a user friendly error message if docker is not setup correctly. """
  executable = getDockerExecutable()
  if not executable:
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
  return executable

def runDocker(args):
  """ Run docker with the given command line arguments. """
  return subprocess.call([getAndVerifyDockerExecutable()]+args)

def getDockerOutput(args):
  """ Run docker with the given command line arguments and return it's output. """
  return subprocess.check_output([getAndVerifyDockerExecutable()]+args)

def runDockerAndExitIfItFails(args,cwd=None):
  """ Run docker with the given command line arguments.  If the command returns a non-zero exit code, exit with an error message. """
  subuserlib.subprocessExtras.subprocessCheckedCall([getAndVerifyDockerExecutable()]+args,cwd=cwd)
