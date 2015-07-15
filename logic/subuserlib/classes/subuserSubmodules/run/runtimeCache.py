#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Stores metadata about images which are built to encorporate changes to subuser images which are required in order to implement various permissions.
"""

#external imports
import sys,os,getpass,json
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.fileBackedObject import FileBackedObject

class RuntimeCache(dict,UserOwnedObject,FileBackedObject):
  __subuser = None
  __pathToRuntimeCacheFile = None

  def getPathToCurrentImagesRuntimeCacheDir(self):
    return os.path.join(self.getUser().getConfig()["runtime-cache"],self.getSubuser().getImageId())

  def __init__(self,user,subuser):
    UserOwnedObject.__init__(self,user)
    self.__subuser = subuser
    if not self.getSubuser().getImageId():
      raise NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException
    self.__pathToRuntimeCacheFile = os.path.join(self.getPathToCurrentImagesRuntimeCacheDir(),self.getSubuser().getPermissions().getHash()+".json")
    self.load()

  def getSubuser(self):
    return self.__subuser

  def save(self):
    try:
      os.makedirs(self.getPathToCurrentImagesRuntimeCacheDir())
    except OSError:
      pass
    with open(self.__pathToRuntimeCacheFile,mode='w') as runtimeCacheFileHandle:
      json.dump(self,runtimeCacheFileHandle,indent=1,separators=(',',': '))

  def load(self):
    if os.path.exists(self.__pathToRuntimeCacheFile):
      with open(self.__pathToRuntimeCacheFile,mode="r") as runtimeCacheFileHandle:
        runtimeCacheInfo = json.load(runtimeCacheFileHandle)
        self.update(runtimeCacheInfo)

class NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException(Exception):
  pass
