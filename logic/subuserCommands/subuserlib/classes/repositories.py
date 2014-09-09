#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os,collections,json
#internal imports
import subuserlib.paths, subuserlib.classes.fileBackedObject, subuserlib.classes.userOwnedObject, subuserlib.classes.repository,subuserlib.loadMultiFallbackJsonConfigFile

class Repositories(collections.Mapping,subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.fileBackedObject.FileBackedObject):
  systemRepositories = {}
  userRepositories = {}

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
    """ Load the repository list from disk, discarding the current in-memory version. """
    repositoryStates = self._loadRepositoryStates()
    def loadRepositoryDict(paths):
      """
       From a list of paths to repository lists load a single unified repository dict.
      """
      repositoryDict = subuserlib.loadMultiFallbackJsonConfigFile.getConfig(paths)
      repositories = {}
      for repoName,repoAttributes in repositoryDict.iteritems():
        if repoName in repositoryStates:
          gitCommitHash = repositoryStates[repoName]["git-commit-hash"]
        else:
          gitCommitHash = "master"
        repositories[repoName] = subuserlib.classes.repository.Repository(self.getUser(),name=repoName,gitOriginURI=repoAttributes["git-origin"],gitCommitHash=gitCommitHash)
      return repositories

    self.systemRepositories = loadRepositoryDict(self.systemRepositoryListPaths)
    self.userRepositories = loadRepositoryDict([self.userRepositoryListPath])

  def _loadRepositoryStates(self):
    """
    Load the repository states from disk.
    Return them as a dictionary object.
    """
    repositoryStatesDotJsonPath = os.path.join(self.getUser().getConfig().getRegistryPath(),"repository-states.json")
    if os.path.exists(repositoryStatesDotJsonPath):
      with open(repositoryStatesDotJsonPath,mode="r") as repositoryStatesDotJsonFile:
        return json.load(repositoryStatesDotJsonFile)
    else:
      return {}

  def addRepository(self,repository):
    if not type(repository.getName()) is int:
      self.getUser().getRegistry().logChange("Adding new repository "+repository.getName())
    else:
      self.getUser().getRegistry().logChange("Adding new temporary repository "+repository.getGitOriginURI())
    self.userRepositories[repository.getName()] = repository

  def removeRepository(self,name):
    if not type(name) is int:
      self.getUser().getRegistry().logChange("Removing repository "+name)
    else:
      self.getUser().getRegistry().logChange("Removing temporary repository "+self[name].getGitOriginURI())
    del self.userRepositories[name]

  def save(self):
    """ Save attributes of the repositories to disk. """
    userRepositoryListDict = {}
    for name,repository in self.userRepositories.iteritems():
      userRepositoryListDict[name] = {}
      userRepositoryListDict[name]["git-origin"] = repository.getGitOriginURI()
    with open(self.userRepositoryListPath, 'w') as file_f:
      json.dump(userRepositoryListDict, file_f, indent=1, separators=(',', ': '))
    repositoryStatesDotJsonPath = os.path.join(self.getUser().getConfig().getRegistryPath(),"repository-states.json")
    repositoryStates = {}
    for repoName,repository in self.iteritems():
      repositoryStates[repoName] = {}
      repositoryStates[repoName]["git-commit-hash"] = repository.getGitCommitHash()
    with open(repositoryStatesDotJsonPath,mode="w") as repositoryStatesDotJsonFile:
      json.dump(repositoryStates,repositoryStatesDotJsonFile, indent=1, separators=(',', ': '))

  def getNewUniqueTempRepoId(self):
    """
    Return a new, unique, identifier for a temporary repository.  This function is useful when creating new temporary repositories.
    """
    id=0
    for _,repo in self.iteritems():
      if repo.getName() == id:
        id = id + 1
    return id

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.systemRepositoryListPaths = ["/etc/subuser/repositories.json"
       ,os.path.join(user.homeDir,".subuser","repositories.json")
       ,os.path.join(subuserlib.paths.getSubuserDir(),"repositories.json")] # TODO how does this work on windows?
    self.userRepositoryListPath = os.path.join(self.getUser().getConfig().getRegistryPath(),"repositories.json")
    self.reloadRepositoryLists()

