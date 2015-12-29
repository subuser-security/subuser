# -*- coding: utf-8 -*-

"""
Module used for loading multiple json config files, where attributes consequtively over-ride eachother.
"""

#external imports
import os
import json
#internal imports
import subuserlib.paths

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
  realHome = os.environ["HOME"]
  os.environ["HOME"] = homeDir
  try:
    path = dictionary[pathAttribute]
    path = os.path.expandvars(path)
    if not "://" in path:
      path = os.path.normpath(path)# Norpath because os.path.expandvars is buggy and expands $HOME/foo to /home/user-name//foo
    dictionary[pathAttribute] = path
  except KeyError:
    pass
  os.environ["HOME"] = realHome

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
