# -*- coding: utf-8 -*-

"""
The ``User`` object is the base object which owns all other objects in a running subuser instance.
"""

#external imports
import getpass
import os
import sys
import pwd
import errno
#internal imports
from subuserlib.classes import registry
from subuserlib.classes import config
from subuserlib.classes import installedImages
from subuserlib.classes.docker import dockerDaemon
from subuserlib.classes.endUser import EndUser
from subuserlib.classes.operation import Operation
from subuserlib import test
from subuserlib import paths
import subuserlib.lock

class User(object):
  """
  This class provides a "base" User object used by subuser.  This is the stem of a tree like data structure which holds all of the various objects owned by a given user.

  You create a new User object by passing the username and home dir of the user.

  >>> import subuserlib.classes.user
  >>> u = subuserlib.classes.user.User(name="root",homeDir="/root/")
  >>> u.homeDir
  '/root/'
  """
  def __init__(self,name=None,homeDir=None,_locked=False):
    self.__config = None
    self.__registry = None
    self.__installedImages = None
    self.__dockerDaemon = None
    self.__runtimeCache = None
    self.__operation = None
    self._has_lock = _locked
    self.name = name
    if homeDir:
      self.homeDir = homeDir
    elif test.testing:
      self.homeDir = os.getcwd()
    else:
      self.homeDir = os.path.expanduser("~")
    self.endUser = EndUser(self)

  @property
  def config(self):
    """
    Get the user's :doc:`Config <config>` object.

    Note: the user's config will be loaded the first time this is called.
    """
    if self.__config == None:
      self.__config = config.Config(self)
    return self.__config

  @property
  def registry(self):
    """
    Get the user's subuser :doc:`Registry <registry>`.

    Note: the registry will be loaded the first time this is called.
    """
    if self.__registry == None:
      self.__registry = registry.Registry(self)
      self.__registry.ensureGitRepoInitialized()
    return self.__registry

  @registry.setter
  def registry(self, registry):
    self.__registry = registry

  def reloadRegistry(self):
    """
    Reload registry from disk.
    """
    self.__registry = None

  @property
  def installedImages(self):
    """
    Get the user's  :doc:`InstalledImages <installed-images>` list.

    Note: the installed images list will be loaded the first time this is called.
    """
    if self.__installedImages == None:
      self.__installedImages = installedImages.InstalledImages(self)
    return self.__installedImages

  @property
  def dockerDaemon(self):
    """
    Get the :doc:`DockerDaemon <docker>` object.  You will use this to communicate with the Docker daemon.
    """
    if self.__dockerDaemon == None:
      self.__dockerDaemon = dockerDaemon.DockerDaemon(self)
    return self.__dockerDaemon

  @property
  def operation(self):
    """
    Get the :doc:`Operation <operation>` object.  This object contains runtime data relating to the current "operation". This includes image building configuration data as well as UX options.
    """
    if self.__operation == None:
      self.__operation = Operation(self)
    return self.__operation

class LockedUser():
  def __init__(self,name=None,homeDir=None):
    self.lock = None
    self.__user = User(name=name,homeDir=homeDir,_locked=True)

  def __enter__(self):
    try:
      self.__user.endUser.makedirs(self.__user.config["lock-dir"])
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        raise
    try:
      self.lock = subuserlib.lock.getLock(self.__user.endUser.get_file(os.path.join(self.__user.config["lock-dir"],"registry.lock"),'w'),timeout=1)
      self.lock.__enter__()
    except IOError as e:
      if e.errno != errno.EINTR:
        raise e
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
    return self.__user

  def __exit__(self, type, value, traceback):
    self.lock.__exit__()
