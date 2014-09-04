#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
#import ..
#internal imports
import subuserlib.classes.userOwnedObject

class MockDockerDaemon(subuserlib.classes.userOwnedObject.UserOwnedObject):
  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)

  def getImageProperties(self,imageTagOrId):
    """
     Returns a dictionary of image properties, or None if the image does not exist.
    """
    if imageTagOrId in self.getUser().getInstalledImages():
      return {}
    return None

  def build(self,directoryWithDockerfile,useCache=True,rm=False,forceRm=False,quiet=False,tag=None,dockerfile=None):
    """
    Build a Docker image.  If a the dockerfile argument is set to a string, use that string as the Dockerfile.  Return the newly created images Id or raises an exception if the build fails.  
    """
    return "Mock image Id"

  def execute(self,args,cwd=None):
    pass
