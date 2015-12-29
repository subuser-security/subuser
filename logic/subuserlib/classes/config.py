# -*- coding: utf-8 -*-
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
    configFileInSubuserDir = paths.getSubuserDataFile("config.json")
    return [configFileInHomeDir,configFileInEtc,configFileInSubuserDir]

  def _expandPathsInConfig(self,config):
    """
    Go through a freshly loaded config file and expand any environment variables in the paths.
    """
    pathsToExpand = [
      "bin-dir"
      ,"registry-dir"
      ,"installed-images-list"
      ,"locked-subusers-path"
      ,"subuser-home-dirs-dir"
      ,"repositories-dir"
      ,"runtime-cache"
      ,"lock-dir"
      ,"volumes-dir"]
    loadMultiFallbackJsonConfigFile.expandPathsInDict(self.getUser().homeDir,pathsToExpand,config)

  def _loadConfig(self):
    """
    Loads the subuser config: a dictionary of settings used by subuser.
    """
    configFileHierarchy = self._getSubuserConfigPaths()
    config = loadMultiFallbackJsonConfigFile.getConfig(configFileHierarchy)
    self._expandPathsInConfig(config)
    for key,entry in config.items():
      self[key] = entry
