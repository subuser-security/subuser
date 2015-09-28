#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This module provides version info and other usefull debugging stuff.
"""

#external imports
import os
#internal imports
import subuserlib.subprocessExtras as subprocessExtras
import subuserlib.paths
from subuserlib.classes.gitRepository import GitRepository
from subuserlib.classes.docker.dockerDaemon import DockerDaemon
import subuserlib.test

def getInfo():
  info = {}
  info["subuser-version"] = getSubuserVersion()
  info["docker-info"] = getDockerInfo()
  return info

def getSubuserVersion():
  if subuserlib.test.testing:
    return "0.5"
  with open(subuserlib.paths.getSubuserDataFile("VERSION")) as f:
    stableVersion = f.read().strip()
  if os.path.exists(os.path.join(subuserlib.paths.getSubuserDir(),".git")):
    gitRepo = GitRepository(subuserlib.paths.getSubuserDir())
    gitHash = gitRepo.getHashOfRef("HEAD")
    return stableVersion+"-dev-"+gitHash
  else:
    return stableVersion

def getDockerInfo():
  dockerDaemon = DockerDaemon(None)
  return dockerDaemon.getInfo()
