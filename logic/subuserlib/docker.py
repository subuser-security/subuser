# -*- coding: utf-8 -*-

"""
This module helps us interact with the Docker executable directly.
"""

#external imports
import sys
import os
import getpass
import grp
#internal imports
import subuserlib.subprocessExtras as subprocessExtras
import subuserlib.executablePath

def getExecutable():
  """
  Return the name of the docker executable or None if docker is not installed.
  """
  if subuserlib.executablePath.which("docker.io"): # Docker is called docker.io on debian.
    return "docker.io"
  if subuserlib.executablePath.which("docker"):
    return "docker"
  return None

def getAndVerifyExecutable():
  """
  Return the name of the docker executable. Exits and displays a user friendly error message if docker is not setup correctly.
  """
  executable = getExecutable()
  if not executable:
    sys.exit("""Error: Docker is not installed.

For installation instructions see <https://www.docker.io/gettingstarted/#h_installation>""")
  if not os.path.exists("/var/run/docker.pid"):
    sys.exit("""Error: Docker is not running.  You can launch it as root with:

# docker -d
""")

  username = getpass.getuser()
  if not os.getuid() == 0:
    try:
      groupmembers = grp.getgrnam("docker").gr_mem
    except KeyError:
      groupmembers = grp.getgrnam("dockerroot").gr_mem
    if not username in groupmembers:
      sys.exit("""Error: You are not a member of the docker group.

To learn how to become a member of the docker group please watch this video: <http://www.youtube.com/watch?v=ahgRx5U4V7E>""")
  return executable

def run(args,cwd=None):
  """
  Run docker with the given command line arguments. Return Docker's exit code.
  """
  return subprocessExtras.call([getAndVerifyExecutable()]+args,cwd)

def runBackground(args,cwd=None,suppressOutput=True,collectStdout=False,collectStderr=False):
  """
  Run docker with the given command line arguments. Return Docker's pid.
  """
  return subprocessExtras.callBackground([getAndVerifyExecutable()]+args,cwd,suppressOutput=suppressOutput,collectStdout=collectStdout,collectStderr=collectStderr)
