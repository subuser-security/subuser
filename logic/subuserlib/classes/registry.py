#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Each user's settings are stored in a "registry". This is a git repository with a set of json files which store the state of the subuser installation.
"""

#external imports
import os
#internal imports
import subuserlib.classes.subusers, subuserlib.classes.userOwnedObject, subuserlib.git

class Registry(subuserlib.classes.userOwnedObject.UserOwnedObject):
  __subusers = None
  __repositories = None
  __changed = False
  __changeLog = ""

  def getSubusers(self):
    if not self.__subusers:
      self.__subusers = subuserlib.classes.subusers.Subusers(self.getUser())
    return self.__subusers

  def reloadSubusersFromDisk(self):
    """
    Discard all changes to the subusers list in memory and reload from disk.
    """
    self.__subusers = None

  def getRepositories(self):
    if not self.__repositories:
      self.__repositories =      subuserlib.classes.repositories.Repositories(self.getUser())
    return self.__repositories

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.ensureGitRepoInitialized()

  def ensureGitRepoInitialized(self):
    if not os.path.exists(self.getUser().getConfig().getRegistryPath()):
      os.makedirs(self.getUser().getConfig().getRegistryPath())
      subuserlib.git.runGit(["init"],cwd=self.getUser().getConfig().getRegistryPath())
      self.logChange("Initial commit.")
      self.commit()

  def log(self,message):
    """
    Add a log message to the registry's change log and print it to the screen, but do not mark the registry as changed.
    """
    self.__changeLog = self.__changeLog + message+"\n"
    print(message)

  def logChange(self,message):
    """
    Add a log message to the registry's change log, and mark the registry as changed.
    """
    self.log(message)
    self.__changed = True

  def logRenameCommit(self, message):
    """
    Add a new message to the top of the log.
    """
    self.__changeLog = message + "\n" + self.__changeLog

  def commit(self):
    """ git commit the changes to the registry files, installed-miages.json and subusers.json. """
    if self.__changed:
      self.getRepositories().save()
      self.getSubusers().save()
      subuserlib.git.runGit(["add","subusers.json","repository-states.json"],cwd=self.getUser().getConfig().getRegistryPath())
      if os.path.exists(os.path.join(self.getUser().getConfig().getRegistryPath(),"repositories.json")):
        subuserlib.git.runGit(["add","repositories.json"],cwd=self.getUser().getConfig().getRegistryPath())
      subuserlib.git.runGit(["commit","-m",self.__changeLog],cwd=self.getUser().getConfig().getRegistryPath())
      self.__changed = False
      self.__changeLog = ""

