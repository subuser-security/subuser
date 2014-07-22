#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess
#internal imports
import subuserlib.classes.installedImages , subuserlib.classes.subusers, subuserlib.classes.userOwnedObject

class Registry(subuserlib.classes.userOwnedObject.UserOwnedObject):
  __installedImages = None
  __subusers = None
  __repositories = None

  def getInstalledImages(self):
    if not self.__installedImages:
      self.__installedImages = subuserlib.classes.installedImages.InstalledImages(self.getUser())
    return self.__installedImages

  def getSubusers(self):
    if not self.__subusers:
      self.__subusers = subuserlib.classes.subusers.Subusers(self.getUser())
    return self.__subusers

  def getRepositories(self):
    if not self.__repositories:
      self.__repositories =      subuserlib.classes.repositories.Repositories(self.getUser())
    return self.__repositories

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)

  def commit(self,message):
    """ git commit the changes to the registry files, installed-miages.json and subusers.json. """
    subprocess.POpen(["git","add","subusers.json","installed-programs.json"],cwd=self.getUser().config.getRegistryPath()).communicate()
    subprocess.POpen(["git","commit"],cwd=self.getUser().config.getRegistryPath()).communicate()
