#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Each user's settings are stored in a "registry". This is a git repository with a set of json files which store the state of the subuser installation.
"""

#external imports
import os
import errno
import sys
from contextlib import contextmanager
import json
#internal imports
from subuserlib.classes import repositories
from subuserlib.classes import subusers
from subuserlib.classes import userOwnedObject
from subuserlib.classes.gitRepository import GitRepository
import subuserlib.lock

class Registry(userOwnedObject.UserOwnedObject):
  def __init__(self,user,gitReadHash="master"):
    self.__subusers = None
    self.__changeLog = u""
    self.__changed = False
    self.__logOutputVerbosity = 2
    self.__repositories = None
    self.__gitRepository = None
    self.__gitReadHash = gitReadHash
    userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__gitRepository = GitRepository(self.getUser().getConfig()["registry-dir"])
    self._ensureGitRepoInitialized()

  def getGitRepository(self):
    return self.__gitRepository

  def getGitReadHash(self):
    return self.__gitReadHash

  def getSubusers(self):
    if not self.__subusers:
      self.__subusers = subusers.Subusers(self.getUser())
    return self.__subusers

  def reloadSubusersFromDisk(self):
    """
    Discard all changes to the subusers list in memory and reload from disk.
    """
    self.__subusers = None

  def getRepositories(self):
    if not self.__repositories:
      self.__repositories = repositories.Repositories(self.getUser())
    return self.__repositories

  def _ensureGitRepoInitialized(self):
    if not os.path.exists(self.getUser().getConfig()["registry-dir"]):
      os.makedirs(self.getUser().getConfig()["registry-dir"])
      self.getGitRepository().run(["init"])

  def setLogOutputVerbosity(self,level):
    self.__logOutputVerbosity = level

  def getLogOutputVerbosity(self):
    return self.__logOutputVerbosity

  def log(self,message):
    """
    Add a log message to the registry's change log and print it to the screen, but do not mark the registry as changed.
    """
    message = message.rstrip()
    self.__changeLog = self.__changeLog + message+u"\n"
    if self.getLogOutputVerbosity() > 0:
      print(message)

  def logChange(self,message):
    """
    Add a log message to the registry's change log, and mark the registry as changed.
    """
    self.log(message)
    self.__changed = True

  def setChanged(self,changed=True):
    self.__changed = changed

  def logRenameCommit(self, message):
    """
    Add a new message to the top of the log.
    """
    self.__changeLog = message + u"\n" + self.__changeLog

  def commit(self):
    """
    Git commit the changes to the registry files, installed-miages.json and subusers.json.
    """
    if self.__changed:
      self.getRepositories().save()
      self.getSubusers().save()
      self.getGitRepository().run(["add","."])
      self.getGitRepository().commit(self.__changeLog)
      # Log to live log
      announcement = {}
      announcement["commit"] = self.getGitRepository().getHashOfRef("master")
      self.logToLiveLog(announcement)
      self.__changed = False
      self.__changeLog = u""

  def logToLiveLog(self,announcement):
    announcementJson = json.dumps(announcement)
    liveLogDir=os.path.join(self.getUser().homeDir,".subuser/registry-live-log")
    if os.path.isdir(liveLogDir):
      for liveLogPid in os.listdir(liveLogDir):
        liveLogPath = os.path.join(liveLogDir,liveLogPid)
        try:
          liveLog = os.open(liveLogPath,os.O_WRONLY|os.O_NONBLOCK)
          os.write(liveLog,announcementJson)
        except OSError:
          pass
        # TODO Note: We don't close the file descriptors, because doing so makes the pipe close on the other end too. This would be a file descriptor leak if this method was used in any long running process(which it is not).

  @contextmanager
  def getLock(self):
    """
    To be used with with.
    """
    try:
      os.makedirs(self.getUser().getConfig()["lock-dir"])
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        raise
    try:
      lock = subuserlib.lock.getLock(os.path.join(self.getUser().getConfig()["lock-dir"],"registry.lock"),timeout=1)
      with lock:
        yield
    except IOError as e:
      if e.errno != errno.EINTR:
        raise e
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
