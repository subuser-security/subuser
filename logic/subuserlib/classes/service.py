# -*- coding: utf-8 -*-

"""
This is an abstract class providing common methods shared by all service types.

The semantics of the lock file mechanism may be found `here <https://github.com/subuser-security/subuser/issues/31>`_ .
"""

#external imports
import abc
import json
import os
import errno
import fcntl
import shutil
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject

class Service(UserOwnedObject):
  __metaclass__ = abc.ABCMeta

  def __init__(self,user,subuser):
    self.__subuser = subuser
    UserOwnedObject.__init__(self,user)

  @abc.abstractmethod
  def start(self,serviceStatus):
    """
    Start the service. Block untill the service has started. Returns a modified service status dictionary with any service specific properties set.
    """
    pass

  @abc.abstractmethod
  def stop(self,serviceStatus):
    """
    Stop the service. Block untill the service has stopped.
    """
    pass

  @abc.abstractmethod
  def cleanUp(self):
    pass

  @abc.abstractmethod
  def isRunning(self,serviceStatus):
    """
    Returns True if the services is running.
    """
    pass

  @abc.abstractmethod
  def getName(self):
    pass

  def getLockfileDir(self):
    return os.path.join(self.getUser().getConfig()["lock-dir"],"services",self.__subuser.getName())

  def getLockfilePath(self):
    return os.path.join(self.getLockfileDir(),self.getName()+".json")

  def removeLockFile(self):
    os.remove(self.getLockfilePath())
    try:
      os.rmdir(self.getLockfileDir())
    except OSError:
      pass

  def getLock(self):
    try:
      self.getUser().getEndUser().makedirs(self.getLockfileDir())
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        raise
    while True:
      try:
        lockFd = open(self.getLockfilePath(),mode="r+")
        break
      except IOError:
        self.getUser().getEndUser().create_file(self.getLockfilePath())
    fcntl.flock(lockFd,fcntl.LOCK_EX)
    return lockFd

  def addClient(self):
    """
    Increase the services client counter, starting the service if necessary. Blocks untill the service is ready to accept the new client.
    """
    with self.getLock() as lockFile:
      try:
        serviceStatus = json.load(lockFile)
      except ValueError:
        serviceStatus = {}
        serviceStatus["client-counter"] = 0
      if serviceStatus["client-counter"] == 0 or not self.isRunning(serviceStatus):
        serviceStatus["client-counter"] = 0
        serviceStatus = self.start(serviceStatus)
      serviceStatus["client-counter"] = serviceStatus["client-counter"] + 1
      lockFile.seek(0)
      lockFile.truncate()
      json.dump(serviceStatus,lockFile)
      fcntl.flock(lockFile,fcntl.LOCK_UN)

  def removeClient(self):
    """
    Decrease the services client counter, stopping the service if no longer necessary.
    """
    noMoreClients = False
    with self.getLock() as lockFile:
      serviceStatus = json.load(lockFile)
      serviceStatus["client-counter"] = serviceStatus["client-counter"] - 1
      if serviceStatus["client-counter"] < 0:
        raise RemoveClientException("The client-counter is already zero. Client cannot be removed!")
      if serviceStatus["client-counter"] == 0:
        self.stop(serviceStatus)
        noMoreClients = True
      lockFile.seek(0)
      lockFile.truncate()
      json.dump(serviceStatus,lockFile)
      if noMoreClients:
        self.removeLockFile()
      fcntl.flock(lockFile,fcntl.LOCK_UN)

  def cleanUpIfNotRunning(self):
    """
    Check if running.
    If not running, run cleanUp method.
    """
    with self.getLock() as lockFile:
      try:
        serviceStatus = json.load(lockFile)
      except ValueError:
        serviceStatus = {}
        serviceStatus["client-counter"] = 0
      if serviceStatus["client-counter"] == 0 or not self.isRunning(serviceStatus):
        self.cleanUp()
        self.removeLockFile()
      fcntl.flock(lockFile,fcntl.LOCK_UN)


class RemoveClientException(Exception):
  pass
