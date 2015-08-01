#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
A subuser is an entity that runs within a Docker container and has a home directory and a set of permissions that allow it to access a limited part of the host system.
"""

#external imports
import os
import stat
import json
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.permissions import Permissions
from subuserlib.classes.describable import Describable
from subuserlib.classes.subuserSubmodules.run.runtime import Runtime
from subuserlib.classes.subuserSubmodules.run.x11Bridge import X11Bridge
from subuserlib.classes.subuserSubmodules.run.runReadyImage import RunReadyImage
from subuserlib.classes.subuserSubmodules.run.runtimeCache import RuntimeCache

class Subuser(UserOwnedObject, Describable):
  def __init__(self,user,name,imageSource,imageId,executableShortcutInstalled,locked,serviceSubusers):
    self.__name = name
    self.__imageSource = imageSource
    self.__imageId = imageId
    self.__executableShortcutInstalled = executableShortcutInstalled
    self.__locked = locked
    self.__serviceSubusers = serviceSubusers
    self.__x11Bridge = None
    self.__runReadyImage = None
    self.__runtime = None
    self.__runtimeCache = None
    self.__permissions = None
    UserOwnedObject.__init__(self,user)

  def getName(self):
    return self.__name

  def getImageSource(self):
    return self.__imageSource

  def isExecutableShortcutInstalled(self):
    return self.__executableShortcutInstalled

  def setExecutableShortcutInstalled(self,installed):
    self.__executableShortcutInstalled = installed

  def getPermissions(self):
    if self.__permissions is None:
      permissionsDotJsonWritePath = os.path.join(self.getUser().getConfig()["user-set-permissions-dir"],self.getName(),"permissions.json")
      permissionsDotJsonReadPath = permissionsDotJsonWritePath
      if not os.path.exists(permissionsDotJsonReadPath):
        permissionsDotJsonReadPath = os.path.join(self.getImageSource().getSourceDir(),"permissions.json")
      if not os.path.exists(permissionsDotJsonReadPath):
        permissionsDotJsonReadPath = None
      self.__permissions = Permissions(self.getUser(),readPath=permissionsDotJsonReadPath,writePath=permissionsDotJsonWritePath)
    return self.__permissions
  
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

  def getServiceSubuserNames(self):
    """
    Get this subuser's service subusers.
    """
    return self.__serviceSubusers

  def addServiceSubuser(self,name):
    self.__serviceSubusers.append(name)

  def getRunReadyImage(self):
    if not self.__runReadyImage:
      self.__runReadyImage = RunReadyImage(self.getUser(),self)
    return self.__runReadyImage

  def getX11Bridge(self):
    """
    Return the X11 bridge object for this subuser.
    """
    if not self.__x11Bridge:
      self.__x11Bridge = X11Bridge(self.getUser(),self)
    return self.__x11Bridge

  def getRuntime(self,environment):
    """
    Returns the subuser's Runtime object for it's current permissions, creating it if necessary.
    """
    if not self.__runtime:
      self.__runtime = Runtime(self.getUser(),subuser=self,environment=environment)
    return self.__runtime

  def getRuntimeCache(self):
    if not self.__runtimeCache:
      self.__runtimeCache = RuntimeCache(self.getUser(),self)
    return self.__runtimeCache

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
      return os.path.join(self.getUser().getConfig()["subuser-home-dirs-dir"],self.getName())
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
    executablePath=os.path.join(self.getUser().getConfig()["bin-dir"], self.getName())
    with open(executablePath, 'w') as file_f:
      file_f.write(redirect)
      st = os.stat(executablePath)
      os.chmod(executablePath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

