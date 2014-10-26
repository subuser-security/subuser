#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
# pylint: disable=unused-argument

"""
In order to make our test suit work, we must use a MockDockerDaemon rather than communicating with a real Docker instance.
"""

#external imports
import json,os
#internal imports
import subuserlib.classes.userOwnedObject

class MockDockerDaemon(subuserlib.classes.userOwnedObject.UserOwnedObject):
  images = {}
  nextImageId = 1

  def __load(self):
    with open(self.imagesPath,"r") as imagesFile:
      self.images = json.load(imagesFile)

  def __save(self):
    with open(self.imagesPath,"w") as imagesFile:
      json.dump(self.images,imagesFile)

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.imagesPath = "/root/subuser/test/docker/images.json"
    if not os.path.exists(self.imagesPath):
      self.imagesPath = "/home/travis/build/subuser-security/subuser/test/docker/images.json"
    self.__load()

  def getImageProperties(self,imageTagOrId):
    """
     Returns a dictionary of image properties, or None if the image does not exist.
    """
    if imageTagOrId in self.images:
      return self.images[imageTagOrId]
    else:
      return None

  def build(self,directoryWithDockerfile=None,useCache=True,rm=False,forceRm=False,quiet=False,tag=None,dockerfile=None):
    """
    Build a Docker image.  If a the dockerfile argument is set to a string, use that string as the Dockerfile.  Return the newly created images Id or raises an exception if the build fails.
    """
    while str(self.nextImageId) in self.images:
      self.nextImageId = self.nextImageId+1
    newId = str(self.nextImageId)
    parent = dockerfile.split("\n")[0].split(" ")[1].rstrip()
    if "debian" in dockerfile:
      parent = ""
    self.images[newId] = {"Id":newId,"Parent":parent}
    self.__save()
    return newId

  def removeImage(self,imageId):
    del self.images[imageId]
    self.__save()

  def execute(self,args,cwd=None):
    pass
