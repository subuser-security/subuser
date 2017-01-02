# -*- coding: utf-8 -*-

"""
This module provides version info and other usefull debugging stuff.
"""

#external imports
import os
import collections
#internal imports
import subuserlib.paths
from subuserlib.classes.gitRepository import GitRepository
from subuserlib.classes.docker.dockerDaemon import DockerDaemon
import subuserlib.test

def getInfo(user):
  info = collections.OrderedDict()
  info["subuser-version"] = getSubuserVersion(user)
  info["docker-info"] = getDockerInfo(user)
  return info

def getSubuserVersion(user):
  if subuserlib.test.testing:
    return "0.5"
  with open(subuserlib.paths.getSubuserDataFile("VERSION")) as f:
    stableVersion = f.read().strip()
  if os.path.exists(os.path.join(subuserlib.paths.getSubuserDir(),".git")):
    gitRepo = GitRepository(user,subuserlib.paths.getSubuserDir())
    gitHash = gitRepo.getHashOfRef("HEAD")
    return stableVersion+"-dev-"+gitHash
  else:
    return stableVersion

def getDockerInfo(user):
  return user.getDockerDaemon().getInfo()
