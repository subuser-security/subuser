#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os,inspect,json
#internal imports
#import ...

def addIfUnrepresented(identifier,path,paths):
  """ Add the tuple to the dictionary if it's key is not yet in the dictionary. """
  if not identifier in paths.keys():
    paths[identifier] = path

def upNDirsInPath(path,n):
  if n > 0:
    return os.path.dirname(upNDirsInPath(path,n-1))
  else:
    return path

def getSubuserDir():
  """ Get the toplevel directory for subuser. """
  pathToThisSourceFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
  return upNDirsInPath(pathToThisSourceFile,5)

def filterOutNonExistantPaths(paths):
  _paths = []
  for path in paths:
    if os.path.exists(path):
      _paths.append(path)
  return _paths

def expandPathInDict(homeDir,pathAttribute,dict):
  """ Expand the environment variables in a dictionary of setting-value pairs given that the setting holds a path. """
  os.environ["SUBUSERDIR"] = getSubuserDir()
  os.environ["HOME"] = homeDir
  dict[pathAttribute] = os.path.expandvars(dict[pathAttribute]).replace("//","/") # os.path.expandvars is buggy and expands $HOME/foo to /home/user-name//foo
  

def expandPathsInDict(homeDir,pathAttributes,dict):
  for pathAttribute in pathAttributes:
    expandPathInDict(homeDir,pathAttribute,dict)

def getConfig(configFileHierarchy):
  """ This function is used for loading hierarchical config files in subuser.  That is, loading config.json and repositories.json.  For more information on config file hierarchies, see the documentation for these two files in the subuser standard:

 config.json - https://github.com/subuser-security/subuser-standard/blob/master/config-dot-json-file-format.md
 repositories.json - https://github.com/subuser-security/subuser-standard/blob/master/repositories-dot-json-file-format.md

It takes a hierarchy(a list of paths) of config files starting with the config file with the highest precidence and going to the config file with the least precidence.

It returns a dictionary of entries.

"""
  configPaths = filterOutNonExistantPaths(configFileHierarchy)
  config = {}
  for _configFile in configPaths:
    with open(_configFile, 'r') as configFile:
      _config = json.load(configFile)
      for identifier,setting in _config.iteritems():
        addIfUnrepresented(identifier,setting,config)
  return config
