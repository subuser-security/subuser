#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess
#internal imports
import subuserlib.classes.installedImages , subuserlib.classes.subusers, subuserlib.classes.userOwnedObject

class Registry(subuserlib.classes.userOwnedObject.UserOwnedObject):
  installedImages = None
  subusers = None
  
  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.installedImages = subuserlib.classes.installedImages.InstalledImages(user)
    self.subusers = subuserlib.classes.subusers.Subusers(user)

  def commit(self,message):
    """ git commit the changes to the registry files, installed-miages.json and subusers.json. """
    subprocess.POpen(["git","add","subusers.json","installed-programs.json"],cwd=self.getUser().config.getRegistryPath()).communicate()
    subprocess.POpen(["git","commit"],cwd=self.getUser().config.getRegistryPath()).communicate()
