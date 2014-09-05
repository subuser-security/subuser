#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess,os,shutil
#internal imports
import subuserlib.git,subuserlib.classes.userOwnedObject,subuserlib.classes.imageSource,subuserlib.subprocessExtras

class Repository(dict,subuserlib.classes.userOwnedObject.UserOwnedObject):
  __name = None
  __gitOriginURI = None

  def __init__(self,user,name,gitOriginURI,gitCommitHash):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__name = name
    self.__gitOriginURI = gitOriginURI
    self.checkoutGitCommit(gitCommitHash)
    self.loadProgamSources()

  def getName(self):
    return self.__name

  def getGitOriginURI(self):
    return self.__gitOriginURI

  def getRepoPath(self):
    """ Get the path of the repo's sources on disk. """
    return os.path.join(self.getUser().getConfig().getRepositoriesDir(),str(self.getName()))

  def removeGitRepo(self):
    """
     Remove the downloaded git repo associated with this repository from disk.
    """
    shutil.rmtree(self.getRepoPath())

  def updateSources(self):
    """ Pull(or clone) the repo's ImageSources from git origin. """
    if not os.path.exists(self.getRepoPath()):
      subuserlib.git.runGit(["clone",self.getGitOriginURI(),self.getRepoPath()])
    else:
      subuserlib.git.runGit(["checkout","master"],cwd=self.getRepoPath())
      subuserlib.git.runGit(["pull"],cwd=self.getRepoPath())

  def loadProgamSources(self):
    """
    Load ProgamSources from disk into memory.
    """
    imageNames = filter(lambda f: os.path.isdir(os.path.join(self.getRepoPath(),f)) and not f == ".git",os.listdir(self.getRepoPath()))
    for imageName in imageNames:
      self[imageName] = (subuserlib.classes.imageSource.ImageSource(self.getUser(),self,imageName))

  def checkoutGitCommit(self,gitCommitHash):
    """
    Checkout a given git commit.
    """
    if not os.path.exists(self.getRepoPath()):
      self.updateSources()
    subuserlib.git.runGit(["checkout",gitCommitHash],cwd=self.getRepoPath())

  def getGitCommitHash(self):
    return subuserlib.git.runGitCollectOutput(["show-ref","-s","HEAD"],cwd=self.getRepoPath()).split("\n")[0]
