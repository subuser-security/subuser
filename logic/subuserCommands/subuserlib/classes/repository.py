#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess,os
#internal imports
import subuserlib.git,subuserlib.classes.userOwnedObject,subuserlib.classes.programSource,subuserlib.subprocessExtras

class Repository(dict,subuserlib.classes.userOwnedObject.UserOwnedObject):
  __name = None
  __gitOriginURI = None

  def __init__(self,user,name,gitOriginURI):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__name = name
    self.__gitOriginURI = gitOriginURI
    self.loadProgamSources()

  def getName(self):
    return self.__name

  def getGitOriginURI(self):
    return self.__gitOriginURI

  def getRepoPath(self):
    """ Get the path of the repo's sources on disk. """
    return os.path.join(self.getUser().homeDir,".subuser","repositories",self.getName())

  def updateSources(self):
    """ Pull(or clone) the repo's ProgramSources from git origin. """
    if not os.path.exists(self.getRepoPath()):
      subuserlib.git.runGit(["clone",self.getGitOriginURI(),self.getRepoPath()])
    else:
      subuserlib.git.runGit(["pull"],cwd=self.getRepoPath())

  def loadProgamSources(self):
    """
     Load progam sources from disk into memory.
    """
    programNames = filter(lambda f: os.path.isdir(os.path.join(self.getRepoPath(),f)) and not f == ".git",os.listdir(self.getRepoPath()))
    for programName in programNames:
      self[programName] = (subuserlib.classes.programSource.ProgramSource(self.getUser(),self,programName))
