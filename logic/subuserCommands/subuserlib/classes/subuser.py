#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess,os
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.classes.imageSource,subuserlib.classes.permissions,subuserlib.classes.describable

class Subuser(subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.describable.Describable):
  __name = None
  __imageSource = None
  __imageId = None
  __executableShortcutInstalled = None

  def __init__(self,user,name,imageSource,imageId,executableShortcutInstalled):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__name = name
    self.__imageSource = imageSource
    self.__imageId = imageId
    self.__executableShortcutInstalled = executableShortcutInstalled

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
  
  def getSetupSymlinksScriptPathOnHost(self):
    """
    For each subuser we have a docker-side script which sets up various symlinks within the container.  This function returns a path to that script as cached on the host side.
    """
    return os.path.join(self.getUser().homeDir,".subuser","cache","by-subuser",self.getName(),"setup-symlinks")
  
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
  
