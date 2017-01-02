# -*- coding: utf-8 -*-

"""
A repository is a collection of ``ImageSource`` s which are published in a git repo.
"""

#external imports
import os
import shutil
import json
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.imageSource import ImageSource
from subuserlib.classes.describable import Describable
from subuserlib.classes.gitRepository import GitRepository
from subuserlib.classes.fileStructure import BasicFileStructure
import subuserlib.version

class Repository(dict,UserOwnedObject,Describable):
  def __init__(self,user,name,gitOriginURI=None,gitCommitHash=None,temporary=False,sourceDir=None):
    """
    Repositories can either be managed by git, or simply be normal directories on the user's computer. If ``sourceDir`` is not set to None, then ``gitOriginURI`` is ignored and the repository is assumed to be a simple directory.
    """
    self.__name = name
    self.__gitOriginURI = gitOriginURI
    self.__lastGitCommitHash = gitCommitHash
    self.__temporary = temporary
    self.__sourceDir = sourceDir
    self.__fileStructure = None
    UserOwnedObject.__init__(self,user)
    self.__gitRepository = GitRepository(user,self.getRepoPath())
    if not self.isPresent():
      self.updateSources(initialUpdate=True)
    self.__repoConfig = self.loadRepoConfig()
    if self.isPresent():
      self.loadImageSources()

  def getName(self):
    return self.__name

  def getURI(self):
    if self.isLocal():
      return self.getSourceDir()
    else:
      return self.getGitOriginURI()

  def getSourceDir(self):
    return self.__sourceDir

  def getGitOriginURI(self):
    return self.__gitOriginURI

  def getGitRepository(self):
    return self.__gitRepository

  def getFileStructure(self):
    if self.__fileStructure is None:
      if self.isLocal():
        self.__fileStructure = BasicFileStructure(self.getSourceDir())
      else:
        if self.getGitCommitHash() is None:
          self.updateGitCommitHash()
        self.__fileStructure = self.getGitRepository().getFileStructureAtCommit(self.getGitCommitHash())
    return self.__fileStructure

  def getDisplayName(self):
    """
    How should we refer to this repository when communicating with the user?
    """
    if self.isTemporary():
      if self.isLocal():
        return self.getSourceDir()
      else:
        return self.getGitOriginURI()
    else:
      return self.getName()

  def describe(self):
    print("Repository: "+self.getDisplayName())
    print("------------")
    if self.isLocal():
      print("Is a local(non-git) repository.")
      if not self.isTemporary():
        print("Located at: " + self.getRepoPath())
    if self.isTemporary():
      print("Is a temporary repository.")
    else:
      if not self.isLocal():
        print("Cloned from: "+self.getGitOriginURI())
        print("Currently at commit: "+self.getGitCommitHash())

  def getSortedList(self):
    """
    Return a list of image sources sorted by name.
    """
    return list(sorted(self.values(),key=lambda imageSource:imageSource.getName()))

  def getRepoPath(self):
    """ Get the path of the repo's sources on disk. """
    if self.isLocal():
      return self.getSourceDir()
    else:
      return os.path.join(self.getUser().getConfig()["repositories-dir"],self.getName())

  def loadRepoConfig(self):
    """
    Either returns the config as a dictionary or None if no configuration exists or can be parsed.
    """
    def verifyPaths(dictionary,paths):
      """
      Looks through a dictionary at all entries that can be considered to be paths, and ensures that they do not contain any relative upwards references.
      Throws a ValueError if they do.
      """
      for path in paths:
        if path in dictionary and path.startswith("../") or "/../" in path:
          raise ValueError("Paths in .subuser.json may not be relative to a higher directory.")
    if self.getFileStructure().exists("./.subuser.json"):
      configFileContents = self.getFileStructure().read("./.subuser.json")
    else:
      return None
    repoConfig = json.loads(configFileContents)
    # Validate untrusted input
    verifyPaths(repoConfig,["image-sources-dir"])
    if "explicit-image-sources" in repoConfig:
      for explicitImageSource in repoConfig["explicit-image-sources"]:
        verifyPaths(explicitImageSource,["image-file","permissions-file","build-context"])
    return repoConfig

  def getRepoConfig(self):
    return self.__repoConfig

  def getImageSourcesDir(self):
    """
    Get the path of the repo's subuser root on disk on the host.
    """
    return os.path.join(self.getRepoPath(),self.getRelativeImageSourcesDir())

  def getRelativeImageSourcesDir(self):
    """
    Get the path of the repo's subuser root on disk on the host.
    """
    repoConfig = self.getRepoConfig()
    if repoConfig and "image-sources-dir" in repoConfig:
      return repoConfig["image-sources-dir"]
    else:
      return "./"

  def isTemporary(self):
    return self.__temporary

  def isInUse(self):
    """
    Are there any installed images or subusers from this repository?
    """
    for _,installedImage in self.getUser().getInstalledImages().items():
      if self.getName() == installedImage.getSourceRepoId():
          return True
      for _,subuser in self.getUser().getRegistry().getSubusers().items():
        try:
          if self.getName() == subuser.getImageSource().getRepository().getName():
            return True
        except subuserlib.classes.subuser.NoImageSourceException:
          pass
    return False

  def isLocal(self):
    if self.__sourceDir:
      return True
    return False

  def removeGitRepo(self):
    """
    Remove the downloaded git repo associated with this repository from disk.
    """
    if not self.isLocal():
      shutil.rmtree(self.getRepoPath())

  def isPresent(self):
    """
    Returns True if the repository's files are present on the system. (Cloned or local)
    """
    return os.path.exists(self.getRepoPath())

  def updateSources(self,initialUpdate=False):
    """
    Pull(or clone) the repo's ImageSources from git origin.
    """
    if self.isLocal():
      return
    if not self.isPresent():
      new = True
      self.getUser().getRegistry().log("Cloning repository "+self.getName()+" from "+self.getGitOriginURI())
      if self.getGitRepository().clone(self.getGitOriginURI()) != 0:
        self.getUser().getRegistry().log("Clone failed.")
        return
    else:
      new = False
    try:
      self.getGitRepository().run(["fetch","--all"])
    except Exception: # For some reason, git outputs normal messages to stderr.
      pass
    if self.updateGitCommitHash():
      if not new:
        self.getUser().getRegistry().logChange("Updated repository "+self.getDisplayName())
      if not initialUpdate:
        self.loadImageSources()

  def serializeToDict(self):
    """
    Return a dictionary which describes the image sources available in this repository.
    """
    imageSourcesDict = {}
    for name,imageSource in self.items():
      imageSourcesDict[name] = {}
    return imageSourcesDict

  def loadImageSources(self):
    """
    Load ImageSources from disk into memory.
    """
    imageNames = self.getFileStructure().lsFolders(self.getRelativeImageSourcesDir())
    imageNames = [os.path.basename(path) for path in imageNames]
    for imageName in imageNames:
      imageSource = ImageSource(self.getUser(),self,imageName)
      if self.getFileStructure().exists(imageSource.getRelativePermissionsFilePath()):
        self[imageName] = imageSource
    if self.getRepoConfig() is not None and "explicit-image-sources" in self.getRepoConfig():
      for imageName,config in self.getRepoConfig()["explicit-image-sources"].items():
        assert config is not None
        self[imageName] = ImageSource(self.getUser(),self,imageName,explicitConfig = config)

  def updateGitCommitHash(self):
    """
    Update the internally stored git commit hash to the current git HEAD of the repository.
    Returns True if the repository has been updated.
    Otherwise false.
    """
    if self.isLocal():
      return True
    # Default
    newCommitHash = self.getGitRepository().getHashOfRef("refs/remotes/origin/master")
    # First we check for version constraints on the repository.
    if self.getGitRepository().getFileStructureAtCommit("master").exists("./.subuser.json"):
      configFileContents = self.getGitRepository().getFileStructureAtCommit("master").read("./.subuser.json")
      configAtMaster = json.loads(configFileContents)
      if "subuser-version-constraints" in configAtMaster:
        versionConstraints = configAtMaster["subuser-version-constraints"]
        subuserVersion = subuserlib.version.getSubuserVersion(self.getUser())
        for constraint in versionConstraints:
          if not len(constraint) == 3:
            raise SyntaxError("Error in .subuser.json file. Invalid subuser-version-constraints."+ str(versionConstraints))
          op,version,commit = constraint
          from operator import lt,le,eq,ge,gt
          operators = {"<":lt,"<=":le,"==":eq,">=":ge,">":gt}
          try:
            matched = operators[op](subuserVersion,version)
          except KeyError:
            raise SyntaxError("Error in .subuser.json file. Invalid subuser-version-constraints.  \""+op+"\" is not a valid operator.\n\n"+ str(versionConstraints))
          if matched:
            try:
              newCommitHash = self.getGitRepository().getHashOfRef("refs/remotes/origin/"+commit)
            except OSError as e:
              if len(commit) == 40:
                newCommitHash = commit
              else:
                raise e
            break
        else:
          raise SyntaxError("Error reading .subuser.json file, no version constraints matched the current subuser version ("+subuserVersion+").\n\n"+str(versionConstraints))
    updated = not (newCommitHash == self.__lastGitCommitHash)
    self.__lastGitCommitHash = newCommitHash
    self.__fileStructure = None
    return updated

  def getGitCommitHash(self):
    return self.__lastGitCommitHash
