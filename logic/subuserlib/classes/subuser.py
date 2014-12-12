#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
A subuser is an entity that runs within a Docker container and has a home directory and a set of permissions that allow it to access a limited part of the host system.
"""

#external imports
import os,stat,json
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.classes.imageSource,subuserlib.classes.permissions,subuserlib.classes.describable,subuserlib.runReadyImages,subuserlib.classes.runtime

class Subuser(subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.describable.Describable):
  __name = None
  __imageSource = None
  __imageId = None
  __executableShortcutInstalled = None

  def __init__(self,user,name,imageSource,imageId,executableShortcutInstalled,locked):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__name = name
    self.__imageSource = imageSource
    self.__imageId = imageId
    self.__executableShortcutInstalled = executableShortcutInstalled
    self.__locked = locked

  def getName(self):
    return self.__name

  def getImageSource(self):
    return self.__imageSource

  def isExecutableShortcutInstalled(self):
    return self.__executableShortcutInstalled

  def setExecutableShortcutInstalled(self,installed):
    self.__executableShortcutInstalled = installed

  def getPermissions(self):
    permissionsDotJsonWritePath = os.path.join(self.getUser().getConfig().getUserSetPermissionsDir(),self.getName(),"permissions.json")
    permissionsDotJsonReadPath = permissionsDotJsonWritePath
    if not os.path.exists(permissionsDotJsonReadPath):
      permissionsDotJsonReadPath = os.path.join(self.getImageSource().getSourceDir(),"permissions.json")
    if not os.path.exists(permissionsDotJsonReadPath):
      permissionsDotJsonReadPath = None
    return subuserlib.classes.permissions.Permissions(self.getUser(),readPath=permissionsDotJsonReadPath,writePath=permissionsDotJsonWritePath)

  def getImageId(self):
    """
     Get the Id of the Docker image associated with this subuser.
     None, if the subuser has no installed image yet.
    """
    return self.__imageId

  def setImageId(self,imageId):
    """
    Set the installed image associated with this subuser.
    """
    self.__imageId = imageId

  def getRuntime(self,environment):
    """
    Returns the subuser's Runtime object for it's current permissions, creating it if necessary.
    """
    pathToCurrentImagesRuntimeCacheDir = os.path.join(self.getUser().getConfig().getRuntimeCache(),self.getImageId())
    pathToRuntimeCacheFile = os.path.join(pathToCurrentImagesRuntimeCacheDir,self.getPermissions().getHash()+".json")
    if os.path.exists(pathToRuntimeCacheFile):
      with open(pathToRuntimeCacheFile,mode="r") as runtimeCacheFileHandle:
        runtimeCacheInfo = json.load(runtimeCacheFileHandle)
        return subuserlib.classes.runtime.Runtime(self.getUser(),subuser=self,runReadyImageId=runtimeCacheInfo['run-ready-image-id'],environment=environment)
    try:
      os.makedirs(pathToCurrentImagesRuntimeCacheDir)
    except OSError:
      pass
    runReadyImageId = subuserlib.runReadyImages.buildRunReadyImageForSubuser(self)
    runtimeInfo = {}
    runtimeInfo['run-ready-image-id'] = runReadyImageId
    with open(pathToRuntimeCacheFile,mode='w') as runtimeCacheFileHandle:
      json.dump(runtimeInfo,runtimeCacheFileHandle,indent=1,separators=(',',': '))
    return subuserlib.classes.runtime.Runtime(self.getUser(),subuser=self,runReadyImageId=runReadyImageId,environment=environment)

  def locked(self):
    """
    Returns True if the subuser is locked.  Users lock subusers in order to prevent updates and rollbacks from effecting them.
    """
    return self.__locked

  def setLocked(self,locked):
    """
    Mark the subuser as locked or unlocked.

    We lock subusers to their current states to prevent updates and rollbacks from effecting them.
    """
    self.__locked = locked

  def getHomeDirOnHost(self):
    """
    Returns the path to the subuser's home dir. Unless the subuser is configured to have a stateless home, in which case returns None.
    """
    if self.getPermissions()["stateful-home"]:
      return os.path.join(self.getUser().getConfig().getSubuserHomeDirsDir(),self.getName())
    else:
      return None

  def getDockersideHome(self):
    if self.getPermissions()["as-root"]:
      return "/root/"
    else:
      return self.getUser().homeDir

  def describe(self):
    print("Subuser: "+self.getName())
    print("------------------")
    print("Progam:")
    self.getImageSource().describe()

  def installExecutableShortcut(self):
    """
     Install a trivial executable script into the PATH which launches the subser image.
    """
    redirect="""#!/bin/bash
  subuser run """+self.getName()+""" $@
  """
    executablePath=os.path.join(self.getUser().getConfig().getBinDir(), self.getName())
    with open(executablePath, 'w') as file_f:
      file_f.write(redirect)
      st = os.stat(executablePath)
      os.chmod(executablePath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

