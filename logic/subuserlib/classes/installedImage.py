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
  __imageSourceHash = None
  __imageSourceName = None
  __sourceRepoId = None
  __alreadyCheckedForUpdates = None

  def __init__(self,user,imageId,imageSourceName,sourceRepoId,imageSourceHash):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__imageId = imageId
    self.__imageSourceHash = imageSourceHash
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

  def getImageSourceHash(self):
    return self.__imageSourceHash

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
          try:
            try:
              self.getUser().getDockerDaemon().removeImage(permissionsSpecificCacheInfo['run-ready-image-id'])
            except subuserlib.classes.dockerDaemon.ImageDoesNotExistsException:
              pass
            os.remove(permissionsSpecificCacheInfoFilePath)
          except subuserlib.classes.dockerDaemon.ContainerDependsOnImageException:
            pass
    except OSError:
      pass
  
  def removeDockerImage(self):
    """
      Remove the image from the Docker daemon's image store.
    """
    try:
      self.getUser().getDockerDaemon().removeImage(self.getImageId())
    except (subuserlib.classes.dockerDaemon.ImageDoesNotExistsException,subuserlib.classes.dockerDaemon.ContainerDependsOnImageException,subuserlib.classes.dockerDaemon.ServerErrorException):
      pass

  def describe(self):
    print("Image Id: "+self.getImageId())
    try:
      print("Image source: "+self.getImageSource().getIdentifier())
    except KeyError:
      print("Image is broken, image source does not exist!")
    print("Last update time: "+self.getCreationDateTime())

  def checkForUpdates(self):
    """ Check for updates using the image's built in check-for-updates script. This launches the script as root in a privilageless container. Returns True if the image needs to be updated. """
    if self.__alreadyCheckedForUpdates:
      return False
    self.__alreadyCheckedForUpdates = True
    if self.getUser().getDockerDaemon().execute(["run",self.getImageId(),"test","-e","/subuser/check-for-updates"]) == 0:
      returnCode = self.getUser().getDockerDaemon().execute(["run",self.getImageId(),"/subuser/check-for-updates"])
      if returnCode == 0:
        return True
    return False

  def getCreationDateTime(self):
    """ Return the creation date/time of the installed docker image. Or None if the image does not exist. """
    imageProperties = self.getUser().getDockerDaemon().getImageProperties(self.getImageId())
    if not imageProperties is None:
      return imageProperties["Created"]
    else:
      return None
