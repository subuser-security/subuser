#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
#import ...
#internal imports
import subuserlib.classes.subusers, subuserlib.classes.userOwnedObject, subuserlib.git

class Registry(subuserlib.classes.userOwnedObject.UserOwnedObject):
  __subusers = None
  __repositories = None
  __changed = False

  def getSubusers(self):
    if not self.__subusers:
      self.__subusers = subuserlib.classes.subusers.Subusers(self.getUser())
    return self.__subusers

  def getRepositories(self):
    if not self.__repositories:
      self.__repositories =      subuserlib.classes.repositories.Repositories(self.getUser())
    return self.__repositories

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)

  def log(self,message):
    """
    Add a log message to the registry's change log and print it to the screen, but do not mark the registry as changed.
    """
    self.__changeLog.append(message+"\n")
    print(message)

  def logChange(self,message):
    """
    Add a log message to the registry's change log, and mark the registry as changed.
    """
    self.log(message)
    self.__changed = True

  def commit(self):
    """ git commit the changes to the registry files, installed-miages.json and subusers.json. """
    if self.__changed:
      subuserlib.git(["add","subusers.json","installed-programs.json"],cwd=self.getUser().config.getRegistryPath())
      subuserlib.git(["commit","-m",self.__changeLog],cwd=self.getUser().config.getRegistryPath())
      self.__changed = False
      self.__changeLog = ""

