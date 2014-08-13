#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
#import ...
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.dockerImages,subuserlib.dockerPs

class InstalledImage(subuserlib.classes.userOwnedObject.UserOwnedObject):
  __imageID = None
  __lastUpdateTime = None

  def __init__(self,user,imageID,lastUpdateTime):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__imageID = imageID
    self.__lastUpdateTime = lastUpdateTime

  def getImageID(self):
    return self.__imageID

  def getLastUpdateTime(self):
    return self.__lastUpdateTime

  def isDockerImageThere(self):
    """
     Does the Docker daemon have an image with this imageID?
    """
    return not subuserlib.dockerImages.inspectImage(self.getImageId()) == None

  def removeDockerImage(self):
    """
      Remove the image from the Docker daemon's image store.
    """
    subuserlib.dockerImages.removeImage(self.getImageID())
