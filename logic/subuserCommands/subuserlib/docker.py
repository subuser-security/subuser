#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys
import subprocess
import os
import getpass
import grp
import utils

# Taken from: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
  def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

  fpath, fname = os.path.split(program)
  if fpath:
    if is_exe(program):
      return program
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      path = path.strip('"')
      exe_file = os.path.join(path, program)
      if is_exe(exe_file):
        return exe_file

  return None

def checkIfDockerIsSetupProperly():
  """ Exits and displays a user friendly error message if docker is not setup correctly. """
  if not which("docker"):
	sys.exit("""Error: Docker is not installed.

For instalation instructions see <https://www.docker.io/gettingstarted/#h_installation>""")
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
  checkIfDockerIsSetupProperly()
  return subprocess.call(["docker"]+args)

def getDockerOutput(args):
  """ Run docker with the given command line arguments and return it's output. """
  checkIfDockerIsSetupProperly()
  return subprocess.check_output(["docker"]+args)

def runDockerAndExitIfItFails(args):
  """ Run docker with the given command line arguments.  If the command returns a non-zero exit code, exit with an error message. """
  checkIfDockerIsSetupProperly()
  utils.subprocessCheckedCall(["docker"]+args)
