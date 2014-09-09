#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import uuid
#internal imports
import subuserlib.classes.userOwnedObject

class MockDockerDaemon(subuserlib.classes.userOwnedObject.UserOwnedObject):
  images = {}
  nextImageId = 1

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    for imageId in user.getInstalledImages().keys():
      self.images[imageId] = {"Id":imageId,"Parent":""}

  def getImageProperties(self,imageTagOrId):
    """
     Returns a dictionary of image properties, or None if the image does not exist.
    """
    if imageTagOrId in self.images:
      return self.images[imageTagOrId]
    else:
      return None

  def build(self,directoryWithDockerfile,useCache=True,rm=False,forceRm=False,quiet=False,tag=None,dockerfile=None):
    """
    Build a Docker image.  If a the dockerfile argument is set to a string, use that string as the Dockerfile.  Return the newly created images Id or raises an exception if the build fails.  
    """
    while str(self.nextImageId) in self.images:
      self.nextImageId = self.nextImageId+1
    newId = str(self.nextImageId)
    parent = dockerfile.split(" ")[1].rstrip()
    if "debian" in dockerfile:
      parent = ""
    self.images[newId] = {"Id":newId,"Parent":parent}
    return newId

  def removeImage(self,imageId):
    del self.images[imageId]

  def execute(self,args,cwd=None):
    pass
