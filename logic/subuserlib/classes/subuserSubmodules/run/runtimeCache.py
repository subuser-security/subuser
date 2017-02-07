# -*- coding: utf-8 -*-

"""
Stores metadata about images which are built to encorporate changes to subuser images which are required in order to implement various permissions.
"""

#external imports
import os
import json
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.fileBackedObject import FileBackedObject

class RuntimeCache(dict,UserOwnedObject,FileBackedObject):
  def __init__(self,user,subuser):
    self.__subuser = subuser
    UserOwnedObject.__init__(self,user)
    self.load()

  def getPathToCurrentImagesRuntimeCacheDir(self):
    return os.path.join(self.getUser().getConfig()["runtime-cache"],self.getSubuser().getImageId())

  def getRuntimeCacheFilePath(self):
    return os.path.join(self.getPathToCurrentImagesRuntimeCacheDir(),self.getSubuser().getPermissions().getHash()+".json")

  def getSubuser(self):
    return self.__subuser

  def save(self):
    try:
      self.getUser().getEndUser().makedirs(self.getPathToCurrentImagesRuntimeCacheDir())
    except OSError:
      pass
    with self.getUser().getEndUser().get_file(self.getRuntimeCacheFilePath(),mode='w') as runtimeCacheFileHandle:
      json.dump(self,runtimeCacheFileHandle,indent=1,separators=(',',': '))

  def reload(self):
    self.save()
    self.load()

  def load(self):
    if not self.getSubuser().getImageId():
      raise NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException("No runnable image for subuser "+self.getSubuser().getName()+" found. Use\n\n $ subuser repair\n\nTo repair your instalation.")
    runtimeCacheFilePath = self.getRuntimeCacheFilePath()
    if os.path.exists(runtimeCacheFilePath):
      with open(runtimeCacheFilePath,mode="r") as runtimeCacheFileHandle:
        runtimeCacheInfo = json.load(runtimeCacheFileHandle)
        self.update(runtimeCacheInfo)

class NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException(Exception):
  pass
