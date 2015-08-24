#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Module used for loading multiple json config files, where attributes consequtively over-ride eachother.
"""

#external imports
import os
import inspect
import json
#internal imports
#import ...

def upNDirsInPath(path,n):
  if n > 0:
    return os.path.dirname(upNDirsInPath(path,n-1))
  else:
    return path

def getSubuserDir():
  """
  Get the toplevel directory for subuser.
  """
  pathToThisSourceFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
  return upNDirsInPath(pathToThisSourceFile,4)

def filterOutNonExistantPaths(paths):
  _paths = []
  for path in paths:
    if os.path.exists(path):
      _paths.append(path)
  return _paths

def expandPathInDict(homeDir,pathAttribute,dictionary):
  """
  Expand the environment variables in a dictionary of setting-value pairs given that the setting holds a path.
  """
  os.environ["SUBUSERDIR"] = getSubuserDir()
  os.environ["HOME"] = homeDir
  dictionary[pathAttribute] = os.path.expandvars(dictionary[pathAttribute]).replace("//","/") # os.path.expandvars is buggy and expands $HOME/foo to /home/user-name//foo

def expandPathsInDict(homeDir,pathAttributes,dictionary):
  for pathAttribute in pathAttributes:
    expandPathInDict(homeDir,pathAttribute,dictionary)

def getConfig(configFileHierarchy):
  """
  This function is used for loading hierarchical config files in subuser.  That is, loading config.json and repositories.json.  For more information on config file hierarchies, see the documentation for these two files in the subuser standard:

   - `config.json <http://subuser.org/subuser-standard/serializations/config-dot-json-file-format.html>`_
   - `repositories.json <http://subuser.org/subuser-standard/serializations/registry/repositories-dot-json-file-format.html>`_

  It takes a hierarchy(a list of paths) of config files starting with the config file with the highest precidence and going to the config file with the least precidence.

  It returns a dictionary of entries.

  """
  configPaths = filterOutNonExistantPaths(configFileHierarchy)
  configPaths.reverse()
  config = {}
  for _configFile in configPaths:
    with open(_configFile, 'r') as configFile:
      _config = json.load(configFile)
      config.update(_config)
  return config
