#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
A repository is a collection of ``ImageSource`` s which are published in a git repo.
"""

#external imports
import os,shutil,io,json
#internal imports
import subuserlib.git,subuserlib.classes.userOwnedObject,subuserlib.classes.imageSource,subuserlib.subprocessExtras

class Repository(dict,subuserlib.classes.userOwnedObject.UserOwnedObject):
  __name = None
  __gitOriginURI = None
  __lastGitCommitHash = None
  __temporary = False
  __sourceDir = None

  def __init__(self,user,name,gitOriginURI=None,gitCommitHash=None,temporary=False,sourceDir=None):
    """
    Repositories can either be managed by git, or simply be normal directories on the user's computer. If ``sourceDir`` is not set to None, then ``gitOriginURI`` is ignored and the repository is assumed to be a simple directory.
    """
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__name = name
    self.__gitOriginURI = gitOriginURI
    self.__lastGitCommitHash = gitCommitHash
    self.__temporary=temporary
    self.__sourceDir=sourceDir
    self.checkoutGitCommit(gitCommitHash)
    self.loadProgamSources()

  def getName(self):
    return self.__name

  def getGitOriginURI(self):
    return self.__gitOriginURI

  def getDisplayName(self):
    """
    How should we refer to this repository when communicating with the user?
    """
    if self.isTemporary():
      if self.__sourceDir:
        return self.__sourceDir
      else:
        return self.getGitOriginURI()
    else:
      return self.getName()

  def getRepoPath(self):
    """ Get the path of the repo's sources on disk. """
    if self.__sourceDir:
      return self.__sourceDir
    else:
      return os.path.join(self.getUser().getConfig().getRepositoriesDir(),str(self.getName()))

  def getRepoConfigPath(self):
    return os.path.join(self.getRepoPath(),".subuser.json")

  def getRepoConfig(self):
    """
    Either returns the config as a dictionary or None.
    """
    if os.path.exists(self.getRepoConfigPath()):
      with io.open(self.getRepoConfigPath(),"r",encoding="utf-8") as configFile:
        try:
          return json.load(configFile)
        except ValueError as ve:
          self.getRegistry().log("Error parsing .subuser.json file for repository "+self.getName()+":\n"+str(ve))
          return None
    else:
      return None

  def getSubuserRepositoryRoot(self):
    """ Get the path of the repo's subuser root on disk on the host. """
    repoConfig = self.getRepoConfig()
    if repoConfig:
      if "subuser-repository-root" in repoConfig:
        if repoConfig["subuser-repository-root"].startswith("../"):
          raise ValueError("Paths in .subuser.json may not be relative to a higher directory.")
        return os.path.join(self.getRepoPath(),repoConfig["subuser-repository-root"])
    return self.getRepoPath()

  def isTemporary(self):
    return self.__temporary

  def removeGitRepo(self):
    """
     Remove the downloaded git repo associated with this repository from disk.
    """
    if not self.__sourceDir:
      shutil.rmtree(self.getRepoPath())

  def updateSources(self):
    """ Pull(or clone) the repo's ImageSources from git origin. """
    if self.__sourceDir:
      return
    if not os.path.exists(self.getRepoPath()):
      subuserlib.git.runGit(["clone",self.getGitOriginURI(),self.getRepoPath()])
    else:
      subuserlib.git.runGit(["checkout","master"],cwd=self.getRepoPath())
      subuserlib.git.runGit(["pull"],cwd=self.getRepoPath())
      if not self.__lastGitCommitHash == self.getGitCommitHash():
        self.getUser().getRegistry().logChange("Updated repository "+self.getDisplayName())

  def loadProgamSources(self):
    """
    Load ProgamSources from disk into memory.
    """
    imageNames = filter(lambda f: os.path.isdir(os.path.join(self.getSubuserRepositoryRoot(),f)) and not f == ".git",os.listdir(self.getSubuserRepositoryRoot()))
    for imageName in imageNames:
      self[imageName] = (subuserlib.classes.imageSource.ImageSource(self.getUser(),self,imageName))

  def checkoutGitCommit(self,gitCommitHash):
    """
    Checkout a given git commit if it is not already checked out.
    """
    if self.__sourceDir:
      return
    if not os.path.exists(self.getRepoPath()):
      self.updateSources()
    if not gitCommitHash == self.getGitCommitHash():
      subuserlib.git.runGit(["checkout",gitCommitHash],cwd=self.getRepoPath())

  def getGitCommitHash(self):
    """
    Get the hash of the local repository's currently checked out git commit.
    """
    if self.__sourceDir:
      return None
    return subuserlib.git.runGitCollectOutput(["show-ref","-s","--head"],cwd=self.getRepoPath()).split("\n")[0]

