# -*- coding: utf-8 -*-

"""
A subuser is an entity that runs within a Docker container and has a home directory and a set of permissions that allow it to access a limited part of the host system.
"""

#external imports
import os
import stat
import errno
import json
import sys
import collections
#internal imports
import subuserlib.permissions
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.permissions import Permissions
from subuserlib.classes.describable import Describable
from subuserlib.classes.subuserSubmodules.run.runtime import Runtime
from subuserlib.classes.subuserSubmodules.run.x11Bridge import X11Bridge
from subuserlib.classes.subuserSubmodules.run.runReadyImage import RunReadyImage
from subuserlib.classes.subuserSubmodules.run.runtimeCache import RuntimeCache

class Subuser(UserOwnedObject, Describable):
  def __init__(self,user,name,imageId,executableShortcutInstalled,locked,serviceSubuserNames,imageSource=None,imageSourceName=None,repoName=None,entrypointsExposed=False,nonDefaultHomeDir=None):
    self.name = name
    self.__imageSource = imageSource
    self.__repoName = repoName
    self.__imageSourceName = imageSourceName
    self.imageId = imageId
    self.executableShortcutInstalled = executableShortcutInstalled
    self.__entryPointsExposed = entrypointsExposed
    self.__entryPointsExposedThisRun = False
    self.locked = locked
    self.serviceSubuserNames = serviceSubuserNames
    self.__x11Bridge = None
    self.__runReadyImage = None
    self.__runtime = None
    self.__runtimeCache = None
    self.__permissions = None
    self.__permissionsTemplate = None
    self.nonDefaultHomeDir = nonDefaultHomeDir
    UserOwnedObject.__init__(self,user)

  @property
  def imageSource(self):
    """
    Note, it is posssible that the subuser's image source no longer exists, in which case this function raises a NoImageSourceException.
    """
    if self.__imageSource is None:
      try:
        self.__imageSource = self.user.registry.repositories[self.__repoName][self.__imageSourceName]
      except KeyError:
        raise NoImageSourceException()
    return self.__imageSource

  @imageSource.setter
  def imageSource(self,new_image_source):
    self.__imageSource=new_image_source
    self.imageId = None

  @property
  def imageSourceName(self):
    if self.__imageSource is None:
      return self.__imageSourceName
    else:
      return self.imageSource.name

  @property
  def sourceRepoName(self):
    if self.__imageSource is None:
      return self.__repoName
    else:
      return self.imageSource.repo.name

  @property
  def entryPointsExposed(self):
    return self.__entryPointsExposed

  @entryPointsExposed.setter
  def entrypointsExposed(self,exposed):
    self.__entryPointsExposed = exposed
    if exposed:
      self.__entryPointsExposedThisRun = True

  def wereEntryPointsExposedThisRun(self):
    return self.__entryPointsExposedThisRun

  @property
  def permissionsDir(self):
    return os.path.join(self.user.config["registry-dir"],"permissions",self.name)

  @property
  def relativePermissionsDir(self):
    """
    Get the permissions directory as relative to the registry's git repository.
    """
    return os.path.join("permissions",self.name)

  def createPermissions(self,permissionsDict):
    permissionsDotJsonWritePath = os.path.join(self.permissionsDir,"permissions.json")
    self.__permissions = Permissions(self.user,initialPermissions=permissionsDict,writePath=permissionsDotJsonWritePath)
    return self.__permissions

  @property
  def permissionsDotJsonWritePath(self):
    return os.path.join(self.permissionsDir,"permissions.json")

  def loadPermissions(self):
    registryFileStructure = self.user.registry.gitRepository.getFileStructureAtCommit(self.user.registry.gitReadHash)
    try:
      initialPermissions = subuserlib.permissions.load(permissionsString=registryFileStructure.read(os.path.join(self.relativePermissionsDir,"permissions.json")),logger=self.user.registry)
    except OSError:
      raise SubuserHasNoPermissionsException("The subuser <"+self.name+"""> has no permissions.

Please run:

$ subuser repair

To repair your subuser installation.\n""")
    except SyntaxError as e:
      sys.exit("The subuser <"+self.name+""">'s permissions appear to be corrupt.

Please file a bug report explaining how you got here.\n"""+ str(e))
    self.__permissions = Permissions(self.user,initialPermissions,writePath=self.permissionsDotJsonWritePath)

  @property
  def permissions(self):
    if self.__permissions is None:
      self.loadPermissions()
    return self.__permissions

  def getPermissionsTemplate(self):
    if self.__permissionsTemplate is None:
      permissionsDotJsonWritePath = os.path.join(self.permissionsDir,"permissions-template.json")
      registryFileStructure = self.user.registry.gitRepository.getFileStructureAtCommit(self.user.registry.gitReadHash)
      if "permissions-template.json" in registryFileStructure.lsFiles(self.relativePermissionsDir):
        initialPermissions = subuserlib.permissions.load(permissionsString=registryFileStructure.read(os.path.join(self.relativePermissionsDir,"permissions-template.json")),logger=self.user.registry)
        save = False
      else:
        initialPermissions = self.imageSource.permissions
        save = True
      self.__permissionsTemplate = Permissions(self.user,initialPermissions,writePath=permissionsDotJsonWritePath)
      if save:
        self.__permissionsTemplate.save()
    return self.__permissionsTemplate

  def editPermissionsCLI(self):
    while True:
      self.user.endUser.runEditor(self.permissions.writePath)
      try:
        initialPermissions = subuserlib.permissions.load(permissionsFilePath=self.permissionsDotJsonWritePath)
        break
      except SyntaxError as e:
        print(e)
        input("Press ENTER to edit the permission file again.")
    self.__permissions = Permissions(self.user,initialPermissions,writePath=self.permissionsDotJsonWritePath)
    self.permissions.save()

  def removePermissions(self):
    """
    Remove the user set and template permission files.
    """
    try:
      self.user.registry.gitRepository.run(["rm",os.path.join(self.relativePermissionsDir,"permissions.json"),os.path.join(self.relativePermissionsDir,"permissions-template.json")])
    except subuserlib.classes.gitRepository.GitException:
      pass
    try:
      self.user.registry.gitRepository.run(["rm",os.path.join(self.relativePermissionsDir,"permissions.json"),os.path.join(self.relativePermissionsDir,"permissions-template.json")])
    except subuserlib.classes.gitRepository.GitException:
      pass

  def isImageInstalled(self):
    return self.user.dockerDaemon.getImageProperties(self.imageId) is not None

  def getRunReadyImage(self):
    if not self.__runReadyImage:
      self.__runReadyImage = RunReadyImage(self.user,self)
    return self.__runReadyImage

  @property
  def x11Bridge(self):
    """
    Return the X11 bridge object for this subuser.
    """
    if not self.__x11Bridge:
      self.__x11Bridge = X11Bridge(self.user,self)
    return self.__x11Bridge

  #TODO clean this up so that we aren't forwarding arguments in needless fluff.
  def getRuntime(self,environment,extraDockerFlags=None,entrypoint=None):
    """
    Returns the subuser's Runtime object for it's current permissions, creating it if necessary.
    """
    if not self.__runtime:
      self.__runtime = Runtime(self.user,subuser=self,environment=environment,extraDockerFlags=extraDockerFlags,entrypoint=entrypoint)
    return self.__runtime

  def getRuntimeCache(self):
    if not self.__runtimeCache:
      self.__runtimeCache = RuntimeCache(self.user,self)
    else:
      self.__runtimeCache.reload()
    return self.__runtimeCache

  def setupHomeDir(self):
    """
    Sets up the subuser's home dir, along with creating symlinks to shared user dirs.
    """
    if self.permissions["basic-common-permissions"] and self.permissions["basic-common-permissions"]["stateful-home"]:
      try:
        self.user.endUser.makedirs(self.homeDirOnHost)
      except OSError as e:
        if e.errno() == errno.EEXIST:
          pass
      if self.permissions["user-dirs"]:
        for userDir in self.permissions["user-dirs"]:
          symlinkPath = os.path.join(self.homeDirOnHost,userDir)
          # https://stackoverflow.com/questions/15718006/check-if-directory-is-symlink
          if symlinkPath.endswith("/"):
            symlinkPath = symlinkPath[:-1]
          destinationPath = os.path.join("/subuser/userdirs",userDir)
          if not os.path.islink(symlinkPath):
            if os.path.exists(symlinkPath):
              self.user.endUser.makedirs(os.path.join(self.homeDirOnHost,"subuser-user-dirs-backups"))
              os.rename(symlinkPath,os.path.join(self.homeDirOnHost,"subuser-user-dirs-backups",userDir))
            try:
              os.symlink(destinationPath,symlinkPath)
              # Arg, why are source and destination switched?
              # os.symlink(where does the symlink point to, where is the symlink)
              # I guess it's to be like cp...
            except OSError:
              pass

  @property
  def homeDirOnHost(self):
    """
    Returns the path to the subuser's home dir. Unless the subuser is configured to have a stateless home, in which case returns None.
    """
    if self.permissions["basic-common-permissions"]["stateful-home"]:
      if self.nonDefaultHomeDir is not None:
        return self.nonDefaultHomeDir
      return os.path.join(self.user.config["subuser-home-dirs-dir"],self.name)
    else:
      return None

  @property
  def dockersideHome(self):
    if self.permissions["as-root"]:
      return "/root/"
    else:
      return self.user.endUser.homeDir

  def describe(self):
    print("Subuser: "+self.name)
    print("------------------")
    try:
      print(self.imageSource.getIdentifier())
    except subuserlib.classes.subuser.NoImageSourceException:
      print("Warning: This subuser has no image, nor does it have a valid image source to install an image from.")
    print("Docker image Id: "+str(self.imageId))
    self.permissions.describe()
    print("")

  def installLaunchScript(self,name,script):
    """
    Install a trivial executable script into the PATH which launches the subser image.
    """
    redirect = script
    executablePath=os.path.join(self.user.config["bin-dir"], name)
    with self.user.endUser.get_file(executablePath, 'w') as file_f:
      file_f.write(redirect)
      st = os.stat(executablePath)
      os.chmod(executablePath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

  def installExecutableShortcut(self):
    self.installLaunchScript(self.name,"#!/bin/bash\nsubuser run "+self.name+" $@")

  def exposeEntrypoints(self):
    """
    Create launcher executables for the subuser's entrypoints.
    """
    for name,path in self.permissions["entrypoints"].items():
      launchScript = """#!/usr/bin/python3
import subprocess,sys
run = """+json.dumps({"subuser-name":self.name,"entrypoint":path})
      launchScript +="""
sys.exit(subprocess.call(["subuser","run","--entrypoint="+run["entrypoint"],run["subuser-name"]]))
"""
      self.installLaunchScript(name,launchScript)

class SubuserHasNoPermissionsException(Exception):
  pass

class NoImageSourceException(Exception):
  pass
