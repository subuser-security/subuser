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
    self.name = name
    self.gitOriginURI = gitOriginURI
    self.gitCommitHash = gitCommitHash
    self.temporary = temporary
    self.sourceDir = sourceDir
    self.__fileStructure = None
    UserOwnedObject.__init__(self,user)
    self.gitRepository = GitRepository(user,self.repoPath)
    if not self.isPresent():
      self.updateSources(initialUpdate=True)
    self.repoConfig = self.loadRepoConfig()
    if self.isPresent():
      self.loadImageSources()

  @property
  def uri(self):
    if self.isLocal:
      return self.sourceDir
    else:
      return self.gitOriginURI

  @property
  def fileStructure(self):
    if self.__fileStructure is None:
      if self.isLocal:
        self.__fileStructure = BasicFileStructure(self.sourceDir)
      else:
        if self.gitCommitHash is None:
          self.updateGitCommitHash()
        self.__fileStructure = self.gitRepository.getFileStructureAtCommit(self.gitCommitHash)
    return self.__fileStructure

  @property
  def displayName(self):
    """
    How should we refer to this repository when communicating with the user?
    """
    if self.temporary:
      if self.isLocal:
        return self.sourceDir
      else:
        return self.gitOriginURI
    else:
      return self.name

  def describe(self):
    print("Repository: "+self.displayName)
    print("------------")
    if self.isLocal:
      print("Is a local(non-git) repository.")
      if not self.temporary:
        print("Located at: " + self.repoPath)
    if self.temporary:
      print("Is a temporary repository.")
    else:
      if not self.isLocal:
        print("Cloned from: "+self.gitOriginURI)
        print("Currently at commit: "+self.gitCommitHash)

  def getSortedList(self):
    """
    Return a list of image sources sorted by name.
    """
    return list(sorted(self.values(),key=lambda imageSource:imageSource.name))

  @property
  def repoPath(self):
    """ Get the path of the repo's sources on disk. """
    if self.isLocal:
      return self.sourceDir
    else:
      return os.path.join(self.user.config["repositories-dir"],self.name)

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
    if self.fileStructure.exists("./.subuser.json"):
      configFileContents = self.fileStructure.read("./.subuser.json")
    else:
      return None
    repoConfig = json.loads(configFileContents)
    # Validate untrusted input
    verifyPaths(repoConfig,["image-sources-dir"])
    if "explicit-image-sources" in repoConfig:
      for explicitImageSource in repoConfig["explicit-image-sources"]:
        verifyPaths(explicitImageSource,["image-file","permissions-file","build-context"])
    return repoConfig

  @property
  def imageSourcesDir(self):
    """
    Get the path of the repo's subuser root on disk on the host.
    """
    return os.path.join(self.repoPath,self.relativeImageSourcesDir)

  @property
  def relativeImageSourcesDir(self):
    """
    Get the path of the repo's subuser root on disk on the host.
    """
    repoConfig = self.repoConfig
    if repoConfig and "image-sources-dir" in repoConfig:
      return repoConfig["image-sources-dir"]
    else:
      return "./"

  def isInUse(self):
    """
    Are there any installed images or subusers from this repository?
    """
    for _,installedImage in self.user.installedImages.items():
      if self.name == installedImage.sourceRepoId:
          return True
      for _,subuser in self.user.registry.subusers.items():
        try:
          if self.name == subuser.imageSource.repo.name:
            return True
        except subuserlib.classes.subuser.NoImageSourceException:
          pass
    return False

  @property
  def isLocal(self):
    if self.sourceDir:
      return True
    return False

  def removeGitRepo(self):
    """
    Remove the downloaded git repo associated with this repository from disk.
    """
    if not self.isLocal:
      shutil.rmtree(self.repoPath)

  def isPresent(self):
    """
    Returns True if the repository's files are present on the system. (Cloned or local)
    """
    return os.path.exists(self.repoPath)

  def updateSources(self,initialUpdate=False):
    """
    Pull(or clone) the repo's ImageSources from git origin.
    """
    if self.isLocal:
      return
    if not self.isPresent():
      new = True
      self.user.registry.log("Cloning repository "+self.name+" from "+self.gitOriginURI)
      if self.gitRepository.clone(self.gitOriginURI) != 0:
        self.user.registry.log("Clone failed.")
        return
    else:
      new = False
    try:
      self.gitRepository.run(["fetch","--all"])
    except Exception: # For some reason, git outputs normal messages to stderr.
      pass
    if self.updateGitCommitHash():
      if not new:
        self.user.registry.logChange("Updated repository "+self.displayName)
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
    imageNames = self.fileStructure.lsFolders(self.relativeImageSourcesDir)
    imageNames = [os.path.basename(path) for path in imageNames]
    for imageName in imageNames:
      imageSource = ImageSource(self.user,self,imageName)
      if self.fileStructure.exists(imageSource.getRelativePermissionsFilePath()):
        self[imageName] = imageSource
    if self.repoConfig is not None and "explicit-image-sources" in self.repoConfig:
      for imageName,config in self.repoConfig["explicit-image-sources"].items():
        assert config is not None
        self[imageName] = ImageSource(self.user,self,imageName,explicitConfig = config)

  def updateGitCommitHash(self):
    """
    Update the internally stored git commit hash to the current git HEAD of the repository.
    Returns True if the repository has been updated.
    Otherwise false.
    """
    if self.isLocal:
      return True
    # Default
    newCommitHash = self.gitRepository.getHashOfRef("refs/remotes/origin/master")
    # First we check for version constraints on the repository.
    if self.gitRepository.getFileStructureAtCommit("master").exists("./.subuser.json"):
      configFileContents = self.gitRepository.getFileStructureAtCommit("master").read("./.subuser.json")
      configAtMaster = json.loads(configFileContents)
      if "subuser-version-constraints" in configAtMaster:
        versionConstraints = configAtMaster["subuser-version-constraints"]
        subuserVersion = subuserlib.version.getSubuserVersion(self.user)
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
              newCommitHash = self.gitRepository.getHashOfRef("refs/remotes/origin/"+commit)
            except OSError as e:
              if len(commit) == 40:
                newCommitHash = commit
              else:
                raise e
            break
        else:
          raise SyntaxError("Error reading .subuser.json file, no version constraints matched the current subuser version ("+subuserVersion+").\n\n"+str(versionConstraints))
    updated = not (newCommitHash == self.gitCommitHash)
    self.gitCommitHash = newCommitHash
    self.__fileStructure = None
    return updated
