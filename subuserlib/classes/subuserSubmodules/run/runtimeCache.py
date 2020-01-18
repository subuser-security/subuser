# -*- coding: utf-8 -*-

"""
Stores metadata about images which are built to encorporate changes to subuser images which are required in order to implement various permissions.
"""

#external imports
import os
import json
from collections import OrderedDict
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.fileBackedObject import FileBackedObject

class RuntimeCache(dict,UserOwnedObject,FileBackedObject):
  def __init__(self,user,subuser):
    self.subuser = subuser
    UserOwnedObject.__init__(self,user)
    self.load()

  @property
  def pathToCurrentImagesRuntimeCacheDir(self):
    return os.path.join(self.user.config["runtime-cache"],self.subuser.imageId)

  @property
  def runtimeCacheFilePath(self):
    return os.path.join(self.pathToCurrentImagesRuntimeCacheDir,self.subuser.getRunReadyImage().sourceHash+".json")

  def save(self):
    try:
      self.user.endUser.makedirs(self.pathToCurrentImagesRuntimeCacheDir)
    except OSError:
      pass
    with self.user.endUser.get_file(self.runtimeCacheFilePath,mode='w') as runtimeCacheFileHandle:
      json.dump(self,runtimeCacheFileHandle,indent=1,separators=(',',': '))

  def reload(self):
    self.save()
    self.load()

  def load(self):
    if not self.subuser.imageId:
      raise NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException("No runnable image for subuser "+self.subuser.name+" found. Use\n\n $ subuser repair\n\nTo repair your instalation.")
    runtimeCacheFilePath = self.runtimeCacheFilePath
    if os.path.exists(runtimeCacheFilePath):
      with open(runtimeCacheFilePath,mode="r") as runtimeCacheFileHandle:
        runtimeCacheInfo = json.load(runtimeCacheFileHandle, object_pairs_hook=OrderedDict)
        self.update(runtimeCacheInfo)

class NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException(Exception):
  pass
