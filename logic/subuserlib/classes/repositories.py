# -*- coding: utf-8 -*-

"""
This is the list of repositories from which subuser images may be installed or updated.
"""

#external imports
import os
import collections
import json
import sys
#internal imports
import subuserlib.paths
from subuserlib.classes.fileBackedObject import FileBackedObject
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.repository import Repository
import subuserlib.loadMultiFallbackJsonConfigFile

class Repositories(collections.Mapping,UserOwnedObject,FileBackedObject):
  def __init__(self,user):
    self.systemRepositories = {} # TODO rename and document these variables
    self.userRepositories = {}
    UserOwnedObject.__init__(self,user)
    self.systemRepositoryListPaths = ["/etc/subuser/repositories.json"
       ,os.path.join(user.homeDir,".subuser","repositories.json")
       ,subuserlib.paths.getSubuserDataFile("repositories.json")] # TODO how does this work on windows?
    self.userRepositoryListPath = os.path.join(self.user.getConfig()["registry-dir"],"repositories.json")
    self.reloadRepositoryLists()

  def _getAllRepositories(self):
    allRepos = {}
    allRepos.update(self.systemRepositories)
    allRepos.update(self.userRepositories)
    return allRepos

  # Frozen dict attributes
  def __iter__(self):
    return iter(self._getAllRepositories())

  def __len__(self):
    return len(self._getAllRepositories())

  def __getitem__(self, key):
    return self._getAllRepositories()[key]

  def reloadRepositoryLists(self):
    """
    Load the repository list from disk, discarding the current in-memory version.
    """
    repositoryStates = self._loadRepositoryStates()
    def loadRepositoryDict(repositoryDict):
      """
      From a list of paths to repository lists load a single unified repository dict.
      """
      repositories = {}
      for repoName,repoAttributes in repositoryDict.items():
        subuserlib.loadMultiFallbackJsonConfigFile.expandPathsInDict(self.user.homeDir,["git-origin","source-dir"],repoAttributes)
        if repoName in repositoryStates:
          gitCommitHash = repositoryStates[repoName]["git-commit-hash"]
        else:
          gitCommitHash = "master"
        if "temporary" in repoAttributes:
          temporary = repoAttributes["temporary"]
        else:
          temporary=False
        if "git-origin" in repoAttributes:
          gitOriginURI = repoAttributes["git-origin"]
        else:
          gitOriginURI = None
        if "source-dir" in repoAttributes:
          sourceDir = repoAttributes["source-dir"]
        else:
          sourceDir = None
        repositories[repoName] = Repository(self.user,name=repoName,gitOriginURI=gitOriginURI,gitCommitHash=gitCommitHash,temporary=temporary,sourceDir=sourceDir)
      return repositories
    self.systemRepositories = loadRepositoryDict(subuserlib.loadMultiFallbackJsonConfigFile.getConfig(self.systemRepositoryListPaths))
    registryFileStructure = self.user.getRegistry().gitRepository.getFileStructureAtCommit(self.user.getRegistry().gitReadHash)
    if self.user.getRegistry().initialized and "repositories.json" in registryFileStructure.lsFiles("./"):
      self.userRepositories = loadRepositoryDict(json.loads(registryFileStructure.read("repositories.json")))
    else:
      self.userRepositories = {}

  def _loadRepositoryStates(self):
    """
    Load the repository states from disk.
    Return them as a dictionary object.
    """
    if not self.user.getRegistry().initialized:
      return {}
    gitFileStructure = self.user.getRegistry().gitRepository.getFileStructureAtCommit(self.user.getRegistry().gitReadHash)
    if "repository-states.json" in gitFileStructure.lsFiles("./"):
      return json.loads(gitFileStructure.read("repository-states.json"))
    else:
      return {}

  def addRepository(self,repository):
    if not repository.temporary:
      self.user.getRegistry().logChange("Adding new repository "+repository.displayName)
    else:
      self.user.getRegistry().logChange("Adding new temporary repository "+repository.displayName)
    self.userRepositories[repository.name] = repository

  def removeRepository(self,name):
    try:
      repository = self.userRepositories[name]
    except KeyError:
      sys.exit("Cannot remove repository "+name+". Repository does not exist.")
    if repository.isInUse():
      sys.exit("Cannot remove repository "+name+". Repository is in use. Subusers or installed images exist which rely on this repository.")
    if not repository.temporary:
      self.user.getRegistry().logChange("Removing repository "+name)
    else:
      self.user.getRegistry().logChange("Removing temporary repository "+self[name].displayName)
    repository.removeGitRepo()
    del self.userRepositories[name]

  def serializeToDict(self):
    """
    Note: The save method serializes only that which needs to be saved. Not the entire repositories list. This returns a complete dictionary including system repositories and their states.
    """
    repositories = {}
    repositories.update(self.serializeRepositoriesToDict(self.userRepositories))
    repositories.update(self.serializeRepositoriesToDict(self.systemRepositories))
    for repoName,repositoryState in self.serializeRepositoryStatesToDict().items():
      repositories[repoName].update(repositoryState)
    return repositories

  def serializeRepositoriesToDict(self,repositories):
    repositoryListDict = collections.OrderedDict()
    for name,repository in sorted(repositories.items(),key=lambda t:t[0]):
      repositoryListDict[name] = collections.OrderedDict()
      if repository.gitOriginURI:
        repositoryListDict[name]["git-origin"] = repository.gitOriginURI
      else:
        repositoryListDict[name]["source-dir"] = repository.repoPath
      repositoryListDict[name]["temporary"] = repository.temporary
    return repositoryListDict

  def serializeRepositoryStatesToDict(self):
    repositoryStates = collections.OrderedDict()
    for repoName,repository in sorted(self.items(),key=lambda t:t[0]):
      repositoryStates[repoName] = collections.OrderedDict()
      repositoryStates[repoName]["git-commit-hash"] = repository.gitCommitHash
    return repositoryStates

  def save(self):
    """
    Save attributes of the repositories to disk.

    Note: This is done automatically for you when you ``commit()`` the registry.
    """
    with self.user.getEndUser().get_file(self.userRepositoryListPath, 'w') as file_f:
      json.dump(self.serializeRepositoriesToDict(self.userRepositories), file_f, indent=1, separators=(',', ': '))
    repositoryStatesDotJsonPath = os.path.join(self.user.getConfig()["registry-dir"],"repository-states.json")
    with self.user.getEndUser().get_file(repositoryStatesDotJsonPath,mode="w") as repositoryStatesDotJsonFile:
      json.dump(self.serializeRepositoryStatesToDict(),repositoryStatesDotJsonFile, indent=1, separators=(',', ': '))

  def getNewUniqueTempRepoId(self):
    """
    Return a new, unique, identifier for a temporary repository.  This function is useful when creating new temporary repositories.
    """
    idAsInt=0
    while str(idAsInt) in self or os.path.exists(os.path.join(self.user.getConfig()["repositories-dir"],str(idAsInt))):
      idAsInt = idAsInt + 1
    return str(idAsInt)
