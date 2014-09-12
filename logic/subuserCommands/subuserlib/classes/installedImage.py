#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
#import ...
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.dockerImages

class InstalledImage(subuserlib.classes.userOwnedObject.UserOwnedObject):
  __imageId = None
  __lastUpdateTime = None
  __imageSourceName = None
  __sourceRepoId = None

  def __init__(self,user,imageId,imageSourceName,sourceRepoId,lastUpdateTime):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__imageId = imageId
    self.__lastUpdateTime = lastUpdateTime
    self.__imageSourceName = imageSourceName
    self.__sourceRepoId = sourceRepoId

  def getImageId(self):
    return self.__imageId

  def getSourceRepoId(self):
    return self.__sourceRepoId

  def getImageSourceName(self):
    return self.__imageSourceName

  def getLastUpdateTime(self):
    return self.__lastUpdateTime

  def isDockerImageThere(self):
    """
     Does the Docker daemon have an image with this imageId?
    """
    return not (self.getUser().getDockerDaemon().getImageProperties(self.getImageId()) == None)

  def removeDockerImage(self):
    """
      Remove the image from the Docker daemon's image store.
    """
    self.getUser().getDockerDaemon().removeImage(self.getImageId())
