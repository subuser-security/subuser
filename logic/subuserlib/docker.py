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

executable = None
verified = False

def getExecutable():
  """
  Return the name of the docker executable or None if docker is not installed.
  """
  global executable
  if executable is not None:
    return executable
  if subuserlib.executablePath.which("docker.io"): # Docker is called docker.io on debian.
    return "docker.io"
  if subuserlib.executablePath.which("docker"):
    return "docker"
  return None

def getAndVerifyExecutable():
  """
  Return the name of the docker executable. Exits and displays a user friendly error message if docker is not setup correctly.
  """
  global executable
  global verified
  if executable is not None and verified:
    return executable
  executable = getExecutable()
  if not executable:
    sys.exit("""Error: Docker is not installed.

For installation instructions see <https://www.docker.io/gettingstarted/#h_installation>""")
  if not os.path.exists("/var/run/docker.pid"):
    sys.exit("""Error: Docker is not running.  You can launch it as root with:

# docker -d
""")
  verified = True
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

def buildImageTag(tag,hash):
  tag ='{:-<95.95}{:-<32.32}'.format(tag,hash)
  def isvalid(c):
    if c in "-_.":
      return True
    return c.isalpha() or c.isdigit()
  return ''.join([c if isvalid(c) else "-" for c in tag])

