#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This module is used to parse the program source identifiers used to identify program sources during instalation.  For more information see the program-source-identifiers section of the subuser standard.
"""

#external imports
import sys
#internal imports
import subuserlib.classes.subuser, subuserlib.classes.repository, subuserlib.classes.programSource

def resolveProgramSource(user,programSourcePath,contextRepository=None,allowRefferingToRepositoriesByName=True):
  """
  From a program source identifier path return a ProgamSource object. 

  >>> user = subuserlib.classes.user.User()

  Usually, the syntax is program-name@repository-name.

  >>> resolveProgramSource(user,"foo@default").getName()
  u'foo'

  If there is no @, then we assume that the repository is the contextRepository.  The default contextRepository is the "default" repository.

  >>> resolveProgramSource(user,"foo").getName()
  u'foo'

  If the repository identifier is a URI and a repository with the same URI already exists, then the URI is resolved to the name of the existing repository. Otherwise, a temporary repository is created.

  >>> resolveProgramSource(user,"bar@file:///root/subuser/test/remote-test-repo").getName()
  Adding new temporary repository file:///root/subuser/test/remote-test-repo
  u'bar'

  Throws an Index error:
    - If the repository does not exist
    - If the program is not in the repository

  >>> resolveProgramSource(user,"non-existant@default")
  Traceback (most recent call last):
  KeyError: 'non-existant'
  """
  if not contextRepository:
    contextRepository = user.getRegistry().getRepositories()["default"]
  splitProgramIdentifier = programSourcePath.split("@",1)
  programName = splitProgramIdentifier[0]
  # For identifiers of the format:
  # "foo" 
  if len(splitProgramIdentifier)==1:
    repository = contextRepository
  # "foo@bar"
  elif not ":" in splitProgramIdentifier[1]:
    if allowRefferingToRepositoriesByName or splitProgramIdentifier[1] == "default":
      repository = user.getRegistry().getRepositories()[splitProgramIdentifier[1]]
    else:
      raise Exception("Error when resolving ProgramSource "+programSourcePath+". Refering to repositories by name is forbidden in this context.")
  # "foo@https://github.com/subuser-security/some-repo.git"
  else:
    repository = getRepositoryFromURI(user,splitProgramIdentifier[1])
  return repository[programName]

def getRepositoryFromURI(user,uri):
  """
  Either return the repository who's URI is equal to the given URI or return a new temporary repository with that URI.
  """
  #First check if a repository with this URI already exists
  for _,repository in user.getRegistry().getRepositories().iteritems():
    if uri == repository.getGitOriginURI():
      return repository
  # If it doesn't, create a new repo and return it.
  newTempRepo = subuserlib.classes.repository.Repository(user=user,name=user.getRegistry().getRepositories().getNewUniqueTempRepoId(),gitOriginURI=uri,gitCommitHash="master")
  user.getRegistry().getRepositories().addRepository(newTempRepo)
  return newTempRepo
