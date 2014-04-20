#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os,inspect,json
#internal imports
#import ...

home = os.path.expanduser("~")

def _getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))) # BLEGH!

def _getSubuserConfigPaths():
  """ Returns a list of paths to config.json files in order that they should be looked in. """
  _configsPaths = []
  _configsPaths.append(os.path.join(home,".subuser","config.json"))
  _configsPaths.append("/etc/subuser/config.json") # TODO how does this work on windows?
  _configsPaths.append(os.path.join(_getSubuserDir(),"config.json"))
  configsPaths = []
  for path in _configsPaths:
   if os.path.exists(path):
    configsPaths.append(path)
  return configsPaths

def _addIfUnrepresented(identifier,path,paths):
  """ Add the tuple to the dictionary if it's key is not yet in the dictionary. """
  if not identifier in paths.keys():
    paths[identifier] = path

def expandPathInConfig(path,config):
  """ Expand the path of a given setting. """
  config[path] = os.path.expandvars(config[path])

def expandPathsInConfig(paths,config):
  for path in paths:
    expandPathInConfig(path,config)

def expandVarsInPaths(config):
  """ Go through a freshly loaded config file and expand any environment variables in the paths. """
  os.environ["SUBUSERDIR"] = _getSubuserDir()
  expandPathsInConfig(["bin-dir","installed-programs.json","user-set-permissions-dir","program-home-dirs-dir"],config)

def getConfig():
  """ Returns a dictionary of settings used by subuser. """
  configPaths = _getSubuserConfigPaths()
  config = {}
  for _configFile in configPaths:
    with open(_configFile, 'r') as configFile:
      _config = json.load(configFile)
      for identifier,setting in _config.iteritems():
        _addIfUnrepresented(identifier,setting,config)
  expandVarsInPaths(config)
  return config
