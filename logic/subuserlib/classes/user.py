# -*- coding: utf-8 -*-

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
from subuserlib.classes.endUser import EndUser
from subuserlib import test
from subuserlib import paths

class User(object):
  """
  This class provides a "base" User object used by subuser.  This is the stem of a tree like data structure which holds all of the various objects owned by a given user.

  You create a new User object by passing the username and home dir of the user.

  >>> import subuserlib.classes.user
  >>> u = subuserlib.classes.user.User(name="root",homeDir="/root/")
  >>> u.homeDir
  '/root/'
  """
  def __init__(self,name=None,homeDir=None):
    self.__config = None
    self.__registry = None
    self.__installedImages = None
    self.__dockerDaemon = None
    self.__runtimeCache = None
    self.name = name
    if homeDir:
      self.homeDir = homeDir
    elif test.testing:
      self.homeDir = os.getcwd()
    else:
      self.homeDir = os.path.expanduser("~")
    self.__endUser = EndUser(self)

  def getEndUser(self):
    return self.__endUser

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
      self.__registry.ensureGitRepoInitialized()
    return self.__registry

  def setRegistry(self, registry):
    self.__registry = registry

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
