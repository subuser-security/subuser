#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
"""
The Config class is used to hold user wide settings.
"""

#external imports
import os
#internal imports
from subuserlib.classes import userOwnedObject
from subuserlib import loadMultiFallbackJsonConfigFile
from subuserlib import paths

class Config(userOwnedObject.UserOwnedObject, dict):
  def __init__(self,user):
    self.__delitem__ = None
    self.__setitem__ = None
    userOwnedObject.UserOwnedObject.__init__(self,user)
    self._loadConfig()

  def _getSubuserConfigPaths(self):
    """ Returns a list of paths to config.json files in order that they should be looked in. """
    configFileInHomeDir = os.path.join(self.getUser().homeDir,".subuser","config.json")
    configFileInEtc = "/etc/subuser/config.json"
    configFileInSubuserDir = os.path.join(paths.getSubuserDir(),"config.json")
    return [configFileInHomeDir,configFileInEtc,configFileInSubuserDir]

  def _expandPathsInConfig(self,config):
    """ Go through a freshly loaded config file and expand any environment variables in the paths. """
    loadMultiFallbackJsonConfigFile.expandPathsInDict(self.getUser().homeDir,["bin-dir","registry-dir","installed-images-list","locked-subusers-path","user-set-permissions-dir","subuser-home-dirs-dir","repositories-dir","runtime-cache","lock-dir","volumes-dir"],config)

  def _loadConfig(self):
    """ Loads the subuser config: a dictionary of settings used by subuser. """
    configFileHierarchy = self._getSubuserConfigPaths()
    config = loadMultiFallbackJsonConfigFile.getConfig(configFileHierarchy)
    self._expandPathsInConfig(config)
    for key,entry in config.items():
      self[key] = entry
