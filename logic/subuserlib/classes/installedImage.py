#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Each user has a set of images that have been installed.
"""

#external imports
import os,json
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.classes.describable

class InstalledImage(subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.describable.Describable):
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

  def getImageSource(self):
    return self.getUser().getRegistry().getRepositories()[self.getSourceRepoId()][self.getImageSourceName()]

  def getLastUpdateTime(self):
    return self.__lastUpdateTime

  def isDockerImageThere(self):
    """
     Does the Docker daemon have an image with this imageId?
    """
    return not (self.getUser().getDockerDaemon().getImageProperties(self.getImageId()) == None)

  def removeCachedRuntimes(self):
    """
    Remove cached runtime environments.
    """
    pathToImagesRuntimeCacheDir = os.path.join(self.getUser().getConfig()["runtime-cache"],self.getImageId())
    try:
      for permissionsSpecificCacheInfoFileName in os.listdir(pathToImagesRuntimeCacheDir):
        permissionsSpecificCacheInfoFilePath = os.path.join(pathToImagesRuntimeCacheDir,permissionsSpecificCacheInfoFileName)
        with open(permissionsSpecificCacheInfoFilePath,mode='r') as permissionsSpecificCacheInfoFileHandle:
          permissionsSpecificCacheInfo = json.load(permissionsSpecificCacheInfoFileHandle)
          self.getUser().getDockerDaemon().removeImage(permissionsSpecificCacheInfo['run-ready-image-id'])
          os.remove(permissionsSpecificCacheInfoFilePath)
    except OSError:
      pass
  
  def removeDockerImage(self):
    """
      Remove the image from the Docker daemon's image store.
    """
    try:
      self.getUser().getDockerDaemon().removeImage(self.getImageId())
    except subuserlib.classes.dockerDaemon.ImageDoesNotExistsException:
      pass

  def describe(self):
    print("Image Id: "+self.getImageId())
    try:
      print("Image source: "+self.getImageSource().getIdentifier())
    except KeyError:
      print("Image is broken, image source does not exist!")
    print("Last update time: "+self.getLastUpdateTime())

