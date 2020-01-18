# -*- coding: utf-8 -*-

"""
Implements functions involved in building/installing/updating subuser images.
"""

#external imports
import sys
#internal imports
import subuserlib.classes.installedImage
import subuserlib.verify
from subuserlib.classes.userOwnedObject import UserOwnedObject
import subuserlib.classes.exceptions as exceptions

class InstallationTask(UserOwnedObject):
  def __init__(self,op):
    UserOwnedObject.__init__(self,op.user)
    self.op = op
    self.__upToDateImageSources = set()
    self.__outOfDateImageSources = set()
    self.__outOfDateSubusers = None
    self.__subusersWhosImagesFailedToBuild = set()

  def getOutOfDateSubusers(self):
    """
    Returns a list of subusers which are out of date or have no InstalledImage associated with them.
    """
    if self.__outOfDateSubusers is None:
      self.user.registry.log("Checking if images need to be updated or installed...")
      self.__outOfDateSubusers = set()
      for subuser in self.op.subusers:
        try:
          if (not subuser.locked) and (not (subuser.imageSource.getLatestInstalledImage() is None)):
            self.user.registry.log("Checking if subuser "+subuser.name+" is up to date.")
            for imageSource in getTargetLineage(subuser.imageSource):
              if imageSource in self.__upToDateImageSources:
                continue
              if imageSource in self.__outOfDateImageSources:
                upToDate = False
              else:
                upToDate = self.isUpToDate(imageSource)
              if upToDate:
                self.__upToDateImageSources.add(imageSource)
              else:
                self.__outOfDateImageSources.add(imageSource)
                self.__outOfDateSubusers.add(subuser)
                break
          if subuser.imageSource.getLatestInstalledImage() is None or subuser.imageId is None or not subuser.isImageInstalled():
            if subuser.locked:
              self.user.registry.log("Subuser "+subuser.name+" has no image. But is locked. Marking for installation anyways.")
            self.__outOfDateSubusers.add(subuser)
        except (exceptions.ImageBuildException, subuserlib.classes.subuser.NoImageSourceException) as e :
          self.user.registry.log(str(e))
          self.__subusersWhosImagesFailedToBuild.add(subuser)
    outOfDateSubusers = list(self.__outOfDateSubusers)
    outOfDateSubusers.sort(key=lambda s:s.name)
    return outOfDateSubusers

  def isUpToDate(self,imageSource):
    installedImage = imageSource.getLatestInstalledImage()
    if installedImage is None:
      return False
    if not installedImage.isDockerImageThere():
      return False
    targetLineage = getTargetLineage(imageSource)
    installedLineage = installedImage.getImageLineage()
    if not (len(targetLineage) == len(installedLineage)):
      return False
    sideBySideLineages = zip(installedLineage,targetLineage)
    for installed,target in sideBySideLineages:
      if target in self.__outOfDateImageSources:
        return False
      if not installed.imageId == target.getLatestInstalledImage().imageId:
        return False
    if not installedImage.imageSourceHash == imageSource.getHash():
      return False
    if self.op.checkForUpdatesExternally and installedImage.checkForUpdates():
      return False
    return True

  def updateOutOfDateSubusers(self):
    """
    Install new images for those subusers which are out of date.
    """
    parent = None
    for subuser in self.getOutOfDateSubusers():
      try:
        for imageSource in getTargetLineage(subuser.imageSource):
          if imageSource in self.__upToDateImageSources:
            parent = imageSource.getLatestInstalledImage().imageId
          elif imageSource in self.__outOfDateImageSources:
            parent = installImage(imageSource,parent=parent)
            self.__outOfDateImageSources.remove(imageSource)
            self.__upToDateImageSources.add(imageSource)
          else:
            if not self.isUpToDate(imageSource):
              parent = installImage(imageSource,parent=parent)
            else:
              parent = imageSource.getLatestInstalledImage().imageId
            self.__upToDateImageSources.add(imageSource)
        if not subuser.imageId == parent:
          subuser.imageId = parent
          subuser.user.registry.logChange("Installed new image <"+subuser.imageId+"> for subuser "+subuser.name)
      except exceptions.ImageBuildException as e:
        self.user.registry.log(str(e))
        self.__subusersWhosImagesFailedToBuild.add(subuser)

  def getSubusersWhosImagesFailedToBuild(self):
    return self.__subusersWhosImagesFailedToBuild

def installImage(imageSource,parent):
  """
  Install a image by building the given ImageSource.
  Register the newly installed image in the user's InstalledImages list.
  Return the Id of the newly installedImage.
  """
  imageSource.user.registry.logChange("Installing " + imageSource.name + " ...")
  imageId = imageSource.build(parent)
  imageSource.user.installedImages[imageId] = subuserlib.classes.installedImage.InstalledImage(imageSource.user,imageId,imageSource.name,imageSource.repo.name,imageSource.getHash())
  imageSource.user.installedImages.save()
  return imageId
  
def getTargetLineage(imageSource):
  """
  Return the lineage of the ImageSource, going from its base dependency up to itself.
  """
  sourceLineage = []
  while imageSource:
    sourceLineage.append(imageSource)
    imageSource = imageSource.getDependency()
  return list(reversed(sourceLineage))
