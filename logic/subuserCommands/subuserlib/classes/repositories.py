#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os,collections
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
    return len(self._getAllRepositories)

  def __getitem__(self, key):
    return self._getAllRepositories()[key]

  def reloadRepositoryLists(self):
    """ Load the repository list from disk, discarding the current in-memory version. """
    def loadRepositoryDict(paths):
      """
       From a list of paths to repository lists load a single unified repository dict.
      """
      repositoryDict = subuserlib.loadMultiFallbackJsonConfigFile.getConfig(paths)
      repositories = {}
      for repoName,repoAttributes in repositoryDict.iteritems():
        repositories[repoName] = subuserlib.classes.repository.Repository(self.getUser(),name=repoName,gitOriginURI=repoAttributes["git-origin"],autoRemove=repoAttributes["auto-remove"])
      return repositories

    self.systemRepositories = loadRepositoryDict(self.systemRepositoryListPaths)
    self.userRepositories = loadRepositoryDict([self.userRepositoryListPath])

  def save(self):
    """ Save attributes of the installed images to disk. """
    userRepositoryListDict = {}
    for name,repository in self.userRepositories.iteritems():
      userRepositoryListDict[name]["git-origin"] = repository.getGitOriginURI()
      userRepositoryListDict[name]["auto-remove"] = repository.getAutoRemove()
    with open(self.userRepositoryListPath, 'w') as file_f:
      json.dump(userRepositoryListDict, file_f, indent=1, separators=(',', ': '))

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.systemRepositoryListPaths = [os.path.join(self.getUser().homeDir,".subuser","repositories.json")
       ,"/etc/subuser/repositories.json"] # TODO how does this work on windows?
    self.userRepositoryListPath = os.path.join(subuserlib.paths.getSubuserDir(),"repositories.json")
    self.reloadRepositoryLists()
