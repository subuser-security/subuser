#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os,inspect,json
#internal imports
#import ...

#The folowing is copied from paths.py in order to avoid a circular import.
home = os.path.expanduser("~")

def getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))) # BLEGH!

##########

def getSubuserConfigPaths():
  """ Returns a list of paths to config.json files in order that they should be looked in. """
  configFileInHomeDir = os.path.join(home,".subuser","config.json")
  configFileInEtc = "/etc/subuser/config.json"
  configFileInSubuserDir = os.path.join(getSubuserDir(),"config.json")
  _configsPaths = [configFileInHomeDir,configFileInEtc,configFileInSubuserDir]
  configsPaths = []
  for path in _configsPaths:
   if os.path.exists(path):
    configsPaths.append(path)
  return configsPaths

def _addIfUnrepresented(identifier,path,paths):
  """ Add the tuple to the dictionary if it's key is not yet in the dictionary. """
  if not identifier in paths.keys():
    paths[identifier] = path

def _expandPathInConfig(path,config):
  """ Expand the environment variables in a config settings value given that the setting holds a path. """
  config[path] = os.path.expandvars(config[path])

def __expandPathsInConfig(paths,config):
  for path in paths:
    _expandPathInConfig(path,config)

def _expandPathsInConfig(config):
  """ Go through a freshly loaded config file and expand any environment variables in the paths. """
  os.environ["SUBUSERDIR"] = getSubuserDir()
  __expandPathsInConfig(["bin-dir","installed-programs.json","user-set-permissions-dir","program-home-dirs-dir"],config)

def getConfig():
  """ Returns a dictionary of settings used by subuser. """
  configPaths = getSubuserConfigPaths()
  config = {}
  for _configFile in configPaths:
    with open(_configFile, 'r') as configFile:
      _config = json.load(configFile)
      for identifier,setting in _config.iteritems():
        _addIfUnrepresented(identifier,setting,config)
  _expandPathsInConfig(config)
  return config
