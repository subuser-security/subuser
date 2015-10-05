#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
The ``User`` object is the base object which owns all other objects in a running subuser instance.
"""

#external imports
import getpass
import os
import sys
import pwd
#internal imports
from subuserlib.classes import registry
from subuserlib.classes import config
from subuserlib.classes import installedImages
from subuserlib.classes.docker import dockerDaemon
from subuserlib import test
from subuserlib import paths

class User(object):
  """
  This class provides a "base" User object used by subuser.  This is the stem of a tree like data structure which holds all of the various objects owned by a given user.

  You create a new User object by passing the username and home dir of the user.

  >>> import subuserlib.classes.user
  >>> u = subuserlib.classes.user.User("root",homeDir="/root/")
  >>> u.homeDir
  '/root/'
  """
  def __init__(self,name=None,uid=None,gid=None,homeDir=None):
    self.__config = None
    self.__registry = None
    self.__installedImages = None
    self.__dockerDaemon = None
    self.__runtimeCache = None
    if homeDir:
      self.homeDir = homeDir
    else:
      if test.testing:
        self.homeDir = "/home/travis/test-home"
      else:
        self.homeDir = os.path.expanduser("~")
    if name:
      self.name = name
    else:
      try:
        self.name = self.getConfig()["user"]
      except KeyError:
        try:
          self.name = getpass.getuser()
        except KeyError:
          # We use a broken setup when generating documentation...
          self.name = "I have no name!"
    if test.testing:
      uid = 1000
      gid = 1000
    if uid is not None:
      self.uid = uid
    else:
      self.uid = pwd.getpwnam(self.name)[2]
    if gid is not None:
      self.gid = gid
    else:
      self.gid = pwd.getpwnam(self.name)[3]
    if os.getuid() == 0 and not self.uid == 0:
      self.rootProxy = True
    else:
      self.rootProxy = False

  def getConfig(self):
    """
    Get the user's :doc:`Config <config>` object.

    Note: the user's config will be loaded the first time this is called.
    """
    if self.__config == None:
      self.__config = config.Config(self)
    return self.__config

  def getRegistry(self):
    """
    Get the user's subuser :doc:`Registry <registry>`.

    Note: the registry will be loaded the first time this is called.
    """
    if self.__registry == None:
      self.__registry = registry.Registry(self)
    return self.__registry

  def reloadRegistry(self):
    """
    Reload registry from disk.
    """
    self.__registry = None

  def getInstalledImages(self):
    """
    Get the user's  :doc:`InstalledImages <installed-images>` list.

    Note: the installed images list will be loaded the first time this is called.
    """
    if self.__installedImages == None:
      self.__installedImages = installedImages.InstalledImages(self)
    return self.__installedImages

  def getDockerDaemon(self):
    """
    Get the :doc:`DockerDaemon <docker>` object.  You will use this to communicate with the Docker daemon.
    """
    if self.__dockerDaemon == None:
      self.__dockerDaemon = dockerDaemon.DockerDaemon(self)
    return self.__dockerDaemon

  def chown(self,path):
    """
    Make this user own the given file if subuser is running as root.
    """
    if self.rootProxy:
      os.chown(path,self.uid,self.gid)

  def makedirs(self,path):
    """
    Create directory + parents, if the directory does not yet exist. Newly created directories will be owned by the user.
    """
    # Taken from http://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python
    folders = []
    while 1:
      path, folder = os.path.split(path)
      if folder:
        folders.append(folder)
      else:
        if path:
          folders.append(path)
        break
    pathBeingBuilt = "/"
    for folder in reversed(folders):
      pathBeingBuilt = os.path.join(pathBeingBuilt,folder)
      if not os.path.exists(pathBeingBuilt):
        os.mkdir(pathBeingBuilt)
        if self.rootProxy:
          os.chown(pathBeingBuilt,self.uid,self.gid)
