#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess,os
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.classes.describable,subuserlib.subprocessExtras

class ProgramSource(subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.describable.Describable):
  __name = None
  __repo = None
  __permissions = None

  def __init__(self,user,repo,name):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__name = name
    self.__repo = repo

  def getName(self):
    return self.__name

  def getRepository(self):
    return self.__repo

  def getInstalledImages(self):
    """ Get all InstalledImage s built from this ProgramSource, including out of date images. """
    return [image for image in self.getUser().getRegistry().getInstalledImages() if image.getProgramSource().getName() == self.getName() and image.getProgramSource().getRepository().getName() == self.getRepository().getName()]

  def getImage(self):
    """ Get the most up to date InstalledImage built from this ProgramSource or None, if there are no InstalledImage s built from this ProgramSource. """
    latestUpdateTime = ""
    imageWithLatestUpdateTime = None
    for image in self.getInstalledImages():
      if image.getLastUpdateTime() > latestUpdateTime:
        latestUpdateTime = image.getLastUpdateTime()
        imageWithLatestUpdateTime = image
    return imageWithLatestUpdateTime

  def getSubusers(self):
    """
     Get a list of subusers that were built from this ProgramSource.
    """
    subusers = []
    for subuser in self.getUser().getRegistry().getSubusers():
      if subuser.getProgramSource()==self:
        subusers.append(subuser)
    return subusers

  def getSourceDir(self):
    return os.path.join(self.getRepository().getRepoPath(),self.getName())

  def getPermissions(self):
    if not self.__permissions:
      permissionsPath=os.path.join(self.getSourceDir(),"permissions.json")
      self.__permissions = subuserlib.classes.permissions.Permissions(self.getUser(),readPath=permissionsPath,writePath=permissionsPath)
    return self.__permissions

  def describe(self):
    print(self.getName()+":")
    self.getPermissions().describe()
