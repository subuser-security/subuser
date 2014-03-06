#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# TODO, refactor by putting helper functions for both repositories.py and configs.py in one place.

import os
import inspect
import json
import collections

home = os.path.expanduser("~")

def _getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))) # BLEGH!

def _getRepositoryListPaths():
  """ Returns a list of paths to repositories.json files in order that they should be looked in. """
  _repositoryListPaths = []
  _repositoryListPaths.append(os.path.join(home,".subuser","repositories.json"))
  _repositoryListPaths.append("/etc/subuser/repositories.json") # TODO how does this work on windows?
  _repositoryListPaths.append(os.path.join(_getSubuserDir(),"repositories.json"))
  repositoryListPaths = []
  for path in _repositoryListPaths:
   if os.path.exists(path):
    repositoryListPaths.append(path)
  return repositoryListPaths

def _addIfUnrepresented(identifier,path,paths):
  """ Add the tuple to the dictionary if it's key is not yet in the dictionary. """
  if not identifier in paths.keys():
    paths[identifier] = path

def expandVarsInPaths(repositories):
  """ Go through a freshly loaded list of repositories and expand any environment variables in the paths. """
  os.environ["SUBUSERDIR"] = _getSubuserDir()
  for reponame,info in repositories.iteritems():
    info["path"] = os.path.expandvars(info["path"])

def getRepositories():
  """ Returns a dictionary of repositories used by subuser. """
  repositoryListPaths = _getRepositoryListPaths()
  repositories = {}
  for _repositoryListFile in repositoryListPaths:
    with open(_repositoryListFile, 'r') as repositoryListFile:
      _repositories = json.load(repositoryListFile, object_pairs_hook=collections.OrderedDict)
      for identifier,repository in _repositories.iteritems():
        _addIfUnrepresented(identifier,repository,repositories)
  expandVarsInPaths(repositories)
  return repositories
