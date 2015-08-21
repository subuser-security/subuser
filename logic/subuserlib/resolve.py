#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This module is used to parse the image source identifiers used to identify image sources during instalation.  For more information see the image-source-identifiers section of the subuser standard.
"""

#external imports
#import ...
#internal imports
import subuserlib.classes.subuser, subuserlib.classes.repository, subuserlib.classes.imageSource

def resolveImageSource(user,imageSourcePath,contextRepository=None,allowRefferingToRepositoriesByName=True):
  """
  From a image source identifier path return a ImageSource object.

  >>> user = subuserlib.classes.user.User()

  Usually, the syntax is image-name@repository-name.

  >>> print(resolveImageSource(user,"foo@default").getName())
  foo

  If there is no @, then we assume that the repository is the contextRepository.  The default contextRepository is the "default" repository.

  >>> print(resolveImageSource(user,"foo").getName())
  foo

  If the repository identifier is a URI and a repository with the same URI already exists, then the URI is resolved to the name of the existing repository. Otherwise, a temporary repository is created.

  >>> print(resolveImageSource(user,"bar@file:///home/travis/remote-test-repo").getName())
  Adding new temporary repository file:///home/travis/remote-test-repo
  bar

  If the repository identifier is a path to a folder on the local machine and a repository pointing to this folder already exists, then the identifier is resolved to the name of the existing repository. Otherwise, a temporary repository is created.

  >>> print(resolveImageSource(user,"bar@/home/travis/remote-test-repo").getName())
  Adding new temporary repository /home/travis/remote-test-repo
  bar

  Throws an Key error:
    - If the repository does not exist
    - If the image is not in the repository

  >>> resolveImageSource(user,"non-existant@default")
  Traceback (most recent call last):
  KeyError: 'non-existant'
  """
  if not contextRepository:
    contextRepository = user.getRegistry().getRepositories()["default"]
  splitImageIdentifier = imageSourcePath.split("@",1)
  imageName = splitImageIdentifier[0]
  # For identifiers of the format:
  # "foo"
  if len(splitImageIdentifier)==1:
    repository = contextRepository
  # "foo@bar"
  elif not ":" in splitImageIdentifier[1] and not splitImageIdentifier[1].startswith("/"):
    if allowRefferingToRepositoriesByName or splitImageIdentifier[1] == "default":
      repository = user.getRegistry().getRepositories()[splitImageIdentifier[1]]
    else:
      raise Exception("Error when resolving ImageSource "+imageSourcePath+". Refering to repositories by name is forbidden in this context.")
  # "foo@https://github.com/subuser-security/some-repo.git"
  else:
    repository = getRepositoryFromURIOrPath(user,splitImageIdentifier[1])
  return repository[imageName]

def lookupRepositoryByURI(user,uri):
  """
  If a repository with this URI exists, return that repository.  Otherwise, return None.
  """
  for _,repository in user.getRegistry().getRepositories().items():
    if uri == repository.getURI():
      return repository
  return None

def lookupRepositoryByPath(user,path):
  """
  If a repository with this path exists, return that repository.  Otherwise, return None.
  """
  for _,repository in user.getRegistry().getRepositories().items():
    if repository.isLocal() and path == repository.getRepoPath():
      return repository
  return None

def lookupRepositoryByURIOrPath(user,uriOrPath):
  if uriOrPath.startswith("/"):
    return lookupRepositoryByPath(user,uriOrPath)
  else:
    return lookupRepositoryByURI(user,uriOrPath)

def getRepositoryFromURI(user,uri):
  """
  Either return the repository who's URI is equal to the given URI or return a new temporary repository with that URI.
  """
  #First check if a repository with this URI already exists
  repository = lookupRepositoryByURI(user,uri)
  if repository:
    return repository
  # If it doesn't, create a new repo and return it.
  newTempRepo = subuserlib.classes.repository.Repository(user=user,name=user.getRegistry().getRepositories().getNewUniqueTempRepoId(),gitOriginURI=uri,gitCommitHash="master",temporary=True)
  user.getRegistry().getRepositories().addRepository(newTempRepo)
  return newTempRepo

def getRepositoryFromPath(user,path):
  repository = lookupRepositoryByPath(user,path)
  if repository:
    return repository
  else:
    # If it doesn't, create a new repo and return it.
    newTempRepo = subuserlib.classes.repository.Repository(user=user,name=user.getRegistry().getRepositories().getNewUniqueTempRepoId(),temporary=True,sourceDir=path)
    user.getRegistry().getRepositories().addRepository(newTempRepo)
    return newTempRepo

def getRepositoryFromURIOrPath(user,uriOrPath):
  if uriOrPath.startswith("/"):
    return getRepositoryFromPath(user,uriOrPath)
  else:
    return getRepositoryFromURI(user,uriOrPath)

